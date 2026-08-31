"""Cliente HTTP mínimo para a API do OpenAlex."""

from __future__ import annotations

import time
from typing import Any, Callable, Iterable, Iterator

import requests

from .config import OPENALEX_BASE_URL, Credentials

MAX_PER_PAGE = 200
DEFAULT_TIMEOUT = 60
RETRY_STATUS = {429, 500, 502, 503, 504}


class OpenAlexError(RuntimeError):
    pass


class OpenAlexClient:
    """Cliente com retry, paginação por cursor e leitura de cota.

    >>> cli = OpenAlexClient(Credentials(mailto="voce@exemplo.br"))
    >>> cli.count("works", {"filter": "publication_year:2024"})
    """

    def __init__(
        self,
        credentials: Credentials,
        base_url: str = OPENALEX_BASE_URL,
        max_retries: int = 5,
        pause: float = 0.1,
    ) -> None:
        self.credentials = credentials
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self.pause = pause
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": credentials.user_agent})
        self.last_rate_limit: dict[str, str] = {}

    # ------------------------------------------------------------------ #
    # requisição bruta
    # ------------------------------------------------------------------ #
    def get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        query = {**(params or {}), **self.credentials.auth_params}
        query = {k: v for k, v in query.items() if v not in (None, "")}

        delay = 1.0
        last_error = ""
        for tentativa in range(1, self.max_retries + 1):
            try:
                resp = self.session.get(url, params=query, timeout=DEFAULT_TIMEOUT)
            except requests.RequestException as exc:  # rede instável
                last_error = f"falha de rede: {exc}"
            else:
                self._store_rate_limit(resp)
                if resp.status_code == 200:
                    if self.pause:
                        time.sleep(self.pause)
                    return resp.json()
                if resp.status_code == 403:
                    raise OpenAlexError(
                        "403 do OpenAlex. Verifique sua api_key / mailto na célula "
                        f"de configuração. Resposta: {resp.text[:300]}"
                    )
                if resp.status_code not in RETRY_STATUS:
                    raise OpenAlexError(f"HTTP {resp.status_code}: {resp.text[:300]}")
                last_error = f"HTTP {resp.status_code}"

            if tentativa < self.max_retries:
                time.sleep(delay)
                delay = min(delay * 2, 30)

        raise OpenAlexError(
            f"Não foi possível completar a requisição após {self.max_retries} "
            f"tentativas ({last_error}). URL: {url}"
        )

    def _store_rate_limit(self, resp: requests.Response) -> None:
        for header in (
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Credits-Used",
            "X-RateLimit-Reset",
        ):
            if header in resp.headers:
                self.last_rate_limit[header] = resp.headers[header]

    # ------------------------------------------------------------------ #
    # helpers de alto nível
    # ------------------------------------------------------------------ #
    def count(self, endpoint: str, params: dict[str, Any] | None = None) -> int:
        """Quantos registros existem para o filtro, sem baixar os registros."""
        payload = self.get(endpoint, {**(params or {}), "per-page": 1})
        return int(payload.get("meta", {}).get("count", 0))

    def group_by(
        self, endpoint: str, group: str, params: dict[str, Any] | None = None
    ) -> list[dict]:
        """Agregação server-side: 1 requisição em vez de baixar tudo.

        Retorna a lista ``[{key, key_display_name, count}, ...]``.
        """
        payload = self.get(endpoint, {**(params or {}), "group_by": group, "per-page": 200})
        return payload.get("group_by", [])

    def paginate(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        max_records: int | None = None,
        per_page: int = MAX_PER_PAGE,
        on_progress: Callable[[int, int], None] | None = None,
    ) -> Iterator[dict]:
        """Percorre resultados usando paginação por cursor (sem limite de 10 mil)."""
        cursor = "*"
        baixados = 0
        total = None
        while cursor:
            payload = self.get(
                endpoint,
                {**(params or {}), "per-page": min(per_page, MAX_PER_PAGE), "cursor": cursor},
            )
            meta = payload.get("meta", {})
            if total is None:
                total = int(meta.get("count", 0))
                if max_records:
                    total = min(total, max_records)
            results = payload.get("results", [])
            if not results:
                break
            for item in results:
                yield item
                baixados += 1
                if max_records and baixados >= max_records:
                    if on_progress:
                        on_progress(baixados, total or baixados)
                    return
            if on_progress:
                on_progress(baixados, total or baixados)
            cursor = meta.get("next_cursor")

    def rate_limit_status(self) -> dict:
        """Consulta o endpoint /rate-limit (exige api_key)."""
        if not self.credentials.api_key:
            return {"detalhe": "sem api_key: cota compartilhada pelo IP da rede"}
        return self.get("rate-limit")


def chunked(itens: Iterable[str], tamanho: int = 50) -> Iterator[list[str]]:
    """Divide uma lista de IDs em blocos para o filtro ``id:a|b|c`` do OpenAlex."""
    bloco: list[str] = []
    for item in itens:
        bloco.append(item)
        if len(bloco) == tamanho:
            yield bloco
            bloco = []
    if bloco:
        yield bloco

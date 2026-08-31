"""
Configuração de acesso à API do OpenAlex.

Cada participante do workshop usa **credenciais individuais**:

* ``mailto``  - o e-mail pessoal/institucional. Coloca as requisições no
  *polite pool* do OpenAlex (respostas mais estáveis). É gratuito e é o
  mínimo exigido por este material.
* ``api_key`` - chave individual obtida em https://openalex.org (criar conta
  → Settings → API key). Gratuita para a maior parte dos usos, com cota
  diária própria de cada participante. Opcional, porém recomendada em sala
  de aula: sem chave, todos os participantes compartilham a cota do IP da
  rede local e as requisições começam a falhar.

Referência: https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication
"""

from __future__ import annotations

import os
from dataclasses import dataclass

OPENALEX_BASE_URL = "https://api.openalex.org"

# Versão do material, enviada no User-Agent para facilitar o suporte.
USER_AGENT_APP = "OA_monitor/1.0 (+https://github.com/fabiocantoadv/OA_monitor)"


@dataclass
class Credentials:
    """Credenciais individuais do participante."""

    mailto: str
    api_key: str | None = None

    def __post_init__(self) -> None:
        self.mailto = (self.mailto or "").strip()
        self.api_key = (self.api_key or "").strip() or None
        if "@" not in self.mailto or "." not in self.mailto.split("@")[-1]:
            raise ValueError(
                "Informe um e-mail válido em `mailto`. Ele identifica você no "
                "polite pool do OpenAlex e é obrigatório neste material."
            )

    @classmethod
    def from_env(cls) -> "Credentials":
        """Lê OPENALEX_MAILTO e OPENALEX_API_KEY do ambiente."""
        return cls(
            mailto=os.environ.get("OPENALEX_MAILTO", ""),
            api_key=os.environ.get("OPENALEX_API_KEY"),
        )

    @property
    def auth_params(self) -> dict[str, str]:
        params = {"mailto": self.mailto}
        if self.api_key:
            params["api_key"] = self.api_key
        return params

    @property
    def user_agent(self) -> str:
        return f"{USER_AGENT_APP} mailto:{self.mailto}"

    def describe(self) -> str:
        chave = "sim (cota individual)" if self.api_key else "não (cota compartilhada pelo IP)"
        return f"mailto={self.mailto} | api_key={chave}"

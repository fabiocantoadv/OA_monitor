"""Construção de filtros e extração de obras (works) do OpenAlex."""

from __future__ import annotations

import re
from typing import Any, Callable

import pandas as pd

from .api import OpenAlexClient

# Campos pedidos ao OpenAlex. Pedir só o necessário deixa a resposta muito
# menor e a extração bem mais rápida.
WORK_FIELDS = [
    "id",
    "doi",
    "title",
    "display_name",
    "publication_year",
    "publication_date",
    "type",
    "language",
    "cited_by_count",
    "fwci",
    "is_retracted",
    "open_access",
    "apc_list",
    "apc_paid",
    "primary_location",
    "best_oa_location",
    "locations_count",
    "authorships",
    "primary_topic",
]

OA_STATUS_ORDEM = ["diamond", "hybrid", "gold", "green", "bronze", "closed"]

OA_STATUS_ROTULO = {
    "diamond": "Diamante",
    "hybrid": "Híbrido",
    "gold": "Dourado",
    "green": "Verde",
    "bronze": "Bronze",
    "closed": "Fechado",
}


# --------------------------------------------------------------------------- #
# normalização de identificadores
# --------------------------------------------------------------------------- #
def normalizar_ror(valor: str) -> str:
    """Aceita ``https://ror.org/041akq887``, ``ror.org/041akq887`` ou ``041akq887``."""
    valor = (valor or "").strip()
    m = re.search(r"(0[0-9a-hj-km-np-tv-z]{6}[0-9]{2})", valor, flags=re.I)
    if not m:
        raise ValueError(
            f"ROR inválido: {valor!r}. Procure o ROR da instituição em "
            "https://ror.org (ex.: 041akq887 para a UFSC)."
        )
    return f"https://ror.org/{m.group(1).lower()}"


def normalizar_orcid(valor: str) -> str:
    valor = (valor or "").strip()
    m = re.search(r"(\d{4}-\d{4}-\d{4}-\d{3}[\dXx])", valor)
    if not m:
        raise ValueError(f"ORCID inválido: {valor!r}. Formato esperado: 0000-0002-8338-1931.")
    return f"https://orcid.org/{m.group(1).upper()}"


def normalizar_pais(valor: str) -> str:
    valor = (valor or "").strip().upper()
    if not re.fullmatch(r"[A-Z]{2}", valor):
        raise ValueError(f"Código de país inválido: {valor!r}. Use ISO 3166-1 alfa-2, ex.: BR, PT.")
    return valor


# --------------------------------------------------------------------------- #
# montagem do filtro
# --------------------------------------------------------------------------- #
def montar_filtro(
    nivel: str,
    identificador: str,
    ano_inicio: int,
    ano_fim: int,
    tipos: list[str] | None = None,
    somente_com_doi: bool = False,
    extras: dict[str, str] | None = None,
) -> str:
    """Monta a string do parâmetro ``filter`` da API.

    nivel: ``"pais"``, ``"instituicao"``, ``"pesquisador"`` ou ``"fonte"``.
    identificador: código de país (BR), ROR, ORCID ou ISSN, conforme o nível.
    """
    nivel = nivel.strip().lower()
    if nivel in ("pais", "país", "country"):
        chave = f"authorships.institutions.country_code:{normalizar_pais(identificador)}"
    elif nivel in ("instituicao", "instituição", "institution", "ror"):
        chave = f"authorships.institutions.ror:{normalizar_ror(identificador)}"
    elif nivel in ("pesquisador", "autor", "author", "orcid"):
        chave = f"authorships.author.orcid:{normalizar_orcid(identificador)}"
    elif nivel in ("fonte", "source", "issn", "periodico", "periódico"):
        chave = f"primary_location.source.issn:{identificador.strip()}"
    else:
        raise ValueError(
            f"Nível desconhecido: {nivel!r}. Use pais, instituicao, pesquisador ou fonte."
        )

    partes = [chave, f"publication_year:{ano_inicio}-{ano_fim}"]
    if tipos:
        partes.append("type:" + "|".join(tipos))
    if somente_com_doi:
        partes.append("has_doi:true")
    for k, v in (extras or {}).items():
        partes.append(f"{k}:{v}")
    return ",".join(partes)


# --------------------------------------------------------------------------- #
# extração
# --------------------------------------------------------------------------- #
def _autor_instituicoes(work: dict) -> tuple[str, str, int]:
    nomes, paises = [], []
    for a in work.get("authorships") or []:
        for inst in a.get("institutions") or []:
            if inst.get("display_name"):
                nomes.append(inst["display_name"])
            if inst.get("country_code"):
                paises.append(inst["country_code"])
    n_autores = len(work.get("authorships") or [])
    return ("; ".join(dict.fromkeys(nomes))[:500], "; ".join(dict.fromkeys(paises)), n_autores)


def achatar_work(work: dict) -> dict:
    """Converte um registro aninhado do OpenAlex numa linha de tabela."""
    oa = work.get("open_access") or {}
    pl = work.get("primary_location") or {}
    fonte = pl.get("source") or {}
    boa = work.get("best_oa_location") or {}
    apc_list = work.get("apc_list") or {}
    apc_paid = work.get("apc_paid") or {}
    topico = work.get("primary_topic") or {}
    instituicoes, paises, n_autores = _autor_instituicoes(work)

    return {
        "id": work.get("id"),
        "doi": work.get("doi"),
        "titulo": work.get("title") or work.get("display_name"),
        "ano": work.get("publication_year"),
        "data": work.get("publication_date"),
        "tipo": work.get("type"),
        "idioma": work.get("language"),
        "citacoes": work.get("cited_by_count", 0),
        "fwci": work.get("fwci"),
        "retratado": work.get("is_retracted", False),
        # --- acesso aberto ---
        "is_oa": bool(oa.get("is_oa", False)),
        "oa_status": oa.get("oa_status", "closed"),
        "oa_url": oa.get("oa_url"),
        "em_repositorio": bool(oa.get("any_repository_has_fulltext", False)),
        "melhor_oa_tipo": boa.get("version"),
        "melhor_oa_local": ((boa.get("source") or {}).get("type")),
        # --- fonte ---
        "fonte": fonte.get("display_name"),
        "fonte_id": fonte.get("id"),
        "fonte_issn_l": fonte.get("issn_l"),
        "fonte_tipo": fonte.get("type"),
        "fonte_editora": fonte.get("host_organization_name"),
        "fonte_no_doaj": bool(fonte.get("is_in_doaj", False)),
        "fonte_is_oa": bool(fonte.get("is_oa", False)),
        # --- APC ---
        "apc_cobrado_usd": apc_list.get("value_usd"),
        "apc_pago_usd": apc_paid.get("value_usd"),
        "apc_pago_origem": apc_paid.get("provenance"),
        # --- contexto ---
        "topico": topico.get("display_name"),
        "area": ((topico.get("field") or {}).get("display_name")),
        "instituicoes": instituicoes,
        "paises_instituicoes": paises,
        "n_autores": n_autores,
    }


def extrair_works(
    client: OpenAlexClient,
    filtro: str,
    max_registros: int | None = 5000,
    on_progress: Callable[[int, int], None] | None = None,
) -> pd.DataFrame:
    """Baixa as obras que atendem ao filtro e devolve um DataFrame achatado."""
    params: dict[str, Any] = {"filter": filtro, "select": ",".join(WORK_FIELDS)}
    linhas = [
        achatar_work(w)
        for w in client.paginate(
            "works", params, max_records=max_registros, on_progress=on_progress
        )
    ]
    df = pd.DataFrame(linhas)
    if df.empty:
        return df

    df["oa_status"] = (
        df["oa_status"].fillna("closed").where(df["oa_status"].isin(OA_STATUS_ORDEM), "closed")
    )
    df["oa_status_rotulo"] = df["oa_status"].map(OA_STATUS_ROTULO)
    df["ano"] = pd.to_numeric(df["ano"], errors="coerce").astype("Int64")
    for col in ("apc_cobrado_usd", "apc_pago_usd", "fwci"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def resumo_rapido(client: OpenAlexClient, filtro: str) -> dict:
    """Contagens agregadas sem baixar registro nenhum (1 requisição cada).

    Útil para dimensionar a extração antes de rodá-la.
    """
    total = client.count("works", {"filter": filtro})
    por_status = {
        g["key"]: g["count"] for g in client.group_by("works", "open_access.oa_status", {"filter": filtro})
    }
    return {"total": total, "por_oa_status": por_status}

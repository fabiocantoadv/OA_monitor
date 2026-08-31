"""Indicadores de Ciência Aberta a partir do DataFrame de obras."""

from __future__ import annotations

import pandas as pd

from .extract import OA_STATUS_ORDEM, OA_STATUS_ROTULO


def _vazio(df: pd.DataFrame) -> bool:
    return df is None or len(df) == 0


# --------------------------------------------------------------------------- #
# 1. Indicadores de cabeçalho
# --------------------------------------------------------------------------- #
def indicadores_gerais(df: pd.DataFrame) -> dict:
    """Números-síntese do conjunto analisado."""
    if _vazio(df):
        return {}
    n = len(df)
    oa = int(df["is_oa"].sum())
    com_apc = df["apc_pago_usd"].notna() & (df["apc_pago_usd"] > 0)
    return {
        "obras": n,
        "periodo": f"{int(df['ano'].min())}–{int(df['ano'].max())}",
        "obras_oa": oa,
        "taxa_oa": round(100 * oa / n, 1),
        "taxa_diamante": round(100 * (df["oa_status"] == "diamond").sum() / n, 1),
        "taxa_em_repositorio": round(100 * df["em_repositorio"].sum() / n, 1),
        "taxa_no_doaj": round(100 * df["fonte_no_doaj"].sum() / n, 1),
        "obras_com_apc_pago": int(com_apc.sum()),
        "apc_total_usd": round(float(df.loc[com_apc, "apc_pago_usd"].sum()), 2),
        "apc_medio_usd": (
            round(float(df.loc[com_apc, "apc_pago_usd"].mean()), 2) if com_apc.any() else 0.0
        ),
        "citacoes_totais": int(df["citacoes"].sum()),
        "citacoes_por_obra": round(float(df["citacoes"].mean()), 2),
    }


# --------------------------------------------------------------------------- #
# 2. Distribuição por via de acesso
# --------------------------------------------------------------------------- #
def distribuicao_oa(df: pd.DataFrame) -> pd.DataFrame:
    """Obras por via de acesso (diamante, híbrido, dourado, verde, bronze, fechado)."""
    if _vazio(df):
        return pd.DataFrame(columns=["oa_status", "rotulo", "obras", "percentual"])
    cont = df["oa_status"].value_counts()
    linhas = [
        {
            "oa_status": s,
            "rotulo": OA_STATUS_ROTULO[s],
            "obras": int(cont.get(s, 0)),
            "percentual": round(100 * int(cont.get(s, 0)) / len(df), 2),
        }
        for s in OA_STATUS_ORDEM
    ]
    return pd.DataFrame(linhas)


# --------------------------------------------------------------------------- #
# 3. Séries temporais
# --------------------------------------------------------------------------- #
def serie_anual_oa(df: pd.DataFrame) -> pd.DataFrame:
    """Taxa de acesso aberto por ano."""
    if _vazio(df):
        return pd.DataFrame(columns=["ano", "obras", "obras_oa", "taxa_oa"])
    g = df.groupby("ano", dropna=True).agg(obras=("id", "size"), obras_oa=("is_oa", "sum"))
    g = g.reset_index()
    g["taxa_oa"] = (100 * g["obras_oa"] / g["obras"]).round(2)
    g["ano"] = g["ano"].astype(int)
    return g.sort_values("ano").reset_index(drop=True)


def serie_anual_por_status(df: pd.DataFrame, percentual: bool = True) -> pd.DataFrame:
    """Composição das vias de acesso ano a ano (formato longo, pronto para Vega)."""
    if _vazio(df):
        return pd.DataFrame(columns=["ano", "oa_status", "rotulo", "obras", "percentual", "ordem"])
    g = (
        df.groupby(["ano", "oa_status"], dropna=True)
        .size()
        .reset_index(name="obras")
    )
    total = g.groupby("ano")["obras"].transform("sum")
    g["percentual"] = (100 * g["obras"] / total).round(2)
    g["rotulo"] = g["oa_status"].map(OA_STATUS_ROTULO)
    g["ano"] = g["ano"].astype(int)
    # `ordem` fixa a sequência semântica das vias (diamante → fechado). É ela que
    # empilha os segmentos na mesma ordem no matplotlib e no Vega — sem isso o
    # Vega empilharia em ordem alfabética do rótulo.
    g["ordem"] = g["oa_status"].map({s: i for i, s in enumerate(OA_STATUS_ORDEM)})
    g = g.sort_values(["ano", "ordem"])
    return g.reset_index(drop=True)


# --------------------------------------------------------------------------- #
# 4. APCs
# --------------------------------------------------------------------------- #
def indicadores_apc(df: pd.DataFrame) -> pd.DataFrame:
    """Custo de publicação por ano: total pago, média e cobertura do dado.

    Atenção: ``apc_paid`` só existe quando o OpenAlex consegue inferir o valor
    (em geral via DOAJ/OpenAPC). É um piso, não o gasto real.
    """
    if _vazio(df):
        return pd.DataFrame(columns=["ano", "obras", "obras_com_apc", "cobertura", "apc_total_usd", "apc_medio_usd"])
    d = df.copy()
    d["tem_apc"] = d["apc_pago_usd"].notna() & (d["apc_pago_usd"] > 0)
    g = d.groupby("ano", dropna=True).agg(
        obras=("id", "size"),
        obras_com_apc=("tem_apc", "sum"),
        apc_total_usd=("apc_pago_usd", "sum"),
        apc_medio_usd=("apc_pago_usd", "mean"),
    ).reset_index()
    g["cobertura"] = (100 * g["obras_com_apc"] / g["obras"]).round(2)
    g["apc_total_usd"] = g["apc_total_usd"].fillna(0).round(2)
    g["apc_medio_usd"] = g["apc_medio_usd"].fillna(0).round(2)
    g["ano"] = g["ano"].astype(int)
    return g[["ano", "obras", "obras_com_apc", "cobertura", "apc_total_usd", "apc_medio_usd"]]


def apc_por_editora(df: pd.DataFrame, top: int = 10) -> pd.DataFrame:
    """Para onde foi o dinheiro de APC."""
    if _vazio(df):
        return pd.DataFrame(columns=["editora", "obras_com_apc", "apc_total_usd", "apc_medio_usd"])
    d = df[df["apc_pago_usd"].notna() & (df["apc_pago_usd"] > 0)].copy()
    if d.empty:
        return pd.DataFrame(columns=["editora", "obras_com_apc", "apc_total_usd", "apc_medio_usd"])
    d["editora"] = d["fonte_editora"].fillna("(não informado)")
    g = d.groupby("editora").agg(
        obras_com_apc=("id", "size"),
        apc_total_usd=("apc_pago_usd", "sum"),
        apc_medio_usd=("apc_pago_usd", "mean"),
    ).reset_index()
    g[["apc_total_usd", "apc_medio_usd"]] = g[["apc_total_usd", "apc_medio_usd"]].round(2)
    return g.sort_values("apc_total_usd", ascending=False).head(top).reset_index(drop=True)


# --------------------------------------------------------------------------- #
# 5. Citação
# --------------------------------------------------------------------------- #
def citacoes_por_status(df: pd.DataFrame) -> pd.DataFrame:
    """Impacto de citação por via de acesso.

    A mediana é o número a ler: a média de citações é dominada por poucos
    outliers. E a diferença entre vias é associação, não causa — obras
    fechadas e abertas não são amostras comparáveis.
    """
    if _vazio(df):
        return pd.DataFrame(columns=["oa_status", "rotulo", "obras", "citacoes_media", "citacoes_mediana", "fwci_mediana"])
    g = df.groupby("oa_status").agg(
        obras=("id", "size"),
        citacoes_media=("citacoes", "mean"),
        citacoes_mediana=("citacoes", "median"),
        fwci_mediana=("fwci", "median"),
    ).reset_index()
    g["rotulo"] = g["oa_status"].map(OA_STATUS_ROTULO)
    g["_ordem"] = g["oa_status"].map({s: i for i, s in enumerate(OA_STATUS_ORDEM)})
    g = g.sort_values("_ordem").drop(columns="_ordem")
    for c in ("citacoes_media", "citacoes_mediana", "fwci_mediana"):
        g[c] = g[c].round(2)
    return g[["oa_status", "rotulo", "obras", "citacoes_media", "citacoes_mediana", "fwci_mediana"]].reset_index(drop=True)


# --------------------------------------------------------------------------- #
# 6. Fontes e áreas
# --------------------------------------------------------------------------- #
def top_fontes(df: pd.DataFrame, top: int = 15) -> pd.DataFrame:
    """Periódicos mais usados, com sua taxa de abertura e presença no DOAJ."""
    if _vazio(df):
        return pd.DataFrame(columns=["fonte", "editora", "obras", "taxa_oa", "no_doaj"])
    d = df[df["fonte"].notna()]
    if d.empty:
        return pd.DataFrame(columns=["fonte", "editora", "obras", "taxa_oa", "no_doaj"])
    g = d.groupby("fonte").agg(
        editora=("fonte_editora", "first"),
        obras=("id", "size"),
        taxa_oa=("is_oa", "mean"),
        no_doaj=("fonte_no_doaj", "first"),
    ).reset_index()
    g["taxa_oa"] = (100 * g["taxa_oa"]).round(1)
    return g.sort_values("obras", ascending=False).head(top).reset_index(drop=True)


def oa_por_area(df: pd.DataFrame, minimo: int = 10) -> pd.DataFrame:
    """Taxa de abertura por grande área, para áreas com massa suficiente."""
    if _vazio(df) or df["area"].isna().all():
        return pd.DataFrame(columns=["area", "obras", "taxa_oa"])
    g = df.dropna(subset=["area"]).groupby("area").agg(
        obras=("id", "size"), taxa_oa=("is_oa", "mean")
    ).reset_index()
    g["taxa_oa"] = (100 * g["taxa_oa"]).round(1)
    return g[g["obras"] >= minimo].sort_values("taxa_oa", ascending=False).reset_index(drop=True)


# --------------------------------------------------------------------------- #
# painel completo
# --------------------------------------------------------------------------- #
def painel_completo(df: pd.DataFrame) -> dict:
    """Roda todos os indicadores de uma vez. É o que alimenta o dashboard."""
    return {
        "gerais": indicadores_gerais(df),
        "distribuicao_oa": distribuicao_oa(df),
        "serie_anual_oa": serie_anual_oa(df),
        "serie_anual_status": serie_anual_por_status(df),
        "apc_anual": indicadores_apc(df),
        "apc_editora": apc_por_editora(df),
        "citacoes_status": citacoes_por_status(df),
        "top_fontes": top_fontes(df),
        "oa_area": oa_por_area(df),
    }

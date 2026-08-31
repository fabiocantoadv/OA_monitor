"""Gráficos em matplotlib para uso dentro do notebook.

Paleta
------
Cada via de acesso tem **uma cor fixa** em todo o material: a cor identifica a
via, nunca a posição no gráfico. Um filtro que remova categorias não repinta as
que sobraram.

As cinco vias abertas usam matizes distintos; "Fechado" é deliberadamente
acromático (cinza) — é a ausência de abertura, não uma sexta via. A ordem
diamante → híbrido → dourado → verde → bronze foi escolhida (e verificada) para
que cores vizinhas em barras empilhadas continuem distinguíveis por leitores com
daltonismo (ΔE CVD ≥ 8 em todos os pares adjacentes). Amarelo, rosa e verde-água
ficam abaixo de 3:1 de contraste com o fundo branco, por isso todos os gráficos
trazem rótulos de valor visíveis e há sempre uma tabela equivalente.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import PercentFormatter

from .extract import OA_STATUS_ORDEM, OA_STATUS_ROTULO

CORES_OA = {
    "diamond": "#2a78d6",  # azul
    "hybrid": "#e87ba4",   # rosa
    "gold": "#eda100",     # amarelo
    "green": "#1baf7a",    # verde-água
    "bronze": "#eb6834",   # laranja
    "closed": "#8f8e88",   # cinza neutro: ausência de abertura
}

TINTA_PRIMARIA = "#0b0b0b"
TINTA_SECUNDARIA = "#52514e"
GRADE = "#e4e3df"
AZUL = "#2a78d6"


def _estilo(ax, titulo: str, subtitulo: str = "") -> None:
    ax.set_title(titulo, loc="left", fontsize=13, color=TINTA_PRIMARIA,
                 pad=26 if subtitulo else 10)
    if subtitulo:
        ax.text(
            0, 1.012, subtitulo, transform=ax.transAxes,
            fontsize=9.5, color=TINTA_SECUNDARIA, va="bottom",
        )
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(GRADE)
    ax.tick_params(colors=TINTA_SECUNDARIA, labelsize=9, length=0)
    ax.grid(axis="y", color=GRADE, linewidth=0.8)
    ax.set_axisbelow(True)


def grafico_distribuicao_oa(dist: pd.DataFrame, titulo: str = "Distribuição por via de acesso"):
    """Barras horizontais: quanto cada via representa do total."""
    d = dist[dist["obras"] > 0].iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 0.55 * max(len(d), 3) + 1.6))
    ax.barh(d["rotulo"], d["percentual"],
            color=[CORES_OA[s] for s in d["oa_status"]], height=0.62)
    for y, (pct, n) in enumerate(zip(d["percentual"], d["obras"])):
        ax.text(pct + max(d["percentual"]) * 0.015, y, f"{pct:.1f}%  ({n:,})".replace(",", "."),
                va="center", fontsize=9, color=TINTA_SECUNDARIA)
    ax.set_xlim(0, max(d["percentual"]) * 1.28)
    ax.xaxis.set_major_formatter(PercentFormatter())
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=GRADE, linewidth=0.8)
    _estilo(ax, titulo, f"{int(d['obras'].sum()):,} obras".replace(",", "."))
    fig.tight_layout()
    return fig


def grafico_serie_oa(serie: pd.DataFrame, titulo: str = "Taxa de acesso aberto por ano"):
    """Linha única: evolução da taxa de abertura. Sem legenda — o título nomeia a série."""
    fig, ax = plt.subplots(figsize=(9, 4.4))
    ax.plot(serie["ano"], serie["taxa_oa"], color=AZUL, linewidth=2,
            marker="o", markersize=5, markerfacecolor=AZUL, markeredgecolor="white", markeredgewidth=1.5)
    # rótulo apenas nos extremos, não em todo ponto
    for i in (0, len(serie) - 1):
        if i < 0 or serie.empty:
            continue
        linha = serie.iloc[i]
        ax.annotate(f"{linha['taxa_oa']:.1f}%", (linha["ano"], linha["taxa_oa"]),
                    textcoords="offset points", xytext=(0, 10), ha="center",
                    fontsize=9.5, color=TINTA_PRIMARIA)
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(PercentFormatter())
    ax.set_xticks(serie["ano"])
    _estilo(ax, titulo, "% das obras do período com alguma versão em acesso aberto")
    fig.tight_layout()
    return fig


def grafico_composicao_anual(longo: pd.DataFrame, titulo: str = "Composição das vias por ano"):
    """Barras empilhadas 100%: como a mistura de vias muda ao longo do tempo."""
    piv = longo.pivot_table(index="ano", columns="oa_status", values="percentual",
                            aggfunc="sum").fillna(0)
    piv = piv.reindex(columns=[s for s in OA_STATUS_ORDEM if s in piv.columns])
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    base = pd.Series(0.0, index=piv.index)
    for status in piv.columns:
        valores = piv[status]
        ax.bar(piv.index, valores, bottom=base, width=0.68,
               color=CORES_OA[status], label=OA_STATUS_ROTULO[status],
               edgecolor="white", linewidth=2)  # 2px de folga entre segmentos
        for x, (v, b) in zip(piv.index, zip(valores, base)):
            if v >= 7:  # rótulo direto só onde cabe
                ax.text(x, b + v / 2, f"{v:.0f}", ha="center", va="center",
                        fontsize=8.5, color="white" if status != "gold" else TINTA_PRIMARIA)
        base = base + valores
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(PercentFormatter())
    ax.set_xticks(list(piv.index))
    ax.legend(frameon=False, fontsize=9, ncol=6, loc="upper center",
              bbox_to_anchor=(0.5, -0.11), labelcolor=TINTA_SECUNDARIA)
    _estilo(ax, titulo, "% das obras de cada ano")
    fig.tight_layout()
    return fig


def grafico_apc(apc: pd.DataFrame, titulo: str = "APCs pagos por ano (USD)"):
    """Uma medida por eixo: valor total. A cobertura do dado vai no rótulo."""
    fig, ax = plt.subplots(figsize=(9, 4.4))
    ax.bar(apc["ano"], apc["apc_total_usd"], width=0.62, color=AZUL)
    for _, r in apc.iterrows():
        ax.text(r["ano"], r["apc_total_usd"], f"US$ {r['apc_total_usd']:,.0f}".replace(",", "."),
                ha="center", va="bottom", fontsize=8.5, color=TINTA_SECUNDARIA)
    ax.set_xticks(list(apc["ano"]))
    cob = apc["cobertura"].mean() if len(apc) else 0
    _estilo(ax, titulo,
            f"Valor identificado pelo OpenAlex — é um piso. Cobertura média do dado: {cob:.0f}% das obras")
    fig.tight_layout()
    return fig


def grafico_citacoes(cit: pd.DataFrame, titulo: str = "Citações por via de acesso (mediana)"):
    """Mediana, não média: a média de citações é dominada por poucos outliers."""
    d = cit[cit["obras"] > 0]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.bar(d["rotulo"], d["citacoes_mediana"], width=0.6,
           color=[CORES_OA[s] for s in d["oa_status"]])
    for x, (v, n) in enumerate(zip(d["citacoes_mediana"], d["obras"])):
        ax.text(x, v, f"{v:g}\nn={n:,}".replace(",", "."), ha="center", va="bottom",
                fontsize=8.5, color=TINTA_SECUNDARIA)
    ax.margins(y=0.22)
    _estilo(ax, titulo, "Associação, não causa: obras abertas e fechadas não são amostras comparáveis")
    fig.tight_layout()
    return fig


def grafico_oa_por_area(area: pd.DataFrame, titulo: str = "Taxa de acesso aberto por área"):
    """Magnitude numa só dimensão: barras ordenadas, hue único."""
    d = area.sort_values("taxa_oa").tail(12)
    fig, ax = plt.subplots(figsize=(8.5, 0.42 * max(len(d), 4) + 1.6))
    ax.barh(d["area"], d["taxa_oa"], color=AZUL, height=0.62)
    for y, (v, n) in enumerate(zip(d["taxa_oa"], d["obras"])):
        ax.text(v + 1.2, y, f"{v:.0f}%  (n={n:,})".replace(",", "."), va="center",
                fontsize=8.5, color=TINTA_SECUNDARIA)
    ax.set_xlim(0, 112)
    ax.xaxis.set_major_formatter(PercentFormatter())
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=GRADE, linewidth=0.8)
    _estilo(ax, titulo)
    fig.tight_layout()
    return fig

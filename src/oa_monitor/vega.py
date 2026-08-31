"""Especificações Vega (v5) geradas a partir dos indicadores.

As specs produzidas aqui são objetos Vega puros — o mesmo formato aceito pelo
componente React ``dashboard/VegaChart.tsx`` (que chama ``vega.parse``) e pelo
``vegaEmbed`` usado no dashboard HTML estático.

Regras de desenho seguidas em todas as specs:

* uma cor fixa por via de acesso (a cor identifica a entidade, nunca o ranking);
* um único eixo de medida por gráfico — nunca dois eixos y;
* rótulos diretos onde cabem, legenda sempre presente quando há 2+ séries;
* tooltip em toda marca;
* grade e eixos discretos, marcas finas.
"""

from __future__ import annotations

import json
from typing import Any

import pandas as pd

from .extract import OA_STATUS_ORDEM, OA_STATUS_ROTULO
from .viz import CORES_OA

SUPERFICIE = "#fcfcfb"
TINTA_PRIMARIA = "#0b0b0b"
TINTA_SECUNDARIA = "#52514e"
GRADE = "#e4e3df"
AZUL = "#2a78d6"

SCHEMA = "https://vega.github.io/schema/vega/v5.json"

_ROTULOS = [OA_STATUS_ROTULO[s] for s in OA_STATUS_ORDEM]
_CORES = [CORES_OA[s] for s in OA_STATUS_ORDEM]


def _base(width: int, height: int) -> dict[str, Any]:
    return {
        "$schema": SCHEMA,
        "width": width,
        "height": height,
        "padding": 8,
        "autosize": {"type": "fit", "contains": "padding"},
        "background": SUPERFICIE,
        "config": {
            "axis": {
                "labelColor": TINTA_SECUNDARIA,
                "labelFontSize": 11,
                "titleColor": TINTA_SECUNDARIA,
                "titleFontSize": 11,
                "titleFontWeight": "normal",
                "domainColor": GRADE,
                "tickColor": GRADE,
                "gridColor": GRADE,
                "gridWidth": 1,
            },
            "legend": {
                "labelColor": TINTA_SECUNDARIA,
                "labelFontSize": 11,
                "titleColor": TINTA_SECUNDARIA,
                "symbolType": "square",
                "symbolSize": 90,
            },
        },
    }


def _escala_cor_oa() -> dict[str, Any]:
    return {
        "name": "cor",
        "type": "ordinal",
        "domain": _ROTULOS,
        "range": _CORES,
    }


# --------------------------------------------------------------------------- #
# 1. distribuição por via de acesso — barras horizontais
# --------------------------------------------------------------------------- #
def spec_distribuicao(dist: pd.DataFrame, width: int = 520) -> dict:
    dados = dist[dist["obras"] > 0].to_dict("records")
    altura = max(len(dados), 3) * 34
    spec = _base(width, altura)
    spec["data"] = [{"name": "tabela", "values": dados}]
    spec["scales"] = [
        {
            "name": "y",
            "type": "band",
            "domain": [r["rotulo"] for r in dados],
            "range": "height",
            "padding": 0.32,
        },
        {
            "name": "x",
            "type": "linear",
            "domain": {"data": "tabela", "field": "percentual"},
            "range": "width",
            "nice": True,
            "zero": True,
        },
        _escala_cor_oa(),
    ]
    spec["axes"] = [
        {"orient": "left", "scale": "y", "domain": False, "ticks": False, "labelPadding": 8},
        {"orient": "bottom", "scale": "x", "grid": True, "format": "d", "title": "% das obras"},
    ]
    spec["marks"] = [
        {
            "type": "rect",
            "from": {"data": "tabela"},
            "encode": {
                "enter": {
                    "y": {"scale": "y", "field": "rotulo"},
                    "height": {"scale": "y", "band": 1},
                    "x": {"scale": "x", "value": 0},
                    "x2": {"scale": "x", "field": "percentual"},
                    "fill": {"scale": "cor", "field": "rotulo"},
                    "cornerRadiusTopRight": {"value": 4},
                    "cornerRadiusBottomRight": {"value": 4},
                    "tooltip": {
                        "signal": "datum.rotulo + ': ' + format(datum.percentual, '.1f') "
                        "+ '% (' + format(datum.obras, ',d') + ' obras)'"
                    },
                },
                "update": {"fillOpacity": {"value": 1}},
                "hover": {"fillOpacity": {"value": 0.78}},
            },
        },
        {
            "type": "text",
            "from": {"data": "tabela"},
            "encode": {
                "enter": {
                    "y": {"scale": "y", "field": "rotulo", "band": 0.5},
                    "x": {"scale": "x", "field": "percentual", "offset": 8},
                    "text": {"signal": "format(datum.percentual, '.1f') + '%'"},
                    "baseline": {"value": "middle"},
                    "fontSize": {"value": 11},
                    "fill": {"value": TINTA_SECUNDARIA},
                }
            },
        },
    ]
    return spec


# --------------------------------------------------------------------------- #
# 2. taxa de OA por ano — linha
# --------------------------------------------------------------------------- #
def spec_serie_oa(serie: pd.DataFrame, width: int = 520, height: int = 260) -> dict:
    dados = serie.to_dict("records")
    spec = _base(width, height)
    spec["data"] = [{"name": "tabela", "values": dados}]
    spec["scales"] = [
        {
            "name": "x",
            "type": "point",
            "domain": [r["ano"] for r in dados],
            "range": "width",
            "padding": 0.5,
        },
        {"name": "y", "type": "linear", "domain": [0, 100], "range": "height", "zero": True},
    ]
    spec["axes"] = [
        {"orient": "bottom", "scale": "x", "format": "d", "labelAngle": 0},
        {"orient": "left", "scale": "y", "grid": True, "title": "% em acesso aberto"},
    ]
    spec["marks"] = [
        {
            "type": "line",
            "from": {"data": "tabela"},
            "encode": {
                "enter": {
                    "x": {"scale": "x", "field": "ano"},
                    "y": {"scale": "y", "field": "taxa_oa"},
                    "stroke": {"value": AZUL},
                    "strokeWidth": {"value": 2},
                }
            },
        },
        {
            "type": "symbol",
            "from": {"data": "tabela"},
            "encode": {
                "enter": {
                    "x": {"scale": "x", "field": "ano"},
                    "y": {"scale": "y", "field": "taxa_oa"},
                    "fill": {"value": AZUL},
                    "stroke": {"value": SUPERFICIE},
                    "strokeWidth": {"value": 1.5},
                    "size": {"value": 70},
                    "tooltip": {
                        "signal": "datum.ano + ': ' + format(datum.taxa_oa, '.1f') + '% de ' "
                        "+ format(datum.obras, ',d') + ' obras'"
                    },
                },
                "hover": {"size": {"value": 140}},
            },
        },
    ]
    return spec


# --------------------------------------------------------------------------- #
# 3. composição das vias por ano — barras empilhadas 100%
# --------------------------------------------------------------------------- #
def spec_composicao(longo: pd.DataFrame, width: int = 520, height: int = 280) -> dict:
    dados = longo.to_dict("records")
    spec = _base(width, height)
    spec["data"] = [
        {
            "name": "tabela",
            "values": dados,
            "transform": [
                {
                    "type": "stack",
                    "groupby": ["ano"],
                    "field": "percentual",
                    # ordem semântica das vias, não alfabética do rótulo
                    "sort": {"field": "ordem", "order": "ascending"},
                }
            ],
        }
    ]
    spec["scales"] = [
        {
            "name": "x",
            "type": "band",
            "domain": sorted({r["ano"] for r in dados}),
            "range": "width",
            "padding": 0.28,
        },
        {"name": "y", "type": "linear", "domain": [0, 100], "range": "height", "zero": True},
        _escala_cor_oa(),
    ]
    spec["axes"] = [
        {"orient": "bottom", "scale": "x", "format": "d", "labelAngle": 0},
        {"orient": "left", "scale": "y", "grid": True, "title": "% das obras do ano"},
    ]
    spec["legends"] = [{"fill": "cor", "orient": "bottom", "direction": "horizontal", "columns": 6}]
    spec["marks"] = [
        {
            "type": "rect",
            "from": {"data": "tabela"},
            "encode": {
                "enter": {
                    "x": {"scale": "x", "field": "ano"},
                    "width": {"scale": "x", "band": 1},
                    "y": {"scale": "y", "field": "y0"},
                    "y2": {"scale": "y", "field": "y1"},
                    "fill": {"scale": "cor", "field": "rotulo"},
                    "stroke": {"value": SUPERFICIE},
                    "strokeWidth": {"value": 2},
                    "tooltip": {
                        "signal": "datum.ano + ' · ' + datum.rotulo + ': ' "
                        "+ format(datum.percentual, '.1f') + '% (' + format(datum.obras, ',d') + ')'"
                    },
                },
                "update": {"fillOpacity": {"value": 1}},
                "hover": {"fillOpacity": {"value": 0.78}},
            },
        }
    ]
    return spec


# --------------------------------------------------------------------------- #
# 4. APC por ano — barras
# --------------------------------------------------------------------------- #
def spec_apc(apc: pd.DataFrame, width: int = 520, height: int = 260) -> dict:
    dados = apc.to_dict("records")
    spec = _base(width, height)
    spec["data"] = [{"name": "tabela", "values": dados}]
    spec["scales"] = [
        {
            "name": "x",
            "type": "band",
            "domain": [r["ano"] for r in dados],
            "range": "width",
            "padding": 0.3,
        },
        {
            "name": "y",
            "type": "linear",
            "domain": {"data": "tabela", "field": "apc_total_usd"},
            "range": "height",
            "nice": True,
            "zero": True,
        },
    ]
    spec["axes"] = [
        {"orient": "bottom", "scale": "x", "format": "d", "labelAngle": 0},
        {"orient": "left", "scale": "y", "grid": True, "title": "APC pago (USD)", "format": "~s"},
    ]
    spec["marks"] = [
        {
            "type": "rect",
            "from": {"data": "tabela"},
            "encode": {
                "enter": {
                    "x": {"scale": "x", "field": "ano"},
                    "width": {"scale": "x", "band": 1},
                    "y": {"scale": "y", "field": "apc_total_usd"},
                    "y2": {"scale": "y", "value": 0},
                    "fill": {"value": AZUL},
                    "cornerRadiusTopLeft": {"value": 4},
                    "cornerRadiusTopRight": {"value": 4},
                    "tooltip": {
                        "signal": "datum.ano + ': US$ ' + format(datum.apc_total_usd, ',.0f') "
                        "+ ' em ' + format(datum.obras_com_apc, ',d') + ' obras (cobertura ' "
                        "+ format(datum.cobertura, '.0f') + '%)'"
                    },
                },
                "update": {"fillOpacity": {"value": 1}},
                "hover": {"fillOpacity": {"value": 0.78}},
            },
        }
    ]
    return spec


# --------------------------------------------------------------------------- #
# 5. citações por via — barras
# --------------------------------------------------------------------------- #
def spec_citacoes(cit: pd.DataFrame, width: int = 520, height: int = 260) -> dict:
    dados = cit[cit["obras"] > 0].to_dict("records")
    spec = _base(width, height)
    spec["data"] = [{"name": "tabela", "values": dados}]
    spec["scales"] = [
        {
            "name": "x",
            "type": "band",
            "domain": [r["rotulo"] for r in dados],
            "range": "width",
            "padding": 0.3,
        },
        {
            "name": "y",
            "type": "linear",
            "domain": {"data": "tabela", "field": "citacoes_mediana"},
            "range": "height",
            "nice": True,
            "zero": True,
        },
        _escala_cor_oa(),
    ]
    spec["axes"] = [
        {"orient": "bottom", "scale": "x"},
        {"orient": "left", "scale": "y", "grid": True, "title": "citações (mediana)"},
    ]
    spec["marks"] = [
        {
            "type": "rect",
            "from": {"data": "tabela"},
            "encode": {
                "enter": {
                    "x": {"scale": "x", "field": "rotulo"},
                    "width": {"scale": "x", "band": 1},
                    "y": {"scale": "y", "field": "citacoes_mediana"},
                    "y2": {"scale": "y", "value": 0},
                    "fill": {"scale": "cor", "field": "rotulo"},
                    "cornerRadiusTopLeft": {"value": 4},
                    "cornerRadiusTopRight": {"value": 4},
                    "tooltip": {
                        "signal": "datum.rotulo + ': mediana ' + datum.citacoes_mediana "
                        "+ ' citações em ' + format(datum.obras, ',d') + ' obras'"
                    },
                },
                "update": {"fillOpacity": {"value": 1}},
                "hover": {"fillOpacity": {"value": 0.78}},
            },
        }
    ]
    return spec


# --------------------------------------------------------------------------- #
def todas_as_specs(painel: dict) -> dict[str, dict]:
    """Recebe a saída de ``indicators.painel_completo`` e devolve as specs."""
    return {
        "distribuicao": spec_distribuicao(painel["distribuicao_oa"]),
        "serie_oa": spec_serie_oa(painel["serie_anual_oa"]),
        "composicao": spec_composicao(painel["serie_anual_status"]),
        "apc": spec_apc(painel["apc_anual"]),
        "citacoes": spec_citacoes(painel["citacoes_status"]),
    }


def salvar_specs(specs: dict[str, dict], caminho: str) -> str:
    with open(caminho, "w", encoding="utf-8") as fh:
        json.dump(specs, fh, ensure_ascii=False, indent=2)
    return caminho

"""Gera um dashboard HTML autocontido a partir dos indicadores.

O HTML resultante carrega Vega pelo CDN e desenha exatamente as mesmas specs
que o componente React ``dashboard/VegaChart.tsx`` consome — os dados vão
embutidos no arquivo, então ele abre offline com um duplo clique.
"""

from __future__ import annotations

import html
import json
from datetime import datetime

import pandas as pd

from .vega import todas_as_specs

_CSS = """
:root{color-scheme:light;--surface-0:#f5f4f1;--surface-1:#fcfcfb;--line:#e4e3df;
--ink-1:#0b0b0b;--ink-2:#52514e;--ink-3:#7a7973;--accent:#2a78d6}
*{box-sizing:border-box}
body{margin:0;background:var(--surface-0);color:var(--ink-1);
font:14px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:32px 20px 64px}
header h1{font-size:24px;margin:0 0 6px;letter-spacing:-.01em}
header p{margin:0;color:var(--ink-2);font-size:13.5px}
.meta{margin-top:10px;font-size:12.5px;color:var(--ink-3)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:26px 0}
.kpi{background:var(--surface-1);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.kpi .n{font-size:25px;font-weight:600;letter-spacing:-.02em;line-height:1.15}
.kpi .l{font-size:12px;color:var(--ink-2);margin-top:4px}
.kpi .s{font-size:11.5px;color:var(--ink-3);margin-top:2px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(430px,1fr));gap:16px}
.card{background:var(--surface-1);border:1px solid var(--line);border-radius:10px;padding:18px 18px 14px;min-width:0}
.card h2{font-size:15px;margin:0 0 2px;font-weight:600}
.card p.sub{margin:0 0 14px;font-size:12.5px;color:var(--ink-2)}
.chart{width:100%;overflow-x:auto}
details{margin-top:10px;border-top:1px solid var(--line);padding-top:8px}
summary{font-size:12.5px;color:var(--ink-2);cursor:pointer}
table{border-collapse:collapse;width:100%;margin-top:10px;font-size:12.5px}
th,td{text-align:right;padding:5px 8px;border-bottom:1px solid var(--line);white-space:nowrap}
th:first-child,td:first-child{text-align:left}
th{color:var(--ink-2);font-weight:600}
footer{margin-top:32px;font-size:12px;color:var(--ink-3);line-height:1.7}
footer code{background:var(--surface-1);border:1px solid var(--line);border-radius:4px;padding:1px 5px}
"""


def _fmt(n, casas: int = 1) -> str:
    """Formata no padrão pt-BR: 1.234,5"""
    if isinstance(n, float) and casas:
        return f"{n:,.{casas}f}".replace(",", "@").replace(".", ",").replace("@", ".")
    return f"{round(n or 0):,}".replace(",", ".")


def _tabela(df: pd.DataFrame, colunas: dict[str, str]) -> str:
    if df is None or df.empty:
        return "<p style='font-size:12.5px;color:#7a7973'>Sem dados.</p>"
    d = df[[c for c in colunas if c in df.columns]]
    cab = "".join(f"<th>{html.escape(colunas[c])}</th>" for c in d.columns)
    linhas = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(v))}</td>" for v in row) + "</tr>"
        for row in d.itertuples(index=False)
    )
    return f"<table><thead><tr>{cab}</tr></thead><tbody>{linhas}</tbody></table>"


def _kpi(numero: str, rotulo: str, sub: str = "") -> str:
    extra = f"<div class='s'>{html.escape(sub)}</div>" if sub else ""
    return (
        f"<div class='kpi'><div class='n'>{html.escape(numero)}</div>"
        f"<div class='l'>{html.escape(rotulo)}</div>{extra}</div>"
    )


def _card(titulo: str, sub: str, chart_id: str, tabela_html: str) -> str:
    return f"""<section class="card">
  <h2>{html.escape(titulo)}</h2>
  <p class="sub">{html.escape(sub)}</p>
  <div class="chart" id="{chart_id}"></div>
  <details><summary>Ver os dados em tabela</summary>{tabela_html}</details>
</section>"""


def gerar_dashboard(
    painel: dict,
    titulo: str,
    subtitulo: str = "",
    caminho: str = "dashboard_oa.html",
) -> str:
    """Escreve o dashboard e devolve o caminho do arquivo."""
    g = painel.get("gerais") or {}
    specs = todas_as_specs(painel)

    kpis = "".join([
        _kpi(f"{g.get('taxa_oa', 0)}%", "Acesso aberto",
             f"{_fmt(g.get('obras_oa', 0))} de {_fmt(g.get('obras', 0))} obras"),
        _kpi(f"{g.get('taxa_diamante', 0)}%", "Via diamante", "sem cobrança de APC ao autor"),
        _kpi(f"{g.get('taxa_em_repositorio', 0)}%", "Em repositório", "texto completo depositado"),
        _kpi(f"{g.get('taxa_no_doaj', 0)}%", "Em periódico do DOAJ"),
        _kpi(f"US$ {_fmt(g.get('apc_total_usd', 0), casas=0)}", "APC identificado",
             f"em {_fmt(g.get('obras_com_apc_pago', 0))} obras — é um piso"),
        _kpi(_fmt(g.get("citacoes_por_obra", 0)), "Citações por obra",
             f"{_fmt(g.get('citacoes_totais', 0))} no total"),
    ])

    cards = "".join([
        _card("Distribuição por via de acesso",
              "Cada via tem cor fixa em todo o painel.",
              "c-distribuicao",
              _tabela(painel["distribuicao_oa"],
                      {"rotulo": "Via", "obras": "Obras", "percentual": "%"})),
        _card("Taxa de acesso aberto por ano",
              "% das obras do ano com alguma versão aberta.",
              "c-serie",
              _tabela(painel["serie_anual_oa"],
                      {"ano": "Ano", "obras": "Obras", "obras_oa": "Abertas", "taxa_oa": "% aberto"})),
        _card("Composição das vias por ano",
              "Como a mistura de vias muda ao longo do tempo.",
              "c-composicao",
              _tabela(painel["serie_anual_status"],
                      {"ano": "Ano", "rotulo": "Via", "obras": "Obras", "percentual": "%"})),
        _card("APCs pagos por ano",
              "Valor que o OpenAlex consegue identificar — piso, não gasto real.",
              "c-apc",
              _tabela(painel["apc_anual"],
                      {"ano": "Ano", "obras_com_apc": "Obras com APC", "cobertura": "Cobertura %",
                       "apc_total_usd": "Total USD", "apc_medio_usd": "Médio USD"})),
        _card("Citações por via de acesso",
              "Mediana. Associação, não causa: as amostras não são comparáveis.",
              "c-citacoes",
              _tabela(painel["citacoes_status"],
                      {"rotulo": "Via", "obras": "Obras", "citacoes_mediana": "Mediana",
                       "citacoes_media": "Média", "fwci_mediana": "FWCI mediano"})),
        _card("Periódicos mais usados",
              "Onde a produção foi publicada, com a taxa de abertura de cada título.",
              "c-fontes",
              _tabela(painel["top_fontes"],
                      {"fonte": "Periódico", "editora": "Editora", "obras": "Obras",
                       "taxa_oa": "% aberto", "no_doaj": "DOAJ"})),
    ])

    specs_json = json.dumps(specs, ensure_ascii=False)
    agora = datetime.now().strftime("%d/%m/%Y às %H:%M")

    return _escrever(caminho, f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(titulo)}</title>
<style>{_CSS}</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>{html.escape(titulo)}</h1>
    <p>{html.escape(subtitulo)}</p>
    <div class="meta">Período {html.escape(str(g.get('periodo', '—')))} ·
      {_fmt(g.get('obras', 0))} obras · dados do OpenAlex · gerado em {agora}</div>
  </header>
  <div class="kpis">{kpis}</div>
  <div class="grid">{cards}</div>
  <footer>
    Fonte dos dados: <strong>OpenAlex</strong> (CC0), via API pública.
    Gerado com <code>OA_monitor</code> — Workshop ConfOA 2026.<br>
    A cobertura de APC e de vínculos institucionais no OpenAlex é parcial; leia os
    valores de APC como um piso e confira os totais contra a fonte antes de publicá-los.
  </footer>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/vega/5.30.0/vega.min.js"></script>
<script>
  const SPECS = {specs_json};
  const ALVOS = {{
    "c-distribuicao": "distribuicao", "c-serie": "serie_oa",
    "c-composicao": "composicao", "c-apc": "apc", "c-citacoes": "citacoes"
  }};
  function desenhar() {{
    for (const [elId, specId] of Object.entries(ALVOS)) {{
      const el = document.getElementById(elId);
      const spec = SPECS[specId];
      if (!el || !spec) continue;
      el.innerHTML = "";
      try {{
        const largura = Math.max(320, el.clientWidth || 480);
        const view = new vega.View(vega.parse({{...spec, width: largura - 10}}), {{
          renderer: "canvas", container: el, hover: true
        }});
        view.runAsync();
      }} catch (e) {{ console.error("Falha ao desenhar " + specId, e); }}
    }}
  }}
  const cartaoFontes = document.getElementById("c-fontes");
  if (cartaoFontes) {{
    const d = cartaoFontes.closest(".card").querySelector("details");
    if (d) d.open = true;   // este cartão é só tabela
  }}
  window.addEventListener("load", desenhar);
  let t; window.addEventListener("resize", () => {{ clearTimeout(t); t = setTimeout(desenhar, 200); }});
</script>
</body>
</html>
""")


def _escrever(caminho: str, conteudo: str) -> str:
    with open(caminho, "w", encoding="utf-8") as fh:
        fh.write(conteudo)
    return caminho

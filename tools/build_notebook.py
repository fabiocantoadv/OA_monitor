#!/usr/bin/env python3
"""Gera notebooks/OA_Monitor_Workshop_ConfOA2026.ipynb a partir de src/oa_monitor/.

O notebook é autocontido: o código das células é o **mesmo** dos módulos em
`src/oa_monitor/`, extraído na hora da geração. Assim o notebook nunca fica
desatualizado em relação ao pacote — quem quiser mudar o comportamento edita o
módulo e roda `python tools/build_notebook.py`.

Uso:  python tools/build_notebook.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SRC = RAIZ / "src" / "oa_monitor"
SAIDA = RAIZ / "notebooks" / "OA_Monitor_Workshop_ConfOA2026.ipynb"

REPO = "https://github.com/fabiocantoadv/OA_monitor"


def codigo_modulo(nome: str) -> str:
    """Lê um módulo e remove o que não faz sentido dentro de um notebook."""
    texto = (SRC / f"{nome}.py").read_text(encoding="utf-8")
    # remove o docstring do módulo (vira célula markdown)
    texto = re.sub(r'^\s*(?:"""|\'\'\').*?(?:"""|\'\'\')\s*\n', "", texto, count=1, flags=re.S)
    linhas = []
    for linha in texto.splitlines():
        if linha.startswith("from __future__"):
            continue
        if re.match(r"^from \.\w*", linha):  # import relativo: tudo está no mesmo escopo
            continue
        linhas.append(linha)
    return "\n".join(linhas).strip() + "\n"


def md(*partes: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": "\n".join(partes)}


def code(fonte: str, titulo: str | None = None, ocultar: bool = False) -> dict:
    meta: dict = {}
    if titulo:
        cabecalho = f'# @title {titulo}'
        if ocultar:
            cabecalho += ' { display-mode: "form" }'
        fonte = cabecalho + "\n" + fonte
        meta["cellView"] = "form" if ocultar else "code"
    return {
        "cell_type": "code",
        "metadata": meta,
        "execution_count": None,
        "outputs": [],
        "source": fonte.rstrip() + "\n",
    }


def construir() -> dict:
    C: list[dict] = []

    # ---------------------------------------------------------------- capa
    C.append(md(
        "# Monitorando a Ciência Aberta",
        "## Geração de indicadores com dados do OpenAlex",
        "",
        "**Workshop — ConfOA 2026** · duração 3h",
        "",
        f'<a target="_blank" href="https://colab.research.google.com/github/fabiocantoadv/'
        f'OA_monitor/blob/main/notebooks/OA_Monitor_Workshop_ConfOA2026.ipynb">'
        f'<img src="https://colab.research.google.com/assets/colab-badge.svg" '
        f'alt="Abrir no Colab"></a>',
        "",
        "Fabio Lorensi do Canto (UFSC/IBICT) · Thiago M. R. Dias (CEFET-MG/IBICT) · "
        "Marcel Garcia de Souza (IBICT) · Washington L. R. Carvalho Segundo (IBICT)",
        "",
        "---",
        "",
        "### O que você vai fazer aqui",
        "",
        "| Bloco | O quê |",
        "|---|---|",
        "| **0** | Configurar sua credencial individual do OpenAlex |",
        "| **2.1** | Escolher um recorte (país, instituição por ROR, pesquisador por ORCID) e extrair os dados |",
        "| **2.2** | Calcular indicadores: taxa de abertura, vias, APCs, citação |",
        "| **2.3** | Visualizar os resultados |",
        "| **3** | Gerar um dashboard interativo (Vega) e baixá-lo |",
        "",
        "**Como rodar:** `Ambiente de execução → Executar tudo` (ou `Ctrl+F9`), "
        "ou célula a célula com `Shift+Enter`.",
        "",
        "> Todo o código deste notebook também está em "
        f"[`{REPO}`]({REPO}) como um pacote Python reutilizável (`src/oa_monitor/`).",
    ))

    # ------------------------------------------------------- 0. credenciais
    C.append(md(
        "---",
        "# Parte 0 — Preparação",
        "",
        "## 0.1 Instalação",
        "",
        "O Colab já traz `pandas`, `matplotlib` e `requests`. Esta célula só garante as versões.",
    ))
    C.append(code(
        "%pip install -q requests pandas matplotlib\n"
        "\n"
        "import json, os, re, time, html\n"
        "from dataclasses import dataclass\n"
        "from datetime import datetime\n"
        "from typing import Any, Callable, Iterable, Iterator\n"
        "\n"
        "import matplotlib.pyplot as plt\n"
        "import pandas as pd\n"
        "import requests\n"
        "from matplotlib.ticker import PercentFormatter\n"
        "\n"
        "pd.set_option('display.max_columns', 50)\n"
        "pd.set_option('display.width', 200)\n"
        "print('Ambiente pronto.')"
    ))

    # -------------------------------------------------- 1. código de apoio
    C.append(md(
        "---",
        "## 0.2 Código de apoio",
        "",
        "As quatro células a seguir definem tudo o que o notebook usa. "
        "**Leia-as** — é este o código que você vai adaptar ao seu contexto depois "
        "(inclusive pedindo a um LLM: *\"altere a função `montar_filtro` para aceitar "
        "também financiador\"*).",
        "",
        "É o mesmo código do pacote `oa_monitor` no repositório.",
    ))

    C.append(md(
        "### Credenciais e cliente HTTP",
        "",
        "O cliente cuida de três coisas chatas: **repetir** requisições que falham "
        "(com espera crescente), **paginar** por cursor (sem o teto de 10 mil registros da "
        "paginação por página) e **ler os cabeçalhos de cota** que o OpenAlex devolve.",
    ))
    C.append(code(codigo_modulo("config") + "\n\n" + codigo_modulo("api"), ocultar=True))

    C.append(md(
        "### Filtros e extração",
        "",
        "`montar_filtro` traduz *\"a UFSC entre 2015 e 2025\"* para a sintaxe do parâmetro "
        "`filter` da API. `achatar_work` transforma o JSON aninhado do OpenAlex numa linha "
        "de tabela — é aqui que você acrescenta um campo, se precisar de outro.",
    ))
    C.append(code(codigo_modulo("extract"), ocultar=True))

    C.append(md(
        "### Indicadores",
        "",
        "Cada função recebe o DataFrame e devolve outro DataFrame, pronto para gráfico ou "
        "para exportar. Nada de estado escondido.",
    ))
    C.append(code(codigo_modulo("indicators"), ocultar=True))

    C.append(md(
        "### Gráficos, specs Vega e dashboard",
    ))
    C.append(code(
        codigo_modulo("viz") + "\n\n" + codigo_modulo("vega") + "\n\n" + codigo_modulo("dashboard"),
        ocultar=True,
    ))

    C.append(md(
        "---",
        "## 0.3 Sua credencial individual do OpenAlex",
        "",
        "**Cada participante usa a sua própria credencial.** São duas coisas diferentes:",
        "",
        "| | O que é | Como obter | Obrigatório? |",
        "|---|---|---|---|",
        "| **`mailto`** | seu e-mail, enviado em cada requisição | você já tem | **sim** |",
        "| **`api_key`** | chave pessoal, com cota diária só sua | conta gratuita em [openalex.org](https://openalex.org) → *Settings* → *API key* | recomendada |",
        "",
        "Informar o e-mail coloca você no *polite pool* do OpenAlex — respostas mais estáveis. "
        "A chave é gratuita para a maior parte dos usos e dá a você uma cota diária individual.",
        "",
        "**Por que isso importa numa sala de aula:** sem chave, todos os participantes saem "
        "pelo mesmo IP da rede local e **dividem uma única cota** — depois de algumas dezenas de "
        "consultas a API começa a recusar as requisições de todo mundo. Com a chave individual, "
        "cada um tem a sua.",
        "",
        "> 🔒 **Nunca digite a chave direto numa célula e nunca a suba para o GitHub.** "
        "A célula abaixo lê a chave dos *Secrets* do Colab (ícone 🔑 na barra lateral, "
        "nome `OPENALEX_API_KEY`) ou pergunta em campo oculto.",
    ))
    C.append(code(
        'EMAIL = ""  # @param {type:"string", placeholder:"seu.email@instituicao.br"}\n'
        'USAR_API_KEY = True  # @param {type:"boolean"}\n'
        "\n"
        "from getpass import getpass\n"
        "\n"
        "_chave = None\n"
        "if USAR_API_KEY:\n"
        "    try:  # 1ª opção: Secrets do Colab (🔑 na barra lateral)\n"
        "        from google.colab import userdata\n"
        "        _chave = userdata.get('OPENALEX_API_KEY')\n"
        "        print('Chave lida dos Secrets do Colab.')\n"
        "    except Exception:\n"
        "        _chave = getpass('Cole sua OpenAlex API key (Enter para seguir sem ela): ') or None\n"
        "\n"
        "credenciais = Credentials(mailto=EMAIL, api_key=_chave)\n"
        "cliente = OpenAlexClient(credenciais)\n"
        "print('Credencial configurada →', credenciais.describe())",
        titulo="Preencha o seu e-mail e rode esta célula",
    ))

    # ------------------------------------------------------- 2.1 extração
    C.append(md(
        "---",
        "# Parte 2 — Atividades práticas",
        "",
        "## 2.1 Pesquisa e extração de dados",
        "",
        "### Escolha o seu recorte",
        "",
        "| Nível | O que preencher em `IDENTIFICADOR` | Onde achar | Exemplo |",
        "|---|---|---|---|",
        "| `pais` | código ISO de 2 letras | — | `BR`, `PT`, `AR` |",
        "| `instituicao` | **o ROR da instituição** | [ror.org](https://ror.org) — busque pelo nome | `041akq887` (UFSC) |",
        "| `pesquisador` | o ORCID | [orcid.org](https://orcid.org) | `0000-0002-8338-1931` |",
        "| `fonte` | o ISSN do periódico | [portal.issn.org](https://portal.issn.org) | `1518-2924` |",
        "",
        "O ROR pode ser colado inteiro (`https://ror.org/041akq887`) ou só o código "
        "(`041akq887`) — a função normaliza os dois.",
        "",
        "**Alguns RORs para testar:** UFSC `041akq887` · IBICT `04sk9pv44` · "
        "CEFET-MG `0384j8v12` · USP `036rp1748` · Univ. do Minho `037wpkx04`",
    ))
    C.append(code(
        'NIVEL = "instituicao"  # @param ["pais", "instituicao", "pesquisador", "fonte"]\n'
        'IDENTIFICADOR = "041akq887"  # @param {type:"string", placeholder:"digite o ROR da instituição"}\n'
        "ANO_INICIO = 2020  # @param {type:\"integer\"}\n"
        "ANO_FIM = 2024  # @param {type:\"integer\"}\n"
        'SOMENTE_ARTIGOS = True  # @param {type:"boolean"}\n'
        "\n"
        "tipos = ['article', 'review'] if SOMENTE_ARTIGOS else None\n"
        "filtro = montar_filtro(NIVEL, IDENTIFICADOR, ANO_INICIO, ANO_FIM, tipos=tipos)\n"
        "print('filter =', filtro)\n"
        "print()\n"
        "print('URL equivalente no navegador:')\n"
        "print(f'https://api.openalex.org/works?filter={filtro}')",
        titulo="Defina o recorte da análise",
    ))

    C.append(md(
        "### Dimensione antes de baixar",
        "",
        "Duas requisições respondem *\"quantos registros existem?\"* e *\"como se distribuem "
        "por via de acesso?\"* **sem baixar nada**. O OpenAlex agrega no servidor (`group_by`).",
        "",
        "Use isto para decidir o `MAX_REGISTROS` da célula seguinte: a extração baixa 200 "
        "registros por requisição, então 20 mil obras ≈ 100 requisições ≈ 1–2 minutos.",
    ))
    C.append(code(
        "resumo = resumo_rapido(cliente, filtro)\n"
        "print(f\"Total de obras no recorte: {resumo['total']:,}\".replace(',', '.'))\n"
        "print()\n"
        "for status, n in sorted(resumo['por_oa_status'].items(), key=lambda x: -x[1]):\n"
        "    pct = 100 * n / max(resumo['total'], 1)\n"
        "    rotulo = OA_STATUS_ROTULO.get(status, status)\n"
        "    print(f'  {rotulo:<10} {n:>8,}  {pct:5.1f}%'.replace(',', '.'))"
    ))

    C.append(md(
        "### Extraia",
        "",
        "Se o total acima for grande, comece com `MAX_REGISTROS = 2000` para a aula andar; "
        "depois rode o recorte inteiro em casa.",
    ))
    C.append(code(
        "MAX_REGISTROS = 3000  # @param {type:\"integer\"}\n"
        "\n"
        "def _progresso(baixados, total):\n"
        "    print(f'\\r  {baixados:,} / {total:,} obras'.replace(',', '.'), end='')\n"
        "\n"
        "t0 = time.time()\n"
        "df = extrair_works(cliente, filtro, max_registros=MAX_REGISTROS, on_progress=_progresso)\n"
        "print(f'\\n\\nPronto: {len(df):,} obras em {time.time() - t0:.0f}s'.replace(',', '.'))\n"
        "if cliente.last_rate_limit:\n"
        "    print('Cota:', cliente.last_rate_limit)\n"
        "df.head(3)",
        titulo="Baixar os dados",
    ))

    C.append(md(
        "### Confira o que veio",
        "",
        "Antes de calcular qualquer indicador, olhe os dados. Quantos anos? "
        "Quantos sem periódico identificado? A cobertura de APC é grande o bastante "
        "para o número significar alguma coisa?",
    ))
    C.append(code(
        "print(f'Obras: {len(df):,}'.replace(',', '.'))\n"
        "print(f\"Período: {df['ano'].min()}–{df['ano'].max()}\")\n"
        "print(f\"Sem periódico identificado: {df['fonte'].isna().sum():,}\".replace(',', '.'))\n"
        "print(f\"Com valor de APC pago: {df['apc_pago_usd'].notna().sum():,} \"\n"
        "      f\"({100 * df['apc_pago_usd'].notna().mean():.1f}% das obras)\".replace(',', '.'))\n"
        "print()\n"
        "display(df['tipo'].value_counts().head())\n"
        "display(df.dtypes.to_frame('tipo do campo').T)"
    ))

    C.append(code(
        "# Guarde o bruto — extrair de novo custa tempo e cota\n"
        "os.makedirs('dados', exist_ok=True)\n"
        "arquivo_bruto = f'dados/works_{NIVEL}_{ANO_INICIO}_{ANO_FIM}.csv'\n"
        "df.to_csv(arquivo_bruto, index=False)\n"
        "print('Salvo em', arquivo_bruto)"
    ))

    # ---------------------------------------------------- 2.2 indicadores
    C.append(md(
        "---",
        "## 2.2 Geração de indicadores",
        "",
        "`painel_completo` roda todos os indicadores de uma vez e devolve um dicionário "
        "de DataFrames. Cada um também pode ser chamado isoladamente.",
    ))
    C.append(code(
        "painel = painel_completo(df)\n"
        "\n"
        "for chave, valor in painel['gerais'].items():\n"
        "    print(f'{chave:<24} {valor}')"
    ))

    C.append(md(
        "### Como ler estes números",
        "",
        "- **taxa_oa** — % de obras com alguma versão em acesso aberto (qualquer via).",
        "- **taxa_diamante** — publicadas em periódicos abertos que **não cobram APC do autor**. "
        "É o indicador mais próximo de \"ciência aberta sem custo para quem publica\".",
        "- **taxa_em_repositorio** — % com texto completo depositado em repositório (via verde). "
        "Para um gestor de repositório, é *o* indicador.",
        "- **apc_total_usd** — ⚠️ **é um piso, não o gasto real.** O OpenAlex só conhece o valor "
        "quando consegue inferi-lo (via DOAJ/OpenAPC); acordos institucionais, descontos e "
        "isenções não aparecem. Sempre reporte junto a **cobertura** do dado.",
        "- **citacoes_por_obra** — a média é puxada por poucos casos extremos; nos gráficos "
        "usamos a **mediana**.",
    ))

    C.append(code(
        "# Distribuição por via de acesso\n"
        "painel['distribuicao_oa']"
    ))
    C.append(code(
        "# Evolução anual\n"
        "painel['serie_anual_oa']"
    ))
    C.append(code(
        "# APCs: repare na coluna `cobertura` antes de olhar o total\n"
        "painel['apc_anual']"
    ))
    C.append(code(
        "# Para onde foi o dinheiro\n"
        "painel['apc_editora']"
    ))
    C.append(code(
        "# Citação por via — leia a mediana, e leia como associação, não como causa\n"
        "painel['citacoes_status']"
    ))
    C.append(code(
        "# Onde a produção foi publicada\n"
        "painel['top_fontes']"
    ))

    # --------------------------------------------------- 2.3 visualização
    C.append(md(
        "---",
        "## 2.3 Visualização de dados",
        "",
        "Cada via de acesso tem **uma cor fixa** em todo o material — a cor identifica a via, "
        "nunca a posição no gráfico. As cinco vias abertas usam matizes distintos e "
        "\"Fechado\" é cinza: é a ausência de abertura, não uma sexta via.",
        "",
        "A ordem (diamante → híbrido → dourado → verde → bronze) foi escolhida para que "
        "cores vizinhas nas barras empilhadas continuem distinguíveis por leitores com "
        "daltonismo. Por isso não troque a ordem sem verificar o contraste.",
    ))
    C.append(code("fig = grafico_distribuicao_oa(painel['distribuicao_oa'])\nplt.show()"))
    C.append(code("fig = grafico_serie_oa(painel['serie_anual_oa'])\nplt.show()"))
    C.append(code("fig = grafico_composicao_anual(painel['serie_anual_status'])\nplt.show()"))
    C.append(code("fig = grafico_apc(painel['apc_anual'])\nplt.show()"))
    C.append(code("fig = grafico_citacoes(painel['citacoes_status'])\nplt.show()"))
    C.append(code(
        "if not painel['oa_area'].empty:\n"
        "    fig = grafico_oa_por_area(painel['oa_area'])\n"
        "    plt.show()\n"
        "else:\n"
        "    print('Poucas obras por área neste recorte.')"
    ))

    C.append(md(
        "### Salvar as figuras",
    ))
    C.append(code(
        "os.makedirs('figuras', exist_ok=True)\n"
        "figuras = {\n"
        "    'distribuicao_oa': grafico_distribuicao_oa(painel['distribuicao_oa']),\n"
        "    'serie_oa': grafico_serie_oa(painel['serie_anual_oa']),\n"
        "    'composicao_anual': grafico_composicao_anual(painel['serie_anual_status']),\n"
        "    'apc_anual': grafico_apc(painel['apc_anual']),\n"
        "    'citacoes_status': grafico_citacoes(painel['citacoes_status']),\n"
        "}\n"
        "for nome, figura in figuras.items():\n"
        "    figura.savefig(f'figuras/{nome}.png', dpi=200, bbox_inches='tight', facecolor='#fcfcfb')\n"
        "plt.close('all')\n"
        "print('Figuras salvas em figuras/')"
    ))

    # --------------------------------------------------------- 3 dashboard
    C.append(md(
        "---",
        "# Parte 3 — Dashboard",
        "",
        "Os mesmos indicadores, agora num painel interativo montado com "
        "[**Vega**](https://vega.github.io/vega/): passe o mouse sobre qualquer marca para "
        "ver os números, e cada gráfico traz a tabela equivalente logo abaixo.",
        "",
        "O arquivo gerado é **autocontido** — os dados vão embutidos nele. Abre com um duplo "
        "clique, funciona offline (menos a biblioteca Vega, que vem do CDN) e pode ser enviado "
        "por e-mail ou publicado num site institucional.",
        "",
        "As mesmas *specs* Vega são consumidas pelo componente React "
        f"[`dashboard/VegaChart.tsx`]({REPO}/blob/main/dashboard/VegaChart.tsx) do repositório, "
        "se você quiser embutir os gráficos numa aplicação sua.",
    ))
    C.append(code(
        'TITULO_DASHBOARD = "Indicadores de Ciência Aberta"  # @param {type:"string"}\n'
        'SUBTITULO_DASHBOARD = ""  # @param {type:"string", placeholder:"ex.: UFSC, 2020–2024"}\n'
        "\n"
        "subtitulo = SUBTITULO_DASHBOARD or f'{NIVEL}: {IDENTIFICADOR} · {ANO_INICIO}–{ANO_FIM}'\n"
        "arquivo_dash = 'dashboard_oa.html'\n"
        "gerar_dashboard(painel, TITULO_DASHBOARD, subtitulo, arquivo_dash)\n"
        "\n"
        "tamanho = os.path.getsize(arquivo_dash) / 1024\n"
        "print(f'Dashboard gerado: {arquivo_dash} ({tamanho:.0f} KB)')",
        titulo="Gerar o dashboard",
    ))

    C.append(md("### Ver aqui no notebook"))
    C.append(code(
        "from IPython.display import HTML, display\n"
        "\n"
        "display(HTML(\n"
        "    f'<iframe srcdoc=\"{html.escape(open(arquivo_dash, encoding=\"utf-8\").read())}\" '\n"
        "    'style=\"width:100%;height:820px;border:1px solid #e4e3df;border-radius:8px\"></iframe>'\n"
        "))"
    ))

    C.append(md(
        "### Exportar tudo",
        "",
        "Além do HTML, vale levar uma planilha com os indicadores (uma aba por tabela) e "
        "as *specs* Vega em JSON, para reaproveitar os mesmos gráficos noutro lugar.",
    ))
    C.append(code(
        "import shutil\n"
        "\n"
        "# specs Vega separadas, para reaproveitar em outra aplicação\n"
        "salvar_specs(todas_as_specs(painel), 'specs_vega.json')\n"
        "\n"
        "# planilha com todos os indicadores, uma aba por tabela\n"
        "with pd.ExcelWriter('indicadores_oa.xlsx') as writer:\n"
        "    pd.DataFrame([painel['gerais']]).T.rename(columns={0: 'valor'}).to_excel(\n"
        "        writer, sheet_name='geral')\n"
        "    for nome, tabela in painel.items():\n"
        "        if isinstance(tabela, pd.DataFrame) and not tabela.empty:\n"
        "            tabela.to_excel(writer, sheet_name=nome[:31], index=False)\n"
        "\n"
        "shutil.make_archive('figuras_oa', 'zip', 'figuras')\n"
        "\n"
        "arquivos = [arquivo_dash, 'indicadores_oa.xlsx', 'specs_vega.json',\n"
        "            'figuras_oa.zip', arquivo_bruto]\n"
        "for arquivo in arquivos:\n"
        "    print(f'{os.path.getsize(arquivo) / 1024:8.0f} KB  {arquivo}')"
    ))

    C.append(md("### Baixar para o seu computador"))
    C.append(code(
        "try:\n"
        "    from google.colab import files\n"
        "    for arquivo in arquivos:\n"
        "        files.download(arquivo)\n"
        "except ImportError:\n"
        "    print('Fora do Colab: os arquivos já estão na pasta de trabalho.')"
    ))

    # --------------------------------------------- análise adicional via input
    C.append(md(
        "---",
        "# Nova análise em outro contexto",
        "",
        "As células seguintes permitem repetir a análise sem alterar os resultados "
        "da primeira consulta. As credenciais já configuradas são reaproveitadas.",
    ))
    C.append(code(
        "# Parâmetros da nova análise\n"
        "NIVEL_NOVA = input('Contexto (pais/instituicao/pesquisador/fonte): ').strip().lower()\n"
        "IDENTIFICADOR_NOVA = input('Identificador — ISO, ROR, ORCID ou ISSN: ').strip()\n"
        "ANO_INICIO_NOVA = int(input('Ano inicial: ').strip())\n"
        "ANO_FIM_NOVA = int(input('Ano final: ').strip())\n"
        "SOMENTE_ARTIGOS_NOVA = input('Considerar somente artigos e reviews? (s/n): ').strip().lower() in {'s', 'sim'}\n"
        "MAX_REGISTROS_NOVA = int(input('Máximo de obras para baixar [1000]: ').strip() or '1000')\n"
        "\n"
        "if NIVEL_NOVA not in {'pais', 'instituicao', 'pesquisador', 'fonte'}:\n"
        "    raise ValueError('Contexto inválido. Use pais, instituicao, pesquisador ou fonte.')\n"
        "if ANO_INICIO_NOVA > ANO_FIM_NOVA:\n"
        "    raise ValueError('O ano inicial não pode ser posterior ao ano final.')\n"
        "\n"
        "# Reaproveita o cliente já configurado; só verifica a conexão novamente.\n"
        "try:\n"
        "    credenciais_ok_nova = 'credenciais' in globals() and 'cliente' in globals()\n"
        "    if credenciais_ok_nova:\n"
        "        cliente.get('works', {'filter': 'publication_year:2024', 'per-page': 1, 'select': 'id'})\n"
        "        print('Credenciais existentes do notebook reaproveitadas.')\n"
        "        print(credenciais.describe())\n"
        "except Exception:\n"
        "    credenciais_ok_nova = False\n"
        "\n"
        "if not credenciais_ok_nova:\n"
        "    from getpass import getpass\n"
        "    email_nova = input('E-mail para o OpenAlex: ').strip()\n"
        "    chave_nova = getpass('OpenAlex API key (Enter para seguir sem ela): ') or None\n"
        "    credenciais = Credentials(mailto=email_nova, api_key=chave_nova)\n"
        "    cliente = OpenAlexClient(credenciais)\n"
        "    cliente.get('works', {'filter': 'publication_year:2024', 'per-page': 1, 'select': 'id'})\n"
        "    print('Novas credenciais verificadas com sucesso.')\n"
        "    print(credenciais.describe())\n"
        "\n"
        "tipos_nova = ['article', 'review'] if SOMENTE_ARTIGOS_NOVA else None\n"
        "filtro_nova = montar_filtro(NIVEL_NOVA, IDENTIFICADOR_NOVA, ANO_INICIO_NOVA, ANO_FIM_NOVA, tipos=tipos_nova)\n"
        "print('Filtro específico:', filtro_nova)",
        titulo="Defina os parâmetros da nova análise",
    ))
    C.append(code(
        "# Extração e visualização tabular\n"
        "resumo_nova = resumo_rapido(cliente, filtro_nova)\n"
        "print(f'Obras encontradas: {resumo_nova[\"total\"]:,}'.replace(',', '.'))\n"
        "\n"
        "def progresso_nova(baixados, total):\n"
        "    print(f'\\rBaixados: {baixados:,} / {total:,}'.replace(',', '.'), end='')\n"
        "\n"
        "df_nova = extrair_works(cliente, filtro_nova, max_registros=MAX_REGISTROS_NOVA, on_progress=progresso_nova)\n"
        "print(f'\\n\\nObras baixadas: {len(df_nova):,}'.replace(',', '.'))\n"
        "\n"
        "if df_nova.empty:\n"
        "    print('Nenhuma obra encontrada para este recorte.')\n"
        "else:\n"
        "    display(df_nova.head(20))\n"
        "    painel_nova = painel_completo(df_nova)\n"
        "    print('Indicadores gerais:')\n"
        "    display(pd.DataFrame([painel_nova['gerais']]))\n"
        "    tabelas_nova = {\n"
        "        'Distribuição por via de acesso': painel_nova['distribuicao_oa'],\n"
        "        'Série anual de acesso aberto': painel_nova['serie_anual_oa'],\n"
        "        'Composição anual por via': painel_nova['serie_anual_status'],\n"
        "        'APCs por ano': painel_nova['apc_anual'],\n"
        "        'APCs por editora': painel_nova['apc_editora'],\n"
        "        'Citações por via': painel_nova['citacoes_status'],\n"
        "        'Periódicos mais utilizados': painel_nova['top_fontes'],\n"
        "        'Acesso aberto por área': painel_nova['oa_area'],\n"
        "    }\n"
        "    for titulo, tabela in tabelas_nova.items():\n"
        "        print(f'\\n{titulo}:')\n"
        "        display(tabela) if tabela is not None and not tabela.empty else print('Sem dados disponíveis.')",
        titulo="Extrair e visualizar em tabelas",
    ))
    C.append(code(
        "# Dashboard da nova análise\n"
        "import html\n"
        "from IPython.display import HTML, display\n"
        "\n"
        "if df_nova.empty:\n"
        "    print('Não é possível gerar o dashboard: não foram encontradas obras.')\n"
        "else:\n"
        "    arquivo_dashboard_nova = f'dashboard_{NIVEL_NOVA}_{ANO_INICIO_NOVA}_{ANO_FIM_NOVA}.html'\n"
        "    gerar_dashboard(\n"
        "        painel_nova,\n"
        "        'Indicadores de Ciência Aberta',\n"
        "        f'{NIVEL_NOVA}: {IDENTIFICADOR_NOVA} · {ANO_INICIO_NOVA}–{ANO_FIM_NOVA}',\n"
        "        arquivo_dashboard_nova,\n"
        "    )\n"
        "    print(f'Dashboard salvo em: {arquivo_dashboard_nova}')\n"
        "    conteudo_dashboard_nova = open(arquivo_dashboard_nova, encoding='utf-8').read()\n"
        "    display(HTML(f'<iframe srcdoc=\"{html.escape(conteudo_dashboard_nova)}\" style=\"width:100%;height:820px;border:1px solid #e4e3df;border-radius:8px\"></iframe>'))",
        titulo="Gerar dashboard da nova análise",
    ))

    # ------------------------------------------------------- 4 exercícios
    C.append(md(
        "---",
        "# Parte 4 — Adapte ao seu contexto",
        "",
        "### Exercícios",
        "",
        "1. **Compare duas instituições.** Rode a extração duas vezes com RORs diferentes e "
        "coloque as duas séries no mesmo gráfico. *(Dica: dois gráficos lado a lado costumam "
        "ler melhor que duas linhas sobrepostas quando os volumes são muito diferentes.)*",
        "2. **Recorte por área.** Filtre `df` por `area` e refaça o painel — a taxa de abertura "
        "de Saúde e a de Humanidades quase nunca se parecem.",
        "3. **Sua própria produção.** Troque `NIVEL` para `pesquisador` e use o seu ORCID.",
        "4. **Um indicador novo.** Que % da produção está em periódicos **nacionais** abertos? "
        "*(Dica: o campo `fonte_editora` e o filtro `has_doi`.)*",
        "5. **APC evitável.** Quanto foi pago em APC para publicar em periódicos **híbridos** — "
        "isto é, em revistas que já cobram assinatura?",
        "",
        "### Vibe coding: peça ao LLM",
        "",
        "Todo o código está visível acima. Copie a função que quer mudar, cole num LLM e peça. "
        "Prompts que funcionam bem:",
        "",
        "```",
        "Aqui está minha função montar_filtro (cole o código).",
        "Adicione suporte a filtrar por financiador (funder) do OpenAlex,",
        "mantendo a mesma assinatura e as mensagens de erro em português.",
        "```",
        "",
        "```",
        "Tenho um DataFrame com as colunas: (cole df.dtypes).",
        "Escreva uma função que calcule, por ano, o % de obras em periódicos",
        "cuja fonte_editora está numa lista de editoras comerciais que eu passo",
        "como parâmetro. Retorne um DataFrame com ano, obras, percentual.",
        "```",
        "",
        "**Sempre confira o que o LLM devolveu**: rode em um recorte pequeno cujo resultado "
        "você consiga verificar na mão, e compare com a contagem do próprio OpenAlex "
        "(`cliente.count('works', {'filter': ...})`).",
        "",
        "---",
        "",
        "### Limites destes dados — leia antes de publicar qualquer número",
        "",
        "| Limite | O que fazer |",
        "|---|---|",
        "| **Vínculo institucional** é inferido pela afiliação declarada na publicação. Autor sem afiliação escrita fica de fora. | Compare o total do OpenAlex com o do seu repositório/CRIS antes de reportar. |",
        "| **`oa_status`** vem do Unpaywall e reflete o estado **hoje**, não na data da publicação. | Não use para série histórica de \"quando abriu\". |",
        "| **APC** só aparece quando o OpenAlex consegue inferir o valor. Acordos e isenções não aparecem. | Reporte sempre com a cobertura do dado. É um piso. |",
        "| **Citações** dependem da cobertura do OpenAlex, que difere de Scopus/WoS. | Não compare números de bases diferentes. |",
        "| Obras **sem DOI** têm metadados mais pobres. | Considere `has_doi:true` quando a qualidade importar mais que a completude. |",
        "",
        "### Para levar",
        "",
        f"- Repositório: [`{REPO}`]({REPO})",
        "- Documentação da API: [docs.openalex.org](https://docs.openalex.org)",
        "- Bracco, L. (2022). *Promoting open science through bibliometrics: A practical guide "
        "to building an open access monitor.* Liber Quarterly, 32, 1–18. "
        "[doi:10.53377/lq.11545](https://doi.org/10.53377/lq.11545)",
        "",
        "Dados do OpenAlex sob licença **CC0**. Este material sob **CC BY 4.0**.",
    ))

    return {
        "nbformat": 4,
        "nbformat_minor": 0,
        "metadata": {
            "colab": {"provenance": [], "toc_visible": True, "name": "OA_Monitor_Workshop_ConfOA2026.ipynb"},
            "kernelspec": {"name": "python3", "display_name": "Python 3"},
            "language_info": {"name": "python"},
        },
        "cells": C,
    }


def main() -> None:
    nb = construir()
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
    n_code = sum(1 for c in nb["cells"] if c["cell_type"] == "code")
    print(f"{SAIDA.relative_to(RAIZ)}: {len(nb['cells'])} células ({n_code} de código)")


if __name__ == "__main__":
    main()

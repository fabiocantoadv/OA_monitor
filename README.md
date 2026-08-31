# OA_monitor — Monitorando a Ciência Aberta

Material do workshop **"Monitorando a Ciência Aberta: geração de indicadores com dados do
OpenAlex"**, apresentado na **ConfOA 2026**.

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fabiocantoadv/OA_monitor/blob/main/notebooks/OA_Monitor_Workshop_ConfOA2026.ipynb)
[![Licença: CC BY 4.0](https://img.shields.io/badge/licen%C3%A7a-CC%20BY%204.0-blue)](LICENSE)

Extrai dados do [OpenAlex](https://openalex.org), calcula indicadores de Ciência Aberta
(taxa de abertura, vias de publicação, APCs, citação) para **um país, uma instituição ou
um pesquisador**, e gera um dashboard interativo em [Vega](https://vega.github.io/vega/).

## Comece por aqui

**No workshop:** clique no botão *Abrir no Colab* acima. Não precisa instalar nada.

**Na sua máquina:**

```bash
git clone https://github.com/fabiocantoadv/OA_monitor.git
cd OA_monitor
pip install -r requirements.txt
```

```python
import sys; sys.path.insert(0, "src")
from oa_monitor import *

cliente = OpenAlexClient(Credentials(mailto="voce@instituicao.br", api_key="sua-chave"))

filtro = montar_filtro("instituicao", "041akq887", 2020, 2024, tipos=["article", "review"])
df = extrair_works(cliente, filtro, max_registros=3000)

painel = painel_completo(df)
print(painel["gerais"])

gerar_dashboard(painel, "Indicadores de Ciência Aberta", "UFSC, 2020–2024", "dashboard.html")
```

## Credencial individual do OpenAlex

Cada participante usa a **sua própria** credencial. São duas coisas diferentes:

| | O que é | Como obter | Obrigatório? |
|---|---|---|---|
| **`mailto`** | seu e-mail, enviado em toda requisição | você já tem | **sim** |
| **`api_key`** | chave pessoal, com cota diária só sua | conta gratuita em [openalex.org](https://openalex.org) → *Settings* → *API key* | recomendada |

O e-mail coloca você no *polite pool* (respostas mais estáveis). A chave é gratuita para a
maior parte dos usos e dá a cada pessoa uma cota diária individual.

**Numa sala de aula isso é decisivo:** sem chave, todos os participantes saem pelo mesmo IP
e dividem uma única cota — depois de algumas dezenas de consultas a API passa a recusar as
requisições de todo mundo.

> 🔒 **Nunca comite a sua chave.** No Colab, use os *Secrets* (🔑 na barra lateral) com o
> nome `OPENALEX_API_KEY`. Localmente, use variáveis de ambiente:
>
> ```bash
> export OPENALEX_MAILTO="voce@instituicao.br"
> export OPENALEX_API_KEY="sua-chave"
> ```
> ```python
> cliente = OpenAlexClient(Credentials.from_env())
> ```
>
> O `.gitignore` já bloqueia `.env`, `*.key` e a pasta `data/`.

Detalhes em [`docs/credencial-openalex.md`](docs/credencial-openalex.md).

## O que tem aqui

```
notebooks/    o notebook do workshop (Colab) — autocontido
src/oa_monitor/
  config.py       credenciais individuais (mailto + api_key)
  api.py          cliente HTTP: retry, paginação por cursor, leitura de cota
  extract.py      filtros por país / ROR / ORCID / ISSN e achatamento dos registros
  indicators.py   os indicadores de Ciência Aberta
  viz.py          gráficos matplotlib
  vega.py         specs Vega v5
  dashboard.py    dashboard HTML autocontido
dashboard/    componente React VegaChart.tsx + como reaproveitar as specs
docs/         programa, dicionário de indicadores, guia da API, guia do participante
tools/        build_notebook.py — gera o notebook a partir de src/
tests/        testes sem rede
```

**O notebook é gerado a partir de `src/`**, então os dois nunca ficam fora de sincronia.
Ao alterar um módulo, rode:

```bash
python tools/build_notebook.py
python tests/test_pipeline.py && python tests/test_notebook.py
```

## Indicadores gerados

| Indicador | O que mede |
|---|---|
| Taxa de acesso aberto | % das obras com alguma versão aberta |
| Distribuição por via | diamante, híbrido, dourado, verde, bronze, fechado |
| Série anual | evolução da taxa e da composição das vias |
| Presença em repositório | % com texto completo depositado (via verde) |
| Presença no DOAJ | % publicada em periódico indexado no DOAJ |
| APCs | total e média por ano, e por editora — **sempre com a cobertura do dado** |
| Citação por via | mediana de citações e FWCI por via de acesso |
| Abertura por área | taxa de abertura por grande área do conhecimento |
| Periódicos mais usados | onde a produção foi publicada e a abertura de cada título |

Definições e ressalvas em [`docs/indicadores.md`](docs/indicadores.md).

## Dashboard

`gerar_dashboard()` escreve um HTML **autocontido**: os dados vão embutidos, abre com um
duplo clique e pode ser enviado por e-mail ou publicado num site institucional. Os gráficos
são interativos (tooltip em toda marca) e cada um traz a tabela equivalente.

As mesmas *specs* Vega alimentam o componente React
[`dashboard/VegaChart.tsx`](dashboard/VegaChart.tsx), se você quiser embutir os gráficos numa
aplicação sua — veja [`dashboard/README.md`](dashboard/README.md).

## Limites destes dados

Leia antes de publicar qualquer número:

- **Vínculo institucional** é inferido da afiliação declarada na publicação; autor sem
  afiliação escrita fica de fora. Compare com o seu repositório/CRIS antes de reportar.
- **`oa_status`** vem do Unpaywall e reflete o estado **hoje**, não na data da publicação.
- **APC** só aparece quando o OpenAlex consegue inferir o valor (via DOAJ/OpenAPC);
  acordos institucionais, descontos e isenções não aparecem. **É um piso, não o gasto real.**
- **Citações** dependem da cobertura do OpenAlex, que difere de Scopus e Web of Science.

## Créditos

Fabio Lorensi do Canto (UFSC/IBICT) · Thiago M. R. Dias (CEFET-MG/IBICT) ·
Marcel Garcia de Souza (IBICT) · Washington L. R. Carvalho Segundo (IBICT)

Referência: Bracco, L. (2022). *Promoting open science through bibliometrics: A practical
guide to building an open access monitor.* Liber Quarterly, 32, 1–18.
[doi:10.53377/lq.11545](https://doi.org/10.53377/lq.11545)

Dados do OpenAlex sob **CC0**. Este material sob **[CC BY 4.0](LICENSE)**.

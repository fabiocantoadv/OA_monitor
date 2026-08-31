# Dicionário de indicadores

Cada indicador aqui traz **o que mede**, **como é calculado** e **o que ele não diz**.
A última coluna é a que mais importa na hora de reportar um número a um gestor.

## Vias de acesso aberto

O campo `open_access.oa_status` do OpenAlex (herdado do Unpaywall) classifica cada obra
em uma via:

| Via | `oa_status` | Definição |
|---|---|---|
| **Diamante** | `diamond` | periódico integralmente aberto que **não cobra APC** do autor |
| **Dourado** | `gold` | periódico integralmente aberto, em geral **com APC** |
| **Híbrido** | `hybrid` | periódico de assinatura em que **aquele artigo** foi aberto mediante pagamento |
| **Verde** | `green` | versão depositada em **repositório**, com o artigo fechado no periódico |
| **Bronze** | `bronze` | legível no site do editor, **sem licença aberta** — pode ser fechado a qualquer momento |
| **Fechado** | `closed` | sem versão aberta localizada |

A ordem acima é a usada em todos os gráficos, e **cada via tem uma cor fixa** em todo o
material — a cor identifica a via, nunca a posição no gráfico.

> **Bronze não é acesso aberto pleno.** É acesso gratuito, revogável e sem direito de
> reúso. Relatórios que somam bronze ao total de "aberto" inflam a taxa; vale sempre
> mostrar a distribuição, não só o total.

---

## Indicadores

### Taxa de acesso aberto — `taxa_oa`

**O quê:** % das obras com alguma versão aberta (qualquer via).
**Cálculo:** `is_oa == True` sobre o total.
**Não diz:** *como* está aberto. Uma taxa de 70% composta de bronze é muito diferente de
uma composta de diamante. Sempre leia junto com a distribuição por via.

### Taxa diamante — `taxa_diamante`

**O quê:** % publicada em periódicos abertos que não cobram do autor.
**Cálculo:** `oa_status == "diamond"` sobre o total.
**Por que importa:** é o indicador mais próximo de "ciência aberta sem custo para quem
publica" — central em contextos onde o APC é uma barreira. É também o indicador em que a
produção latino-americana costuma se destacar, por causa do modelo SciELO/Redalyc.

### Presença em repositório — `taxa_em_repositorio`

**O quê:** % com texto completo depositado em algum repositório.
**Cálculo:** `open_access.any_repository_has_fulltext == True`.
**Para quem gerencia repositório institucional, é *o* indicador.** Cuidado: mede depósito
em *qualquer* repositório (inclusive PubMed Central, arXiv, ResearchGate não conta), não
apenas no seu.

### Presença no DOAJ — `taxa_no_doaj`

**O quê:** % publicada em periódico indexado no [DOAJ](https://doaj.org).
**Cálculo:** `primary_location.source.is_in_doaj == True`.
**Não diz:** que o artigo está aberto — diz que o *periódico* é reconhecidamente aberto.

### APCs — `apc_total_usd`, `apc_medio_usd`, `cobertura`

**O quê:** quanto foi pago em taxas de publicação, por ano e por editora.
**Cálculo:** soma de `apc_paid.value_usd`.

> ⚠️ **É um piso, não o gasto real.** O OpenAlex só conhece o valor quando consegue
> inferi-lo (via DOAJ/OpenAPC). Acordos institucionais *read & publish*, descontos,
> isenções e pagamentos por fora não aparecem. A tabela `apc_anual` traz sempre a coluna
> **`cobertura`** — o % de obras do ano para as quais existe valor. **Nunca reporte o
> total sem a cobertura ao lado.** Cobertura de 15% significa que o número real é
> provavelmente várias vezes maior.

Há também `apc_cobrado_usd` (`apc_list`), o preço de tabela do periódico — útil para
estimar o custo potencial de uma produção, mesmo quando não se sabe o que foi pago.

### Citação por via — `citacoes_status`

**O quê:** mediana de citações e de FWCI por via de acesso.
**Cálculo:** mediana de `cited_by_count` e de `fwci`, agrupadas por `oa_status`.

**Leia a mediana, não a média:** a distribuição de citações é fortemente assimétrica e a
média é dominada por poucos artigos muito citados.

**E leia como associação, não como causa.** Obras abertas e fechadas não são amostras
comparáveis: diferem em área, idioma, tipo de periódico, ano e prestígio. A diferença de
citação entre vias não mede o "efeito da abertura" — mede a diferença entre dois conjuntos
que já eram diferentes. O FWCI mediano ameniza (normaliza por área e ano), mas não
resolve.

### Abertura por área — `oa_area`

**O quê:** taxa de abertura por grande área (`primary_topic.field`).
**Cálculo:** média de `is_oa` por área, restrita a áreas com pelo menos 10 obras.
**Por que o mínimo:** com 3 obras numa área, uma aberta vira "33%" e polui o gráfico.

### Periódicos mais usados — `top_fontes`

**O quê:** onde a produção foi publicada, com a taxa de abertura de cada título.
**Uso típico:** identificar os títulos que concentram a produção e checar quais deles são
abertos — insumo direto para negociação de acordos e para política institucional.

---

## Campos usados do OpenAlex

| Campo da API | Coluna no DataFrame |
|---|---|
| `open_access.is_oa` | `is_oa` |
| `open_access.oa_status` | `oa_status` |
| `open_access.any_repository_has_fulltext` | `em_repositorio` |
| `apc_paid.value_usd` | `apc_pago_usd` |
| `apc_list.value_usd` | `apc_cobrado_usd` |
| `primary_location.source.is_in_doaj` | `fonte_no_doaj` |
| `primary_location.source.host_organization_name` | `fonte_editora` |
| `cited_by_count` | `citacoes` |
| `fwci` | `fwci` |
| `primary_topic.field.display_name` | `area` |

Esquema completo: [docs.openalex.org/api-entities/works](https://docs.openalex.org/api-entities/works)

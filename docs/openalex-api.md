# Guia rápido da API do OpenAlex

Base: `https://api.openalex.org` · Documentação: [docs.openalex.org](https://docs.openalex.org)

Tudo o que o notebook faz pode ser feito **colando uma URL no navegador**. É assim que se
aprende a API: monte a URL, olhe o JSON, depois automatize.

## Anatomia de uma consulta

```
https://api.openalex.org/works
  ?filter=authorships.institutions.ror:https://ror.org/041akq887,publication_year:2020-2024
  &group_by=open_access.oa_status
  &mailto=voce@instituicao.br
```

| Parâmetro | Para quê |
|---|---|
| `filter` | recorta o conjunto; critérios separados por vírgula (**E**), alternativas por `\|` (**OU**) |
| `select` | escolhe os campos que voltam — deixa a resposta muito menor |
| `group_by` | agrega no servidor; devolve contagens, **não** os registros |
| `per-page` | até 200 |
| `cursor` | paginação sem teto; comece com `*` e siga o `meta.next_cursor` |
| `sort` | ex.: `cited_by_count:desc` |
| `mailto` / `api_key` | identificação (ver [credencial-openalex.md](credencial-openalex.md)) |

## Filtros que este material usa

| Recorte | Filtro |
|---|---|
| País | `authorships.institutions.country_code:BR` |
| Instituição (ROR) | `authorships.institutions.ror:https://ror.org/041akq887` |
| Pesquisador (ORCID) | `authorships.author.orcid:https://orcid.org/0000-0002-8338-1931` |
| Periódico (ISSN) | `primary_location.source.issn:1518-2924` |
| Período | `publication_year:2020-2024` |
| Tipo | `type:article\|review` |
| Só com DOI | `has_doi:true` |
| Só aberto | `is_oa:true` |
| Via específica | `open_access.oa_status:diamond` |
| No DOAJ | `primary_location.source.is_in_doaj:true` |

Combinam-se com vírgula:
`filter=authorships.institutions.ror:https://ror.org/041akq887,publication_year:2024,is_oa:true`

## Dois truques que economizam muito tempo

### 1. `group_by` responde sem baixar nada

```
/works?filter=institutions.country_code:BR,publication_year:2024&group_by=open_access.oa_status
```

Uma requisição, e você já tem a distribuição inteira. Use antes de decidir extrair.
Só um `group_by` por requisição.

### 2. `select` encolhe a resposta

Pedir os 40 campos de um work quando você usa 15 multiplica o tempo de download.
`extract.WORK_FIELDS` lista exatamente os campos que este material usa.

## Paginação: use cursor

A paginação por `page` para em 10 mil registros. A por cursor não tem teto:

```python
cursor = "*"
while cursor:
    r = requests.get(url, params={..., "cursor": cursor, "per-page": 200}).json()
    ...
    cursor = r["meta"]["next_cursor"]
```

É o que `OpenAlexClient.paginate` faz.

## Cota

Modelo de créditos: 1 crédito por consulta a um registro, 10 por consulta de lista.
No plano gratuito com chave, na faixa de 100 mil créditos/dia. Os cabeçalhos
`X-RateLimit-Remaining` e `X-RateLimit-Reset` vêm em toda resposta e ficam guardados em
`cliente.last_rate_limit`.

## Entidades

| Endpoint | O quê |
|---|---|
| `/works` | publicações — o foco deste workshop |
| `/authors` | autores |
| `/institutions` | instituições (busque o ROR aqui: `/institutions?search=UFSC`) |
| `/sources` | periódicos e repositórios |
| `/funders` | financiadores |
| `/topics` | classificação temática |

Achar o ROR de uma instituição pela própria API:

```
https://api.openalex.org/institutions?search=Universidade Federal de Santa Catarina
```

O campo `ror` vem no primeiro resultado.

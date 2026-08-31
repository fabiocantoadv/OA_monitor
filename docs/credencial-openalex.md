# Credencial individual do OpenAlex

## Por que cada participante precisa da sua

O OpenAlex limita o uso da API por **cota diária de créditos**. Quem não se identifica é
contado **pelo endereço IP**. Numa sala de aula com 30 pessoas na mesma rede Wi-Fi, isso
significa uma cota só, dividida por todo mundo — e as requisições começam a falhar para
todos ao mesmo tempo, no meio da atividade prática.

Com uma chave individual, cada participante tem a própria cota.

## As duas formas de se identificar

### 1. `mailto` — obrigatório neste material

Seu e-mail, enviado em cada requisição. Coloca você no **polite pool** do OpenAlex, que
tem respostas mais estáveis. Não exige cadastro nenhum.

```
https://api.openalex.org/works?filter=...&mailto=voce@instituicao.br
```

### 2. `api_key` — gratuita e recomendada

1. Acesse [openalex.org](https://openalex.org) e crie uma conta (gratuita).
2. Vá em **Settings → API key**.
3. Copie a chave.

```
https://api.openalex.org/works?filter=...&api_key=SUA_CHAVE
```

A chave dá uma **cota diária individual** (na faixa de 100 mil créditos/dia no plano
gratuito — consultas de lista custam 10 créditos, consultas a um registro específico
custam 1). Assinaturas Premium elevam esse teto e liberam filtros extras.

Para conferir quanto você já gastou:

```python
cliente.rate_limit_status()      # endpoint /rate-limit, exige api_key
cliente.last_rate_limit          # cabeçalhos da última requisição
```

## Como guardar a chave sem vazá-la

### No Google Colab — Secrets

1. Ícone **🔑** na barra lateral esquerda.
2. **+ Adicionar novo secret**, nome `OPENALEX_API_KEY`, cole o valor.
3. Ative o botão **Acesso ao notebook**.

O notebook lê o secret sozinho. A chave não fica salva no `.ipynb`, então você pode
compartilhar o notebook sem risco.

### Localmente — variáveis de ambiente

```bash
export OPENALEX_MAILTO="voce@instituicao.br"
export OPENALEX_API_KEY="sua-chave"
```

```python
from oa_monitor import Credentials, OpenAlexClient
cliente = OpenAlexClient(Credentials.from_env())
```

### O que **não** fazer

- ❌ escrever a chave direto numa célula do notebook e salvar
- ❌ comitar um `.env` (o `.gitignore` deste repositório já bloqueia)
- ❌ compartilhar a chave com colegas — ela é individual, e a cota é dela

Se a chave vazar, revogue-a em *Settings → API key* e gere outra.

## Diagnóstico rápido

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| `403 Forbidden` | chave inválida, ou requisição sem identificação | confira `mailto` e `api_key` na célula de configuração |
| `429 Too Many Requests` | cota esgotada | espere o reset (cabeçalho `X-RateLimit-Reset`) ou use uma chave individual |
| Muito lento | fora do polite pool | preencha o `mailto` |
| `0 obras` | filtro sem resultado | abra a URL impressa pela célula no navegador e veja o `meta.count` |

Referência: [docs.openalex.org — rate limits and authentication](https://docs.openalex.org/how-to-use-the-api/rate-limits-and-authentication)

# Guia do participante

## Antes do workshop — 10 minutos

### 1. Conta no OpenAlex e sua API key

1. Acesse [openalex.org](https://openalex.org) e crie uma conta (gratuita).
2. Vá em **Settings → API key** e copie a chave.
3. Guarde-a onde possa colar depois — você vai precisar dela na primeira célula.

Sem chave o workshop também funciona, mas todos os participantes dividem uma cota única
pela rede do local e as consultas podem começar a falhar no meio da atividade.

### 2. Conta Google

O notebook roda no Google Colab. Se você já usa Gmail, já tem.

### 3. Tenha à mão o identificador que quer analisar

| Se você quer analisar… | Precisa de… | Onde achar |
|---|---|---|
| uma instituição | o **ROR** | [ror.org](https://ror.org) — busque pelo nome |
| um pesquisador | o **ORCID** | [orcid.org](https://orcid.org) |
| um país | o código de 2 letras | `BR`, `PT`, `AR`, `MX`… |
| um periódico | o **ISSN** | [portal.issn.org](https://portal.issn.org) |

**Alguns RORs:** UFSC `041akq887` · IBICT `04sk9pv44` · CEFET-MG `0384j8v12` ·
USP `036rp1748` · Universidade do Minho `037wpkx04`

---

## Durante o workshop

### Abrir o notebook

Clique no botão **Abrir no Colab** no [README](../README.md) do repositório e, no Colab,
faça **Arquivo → Salvar uma cópia no Drive**. Assim as suas alterações ficam com você.

### Guardar a chave com segurança

No Colab, clique no ícone **🔑** na barra lateral esquerda:

1. **+ Adicionar novo secret**
2. Nome: `OPENALEX_API_KEY`
3. Valor: cole a sua chave
4. Ative **Acesso ao notebook**

O notebook lê o secret sozinho — a chave não fica gravada no arquivo.

### Rodar

`Ambiente de execução → Executar tudo`, ou célula a célula com **Shift+Enter**.
Os campos de formulário (e-mail, ROR, anos) são preenchidos direto na interface, sem
mexer no código.

---

## Se algo der errado

| O que aparece | O que fazer |
|---|---|
| `Informe um e-mail válido em mailto` | preencha o campo **EMAIL** na célula 0.3 e rode de novo |
| `ROR inválido` | use só o código (`041akq887`) ou a URL completa; confira em [ror.org](https://ror.org) |
| `403 Forbidden` | chave errada ou ausente — confira nos Secrets |
| `429 Too Many Requests` | cota esgotada; use a sua chave individual, ou espere |
| `0 obras` | abra no navegador a URL que a célula imprimiu e veja o `meta.count` — o filtro pode estar vazio mesmo |
| Extração muito lenta | baixe `MAX_REGISTROS` para 1000 e siga; rode o recorte completo depois |
| `NameError: name 'cliente' is not defined` | você pulou uma célula — `Ambiente de execução → Executar tudo` |

Se travar de vez: `Ambiente de execução → Reiniciar sessão e executar tudo`.

---

## Depois do workshop

Tudo o que você gerou pode ser baixado pela última célula: o dashboard HTML, a planilha de
indicadores, as figuras em alta resolução, as specs Vega e o CSV bruto.

Para reproduzir na sua instituição, o repositório
[`fabiocantoadv/OA_monitor`](https://github.com/fabiocantoadv/OA_monitor) traz o mesmo
código como pacote Python (`src/oa_monitor/`), instalável e importável em qualquer script.

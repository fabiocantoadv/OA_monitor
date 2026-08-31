# Programa do workshop — 3 horas

**Monitorando a Ciência Aberta: geração de indicadores com dados do OpenAlex**
ConfOA 2026

## Objetivo

Capacitar os participantes a gerar indicadores de monitoramento da Ciência Aberta — taxas
de abertura, vias de publicação, custos com APC — em diferentes contextos (pesquisador,
instituição, agência de financiamento, país), a partir de dados extraídos da API do
OpenAlex.

## Público

Gestores de repositórios, bibliotecários, gestores de dados de pesquisa, decisores
políticos e gestores de ciência. **Não é preciso saber programar** — o notebook roda
inteiro sem que ninguém precise escrever código do zero.

## Requisitos

- Acesso à internet e projetor.
- Cada participante com um computador (ou equipamento pessoal).
- **Antes do workshop:** criar uma conta gratuita em [openalex.org](https://openalex.org)
  e ter à mão a sua API key (*Settings → API key*). Ver
  [`guia-participante.md`](guia-participante.md).
- Nada a instalar: tudo roda no Google Colab.

---

## Parte 1 — Conceitos introdutórios (~70 min)

### 1.1 Indicadores bibliométricos (20 min)
- Métrica × indicador: quando um número vira um indicador
- Contagem, normalização por área e por ano; o problema das comparações
- O que um indicador não pode fazer sozinho

### 1.2 Indicadores de Ciência Aberta (30 min)
- Modelos de acesso: diamante, dourado, híbrido, verde, bronze — e por que bronze não é
  acesso aberto pleno
- APCs e o custo da abertura; o que os dados públicos conseguem e não conseguem mostrar
- O que monitorar em cada nível: pesquisador, instituição, financiador, país
- Referência: Bracco (2022), *Building an open access monitor*

### 1.3 Introdução ao OpenAlex (20 min)
- O que é, o que cobre, como se compara a Scopus/WoS
- Entidades: works, authors, institutions, sources, funders, topics
- Identificadores persistentes: DOI, **ROR**, ORCID, ISSN
- Como se faz uma requisição a uma API; a URL como consulta
- **Demonstração ao vivo:** montar uma consulta no navegador e ler o JSON

**Intervalo — 10 min**

---

## Parte 2 — Atividades práticas (~90 min)

Notebook: [`OA_Monitor_Workshop_ConfOA2026.ipynb`](../notebooks/OA_Monitor_Workshop_ConfOA2026.ipynb)

### 2.0 Preparação (10 min)
- Abrir o notebook no Colab e salvar uma cópia no Drive
- Configurar a **credencial individual**: e-mail e API key nos Secrets
- Rodar as células de código de apoio

### 2.1 Pesquisa e extração (25 min)
- Escolher o recorte: país, **instituição (pelo ROR)**, pesquisador (pelo ORCID) ou periódico
- Dimensionar antes de baixar: `count` e `group_by` sem trazer registro nenhum
- Extrair, conferir a qualidade do que veio, salvar o bruto

### 2.2 Geração de indicadores (30 min)
- Taxa de abertura, distribuição por via, série anual
- APCs — e a leitura correta da **cobertura** do dado
- Citação por via: por que mediana, e por que não é causa
- Discussão em grupo: o que cada número significaria no contexto de cada participante

### 2.3 Visualização e dashboard (25 min)
- Gráficos e as escolhas por trás deles (cor fixa por via, um eixo por gráfico, tabela
  sempre disponível)
- Gerar o dashboard Vega autocontido e baixá-lo
- Exportar a planilha de indicadores

---

## Encerramento (~20 min)

- **Vibe coding:** adaptar o código com apoio de um LLM — prompts que funcionam, e como
  conferir o que o modelo devolveu
- Limites dos dados: o que não publicar sem checar
- Como levar isto para a sua instituição
- Perguntas

## Resultados de aprendizagem

Ao final, espera-se que os participantes sejam capazes de:

1. compreender os principais conceitos e indicadores de Ciência Aberta;
2. entender o funcionamento de APIs de bases de dados;
3. aplicar técnicas básicas de processamento de dados;
4. gerar e interpretar indicadores de Ciência Aberta;
5. usar notebooks no Colab para reproduzir a análise em outros contextos;
6. empregar LLMs como apoio à codificação e ao processamento de dados.

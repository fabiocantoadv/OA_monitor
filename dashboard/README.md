# Dashboard

Duas formas de usar os mesmos gráficos.

## 1. HTML autocontido (o caminho do workshop)

```python
from oa_monitor import painel_completo, gerar_dashboard

painel = painel_completo(df)
gerar_dashboard(painel, "Indicadores de Ciência Aberta", "UFSC, 2020–2024", "dashboard.html")
```

Gera um arquivo único com os dados embutidos: abre com duplo clique, é interativo
(tooltip em toda marca), traz a tabela de cada gráfico e pode ser enviado por e-mail ou
publicado num site institucional. A única dependência externa é a biblioteca Vega, vinda
do CDN — para uso totalmente offline, baixe `vega.min.js` e troque o `<script src=...>`
por um `<script>` com o conteúdo do arquivo.

## 2. Componente React — `VegaChart.tsx`

Para embutir os gráficos numa aplicação sua. O componente recebe uma spec Vega e a
renderiza num canvas, com hover ativo e limpeza da view ao desmontar.

Exporte as specs do notebook:

```python
from oa_monitor import todas_as_specs, salvar_specs
salvar_specs(todas_as_specs(painel), "specs_vega.json")
```

E use:

```tsx
import specs from "./specs_vega.json";
import { VegaChart } from "./VegaChart";

export function PainelOA() {
  return (
    <div className="grid">
      <VegaChart spec={specs.distribuicao} />
      <VegaChart spec={specs.serie_oa} />
      <VegaChart spec={specs.composicao} />
      <VegaChart spec={specs.apc} />
      <VegaChart spec={specs.citacoes} />
    </div>
  );
}
```

```bash
npm install vega
```

`onViewReady` dá acesso à view para exportar a imagem:

```tsx
const [view, setView] = useState<{ toImageURL: (t: "png" | "svg") => Promise<string> } | null>(null);
// ...
<VegaChart spec={specs.composicao} onViewReady={setView} />
<button onClick={async () => window.open(await view!.toImageURL("png"))}>Baixar PNG</button>
```

> **Passe uma spec estável.** O `useEffect` do componente depende de `spec` e de
> `onViewReady`: se você montar o objeto da spec dentro do render, ele é recriado a cada
> ciclo e o gráfico se redesenha sem parar. Use `useMemo` para a spec e `useCallback`
> para o handler.

## As specs

| Chave | Gráfico | Forma |
|---|---|---|
| `distribuicao` | obras por via de acesso | barras horizontais |
| `serie_oa` | taxa de abertura por ano | linha |
| `composicao` | vias por ano | barras empilhadas 100% |
| `apc` | APC pago por ano | barras |
| `citacoes` | citações por via | barras |

São specs **Vega v5** (não Vega-Lite) — o formato que `vega.parse` aceita direto.

### Regras de desenho

Valem para todos os gráficos, no notebook e aqui:

- **Uma cor fixa por via de acesso.** A cor identifica a via, nunca a posição. Filtrar
  categorias não repinta as que sobraram.
- **"Fechado" é cinza**, deliberadamente acromático: é a ausência de abertura, não uma
  sexta via.
- **A ordem diamante → híbrido → dourado → verde → bronze** foi verificada para que cores
  vizinhas nas barras empilhadas continuem distinguíveis por leitores com daltonismo
  (ΔE ≥ 8 em todos os pares adjacentes, protanopia/deuteranopia/tritanopia). Não reordene
  sem refazer essa verificação.
- **Um eixo de medida por gráfico.** Nunca dois eixos y — duas medidas de escalas
  diferentes viram dois gráficos.
- **Tooltip em toda marca** e **tabela equivalente** sempre disponível: três das cores
  ficam abaixo de 3:1 de contraste com o fundo claro, então a identidade nunca depende só
  da cor.

Alterar as cores é mexer em `CORES_OA`, em `src/oa_monitor/viz.py` — as specs Vega e os
gráficos matplotlib leem do mesmo lugar.

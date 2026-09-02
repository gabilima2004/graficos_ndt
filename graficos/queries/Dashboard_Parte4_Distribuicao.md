# Dashboard NDT Unificado — Parte 4: Distribuição

> **Tipo de painel:** Plotly (plugin `nline-plotlyjs-panel`)  
> **Filtros:** `$isp` (provedor), `$server` (servidor), período do dashboard  
> **Visualizações:** Box plots e Violin plots por provedor

---

## Conceito: Box Plot vs Violin Plot

| Tipo            | O que mostra                                                            |
| --------------- | ----------------------------------------------------------------------- |
| **Box Plot**    | Quartis (Q1, Q2/mediana, Q3), outliers e "bigodes" (min/max)            |
| **Violin Plot** | Densidade da distribuição — mostra a "forma" dos dados além dos quartis |

> **Pergunta para refletir:** Por que usar ambos?
> **Resposta:** O box plot mostra estatísticas precisas (mediana, quartis). O violin plot mostra a densidade — se os dados estão concentrados em um valor ou espalhados. Juntos, dão visão completa da distribuição.

---

## Como funciona o Plotly no Grafana

O plugin `nline-plotlyjs-panel` funciona assim:

1. **Query SQL** → retorna os dados brutos (sem agregação)
2. **Script JavaScript** → transforma os dados em um gráfico Plotly
3. O script recebe `data.series[0].fields[0].values` (coluna 1) e `fields[1].values` (coluna 2)

```
SQL: SELECT valor, categoria FROM ...
          ↓
Grafana: fields[0] = valor, fields[1] = categoria
          ↓
Script JS: { y: fields[0], x: fields[1], type: 'box' }
          ↓
Plotly renderiza o gráfico
```

---

## 4.1 — Box Plot de Download por Provedor

### Query SQL:

```sql
SELECT
    d.mean_throughput_mbps AS "Download (Mbps)",
    CASE
        WHEN c.asn IN ('18881', '26599', '27699', '19182', '10429') THEN 'Telefônica'
        WHEN c.asn IN ('28573', '4230', '22085') THEN 'Claro'
        WHEN c.asn IN ('265303') THEN 'TV Alphaville'
        WHEN c.asn IN ('14868') THEN 'COPEL Telecom'
        WHEN c.asn IN ('53184') THEN 'INB Telecom'
        WHEN c.asn IN ('262907') THEN 'Avato Tecnologia'
        WHEN c.asn IN ('61844') THEN 'New Master'
        WHEN c.asn IN ('28258') THEN 'Powerline Internet'
        WHEN c.asn IN ('273683') THEN 'Desconhecido'
        WHEN c.asn IN ('22689') THEN 'Sercomtel'
        WHEN c.asn IN ('53062') THEN 'G G Net'
        WHEN c.asn IN ('264228') THEN 'Brasil Starlink'
        WHEN c.asn IN ('28669') THEN 'America Net'
        WHEN c.asn IN ('263645') THEN 'Fixtell Telecom'
        WHEN c.asn IN ('266949') THEN 'Divifibra'
        WHEN c.asn IN ('262700') THEN 'Efibra Telecom'
        WHEN c.asn IN ('28658') THEN 'Gigalink'
        WHEN c.asn IN ('262673') THEN 'Lafaiete'
        WHEN c.asn IN ('52900') THEN 'Quality Telecom'
        WHEN c.asn IN ('263629') THEN 'Celloni'
        WHEN c.asn IN ('52940') THEN 'Nemesis'
        WHEN c.asn IN ('262671') THEN 'S & M Informática'
        WHEN c.asn IN ('28241') THEN 'Viaceu Internet'
        WHEN c.asn IN ('53191') THEN 'Plug Telecom'
        WHEN c.asn IN ('28263') THEN 'Ensite Brasil'
        WHEN c.asn IN ('263072') THEN 'BD Fibra Telecom'
        WHEN c.asn IN ('53171') THEN 'Omni Telecom'
        ELSE c.as_name
    END AS "Provedor"
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE $__timeFilter(d.test_time)
    AND d.mean_throughput_mbps >= 0
    AND CASE
        WHEN c.asn IN ('18881', '26599', '27699', '19182', '10429') THEN 'Telefônica'
        WHEN c.asn IN ('28573', '4230', '22085') THEN 'Claro'
        WHEN c.asn IN ('265303') THEN 'TV Alphaville'
        WHEN c.asn IN ('14868') THEN 'COPEL Telecom'
        WHEN c.asn IN ('53184') THEN 'INB Telecom'
        WHEN c.asn IN ('262907') THEN 'Avato Tecnologia'
        WHEN c.asn IN ('61844') THEN 'New Master'
        WHEN c.asn IN ('28258') THEN 'Powerline Internet'
        WHEN c.asn IN ('273683') THEN 'Desconhecido'
        WHEN c.asn IN ('22689') THEN 'Sercomtel'
        WHEN c.asn IN ('53062') THEN 'G G Net'
        WHEN c.asn IN ('264228') THEN 'Brasil Starlink'
        WHEN c.asn IN ('28669') THEN 'America Net'
        WHEN c.asn IN ('263645') THEN 'Fixtell Telecom'
        WHEN c.asn IN ('266949') THEN 'Divifibra'
        WHEN c.asn IN ('262700') THEN 'Efibra Telecom'
        WHEN c.asn IN ('28658') THEN 'Gigalink'
        WHEN c.asn IN ('262673') THEN 'Lafaiete'
        WHEN c.asn IN ('52900') THEN 'Quality Telecom'
        WHEN c.asn IN ('263629') THEN 'Celloni'
        WHEN c.asn IN ('52940') THEN 'Nemesis'
        WHEN c.asn IN ('262671') THEN 'S & M Informática'
        WHEN c.asn IN ('28241') THEN 'Viaceu Internet'
        WHEN c.asn IN ('53191') THEN 'Plug Telecom'
        WHEN c.asn IN ('28263') THEN 'Ensite Brasil'
        WHEN c.asn IN ('263072') THEN 'BD Fibra Telecom'
        WHEN c.asn IN ('53171') THEN 'Omni Telecom'
        ELSE c.as_name
    END IN ($isp)
    AND ('$server' = '$__all' OR d.server_site IN ($server))
```

### Script JavaScript (Plotly):

```javascript
// Verifica se existem dados
if (
  !data ||
  !data.series ||
  data.series.length === 0 ||
  !data.series[0].fields ||
  data.series[0].fields.length < 2
) {
  return {
    data: [],
    layout: { title: "Sem dados para o filtro selecionado" },
  };
}

// fields[0] = "Download (Mbps)", fields[1] = "Provedor"
var valores = Array.from(data.series[0].fields[0].values);
var provedores = Array.from(data.series[0].fields[1].values);

var trace = {
  type: "box",
  y: valores,
  x: provedores,
  name: "Download (Mbps)",
  box: { visible: true },
  meanline: { visible: true },
  points: "outliers",
  marker: { color: "#8e44ad", size: 3 },
  line: { color: "#8e44ad", width: 1.5 },
  fillcolor: "rgba(142, 68, 173, 0.3)",
};

var layout = {
  title: "Distribuição de Download por Provedor",
  xaxis: { title: "Provedor", type: "category", automargin: true },
  yaxis: { title: "Download (Mbps)", automargin: true },
  margin: { t: 40, r: 20, b: 60, l: 60 },
};

return { data: [trace], layout: layout };
```

### Configuração no Grafana:

| Configuração    | Valor                  |
| --------------- | ---------------------- |
| Panel type      | `nline-plotlyjs-panel` |
| Format          | `table`                |
| Sync time range | `true`                 |

---

## 4.2 — Violin Plot de Download por Provedor

### Query SQL:

> **Mesma query do 4.1** — só muda o script JavaScript.

### Script JavaScript (Plotly):

```javascript
if (
  !data ||
  !data.series ||
  data.series.length === 0 ||
  !data.series[0].fields ||
  data.series[0].fields.length < 2
) {
  return {
    data: [],
    layout: { title: "Sem dados para o filtro selecionado" },
  };
}

var valores = Array.from(data.series[0].fields[0].values);
var provedores = Array.from(data.series[0].fields[1].values);

var trace = {
  type: "violin",
  y: valores,
  x: provedores,
  name: "Download (Mbps)",
  side: "both",
  box: { visible: false },
  meanline: { visible: false },
  points: false,
  line: { color: "#8e44ad", width: 1.5 },
  fillcolor: "rgba(142, 68, 173, 0.4)",
};

var layout = {
  title: "Densidade de Download por Provedor",
  xaxis: { title: "Provedor", type: "category", automargin: true },
  yaxis: { title: "Download (Mbps)", automargin: true },
  margin: { t: 40, r: 20, b: 60, l: 60 },
};

return { data: [trace], layout: layout };
```

---

## 4.3 — Box Plot de Upload por Provedor

### Query SQL:

```sql
SELECT
    d.mean_throughput_mbps AS "Upload (Mbps)",
    CASE
        WHEN c.asn IN ('18881', '26599', '27699', '19182', '10429') THEN 'Telefônica'
        WHEN c.asn IN ('28573', '4230', '22085') THEN 'Claro'
        WHEN c.asn IN ('265303') THEN 'TV Alphaville'
        WHEN c.asn IN ('14868') THEN 'COPEL Telecom'
        WHEN c.asn IN ('53184') THEN 'INB Telecom'
        WHEN c.asn IN ('262907') THEN 'Avato Tecnologia'
        WHEN c.asn IN ('61844') THEN 'New Master'
        WHEN c.asn IN ('28258') THEN 'Powerline Internet'
        WHEN c.asn IN ('273683') THEN 'Desconhecido'
        WHEN c.asn IN ('22689') THEN 'Sercomtel'
        WHEN c.asn IN ('53062') THEN 'G G Net'
        WHEN c.asn IN ('264228') THEN 'Brasil Starlink'
        WHEN c.asn IN ('28669') THEN 'America Net'
        WHEN c.asn IN ('263645') THEN 'Fixtell Telecom'
        WHEN c.asn IN ('266949') THEN 'Divifibra'
        WHEN c.asn IN ('262700') THEN 'Efibra Telecom'
        WHEN c.asn IN ('28658') THEN 'Gigalink'
        WHEN c.asn IN ('262673') THEN 'Lafaiete'
        WHEN c.asn IN ('52900') THEN 'Quality Telecom'
        WHEN c.asn IN ('263629') THEN 'Celloni'
        WHEN c.asn IN ('52940') THEN 'Nemesis'
        WHEN c.asn IN ('262671') THEN 'S & M Informática'
        WHEN c.asn IN ('28241') THEN 'Viaceu Internet'
        WHEN c.asn IN ('53191') THEN 'Plug Telecom'
        WHEN c.asn IN ('28263') THEN 'Ensite Brasil'
        WHEN c.asn IN ('263072') THEN 'BD Fibra Telecom'
        WHEN c.asn IN ('53171') THEN 'Omni Telecom'
        ELSE c.as_name
    END AS "Provedor"
FROM upload d
JOIN client c ON d.client_ip = c.client_ip
WHERE $__timeFilter(d.test_time)
    AND d.mean_throughput_mbps >= 0
    AND CASE
        WHEN c.asn IN ('18881', '26599', '27699', '19182', '10429') THEN 'Telefônica'
        WHEN c.asn IN ('28573', '4230', '22085') THEN 'Claro'
        WHEN c.asn IN ('265303') THEN 'TV Alphaville'
        WHEN c.asn IN ('14868') THEN 'COPEL Telecom'
        WHEN c.asn IN ('53184') THEN 'INB Telecom'
        WHEN c.asn IN ('262907') THEN 'Avato Tecnologia'
        WHEN c.asn IN ('61844') THEN 'New Master'
        WHEN c.asn IN ('28258') THEN 'Powerline Internet'
        WHEN c.asn IN ('273683') THEN 'Desconhecido'
        WHEN c.asn IN ('22689') THEN 'Sercomtel'
        WHEN c.asn IN ('53062') THEN 'G G Net'
        WHEN c.asn IN ('264228') THEN 'Brasil Starlink'
        WHEN c.asn IN ('28669') THEN 'America Net'
        WHEN c.asn IN ('263645') THEN 'Fixtell Telecom'
        WHEN c.asn IN ('266949') THEN 'Divifibra'
        WHEN c.asn IN ('262700') THEN 'Efibra Telecom'
        WHEN c.asn IN ('28658') THEN 'Gigalink'
        WHEN c.asn IN ('262673') THEN 'Lafaiete'
        WHEN c.asn IN ('52900') THEN 'Quality Telecom'
        WHEN c.asn IN ('263629') THEN 'Celloni'
        WHEN c.asn IN ('52940') THEN 'Nemesis'
        WHEN c.asn IN ('262671') THEN 'S & M Informática'
        WHEN c.asn IN ('28241') THEN 'Viaceu Internet'
        WHEN c.asn IN ('53191') THEN 'Plug Telecom'
        WHEN c.asn IN ('28263') THEN 'Ensite Brasil'
        WHEN c.asn IN ('263072') THEN 'BD Fibra Telecom'
        WHEN c.asn IN ('53171') THEN 'Omni Telecom'
        ELSE c.as_name
    END IN ($isp)
    AND ('$server' = '$__all' OR d.server_site IN ($server))
```

### Script JavaScript (Plotly):

```javascript
if (
  !data ||
  !data.series ||
  data.series.length === 0 ||
  !data.series[0].fields ||
  data.series[0].fields.length < 2
) {
  return { data: [], layout: { title: "Sem dados" } };
}

var valores = Array.from(data.series[0].fields[0].values);
var provedores = Array.from(data.series[0].fields[1].values);

var trace = {
  type: "box",
  y: valores,
  x: provedores,
  name: "Upload (Mbps)",
  box: { visible: true },
  meanline: { visible: true },
  points: "outliers",
  marker: { color: "#e67e22", size: 3 },
  line: { color: "#e67e22", width: 1.5 },
  fillcolor: "rgba(230, 126, 34, 0.3)",
};

var layout = {
  title: "Distribuição de Upload por Provedor",
  xaxis: { title: "Provedor", type: "category", automargin: true },
  yaxis: { title: "Upload (Mbps)", automargin: true },
  margin: { t: 40, r: 20, b: 60, l: 60 },
};

return { data: [trace], layout: layout };
```

---

## 4.4 — Box Plot de RTT por Provedor

### Query SQL:

```sql
SELECT
    d.min_rtt AS "RTT (ms)",
    CASE
        WHEN c.asn IN ('18881', '26599', '27699', '19182', '10429') THEN 'Telefônica'
        WHEN c.asn IN ('28573', '4230', '22085') THEN 'Claro'
        WHEN c.asn IN ('265303') THEN 'TV Alphaville'
        WHEN c.asn IN ('14868') THEN 'COPEL Telecom'
        WHEN c.asn IN ('53184') THEN 'INB Telecom'
        WHEN c.asn IN ('262907') THEN 'Avato Tecnologia'
        WHEN c.asn IN ('61844') THEN 'New Master'
        WHEN c.asn IN ('28258') THEN 'Powerline Internet'
        WHEN c.asn IN ('273683') THEN 'Desconhecido'
        WHEN c.asn IN ('22689') THEN 'Sercomtel'
        WHEN c.asn IN ('53062') THEN 'G G Net'
        WHEN c.asn IN ('264228') THEN 'Brasil Starlink'
        WHEN c.asn IN ('28669') THEN 'America Net'
        WHEN c.asn IN ('263645') THEN 'Fixtell Telecom'
        WHEN c.asn IN ('266949') THEN 'Divifibra'
        WHEN c.asn IN ('262700') THEN 'Efibra Telecom'
        WHEN c.asn IN ('28658') THEN 'Gigalink'
        WHEN c.asn IN ('262673') THEN 'Lafaiete'
        WHEN c.asn IN ('52900') THEN 'Quality Telecom'
        WHEN c.asn IN ('263629') THEN 'Celloni'
        WHEN c.asn IN ('52940') THEN 'Nemesis'
        WHEN c.asn IN ('262671') THEN 'S & M Informática'
        WHEN c.asn IN ('28241') THEN 'Viaceu Internet'
        WHEN c.asn IN ('53191') THEN 'Plug Telecom'
        WHEN c.asn IN ('28263') THEN 'Ensite Brasil'
        WHEN c.asn IN ('263072') THEN 'BD Fibra Telecom'
        WHEN c.asn IN ('53171') THEN 'Omni Telecom'
        ELSE c.as_name
    END AS "Provedor"
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE $__timeFilter(d.test_time)
    AND d.min_rtt >= 0
    AND d.min_rtt <= 1500000
    AND CASE
        WHEN c.asn IN ('18881', '26599', '27699', '19182', '10429') THEN 'Telefônica'
        WHEN c.asn IN ('28573', '4230', '22085') THEN 'Claro'
        WHEN c.asn IN ('265303') THEN 'TV Alphaville'
        WHEN c.asn IN ('14868') THEN 'COPEL Telecom'
        WHEN c.asn IN ('53184') THEN 'INB Telecom'
        WHEN c.asn IN ('262907') THEN 'Avato Tecnologia'
        WHEN c.asn IN ('61844') THEN 'New Master'
        WHEN c.asn IN ('28258') THEN 'Powerline Internet'
        WHEN c.asn IN ('273683') THEN 'Desconhecido'
        WHEN c.asn IN ('22689') THEN 'Sercomtel'
        WHEN c.asn IN ('53062') THEN 'G G Net'
        WHEN c.asn IN ('264228') THEN 'Brasil Starlink'
        WHEN c.asn IN ('28669') THEN 'America Net'
        WHEN c.asn IN ('263645') THEN 'Fixtell Telecom'
        WHEN c.asn IN ('266949') THEN 'Divifibra'
        WHEN c.asn IN ('262700') THEN 'Efibra Telecom'
        WHEN c.asn IN ('28658') THEN 'Gigalink'
        WHEN c.asn IN ('262673') THEN 'Lafaiete'
        WHEN c.asn IN ('52900') THEN 'Quality Telecom'
        WHEN c.asn IN ('263629') THEN 'Celloni'
        WHEN c.asn IN ('52940') THEN 'Nemesis'
        WHEN c.asn IN ('262671') THEN 'S & M Informática'
        WHEN c.asn IN ('28241') THEN 'Viaceu Internet'
        WHEN c.asn IN ('53191') THEN 'Plug Telecom'
        WHEN c.asn IN ('28263') THEN 'Ensite Brasil'
        WHEN c.asn IN ('263072') THEN 'BD Fibra Telecom'
        WHEN c.asn IN ('53171') THEN 'Omni Telecom'
        ELSE c.as_name
    END IN ($isp)
    AND ('$server' = '$__all' OR d.server_site IN ($server))
```

### Script JavaScript (Plotly):

```javascript
if (
  !data ||
  !data.series ||
  data.series.length === 0 ||
  !data.series[0].fields ||
  data.series[0].fields.length < 2
) {
  return { data: [], layout: { title: "Sem dados" } };
}

var valores = Array.from(data.series[0].fields[0].values);
var provedores = Array.from(data.series[0].fields[1].values);

var trace = {
  type: "box",
  y: valores,
  x: provedores,
  name: "RTT (ms)",
  box: { visible: true },
  meanline: { visible: true },
  points: "outliers",
  marker: { color: "#33a2e5", size: 3 },
  line: { color: "#33a2e5", width: 1.5 },
  fillcolor: "rgba(51, 162, 229, 0.3)",
};

var layout = {
  title: "Distribuição de RTT por Provedor",
  xaxis: { title: "Provedor", type: "category", automargin: true },
  yaxis: { title: "RTT (ms)", type: "log", automargin: true },
  margin: { t: 40, r: 20, b: 60, l: 60 },
};

return { data: [trace], layout: layout };
```

> **Atenção:** O eixo Y usa `type: 'log'` — escala logarítmica, porque RTT varia em várias ordens de grandeza.

---

## 4.5 — Box Plot de Loss Rate por Provedor

### Query SQL:

```sql
SELECT
    d.loss_rate AS "Loss Rate",
    CASE
        WHEN c.asn IN ('18881', '26599', '27699', '19182', '10429') THEN 'Telefônica'
        WHEN c.asn IN ('28573', '4230', '22085') THEN 'Claro'
        WHEN c.asn IN ('265303') THEN 'TV Alphaville'
        WHEN c.asn IN ('14868') THEN 'COPEL Telecom'
        WHEN c.asn IN ('53184') THEN 'INB Telecom'
        WHEN c.asn IN ('262907') THEN 'Avato Tecnologia'
        WHEN c.asn IN ('61844') THEN 'New Master'
        WHEN c.asn IN ('28258') THEN 'Powerline Internet'
        WHEN c.asn IN ('273683') THEN 'Desconhecido'
        WHEN c.asn IN ('22689') THEN 'Sercomtel'
        WHEN c.asn IN ('53062') THEN 'G G Net'
        WHEN c.asn IN ('264228') THEN 'Brasil Starlink'
        WHEN c.asn IN ('28669') THEN 'America Net'
        WHEN c.asn IN ('263645') THEN 'Fixtell Telecom'
        WHEN c.asn IN ('266949') THEN 'Divifibra'
        WHEN c.asn IN ('262700') THEN 'Efibra Telecom'
        WHEN c.asn IN ('28658') THEN 'Gigalink'
        WHEN c.asn IN ('262673') THEN 'Lafaiete'
        WHEN c.asn IN ('52900') THEN 'Quality Telecom'
        WHEN c.asn IN ('263629') THEN 'Celloni'
        WHEN c.asn IN ('52940') THEN 'Nemesis'
        WHEN c.asn IN ('262671') THEN 'S & M Informática'
        WHEN c.asn IN ('28241') THEN 'Viaceu Internet'
        WHEN c.asn IN ('53191') THEN 'Plug Telecom'
        WHEN c.asn IN ('28263') THEN 'Ensite Brasil'
        WHEN c.asn IN ('263072') THEN 'BD Fibra Telecom'
        WHEN c.asn IN ('53171') THEN 'Omni Telecom'
        ELSE c.as_name
    END AS "Provedor"
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE $__timeFilter(d.test_time)
    AND d.loss_rate >= 0
    AND CASE
        WHEN c.asn IN ('18881', '26599', '27699', '19182', '10429') THEN 'Telefônica'
        WHEN c.asn IN ('28573', '4230', '22085') THEN 'Claro'
        WHEN c.asn IN ('265303') THEN 'TV Alphaville'
        WHEN c.asn IN ('14868') THEN 'COPEL Telecom'
        WHEN c.asn IN ('53184') THEN 'INB Telecom'
        WHEN c.asn IN ('262907') THEN 'Avato Tecnologia'
        WHEN c.asn IN ('61844') THEN 'New Master'
        WHEN c.asn IN ('28258') THEN 'Powerline Internet'
        WHEN c.asn IN ('273683') THEN 'Desconhecido'
        WHEN c.asn IN ('22689') THEN 'Sercomtel'
        WHEN c.asn IN ('53062') THEN 'G G Net'
        WHEN c.asn IN ('264228') THEN 'Brasil Starlink'
        WHEN c.asn IN ('28669') THEN 'America Net'
        WHEN c.asn IN ('263645') THEN 'Fixtell Telecom'
        WHEN c.asn IN ('266949') THEN 'Divifibra'
        WHEN c.asn IN ('262700') THEN 'Efibra Telecom'
        WHEN c.asn IN ('28658') THEN 'Gigalink'
        WHEN c.asn IN ('262673') THEN 'Lafaiete'
        WHEN c.asn IN ('52900') THEN 'Quality Telecom'
        WHEN c.asn IN ('263629') THEN 'Celloni'
        WHEN c.asn IN ('52940') THEN 'Nemesis'
        WHEN c.asn IN ('262671') THEN 'S & M Informática'
        WHEN c.asn IN ('28241') THEN 'Viaceu Internet'
        WHEN c.asn IN ('53191') THEN 'Plug Telecom'
        WHEN c.asn IN ('28263') THEN 'Ensite Brasil'
        WHEN c.asn IN ('263072') THEN 'BD Fibra Telecom'
        WHEN c.asn IN ('53171') THEN 'Omni Telecom'
        ELSE c.as_name
    END IN ($isp)
    AND ('$server' = '$__all' OR d.server_site IN ($server))
```

### Script JavaScript (Plotly):

```javascript
if (
  !data ||
  !data.series ||
  data.series.length === 0 ||
  !data.series[0].fields ||
  data.series[0].fields.length < 2
) {
  return { data: [], layout: { title: "Sem dados" } };
}

var valores = Array.from(data.series[0].fields[0].values);
var provedores = Array.from(data.series[0].fields[1].values);

var trace = {
  type: "box",
  y: valores,
  x: provedores,
  name: "Loss Rate",
  box: { visible: true },
  meanline: { visible: true },
  points: "outliers",
  marker: { color: "#e74c3c", size: 3 },
  line: { color: "#e74c3c", width: 1.5 },
  fillcolor: "rgba(231, 76, 60, 0.3)",
};

var layout = {
  title: "Distribuição de Loss Rate por Provedor",
  xaxis: { title: "Provedor", type: "category", automargin: true },
  yaxis: {
    title: "Loss Rate",
    type: "log",
    automargin: true,
    tickformat: ".2%",
  },
  margin: { t: 40, r: 20, b: 60, l: 60 },
};

return { data: [trace], layout: layout };
```

> **Atenção:** Eixo Y com `type: 'log'` e `tickformat: '.2%'` para mostrar como percentual.

---

## Resumo da Parte 4

| #   | Painel               | Tipo          | Tabela   | Cor                | Escala Y |
| --- | -------------------- | ------------- | -------- | ------------------ | -------- |
| 4.1 | Box Plot Download    | Plotly box    | download | Roxo `#8e44ad`     | Linear   |
| 4.2 | Violin Plot Download | Plotly violin | download | Roxo `#8e44ad`     | Linear   |
| 4.3 | Box Plot Upload      | Plotly box    | upload   | Laranja `#e67e22`  | Linear   |
| 4.4 | Box Plot RTT         | Plotly box    | download | Azul `#33a2e5`     | **Log**  |
| 4.5 | Box Plot Loss Rate   | Plotly box    | download | Vermelho `#e74c3c` | **Log**  |

### Padrão de cores (herdado do dashboard antigo):

| Métrica      | Cor      | Hex       |
| ------------ | -------- | --------- |
| Download     | Roxo     | `#8e44ad` |
| Upload       | Laranja  | `#e67e22` |
| RTT/Latência | Azul     | `#33a2e5` |
| Loss Rate    | Vermelho | `#e74c3c` |

### Estrutura do script Plotly:

```javascript
// 1. Verificar se há dados
if (!data || !data.series || ...) return { data: [], layout: { title: 'Sem dados' } };

// 2. Extrair colunas (fields[0] = valores, fields[1] = categorias)
var valores = Array.from(data.series[0].fields[0].values);
var provedores = Array.from(data.series[0].fields[1].values);

// 3. Configurar o trace (box ou violin)
var trace = { type: 'box', y: valores, x: provedores, ... };

// 4. Configurar o layout (títulos, eixos, escala)
var layout = { title: '...', xaxis: {...}, yaxis: {...} };

// 5. Retornar
return { data: [trace], layout: layout };
```

### Pergunta para refletir:

> Por que os box plots de RTT e Loss Rate usam escala log no eixo Y?
> **Resposta:** RTT pode variar de 5ms a 500ms (100x), e loss rate de 0.0001 a 0.5 (5000x). Sem escala log, a maioria dos valores ficaria "amassada" perto de zero e os outliers dominariam o gráfico. Com log, a distribuição fica visível em todas as faixas.

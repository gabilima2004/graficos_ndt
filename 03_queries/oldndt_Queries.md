## Big Query

{
"annotations": {
"list": [
{
"builtIn": 1,
"datasource": {
"type": "grafana",
"uid": "-- Grafana --"
},
"enable": true,
"hide": true,
"iconColor": "rgba(0, 211, 255, 1)",
"name": "Annotations & Alerts",
"type": "dashboard"
}
]
},
"editable": true,
"fiscalYearStartMonth": 0,
"graphTooltip": 0,
"id": 101,
"links": [],
"panels": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"fieldConfig": {
"defaults": {
"color": {
"mode": "palette-classic"
},
"custom": {
"axisBorderShow": false,
"axisCenteredZero": false,
"axisColorMode": "text",
"axisLabel": "",
"axisPlacement": "auto",
"axisSoftMax": 1000,
"barAlignment": 0,
"barWidthFactor": 0.6,
"drawStyle": "points",
"fillOpacity": 0,
"gradientMode": "none",
"hideFrom": {
"legend": false,
"tooltip": false,
"viz": false
},
"insertNulls": false,
"lineInterpolation": "linear",
"lineWidth": 1,
"pointSize": 2.5,
"scaleDistribution": {
"type": "linear"
},
"showPoints": "auto",
"spanNulls": false,
"stacking": {
"group": "A",
"mode": "none"
},
"thresholdsStyle": {
"mode": "off"
}
},
"fieldMinMax": false,
"mappings": [],
"thresholds": {
"mode": "absolute",
"steps": [
{
"color": "green"
},
{
"color": "red",
"value": 80
}
]
},
"unit": "MBs"
},
"overrides": []
},
"gridPos": {
"h": 13,
"w": 16,
"x": 0,
"y": 0
},
"id": 2,
"options": {
"legend": {
"calcs": [
"mean",
"variance",
"p30",
"p50",
"p70",
"p90",
"p95",
"p99"
],
"displayMode": "list",
"placement": "bottom",
"showLegend": true
},
"tooltip": {
"hideZeros": false,
"mode": "single",
"sort": "none"
}
},
"pluginVersion": "12.0.2",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"editorMode": "code",
"format": "time*series",
"rawQuery": true,
"rawSql": "SELECT\n $__timeGroup(t.start_time, '5m') as time,\n    AVG(t.throughput_mbps) as \"Download (Mbps)\",\n    \n    CASE\n        WHEN '${Provedor:csv}' LIKE '%,%'\n THEN t.provider\n ELSE t.zone\n END AS \"Grupo\"\n\nFROM tests_union_grafana_ht t\nWHERE\n $__timeFilter(t.start_time) AND\n    t.test_type = 'download' AND\n    t.provider IN (${Provedor:sqlstring}) AND \n ('${Zone:csv}' = 'All' OR t.zone IN (${Zone:sqlstring})) AND\n ('${OS:csv}' = 'All' OR t.client_name IN (${OS:sqlstring})) AND ('${Location:csv}' = 'All' OR t.location IN (${Location:sqlstring}))\nGROUP BY 1, 3\nORDER BY 1 ASC;",
"refId": "A",
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "Download",
"type": "timeseries"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"fieldConfig": {
"defaults": {
"color": {
"mode": "continuous-GrYlRd"
},
"custom": {
"align": "auto",
"cellOptions": {
"type": "color-background"
},
"inspect": false
},
"mappings": [],
"thresholds": {
"mode": "absolute",
"steps": [
{
"color": "green"
},
{
"color": "red",
"value": 80
}
]
}
},
"overrides": []
},
"gridPos": {
"h": 13,
"w": 8,
"x": 16,
"y": 0
},
"id": 19,
"options": {
"cellHeight": "sm",
"footer": {
"countRows": false,
"fields": "",
"reducer": [
"sum"
],
"show": false
},
"showHeader": true
},
"pluginVersion": "12.0.2",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"editorMode": "code",
"format": "table",
"rawQuery": true,
"rawSql": "SELECT * FROM (\n SELECT\n CASE\n WHEN '${Provedor:csv}' LIKE '%,%'\n THEN t.provider\n ELSE t.zone\n END AS \"Servidor/Zona\",\n \n COUNT(_) AS \"Total de Testes\",\n \n ROUND(AVG(t.throughput_mbps)::numeric, 2) AS \"Média (Mbps)\",\n \n ROUND(MIN(t.throughput_mbps)::numeric, 2) AS \"Mínimo (Mbps)\",\n \n ROUND(MAX(t.throughput_mbps)::numeric, 2) AS \"Máximo (Mbps)\"\n\n FROM tests_union_grafana_ht t\n WHERE\n $__timeFilter(t.start_time)\n        AND t.test_type = 'download'\n        AND t.provider IN (${Provedor:sqlstring})\n AND ('${Zone:csv}' = 'All' OR t.zone IN (${Zone:sqlstring}))\n AND ('${OS:csv}' = 'All' OR t.client_name IN (${OS:sqlstring}))\n AND ('${Location:csv}' = 'All' OR t.location IN (${Location:sqlstring}))\n \n\n GROUP BY\n CASE\n WHEN '${Provedor:csv}' LIKE '%,%'\n            THEN t.provider\n            ELSE t.zone\n        END\n\n    UNION ALL\n\n    SELECT\n        '📊 TOTAL GERAL' AS \"Servidor/Zona\",\n        \n        COUNT(*) AS \"Total de Testes\",\n        \n        ROUND(AVG(t.throughput_mbps)::numeric, 2) AS \"Média (Mbps)\",\n        \n        ROUND(MIN(t.throughput_mbps)::numeric, 2) AS \"Mínimo (Mbps)\",\n        \n        ROUND(MAX(t.throughput_mbps)::numeric, 2) AS \"Máximo (Mbps)\"\n\n    FROM tests_union_grafana_ht t\n    WHERE\n        $__timeFilter(t.start_time)\n        AND t.test_type = 'download'\n        AND t.provider IN (${Provedor:sqlstring})\n AND ('${Zone:csv}' = 'All' OR t.zone IN (${Zone:sqlstring}))\n AND ('${OS:csv}' = 'All' OR t.client_name IN (${OS:sqlstring}))\n AND ('${Location:csv}' = 'All' OR t.location IN (${Location:sqlstring}))\n \n) AS resultado\nORDER BY \"Total de Testes\" DESC;",
"refId": "A",
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "Download dados",
"type": "table"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"fieldConfig": {
"defaults": {
"color": {
"mode": "palette-classic"
},
"custom": {
"axisBorderShow": false,
"axisCenteredZero": false,
"axisColorMode": "text",
"axisLabel": "",
"axisPlacement": "auto",
"axisSoftMax": 1000,
"barAlignment": 0,
"barWidthFactor": 0.6,
"drawStyle": "points",
"fillOpacity": 0,
"gradientMode": "none",
"hideFrom": {
"legend": false,
"tooltip": false,
"viz": false
},
"insertNulls": false,
"lineInterpolation": "linear",
"lineWidth": 1,
"pointSize": 2.5,
"scaleDistribution": {
"type": "linear"
},
"showPoints": "auto",
"spanNulls": false,
"stacking": {
"group": "A",
"mode": "none"
},
"thresholdsStyle": {
"mode": "off"
}
},
"fieldMinMax": false,
"mappings": [],
"thresholds": {
"mode": "absolute",
"steps": [
{
"color": "green"
},
{
"color": "red",
"value": 80
}
]
},
"unit": "MBs"
},
"overrides": []
},
"gridPos": {
"h": 13,
"w": 16,
"x": 0,
"y": 13
},
"id": 18,
"options": {
"legend": {
"calcs": [
"mean",
"variance",
"p30",
"p50",
"p70",
"p90",
"p95",
"p99"
],
"displayMode": "list",
"placement": "bottom",
"showLegend": true
},
"tooltip": {
"hideZeros": false,
"mode": "single",
"sort": "none"
}
},
"pluginVersion": "12.0.2",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"editorMode": "code",
"format": "time*series",
"rawQuery": true,
"rawSql": "SELECT\n $__timeGroup(t.start_time, '5m') as time,\n    AVG(t.throughput_mbps) as \"Upload (Mbps)\", -- Alias de Upload\n    \n    -- << A MÁGICA CONDICIONAL APLICADA AQUI >>\n    CASE\n        -- 1. Verifica se a string da variável contém uma vírgula (indicando múltiplos provedores)\n        WHEN '${Provedor:csv}' LIKE '%,%'\n \n -- 2. Se VERDADEIRO (mais de 1 provedor):\n THEN t.provider -- Use o PROVEDOR para colorir\n \n -- 3. Se FALSO (só 1 provedor):\n ELSE t.zone -- Use a ZONE para colorir\n \n END AS \"Grupo\" -- O Grafana usará esta coluna para as cores e legenda\n\nFROM tests_union_grafana_ht t\nWHERE\n $__timeFilter(t.start_time) AND\n    t.test_type = 'upload' AND -- Filtro de 'upload' mantido\n    t.provider IN (${Provedor:sqlstring}) AND \n ('${Zone:csv}' = 'All' OR t.zone IN (${Zone:sqlstring})) AND\n ('${OS:csv}' = 'All' OR t.client_name IN (${OS:sqlstring})) AND ('${Location:csv}' = 'All' OR t.location IN (${Location:sqlstring}))\nGROUP BY 1, 3\nORDER BY 1 ASC;",
"refId": "A",
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "Upload",
"type": "timeseries"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"fieldConfig": {
"defaults": {
"color": {
"mode": "continuous-GrYlRd"
},
"custom": {
"align": "auto",
"cellOptions": {
"type": "color-background"
},
"inspect": false
},
"mappings": [],
"thresholds": {
"mode": "absolute",
"steps": [
{
"color": "green"
},
{
"color": "red",
"value": 80
}
]
}
},
"overrides": []
},
"gridPos": {
"h": 13,
"w": 8,
"x": 16,
"y": 13
},
"id": 20,
"options": {
"cellHeight": "sm",
"footer": {
"countRows": false,
"fields": "",
"reducer": [
"sum"
],
"show": false
},
"showHeader": true
},
"pluginVersion": "12.0.2",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"editorMode": "code",
"format": "table",
"rawQuery": true,
"rawSql": "SELECT * FROM (\n SELECT\n CASE\n WHEN '${Provedor:csv}' LIKE '%,%'\n THEN t.provider\n ELSE t.zone\n END AS \"Servidor/Zona\",\n \n COUNT(_) AS \"Total de Testes\",\n \n ROUND(AVG(t.throughput_mbps)::numeric, 2) AS \"Média (Mbps)\",\n \n ROUND(MIN(t.throughput_mbps)::numeric, 2) AS \"Mínimo (Mbps)\",\n \n ROUND(MAX(t.throughput_mbps)::numeric, 2) AS \"Máximo (Mbps)\"\n\n FROM tests_union_grafana_ht t\n WHERE\n $__timeFilter(t.start_time)\n        AND t.test_type = 'upload'\n        AND t.provider IN (${Provedor:sqlstring})\n AND ('${Zone:csv}' = 'All' OR t.zone IN (${Zone:sqlstring}))\n AND ('${OS:csv}' = 'All' OR t.client_name IN (${OS:sqlstring}))\n AND ('${Location:csv}' = 'All' OR t.location IN (${Location:sqlstring}))\n \n\n GROUP BY\n CASE\n WHEN '${Provedor:csv}' LIKE '%,%'\n            THEN t.provider\n            ELSE t.zone\n        END\n\n    UNION ALL\n\n    SELECT\n        '📊 TOTAL GERAL' AS \"Servidor/Zona\",\n        \n        COUNT(*) AS \"Total de Testes\",\n        \n        ROUND(AVG(t.throughput_mbps)::numeric, 2) AS \"Média (Mbps)\",\n        \n        ROUND(MIN(t.throughput_mbps)::numeric, 2) AS \"Mínimo (Mbps)\",\n        \n        ROUND(MAX(t.throughput_mbps)::numeric, 2) AS \"Máximo (Mbps)\"\n\n    FROM tests_union_grafana_ht t\n    WHERE\n        $__timeFilter(t.start_time)\n        AND t.test_type = 'upload'\n        AND t.provider IN (${Provedor:sqlstring})\n AND ('${Zone:csv}' = 'All' OR t.zone IN (${Zone:sqlstring}))\n AND ('${OS:csv}' = 'All' OR t.client_name IN (${OS:sqlstring}))\n AND ('${Location:csv}' = 'All' OR t.location IN (${Location:sqlstring}))\n \n) AS resultado\nORDER BY \"Total de Testes\" DESC;",
"refId": "A",
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "Upload dados",
"type": "table"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"fieldConfig": {
"defaults": {
"color": {
"mode": "palette-classic",
"seriesBy": "min"
},
"custom": {
"axisBorderShow": false,
"axisCenteredZero": false,
"axisColorMode": "text",
"axisLabel": "",
"axisPlacement": "auto",
"barAlignment": 0,
"barWidthFactor": 0.6,
"drawStyle": "points",
"fillOpacity": 0,
"gradientMode": "none",
"hideFrom": {
"legend": false,
"tooltip": false,
"viz": false
},
"insertNulls": false,
"lineInterpolation": "linear",
"lineWidth": 1,
"pointSize": 2.5,
"scaleDistribution": {
"log": 2,
"type": "log"
},
"showPoints": "auto",
"spanNulls": false,
"stacking": {
"group": "A",
"mode": "none"
},
"thresholdsStyle": {
"mode": "off"
}
},
"mappings": [],
"thresholds": {
"mode": "absolute",
"steps": [
{
"color": "green"
},
{
"color": "red",
"value": 80
}
]
},
"unit": "percentunit"
},
"overrides": []
},
"gridPos": {
"h": 14,
"w": 24,
"x": 0,
"y": 26
},
"id": 8,
"options": {
"legend": {
"calcs": [
"mean",
"variance",
"p30",
"p50",
"p70",
"p90",
"p95",
"p99"
],
"displayMode": "list",
"placement": "bottom",
"showLegend": true
},
"tooltip": {
"hideZeros": false,
"mode": "single",
"sort": "none"
}
},
"pluginVersion": "12.0.2",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"editorMode": "code",
"format": "time*series",
"rawQuery": true,
"rawSql": "-- Loss Rate\nSELECT\n $__timeGroup(t.start_time, '5m') as time,\n    AVG(t.loss_rate) as \"Perda de Pacotes (%)\",\n    \n    -- << A MÁGICA CONDICIONAL APLICADA AQUI >>\n    CASE\n        -- 1. Verifica se a string da variável contém uma vírgula (indicando múltiplos provedores)\n        WHEN '${Provedor:csv}' LIKE '%,%'\n \n -- 2. Se VERDADEIRO (mais de 1 provedor):\n THEN t.provider -- Use o PROVEDOR para colorir\n \n -- 3. Se FALSO (só 1 provedor):\n ELSE t.zone -- Use a ZONE para colorir\n \n END AS \"Grupo\" -- O Grafana usará esta coluna para as cores e legenda\n\nFROM tests_union_grafana_ht t\nWHERE\n $__timeFilter(t.start_time) AND\n    t.provider IN (${Provedor:sqlstring}) AND\n ('${Zone:csv}' = 'All' OR t.zone IN (${Zone:sqlstring})) AND\n ('${OS:csv}' = 'All' OR t.client_name IN (${OS:sqlstring})) AND ('${Location:csv}' = 'All' OR t.location IN (${Location:sqlstring}))\nGROUP BY 1, 3\nORDER BY 1 ASC;",
"refId": "A",
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "loss rate",
"type": "timeseries"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"fieldConfig": {
"defaults": {
"color": {
"mode": "palette-classic",
"seriesBy": "min"
},
"custom": {
"axisBorderShow": false,
"axisCenteredZero": false,
"axisColorMode": "text",
"axisLabel": "",
"axisPlacement": "auto",
"barAlignment": 0,
"barWidthFactor": 0.6,
"drawStyle": "points",
"fillOpacity": 0,
"gradientMode": "none",
"hideFrom": {
"legend": false,
"tooltip": false,
"viz": false
},
"insertNulls": false,
"lineInterpolation": "linear",
"lineWidth": 1,
"pointSize": 2.5,
"scaleDistribution": {
"log": 2,
"type": "log"
},
"showPoints": "auto",
"spanNulls": false,
"stacking": {
"group": "A",
"mode": "none"
},
"thresholdsStyle": {
"mode": "off"
}
},
"mappings": [],
"thresholds": {
"mode": "absolute",
"steps": [
{
"color": "green"
},
{
"color": "red",
"value": 80
}
]
},
"unit": "µs"
},
"overrides": []
},
"gridPos": {
"h": 13,
"w": 24,
"x": 0,
"y": 40
},
"id": 5,
"options": {
"legend": {
"calcs": [
"mean",
"variance",
"p30",
"p50",
"p70",
"p90",
"p95",
"p99"
],
"displayMode": "list",
"placement": "bottom",
"showLegend": true
},
"tooltip": {
"hideZeros": false,
"mode": "single",
"sort": "none"
}
},
"pluginVersion": "12.0.2",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"editorMode": "code",
"format": "time_series",
"rawQuery": true,
"rawSql": "-- RTT\nSELECT\n $__timeGroup(t.start_time, '5m') as time,\n    AVG(t.min_rtt) as \"RTT Mínimo (µs)\",\n    \n    -- << A MÁGICA CONDICIONAL APLICADA AQUI >>\n    CASE\n        -- 1. Verifica se há mais de um provedor selecionado (checa por vírgula)\n        WHEN '${Provedor:csv}' LIKE '%,%'\n \n -- 2. Se VERDADEIRO (mais de 1 provedor):\n THEN t.provider -- Colore por provedor\n \n -- 3. Se FALSO (só 1 provedor):\n ELSE t.zone -- Colore por zona\n \n END AS \"Grupo\" -- O Grafana usará esta coluna para as cores\n\nFROM tests_union_grafana_ht t\nWHERE\n $__timeFilter(t.start_time) AND\n    t.provider IN (${Provedor:sqlstring}) AND\n ('${Zone:csv}' = 'All' OR t.zone IN (${Zone:sqlstring})) AND\n ('${OS:csv}' = 'All' OR t.client_name IN (${OS:sqlstring})) AND ('${Location:csv}' = 'All' OR t.location IN (${Location:sqlstring})) AND\n t.min_rtt <= 1500000\nGROUP BY 1, 3\nORDER BY 1 ASC;",
"refId": "A",
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "rtt_min",
"type": "timeseries"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"fieldConfig": {
"defaults": {
"color": {
"mode": "palette-classic"
},
"custom": {
"axisBorderShow": false,
"axisCenteredZero": false,
"axisColorMode": "text",
"axisLabel": "",
"axisPlacement": "auto",
"barAlignment": 0,
"barWidthFactor": 0.6,
"drawStyle": "points",
"fillOpacity": 0,
"gradientMode": "none",
"hideFrom": {
"legend": false,
"tooltip": false,
"viz": false
},
"insertNulls": false,
"lineInterpolation": "linear",
"lineWidth": 1,
"pointSize": 2.5,
"scaleDistribution": {
"type": "linear"
},
"showPoints": "auto",
"spanNulls": false,
"stacking": {
"group": "A",
"mode": "none"
},
"thresholdsStyle": {
"mode": "off"
}
},
"mappings": [],
"thresholds": {
"mode": "absolute",
"steps": [
{
"color": "green"
},
{
"color": "red",
"value": 80
}
]
},
"unit": "s"
},
"overrides": []
},
"gridPos": {
"h": 13,
"w": 16,
"x": 0,
"y": 53
},
"id": 10,
"options": {
"legend": {
"calcs": [
"mean",
"min",
"max"
],
"displayMode": "list",
"placement": "bottom",
"showLegend": true
},
"tooltip": {
"hideZeros": false,
"mode": "single",
"sort": "none"
}
},
"pluginVersion": "12.0.2",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"editorMode": "code",
"format": "time_series",
"rawQuery": true,
"rawSql": "-- Duração dos Testes\nSELECT\n $__timeGroup(t.start_time, '5m') as time,\n    AVG((t.duration_ms / 1000.0)) as \"Duração (segundos)\",\n    \n    -- << A MÁGICA CONDICIONAL APLICADA AQUI >>\n    CASE\n        -- 1. Verifica se há mais de um provedor selecionado (checa por vírgula)\n        WHEN '${Provedor:csv}' LIKE '%,%'\n \n -- 2. Se VERDADEIRO (mais de 1 provedor):\n THEN t.provider -- Colore por provedor\n \n -- 3. Se FALSO (só 1 provedor):\n ELSE t.zone -- Colore por zona\n \n END AS \"Grupo\" -- O Grafana usará esta coluna para as cores\n\nFROM tests_union_grafana_ht t\nWHERE\n $__timeFilter(t.start_time) AND\n    t.provider IN (${Provedor:sqlstring}) AND\n ('${Zone:csv}' = 'All' OR t.zone IN (${Zone:sqlstring})) AND\n ('${OS:csv}' = 'All' OR t.client_name IN (${OS:sqlstring})) AND ('${Location:csv}' = 'All' OR t.location IN (${Location:sqlstring})) AND\n t.duration_ms <= 15000\nGROUP BY 1, 3\nORDER BY 1 ASC;",
"refId": "A",
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "Duração dos testes",
"type": "timeseries"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"fieldConfig": {
"defaults": {},
"overrides": []
},
"gridPos": {
"h": 8,
"w": 12,
"x": 0,
"y": 66
},
"id": 11,
"options": {
"allData": {},
"config": {},
"data": [],
"imgFormat": "png",
"layout": {
"font": {
"family": "Inter, Helvetica, Arial, sans-serif"
},
"margin": {
"b": 0,
"l": 0,
"r": 0,
"t": 0
},
"title": "Box Plot de Download por Zona",
"xaxis": {
"automargin": true,
"autorange": true,
"title": "Zona",
"type": "category"
},
"yaxis": {
"automargin": true,
"autorange": true,
"title": "Download (Mbps)"
}
},
"onclick": "// Event handling\n/*\n// 'data', 'variables', 'options', 'utils', and 'event' are passed as arguments\n\ntry {\n const { type: eventType, data: eventData } = event;\n const { timeZone, dayjs, locationService, getTemplateSrv } = utils;\n\n switch (eventType) {\n case 'click':\n console.log('Click event:', eventData.points);\n break;\n case 'select':\n console.log('Selection event:', eventData.range);\n break;\n case 'zoom':\n console.log('Zoom event:', eventData);\n break;\n default:\n console.log('Unhandled event type:', eventType, eventData);\n }\n\n console.log('Current time zone:', timeZone);\n console.log('From time:', dayjs(variables.**from).format());\n console.log('To time:', dayjs(variables.**to).format());\n\n // Example of using locationService\n // locationService.partial({ 'var-example': 'test' }, true);\n\n} catch (error) {\n console.error('Error in onclick handler:', error);\n}\n*/\n ",
"resScale": 2,
"script": "// fields[0] é \"Download (Mbps)\"\n// fields[1] é \"Zone\"\n\nvar trace = {\n type: 'box',\n \n // Eixo Y (valores) usa a primeira coluna (índice 0)\n y: data.series[0].fields[0].values,\n \n // Eixo X (categorias) usa a segunda coluna (índice 1)\n x: data.series[0].fields[1].values\n};\n\nvar layout = {\n title: 'Box Plot de Download por Zona',\n yaxis: { title: 'Download (Mbps)' },\n xaxis: { title: 'Zona' }\n};\n\nreturn {\n data: [trace],\n layout: layout\n};",
"syncTimeRange": false,
"timeCol": ""
},
"pluginVersion": "1.8.1",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"editorMode": "code",
"format": "table",
"rawQuery": true,
"rawSql": "SELECT\n t.throughput_mbps as \"Download (Mbps)\",\n -- MUDANÇA AQUI: Usa substring com regex para pegar as duas primeiras palavras\n (substring(t.provider from '^([^\\s]+(\\s+[^\\s]+)?)') || '/' || t.zone) as \"Provedor/Zone\"\nFROM tests_union_grafana_ht t\nWHERE\n $__timeFilter(t.start_time) AND\n    t.test_type = 'download' AND\n    t.provider IN (${Provedor:sqlstring}) AND\n ('${Zone:csv}' = 'All' OR t.zone IN (${Zone:sqlstring})) AND\n ('${OS:csv}' = 'All' OR t.client_name IN (${OS:sqlstring})) AND ('${Location:csv}' = 'All' OR t.location IN (${Location:sqlstring}))\nORDER BY\n \"Provedor/Zone\";",
"refId": "A",
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "box plot download",
"type": "nline-plotlyjs-panel"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"fieldConfig": {
"defaults": {},
"overrides": []
},
"gridPos": {
"h": 8,
"w": 12,
"x": 12,
"y": 66
},
"id": 14,
"options": {
"allData": {},
"config": {},
"data": [],
"imgFormat": "png",
"layout": {
"font": {
"family": "Inter, Helvetica, Arial, sans-serif"
},
"margin": {
"b": 0,
"l": 0,
"r": 0,
"t": 0
},
"title": "Box Plot de Download por Zona",
"xaxis": {
"automargin": true,
"autorange": true,
"title": "Zona",
"type": "category"
},
"yaxis": {
"automargin": true,
"autorange": true,
"title": "Download (Mbps)"
}
},
"onclick": "// Event handling\n/*\n// 'data', 'variables', 'options', 'utils', and 'event' are passed as arguments\n\ntry {\n const { type: eventType, data: eventData } = event;\n const { timeZone, dayjs, locationService, getTemplateSrv } = utils;\n\n switch (eventType) {\n case 'click':\n console.log('Click event:', eventData.points);\n break;\n case 'select':\n console.log('Selection event:', eventData.range);\n break;\n case 'zoom':\n console.log('Zoom event:', eventData);\n break;\n default:\n console.log('Unhandled event type:', eventType, eventData);\n }\n\n console.log('Current time zone:', timeZone);\n console.log('From time:', dayjs(variables.**from).format());\n console.log('To time:', dayjs(variables.**to).format());\n\n // Example of using locationService\n // locationService.partial({ 'var-example': 'test' }, true);\n\n} catch (error) {\n console.error('Error in onclick handler:', error);\n}\n*/\n ",
"resScale": 2,
"script": "// fields[0] é \"Download (Mbps)\"\n// fields[1] é \"Zone\"\n\nvar trace = {\n type: 'violin',\n \n // Eixo Y (valores) usa a primeira coluna (índice 0)\n y: data.series[0].fields[0].values,\n \n // Eixo X (categorias) usa a segunda coluna (índice 1)\n x: data.series[0].fields[1].values\n};\n\nvar layout = {\n title: 'Box Plot de Download por Zona',\n yaxis: { title: 'Download (Mbps)' },\n xaxis: { title: 'Zona' }\n};\n\nreturn {\n data: [trace],\n layout: layout\n};",
"syncTimeRange": false,
"timeCol": ""
},
"pluginVersion": "1.8.1",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"editorMode": "code",
"format": "table",
"rawQuery": true,
"rawSql": "SELECT\n t.throughput_mbps as \"Download (Mbps)\",\n -- MUDANÇA AQUI: Usa substring com regex para pegar as duas primeiras palavras\n (substring(t.provider from '^([^\\s]+(\\s+[^\\s]+)?)') || '/' || t.zone) as \"Provedor/Zone\"\nFROM tests_union_grafana_ht t\nWHERE\n $__timeFilter(t.start_time) AND\n    t.test_type = 'download' AND\n    t.provider IN (${Provedor:sqlstring}) AND\n ('${Zone:csv}' = 'All' OR t.zone IN (${Zone:sqlstring})) AND\n ('${OS:csv}' = 'All' OR t.client_name IN (${OS:sqlstring})) AND ('${Location:csv}' = 'All' OR t.location IN (${Location:sqlstring}))\nORDER BY\n \"Provedor/Zone\";",
"refId": "A",
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "box plot download",
"type": "nline-plotlyjs-panel"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"fieldConfig": {
"defaults": {},
"overrides": []
},
"gridPos": {
"h": 8,
"w": 12,
"x": 0,
"y": 74
},
"id": 12,
"options": {
"allData": {},
"config": {},
"data": [],
"imgFormat": "png",
"layout": {
"font": {
"family": "Inter, Helvetica, Arial, sans-serif"
},
"margin": {
"b": 0,
"l": 0,
"r": 0,
"t": 0
},
"title": "Box Plot de Download por Zona",
"xaxis": {
"automargin": true,
"autorange": true,
"title": "Zona",
"type": "category"
},
"yaxis": {
"automargin": true,
"autorange": true,
"title": "Download (Mbps)"
}
},
"onclick": "// Event handling\n/*\n// 'data', 'variables', 'options', 'utils', and 'event' are passed as arguments\n\ntry {\n const { type: eventType, data: eventData } = event;\n const { timeZone, dayjs, locationService, getTemplateSrv } = utils;\n\n switch (eventType) {\n case 'click':\n console.log('Click event:', eventData.points);\n break;\n case 'select':\n console.log('Selection event:', eventData.range);\n break;\n case 'zoom':\n console.log('Zoom event:', eventData);\n break;\n default:\n console.log('Unhandled event type:', eventType, eventData);\n }\n\n console.log('Current time zone:', timeZone);\n console.log('From time:', dayjs(variables.**from).format());\n console.log('To time:', dayjs(variables.**to).format());\n\n // Example of using locationService\n // locationService.partial({ 'var-example': 'test' }, true);\n\n} catch (error) {\n console.error('Error in onclick handler:', error);\n}\n*/\n ",
"resScale": 2,
"script": "// fields[0] é \"Download (Mbps)\"\n// fields[1] é \"Zone\"\n\nvar trace = {\n type: 'box',\n \n // Eixo Y (valores) usa a primeira coluna (índice 0)\n y: data.series[0].fields[0].values,\n \n // Eixo X (categorias) usa a segunda coluna (índice 1)\n x: data.series[0].fields[1].values\n};\n\nvar layout = {\n title: 'Box Plot de Download por Zona',\n yaxis: { title: 'upload (Mbps)' },\n xaxis: { title: 'Zona' }\n};\n\nreturn {\n data: [trace],\n layout: layout\n};",
"syncTimeRange": false,
"timeCol": ""
},
"pluginVersion": "1.8.1",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"editorMode": "code",
"format": "table",
"rawQuery": true,
"rawSql": "SELECT\n t.throughput_mbps as \"Upload (Mbps)\",\n -- MUDANÇA AQUI: Usa substring com regex para pegar as duas primeiras palavras\n (substring(t.provider from '^([^\\s]+(\\s+[^\\s]+)?)') || '/' || t.zone) as \"Provedor/Zone\"\nFROM tests_union_grafana_ht t\nWHERE\n $__timeFilter(t.start_time) AND\n    t.test_type = 'upload' AND\n    t.provider IN (${Provedor:sqlstring}) AND\n ('${Zone:csv}' = 'All' OR t.zone IN (${Zone:sqlstring})) AND\n ('${OS:csv}' = 'All' OR t.client_name IN (${OS:sqlstring})) AND ('${Location:csv}' = 'All' OR t.location IN (${Location:sqlstring}))\nORDER BY\n \"Provedor/Zone\"; -- MUDANÇA AQUI",
"refId": "A",
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "box plot upload",
"type": "nline-plotlyjs-panel"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"fieldConfig": {
"defaults": {},
"overrides": []
},
"gridPos": {
"h": 8,
"w": 12,
"x": 12,
"y": 74
},
"id": 15,
"options": {
"allData": {},
"config": {},
"data": [],
"imgFormat": "png",
"layout": {
"font": {
"family": "Inter, Helvetica, Arial, sans-serif"
},
"margin": {
"b": 0,
"l": 0,
"r": 0,
"t": 0
},
"title": "Box Plot de Download por Zona",
"xaxis": {
"automargin": true,
"autorange": true,
"title": "Zona",
"type": "category"
},
"yaxis": {
"automargin": true,
"autorange": true,
"title": "Download (Mbps)"
}
},
"onclick": "// Event handling\n/*\n// 'data', 'variables', 'options', 'utils', and 'event' are passed as arguments\n\ntry {\n const { type: eventType, data: eventData } = event;\n const { timeZone, dayjs, locationService, getTemplateSrv } = utils;\n\n switch (eventType) {\n case 'click':\n console.log('Click event:', eventData.points);\n break;\n case 'select':\n console.log('Selection event:', eventData.range);\n break;\n case 'zoom':\n console.log('Zoom event:', eventData);\n break;\n default:\n console.log('Unhandled event type:', eventType, eventData);\n }\n\n console.log('Current time zone:', timeZone);\n console.log('From time:', dayjs(variables.**from).format());\n console.log('To time:', dayjs(variables.**to).format());\n\n // Example of using locationService\n // locationService.partial({ 'var-example': 'test' }, true);\n\n} catch (error) {\n console.error('Error in onclick handler:', error);\n}\n*/\n ",
"resScale": 2,
"script": "// fields[0] é \"Download (Mbps)\"\n// fields[1] é \"Zone\"\n\nvar trace = {\n type: 'violin',\n \n // Eixo Y (valores) usa a primeira coluna (índice 0)\n y: data.series[0].fields[0].values,\n \n // Eixo X (categorias) usa a segunda coluna (índice 1)\n x: data.series[0].fields[1].values\n};\n\nvar layout = {\n title: 'Box Plot de Download por Zona',\n yaxis: { title: 'upload (Mbps)' },\n xaxis: { title: 'Zona' }\n};\n\nreturn {\n data: [trace],\n layout: layout\n};",
"syncTimeRange": false,
"timeCol": ""
},
"pluginVersion": "1.8.1",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"editorMode": "code",
"format": "table",
"rawQuery": true,
"rawSql": "SELECT\n t.throughput_mbps as \"Upload (Mbps)\",\n -- MUDANÇA AQUI: Usa substring com regex para pegar as duas primeiras palavras\n (substring(t.provider from '^([^\\s]+(\\s+[^\\s]+)?)') || '/' || t.zone) as \"Provedor/Zone\"\nFROM tests_union_grafana_ht t\nWHERE\n $__timeFilter(t.start_time) AND\n    t.test_type = 'upload' AND\n    t.provider IN (${Provedor:sqlstring}) AND\n ('${Zone:csv}' = 'All' OR t.zone IN (${Zone:sqlstring})) AND\n ('${OS:csv}' = 'All' OR t.client_name IN (${OS:sqlstring})) AND ('${Location:csv}' = 'All' OR t.location IN (${Location:sqlstring}))\nORDER BY\n \"Provedor/Zone\"; -- MUDANÇA AQUI",
"refId": "A",
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "box plot upload",
"type": "nline-plotlyjs-panel"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"fieldConfig": {
"defaults": {},
"overrides": []
},
"gridPos": {
"h": 8,
"w": 12,
"x": 0,
"y": 82
},
"id": 13,
"options": {
"allData": {},
"config": {},
"data": [],
"imgFormat": "png",
"layout": {
"font": {
"family": "Inter, Helvetica, Arial, sans-serif"
},
"margin": {
"b": 0,
"l": 0,
"r": 0,
"t": 0
},
"title": "Box Plot de RTT por Zona (µs)",
"xaxis": {
"automargin": true,
"autorange": true,
"title": "Zona",
"type": "category"
},
"yaxis": {
"automargin": true,
"autorange": true,
"title": "RTT (µs)"
}
},
"onclick": "// Event handling\n/*\n// 'data', 'variables', 'options', 'utils', and 'event' are passed as arguments\n\ntry {\n const { type: eventType, data: eventData } = event;\n const { timeZone, dayjs, locationService, getTemplateSrv } = utils;\n\n switch (eventType) {\n case 'click':\n console.log('Click event:', eventData.points);\n break;\n case 'select':\n console.log('Selection event:', eventData.range);\n break;\n case 'zoom':\n console.log('Zoom event:', eventData);\n break;\n default:\n console.log('Unhandled event type:', eventType, eventData);\n }\n\n console.log('Current time zone:', timeZone);\n console.log('From time:', dayjs(variables.**from).format());\n console.log('To time:', dayjs(variables.**to).format());\n\n // Example of using locationService\n // locationService.partial({ 'var-example': 'test' }, true);\n\n} catch (error) {\n console.error('Error in onclick handler:', error);\n}\n*/\n ",
"resScale": 2,
"script": "// fields[0] é \"RTT (µs)\"\n// fields[1] é \"Zone\"\n\nvar trace = {\n type: 'box',\n \n // Eixo Y (valores) usa a primeira coluna (índice 0)\n y: data.series[0].fields[0].values,\n \n // Eixo X (categorias) usa a segunda coluna (índice 1)\n x: data.series[0].fields[1].values\n};\n\n// Layout de fallback com a unidade corrigida\nvar layout = {\n title: 'Box Plot de RTT por Zona (µs)',\n yaxis: { title: 'RTT (µs)' },\n xaxis: { title: 'Zona' }\n};\n\nreturn {\n data: [trace],\n layout: layout\n};",
"syncTimeRange": false,
"timeCol": ""
},
"pluginVersion": "1.8.1",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"editorMode": "code",
"format": "table",
"rawQuery": true,
"rawSql": "SELECT\n t.min_rtt as \"RTT (µs)\",\n -- MUDANÇA AQUI: Usa substring com regex para pegar as duas primeiras palavras\n (substring(t.provider from '^([^\\s]+(\\s+[^\\s]+)?)') || '/' || t.zone) as \"Provedor/Zone\"\nFROM tests_union_grafana_ht t\nWHERE\n $__timeFilter(t.start_time) AND\n    t.provider IN (${Provedor:sqlstring}) AND\n ('${Zone:csv}' = 'All' OR t.zone IN (${Zone:sqlstring})) AND\n ('${OS:csv}' = 'All' OR t.client_name IN (${OS:sqlstring})) AND ('${Location:csv}' = 'All' OR t.location IN (${Location:sqlstring})) AND\n t.min_rtt <= 1500000\nORDER BY\n \"Provedor/Zone\"; -- MUDANÇA AQUI",
"refId": "A",
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "box plot rtt",
"type": "nline-plotlyjs-panel"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"fieldConfig": {
"defaults": {},
"overrides": []
},
"gridPos": {
"h": 8,
"w": 12,
"x": 12,
"y": 82
},
"id": 17,
"options": {
"allData": {},
"config": {},
"data": [],
"imgFormat": "png",
"layout": {
"font": {
"family": "Inter, Helvetica, Arial, sans-serif"
},
"margin": {
"b": 0,
"l": 0,
"r": 0,
"t": 0
},
"title": "Box Plot de RTT por Zona (µs)",
"xaxis": {
"automargin": true,
"autorange": true,
"title": "Zona",
"type": "category"
},
"yaxis": {
"automargin": true,
"autorange": true,
"title": "RTT (µs)"
}
},
"onclick": "// Event handling\n/*\n// 'data', 'variables', 'options', 'utils', and 'event' are passed as arguments\n\ntry {\n const { type: eventType, data: eventData } = event;\n const { timeZone, dayjs, locationService, getTemplateSrv } = utils;\n\n switch (eventType) {\n case 'click':\n console.log('Click event:', eventData.points);\n break;\n case 'select':\n console.log('Selection event:', eventData.range);\n break;\n case 'zoom':\n console.log('Zoom event:', eventData);\n break;\n default:\n console.log('Unhandled event type:', eventType, eventData);\n }\n\n console.log('Current time zone:', timeZone);\n console.log('From time:', dayjs(variables.**from).format());\n console.log('To time:', dayjs(variables.**to).format());\n\n // Example of using locationService\n // locationService.partial({ 'var-example': 'test' }, true);\n\n} catch (error) {\n console.error('Error in onclick handler:', error);\n}\n*/\n ",
"resScale": 2,
"script": "// fields[0] é \"RTT (µs)\"\n// fields[1] é \"Zone\"\n\nvar trace = {\n type: 'violin',\n \n // Eixo Y (valores) usa a primeira coluna (índice 0)\n y: data.series[0].fields[0].values,\n \n // Eixo X (categorias) usa a segunda coluna (índice 1)\n x: data.series[0].fields[1].values\n};\n\n// Layout de fallback com a unidade corrigida\nvar layout = {\n title: 'Box Plot de RTT por Zona (µs)',\n yaxis: { title: 'RTT (µs)' },\n xaxis: { title: 'Zona' }\n};\n\nreturn {\n data: [trace],\n layout: layout\n};",
"syncTimeRange": false,
"timeCol": ""
},
"pluginVersion": "1.8.1",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"editorMode": "code",
"format": "table",
"rawQuery": true,
"rawSql": "SELECT\n t.min_rtt as \"RTT (µs)\",\n -- MUDANÇA AQUI: Usa substring com regex para pegar as duas primeiras palavras\n (substring(t.provider from '^([^\\s]+(\\s+[^\\s]+)?)') || '/' || t.zone) as \"Provedor/Zone\"\nFROM tests_union_grafana_ht t\nWHERE\n $__timeFilter(t.start_time) AND\n    t.provider IN (${Provedor:sqlstring}) AND\n ('${Zone:csv}' = 'All' OR t.zone IN (${Zone:sqlstring})) AND\n ('${OS:csv}' = 'All' OR t.client_name IN (${OS:sqlstring})) AND ('${Location:csv}' = 'All' OR t.location IN (${Location:sqlstring})) AND\n t.min_rtt <= 1500000\nORDER BY\n \"Provedor/Zone\"; -- MUDANÇA AQUI",
"refId": "A",
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "box plot rtt",
"type": "nline-plotlyjs-panel"
}
],
"preload": false,
"schemaVersion": 41,
"tags": [],
"templating": {
"list": [
{
"current": {
"text": [
"Henet Telecomunicacoes Ltda"
],
"value": [
"Henet Telecomunicacoes Ltda"
]
},
"includeAll": false,
"multi": true,
"name": "Provedor",
"options": [
{
"selected": false,
"text": "ALGAR TELECOM S/A",
"value": "ALGAR TELECOM S/A"
},
{
"selected": false,
"text": "BRISANET SERVICOS DE TELECOMUNICACOES LTDA",
"value": "BRISANET SERVICOS DE TELECOMUNICACOES LTDA"
},
{
"selected": false,
"text": "Claro S/A",
"value": "Claro S/A"
},
{
"selected": false,
"text": "CLARO S.A.",
"value": "CLARO S.A."
},
{
"selected": false,
"text": "COPEL Telecomunicações S.A.",
"value": "COPEL Telecomunicações S.A."
},
{
"selected": false,
"text": "Friburgo Online LTDA ME",
"value": "Friburgo Online LTDA ME"
},
{
"selected": false,
"text": "Gigalink de Nova Friburgo Solucoes em Rede Multimi",
"value": "Gigalink de Nova Friburgo Solucoes em Rede Multimi"
},
{
"selected": true,
"text": "Henet Telecomunicacoes Ltda",
"value": "Henet Telecomunicacoes Ltda"
},
{
"selected": false,
"text": "K1 Telecom e Multimidia LTDA",
"value": "K1 Telecom e Multimidia LTDA"
},
{
"selected": false,
"text": "K2 Telecom e Multimidia LTDA ME",
"value": "K2 Telecom e Multimidia LTDA ME"
},
{
"selected": false,
"text": "Mob Servicos de Telecomunicacoes Ltda",
"value": "Mob Servicos de Telecomunicacoes Ltda"
},
{
"selected": false,
"text": "Netskope Inc",
"value": "Netskope Inc"
},
{
"selected": false,
"text": "Space Exploration Technologies Corporation",
"value": "Space Exploration Technologies Corporation"
},
{
"selected": false,
"text": "TELEFONICA BRASIL S.A",
"value": "TELEFONICA BRASIL S.A"
},
{
"selected": false,
"text": "Telefonica Data S.A.",
"value": "Telefonica Data S.A."
},
{
"selected": false,
"text": "Telemar Norte Leste S.A.",
"value": "Telemar Norte Leste S.A."
},
{
"selected": false,
"text": "Tim Celular S.A.",
"value": "Tim Celular S.A."
},
{
"selected": false,
"text": "ZSCALER INC",
"value": "ZSCALER INC"
},
{
"selected": false,
"text": "VM OPENLINK COMUNICACAO MULTIMIDIA E INFORMATICA L",
"value": "VM OPENLINK COMUNICACAO MULTIMIDIA E INFORMATICA L"
}
],
"query": "ALGAR TELECOM S/A,BRISANET SERVICOS DE TELECOMUNICACOES LTDA,Claro S/A,CLARO S.A.,COPEL Telecomunicações S.A.,Friburgo Online LTDA ME,Gigalink de Nova Friburgo Solucoes em Rede Multimi,Henet Telecomunicacoes Ltda,K1 Telecom e Multimidia LTDA,K2 Telecom e Multimidia LTDA ME,Mob Servicos de Telecomunicacoes Ltda,Netskope Inc,Space Exploration Technologies Corporation,TELEFONICA BRASIL S.A,Telefonica Data S.A.,Telemar Norte Leste S.A.,Tim Celular S.A.,ZSCALER INC,VM OPENLINK COMUNICACAO MULTIMIDIA E INFORMATICA L",
"type": "custom"
},
{
"allowCustomValue": false,
"current": {
"text": "All",
"value": [
"$__all"
]
},
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"definition": "SELECT location FROM (\n SELECT \n location,\n COUNT(*) AS total\n FROM tests*union_grafana_ht\n WHERE\n $__timeFilter(start_time)\n        AND provider IN (${Provedor:sqlstring})\n AND location IS NOT NULL\n GROUP BY location\n) AS sub\nORDER BY total DESC\nLIMIT 200;",
"description": "",
"includeAll": true,
"label": "Location",
"multi": true,
"name": "Location",
"options": [],
"query": "SELECT location FROM (\n SELECT \n location,\n COUNT(*) AS total\n FROM tests*union_grafana_ht\n WHERE\n $__timeFilter(start_time)\n        AND provider IN (${Provedor:sqlstring})\n AND location IS NOT NULL\n GROUP BY location\n) AS sub\nORDER BY total DESC\nLIMIT 200;",
"refresh": 1,
"regex": "",
"type": "query"
},
{
"allowCustomValue": false,
"current": {
"text": "All",
"value": [
"$__all"
]
},
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"definition": "SELECT \n client_name || ' (' || COUNT(*) || ')' AS **text,\n client_name AS **value\nFROM tests*union_grafana_ht\nWHERE\n $__timeFilter(start_time)\n    AND provider IN (${Provedor:sqlstring})\n AND ('${Location:csv}' = 'All' OR location IN (${Location:sqlstring}))\n AND client_name IS NOT NULL\n AND client_name != ''\nGROUP BY client_name\nORDER BY COUNT(*) DESC\nLIMIT 200;",
"includeAll": true,
"label": "OS",
"multi": true,
"name": "OS",
"options": [],
"query": "SELECT \n client*name || ' (' || COUNT(*) || ')' AS **text,\n client_name AS **value\nFROM tests*union_grafana_ht\nWHERE\n $__timeFilter(start_time)\n    AND provider IN (${Provedor:sqlstring})\n AND ('${Location:csv}' = 'All' OR location IN (${Location:sqlstring}))\n AND client_name IS NOT NULL\n AND client_name != ''\nGROUP BY client_name\nORDER BY COUNT(*) DESC\nLIMIT 200;",
"refresh": 1,
"regex": "",
"type": "query"
},
{
"allowCustomValue": false,
"current": {
"text": "All",
"value": "$__all"
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "fex2zuup79ibkb"
        },
        "definition": "SELECT \n    zone || ' (' || COUNT(*) || ')' AS __text,\n    zone AS __value\nFROM tests_union_grafana_ht\nWHERE\n    $__timeFilter(start_time)\n    AND provider IN (${Provedor:sqlstring})\n AND ('${Location:csv}' = 'All' OR location IN (${Location:sqlstring}))\n AND ('${OS:csv}' = 'All' OR client_name IN (${OS:sqlstring}))\n AND zone IS NOT NULL\nGROUP BY zone\nORDER BY COUNT(_) DESC\nLIMIT 200;",
"includeAll": true,
"label": "Zone",
"multi": true,
"name": "Zone",
"options": [],
"query": "SELECT \n zone || ' (' || COUNT(_) || ')' AS **text,\n zone AS **value\nFROM tests_union_grafana_ht\nWHERE\n $__timeFilter(start_time)\n    AND provider IN (${Provedor:sqlstring})\n AND ('${Location:csv}' = 'All' OR location IN (${Location:sqlstring}))\n AND ('${OS:csv}' = 'All' OR client_name IN (${OS:sqlstring}))\n AND zone IS NOT NULL\nGROUP BY zone\nORDER BY COUNT(\*) DESC\nLIMIT 200;",
"refresh": 1,
"regex": "",
"type": "query"
}
]
},
"time": {
"from": "2026-03-09T03:00:00.000Z",
"to": "2026-03-13T02:59:59.000Z"
},
"timepicker": {
"refresh_intervals": []
},
"timezone": "browser",
"title": "NDT_7_Big_Query",
"uid": "e2bd6f0f-d848-479e-a44b-c64cbed28a72ass",
"version": 9
}

{
"annotations": {
"list": [
{
"builtIn": 1,
"datasource": {
"type": "grafana",
"uid": "-- Grafana --"
},
"enable": true,
"hide": true,
"iconColor": "rgba(0, 211, 255, 1)",
"name": "Annotations & Alerts",
"type": "dashboard"
}
]
},
"editable": true,
"fiscalYearStartMonth": 0,
"graphTooltip": 0,
"id": 72,
"links": [],
"panels": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"fieldConfig": {
"defaults": {
"color": {
"mode": "thresholds"
},
"custom": {
"align": "auto",
"cellOptions": {
"type": "auto"
},
"inspect": false
},
"mappings": [],
"thresholds": {
"mode": "absolute",
"steps": [
{
"color": "green"
},
{
"color": "red",
"value": 80
}
]
}
},
"overrides": []
},
"gridPos": {
"h": 15,
"w": 24,
"x": 0,
"y": 0
},
"id": 1,
"options": {
"cellHeight": "sm",
"footer": {
"countRows": false,
"fields": "",
"reducer": [
"sum"
],
"show": false
},
"showHeader": true,
"sortBy": [
{
"desc": true,
"displayName": "End Time"
}
]
},
"pluginVersion": "12.0.2",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"editorMode": "code",
"format": "table",
"rawQuery": true,
"rawSql": "SELECT\n t.start*time AS \"Time\",\n t.start_time AS \"Start Time\",\n t.end_time AS \"End Time\",\n ROUND((t.duration_ms / 1000.0)::numeric, 2) AS \"Duration (s)\",\n t.client_ip::text AS \"IP do Cliente\",\n t.test_type AS \"Tipo de Teste\",\n ROUND(t.throughput_mbps::numeric, 2) AS \"Throughput (Mbps)\",\n ROUND((t.min_rtt / 1000.0)::numeric, 2) AS \"RTT (ms)\",\n t.location AS \"Location\",\n t.loss_rate as \"Package_loss\"\nFROM tests_union_grafana_ht t\nWHERE\n $__timeFilter(t.start_time) AND\n    t.test_type IN ('download', 'upload') AND\n    t.provider IN (${Provedor:sqlstring}) AND\n ('${Zone:csv}' = 'All' OR t.zone IN (${Zone:sqlstring})) AND\n ('${OS:csv}' = 'All' OR t.client_name IN (${OS:sqlstring})) AND\n ('${Location:csv}' = 'All' OR t.location IN (${Location:sqlstring})) \nORDER BY \"Time\" DESC\nLIMIT 10000;",
"refId": "A",
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "New panel",
"type": "table"
}
],
"preload": false,
"schemaVersion": 41,
"tags": [],
"templating": {
"list": [
{
"current": {
"text": [
"Gigalink de Nova Friburgo Solucoes em Rede Multimi"
],
"value": [
"Gigalink de Nova Friburgo Solucoes em Rede Multimi"
]
},
"includeAll": true,
"multi": true,
"name": "Provedor",
"options": [
{
"selected": false,
"text": "ALGAR TELECOM S/A",
"value": "ALGAR TELECOM S/A"
},
{
"selected": false,
"text": "BRISANET SERVICOS DE TELECOMUNICACOES LTDA",
"value": "BRISANET SERVICOS DE TELECOMUNICACOES LTDA"
},
{
"selected": false,
"text": "Claro S/A",
"value": "Claro S/A"
},
{
"selected": false,
"text": "CLARO S.A.",
"value": "CLARO S.A."
},
{
"selected": false,
"text": "COPEL Telecomunicações S.A.",
"value": "COPEL Telecomunicações S.A."
},
{
"selected": false,
"text": "Friburgo Online LTDA ME",
"value": "Friburgo Online LTDA ME"
},
{
"selected": true,
"text": "Gigalink de Nova Friburgo Solucoes em Rede Multimi",
"value": "Gigalink de Nova Friburgo Solucoes em Rede Multimi"
},
{
"selected": false,
"text": "Henet Telecomunicacoes Ltda",
"value": "Henet Telecomunicacoes Ltda"
},
{
"selected": false,
"text": "K1 Telecom e Multimidia LTDA",
"value": "K1 Telecom e Multimidia LTDA"
},
{
"selected": false,
"text": "K2 Telecom e Multimidia LTDA ME",
"value": "K2 Telecom e Multimidia LTDA ME"
},
{
"selected": false,
"text": "Mob Servicos de Telecomunicacoes Ltda",
"value": "Mob Servicos de Telecomunicacoes Ltda"
},
{
"selected": false,
"text": "Netskope Inc",
"value": "Netskope Inc"
},
{
"selected": false,
"text": "Space Exploration Technologies Corporation",
"value": "Space Exploration Technologies Corporation"
},
{
"selected": false,
"text": "TELEFONICA BRASIL S.A",
"value": "TELEFONICA BRASIL S.A"
},
{
"selected": false,
"text": "Telefonica Data S.A.",
"value": "Telefonica Data S.A."
},
{
"selected": false,
"text": "Telemar Norte Leste S.A.",
"value": "Telemar Norte Leste S.A."
},
{
"selected": false,
"text": "Tim Celular S.A.",
"value": "Tim Celular S.A."
},
{
"selected": false,
"text": "ZSCALER INC",
"value": "ZSCALER INC"
},
{
"selected": false,
"text": "VM OPENLINK COMUNICAÇÃO E INFORMÁTICA L",
"value": "VM OPENLINK COMUNICAÇÃO E INFORMÁTICA L"
}
],
"query": "ALGAR TELECOM S/A,BRISANET SERVICOS DE TELECOMUNICACOES LTDA,Claro S/A,CLARO S.A.,COPEL Telecomunicações S.A.,Friburgo Online LTDA ME,Gigalink de Nova Friburgo Solucoes em Rede Multimi,Henet Telecomunicacoes Ltda,K1 Telecom e Multimidia LTDA,K2 Telecom e Multimidia LTDA ME,Mob Servicos de Telecomunicacoes Ltda,Netskope Inc,Space Exploration Technologies Corporation,TELEFONICA BRASIL S.A,Telefonica Data S.A.,Telemar Norte Leste S.A.,Tim Celular S.A.,ZSCALER INC,VM OPENLINK COMUNICAÇÃO E INFORMÁTICA L",
"type": "custom"
},
{
"allowCustomValue": false,
"current": {
"text": "All",
"value": [
"$__all"
]
},
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"definition": "WITH filtered_data AS ( SELECT location FROM tests_union_grafana_ht WHERE $__timeFilter(start_time) AND location IS NOT NULL AND ('${Provedor:csv}' = 'All' OR provider IN (${Provedor:sqlstring})) ) SELECT location FROM filtered_data GROUP BY location ORDER BY COUNT(*) DESC;",
"description": "",
"includeAll": true,
"label": "Location",
"multi": true,
"name": "Location",
"options": [],
"query": "WITH filtered_data AS ( SELECT location FROM tests_union_grafana_ht WHERE $__timeFilter(start_time) AND location IS NOT NULL AND ('${Provedor:csv}' = 'All' OR provider IN (${Provedor:sqlstring})) ) SELECT location FROM filtered_data GROUP BY location ORDER BY COUNT(*) DESC;",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": [
            "ist (1592)",
            "ndt7-android (22)",
            "speed-measurementlab-net-1 (22)"
          ],
          "value": [
            "ist",
            "ndt7-android",
            "speed-measurementlab-net-1"
          ]
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "fex2zuup79ibkb"
        },
        "definition": "WITH filtered_data AS ( SELECT client_name FROM tests_union_grafana_ht WHERE $__timeFilter(start_time) AND client_name IS NOT NULL AND client_name != '' AND ('${Provedor:csv}' = 'All' OR provider IN (${Provedor:sqlstring})) AND ('${Location:csv}' = 'All' OR location IN (${Location:sqlstring})) ) SELECT client_name || ' (' || COUNT(*) || ')' AS __text, client_name AS __value FROM filtered_data GROUP BY client_name ORDER BY COUNT(*) DESC;",
        "includeAll": true,
        "label": "OS",
        "multi": true,
        "name": "OS",
        "options": [],
        "query": "WITH filtered_data AS ( SELECT client_name FROM tests_union_grafana_ht WHERE $__timeFilter(start_time) AND client_name IS NOT NULL AND client_name != '' AND ('${Provedor:csv}' = 'All' OR provider IN (${Provedor:sqlstring})) AND ('${Location:csv}' = 'All' OR location IN (${Location:sqlstring})) ) SELECT client_name || ' (' || COUNT(*) || ')' AS __text, client_name AS __value FROM filtered_data GROUP BY client_name ORDER BY COUNT(*) DESC;",
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "All",
          "value": [
            "$**all"
]
},
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "fex2zuup79ibkb"
},
"definition": "WITH filtered_data AS ( SELECT zone FROM tests_union_grafana_ht WHERE $**timeFilter(start_time) AND zone IS NOT NULL AND ('${Provedor:csv}' = 'All' OR provider IN (${Provedor:sqlstring})) AND ('${Location:csv}' = 'All' OR location IN (${Location:sqlstring})) AND ('${OS:csv}' = 'All' OR client_name IN (${OS:sqlstring})) ) SELECT zone || ' (' || COUNT(*) || ')' AS **text, zone AS **value FROM filtered*data GROUP BY zone ORDER BY COUNT(*) DESC;",
"includeAll": true,
"label": "Zone",
"multi": true,
"name": "Zone",
"options": [],
"query": "WITH filtered*data AS ( SELECT zone FROM tests_union_grafana_ht WHERE $__timeFilter(start_time) AND zone IS NOT NULL AND ('${Provedor:csv}' = 'All' OR provider IN (${Provedor:sqlstring})) AND ('${Location:csv}' = 'All' OR location IN (${Location:sqlstring})) AND ('${OS:csv}' = 'All' OR client_name IN (${OS:sqlstring})) ) SELECT zone || ' (' || COUNT(*) || ')' AS **text, zone AS **value FROM filtered*data GROUP BY zone ORDER BY COUNT(\*) DESC;",
"refresh": 1,
"regex": "",
"type": "query"
}
]
},
"time": {
"from": "2026-03-01T00:00:00.000Z",
"to": "2026-03-29T23:59:59.000Z"
},
"timepicker": {
"refresh_intervals": []
},
"timezone": "utc",
"title": "NDT_7_Big_Query_tables_export",
"uid": "e2bd6f0f-d848-479e-a44b-c64cbed28a75",
"version": 13
}

## QuestDB

### Agrupado

{
"annotations": {
"list": [
{
"builtIn": 1,
"datasource": {
"type": "grafana",
"uid": "-- QuestDB --"
},
"enable": true,
"hide": true,
"iconColor": "rgba(0, 211, 255, 1)",
"name": "Annotations & Alerts",
"type": "dashboard"
}
]
},
"editable": true,
"fiscalYearStartMonth": 0,
"graphTooltip": 1,
"id": 173,
"links": [],
"panels": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"fieldConfig": {
"defaults": {
"color": {
"mode": "palette-classic"
},
"custom": {
"axisBorderShow": false,
"axisCenteredZero": false,
"axisColorMode": "text",
"axisLabel": "",
"axisPlacement": "auto",
"barAlignment": 0,
"barWidthFactor": 0.6,
"drawStyle": "points",
"fillOpacity": 0,
"gradientMode": "none",
"hideFrom": {
"legend": false,
"tooltip": false,
"viz": false
},
"insertNulls": false,
"lineInterpolation": "linear",
"lineWidth": 0,
"pointSize": 5,
"scaleDistribution": {
"type": "linear"
},
"showPoints": "always",
"spanNulls": false,
"stacking": {
"group": "A",
"mode": "none"
},
"thresholdsStyle": {
"mode": "off"
}
},
"mappings": [],
"thresholds": {
"mode": "absolute",
"steps": [
{
"color": "green"
},
{
"color": "red",
"value": 80
}
]
},
"unit": "bps"
},
"overrides": []
},
"gridPos": {
"h": 12,
"w": 14,
"x": 0,
"y": 0
},
"id": 1,
"options": {
"legend": {
"calcs": [
"mean",
"last"
],
"displayMode": "list",
"placement": "bottom",
"showLegend": true
},
"tooltip": {
"hideZeros": false,
"mode": "single",
"sort": "none"
}
},
"pluginVersion": "12.0.2",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"editorMode": "code",
"format": 0,
"rawQuery": true,
"rawSql": "SELECT\n cast(cast(test*timestamp as long) / 300000 * 300000 as timestamp) as time,\n AVG(download*tp_bps) as \"Download (bps)\",\n mac_address AS \"MAC\"\nFROM ndt_tests\nWHERE\n $\_\_timeFilter(test_timestamp) AND\n download_tp_bps >= 0 \nGROUP BY time, \"MAC\"\nORDER BY 1 ASC;",
"refId": "A",
"selectedFormat": 0,
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "Download",
"type": "timeseries"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"fieldConfig": {
"defaults": {
"color": {
"mode": "continuous-RdYlGr"
},
"custom": {
"align": "auto",
"cellOptions": {
"type": "color-background"
},
"inspect": false
},
"mappings": [],
"thresholds": {
"mode": "absolute",
"steps": [
{
"color": "red"
},
{
"color": "yellow",
"value": 50
},
{
"color": "green",
"value": 100
}
]
},
"unit": "decbits"
},
"overrides": [
{
"matcher": {
"id": "byName",
"options": "Total Tests"
},
"properties": [
{
"id": "unit",
"value": "none"
}
]
}
]
},
"gridPos": {
"h": 12,
"w": 10,
"x": 14,
"y": 0
},
"id": 2,
"options": {
"cellHeight": "sm",
"footer": {
"countRows": false,
"fields": "",
"reducer": [
"sum"
],
"show": true
},
"showHeader": true,
"sortBy": [
{
"desc": false,
"displayName": "Min (Mbps)"
}
]
},
"pluginVersion": "12.0.2",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"editorMode": "code",
"format": 0,
"rawQuery": true,
"rawSql": "SELECT\n mac_address AS \"MAC\",\n COUNT(*) AS \"Total Tests\",\n AVG(download_tp_bps) AS \"Avg (bps)\",\n MIN(download_tp_bps) AS \"Min (bps)\",\n MAX(download_tp_bps) AS \"Max (bps)\",\n approx_median(download_tp_bps, 0) AS \"Median (bps)\"\nFROM ndt_tests\nWHERE\n $__timeFilter(test_timestamp) AND\n    download_tp_bps >= 0 \nGROUP BY mac_address\nORDER BY \"Total Tests\" DESC;",
          "refId": "A",
          "selectedFormat": 0,
          "sql": {
            "columns": [
              {
                "parameters": [],
                "type": "function"
              }
            ],
            "groupBy": [
              {
                "property": {
                  "type": "string"
                },
                "type": "groupBy"
              }
            ],
            "limit": 50
          }
        }
      ],
      "title": "Download dados",
      "type": "table"
    },
    {
      "datasource": {
        "type": "grafana-postgresql-datasource",
        "uid": "efsezsv9ajri8f"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "axisBorderShow": false,
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "barWidthFactor": 0.6,
            "drawStyle": "points",
            "fillOpacity": 0,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "insertNulls": false,
            "lineInterpolation": "linear",
            "lineWidth": 0,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "always",
            "spanNulls": false,
            "stacking": {
              "group": "A",
              "mode": "none"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green"
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          },
          "unit": "bps"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 13,
        "w": 14,
        "x": 0,
        "y": 12
      },
      "id": 3,
      "options": {
        "legend": {
          "calcs": [
            "mean",
            "last"
          ],
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true
        },
        "tooltip": {
          "hideZeros": false,
          "mode": "single",
          "sort": "none"
        }
      },
      "pluginVersion": "12.0.2",
      "targets": [
        {
          "datasource": {
            "type": "grafana-postgresql-datasource",
            "uid": "efsezsv9ajri8f"
          },
          "editorMode": "code",
          "format": 0,
          "rawQuery": true,
          "rawSql": "SELECT\n    cast(cast(test_timestamp as long) / 300000 * 300000 as timestamp) as time,\n    AVG(upload_tp_bps) as \"Upload (bps)\",\n    mac_address AS \"MAC\"\nFROM ndt_tests\nWHERE\n    $__timeFilter(test_timestamp) AND\n    upload_tp_bps >= 0 \nGROUP BY time, \"MAC\"\nORDER BY 1 ASC;",
          "refId": "A",
          "selectedFormat": 0,
          "sql": {
            "columns": [
              {
                "parameters": [],
                "type": "function"
              }
            ],
            "groupBy": [
              {
                "property": {
                  "type": "string"
                },
                "type": "groupBy"
              }
            ],
            "limit": 50
          }
        }
      ],
      "title": "Upload",
      "type": "timeseries"
    },
    {
      "datasource": {
        "type": "grafana-postgresql-datasource",
        "uid": "efsezsv9ajri8f"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "continuous-RdYlGr"
          },
          "custom": {
            "align": "auto",
            "cellOptions": {
              "type": "color-background"
            },
            "inspect": false
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "red"
              },
              {
                "color": "yellow",
                "value": 50
              },
              {
                "color": "green",
                "value": 100
              }
            ]
          },
          "unit": "decbits"
        },
        "overrides": [
          {
            "matcher": {
              "id": "byName",
              "options": "Total Tests"
            },
            "properties": [
              {
                "id": "unit",
                "value": "none"
              }
            ]
          }
        ]
      },
      "gridPos": {
        "h": 13,
        "w": 10,
        "x": 14,
        "y": 12
      },
      "id": 4,
      "options": {
        "cellHeight": "sm",
        "footer": {
          "countRows": false,
          "fields": "",
          "reducer": [
            "sum"
          ],
          "show": true
        },
        "showHeader": true,
        "sortBy": [
          {
            "desc": true,
            "displayName": "Total Tests"
          }
        ]
      },
      "pluginVersion": "12.0.2",
      "targets": [
        {
          "datasource": {
            "type": "grafana-postgresql-datasource",
            "uid": "efsezsv9ajri8f"
          },
          "editorMode": "code",
          "format": 0,
          "rawQuery": true,
          "rawSql": "SELECT\n    mac_address AS \"MAC\",\n    COUNT(*) AS \"Total Tests\",\n    AVG(upload_tp_bps) AS \"Avg (bps)\",\n    MIN(upload_tp_bps) AS \"Min (bps)\",\n    MAX(upload_tp_bps) AS \"Max (bps)\",\n    approx_median(upload_tp_bps, 0) AS \"Median (bps)\"\nFROM ndt_tests\nWHERE\n    $__timeFilter(test_timestamp) AND\n    upload_tp_bps >= 0 \nGROUP BY mac_address\nORDER BY \"Total Tests\" DESC;",
          "refId": "A",
          "selectedFormat": 0,
          "sql": {
            "columns": [
              {
                "parameters": [],
                "type": "function"
              }
            ],
            "groupBy": [
              {
                "property": {
                  "type": "string"
                },
                "type": "groupBy"
              }
            ],
            "limit": 50
          }
        }
      ],
      "title": "Upload dados",
      "type": "table"
    },
    {
      "datasource": {
        "type": "grafana-postgresql-datasource",
        "uid": "efsezsv9ajri8f"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "axisBorderShow": false,
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "barWidthFactor": 0.6,
            "drawStyle": "points",
            "fillOpacity": 0,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "insertNulls": false,
            "lineInterpolation": "linear",
            "lineWidth": 0,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "always",
            "spanNulls": false,
            "stacking": {
              "group": "A",
              "mode": "none"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green"
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          },
          "unit": "s"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 25
      },
      "id": 5,
      "options": {
        "legend": {
          "calcs": [
            "mean",
            "last"
          ],
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true
        },
        "tooltip": {
          "hideZeros": false,
          "mode": "single",
          "sort": "none"
        }
      },
      "pluginVersion": "12.0.2",
      "targets": [
        {
          "datasource": {
            "type": "grafana-postgresql-datasource",
            "uid": "efsezsv9ajri8f"
          },
          "editorMode": "code",
          "format": 0,
          "rawQuery": true,
          "rawSql": "SELECT\n    cast(cast(test_timestamp as long) / 300000 * 300000 as timestamp) as time,\n    AVG(latency_download_sec) as \"Latency (ms)\",\n    mac_address AS \"MAC\"\nFROM ndt_tests\nWHERE\n    $__timeFilter(test_timestamp) AND\n    latency_download_sec >= 0 \nGROUP BY time, \"MAC\"\nORDER BY 1 ASC;",
          "refId": "A",
          "selectedFormat": 0,
          "sql": {
            "columns": [
              {
                "parameters": [],
                "type": "function"
              }
            ],
            "groupBy": [
              {
                "property": {
                  "type": "string"
                },
                "type": "groupBy"
              }
            ],
            "limit": 50
          }
        }
      ],
      "title": "Latency Download",
      "type": "timeseries"
    },
    {
      "datasource": {
        "type": "grafana-postgresql-datasource",
        "uid": "efsezsv9ajri8f"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "axisBorderShow": false,
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "barWidthFactor": 0.6,
            "drawStyle": "points",
            "fillOpacity": 0,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "insertNulls": false,
            "lineInterpolation": "linear",
            "lineWidth": 0,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "always",
            "spanNulls": false,
            "stacking": {
              "group": "A",
              "mode": "none"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green"
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          },
          "unit": "s"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 12,
        "y": 25
      },
      "id": 6,
      "options": {
        "legend": {
          "calcs": [
            "mean",
            "last"
          ],
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true
        },
        "tooltip": {
          "hideZeros": false,
          "mode": "single",
          "sort": "none"
        }
      },
      "pluginVersion": "12.0.2",
      "targets": [
        {
          "datasource": {
            "type": "grafana-postgresql-datasource",
            "uid": "efsezsv9ajri8f"
          },
          "editorMode": "code",
          "format": 0,
          "rawQuery": true,
          "rawSql": "SELECT\n    cast(cast(test_timestamp as long) / 300000 * 300000 as timestamp) as time,\n    AVG(latency_upload_sec) as \"Latency (s)\",\n    mac_address AS \"MAC\"\nFROM ndt_tests\nWHERE\n    $__timeFilter(test_timestamp) AND\n    latency_upload_sec >= 0 \nGROUP BY time, \"MAC\"\nORDER BY 1 ASC;",
          "refId": "A",
          "selectedFormat": 0,
          "sql": {
            "columns": [
              {
                "parameters": [],
                "type": "function"
              }
            ],
            "groupBy": [
              {
                "property": {
                  "type": "string"
                },
                "type": "groupBy"
              }
            ],
            "limit": 50
          }
        }
      ],
      "title": "Latency Upload",
      "type": "timeseries"
    },
    {
      "datasource": {
        "type": "grafana-postgresql-datasource",
        "uid": "efsezsv9ajri8f"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "axisBorderShow": false,
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "barWidthFactor": 0.6,
            "drawStyle": "points",
            "fillOpacity": 0,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "insertNulls": false,
            "lineInterpolation": "linear",
            "lineWidth": 0,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "always",
            "spanNulls": false,
            "stacking": {
              "group": "A",
              "mode": "none"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green"
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          },
          "unit": "percent"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 33
      },
      "id": 7,
      "options": {
        "legend": {
          "calcs": [
            "mean",
            "last"
          ],
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true
        },
        "tooltip": {
          "hideZeros": false,
          "mode": "single",
          "sort": "none"
        }
      },
      "pluginVersion": "12.0.2",
      "targets": [
        {
          "datasource": {
            "type": "grafana-postgresql-datasource",
            "uid": "efsezsv9ajri8f"
          },
          "editorMode": "code",
          "format": 0,
          "rawQuery": true,
          "rawSql": "SELECT\n    cast(cast(test_timestamp as long) / 300000 * 300000 as timestamp) as time,\n    AVG(download_retrans_percent) as \"Loss (%)\",\n    mac_address AS \"MAC\"\nFROM ndt_tests\nWHERE\n    $__timeFilter(test_timestamp) AND\n    download_retrans_percent >= 0 \nGROUP BY time, \"MAC\"\nORDER BY 1 ASC;",
          "refId": "A",
          "selectedFormat": 0,
          "sql": {
            "columns": [
              {
                "parameters": [],
                "type": "function"
              }
            ],
            "groupBy": [
              {
                "property": {
                  "type": "string"
                },
                "type": "groupBy"
              }
            ],
            "limit": 50
          }
        }
      ],
      "title": "Packet Loss",
      "type": "timeseries"
    }
  ],
  "preload": false,
  "schemaVersion": 41,
  "tags": [],
  "templating": {
    "list": [
      {
        "allowCustomValue": false,
        "current": {
          "text": [
            "e4:5f:01:b4:36:5d - Gigalink-NOF",
            "e4:5f:01:36:10:c8 - Gigalink-ARBU",
            "e4:5f:01:36:07:cb - Gigalink-ACB",
            "e4:5f:01:1e:2d:20 - Gigalink-CPS"
          ],
          "value": [
            "e4:5f:01:b4:36:5d",
            "e4:5f:01:36:10:c8",
            "e4:5f:01:36:07:cb",
            "e4:5f:01:1e:2d:20"
          ]
        },
        "datasource": {
          "type": "grafana-postgresql-datasource",
          "uid": "efsezsv9ajri8f"
        },
        "definition": "WITH test_counts AS (\n  SELECT mac_address, COUNT() AS total_tests\n  FROM ndt_tests\n  GROUP BY mac_address\n)\nSELECT\n  t.mac_address AS __value,\n  CONCAT(\n    t.mac_address,\n    ' - ',\n    COALESCE(d.owner, 'Sem Dono')\n  ) AS __text,\n  t.total_tests\nFROM test_counts t\nLEFT JOIN devices d ON d.mac = t.mac_address\nORDER BY t.total_tests DESC",
        "includeAll": false,
        "label": "mac_address",
        "multi": true,
        "name": "mac",
        "options": [],
        "query": "WITH test_counts AS (\n  SELECT mac_address, COUNT() AS total_tests\n  FROM ndt_tests\n  GROUP BY mac_address\n)\nSELECT\n  t.mac_address AS __value,\n  CONCAT(\n    t.mac_address,\n    ' - ',\n    COALESCE(d.owner, 'Sem Dono')\n  ) AS __text,\n  t.total_tests\nFROM test_counts t\nLEFT JOIN devices d ON d.mac = t.mac_address\nORDER BY t.total_tests DESC",
        "refresh": 2,
        "regex": "",
        "type": "query"
      },
      {
        "allowCustomValue": false,
        "current": {
          "text": "All",
          "value": [
            "$**all"
]
},
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"definition": "WITH base AS (\n SELECT\n split_part(server_ip, '/', 1) AS ip,\n MAX(server_fqdn) AS fqdn,\n COUNT() AS n\n FROM ndt_tests\n WHERE server_ip IS NOT NULL\n GROUP BY split_part(server_ip, '/', 1)\n)\nSELECT\n CONCAT(ip, ' - ', fqdn) AS **text,\n ip AS **value,\n n AS total_testes\nFROM base\nORDER BY total_testes DESC",
"includeAll": true,
"label": "server_ip",
"multi": true,
"name": "server",
"options": [],
"query": "WITH base AS (\n SELECT\n split_part(server_ip, '/', 1) AS ip,\n MAX(server_fqdn) AS fqdn,\n COUNT() AS n\n FROM ndt_tests\n WHERE server_ip IS NOT NULL\n GROUP BY split_part(server_ip, '/', 1)\n)\nSELECT\n CONCAT(ip, ' - ', fqdn) AS **text,\n ip AS \_\_value,\n n AS total_testes\nFROM base\nORDER BY total_testes DESC",
"refresh": 2,
"regex": "",
"type": "query"
}
]
},
"time": {
"from": "now-7d",
"to": "now"
},
"timepicker": {},
"timezone": "browser",
"title": "agrupado",
"uid": "questdb-agrupado",
"version": 4
}

### Individual

{
"annotations": {
"list": [
{
"builtIn": 1,
"datasource": {
"type": "grafana",
"uid": "-- Grafana --"
},
"enable": true,
"hide": true,
"iconColor": "rgba(0, 211, 255, 1)",
"name": "Annotations & Alerts",
"type": "dashboard"
}
]
},
"editable": true,
"fiscalYearStartMonth": 0,
"graphTooltip": 0,
"id": 174,
"links": [],
"panels": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"fieldConfig": {
"defaults": {
"color": {
"mode": "thresholds"
},
"links": [
{
"targetBlank": true,
"title": "Monitoramento",
"url": "http://grafana.land.ufrj.br/d/questdb-monitoramento-e-logs/monitoramento-e-logs?${mac:queryparam}"
}
],
"mappings": [
{
"options": {
"from": 0,
"result": {
"color": "green",
"index": 0,
"text": "Online"
},
"to": 300
},
"type": "range"
},
{
"options": {
"from": 300,
"result": {
"color": "red",
"index": 1,
"text": "Offline"
}
},
"type": "range"
}
],
"thresholds": {
"mode": "absolute",
"steps": [
{
"color": "green"
},
{
"color": "red",
"value": 300
}
]
},
"unit": "s"
},
"overrides": []
},
"gridPos": {
"h": 7,
"w": 10,
"x": 0,
"y": 0
},
"id": 1,
"options": {
"colorMode": "value",
"graphMode": "area",
"justifyMode": "auto",
"orientation": "auto",
"percentChangeColorMode": "standard",
"reduceOptions": {
"calcs": [
"lastNotNull"
],
"fields": "",
"values": false
},
"showPercentChange": false,
"textMode": "auto",
"wideLayout": true
},
"pluginVersion": "12.0.2",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"editorMode": "code",
"format": 0,
"rawQuery": true,
"rawSql": "SELECT EXTRACT(EPOCH FROM now() - last*ping) AS \"seconds\"\nFROM devices\nWHERE mac = $mac;",
          "refId": "A",
          "selectedFormat": 0,
          "sql": {
            "columns": [
              {
                "parameters": [],
                "type": "function"
              }
            ],
            "groupBy": [
              {
                "property": {
                  "type": "string"
                },
                "type": "groupBy"
              }
            ],
            "limit": 50
          }
        }
      ],
      "title": "Status",
      "type": "stat"
    },
    {
      "datasource": {
        "type": "grafana-postgresql-datasource",
        "uid": "efsezsv9ajri8f"
      },
      "description": "D5: quebrado em 2 targets (Last Test + Next Test) ao inves de UNION ALL. CTEs encadeadas nao funcionam no QuestDB.",
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "thresholds"
          },
          "custom": {
            "align": "auto",
            "cellOptions": {
              "type": "auto"
            },
            "inspect": false
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green"
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          }
        },
        "overrides": [
          {
            "matcher": {
              "id": "byName",
              "options": "Latência Download(ms)"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 182
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Download (Mbps)"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 136
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Evento"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 115
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Upload(Mbps)"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 112
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Perda de Pacote(%)"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 156
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Latência Upload(ms)"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 163
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Horário"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 155
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Servidor"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 471
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Latency Download(ms)"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 171
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Packet Loss(%)"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 125
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Event"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 107
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Time"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 162
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Server"
            },
            "properties": [
              {
                "id": "custom.width"
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Latency Upload(ms)"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 155
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Download (bps) {Event=\"Last Test\", Server=\"mlab1-gru02.mlab-oti.measurement-lab.org\"}"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 442
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": ""
            },
            "properties": []
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Download (bps) ndt-gig1916-c89ffeef.rnp.autojoin.measurement-lab.org"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 243
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Download (bps) ndt-gru1916-c885c077.rnp.autojoin.measurement-lab.org"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 224
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Latency Download (s) ndt-gig1916-c89ffeef.rnp.autojoin.measurement-lab.org"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 739
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Latency Download (s)"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 165
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Download (bps)"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 133
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Last Test Download (bps)"
            },
            "properties": [
              {
                "id": "unit",
                "value": "bps"
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Last Test Upload (bps)"
            },
            "properties": [
              {
                "id": "unit",
                "value": "bps"
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Last Test Latency Download (s)"
            },
            "properties": [
              {
                "id": "unit",
                "value": "s"
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Last Test Packet Loss(%)"
            },
            "properties": [
              {
                "id": "unit",
                "value": "percent"
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Upload (bps)"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 114
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Latency Upload (s)"
            },
            "properties": [
              {
                "id": "custom.width",
                "value": 146
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "Last Test Latency Upload (s)"
            },
            "properties": [
              {
                "id": "unit",
                "value": "s"
              }
            ]
          }
        ]
      },
      "gridPos": {
        "h": 7,
        "w": 14,
        "x": 10,
        "y": 0
      },
      "id": 2,
      "options": {
        "cellHeight": "sm",
        "footer": {
          "countRows": false,
          "fields": "",
          "reducer": [
            "sum"
          ],
          "show": false
        },
        "frameIndex": 0,
        "showHeader": true,
        "sortBy": []
      },
      "pluginVersion": "12.0.2",
      "targets": [
        {
          "datasource": {
            "type": "grafana-postgresql-datasource",
            "uid": "efsezsv9ajri8f"
          },
          "editorMode": "code",
          "format": 1,
          "rawQuery": true,
          "rawSql": "SELECT\n  Time,\n  \"Download (bps)\",\n  \"Latency Download (s)\",\n  \"Packet Loss(%)\",\n  \"Upload (bps)\",\n  \"Latency Upload (s)\",\n  Server\nFROM (\n  SELECT\n    test_timestamp AS Time,\n    CASE WHEN download_tp_bps >= 0 THEN download_tp_bps ELSE -1 END AS \"Download (bps)\",\n    CASE WHEN latency_download_sec >= 0 THEN latency_download_sec ELSE -1 END AS \"Latency Download (s)\",\n    CASE WHEN download_retrans_percent >= 0 THEN download_retrans_percent ELSE -1 END AS \"Packet Loss(%)\",\n    CASE WHEN upload_tp_bps >= 0 THEN upload_tp_bps ELSE -1 END AS \"Upload (bps)\",\n    CASE WHEN latency_upload_sec >= 0 THEN latency_upload_sec ELSE -1 END AS \"Latency Upload (s)\",\n    server_fqdn AS Server\n  FROM ndt_tests\n  WHERE mac_address = $mac AND download_tp_bps >= 0\n  ORDER BY test_timestamp DESC\n  LIMIT 4\n)\nORDER BY Time ASC;",
          "refId": "Last Test",
          "selectedFormat": 1,
          "sql": {
            "columns": [],
            "groupBy": [
              {
                "property": {
                  "type": "string"
                },
                "type": "groupBy"
              }
            ],
            "limit": 50
          }
        },
        {
          "datasource": {
            "type": "grafana-postgresql-datasource",
            "uid": "efsezsv9ajri8f"
          },
          "editorMode": "code",
          "format": 0,
          "hide": false,
          "rawQuery": true,
          "rawSql": "-- Proximo Teste Agendado\nSELECT\n  'Next Test' AS \"Event\",\n  scheduled_time AS \"Time\"\nFROM test_schedules\nWHERE mac_address = $mac AND scheduled_time > now()\nORDER BY scheduled_time ASC\nLIMIT 1;",
          "refId": "Next Test",
          "selectedFormat": 0,
          "sql": {
            "columns": [],
            "groupBy": [
              {
                "property": {
                  "type": "string"
                },
                "type": "groupBy"
              }
            ],
            "limit": 50
          }
        }
      ],
      "title": "Resume",
      "type": "table"
    },
    {
      "datasource": {
        "type": "grafana-postgresql-datasource",
        "uid": "efsezsv9ajri8f"
      },
      "description": "D5: 1 query com 8 subqueries (sem CTEs encadeadas). Original tinha 6+ CTEs encadeadas (TestsRealizadosHoje, TestsEsperadosHoje, ...) que nao funcionam no QuestDB. Subqueries inline com `($mac)` aplicado direto.",
"fieldConfig": {
"defaults": {
"color": {
"mode": "thresholds"
},
"fieldMinMax": false,
"mappings": [],
"thresholds": {
"mode": "absolute",
"steps": [
{
"color": "green"
}
]
},
"unit": "none"
},
"overrides": [
{
"matcher": {
"id": "byName",
"options": "top_download"
},
"properties": [
{
"id": "unit",
"value": "bps"
}
]
},
{
"matcher": {
"id": "byName",
"options": "top_upload"
},
"properties": [
{
"id": "unit",
"value": "bps"
}
]
},
{
"matcher": {
"id": "byName",
"options": "top_lat_download"
},
"properties": [
{
"id": "unit",
"value": "s"
}
]
},
{
"matcher": {
"id": "byName",
"options": "top_lat_upload"
},
"properties": [
{
"id": "unit",
"value": "s"
}
]
}
]
},
"gridPos": {
"h": 8,
"w": 24,
"x": 0,
"y": 7
},
"id": 3,
"options": {
"colorMode": "value",
"graphMode": "area",
"justifyMode": "auto",
"orientation": "auto",
"percentChangeColorMode": "standard",
"reduceOptions": {
"calcs": [
"lastNotNull"
],
"fields": "/.*/",
"values": false
},
"showPercentChange": false,
"textMode": "auto",
"wideLayout": true
},
"pluginVersion": "12.0.2",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"editorMode": "code",
"format": 1,
"rawQuery": true,
"rawSql": "SELECT\n -- Métricas do Período Selecionado no Dashboard\n selected*tests.cnt AS \"Testes no Período\",\n selected_expected.cnt AS \"Testes Previstos no Período\",\n\n -- Métricas do Dia Atual (Hoje)\n today_tests.cnt AS \"Testes Realizados Hoje\",\n expected_tests.cnt AS \"Testes Previstos Hoje\",\n\n -- Totais e Recordes Históricos\n total_tests.cnt AS \"Total Histórico de Testes\",\n top_server.name AS \"Servidor Mais Testado\",\n top_dl.mbps AS \"Maior Download (Mbps)\",\n top_ul.mbps AS \"Maior Upload (Mbps)\",\n top_latd.ms AS \"Melhor Latência Download (ms)\",\n top_latu.ms AS \"Melhor Latência Upload (ms)\"\nFROM\n -- Testes realizados no período do filtro de tempo do Grafana\n (SELECT COUNT() AS cnt \n FROM ndt_tests\n WHERE $\_\_timeFilter(test_timestamp)\n AND mac_address = $mac) selected_tests,\n\n -- Testes previstos no período do filtro de tempo do Grafana\n (SELECT COUNT() * 4 AS cnt \n FROM test*schedules\n WHERE $\_\_timeFilter(scheduled_time)\n AND mac_address = $mac) selected_expected,\n\n -- Testes realizados hoje\n (SELECT COUNT() AS cnt \n FROM ndt_tests\n WHERE date_trunc('day', test_timestamp) = date_trunc('day', now())\n AND mac_address = $mac) today_tests,\n \n -- Testes esperados hoje\n (SELECT COUNT() * 4 AS cnt \n FROM test_schedules\n WHERE date_trunc('day', scheduled_time) = date_trunc('day', now())\n AND mac_address = $mac) expected_tests,\n     \n  -- Total histórico de testes\n  (SELECT COUNT() AS cnt \n   FROM ndt_tests \n   WHERE mac_address = $mac) total_tests,\n   \n  -- Servidor mais utilizado\n  (SELECT\n      CASE \n        WHEN server_fqdn LIKE 'ndt-%' THEN CONCAT(split_part(server_fqdn, '-', 1), '-', split_part(server_fqdn, '-', 2))\n        WHEN server_fqdn IS NOT NULL THEN split_part(server_fqdn, '.', 1)\n        ELSE split_part(split_part(server_ip, '/', 1), ':', 1) \n      END AS name\n    FROM ndt_tests \n    WHERE mac_address = $mac\n    GROUP BY 1 \n    ORDER BY COUNT() DESC \n    LIMIT 1\n  ) top_server,\n  \n  -- Recorde de Download (bps -> Mbps)\n  (SELECT (download_tp_bps / 1000000.0) AS mbps\n    FROM ndt_tests \n    WHERE mac_address = $mac AND download_tp_bps >= 0\n    ORDER BY download_tp_bps DESC \n    LIMIT 1) top_dl,\n    \n  -- Recorde de Upload (bps -> Mbps)\n  (SELECT (upload_tp_bps / 1000000.0) AS mbps\n    FROM ndt_tests \n    WHERE mac_address = $mac AND upload_tp_bps >= 0\n    ORDER BY upload_tp_bps DESC \n    LIMIT 1) top_ul,\n    \n  -- Melhor Latência de Download (segundos -> ms)\n  (SELECT (latency_download_sec * 1000.0) AS ms\n    FROM ndt_tests \n    WHERE mac_address = $mac AND latency_download_sec >= 0\n    ORDER BY latency_download_sec ASC \n    LIMIT 1) top_latd,\n    \n  -- Melhor Latência de Upload (segundos -> ms)\n  (SELECT (latency_upload_sec * 1000.0) AS ms\n    FROM ndt_tests \n    WHERE mac_address = $mac AND latency_upload_sec >= 0\n    ORDER BY latency_upload_sec ASC \n    LIMIT 1) top_latu\n;",
          "refId": "A",
          "selectedFormat": 2,
          "sql": {
            "columns": [],
            "groupBy": [
              {
                "property": {
                  "type": "string"
                },
                "type": "groupBy"
              }
            ],
            "limit": 50
          }
        }
      ],
      "title": "General Statistics",
      "type": "stat"
    },
    {
      "datasource": {
        "type": "grafana-postgresql-datasource",
        "uid": "efsezsv9ajri8f"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "continuous-RdYlGr",
            "seriesBy": "min"
          },
          "custom": {
            "axisBorderShow": false,
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "barWidthFactor": 0.6,
            "drawStyle": "points",
            "fillOpacity": 0,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "insertNulls": false,
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "auto",
            "spanNulls": false,
            "stacking": {
              "group": "A",
              "mode": "none"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "decimals": 2,
          "displayName": "${**field.labels.metric}",
"fieldMinMax": false,
"links": [
{
"targetBlank": true,
"title": "Measurements",
"url": "http://grafana.land.ufrj.br/d/questdb-measurements-details/measurements-details?var-test_uuid=${**field.labels.test_uuid}"
},
{
"oneClick": false,
"targetBlank": true,
"title": "Traceroute",
"url": "http://10.246.47.170:22222/?test_uuid=${__field.labels.test_uuid}"
}
],
"mappings": [],
"max": 1000000000,
"min": 0,
"thresholds": {
"mode": "absolute",
"steps": [
{
"color": "green"
},
{
"color": "red",
"value": 80
}
]
},
"unit": "bps"
},
"overrides": []
},
"gridPos": {
"h": 12,
"w": 12,
"x": 0,
"y": 15
},
"id": 10,
"options": {
"legend": {
"calcs": [
"count"
],
"displayMode": "list",
"placement": "bottom",
"showLegend": false
},
"tooltip": {
"hideZeros": false,
"mode": "single",
"sort": "none"
}
},
"pluginVersion": "12.0.2",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"editorMode": "code",
"format": 0,
"rawQuery": true,
"rawSql": "SELECT\n test_timestamp AS \"time\",\n t.download_tp_bps AS \"Download (bps)\",\n t.test_uuid,\n CONCAT('Server: ', COALESCE(t.server_fqdn, t.server_ip), ' | ', t.server_ip) AS metric\nFROM\n ndt_tests AS t\nWHERE\n $__timeFilter(test_timestamp) AND\n  t.mac_address = $mac AND\n  position('${server:csv}', split_part(t.server_ip, '/', 1)) > 0 AND\n t.download_tp_bps >= 0\nORDER BY\n \"time\" ASC;",
"refId": "A",
"selectedFormat": 0,
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "Tp. Download",
"transformations": [
{
"id": "prepareTimeSeries",
"options": {
"format": "multi"
}
}
],
"type": "timeseries"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"fieldConfig": {
"defaults": {},
"overrides": []
},
"gridPos": {
"h": 12,
"w": 12,
"x": 12,
"y": 15
},
"id": 11,
"options": {
"allData": {},
"config": {},
"data": [],
"imgFormat": "png",
"layout": {
"font": {
"family": "Inter, Helvetica, Arial, sans-serif"
},
"margin": {
"b": 0,
"l": 0,
"r": 0,
"t": 0
},
"title": {
"automargin": true
},
"xaxis": {
"automargin": true,
"autorange": true,
"type": "date"
},
"yaxis": {
"automargin": true,
"autorange": true
}
},
"onclick": "// Event handling\n/_\n// 'data', 'variables', 'options', 'utils', and 'event' are passed as arguments\n\ntry {\n const { type: eventType, data: eventData } = event;\n const { timeZone, dayjs, locationService, getTemplateSrv } = utils;\n\n switch (eventType) {\n case 'click':\n console.log('Click event:', eventData.points);\n break;\n case 'select':\n console.log('Selection event:', eventData.range);\n break;\n case 'zoom':\n console.log('Zoom event:', eventData);\n break;\n default:\n console.log('Unhandled event type:', eventType, eventData);\n }\n\n console.log('Current time zone:', timeZone);\n console.log('From time:', dayjs(variables.**from).format());\n console.log('To time:', dayjs(variables.**to).format());\n\n // Example of using locationService\n // locationService.partial({ 'var-example': 'test' }, true);\n\n} catch (error) {\n console.error('Error in onclick handler:', error);\n}\n_/\n ",
"resScale": 2,
"script": "// Verifica se existem dados retornados pela query\nif (!data || !data.series || data.series.length === 0 || !data.series[0].fields || data.series[0].fields.length < 2) {\n return {\n data: [],\n layout: { title: 'Sem dados para o filtro selecionado' }\n };\n}\n\n// Converte os Vectors do Grafana em Arrays puros do JavaScript\nvar servers = Array.from(data.series[0].fields[0].values);\nvar rawThroughput = Array.from(data.series[0].fields[1].values);\n\n// Converte de bps para Mbps (divide por 1.000.000) pra facilitar a leitura no gráfico\nvar throughputMbps = rawThroughput.map(function(val) {\n return val !== null ? val / 1000000 : null;\n});\n\nvar trace = {\n type: 'violin',\n x: servers,\n y: throughputMbps,\n name: 'Vazão de Download',\n \n // Desenha a forma do violino nos dois lados\n side: 'both',\n \n // Oculta a caixa interna do box plot\n box: {\n visible: false\n },\n \n // Oculta a linha da média\n meanline: {\n visible: false\n },\n \n // Desativa todos os pontos (outliers/amostras)\n points: false,\n \n // Estilização do violino (Roxo para Vazão de Download)\n line: {\n color: '#8e44ad',\n width: 1.5\n },\n fillcolor: 'rgba(142, 68, 173, 0.4)' // Preenchimento roxo suave\n};\n\nvar layout = {\n title: 'Densidade da Vazão de Download por Servidor',\n xaxis: { \n title: 'Servidores',\n type: 'category',\n automargin: true\n },\n yaxis: {\n title: 'Vazão de Download (Mbps)',\n zeroline: true,\n automargin: true\n },\n margin: { t: 40, r: 20, b: 60, l: 60 }\n};\n\nreturn {\n data: [trace],\n layout: layout\n};",
"syncTimeRange": true,
"timeCol": ""
},
"pluginVersion": "1.8.1",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"editorMode": "code",
"format": 0,
"rawQuery": true,
"rawSql": "SELECT\n CASE\n WHEN server_fqdn LIKE 'ndt-%' THEN CONCAT(split_part(server_fqdn, '-', 1), '-', split_part(server_fqdn, '-', 2))\n WHEN server_fqdn IS NOT NULL THEN split_part(server_fqdn, '.', 1)\n ELSE split_part(split_part(server_ip, '/', 1), ':', 1)\n END AS \"Servidor Curto\",\n download_tp_bps AS \"Download (bps)\"\nFROM ndt_tests\nWHERE\n -- $__timeFilter(test_timestamp) AND\n  mac_address = $mac AND \n  CONCAT(split_part(split_part(server_ip, '/', 1), ':', 1), ' - ', server_fqdn) ~ '${server:regex}' AND\n download_tp_bps >= 0;",
"refId": "A",
"selectedFormat": 0,
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "Tp. Download Box Plot (All time) (Mbps)",
"type": "nline-plotlyjs-panel"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"fieldConfig": {
"defaults": {
"color": {
"mode": "continuous-GrYlRd",
"seriesBy": "min"
},
"custom": {
"axisBorderShow": false,
"axisCenteredZero": false,
"axisColorMode": "text",
"axisLabel": "",
"axisPlacement": "auto",
"barAlignment": 0,
"barWidthFactor": 0.6,
"drawStyle": "points",
"fillOpacity": 0,
"gradientMode": "none",
"hideFrom": {
"legend": false,
"tooltip": false,
"viz": false
},
"insertNulls": false,
"lineInterpolation": "linear",
"lineWidth": 1,
"pointSize": 5,
"scaleDistribution": {
"type": "linear"
},
"showPoints": "auto",
"spanNulls": false,
"stacking": {
"group": "A",
"mode": "none"
},
"thresholdsStyle": {
"mode": "off"
}
},
"decimals": 2,
"displayName": "${__field.labels.metric}",
          "links": [
            {
              "targetBlank": true,
              "title": "Measurements",
              "url": "http://grafana.land.ufrj.br/d/questdb-measurements-details/measurements-details?var-test_uuid=${**field.labels.test_uuid}"
},
{
"targetBlank": true,
"title": "Traceroute",
"url": "http://10.246.47.170:22222/?test_uuid=${**field.labels.test_uuid}"
}
],
"mappings": [],
"min": 0,
"thresholds": {
"mode": "absolute",
"steps": [
{
"color": "green"
},
{
"color": "red",
"value": 80
}
]
},
"unit": "s"
},
"overrides": []
},
"gridPos": {
"h": 12,
"w": 12,
"x": 0,
"y": 27
},
"id": 12,
"options": {
"legend": {
"calcs": [
"count"
],
"displayMode": "list",
"placement": "bottom",
"showLegend": false
},
"tooltip": {
"hideZeros": false,
"mode": "single",
"sort": "none"
}
},
"pluginVersion": "12.0.2",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"editorMode": "code",
"format": 0,
"rawQuery": true,
"rawSql": "SELECT\n test_timestamp AS \"time\",\n t.latency_download_sec AS \"Latency (s)\",\n t.test_uuid,\n CONCAT('Server: ', COALESCE(t.server_fqdn, t.server_ip), ' | ', t.server_ip) AS metric\nFROM\n ndt_tests AS t\nWHERE\n $__timeFilter(test_timestamp) AND\n  t.mac_address = $mac AND\n  position('${server:csv}', split_part(t.server_ip, '/', 1)) > 0 AND\n t.latency_download_sec >= 0\nORDER BY\n \"time\" ASC;",
"refId": "A",
"selectedFormat": 0,
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "Latency Download",
"transformations": [
{
"id": "prepareTimeSeries",
"options": {
"format": "multi"
}
}
],
"type": "timeseries"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"fieldConfig": {
"defaults": {},
"overrides": []
},
"gridPos": {
"h": 12,
"w": 12,
"x": 12,
"y": 27
},
"id": 13,
"options": {
"allData": {},
"config": {},
"data": [],
"imgFormat": "png",
"layout": {
"font": {
"family": "Inter, Helvetica, Arial, sans-serif"
},
"margin": {
"b": 0,
"l": 0,
"r": 0,
"t": 0
},
"title": {
"automargin": true
},
"xaxis": {
"automargin": true,
"autorange": true,
"type": "date"
},
"yaxis": {
"automargin": true,
"autorange": true,
"type": "second"
}
},
"onclick": "// Event handling\n/_\n// 'data', 'variables', 'options', 'utils', and 'event' are passed as arguments\n\ntry {\n const { type: eventType, data: eventData } = event;\n const { timeZone, dayjs, locationService, getTemplateSrv } = utils;\n\n switch (eventType) {\n case 'click':\n console.log('Click event:', eventData.points);\n break;\n case 'select':\n console.log('Selection event:', eventData.range);\n break;\n case 'zoom':\n console.log('Zoom event:', eventData);\n break;\n default:\n console.log('Unhandled event type:', eventType, eventData);\n }\n\n console.log('Current time zone:', timeZone);\n console.log('From time:', dayjs(variables.**from).format());\n console.log('To time:', dayjs(variables.**to).format());\n\n // Example of using locationService\n // locationService.partial({ 'var-example': 'test' }, true);\n\n} catch (error) {\n console.error('Error in onclick handler:', error);\n}\n_/\n ",
"resScale": 2,
"script": "// Verifica se existem dados retornados pela query\nif (!data || !data.series || data.series.length === 0 || !data.series[0].fields || data.series[0].fields.length < 2) {\n return {\n data: [],\n layout: { title: 'Sem dados para o filtro selecionado' }\n };\n}\n\n// Converte os Vectors do Grafana em Arrays puros do JavaScript\nvar servers = Array.from(data.series[0].fields[0].values);\nvar latencies = Array.from(data.series[0].fields[1].values);\n\nvar trace = {\n type: 'violin',\n x: servers,\n y: latencies,\n name: 'Latência de Download',\n \n // Desenha a forma do violino nos dois lados\n side: 'both',\n \n // Oculta a caixa interna do box plot\n box: {\n visible: false\n },\n \n // Oculta a linha da média\n meanline: {\n visible: false\n },\n \n // Desativa todos os pontos (outliers/amostras)\n points: false,\n \n // Estilização do violino\n line: {\n color: '#33a2e5',\n width: 1.5\n },\n fillcolor: 'rgba(51, 162, 229, 0.5)' // Cor de preenchimento do violino\n};\n\nvar layout = {\n title: 'Densidade da Latência por Servidor',\n xaxis: { \n title: 'Servidores',\n type: 'category',\n automargin: true\n },\n yaxis: {\n title: 'Latência de Download (ms)',\n zeroline: true,\n automargin: true\n },\n margin: { t: 40, r: 20, b: 60, l: 60 }\n};\n\nreturn {\n data: [trace],\n layout: layout\n};",
"syncTimeRange": true,
"timeCol": ""
},
"pluginVersion": "1.8.1",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"editorMode": "code",
"format": 0,
"rawQuery": true,
"rawSql": "SELECT\n CASE\n WHEN server_fqdn LIKE 'ndt-%' THEN CONCAT(split_part(server_fqdn, '-', 1), '-', split_part(server_fqdn, '-', 2))\n WHEN server_fqdn IS NOT NULL THEN split_part(server_fqdn, '.', 1)\n ELSE split_part(split_part(server_ip, '/', 1), ':', 1)\n END AS \"Servidor Curto\",\n latency_download_sec AS \"Latency Download (ms)\"\nFROM ndt_tests\nWHERE\n -- $__timeFilter(test_timestamp) AND\n  mac_address = $mac AND \n  CONCAT(split_part(split_part(server_ip, '/', 1), ':', 1), ' - ', server_fqdn) ~ '${server:regex}' AND\n latency_download_sec >= 0;",
"refId": "A",
"selectedFormat": 0,
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "Latency Download Box Plot (All time) (ms)",
"type": "nline-plotlyjs-panel"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"description": "",
"fieldConfig": {
"defaults": {
"color": {
"mode": "continuous-RdYlGr",
"seriesBy": "min"
},
"custom": {
"axisBorderShow": false,
"axisCenteredZero": false,
"axisColorMode": "text",
"axisLabel": "",
"axisPlacement": "auto",
"barAlignment": 0,
"barWidthFactor": 0.6,
"drawStyle": "points",
"fillOpacity": 0,
"gradientMode": "none",
"hideFrom": {
"legend": false,
"tooltip": false,
"viz": false
},
"insertNulls": false,
"lineInterpolation": "linear",
"lineWidth": 1,
"pointSize": 5,
"scaleDistribution": {
"type": "linear"
},
"showPoints": "auto",
"spanNulls": false,
"stacking": {
"group": "A",
"mode": "none"
},
"thresholdsStyle": {
"mode": "off"
}
},
"decimals": 2,
"displayName": "${__field.labels.metric}",
          "fieldMinMax": false,
          "links": [
            {
              "targetBlank": true,
              "title": "Measurements",
              "url": "http://grafana.land.ufrj.br/d/questdb-measurements-details/measurements-details?var-test_uuid=${**field.labels.test_uuid}"
},
{
"targetBlank": true,
"title": "Traceroute",
"url": "http://10.246.47.170:22222/?test_uuid=${**field.labels.test_uuid}"
}
],
"mappings": [],
"max": 1000000000,
"min": 0,
"noValue": "bruh",
"thresholds": {
"mode": "absolute",
"steps": [
{
"color": "green"
}
]
},
"unit": "bps"
},
"overrides": []
},
"gridPos": {
"h": 12,
"w": 12,
"x": 0,
"y": 39
},
"id": 16,
"options": {
"legend": {
"calcs": [
"count"
],
"displayMode": "list",
"placement": "bottom",
"showLegend": false
},
"tooltip": {
"hideZeros": false,
"mode": "single",
"sort": "none"
}
},
"pluginVersion": "12.0.2",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"editorMode": "code",
"format": 0,
"rawQuery": true,
"rawSql": "SELECT\n test_timestamp AS \"time\",\n t.upload_tp_bps AS \"Upload (bps)\",\n t.test_uuid,\n CONCAT('Server: ', COALESCE(t.server_fqdn, t.server_ip), ' | ', t.server_ip) AS metric\nFROM\n ndt_tests AS t\nWHERE\n $__timeFilter(test_timestamp) AND\n  t.mac_address = $mac AND\n  position('${server:csv}', split_part(t.server_ip, '/', 1)) > 0 AND\n t.upload_tp_bps >= 0\nORDER BY\n \"time\" ASC;",
"refId": "A",
"selectedFormat": 0,
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "Tp. Upload ",
"transformations": [
{
"id": "prepareTimeSeries",
"options": {
"format": "multi"
}
}
],
"type": "timeseries"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"fieldConfig": {
"defaults": {},
"overrides": []
},
"gridPos": {
"h": 12,
"w": 12,
"x": 12,
"y": 39
},
"id": 17,
"options": {
"allData": {},
"config": {},
"data": [],
"imgFormat": "png",
"layout": {
"font": {
"family": "Inter, Helvetica, Arial, sans-serif"
},
"margin": {
"b": 0,
"l": 0,
"r": 0,
"t": 0
},
"title": {
"automargin": true
},
"xaxis": {
"automargin": true,
"autorange": true,
"type": "date"
},
"yaxis": {
"automargin": true,
"autorange": true
}
},
"onclick": "// Event handling\n/_\n// 'data', 'variables', 'options', 'utils', and 'event' are passed as arguments\n\ntry {\n const { type: eventType, data: eventData } = event;\n const { timeZone, dayjs, locationService, getTemplateSrv } = utils;\n\n switch (eventType) {\n case 'click':\n console.log('Click event:', eventData.points);\n break;\n case 'select':\n console.log('Selection event:', eventData.range);\n break;\n case 'zoom':\n console.log('Zoom event:', eventData);\n break;\n default:\n console.log('Unhandled event type:', eventType, eventData);\n }\n\n console.log('Current time zone:', timeZone);\n console.log('From time:', dayjs(variables.**from).format());\n console.log('To time:', dayjs(variables.**to).format());\n\n // Example of using locationService\n // locationService.partial({ 'var-example': 'test' }, true);\n\n} catch (error) {\n console.error('Error in onclick handler:', error);\n}\n_/\n ",
"resScale": 2,
"script": "// Verifica se existem dados retornados pela query\nif (!data || !data.series || data.series.length === 0 || !data.series[0].fields || data.series[0].fields.length < 2) {\n return {\n data: [],\n layout: { title: 'Sem dados para o filtro selecionado' }\n };\n}\n\n// Converte os Vectors do Grafana em Arrays puros do JavaScript\nvar servers = Array.from(data.series[0].fields[0].values);\nvar rawThroughput = Array.from(data.series[0].fields[1].values);\n\n// Converte de bps para Mbps (divide por 1.000.000) pra facilitar a leitura no gráfico\nvar throughputMbps = rawThroughput.map(function(val) {\n return val !== null ? val / 1000000 : null;\n});\n\nvar trace = {\n type: 'violin',\n x: servers,\n y: throughputMbps,\n name: 'Vazão de Upload',\n \n // Desenha a forma do violino nos dois lados\n side: 'both',\n \n // Oculta a caixa interna do box plot\n box: {\n visible: false\n },\n \n // Oculta a linha da média\n meanline: {\n visible: false\n },\n \n // Desativa todos os pontos (outliers/amostras)\n points: false,\n \n // Estilização do violino (Laranja/Âmbar para Vazão de Upload)\n line: {\n color: '#e67e22',\n width: 1.5\n },\n fillcolor: 'rgba(230, 126, 34, 0.4)' // Preenchimento laranja suave\n};\n\nvar layout = {\n title: 'Densidade da Vazão de Upload por Servidor',\n xaxis: { \n title: 'Servidores',\n type: 'category',\n automargin: true\n },\n yaxis: {\n title: 'Vazão de Upload (Mbps)',\n zeroline: true,\n automargin: true\n },\n margin: { t: 40, r: 20, b: 60, l: 60 }\n};\n\nreturn {\n data: [trace],\n layout: layout\n};",
"syncTimeRange": true,
"timeCol": ""
},
"pluginVersion": "1.8.1",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"editorMode": "code",
"format": 0,
"rawQuery": true,
"rawSql": "SELECT\n CASE\n WHEN server_fqdn LIKE 'ndt-%' THEN CONCAT(split_part(server_fqdn, '-', 1), '-', split_part(server_fqdn, '-', 2))\n WHEN server_fqdn IS NOT NULL THEN split_part(server_fqdn, '.', 1)\n ELSE split_part(split_part(server_ip, '/', 1), ':', 1)\n END AS \"Servidor Curto\",\n upload_tp_bps AS \"Upload (bps)\"\nFROM ndt_tests\nWHERE\n -- $__timeFilter(test_timestamp) AND\n  mac_address = $mac AND \n  CONCAT(split_part(split_part(server_ip, '/', 1), ':', 1), ' - ', server_fqdn) ~ '${server:regex}' AND\n upload_tp_bps >= 0;",
"refId": "A",
"selectedFormat": 0,
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "Tp. Upload Box Plot (All Time) (Mbps)",
"type": "nline-plotlyjs-panel"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"description": "",
"fieldConfig": {
"defaults": {
"color": {
"mode": "continuous-GrYlRd",
"seriesBy": "min"
},
"custom": {
"axisBorderShow": false,
"axisCenteredZero": false,
"axisColorMode": "text",
"axisLabel": "",
"axisPlacement": "auto",
"barAlignment": 0,
"barWidthFactor": 0.6,
"drawStyle": "points",
"fillOpacity": 0,
"gradientMode": "none",
"hideFrom": {
"legend": false,
"tooltip": false,
"viz": false
},
"insertNulls": false,
"lineInterpolation": "linear",
"lineWidth": 1,
"pointSize": 5,
"scaleDistribution": {
"type": "linear"
},
"showPoints": "auto",
"spanNulls": false,
"stacking": {
"group": "A",
"mode": "none"
},
"thresholdsStyle": {
"mode": "off"
}
},
"decimals": 2,
"displayName": "${__field.labels.metric}",
          "fieldMinMax": false,
          "links": [
            {
              "targetBlank": true,
              "title": "Measurements",
              "url": "http://grafana.land.ufrj.br/d/questdb-measurements-details/measurements-details?var-test_uuid=${**field.labels.test_uuid}"
},
{
"targetBlank": true,
"title": "Traceroute",
"url": "http://10.246.47.170:22222/?test_uuid=${**field.labels.test_uuid}"
}
],
"mappings": [],
"min": 0,
"thresholds": {
"mode": "absolute",
"steps": [
{
"color": "green"
},
{
"color": "red",
"value": 80
}
]
},
"unit": "s"
},
"overrides": []
},
"gridPos": {
"h": 12,
"w": 12,
"x": 0,
"y": 51
},
"id": 18,
"options": {
"legend": {
"calcs": [
"count"
],
"displayMode": "list",
"placement": "bottom",
"showLegend": false
},
"tooltip": {
"hideZeros": false,
"mode": "single",
"sort": "none"
}
},
"pluginVersion": "12.0.2",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"editorMode": "code",
"format": 0,
"rawQuery": true,
"rawSql": "SELECT\n test_timestamp AS \"time\",\n t.latency_upload_sec AS \"Latency (s)\",\n t.test_uuid,\n CONCAT('Server: ', COALESCE(t.server_fqdn, t.server_ip), ' | ', t.server_ip) AS metric\nFROM\n ndt_tests AS t\nWHERE\n $__timeFilter(test_timestamp) AND\n  t.mac_address = $mac AND\n  position('${server:csv}', split_part(t.server_ip, '/', 1)) > 0 AND\n t.latency_upload_sec >= 0\nORDER BY\n \"time\" ASC;",
"refId": "A",
"selectedFormat": 0,
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "Latency Upload ",
"transformations": [
{
"id": "prepareTimeSeries",
"options": {
"format": "multi"
}
}
],
"type": "timeseries"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"fieldConfig": {
"defaults": {},
"overrides": []
},
"gridPos": {
"h": 12,
"w": 12,
"x": 12,
"y": 51
},
"id": 19,
"options": {
"allData": {},
"config": {},
"data": [],
"imgFormat": "png",
"layout": {
"font": {
"family": "Inter, Helvetica, Arial, sans-serif"
},
"margin": {
"b": 0,
"l": 0,
"r": 0,
"t": 0
},
"title": {
"automargin": true
},
"xaxis": {
"automargin": true,
"autorange": true,
"type": "date"
},
"yaxis": {
"automargin": true,
"autorange": true
}
},
"onclick": "// Event handling\n/_\n// 'data', 'variables', 'options', 'utils', and 'event' are passed as arguments\n\ntry {\n const { type: eventType, data: eventData } = event;\n const { timeZone, dayjs, locationService, getTemplateSrv } = utils;\n\n switch (eventType) {\n case 'click':\n console.log('Click event:', eventData.points);\n break;\n case 'select':\n console.log('Selection event:', eventData.range);\n break;\n case 'zoom':\n console.log('Zoom event:', eventData);\n break;\n default:\n console.log('Unhandled event type:', eventType, eventData);\n }\n\n console.log('Current time zone:', timeZone);\n console.log('From time:', dayjs(variables.**from).format());\n console.log('To time:', dayjs(variables.**to).format());\n\n // Example of using locationService\n // locationService.partial({ 'var-example': 'test' }, true);\n\n} catch (error) {\n console.error('Error in onclick handler:', error);\n}\n_/\n ",
"resScale": 2,
"script": "// Verifica se existem dados retornados pela query\nif (!data || !data.series || data.series.length === 0 || !data.series[0].fields || data.series[0].fields.length < 2) {\n return {\n data: [],\n layout: { title: 'Sem dados para o filtro selecionado' }\n };\n}\n\n// Converte os Vectors do Grafana em Arrays puros do JavaScript\nvar servers = Array.from(data.series[0].fields[0].values);\nvar latencies = Array.from(data.series[0].fields[1].values);\n\nvar trace = {\n type: 'violin',\n x: servers,\n y: latencies,\n name: 'Latência de Upload',\n \n // Desenha a forma do violino nos dois lados\n side: 'both',\n \n // Oculta a caixa interna do box plot\n box: {\n visible: false\n },\n \n // Oculta a linha da média\n meanline: {\n visible: false\n },\n \n // Desativa todos os pontos (outliers/amostras)\n points: false,\n \n // Estilização do violino (Tom esmeralda/verde para Upload)\n line: {\n color: '#2ecc71',\n width: 1.5\n },\n fillcolor: 'rgba(46, 204, 113, 0.4)' // Preenchimento verde suave\n};\n\nvar layout = {\n title: 'Densidade da Latência de Upload por Servidor',\n xaxis: { \n title: 'Servidores',\n type: 'category',\n automargin: true\n },\n yaxis: {\n title: 'Latência de Upload (s)',\n zeroline: true,\n automargin: true\n },\n margin: { t: 40, r: 20, b: 60, l: 60 }\n};\n\nreturn {\n data: [trace],\n layout: layout\n};",
"syncTimeRange": true,
"timeCol": ""
},
"pluginVersion": "1.8.1",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"editorMode": "code",
"format": 0,
"rawQuery": true,
"rawSql": "SELECT\n CASE\n WHEN server_fqdn LIKE 'ndt-%' THEN CONCAT(split_part(server_fqdn, '-', 1), '-', split_part(server_fqdn, '-', 2))\n WHEN server_fqdn IS NOT NULL THEN split_part(server_fqdn, '.', 1)\n ELSE split_part(split_part(server_ip, '/', 1), ':', 1)\n END AS \"Servidor Curto\",\n latency_upload_sec AS \"Latency Upload (s)\"\nFROM ndt_tests\nWHERE\n -- $__timeFilter(test_timestamp) AND\n  mac_address = $mac AND \n  CONCAT(split_part(split_part(server_ip, '/', 1), ':', 1), ' - ', server_fqdn) ~ '${server:regex}' AND\n latency_upload_sec >= 0;",
"refId": "A",
"selectedFormat": 0,
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "Latency Upload Box Plot (All time) (s)",
"type": "nline-plotlyjs-panel"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"fieldConfig": {
"defaults": {
"color": {
"mode": "continuous-GrYlRd",
"seriesBy": "min"
},
"custom": {
"axisBorderShow": false,
"axisCenteredZero": false,
"axisColorMode": "text",
"axisLabel": "",
"axisPlacement": "auto",
"barAlignment": 0,
"barWidthFactor": 0.6,
"drawStyle": "points",
"fillOpacity": 0,
"gradientMode": "none",
"hideFrom": {
"legend": false,
"tooltip": false,
"viz": false
},
"insertNulls": false,
"lineInterpolation": "linear",
"lineWidth": 1,
"pointSize": 5,
"scaleDistribution": {
"type": "linear"
},
"showPoints": "auto",
"spanNulls": false,
"stacking": {
"group": "A",
"mode": "none"
},
"thresholdsStyle": {
"mode": "off"
}
},
"decimals": 2,
"displayName": "${__field.labels.metric}",
          "links": [
            {
              "targetBlank": true,
              "title": "Measurements",
              "url": "http://grafana.land.ufrj.br/d/questdb-measurements-details/measurements-details?var-test_uuid=${**field.labels[test_uuid]}"
},
{
"targetBlank": true,
"title": "Traceroute",
"url": "http://10.246.47.170:22222/?test_uuid=${**field.labels.test_uuid}"
}
],
"mappings": [],
"min": 0,
"thresholds": {
"mode": "absolute",
"steps": [
{
"color": "green"
},
{
"color": "red",
"value": 80
}
]
},
"unit": "percent"
},
"overrides": []
},
"gridPos": {
"h": 12,
"w": 12,
"x": 0,
"y": 63
},
"id": 14,
"options": {
"legend": {
"calcs": [
"count"
],
"displayMode": "list",
"placement": "bottom",
"showLegend": false
},
"tooltip": {
"hideZeros": false,
"mode": "single",
"sort": "none"
}
},
"pluginVersion": "12.0.2",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"editorMode": "code",
"format": 0,
"rawQuery": true,
"rawSql": "SELECT\n test_timestamp AS \"time\",\n t.download_retrans_percent AS \"Retrans (%)\",\n t.test_uuid,\n CONCAT('Server: ', COALESCE(t.server_fqdn, t.server_ip), ' | ', t.server_ip) AS metric\nFROM\n ndt_tests AS t\nWHERE\n $__timeFilter(test_timestamp) AND\n  t.mac_address = $mac AND\n  position('${server:csv}', split_part(t.server_ip, '/', 1)) > 0 AND\n t.download_retrans_percent >= 0\nORDER BY\n \"time\" ASC;",
"refId": "A",
"selectedFormat": 0,
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "Packet Loss",
"transformations": [
{
"id": "prepareTimeSeries",
"options": {
"format": "multi"
}
}
],
"type": "timeseries"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"fieldConfig": {
"defaults": {},
"overrides": []
},
"gridPos": {
"h": 12,
"w": 12,
"x": 12,
"y": 63
},
"id": 15,
"options": {
"allData": {},
"config": {},
"data": [],
"imgFormat": "png",
"layout": {
"font": {
"family": "Inter, Helvetica, Arial, sans-serif"
},
"margin": {
"b": 0,
"l": 0,
"r": 0,
"t": 0
},
"title": {
"automargin": true
},
"xaxis": {
"automargin": true,
"autorange": true,
"type": "date"
},
"yaxis": {
"automargin": true,
"autorange": true
}
},
"onclick": "// Event handling\n/_\n// 'data', 'variables', 'options', 'utils', and 'event' are passed as arguments\n\ntry {\n const { type: eventType, data: eventData } = event;\n const { timeZone, dayjs, locationService, getTemplateSrv } = utils;\n\n switch (eventType) {\n case 'click':\n console.log('Click event:', eventData.points);\n break;\n case 'select':\n console.log('Selection event:', eventData.range);\n break;\n case 'zoom':\n console.log('Zoom event:', eventData);\n break;\n default:\n console.log('Unhandled event type:', eventType, eventData);\n }\n\n console.log('Current time zone:', timeZone);\n console.log('From time:', dayjs(variables.**from).format());\n console.log('To time:', dayjs(variables.**to).format());\n\n // Example of using locationService\n // locationService.partial({ 'var-example': 'test' }, true);\n\n} catch (error) {\n console.error('Error in onclick handler:', error);\n}\n_/\n ",
"resScale": 2,
"script": "// Verifica se existem dados retornados pela query\nif (!data || !data.series || data.series.length === 0 || !data.series[0].fields || data.series[0].fields.length < 2) {\n return {\n data: [],\n layout: { title: 'Sem dados para o filtro selecionado' }\n };\n}\n\n// Converte os Vectors do Grafana em Arrays puros do JavaScript\nvar servers = Array.from(data.series[0].fields[0].values);\nvar retransPercent = Array.from(data.series[0].fields[1].values);\n\nvar trace = {\n type: 'violin',\n x: servers,\n y: retransPercent,\n name: 'Retransmissão (%)',\n \n // Desenha a forma do violino nos dois lados\n side: 'both',\n \n // Oculta a caixa interna do box plot\n box: {\n visible: false\n },\n \n // Oculta a linha da média\n meanline: {\n visible: false\n },\n \n // Desativa todos os pontos (outliers/amostras)\n points: false,\n \n // Estilização do violino (Vermelho para Retransmissão / Perda)\n line: {\n color: '#e74c3c',\n width: 1.5\n },\n fillcolor: 'rgba(231, 76, 60, 0.4)' // Preenchimento vermelho suave\n};\n\nvar layout = {\n title: 'Densidade de Retransmissão por Servidor',\n xaxis: { \n title: 'Servidores',\n type: 'category',\n automargin: true\n },\n yaxis: {\n title: 'Retransmissão / Perda (%)',\n zeroline: true,\n automargin: true\n },\n margin: { t: 40, r: 20, b: 60, l: 60 }\n};\n\nreturn {\n data: [trace],\n layout: layout\n};",
"syncTimeRange": true,
"timeCol": ""
},
"pluginVersion": "1.8.1",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"editorMode": "code",
"format": 0,
"rawQuery": true,
"rawSql": "SELECT\n CASE\n WHEN server_fqdn LIKE 'ndt-%' THEN CONCAT(split_part(server_fqdn, '-', 1), '-', split_part(server_fqdn, '-', 2))\n WHEN server_fqdn IS NOT NULL THEN split_part(server_fqdn, '.', 1)\n ELSE split_part(split_part(server_ip, '/', 1), ':', 1)\n END AS \"Servidor Curto\",\n download_retrans_percent AS \"Perda de Pacote (%)\"\nFROM ndt_tests\nWHERE\n -- $__timeFilter(test_timestamp) AND\n  mac_address = $mac AND \n  CONCAT(split_part(split_part(server_ip, '/', 1), ':', 1), ' - ', server_fqdn) ~ '${server:regex}' AND\n download_retrans_percent >= 0;",
"refId": "A",
"selectedFormat": 0,
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "Packet Loss Box Plot (All time) (%)",
"type": "nline-plotlyjs-panel"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"fieldConfig": {
"defaults": {
"color": {
"mode": "fixed"
},
"custom": {
"axisBorderShow": false,
"axisCenteredZero": false,
"axisColorMode": "text",
"axisLabel": "",
"axisPlacement": "auto",
"fillOpacity": 80,
"gradientMode": "opacity",
"hideFrom": {
"legend": false,
"tooltip": false,
"viz": false
},
"lineWidth": 1,
"scaleDistribution": {
"type": "linear"
},
"thresholdsStyle": {
"mode": "off"
}
},
"mappings": [],
"thresholds": {
"mode": "absolute",
"steps": [
{
"color": "green"
}
]
}
},
"overrides": [
{
"matcher": {
"id": "byName",
"options": "Download (bps)"
},
"properties": [
{
"id": "color",
"value": {
"fixedColor": "semi-dark-red",
"mode": "fixed"
}
},
{
"id": "unit",
"value": "bps"
},
{
"id": "fieldMinMax",
"value": true
}
]
},
{
"matcher": {
"id": "byName",
"options": "Upload (bps)"
},
"properties": [
{
"id": "color",
"value": {
"fixedColor": "light-red",
"mode": "fixed"
}
},
{
"id": "unit",
"value": "bps"
},
{
"id": "fieldMinMax",
"value": true
}
]
},
{
"matcher": {
"id": "byName",
"options": "\"Lat. Down (s)\""
},
"properties": [
{
"id": "color",
"value": {
"fixedColor": "semi-dark-orange",
"mode": "fixed"
}
},
{
"id": "unit",
"value": "s"
},
{
"id": "fieldMinMax",
"value": true
}
]
},
{
"matcher": {
"id": "byName",
"options": "\"Lat. Up (s)\""
},
"properties": [
{
"id": "color",
"value": {
"fixedColor": "light-orange",
"mode": "fixed"
}
},
{
"id": "unit",
"value": "s"
},
{
"id": "fieldMinMax",
"value": true
}
]
},
{
"matcher": {
"id": "byName",
"options": "\"Retrans. (%)\""
},
"properties": [
{
"id": "unit",
"value": "percent"
},
{
"id": "color",
"value": {
"fixedColor": "green",
"mode": "fixed"
}
},
{
"id": "fieldMinMax",
"value": true
}
]
},
{
"matcher": {
"id": "byName",
"options": "Testes"
},
"properties": [
{
"id": "color",
"value": {
"fixedColor": "blue",
"mode": "fixed"
}
}
]
}
]
},
"gridPos": {
"h": 11,
"w": 24,
"x": 0,
"y": 75
},
"id": 4,
"options": {
"barRadius": 0,
"barWidth": 0.97,
"fullHighlight": false,
"groupWidth": 0.7,
"legend": {
"calcs": [],
"displayMode": "list",
"placement": "bottom",
"showLegend": true
},
"orientation": "auto",
"showValue": "auto",
"stacking": "none",
"tooltip": {
"hideZeros": false,
"mode": "single",
"sort": "none"
},
"xTickLabelRotation": 0,
"xTickLabelSpacing": 0
},
"pluginVersion": "12.0.2",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"editorMode": "code",
"format": 1,
"rawQuery": true,
"rawSql": "SELECT\n CASE\n WHEN server_fqdn LIKE 'ndt-%'\n THEN CONCAT(split_part(server_fqdn, '-', 1), '-', split_part(server_fqdn, '-', 2))\n ELSE split_part(COALESCE(server_fqdn, server_ip), '.', 1)\n END AS \"Servidor\",\n COUNT(*) AS \"Testes\",\n approx*median(download_tp_bps, 3) AS \"Download (bps)\",\n approx_median(upload_tp_bps, 3) AS \"Upload (bps)\",\n approx_median(latency_download_sec, 3) AS \"Lat. Down (s)\",\n approx_median(latency_upload_sec, 3) AS \"Lat. Up (s)\",\n approx_median(download_retrans_percent, 3) AS \"Retrans. (%)\"\nFROM ndt_tests\nWHERE\n mac_address = $mac AND\n  download_tp_bps >= 0 AND download_tp_bps < 1e9 AND\n  upload_tp_bps >= 0 AND upload_tp_bps < 1e9 AND\n  latency_download_sec >= 0 AND latency_upload_sec >= 0 AND\n  download_retrans_percent >= 0 AND\n  position('${server:csv}', split_part(server_ip, '/', 1)) > 0\nGROUP BY \"Servidor\"\nORDER BY \"Testes\" DESC;",
"refId": "A",
"selectedFormat": 1,
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "Median Between Servers",
"type": "barchart"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "questdb-routers-datasource"
},
"description": "Pivot 5 RTTs em 5 series. Adaptado de unnest(ARRAY[...]) que nao funciona no QuestDB.",
"fieldConfig": {
"defaults": {
"color": {
"mode": "palette-classic"
},
"custom": {
"axisBorderShow": false,
"axisCenteredZero": false,
"axisColorMode": "text",
"axisLabel": "",
"axisPlacement": "auto",
"barAlignment": 0,
"barWidthFactor": 0.6,
"drawStyle": "line",
"fillOpacity": 0,
"gradientMode": "none",
"hideFrom": {
"legend": false,
"tooltip": false,
"viz": false
},
"insertNulls": false,
"lineInterpolation": "linear",
"lineWidth": 1,
"pointSize": 5,
"scaleDistribution": {
"type": "linear"
},
"showPoints": "auto",
"spanNulls": false,
"stacking": {
"group": "A",
"mode": "none"
},
"thresholdsStyle": {
"mode": "off"
}
},
"decimals": 2,
"mappings": [],
"thresholds": {
"mode": "absolute",
"steps": [
{
"color": "green"
},
{
"color": "red",
"value": 80
}
]
},
"unit": "µs"
},
"overrides": [
{
"matcher": {
"id": "byName",
"options": "value 45.236.48.43/32"
},
"properties": [
{
"id": "color",
"value": {
"fixedColor": "dark-red",
"mode": "fixed"
}
}
]
},
{
"matcher": {
"id": "byName",
"options": "value 200.137.76.137/32"
},
"properties": [
{
"id": "color",
"value": {
"fixedColor": "text",
"mode": "fixed"
}
}
]
},
{
"matcher": {
"id": "byName",
"options": "value 8.8.8.8/32"
},
"properties": [
{
"id": "color",
"value": {
"fixedColor": "#00d7ff",
"mode": "fixed"
}
}
]
}
]
},
"gridPos": {
"h": 8,
"w": 24,
"x": 0,
"y": 86
},
"id": 9,
"interval": "1m",
"options": {
"legend": {
"calcs": [
"median"
],
"displayMode": "list",
"placement": "bottom",
"showLegend": true
},
"tooltip": {
"hideZeros": false,
"mode": "single",
"sort": "none"
}
},
"pluginVersion": "12.0.2",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "questdb-routers-datasource"
},
"editorMode": "code",
"format": 0,
"rawQuery": true,
"rawSql": "SELECT\n timestamp AS \"time\",\n destination AS metric,\n approx_median((COALESCE(rtt1_us,0) + COALESCE(rtt2_us,0) + COALESCE(rtt3_us,0) + COALESCE(rtt4_us,0) + COALESCE(rtt5_us,0)) / 5.0, 2) AS value\nFROM ping_metrics\nWHERE $**timeFilter(timestamp)\nSAMPLE BY 1m ALIGN TO CALENDAR;",
"refId": "A",
"selectedFormat": 0,
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "Ping Variation",
"transformations": [
{
"id": "prepareTimeSeries",
"options": {
"format": "multi"
}
}
],
"type": "timeseries"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"fieldConfig": {
"defaults": {
"color": {
"fixedColor": "blue",
"mode": "continuous-RdYlGr"
},
"custom": {
"axisBorderShow": false,
"axisCenteredZero": false,
"axisColorMode": "text",
"axisLabel": "",
"axisPlacement": "auto",
"fillOpacity": 80,
"gradientMode": "scheme",
"hideFrom": {
"legend": false,
"tooltip": false,
"viz": false
},
"lineWidth": 0,
"scaleDistribution": {
"type": "linear"
},
"thresholdsStyle": {
"mode": "off"
}
},
"mappings": [],
"thresholds": {
"mode": "absolute",
"steps": [
{
"color": "green"
}
]
}
},
"overrides": [
{
"**systemRef": "hideSeriesFrom",
"matcher": {
"id": "byNames",
"options": {
"mode": "exclude",
"names": [
"Total de Testes"
],
"prefix": "All except:",
"readOnly": true
}
},
"properties": [
{
"id": "custom.hideFrom",
"value": {
"legend": false,
"tooltip": false,
"viz": true
}
}
]
}
]
},
"gridPos": {
"h": 8,
"w": 12,
"x": 0,
"y": 94
},
"id": 5,
"options": {
"barRadius": 0.15,
"barWidth": 0.9,
"colorByField": "Total de Testes",
"fullHighlight": false,
"groupWidth": 0.7,
"legend": {
"calcs": [
"sum"
],
"displayMode": "list",
"placement": "bottom",
"showLegend": true
},
"orientation": "auto",
"showValue": "auto",
"stacking": "none",
"tooltip": {
"hideZeros": false,
"mode": "single",
"sort": "none"
},
"xField": "Servidor Curto",
"xTickLabelRotation": 0,
"xTickLabelSpacing": 0
},
"pluginVersion": "12.0.2",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"editorMode": "code",
"format": 1,
"rawQuery": true,
"rawSql": "SELECT\n CASE\n WHEN t.server_fqdn LIKE 'ndt-%'\n THEN CONCAT(split_part(t.server_fqdn, '-', 1), '-', split_part(t.server_fqdn, '-', 2))\n ELSE split_part(COALESCE(t.server_fqdn, t.server_ip), '.', 1)\n END AS \"Servidor Curto\",\n COUNT(\*) AS \"Total de Testes\"\nFROM ndt_tests AS t\nWHERE $**timeFilter(test_timestamp) AND mac_address = $mac\nGROUP BY \"Servidor Curto\"\nORDER BY \"Total de Testes\" DESC;",
"refId": "A",
"selectedFormat": 1,
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "Tests by Servers",
"type": "barchart"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"fieldConfig": {
"defaults": {
"color": {
"mode": "palette-classic"
},
"custom": {
"axisBorderShow": false,
"axisCenteredZero": false,
"axisColorMode": "text",
"axisLabel": "",
"axisPlacement": "auto",
"barAlignment": 0,
"barWidthFactor": 0.6,
"drawStyle": "line",
"fillOpacity": 0,
"gradientMode": "none",
"hideFrom": {
"legend": false,
"tooltip": false,
"viz": false
},
"insertNulls": false,
"lineInterpolation": "linear",
"lineWidth": 0.1,
"pointSize": 8,
"scaleDistribution": {
"type": "linear"
},
"showPoints": "auto",
"spanNulls": false,
"stacking": {
"group": "A",
"mode": "none"
},
"thresholdsStyle": {
"mode": "off"
}
},
"mappings": [],
"max": 1,
"thresholds": {
"mode": "absolute",
"steps": [
{
"color": "green"
},
{
"color": "red",
"value": 80
}
]
}
},
"overrides": [
{
"matcher": {
"id": "byName",
"options": "Agendado"
},
"properties": [
{
"id": "custom.drawStyle",
"value": "bars"
},
{
"id": "custom.barWidthFactor",
"value": 0.1
},
{
"id": "color",
"value": {
"fixedColor": "orange",
"mode": "fixed"
}
}
]
},
{
"matcher": {
"id": "byName",
"options": "Realizado"
},
"properties": [
{
"id": "custom.drawStyle",
"value": "points"
},
{
"id": "color",
"value": {
"fixedColor": "green",
"mode": "fixed"
}
}
]
}
]
},
"gridPos": {
"h": 8,
"w": 12,
"x": 12,
"y": 94
},
"id": 7,
"options": {
"legend": {
"calcs": [],
"displayMode": "list",
"placement": "bottom",
"showLegend": true
},
"tooltip": {
"hideZeros": false,
"mode": "single",
"sort": "none"
}
},
"pluginVersion": "12.0.2",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"editorMode": "code",
"format": 0,
"rawQuery": true,
"rawSql": "SELECT\n scheduled_time AS \"time\",\n 1 AS \"Agendado\"\nFROM test_schedules\nWHERE\n $**timeFilter(scheduled_time) AND mac_address = $mac;",
"refId": "Agendado",
"selectedFormat": 0,
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"editorMode": "code",
"format": 0,
"hide": false,
"rawQuery": true,
"rawSql": "SELECT\n test_timestamp AS \"time\",\n 1 AS \"Realizado\"\nFROM ndt_tests\nWHERE\n $**timeFilter(test_timestamp) AND mac_address = $mac;",
"refId": "Realizado",
"selectedFormat": 0,
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "Tests Schedules",
"type": "timeseries"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"fieldConfig": {
"defaults": {
"color": {
"mode": "palette-classic"
},
"custom": {
"axisBorderShow": false,
"axisCenteredZero": false,
"axisColorMode": "text",
"axisLabel": "",
"axisPlacement": "auto",
"barAlignment": 0,
"barWidthFactor": 0.6,
"drawStyle": "line",
"fillOpacity": 0,
"gradientMode": "none",
"hideFrom": {
"legend": false,
"tooltip": false,
"viz": false
},
"insertNulls": false,
"lineInterpolation": "linear",
"lineStyle": {
"fill": "solid"
},
"lineWidth": 4,
"pointSize": 5,
"scaleDistribution": {
"type": "linear"
},
"showPoints": "auto",
"spanNulls": false,
"stacking": {
"group": "A",
"mode": "none"
},
"thresholdsStyle": {
"mode": "off"
}
},
"mappings": [],
"thresholds": {
"mode": "absolute",
"steps": [
{
"color": "green"
}
]
}
},
"overrides": []
},
"gridPos": {
"h": 8,
"w": 12,
"x": 0,
"y": 102
},
"id": 8,
"options": {
"legend": {
"calcs": [],
"displayMode": "list",
"placement": "bottom",
"showLegend": true
},
"tooltip": {
"hideZeros": false,
"mode": "single",
"sort": "none"
}
},
"pluginVersion": "12.0.2",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"editorMode": "code",
"format": 0,
"rawQuery": true,
"rawSql": "SELECT\n test_timestamp AS \"time\",\n 1 AS value,\n client_ip AS metric\nFROM\n ndt_tests\nWHERE\n $**timeFilter(test_timestamp) AND\n mac_address = $mac\nORDER BY\n test_timestamp ASC;",
"refId": "A",
"selectedFormat": 0,
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "IP Variation",
"transformations": [
{
"disabled": true,
"id": "prepareTimeSeries",
"options": {
"format": "multi"
}
}
],
"type": "timeseries"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"description": "Self-join no lugar de LAG OVER PARTITION BY (que nao funciona no QuestDB). Para cada teste (a), busca o teste anterior (b) mais recente mesmo mac, mesmo dia.",
"fieldConfig": {
"defaults": {
"color": {
"mode": "palette-classic"
},
"custom": {
"fillOpacity": 47,
"gradientMode": "hue",
"hideFrom": {
"legend": false,
"tooltip": false,
"viz": false
},
"lineWidth": 3,
"stacking": {
"group": "A",
"mode": "none"
}
},
"decimals": 0,
"fieldMinMax": false,
"mappings": [],
"thresholds": {
"mode": "absolute",
"steps": [
{
"color": "green"
},
{
"color": "red",
"value": 80
}
]
}
},
"overrides": [
{
"matcher": {
"id": "byName",
"options": "Intervalo (Minutos)"
},
"properties": [
{
"id": "color",
"value": {
"fixedColor": "light-blue",
"mode": "fixed"
}
}
]
},
{
"**systemRef": "hideSeriesFrom",
"matcher": {
"id": "byNames",
"options": {
"mode": "exclude",
"names": [
"Intervalo (Minutos)"
],
"prefix": "All except:",
"readOnly": true
}
},
"properties": [
{
"id": "custom.hideFrom",
"value": {
"legend": false,
"tooltip": false,
"viz": true
}
}
]
}
]
},
"gridPos": {
"h": 8,
"w": 12,
"x": 12,
"y": 102
},
"id": 6,
"options": {
"combine": false,
"legend": {
"calcs": [
"mean"
],
"displayMode": "list",
"placement": "bottom",
"showLegend": true
},
"tooltip": {
"hideZeros": false,
"mode": "single",
"sort": "none"
}
},
"pluginVersion": "12.0.2",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"editorMode": "code",
"format": 1,
"rawQuery": true,
"rawSql": "WITH intervals AS (\n SELECT\n scheduled_time,\n LAG(scheduled_time, 1) OVER (\n PARTITION BY mac_address, date_trunc('day', scheduled_time)\n ORDER BY scheduled_time ASC\n ) AS prev\n FROM test_schedules\n WHERE\n $**timeFilter(scheduled_time) AND\n mac_address = $mac\n)\nSELECT (scheduled_time - prev) / 60000000 AS \"Intervalo (Minutos)\"\nFROM intervals\nWHERE prev IS NOT NULL;",
"refId": "A",
"selectedFormat": 1,
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "Exponential Distribution Between Tests",
"type": "histogram"
}
],
"preload": false,
"refresh": "auto",
"schemaVersion": 41,
"tags": [],
"templating": {
"list": [
{
"allowCustomValue": false,
"current": {
"text": [
"dc:a6:32:6b:9c:a8 - Edworld"
],
"value": [
"dc:a6:32:6b:9c:a8"
]
},
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"definition": "WITH test_counts AS (\n SELECT mac_address, COUNT() AS total_tests\n FROM ndt_tests\n GROUP BY mac_address\n)\nSELECT\n t.mac_address AS **value,\n CONCAT(\n t.mac_address,\n ' - ',\n COALESCE(d.owner, 'Sem Dono')\n ) AS **text,\n t.total_tests\nFROM test_counts t\nLEFT JOIN devices d ON d.mac = t.mac_address\nORDER BY t.total_tests DESC",
"includeAll": false,
"label": "mac_address",
"multi": true,
"name": "mac",
"options": [],
"query": "WITH test_counts AS (\n SELECT mac_address, COUNT() AS total_tests\n FROM ndt_tests\n GROUP BY mac_address\n)\nSELECT\n t.mac_address AS **value,\n CONCAT(\n t.mac_address,\n ' - ',\n COALESCE(d.owner, 'Sem Dono')\n ) AS **text,\n t.total_tests\nFROM test_counts t\nLEFT JOIN devices d ON d.mac = t.mac_address\nORDER BY t.total_tests DESC",
"refresh": 1,
"regex": "",
"type": "query"
},
{
"allowCustomValue": false,
"current": {
"text": [
"200.159.254.239 - ndt-gig1916-c89ffeef.rnp.autojoin.measurement-lab.org",
"200.137.76.137 - ndt-vix1916-c8894c89.rnp.autojoin.measurement-lab.org",
"200.133.192.119 - ndt-gru1916-c885c077.rnp.autojoin.measurement-lab.org",
"45.236.48.43 - ndt-ppy268205-2dec302b.redebrasil.autojoin.measurement-lab.org",
"200.131.2.169 - ndt-cnf1916-c88302a9.rnp.autojoin.measurement-lab.org"
],
"value": [
"200.159.254.239 - ndt-gig1916-c89ffeef.rnp.autojoin.measurement-lab.org",
"200.137.76.137 - ndt-vix1916-c8894c89.rnp.autojoin.measurement-lab.org",
"200.133.192.119 - ndt-gru1916-c885c077.rnp.autojoin.measurement-lab.org",
"45.236.48.43 - ndt-ppy268205-2dec302b.redebrasil.autojoin.measurement-lab.org",
"200.131.2.169 - ndt-cnf1916-c88302a9.rnp.autojoin.measurement-lab.org"
]
},
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"definition": "WITH base AS (\n SELECT\n split_part(server_ip, '/', 1) AS ip,\n MAX(server_fqdn) AS fqdn,\n COUNT() AS n\n FROM ndt_tests\n WHERE server_ip IS NOT NULL\n GROUP BY split_part(server_ip, '/', 1)\n)\nSELECT\n CONCAT(COALESCE(ip, fqdn), ' - ', fqdn) AS server_display\nFROM base\nORDER BY n DESC;",
"includeAll": false,
"label": "server_ip",
"multi": true,
"name": "server",
"options": [],
"query": "WITH base AS (\n SELECT\n split_part(server_ip, '/', 1) AS ip,\n MAX(server_fqdn) AS fqdn,\n COUNT() AS n\n FROM ndt_tests\n WHERE server_ip IS NOT NULL\n GROUP BY split_part(server_ip, '/', 1)\n)\nSELECT\n CONCAT(COALESCE(ip, fqdn), ' - ', fqdn) AS server_display\nFROM base\nORDER BY n DESC;",
"refresh": 1,
"regex": "",
"type": "query"
}
]
},
"time": {
"from": "now/d",
"to": "now/d"
},
"timepicker": {},
"timezone": "utc",
"title": "Individual",
"uid": "questdb-individual",
"version": 18
}

### Mesurament Details

{
"annotations": {
"list": [
{
"builtIn": 1,
"datasource": {
"type": "grafana",
"uid": "-- Grafana --"
},
"enable": true,
"hide": true,
"iconColor": "rgba(0, 211, 255, 1)",
"name": "Annotations & Alerts",
"type": "dashboard"
}
]
},
"editable": true,
"fiscalYearStartMonth": 0,
"graphTooltip": 0,
"id": 175,
"links": [],
"panels": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"fieldConfig": {
"defaults": {
"color": {
"mode": "thresholds"
},
"custom": {
"align": "center",
"cellOptions": {
"type": "auto",
"wrapText": true
},
"filterable": false,
"inspect": false
},
"mappings": [],
"thresholds": {
"mode": "absolute",
"steps": [
{
"color": "green"
},
{
"color": "red",
"value": 80
}
]
}
},
"overrides": []
},
"gridPos": {
"h": 6,
"w": 24,
"x": 0,
"y": 0
},
"id": 1,
"options": {
"cellHeight": "md",
"footer": {
"countRows": false,
"fields": "",
"reducer": [
"sum"
],
"show": false
},
"showHeader": true,
"sortBy": []
},
"pluginVersion": "12.0.2",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"editorMode": "code",
"format": 1,
"rawQuery": true,
"rawSql": "SELECT\n test*timestamp AS \"Hora do Teste\",\n t.mac_address AS \"MAC do Dispositivo\",\n d.owner AS \"Proprietário\",\n t.client_ip AS \"IP do Cliente\",\n (t.download_tp_bps / 1000000.0) AS \"Download (Mbps)\",\n (t.upload_tp_bps / 1000000.0) AS \"Upload (Mbps)\",\n (t.latency_download_sec * 1000.0) AS \"Latência Download (ms)\",\n (t.latency*upload_sec * 1000.0) AS \"Latência Upload (ms)\",\n t.download_retrans_percent AS \"Perda de Pacote (%)\",\n CASE\n WHEN t.server_fqdn LIKE 'ndt-%' THEN CONCAT(split_part(t.server_fqdn, '-', 1), '-', split_part(t.server_fqdn, '-', 2))\n WHEN t.server_fqdn IS NOT NULL THEN split_part(t.server_fqdn, '.', 1)\n ELSE split_part(split_part(t.server_ip, '/', 1), ':', 1)\n END AS \"Servidor\",\n t.server_ip AS \"IP Servidor\",\n t.test_uuid AS \"UUID\"\nFROM ndt_tests AS t\nLEFT JOIN devices AS d ON d.mac = t.mac_address\nWHERE\n t.test_uuid = '$test_uuid'\nORDER BY test_timestamp DESC;",
          "refId": "A",
          "selectedFormat": 1,
          "sql": {
            "columns": [
              {
                "parameters": [],
                "type": "function"
              }
            ],
            "groupBy": [
              {
                "property": {
                  "type": "string"
                },
                "type": "groupBy"
              }
            ],
            "limit": 50
          }
        }
      ],
      "title": "Resumo",
      "type": "table"
    },
    {
      "datasource": {
        "type": "grafana-postgresql-datasource",
        "uid": "efsezsv9ajri8f"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "thresholds"
          },
          "custom": {
            "align": "auto",
            "cellOptions": {
              "type": "auto"
            },
            "inspect": false
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green"
              },
              {
                "color": "red",
                "value": 80
              }
            ]
          }
        },
        "overrides": []
      },
      "gridPos": {
        "h": 11,
        "w": 24,
        "x": 0,
        "y": 6
      },
      "id": 2,
      "options": {
        "cellHeight": "sm",
        "footer": {
          "countRows": false,
          "fields": "",
          "reducer": [
            "sum"
          ],
          "show": false
        },
        "showHeader": true
      },
      "pluginVersion": "12.0.2",
      "targets": [
        {
          "datasource": {
            "type": "grafana-postgresql-datasource",
            "uid": "efsezsv9ajri8f"
          },
          "editorMode": "code",
          "format": 1,
          "rawQuery": true,
          "rawSql": "SELECT *\nFROM ndt_measurements\nWHERE\n  test_uuid = '$test_uuid' AND\n $\_\_timeFilter(measurement_time)\nORDER BY measurement_time ASC, origin ASC;",
"refId": "A",
"selectedFormat": 1,
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "Measurements",
"type": "table"
}
],
"preload": false,
"schemaVersion": 41,
"tags": [],
"templating": {
"list": [
{
"current": {
"text": "c89aeb98578d_1764700171_0000000000103C39",
"value": "c89aeb98578d_1764700171_0000000000103C39"
},
"hide": 2,
"name": "test_uuid",
"options": [
{
"selected": true,
"text": "c89aeb98578d_1764700171_0000000000103C39",
"value": "c89aeb98578d_1764700171_0000000000103C39"
}
],
"query": "c89aeb98578d_1764700171_0000000000103C39",
"type": "textbox"
}
]
},
"time": {
"from": "now-14d",
"to": "now"
},
"timepicker": {},
"timezone": "browser",
"title": "Measurements Details",
"uid": "questdb-measurements-details",
"version": 3
}

### Monitoramento e logs

{
"annotations": {
"list": [
{
"builtIn": 1,
"datasource": {
"type": "grafana",
"uid": "-- Grafana --"
},
"enable": true,
"hide": true,
"iconColor": "rgba(0, 211, 255, 1)",
"name": "Annotations & Alerts",
"type": "dashboard"
}
]
},
"editable": true,
"fiscalYearStartMonth": 0,
"graphTooltip": 0,
"id": 176,
"links": [],
"panels": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"fieldConfig": {
"defaults": {
"color": {
"mode": "thresholds"
},
"mappings": [],
"thresholds": {
"mode": "absolute",
"steps": [
{
"color": "green"
},
{
"color": "red",
"value": 80
}
]
}
},
"overrides": []
},
"gridPos": {
"h": 8,
"w": 12,
"x": 0,
"y": 0
},
"id": 1,
"options": {
"colorMode": "value",
"graphMode": "area",
"justifyMode": "auto",
"orientation": "auto",
"percentChangeColorMode": "standard",
"reduceOptions": {
"calcs": [
"lastNotNull"
],
"fields": "",
"values": false
},
"showPercentChange": false,
"textMode": "auto",
"wideLayout": true
},
"pluginVersion": "12.0.2",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"editorMode": "code",
"format": 0,
"rawQuery": true,
"rawSql": "SELECT COUNT(DISTINCT mac) \r\nFROM devices \r\nWHERE last_ping > dateadd('m', -5, now()) AND tipo != 'router';",
"refId": "A",
"selectedFormat": 0,
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "Online",
"type": "stat"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"fieldConfig": {
"defaults": {
"color": {
"mode": "thresholds"
},
"mappings": [],
"thresholds": {
"mode": "absolute",
"steps": [
{
"color": "red"
}
]
}
},
"overrides": []
},
"gridPos": {
"h": 8,
"w": 12,
"x": 12,
"y": 0
},
"id": 2,
"options": {
"colorMode": "value",
"graphMode": "area",
"justifyMode": "auto",
"orientation": "auto",
"percentChangeColorMode": "standard",
"reduceOptions": {
"calcs": [
"lastNotNull"
],
"fields": "",
"values": false
},
"showPercentChange": false,
"textMode": "auto",
"wideLayout": true
},
"pluginVersion": "12.0.2",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"editorMode": "code",
"format": 0,
"rawQuery": true,
"rawSql": "SELECT COUNT(DISTINCT mac) \r\nFROM devices \r\nWHERE (last_ping <= dateadd('m', -5, now()) OR last_ping IS NULL) and tipo != 'router';",
"refId": "A",
"selectedFormat": 0,
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "Offline",
"type": "stat"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"fieldConfig": {
"defaults": {
"color": {
"mode": "thresholds"
},
"custom": {
"align": "auto",
"cellOptions": {
"type": "auto"
},
"inspect": false
},
"mappings": [],
"thresholds": {
"mode": "absolute",
"steps": [
{
"color": "green"
},
{
"color": "red",
"value": 80
}
]
}
},
"overrides": [
{
"matcher": {
"id": "byName",
"options": "Duração Total"
},
"properties": [
{
"id": "custom.width",
"value": 116
}
]
},
{
"matcher": {
"id": "byName",
"options": "MAC"
},
"properties": [
{
"id": "custom.width",
"value": 153
}
]
},
{
"matcher": {
"id": "byName",
"options": "Proprietário"
},
"properties": [
{
"id": "custom.width",
"value": 157
}
]
},
{
"matcher": {
"id": "byName",
"options": "Fim do Apagão"
},
"properties": [
{
"id": "custom.width",
"value": 180
}
]
},
{
"matcher": {
"id": "byName",
"options": "Início do Apagão"
},
"properties": [
{
"id": "custom.width",
"value": 186
}
]
},
{
"matcher": {
"id": "byName",
"options": "Testes Executados"
},
"properties": [
{
"id": "custom.width",
"value": 150
}
]
}
]
},
"gridPos": {
"h": 8,
"w": 24,
"x": 0,
"y": 8
},
"id": 7,
"options": {
"cellHeight": "sm",
"footer": {
"countRows": false,
"fields": "",
"reducer": [
"sum"
],
"show": false
},
"showHeader": true,
"sortBy": []
},
"pluginVersion": "12.0.2",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"editorMode": "code",
"format": 1,
"rawQuery": true,
"rawSql": "SELECT\n o.outage_start_time AS \"Início do Apagão\",\n o.outage_end_time AS \"Fim do Apagão\",\n d.owner AS \"Proprietário\",\n o.mac_address AS \"MAC\",\n o.missed_tests_count AS \"Testes Executados\",\n CAST((o.outage_end_time - o.outage_start_time) / 1000000 AS LONG) / 60 AS \"Duração (minutos)\",\n o.details AS \"Horários: (Aprox.)\"\nFROM outage_logs AS o\nLEFT JOIN devices AS d ON d.mac = o.mac_address\nWHERE\n $**timeFilter(o.outage_start_time) AND\n o.outage_end_time > o.outage_start_time\n AND o.outage_end_time < dateadd('y', 1, now())\nORDER BY o.outage_start_time DESC;",
"refId": "A",
"selectedFormat": 1,
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "Registro de Apagões",
"type": "table"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"fieldConfig": {
"defaults": {
"color": {
"mode": "thresholds"
},
"custom": {
"align": "center",
"cellOptions": {
"type": "auto",
"wrapText": true
},
"filterable": false,
"inspect": false
},
"fieldMinMax": false,
"mappings": [],
"thresholds": {
"mode": "absolute",
"steps": [
{
"color": "green"
},
{
"color": "red",
"value": 80
}
]
}
},
"overrides": []
},
"gridPos": {
"h": 12,
"w": 24,
"x": 0,
"y": 16
},
"id": 3,
"options": {
"cellHeight": "md",
"footer": {
"countRows": false,
"fields": "",
"reducer": [
"sum"
],
"show": false
},
"showHeader": true,
"sortBy": [
{
"desc": false,
"displayName": "Tipo"
}
]
},
"pluginVersion": "12.0.2",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"editorMode": "code",
"format": 1,
"rawQuery": true,
"rawSql": "SELECT\n mac AS \"Mac\",\n owner AS \"Dono\",\n ip_wg AS \"IP\",\n last_ping AS \"Último Heartbeat\",\n CASE\n WHEN last_ping IS NULL THEN 'Nunca visto'\n ELSE concat(\n CAST(((now() - last_ping) / 86400000000) AS VARCHAR), 'd ',\n CAST((((now() - last_ping) / 3600000000) % 24) AS VARCHAR), 'h ',\n CAST((((now() - last_ping) / 60000000) % 60) AS VARCHAR), 'm'\n )\n END AS \"Tempo Offline\"\nFROM devices\nWHERE\n (last_ping <= dateadd('m', -5, now()) OR last_ping IS NULL) AND\n tipo != 'router'\nORDER BY last_ping IS NULL DESC, last_ping ASC;",
"refId": "A",
"selectedFormat": 1,
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "Dispositivos Offline",
"type": "table"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"fieldConfig": {
"defaults": {
"color": {
"mode": "thresholds"
},
"custom": {
"align": "center",
"cellOptions": {
"type": "auto"
},
"inspect": false
},
"mappings": [],
"thresholds": {
"mode": "absolute",
"steps": [
{
"color": "green"
},
{
"color": "red",
"value": 80
}
]
}
},
"overrides": [
{
"matcher": {
"id": "byName",
"options": "Detalhes"
},
"properties": [
{
"id": "custom.width",
"value": 522
}
]
},
{
"matcher": {
"id": "byName",
"options": "MAC"
},
"properties": [
{
"id": "custom.width",
"value": 191
}
]
},
{
"matcher": {
"id": "byName",
"options": "time"
},
"properties": [
{
"id": "custom.width",
"value": 202
}
]
},
{
"matcher": {
"id": "byName",
"options": "Origem"
},
"properties": [
{
"id": "custom.width",
"value": 142
}
]
},
{
"matcher": {
"id": "byName",
"options": "Tipo Erro"
},
"properties": [
{
"id": "custom.width",
"value": 211
}
]
},
{
"matcher": {
"id": "byName",
"options": "UUID Teste (se aplicável)"
},
"properties": [
{
"id": "custom.width",
"value": 509
}
]
}
]
},
"gridPos": {
"h": 9,
"w": 24,
"x": 0,
"y": 28
},
"id": 4,
"options": {
"cellHeight": "md",
"footer": {
"countRows": false,
"fields": "",
"reducer": [
"sum"
],
"show": false
},
"showHeader": true,
"sortBy": [
{
"desc": false,
"displayName": "Origem"
}
]
},
"pluginVersion": "12.0.2",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"editorMode": "code",
"format": 1,
"rawQuery": true,
"rawSql": "SELECT\n error_time AS \"time\",\n mac_address AS \"MAC\",\n source AS \"Origem\",\n error_type AS \"Tipo Erro\",\n details AS \"Detalhes\",\n test_uuid AS \"UUID Teste\"\nFROM application_errors\nWHERE\n $**timeFilter(error_time) AND mac_address = $mac\nORDER BY \"time\" DESC\nLIMIT 200;",
"refId": "A",
"selectedFormat": 1,
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "Errors de Aplicação",
"type": "table"
},
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"fieldConfig": {
"defaults": {
"color": {
"mode": "thresholds"
},
"custom": {
"align": "auto",
"cellOptions": {
"type": "auto"
},
"inspect": false
},
"mappings": [],
"thresholds": {
"mode": "absolute",
"steps": [
{
"color": "green"
},
{
"color": "red",
"value": 80
}
]
}
},
"overrides": [
{
"matcher": {
"id": "byName",
"options": "Status Download"
},
"properties": []
}
]
},
"gridPos": {
"h": 11,
"w": 24,
"x": 0,
"y": 37
},
"id": 5,
"options": {
"cellHeight": "sm",
"footer": {
"countRows": false,
"fields": "",
"reducer": [
"sum"
],
"show": false
},
"showHeader": true
},
"pluginVersion": "12.0.2",
"targets": [
{
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"editorMode": "code",
"format": 1,
"rawQuery": true,
"rawSql": "SELECT\n test_timestamp AS \"time\",\n mac_address AS \"MAC\",\n test_uuid,\n CASE WHEN download_tp_bps = -1 THEN 'Falha' ELSE 'OK' END AS \"Status Download\",\n CASE WHEN upload_tp_bps = -1 THEN 'Falha' ELSE 'OK' END AS \"Status Upload\",\n CASE WHEN traceroute_udp_error != 0 THEN 'Erro ' || traceroute_udp_error ELSE 'OK' END AS \"Status UDP Trace\",\n CASE WHEN traceroute_icmp_error != 0 THEN 'Erro ' || traceroute_icmp_error ELSE 'OK' END AS \"Status ICMP Trace\"\nFROM ndt_tests\nWHERE\n $**timeFilter(test_timestamp) AND\n (download_tp_bps = -1 OR upload_tp_bps = -1\n OR traceroute_udp_error != 0 OR traceroute_icmp_error != 0)\nORDER BY \"time\" DESC\nLIMIT 100;",
"refId": "A",
"selectedFormat": 1,
"sql": {
"columns": [
{
"parameters": [],
"type": "function"
}
],
"groupBy": [
{
"property": {
"type": "string"
},
"type": "groupBy"
}
],
"limit": 50
}
}
],
"title": "Erros de Testes",
"type": "table"
}
],
"preload": false,
"schemaVersion": 41,
"tags": [],
"templating": {
"list": [
{
"allowCustomValue": false,
"current": {
"text": [
"dc:a6:32:6b:9a:da - Theo"
],
"value": [
"dc:a6:32:6b:9a:da"
]
},
"datasource": {
"type": "grafana-postgresql-datasource",
"uid": "efsezsv9ajri8f"
},
"definition": "WITH test_counts AS (\n SELECT mac_address, COUNT() AS total_tests\n FROM ndt_tests\n GROUP BY mac_address\n)\nSELECT\n t.mac_address AS **value,\n CONCAT(\n t.mac_address,\n ' - ',\n COALESCE(d.owner, 'Sem Dono')\n ) AS **text,\n t.total_tests\nFROM test_counts t\nLEFT JOIN devices d ON d.mac = t.mac_address\nORDER BY t.total_tests DESC",
"description": "",
"multi": true,
"name": "mac",
"options": [],
"query": "WITH test_counts AS (\n SELECT mac_address, COUNT() AS total_tests\n FROM ndt_tests\n GROUP BY mac_address\n)\nSELECT\n t.mac_address AS **value,\n CONCAT(\n t.mac_address,\n ' - ',\n COALESCE(d.owner, 'Sem Dono')\n ) AS \_\_text,\n t.total_tests\nFROM test_counts t\nLEFT JOIN devices d ON d.mac = t.mac_address\nORDER BY t.total_tests DESC",
"refresh": 1,
"regex": "",
"type": "query"
}
]
},
"time": {
"from": "now-7d",
"to": "now"
},
"timepicker": {},
"timezone": "browser",
"title": "Monitoramento e Logs",
"uid": "questdb-monitoramento-e-logs",
"version": 2
}

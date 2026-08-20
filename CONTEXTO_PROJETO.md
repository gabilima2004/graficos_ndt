# CONTEXTO DO PROJETO — Gráficos NDT

> Use este arquivo como contexto ao iniciar um novo chat.

---

## 1. O que é o projeto

Dashboard no **Grafana** com dados do **NDT (Network Diagnostic Tool)** do M-Lab, armazenados em **QuestDB**. O chefe pediu para replicar um dashboard antigo, com foco em:

1. **Filtro por provedor (ISP)**
2. **Ver medições por provedor**
3. **Mapa relacionando clientes e servidores** (ver se há padrão geográfico)

---

## 2. Banco de dados — QuestDB

**Plugin Grafana:** `questdb-questdb-datasource` (UID: `dfudvhox4xudce`)

### 4 Tabelas:

**`client`** — client_ip, continent_code, country_code, country_name, region, city, postal_code, latitude, longitude, cidr, asn (STRING), as_name, client_name, early_exit, update_time

**`download`** — uuid, test_time, mean_throughput_mbps, min_rtt, loss_rate, version, git_short_commit, server_ip, server_port, client_ip, client_port, client_name, server_site, server_machine, server_asn, client_asn

**`upload`** — mesmas colunas do download

**`server`** — site, machine, server_ip, continent_code, country_code, country_name, region, city, postal_code, latitude, longitude, cidr, asn, as_name, machine_zone, machine_type, update_time

### Importante:

- A coluna `asn` é **STRING** (todos os ASNs vão entre aspas: `'28573'`)
- O macro de tempo do Grafana é `$__timeFilter(coluna)` (dois underscores)
- `count()` sem argumentos = `count(*)`
- `approx_median()` é a função de mediana do QuestDB

---

## 3. Mapeamento de ISPs (CASE WHEN por ASN)

A coluna `as_name` tem variações (ex: `CLARO S.A.` e `Claro S/A`). Solução: CASE WHEN por ASN normalizando os nomes. 33 ASNs mapeados:

```sql
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
END
```

---

## 4. Variáveis do Grafana

### `$isp` (filtro por provedor)

- Tipo: Query, Multi-value, Include All
- Query: `SELECT DISTINCT CASE WHEN ... END AS __text, CASE WHEN ... END AS __value FROM client ORDER BY 1`

### `$server` (filtro por servidor)

- Tipo: Query, Multi-value, Include All
- Query: `SELECT DISTINCT server_site AS __text, server_site AS __value FROM download WHERE server_site IS NOT NULL ORDER BY server_site`

### Sintaxe do filtro nas queries:

- ISP: `AND CASE WHEN ... END IN ($isp)`
- Server: `AND ('$server' = '$__all' OR d.server_site IN ($server))`

---

## 5. Estrutura do dashboard (4 partes)

### Parte 1 — Visão Geral ✅ JSON pronto (`ndt_dashboard_parte1.json`)

- Total de Clientes (Stat)
- Total de Servidores (Stat)
- Total de Testes (Stat)
- Clientes por Provedor (Bar Chart)
- Mapa Cliente→Servidor (Geomap 2 camadas: servidores azul fixo, clientes coloridos por server_ip)
- **Problema conhecido:** o mapa não está com as cores certas, precisa ajustar manualmente no Grafana

### Parte 2 — Métricas no tempo ✅ Funcionando (`ndt_dashboard_parte2.json`)

- Download (Time Series, cor por provedor, unit Mbps)
- Upload (Time Series, cor por provedor, unit Mbps)
- RTT (Time Series, escala log base 2, unit ms, filtro `min_rtt <= 1500000`)
- Loss Rate (Time Series, escala log base 2, unit percentunit)
- Todas com legendas: mean, last, p50, p90, p95
- Todas com `GROUP BY 1, 3` (tempo + provedor)
- **Correção aplicada:** QuestDB exige aspas duplas em palavras reservadas, então `AS time` foi alterado para `AS "time"` nas 4 queries

### Parte 3 — Estatísticas por Provedor ✅ JSON unificado (`ndt_dashboard_parte3.json`)

> Os arquivos `ndt_dashboard_parte3a.json` (tabelas) e `ndt_dashboard_parte3b.json` (bar charts) foram unidos em `ndt_dashboard_parte3.json`.

- **Tabelas:**
  - Download por Provedor (avg, mediana, min, max, total, clientes únicos + linha TOTAL GERAL via UNION ALL)
  - Upload por Provedor (mesma estrutura)
- **Bar Charts:**
  - Mediana Download por Provedor (DESC)
  - Mediana Upload por Provedor (DESC)
  - RTT médio por Provedor (ASC)
  - Loss Rate médio por Provedor (ASC)
  - Total de Testes por Provedor (DESC)

### Arquivos legados (mantidos para referência)

- `ndt_dashboard_parte3a.json` — versão anterior com apenas as tabelas
- `ndt_dashboard_parte3b.json` — versão anterior com apenas os bar charts

### Parte 4 — Distribuição ✅ JSON pronto (`ndt_dashboard_parte4.json`)

- Box Plot Download (roxo `#8e44ad`)
- Box Plot Upload (laranja `#e67e22`)
- Box Plot RTT (azul `#33a2e5`, escala log)
- Box Plot Loss Rate (vermelho `#e74c3c`, escala log, tickformat `.2%`)
- Cada painel: query SQL (dados brutos) + script JavaScript (Plotly)

---

## 6. Padrões das queries

### Query base (download + client com ISP):

```sql
SELECT ...
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE $__timeFilter(d.test_time)
    AND d.mean_throughput_mbps >= 0
    AND CASE WHEN ... END IN ($isp)
    AND ('$server' = '$__all' OR d.server_site IN ($server))
GROUP BY ...
ORDER BY ...
```

### Filtros de outlier:

- `mean_throughput_mbps >= 0`
- `min_rtt >= 0 AND min_rtt <= 1500000`
- `loss_rate >= 0`

### Ordenação:

- Throughput: `DESC` (maior é melhor)
- RTT e Loss: `ASC` (menor é melhor)

---

## 7. Arquivos do projeto

### Dashboards JSON (importáveis no Grafana)

| Arquivo                      | Conteúdo                                                                                 |
| ---------------------------- | ---------------------------------------------------------------------------------------- |
| `ndt_dashboard_parte1.json`  | Visão geral: clientes, servidores, testes, clientes por provedor e mapa cliente→servidor |
| `ndt_dashboard_parte2.json`  | Métricas no tempo: download, upload, RTT e loss rate por provedor                        |
| `ndt_dashboard_parte3.json`  | Estatísticas por provedor: tabelas + bar charts (unificação de 3a e 3b)                  |
| `ndt_dashboard_parte3a.json` | _(legado)_ Tabelas de estatísticas de download e upload por provedor                     |
| `ndt_dashboard_parte3b.json` | _(legado)_ Bar charts de mediana, RTT, loss rate e total de testes por provedor          |
| `ndt_dashboard_parte4.json`  | Box plots e violin plots (Plotly) por provedor                                           |

### Documentação de queries

| Arquivo                             | Conteúdo                                              |
| ----------------------------------- | ----------------------------------------------------- |
| `Dashboard_Parte1_VisaoGeral.md`    | Queries SQL e configuração dos painéis da Parte 1     |
| `Dashboard_Parte2_MetricasTempo.md` | Queries SQL e configuração das time series da Parte 2 |
| `Dashboard_Parte3_Estatisticas.md`  | Queries SQL das tabelas e bar charts da Parte 3       |
| `Dashboard_Parte4_Distribuicao.md`  | Queries SQL e scripts Plotly da Parte 4               |

### Documentação geral

| Arquivo                           | Conteúdo                                                                         |
| --------------------------------- | -------------------------------------------------------------------------------- |
| `CONTEXTO_PROJETO.md`             | Visão geral do projeto, banco, mapeamento, variáveis e status (este arquivo)     |
| `NDT_Documentacao.md`             | Explicação das métricas do NDT e descrição das tabelas do QuestDB                |
| `NDT_Insights_e_Interpretacao.md` | Guia de interpretação: o que cada gráfico revela e que decisões ele pode embasar |
| `Avaliacao_OldNDT.md`             | Análise dos dashboards antigos, boas práticas e problemas identificados          |
| `oldndt.md`                       | JSONs dos dashboards antigos do NDT (referência histórica)                       |

### Mapeamento de ISPs

| Arquivo                | Conteúdo                                                      |
| ---------------------- | ------------------------------------------------------------- |
| `isp_mapping.csv`      | Tabela de mapeamento de ASN para nome normalizado do provedor |
| `isp_mapping_doc.md`   | Documentação do mapeamento de ISPs                            |
| `isp_mapping_query.md` | Query SQL com o `CASE WHEN` completo de mapeamento de ISPs    |

### Outros arquivos

| Arquivo                           | Conteúdo                                                                 |
| --------------------------------- | ------------------------------------------------------------------------ |
| `fix_parte2.py`                   | Script Python usado para corrigir queries do `ndt_dashboard_parte2.json` |
| `Painel1_Clientes_Queries.md`     | Queries relacionadas ao painel de clientes                               |
| `Painel2_Servidores_Queries.md`   | Queries relacionadas ao painel de servidores                             |
| `Painel3_Metricas_Queries.md`     | Queries relacionadas às métricas                                         |
| `questdb-query-1786669747854.csv` | Arquivo CSV com resultado de uma query do QuestDB                        |

---

## 8. O que falta fazer / já resolvido

| #   | Item                                                                         | Status       | Observação                                                                           |
| --- | ---------------------------------------------------------------------------- | ------------ | ------------------------------------------------------------------------------------ |
| 1   | `ndt_dashboard_parte3b.json` — Bar charts de mediana por provedor            | ✅ Resolvido | JSON criado e pronto; posteriormente unificado com 3a em `ndt_dashboard_parte3.json` |
| 2   | `ndt_dashboard_parte4.json` — Box plots e violin plots (Plotly) por provedor | ✅ Resolvido | JSON criado e pronto                                                                 |
| 3   | Corrigir importação do `ndt_dashboard_parte2.json`                           | ✅ Resolvido | Erro do QuestDB com `AS time` foi corrigido para `AS "time"`                         |
| 4   | Ajustar o mapa do Parte 1 (cores das camadas do Geomap)                      | ⏳ Pendente  | Ajuste manual no Grafana                                                             |
| 5   | Unificar Parte 3a e Parte 3b                                                 | ✅ Resolvido | Arquivo `ndt_dashboard_parte3.json` criado com tabelas + bar charts                  |
| 6   | Unificar tudo em um único JSON                                               | ⏳ Opcional  | Não prioritário                                                                      |

---

## 9. Dashboard antigo (referência)

O `oldndt.md` contém 8 dashboards antigos:

- BigQuery: `NDT_7_Big_Query` (principal, 13 painéis), `NDT_7_Big_Query_tables_export`
- QuestDB: `Agrupado` (por MAC), `Individual` (por dispositivo, 19 painéis com violin plots), `Measurements Details`, `Monitoramento e Logs`
- Timescale: `Measurements Details`

### Boas práticas do antigo para manter:

- Filtros de outlier
- Escala log para RTT e loss rate
- Legendas com percentis (mean, p50, p90, p95)
- `approx_median()` em vez de `avg()` onde possível
- Cores temáticas: download=roxo, upload=laranja, RTT=azul, loss=vermelho
- Tabela com linha de total geral (UNION ALL)
- `SAMPLE BY` do QuestDB para agregação temporal

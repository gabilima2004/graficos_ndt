# Guia de Análise de Dados NDT

> Objetivo: analisar os dados do NDT de forma superficial, um provedor/servidor por vez,
> e identificar padrões. Este guia te dá as queries prontas para rodar no console do QuestDB.

---

## Estratégia

Como são muitos provedores (33) e muitos servidores, vamos analisar **1 de cada vez**:

1. **Visão geral** — panorama de todos os provedores
2. **Analisar os 3 maiores provedores** — Telefônica, Claro, e o 3º que aparecer
3. **Analisar os servidores mais usados**
4. **Comparar provedores** — quem é melhor em quê
5. **Identificar padrões** — geográficos, temporais, de qualidade

---

## Fase 1 — Visão Geral (rodar no console do QuestDB)

### 1.1 — Ranking de provedores por volume de testes (últimos 7 dias)

```sql
SELECT
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
    END AS provedor,
    count() AS total_testes,
    count(DISTINCT d.client_ip) AS clientes_unicos
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE d.test_time > dateadd('d', -7, now())
    AND d.mean_throughput_mbps >= 0
GROUP BY provedor
ORDER BY total_testes DESC;
```

**O que isso mostra:** qual provedor tem mais testes e mais clientes. Os 3 maiores são os que vamos analisar primeiro.

### 1.2 — Resumo de qualidade por provedor (mediana e RTT)

```sql
SELECT
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
    END AS provedor,
    count() AS testes,
    approx_median(d.mean_throughput_mbps) AS mediana_download,
    avg(d.mean_throughput_mbps) AS media_download,
    approx_median(d.min_rtt) AS mediana_rtt,
    approx_median(d.loss_rate) AS mediana_loss
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE d.test_time > dateadd('d', -7, now())
    AND d.mean_throughput_mbps >= 0
    AND d.min_rtt >= 0 AND d.min_rtt <= 1500000
    AND d.loss_rate >= 0
GROUP BY provedor
ORDER BY mediana_download DESC;
```

**O que isso mostra:** ranking de provedores por qualidade (download, RTT, loss). Salve o resultado como CSV.

---

## Fase 2 — Analisar os 3 maiores provedores (1 por vez)

### 2.1 — Perfil do provedor (exemplo: Telefônica)

```sql
SELECT
    count() AS total_testes,
    count(DISTINCT d.client_ip) AS clientes_unicos,
    approx_median(d.mean_throughput_mbps) AS mediana_download,
    avg(d.mean_throughput_mbps) AS media_download,
    min(d.mean_throughput_mbps) AS min_download,
    max(d.mean_throughput_mbps) AS max_download,
    approx_median(d.min_rtt) AS mediana_rtt,
    approx_median(d.loss_rate) AS mediana_loss,
    count(DISTINCT d.server_site) AS servidores_usados
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE d.test_time > dateadd('d', -7, now())
    AND d.mean_throughput_mbps >= 0
    AND c.asn IN ('18881', '26599', '27699', '19182', '10429');
```

**Para analisar Claro:** troque os ASNs por `('28573', '4230', '22085')`
**Para analisar outro provedor:** troque os ASNs pelos dele (ver `04_isp_mapping/isp_mapping.csv`)

### 2.2 — Distribuição de download por provedor (percentis)

```sql
SELECT
    approx_median(d.mean_throughput_mbps) AS p50,
    approx_percentile(d.mean_throughput_mbps, 0.90) AS p90,
    approx_percentile(d.mean_throughput_mbps, 0.95) AS p95,
    approx_percentile(d.mean_throughput_mbps, 0.10) AS p10
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE d.test_time > dateadd('d', -7, now())
    AND d.mean_throughput_mbps >= 0
    AND c.asn IN ('18881', '26599', '27699', '19182', '10429');
```

**Interpretação:**

- p50 (mediana) = experiência do cliente típico
- p90 = 10% dos clientes têm download acima disso
- p10 = 10% dos clientes têm download abaixo disso (os piores)
- Diferença grande entre p10 e p90 = muita desigualdade de qualidade

### 2.3 — Quais servidores cada provedor usa mais

```sql
SELECT
    d.server_site,
    count() AS total_testes,
    count(DISTINCT d.client_ip) AS clientes_unicos,
    approx_median(d.mean_throughput_mbps) AS mediana_download,
    approx_median(d.min_rtt) AS mediana_rtt
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE d.test_time > dateadd('d', -7, now())
    AND d.mean_throughput_mbps >= 0
    AND c.asn IN ('18881', '26599', '27699', '19182', '10429')
GROUP BY d.server_site
ORDER BY total_testes DESC
LIMIT 10;
```

**O que isso mostra:** quais servidores o provedor usa mais e a qualidade em cada um.

---

## Fase 3 — Comparar provedores

### 3.1 — Ranking de download mediano (todos os provedores)

```sql
SELECT
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
    END AS provedor,
    approx_median(d.mean_throughput_mbps) AS mediana_download,
    approx_median(d.min_rtt) AS mediana_rtt,
    approx_median(d.loss_rate) AS mediana_loss,
    count() AS testes
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE d.test_time > dateadd('d', -7, now())
    AND d.mean_throughput_mbps >= 0
    AND d.min_rtt >= 0 AND d.min_rtt <= 1500000
    AND d.loss_rate >= 0
GROUP BY provedor
ORDER BY mediana_download DESC;
```

### 3.2 — Mesmo ranking para upload

```sql
SELECT
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
    END AS provedor,
    approx_median(u.mean_throughput_mbps) AS mediana_upload,
    count() AS testes
FROM upload u
JOIN client c ON u.client_ip = c.client_ip
WHERE u.test_time > dateadd('d', -7, now())
    AND u.mean_throughput_mbps >= 0
GROUP BY provedor
ORDER BY mediana_upload DESC;
```

---

## Fase 4 — Identificar padrões

### 4.1 — Padrão temporal: horários de pico e queda

```sql
SELECT
    hour(d.test_time) AS hora,
    approx_median(d.mean_throughput_mbps) AS mediana_download,
    count() AS total_testes
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE d.test_time > dateadd('d', -7, now())
    AND d.mean_throughput_mbps >= 0
    AND c.asn IN ('18881', '26599', '27699', '19182', '10429')
GROUP BY hora
ORDER BY hora;
```

**O que procurar:**

- Download cai em horários de pico (18h-22h)? = congestionamento
- Download sobe de madrugada? = confirma congestionamento diurno
- Testes aumentam em algum horário? = padrão de uso

### 4.2 — Padrão geográfico: qualidade por cidade

```sql
SELECT
    c.city,
    c.region,
    count() AS total_testes,
    approx_median(d.mean_throughput_mbps) AS mediana_download,
    approx_median(d.min_rtt) AS mediana_rtt
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE d.test_time > dateadd('d', -7, now())
    AND d.mean_throughput_mbps >= 0
    AND c.country_code = 'BR'
    AND c.asn IN ('18881', '26599', '27699', '19182', '10429')
    AND c.city IS NOT NULL
GROUP BY c.city, c.region
ORDER BY total_testes DESC
LIMIT 20;
```

**O que procurar:**

- Cidades com download muito abaixo da média = problema local
- Cidades com RTT alto = longe dos servidores ou roteamento ruim
- Diferença grande entre cidades do mesmo provedor = infraestrutura desigual

### 4.3 — Padrão: clientes com early_exit (desistiram do teste)

```sql
SELECT
    CASE
        WHEN c.asn IN ('18881', '26599', '27699', '19182', '10429') THEN 'Telefônica'
        WHEN c.asn IN ('28573', '4230', '22085') THEN 'Claro'
        ELSE c.as_name
    END AS provedor,
    count() AS total_testes,
    sum(CASE WHEN c.early_exit = 'true' THEN 1 ELSE 0 END) AS desistencias,
    round(100.0 * sum(CASE WHEN c.early_exit = 'true' THEN 1 ELSE 0 END) / count(), 2) AS pct_desistencia
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE d.test_time > dateadd('d', -7, now())
GROUP BY provedor
ORDER BY pct_desistencia DESC;
```

**O que isso mostra:** provedores com mais desistências podem ter testes que demoram demais (rede lenta).

---

## Fase 5 — Relatório final

Depois de rodar as queries e salvar os resultados, preencha o relatório:

### Template do relatório

```markdown
# Análise NDT — Resultados

## 1. Visão Geral

- Total de testes (7 dias): XXX
- Total de clientes únicos: XXX
- Provedor com mais testes: XXX
- Provedor com melhor download mediano: XXX

## 2. Ranking de Provedores

| Provedor | Testes | Mediana Download | Mediana RTT | Mediana Loss |
| -------- | ------ | ---------------- | ----------- | ------------ |
| ...      | ...    | ...              | ...         | ...          |

## 3. Análise dos 3 maiores provedores

### 3.1 Telefônica

- Clientes: XXX
- Download mediano: XXX Mbps
- RTT mediano: XXX ms
- Loss mediano: XXX%
- Servidores mais usados: XXX
- Padrão geográfico: XXX

### 3.2 Claro

- (mesma estrutura)

### 3.3 (3º provedor)

- (mesma estrutura)

## 4. Padrões identificados

- Padrão temporal: XXX
- Padrão geográfico: XXX
- Correlação RTT vs download: XXX
- Provedores com mais desistências: XXX

## 5. Conclusões

- Provedor mais rápido: XXX
- Provedor mais estável: XXX
- Provedor com melhor latência: XXX
- Recomendações: XXX
```

---

## Como usar este guia

1. Abra o console do QuestDB (interface web, porta 9000)
2. Rode as queries **uma por vez**
3. Salve os resultados como CSV (botão Download no console)
4. Guarde os CSVs na pasta `07_dados_csv/`
5. Anote os achados no relatório (template acima)
6. Comece pela Fase 1, depois Fase 2, etc.

**Dica:** se uma query demorar mais de 30 segundos, reduza o período de 7 dias para 1 dia (`dateadd('d', -1, now()`)

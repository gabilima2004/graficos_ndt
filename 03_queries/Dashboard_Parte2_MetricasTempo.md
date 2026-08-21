# Dashboard NDT Unificado — Parte 2: Métricas ao longo do tempo

> **Tipo de painel:** Time Series  
> **Filtros:** `$isp` (provedor), `$server` (servidor), período do dashboard  
> **Coloração:** Por provedor (ISP normalizado via CASE WHEN)

---

## Conceito-chave: Coloração por provedor

No dashboard antigo, a coloração condicional usava:

```sql
CASE WHEN '${Provedor:csv}' LIKE '%,%' THEN t.provider ELSE t.zone END
```

No nosso caso, como sempre filtramos por ISP, a coloração será **sempre por provedor**:

```sql
CASE
    WHEN c.asn IN ('18881', ...) THEN 'Telefônica'
    WHEN c.asn IN ('28573', ...) THEN 'Claro'
    ...
END AS provedor
```

O Grafana cria uma linha para cada valor único de `provedor`.

---

## 2.1 — Download ao longo do tempo (Time Series)

```sql
SELECT
    $__timeGroup(d.test_time, '5m') AS time,
    avg(d.mean_throughput_mbps) AS download_mbps,
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
    END AS provedor
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
GROUP BY 1, 3
ORDER BY 1 ASC
```

### Configuração no Grafana:

| Configuração   | Valor                               |
| -------------- | ----------------------------------- |
| Unit           | `Mbps` ou `Mbits/sec`               |
| Draw style     | `points`                            |
| Point size     | `5`                                 |
| Line width     | `0`                                 |
| Legend calcs   | `mean`, `last`, `p50`, `p90`, `p95` |
| Legend display | `list`                              |
| Color mode     | `palette-classic`                   |

---

## 2.2 — Upload ao longo do tempo (Time Series)

```sql
SELECT
    $__timeGroup(d.test_time, '5m') AS time,
    avg(d.mean_throughput_mbps) AS upload_mbps,
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
    END AS provedor
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
GROUP BY 1, 3
ORDER BY 1 ASC
```

### Configuração no Grafana:

| Configuração | Valor                               |
| ------------ | ----------------------------------- |
| Unit         | `Mbps` ou `Mbits/sec`               |
| Draw style   | `points`                            |
| Point size   | `5`                                 |
| Line width   | `0`                                 |
| Legend calcs | `mean`, `last`, `p50`, `p90`, `p95` |
| Color mode   | `palette-classic`                   |

---

## 2.3 — RTT ao longo do tempo (Time Series, escala log)

```sql
SELECT
    $__timeGroup(d.test_time, '5m') AS time,
    avg(d.min_rtt) AS rtt_ms,
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
    END AS provedor
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
GROUP BY 1, 3
ORDER BY 1 ASC
```

### Configuração no Grafana:

| Configuração       | Valor                               |
| ------------------ | ----------------------------------- |
| Unit               | `ms` (milissegundos)                |
| Draw style         | `points`                            |
| Point size         | `5`                                 |
| Line width         | `0`                                 |
| Scale distribution | `Log`, base `2`                     |
| Legend calcs       | `mean`, `last`, `p50`, `p90`, `p95` |
| Color mode         | `palette-classic`                   |

> **Filtro de outlier:** `min_rtt <= 1500000` remove valores absurdos (herdado do dashboard antigo).

---

## 2.4 — Loss Rate ao longo do tempo (Time Series, escala log)

```sql
SELECT
    $__timeGroup(d.test_time, '5m') AS time,
    avg(d.loss_rate) AS loss_rate,
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
    END AS provedor
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
GROUP BY 1, 3
ORDER BY 1 ASC
```

### Configuração no Grafana:

| Configuração       | Valor                               |
| ------------------ | ----------------------------------- |
| Unit               | `percentunit` (0.0-1.0 → 0%-100%)   |
| Draw style         | `points`                            |
| Point size         | `5`                                 |
| Line width         | `0`                                 |
| Scale distribution | `Log`, base `2`                     |
| Legend calcs       | `mean`, `last`, `p50`, `p90`, `p95` |
| Color mode         | `palette-classic`                   |

---

## Resumo da Parte 2

| #   | Painel    | Tabela     | Unit        | Escala           | Filtro de outlier     |
| --- | --------- | ---------- | ----------- | ---------------- | --------------------- |
| 2.1 | Download  | `download` | Mbps        | Linear           | `>= 0`                |
| 2.2 | Upload    | `upload`   | Mbps        | Linear           | `>= 0`                |
| 2.3 | RTT       | `download` | ms          | **Log (base 2)** | `>= 0 AND <= 1500000` |
| 2.4 | Loss Rate | `download` | percentunit | **Log (base 2)** | `>= 0`                |

### Padrão em todas as queries:

- `$__timeGroup(d.test_time, '5m')` — agrupa em buckets de 5 minutos
- `JOIN client c ON d.client_ip = c.client_ip` — traz o ASN do cliente
- CASE WHEN no SELECT → vira a coluna `provedor` (cor da linha)
- CASE WHEN no WHERE → filtra pelo ISP selecionado
- `('$server' = '$__all' OR d.server_site IN ($server))` — filtro de servidor opcional
- `GROUP BY 1, 3` — agrupa por tempo (1) e provedor (3)
- `ORDER BY 1 ASC` — ordena por tempo

### Pergunta para refletir:

> Por que RTT e Loss Rate usam escala log, mas Download e Upload não?
> **Resposta:** RTT e loss rate variam em várias ordens de grandeza (ex: RTT de 5ms a 500ms, loss de 0.001 a 0.5). Escala log mostra melhor essa variação. Download/upload já variam de forma mais linear (ex: 10 a 100 Mbps).

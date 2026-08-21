# Dashboard NDT Unificado — Parte 3: Estatísticas por provedor

> **Tipos de painel:** Table + Bar Chart  
> **Filtros:** `$isp` (provedor), `$server` (servidor), período do dashboard

---

## 3.1 — Tabela de Estatísticas de Download por Provedor (Table)

**Tipo de painel:** Table  
**Descrição:** Estatísticas completas de download por provedor, com linha de total geral no final.

```sql
SELECT * FROM (
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
        END AS "Provedor",
        count() AS "Total de Testes",
        count(DISTINCT d.client_ip) AS "Clientes Únicos",
        round(avg(d.mean_throughput_mbps), 2) AS "Média (Mbps)",
        approx_median(d.mean_throughput_mbps) AS "Mediana (Mbps)",
        round(min(d.mean_throughput_mbps), 2) AS "Mínimo (Mbps)",
        round(max(d.mean_throughput_mbps), 2) AS "Máximo (Mbps)"
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
    GROUP BY "Provedor"

    UNION ALL

    SELECT
        '📊 TOTAL GERAL' AS "Provedor",
        count() AS "Total de Testes",
        count(DISTINCT d.client_ip) AS "Clientes Únicos",
        round(avg(d.mean_throughput_mbps), 2) AS "Média (Mbps)",
        approx_median(d.mean_throughput_mbps) AS "Mediana (Mbps)",
        round(min(d.mean_throughput_mbps), 2) AS "Mínimo (Mbps)",
        round(max(d.mean_throughput_mbps), 2) AS "Máximo (Mbps)"
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
) AS resultado
ORDER BY "Total de Testes" DESC
```

> **Atenção:** O `UNION ALL` adiciona a linha "📊 TOTAL GERAL" no final. O `SELECT * FROM (...)` no final permite ordenar o resultado completo.

### Configuração no Grafana:

| Configuração | Valor                                |
| ------------ | ------------------------------------ |
| Cell options | `color-background`                   |
| Color mode   | `continuous-GrYlRd`                  |
| Thresholds   | red < 50, yellow 50-100, green > 100 |
| Footer       | `show: true`, reducer: `sum`         |
| Sort by      | "Total de Testes" DESC               |

---

## 3.2 — Tabela de Estatísticas de Upload por Provedor (Table)

```sql
SELECT * FROM (
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
        END AS "Provedor",
        count() AS "Total de Testes",
        count(DISTINCT d.client_ip) AS "Clientes Únicos",
        round(avg(d.mean_throughput_mbps), 2) AS "Média (Mbps)",
        approx_median(d.mean_throughput_mbps) AS "Mediana (Mbps)",
        round(min(d.mean_throughput_mbps), 2) AS "Mínimo (Mbps)",
        round(max(d.mean_throughput_mbps), 2) AS "Máximo (Mbps)"
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
    GROUP BY "Provedor"

    UNION ALL

    SELECT
        '📊 TOTAL GERAL' AS "Provedor",
        count() AS "Total de Testes",
        count(DISTINCT d.client_ip) AS "Clientes Únicos",
        round(avg(d.mean_throughput_mbps), 2) AS "Média (Mbps)",
        approx_median(d.mean_throughput_mbps) AS "Mediana (Mbps)",
        round(min(d.mean_throughput_mbps), 2) AS "Mínimo (Mbps)",
        round(max(d.mean_throughput_mbps), 2) AS "Máximo (Mbps)"
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
) AS resultado
ORDER BY "Total de Testes" DESC
```

> **Diferença da 3.1:** Usa `FROM upload` em vez de `FROM download`.

---

## 3.3 — Mediana de Download por Provedor (Bar Chart)

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
    approx_median(d.mean_throughput_mbps) AS mediana_download_mbps
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
GROUP BY provedor
ORDER BY mediana_download_mbps DESC
```

> **Por que mediana e não média?** A mediana é mais robusta contra outliers. Um único teste de 1000 Mbps pode puxar a média para cima, mas a mediana não é afetada.

---

## 3.4 — Mediana de Upload por Provedor (Bar Chart)

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
    approx_median(d.mean_throughput_mbps) AS mediana_upload_mbps
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
GROUP BY provedor
ORDER BY mediana_upload_mbps DESC
```

---

## 3.5 — RTT Médio por Provedor (Bar Chart)

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
    round(avg(d.min_rtt), 2) AS rtt_medio_ms
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
GROUP BY provedor
ORDER BY rtt_medio_ms ASC
```

> **Atenção:** `ORDER BY ... ASC` — menor RTT é melhor (diferente do throughput onde maior é melhor).

---

## 3.6 — Loss Rate Médio por Provedor (Bar Chart)

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
    round(avg(d.loss_rate), 4) AS loss_rate_medio
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
GROUP BY provedor
ORDER BY loss_rate_medio ASC
```

> **Atenção:** `ORDER BY ... ASC` — menor loss rate é melhor.  
> Configure o Unit para `percentunit` no Grafana.

---

## 3.7 — Total de Testes por Provedor (Bar Chart)

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
    count() AS total_testes
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE $__timeFilter(d.test_time)
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
GROUP BY provedor
ORDER BY total_testes DESC
```

---

## Resumo da Parte 3

| #   | Painel                        | Tipo      | Tabela   | ORDER BY     | Unit        |
| --- | ----------------------------- | --------- | -------- | ------------ | ----------- |
| 3.1 | Estatísticas de Download      | Table     | download | Total DESC   | Mbps        |
| 3.2 | Estatísticas de Upload        | Table     | upload   | Total DESC   | Mbps        |
| 3.3 | Mediana Download por Provedor | Bar Chart | download | Mediana DESC | Mbps        |
| 3.4 | Mediana Upload por Provedor   | Bar Chart | upload   | Mediana DESC | Mbps        |
| 3.5 | RTT Médio por Provedor        | Bar Chart | download | RTT **ASC**  | ms          |
| 3.6 | Loss Rate Médio por Provedor  | Bar Chart | download | Loss **ASC** | percentunit |
| 3.7 | Total de Testes por Provedor  | Bar Chart | download | Total DESC   | none        |

### Pergunta para refletir:

> Por que as tabelas (3.1 e 3.2) usam `UNION ALL` para adicionar o total geral?
> **Resposta:** O `UNION ALL` permite combinar duas queries — uma com os dados por provedor e outra com o total consolidado. O `ALL` (em vez de `UNION` simples) não remove duplicatas, o que é importante porque o total geral é uma linha adicional, não uma duplicata.

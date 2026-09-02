# Dashboard NDT Unificado — Parte 1: Visão Geral

> **Banco:** QuestDB  
> **Plugin Grafana:** QuestDB Data Source (`questdb-questdb-datasource`)  
> **Tabelas:** `download`, `upload`, `client`, `server`

---

## Estrutura do dashboard completo (4 partes)

```
Parte 1 — Visão Geral (este arquivo)
  ├── Total de clientes (Stat)
  ├── Total de servidores (Stat)
  ├── Total de testes (Stat)
  ├── Mapa cliente→servidor (Geomap 2 camadas)
  └── Clientes por provedor (Bar Chart)

Parte 2 — Métricas ao longo do tempo
  ├── Download (Time Series, cor por provedor)
  ├── Upload (Time Series, cor por provedor)
  ├── RTT (Time Series, escala log, cor por provedor)
  └── Loss Rate (Time Series, escala log, cor por provedor)

Parte 3 — Estatísticas por provedor
  ├── Tabela com avg/min/max/mediana + total geral
  ├── Bar charts: mediana de download/upload/RTT/loss por provedor
  └── Bar chart: total de testes por provedor

Parte 4 — Distribuição
  ├── Box plot de download por provedor (Plotly)
  ├── Violin plot de download por provedor (Plotly)
  └── (opcional) Box/violin de upload, RTT, loss
```

---

## Variáveis do dashboard

### Variável 1: `isp` (filtro por provedor)

**Tipo:** Query  
**Multi-value:** ✅  
**Include All:** ✅

```sql
SELECT DISTINCT
    CASE
        WHEN asn IN ('18881', '26599', '27699', '19182', '10429') THEN 'Telefônica'
        WHEN asn IN ('28573', '4230', '22085') THEN 'Claro'
        WHEN asn IN ('265303') THEN 'TV Alphaville'
        WHEN asn IN ('14868') THEN 'COPEL Telecom'
        WHEN asn IN ('53184') THEN 'INB Telecom'
        WHEN asn IN ('262907') THEN 'Avato Tecnologia'
        WHEN asn IN ('61844') THEN 'New Master'
        WHEN asn IN ('28258') THEN 'Powerline Internet'
        WHEN asn IN ('273683') THEN 'Desconhecido'
        WHEN asn IN ('22689') THEN 'Sercomtel'
        WHEN asn IN ('53062') THEN 'G G Net'
        WHEN asn IN ('264228') THEN 'Brasil Starlink'
        WHEN asn IN ('28669') THEN 'America Net'
        WHEN asn IN ('263645') THEN 'Fixtell Telecom'
        WHEN asn IN ('266949') THEN 'Divifibra'
        WHEN asn IN ('262700') THEN 'Efibra Telecom'
        WHEN asn IN ('28658') THEN 'Gigalink'
        WHEN asn IN ('262673') THEN 'Lafaiete'
        WHEN asn IN ('52900') THEN 'Quality Telecom'
        WHEN asn IN ('263629') THEN 'Celloni'
        WHEN asn IN ('52940') THEN 'Nemesis'
        WHEN asn IN ('262671') THEN 'S & M Informática'
        WHEN asn IN ('28241') THEN 'Viaceu Internet'
        WHEN asn IN ('53191') THEN 'Plug Telecom'
        WHEN asn IN ('28263') THEN 'Ensite Brasil'
        WHEN asn IN ('263072') THEN 'BD Fibra Telecom'
        WHEN asn IN ('53171') THEN 'Omni Telecom'
        ELSE as_name
    END AS __text,
    CASE
        WHEN asn IN ('18881', '26599', '27699', '19182', '10429') THEN 'Telefônica'
        WHEN asn IN ('28573', '4230', '22085') THEN 'Claro'
        WHEN asn IN ('265303') THEN 'TV Alphaville'
        WHEN asn IN ('14868') THEN 'COPEL Telecom'
        WHEN asn IN ('53184') THEN 'INB Telecom'
        WHEN asn IN ('262907') THEN 'Avato Tecnologia'
        WHEN asn IN ('61844') THEN 'New Master'
        WHEN asn IN ('28258') THEN 'Powerline Internet'
        WHEN asn IN ('273683') THEN 'Desconhecido'
        WHEN asn IN ('22689') THEN 'Sercomtel'
        WHEN asn IN ('53062') THEN 'G G Net'
        WHEN asn IN ('264228') THEN 'Brasil Starlink'
        WHEN asn IN ('28669') THEN 'America Net'
        WHEN asn IN ('263645') THEN 'Fixtell Telecom'
        WHEN asn IN ('266949') THEN 'Divifibra'
        WHEN asn IN ('262700') THEN 'Efibra Telecom'
        WHEN asn IN ('28658') THEN 'Gigalink'
        WHEN asn IN ('262673') THEN 'Lafaiete'
        WHEN asn IN ('52900') THEN 'Quality Telecom'
        WHEN asn IN ('263629') THEN 'Celloni'
        WHEN asn IN ('52940') THEN 'Nemesis'
        WHEN asn IN ('262671') THEN 'S & M Informática'
        WHEN asn IN ('28241') THEN 'Viaceu Internet'
        WHEN asn IN ('53191') THEN 'Plug Telecom'
        WHEN asn IN ('28263') THEN 'Ensite Brasil'
        WHEN asn IN ('263072') THEN 'BD Fibra Telecom'
        WHEN asn IN ('53171') THEN 'Omni Telecom'
        ELSE as_name
    END AS __value
FROM client
ORDER BY 1
```

### Variável 2: `server` (filtro por servidor)

**Tipo:** Query  
**Multi-value:** ✅  
**Include All:** ✅

```sql
SELECT DISTINCT
    server_site AS __text,
    server_site AS __value
FROM download
WHERE server_site IS NOT NULL
ORDER BY server_site
```

---

## Queries da Parte 1 — Visão Geral

### 1.1 — Total de Clientes Únicos (Stat)

```sql
SELECT count(DISTINCT d.client_ip) AS total_clientes
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
```

### 1.2 — Total de Servidores (Stat)

```sql
SELECT count(DISTINCT server_ip) AS total_servidores
FROM server
```

### 1.3 — Total de Testes (Stat)

```sql
SELECT count() AS total_testes
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
```

### 1.4 — Mapa Cliente→Servidor (Geomap 2 camadas)

**Camada 1 — Servidores** (pontos grandes, cor fixa):

```sql
SELECT
    s.latitude AS lat,
    s.longitude AS lon,
    s.server_ip,
    s.site,
    s.machine,
    s.country_name,
    s.city,
    s.as_name AS server_isp
FROM server s
WHERE s.latitude IS NOT NULL
    AND s.longitude IS NOT NULL
```

**Camada 2 — Clientes** (pontos pequenos, cor por servidor):

```sql
SELECT
    c.latitude AS lat,
    c.longitude AS lon,
    c.client_ip,
    d.server_ip,
    d.server_site,
    c.city,
    c.country_name,
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
    AND c.latitude IS NOT NULL
    AND c.longitude IS NOT NULL
    AND ('$server' = '$__all' OR d.server_site IN ($server))
GROUP BY c.latitude, c.longitude, c.client_ip, d.server_ip, d.server_site, c.city, c.country_name
```

### 1.5 — Clientes por Provedor (Bar Chart)

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
    count(DISTINCT d.client_ip) AS total_clientes
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
GROUP BY provedor
ORDER BY total_clientes DESC
LIMIT 20
```

---

## Configurações do Geomap (importante!)

### Camada 1 — Servidores:

| Configuração    | Valor                         |
| --------------- | ----------------------------- |
| Display name    | `Servidores`                  |
| Location mode   | Coords                        |
| Latitude field  | `lat`                         |
| Longitude field | `lon`                         |
| Color mode      | Fixed                         |
| Color           | `blue`                        |
| Size mode       | Fixed                         |
| Size            | `10`                          |
| Symbol          | `img/icons/marker/circle.svg` |

### Camada 2 — Clientes:

| Configuração    | Valor                         |
| --------------- | ----------------------------- | --- |
| Display name    | `Clientes`                    |
| Location mode   | Coords                        |
| Latitude field  | `lat`                         |
| Longitude field | `lon`                         |
| Color mode      | Value                         |
| Color field     | `server_ip`                   |
| Color scheme    | Palette classic               |
| Size mode       | Value                         |
| Size field      | `total_testes`                |
| Size min        | 2, max                        | 8   |
| Symbol          | `img/icons/marker/circle.svg` |

---

## Notas

- O filtro `$server` usa a sintaxe `('$server' = '$__all' OR d.server_site IN ($server))` que permite "All" sem quebrar a query
- Os filtros de outlier (`mean_throughput_mbps >= 0`, `min_rtt <= 1500000`, `loss_rate >= 0`) serão adicionados na Parte 2 (métricas)
- O CASE WHEN é repetido em cada query porque não estamos usando view
- Para o JSON do Grafana, será gerado após definirmos todas as 4 partes

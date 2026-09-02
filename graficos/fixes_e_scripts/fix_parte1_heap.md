# Fix — Parte 1: Java Heap Space

> Erro: `java heap space` no QuestDB ao carregar a Parte 1.
> Causa: queries pesadas (GROUP BY por lat/lon, `count(DISTINCT)`, JOIN sobre 30 dias).

---

## Problemas identificados

### 1. Mapa (painel 1.4) — CRÍTICO

```sql
-- ❌ PROBLEMA: agrupa por lat+lon = ~467k grupos + count(DISTINCT)
GROUP BY c.latitude, c.longitude, c.city, c.country_name, d.server_site
count(DISTINCT d.client_ip) AS clientes_unicos
```

Cada combinação única de latitude/longitude é um grupo separado. Com 467k clientes, isso cria centenas de milhares de grupos na memória.

### 2. count(DISTINCT) — pesado em memória

`count(DISTINCT coluna)` mantém todos os valores únicos na memória para deduplicar. Em tabelas grandes, isso esgota o heap.

### 3. Período de 30 dias

O dashboard está com `from: "now-30d"`. Mais dados = mais memória.

---

## Soluções aplicadas

### 1. Mapa: agrupar por CIDADE em vez de lat/lon

```sql
-- ✅ OTIMIZADO: agrupa por cidade (poucos grupos) + avg(lat/lon) para posicionar
SELECT
    avg(c.latitude) AS lat,
    avg(c.longitude) AS lon,
    c.city,
    c.country_name,
    d.server_site,
    count() AS total_testes
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE $__timeFilter(d.test_time)
    AND c.country_code = 'BR'
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
GROUP BY c.city, c.country_name, d.server_site
LIMIT 500
```

**O que mudou:**

- `GROUP BY c.city, c.country_name, d.server_site` (poucos grupos) em vez de lat/lon (centenas de milhares)
- `avg(c.latitude)` e `avg(c.longitude)` para posicionar o ponto no centro da cidade
- Removido `count(DISTINCT d.client_ip)` (pesado em memória)
- Adicionado `LIMIT 500` como segurança

### 2. count(DISTINCT) — MANTIDO (não usar approx_distinct)

```sql
-- ✅ MANTER: count(DISTINCT) funciona corretamente
SELECT count(DISTINCT d.client_ip) AS total_clientes
```

> **Aviso:** `approx_distinct()` NÃO funciona neste QuestDB — retorna erro
> `unknown function name: approx_distinct(SYMBOL)`.
> A função não suporta colunas do tipo SYMBOL (que é o tipo de `client_ip`).
> Mantenha `count(DISTINCT)` que funciona normalmente.

### 3. Reduzir período padrão para 7 dias

No JSON do dashboard, alterar:

```json
"time": {
    "from": "now-7d",   // era "now-30d"
    "to": "now"
}
```

---

## Resumo das mudanças

| Painel               | Mudança                                                  | Motivo                                  |
| -------------------- | -------------------------------------------------------- | --------------------------------------- |
| Mapa (1.4)           | `GROUP BY city` em vez de `lat,lon` + `LIMIT 500`        | Reduz de ~467k grupos para ~milhares    |
| Mapa (1.4)           | Subquery de pré-agregação + `GROUP BY city`              | Reduz volume do JOIN + número de grupos |
| Mapa (1.4)           | Removido `count(DISTINCT)`                               | Menos consumo de memória                |
| Total Clientes (1.1) | Mantido `count(DISTINCT)` (approx_distinct não funciona) | —                                       |
| Total Testes (1.3)   | Mantido `count()` (já é leve)                            | —                                       |
| Dashboard            | Período padrão: 7 dias                                   | Menos dados na memória                  |

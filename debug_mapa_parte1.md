# Debug: Queries do Mapa da Parte 1

Rode essas queries no QuestDB para descobrir por que o mapa ficou vazio.

---

## Query de Servidores (exatamente como está no JSON)

```sql
SELECT
    s.latitude AS lat,
    s.longitude AS lon,
    s.server_ip,
    d.server_site,
    s.country_name,
    s.city,
    count() AS total_testes,
    count(DISTINCT d.client_ip) AS clientes_unicos
FROM download d
JOIN server s ON d.server_ip = s.server_ip
WHERE d.test_time > dateadd('d', -30, now())
    AND s.country_code = 'BR'
    AND s.latitude IS NOT NULL
    AND s.longitude IS NOT NULL
GROUP BY s.latitude, s.longitude, s.server_ip, d.server_site, s.country_name, s.city;
```

---

## Query de Clientes (exatamente como está no JSON)

```sql
SELECT
    c.latitude AS lat,
    c.longitude AS lon,
    c.city,
    c.country_name,
    d.server_site,
    count() AS total_testes,
    count(DISTINCT d.client_ip) AS clientes_unicos
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE d.test_time > dateadd('d', -30, now())
    AND c.country_code = 'BR'
    AND c.latitude IS NOT NULL
    AND c.longitude IS NOT NULL
GROUP BY c.latitude, c.longitude, c.city, c.country_name, d.server_site;
```

---

## Teste simplificado: servidores usados no período

```sql
SELECT
    d.server_site,
    d.server_ip,
    count() AS total_testes
FROM download d
WHERE d.test_time > dateadd('d', -30, now())
GROUP BY d.server_site, d.server_ip
ORDER BY total_testes DESC
LIMIT 10;
```

---

## Teste: existe `country_code` na tabela `server`?

```sql
SELECT country_code, count() AS total
FROM server
GROUP BY country_code
ORDER BY total DESC
LIMIT 10;
```

---

## Teste: existe `country_code` na tabela `client`?

```sql
SELECT country_code, count() AS total
FROM client
GROUP BY country_code
ORDER BY total DESC
LIMIT 10;
```

---

## Possíveis causas do mapa vazio

1. **Filtro `country_code = 'BR'` não encontra nada** porque a coluna está vazia ou tem outro formato (ex: `BRA`, `Brasil`, `null`).
2. **JOIN `download` ↔ `server` falha** porque `server_ip` não bate entre as tabelas.
3. **Colunas `latitude`/`longitude` estão nulas** na tabela `server`.
4. **A query de servidores retorna dados, mas o Grafana não consegue plotar** porque falta algum campo obrigatório.

Me manda o resultado dessas queries que a gente ajusta.

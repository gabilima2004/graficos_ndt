# Validação: Quais servidores os clientes brasileiros realmente usam?

Use essas queries no QuestDB para entender por que o mapa mostra servidores no mundo todo.

---

## 1. Todos os servidores cadastrados na tabela `server`

```sql
SELECT
    s.server_site,
    s.server_ip,
    s.city,
    s.country_name,
    s.country_code,
    s.latitude,
    s.longitude
FROM server s
ORDER BY s.country_name, s.city;
```

---

## 2. Servidores realmente usados em testes de download nos últimos 30 dias

```sql
SELECT
    d.server_site,
    d.server_ip,
    count() AS total_testes,
    count(DISTINCT d.client_ip) AS clientes_unicos
FROM download d
WHERE d.test_time > dateadd('d', -30, now())
GROUP BY d.server_site, d.server_ip
ORDER BY total_testes DESC;
```

---

## 3. Servidores usados por clientes brasileiros nos últimos 30 dias (com localização)

```sql
SELECT
    d.server_site,
    d.server_ip,
    s.city,
    s.country_name,
    s.country_code,
    s.latitude,
    s.longitude,
    count() AS total_testes,
    count(DISTINCT d.client_ip) AS clientes_unicos
FROM download d
JOIN server s ON d.server_ip = s.server_ip
WHERE d.test_time > dateadd('d', -30, now())
GROUP BY d.server_site, d.server_ip, s.city, s.country_name, s.country_code, s.latitude, s.longitude
ORDER BY total_testes DESC;
```

---

## 4. Quantos testes foram para servidores fora do Brasil?

```sql
SELECT
    CASE WHEN s.country_code = 'BR' THEN 'Brasil' ELSE 'Exterior' END AS local,
    count() AS total_testes,
    count(DISTINCT d.client_ip) AS clientes_unicos,
    round(100.0 * count() / sum(count()) OVER (), 2) AS percentual_testes
FROM download d
JOIN server s ON d.server_ip = s.server_ip
WHERE d.test_time > dateadd('d', -30, now())
GROUP BY CASE WHEN s.country_code = 'BR' THEN 'Brasil' ELSE 'Exterior' END;
```

---

## 5. Países dos servidores usados pelos clientes brasileiros

```sql
SELECT
    s.country_name,
    s.country_code,
    count() AS total_testes,
    count(DISTINCT d.client_ip) AS clientes_unicos
FROM download d
JOIN server s ON d.server_ip = s.server_ip
WHERE d.test_time > dateadd('d', -30, now())
GROUP BY s.country_name, s.country_code
ORDER BY total_testes DESC;
```

---

## 6. Servidores cadastrados mas NUNCA usados nos últimos 30 dias

```sql
SELECT
    s.server_site,
    s.server_ip,
    s.city,
    s.country_name,
    s.country_code
FROM server s
LEFT JOIN (
    SELECT DISTINCT server_ip
    FROM download
    WHERE test_time > dateadd('d', -30, now())
) d ON s.server_ip = d.server_ip
WHERE d.server_ip IS NULL
ORDER BY s.country_name, s.city;
```

---

## O que observar

- Se a query 1 mostrar muitos países e a query 5 mostrar só Brasil, o problema é a query do mapa.
- Se a query 5 mostrar países fora do Brasil, os clientes brasileiros realmente medem para servidores no exterior.
- Se a query 6 mostrar muitos servidores "nunca usados", a tabela `server` tem lixo.

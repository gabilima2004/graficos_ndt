# Validação: Número de Clientes e Distribuição por País

Use essas queries no QuestDB para verificar se o número de 467.400 clientes faz sentido.

---

## 1. Total de clientes cadastrados na tabela `client`

```sql
SELECT count(DISTINCT client_ip) AS total_clientes_cadastrados
FROM client;
```

---

## 2. Clientes únicos que fizeram teste nos últimos 30 dias

```sql
SELECT count(DISTINCT d.client_ip) AS clientes_ativos_30d
FROM download d
WHERE d.test_time > dateadd('d', -30, now());
```

---

## 3. Clientes únicos por país (tabela `client` completa)

```sql
SELECT
    c.country_name,
    c.country_code,
    count(DISTINCT c.client_ip) AS total_clientes
FROM client c
GROUP BY c.country_name, c.country_code
ORDER BY total_clientes DESC;
```

---

## 4. Clientes únicos por país que fizeram download nos últimos 30 dias

```sql
SELECT
    c.country_name,
    c.country_code,
    count(DISTINCT d.client_ip) AS clientes_ativos
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE d.test_time > dateadd('d', -30, now())
GROUP BY c.country_name, c.country_code
ORDER BY clientes_ativos DESC;
```

---

## 5. Total de testes e média por cliente (últimos 30 dias)

```sql
SELECT
    count(DISTINCT d.client_ip) AS clientes_unicos,
    count() AS total_testes,
    count() / count(DISTINCT d.client_ip) AS media_testes_por_cliente
FROM download d
WHERE d.test_time > dateadd('d', -30, now());
```

---

## 6. Distribuição: quantos testes cada cliente fez (últimos 30 dias)

```sql
SELECT testes_por_cliente, count() AS quantidade_clientes
FROM (
    SELECT client_ip, count() AS testes_por_cliente
    FROM download
    WHERE test_time > dateadd('d', -30, now())
    GROUP BY client_ip
)
GROUP BY testes_por_cliente
ORDER BY quantidade_clientes DESC
LIMIT 20;
```

---

## 7. Clientes por país + média de testes por cliente (últimos 30 dias)

```sql
SELECT
    c.country_name,
    c.country_code,
    count(DISTINCT d.client_ip) AS clientes_unicos,
    count() AS total_testes,
    count() / count(DISTINCT d.client_ip) AS media_testes_por_cliente
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE d.test_time > dateadd('d', -30, now())
GROUP BY c.country_name, c.country_code
ORDER BY clientes_unicos DESC;
```

---

## O que observar

- Se a query 1 der um número muito maior que a query 2, significa que a base tem muitos clientes "fantasmas" (cadastrados mas sem teste recente).
- Se a query 4 mostrar países fora do Brasil, o mapa mundial faz sentido.
- Se a query 6 mostrar clientes com milhares de testes, pode ser robô, servidor de teste automatizado ou NAT corporativo.
- Se `client_ip` não for único por pessoa física (CGNAT, rede corporativa, etc.), o número de "clientes" vai estar inflacionado.

# Painel 1 — Clientes | Queries para Grafana + QuestDB

> **Banco:** QuestDB  
> **Plugin Grafana:** PostgreSQL Data Source (QuestDB é compatível com o protocolo PostgreSQL)  
> **Tabela base:** `download` (pode ser adaptada para `upload` ou ambas)

---

## 0. Variável de Dashboard — Filtro por ISP

Antes de criar os painéis, precisamos criar uma **variável no Grafana** para o filtro de ISP.

### Como criar:

1. Vá em **Dashboard Settings → Variables → Add variable**
2. Configure:
   - **Name:** `isp`
   - **Type:** Query
   - **Data source:** seu QuestDB
   - **Query:**

```sql
SELECT DISTINCT as_name AS __text, as_name AS __value
FROM client
ORDER BY as_name
```

> **Explicação:** Esta query busca todos os provedores únicos (AS names) da tabela `client`.  
> O formato `__text` / `__value` permite que o Grafana mostre o nome amigável no dropdown.  
> Marque a opção **"Include All option"** para permitir selecionar todos os provedores de uma vez.

### Como usar a variável nas queries:

- Para filtro de seleção única: `AND c.as_name = '$isp'`
- Para permitir "All" (múltiplos): `AND c.as_name IN ($isp)`

> **Dica:** Use `IN ($isp)` — quando o usuário seleciona "All", o Grafana expande para todos os valores automaticamente.

---

## 1. Total de Clientes Únicos que Realizaram Testes

**Tipo de painel:** Stat  
**Descrição:** Mostra o número de clientes distintos (por IP) que fizeram pelo menos um teste.

```sql
SELECT count(DISTINCT client_ip) AS total_clientes
FROM download
WHERE $__timeFilter(test_time)
```

### Entendendo a query:

| Parte                            | O que faz                                                            |
| -------------------------------- | -------------------------------------------------------------------- |
| `count(DISTINCT client_ip)`      | Conta IPs únicos — se o mesmo IP fez 10 testes, conta como 1 cliente |
| `FROM download`                  | Usa a tabela de testes de download como base                         |
| `WHERE $__timeFilter(test_time)` | Filtra pelo período selecionado no dashboard (macro do Grafana)      |

> **Pergunta para refletir:** Por que usamos `DISTINCT`? O que aconteceria se usássemos apenas `count(client_ip)`?  
> **Resposta:** Sem `DISTINCT`, contaríamos o **número de testes**, não o número de **clientes**. Um cliente que fez 50 testes seria contado 50 vezes.

### Variação — Incluindo upload também:

Se você quiser contar clientes que fizeram **qualquer** teste (download OU upload):

```sql
SELECT count(DISTINCT client_ip) AS total_clientes
FROM (
    SELECT client_ip FROM download WHERE $__timeFilter(test_time)
    UNION
    SELECT client_ip FROM upload WHERE $__timeFilter(test_time)
)
```

> **Atenção:** O `UNION` (sem `ALL`) já remove duplicatas automaticamente entre as duas tabelas.

---

## 2. Localização dos Clientes (Mapa)

**Tipo de painel:** Geomap  
**Descrição:** Mostra no mapa de onde os clientes estão testando.

```sql
SELECT
    c.latitude AS lat,
    c.longitude AS lon,
    c.client_ip,
    c.as_name,
    c.country_name,
    c.city,
    count() AS total_testes
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE $__timeFilter(d.test_time)
    AND c.as_name IN ($isp)
    AND c.latitude IS NOT NULL
    AND c.longitude IS NOT NULL
GROUP BY c.latitude, c.longitude, c.client_ip, c.as_name, c.country_name, c.city
```

### Entendendo a query:

| Parte                                        | O que faz                                                                          |
| -------------------------------------------- | ---------------------------------------------------------------------------------- |
| `JOIN client c ON d.client_ip = c.client_ip` | Traz a geolocalização da tabela `client` para os resultados dos testes             |
| `c.latitude AS lat, c.longitude AS lon`      | Coordenadas que o Geomap usa para posicionar os pontos                             |
| `count() AS total_testes`                    | Conta quantos testes cada cliente fez — pode ser usado para o tamanho/cor do ponto |
| `GROUP BY ...`                               | Agrupa por cliente único para não duplicar pontos no mapa                          |
| `c.latitude IS NOT NULL`                     | Remove clientes sem geolocalização válida                                          |
| `c.as_name IN ($isp)`                        | Aplica o filtro de ISP                                                             |

### Configuração do Geomap no Grafana:

1. **Location data:** Coords (latitude/longitude)
2. **Latitude field:** `lat`
3. **Longitude field:** `lon`
4. **Layers → Marker size:** `total_testes` (pontos maiores = mais testes)
5. **Tooltip:** mostrar `client_ip`, `city`, `country_name`, `as_name`, `total_testes`

> **Ponto de atenção:** A tabela `client` pode ter **múltiplas entradas** para o mesmo `client_ip` (atualizações ao longo do tempo com `update_time`). Se isso acontecer, o JOIN pode gerar duplicatas.  
> **Solução se necessário:** Usar `ASOF JOIN` para pegar a entrada mais recente:
>
> ```sql
> -- Alternativa com ASOF JOIN (pega a info mais recente do cliente)
> SELECT
>     c.latitude AS lat,
>     c.longitude AS lon,
>     d.client_ip,
>     c.as_name,
>     count() AS total_testes
> FROM download d
> ASOF JOIN client c ON d.client_ip = c.client_ip
> WHERE $__timeFilter(d.test_time)
>     AND c.as_name IN ($isp)
> GROUP BY c.latitude, c.longitude, d.client_ip, c.as_name
> ```
>
> O `ASOF JOIN` do QuestDB encontra o registro mais próximo **anterior** ao timestamp do teste — ideal para séries temporais.

---

## 3. Clientes por Provedor (ISP)

**Tipo de painel:** Bar Chart (gráfico de barras)  
**Descrição:** Mostra quantos clientes únicos cada provedor tem.

```sql
SELECT
    c.as_name AS provedor,
    count(DISTINCT d.client_ip) AS total_clientes
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE $__timeFilter(d.test_time)
    AND c.as_name IN ($isp)
GROUP BY c.as_name
ORDER BY total_clientes DESC
LIMIT 20
```

### Entendendo a query:

| Parte                          | O que faz                                           |
| ------------------------------ | --------------------------------------------------- |
| `count(DISTINCT d.client_ip)`  | Conta clientes únicos por provedor                  |
| `GROUP BY c.as_name`           | Agrupa os resultados por nome do provedor           |
| `ORDER BY total_clientes DESC` | Ordena do maior para o menor                        |
| `LIMIT 20`                     | Mostra apenas os 20 maiores (evita gráfico poluído) |

> **Pergunta para refletir:** Por que `LIMIT 20`? O que acontece se houver 500 provedores?  
> **Resposta:** Um gráfico de barras com 500 barras fica ilegível. O `LIMIT` mantém o dashboard limpo. Você pode ajustar esse número conforme a necessidade.

### Variação — Como tabela (alternativa ao gráfico de barras):

Se preferir uma tabela com mais informações:

```sql
SELECT
    c.as_name AS provedor,
    c.asn AS asn,
    count(DISTINCT d.client_ip) AS total_clientes,
    count() AS total_testes
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE $__timeFilter(d.test_time)
    AND c.as_name IN ($isp)
GROUP BY c.as_name, c.asn
ORDER BY total_clientes DESC
```

> Aqui adicionamos `c.asn` (número) e `count()` (total de testes) para dar mais contexto.

---

## 4. Bônus — Clientes por País/Região

**Tipo de painel:** Pie Chart ou Bar Chart  
**Descrição:** Mostra de quais países/regiões vêm os clientes.

```sql
SELECT
    c.country_name AS pais,
    count(DISTINCT d.client_ip) AS total_clientes
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE $__timeFilter(d.test_time)
    AND c.as_name IN ($isp)
GROUP BY c.country_name
ORDER BY total_clientes DESC
LIMIT 15
```

> **Sugestão:** Você pode duplicar esta query trocando `country_name` por `region` ou `city` para ter visões mais granulares.

---

## 5. Resumo — Estrutura do Painel 1

```
┌─────────────────────────────────────────────────────┐
│                   PAINEL: CLIENTES                   │
│                                                      │
│  [Filtro ISP: ▼ All]  [Período: ▼ Last 7 days]      │
│                                                      │
│  ┌──────────────┐  ┌──────────────────────────────┐ │
│  │ Total        │  │      Mapa de Clientes        │ │
│  │ Clientes     │  │      (Geomap)                │ │
│  │ (Stat)       │  │                              │ │
│  └──────────────┘  └──────────────────────────────┘ │
│                                                      │
│  ┌─────────────────────┐  ┌───────────────────────┐ │
│  │ Clientes por ISP    │  │ Clientes por País     │ │
│  │ (Bar Chart)         │  │ (Pie/Bar Chart)       │ │
│  └─────────────────────┘  └───────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

---

## 6. Notas Importantes sobre QuestDB + Grafana

### Macro `$__timeFilter`:

O `$__timeFilter(test_time)` é uma macro do plugin PostgreSQL do Grafana. Ela é substituída automaticamente por algo como:

```sql
test_time >= '2026-08-05T00:00:00' AND test_time <= '2026-08-12T00:00:00'
```

baseado no seletor de período do dashboard.

### Performance:

- QuestDB é **muito rápido** para queries de séries temporais com `SAMPLE BY`
- JOINs podem ser mais lentos em tabelas grandes — se notar lentidão, considere:
  - Usar `ASOF JOIN` em vez de `JOIN` regular
  - Adicionar filtros de tempo mais restritos
  - Usar `LIMIT` para reduzir o volume de dados

### Sobre o `count()` no QuestDB:

No QuestDB, `count()` sem argumentos conta todas as linhas (equivalente a `count(*)` em outros bancos).

---

## 7. Próximos Passos

1. ✅ Criar a variável `isp` no dashboard
2. ✅ Criar o painel Stat (total de clientes)
3. ✅ Criar o painel Geomap (localização)
4. ✅ Criar o painel Bar Chart (clientes por provedor)
5. ✅ Criar o painel Pie/Bar Chart (clientes por país)
6. 🔲 Testar as queries no QuestDB antes de colocar no Grafana
7. 🔲 Ajustar o layout e cores dos painéis

> **Dica de professor:** Sempre teste suas queries diretamente no console do QuestDB (geralmente na porta 9000) antes de colocá-las no Grafana. Assim você consegue ver os dados e validar se a query está correta!

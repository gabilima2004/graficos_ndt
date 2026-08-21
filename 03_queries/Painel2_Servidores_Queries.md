# Painel 2 — Servidores | Queries para Grafana + QuestDB

> **Banco:** QuestDB  
> **Plugin Grafana:** QuestDB Data Source  
> **Tabelas base:** `server`, `download`, `upload`, `client`

---

## Visão geral do painel

```
┌─────────────────────────────────────────────────────────┐
│                  PAINEL: SERVIDORES                      │
│                                                          │
│  [Filtro ISP: ▼ All]  [Período: ▼ Last 7 days]          │
│                                                          │
│  ┌──────────────┐  ┌──────────────────────────────────┐ │
│  │ Total        │  │    Mapa Servidores + Clientes    │ │
│  │ Servidores   │  │    (Geomap com 2 camadas)        │ │
│  │ (Stat)       │  │                                  │ │
│  └──────────────┘  └──────────────────────────────────┘ │
│                                                          │
│  ┌─────────────────────────┐  ┌───────────────────────┐ │
│  │ Clientes por Servidor   │  │ Localização Servidores │ │
│  │ (Bar Chart)             │  │ (Tabela)              │ │
│  └─────────────────────────┘  └───────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## 1. Total de Servidores (Stat)

**Tipo de painel:** Stat

```sql
SELECT count(DISTINCT server_ip) AS total_servidores
FROM server
```

> **Pergunta para refletir:** Por que `count(DISTINCT server_ip)` e não `count()`?  
> **Resposta:** A tabela `server` pode ter múltiplas entradas para o mesmo IP (atualizações com `update_time`). O `DISTINCT` garante que cada servidor seja contado uma vez.

---

## 2. Mapa — Servidores + Clientes (Geomap com 2 camadas)

**Tipo de painel:** Geomap  
**Descrição:** Mostra servidores e clientes no mesmo mapa. Clientes coloridos pelo servidor que testaram.

### Camada 1 — Servidores (pontos maiores, cor fixa)

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

### Camada 2 — Clientes (pontos menores, cor por servidor)

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
    AND c.latitude IS NOT NULL
    AND c.longitude IS NOT NULL
GROUP BY c.latitude, c.longitude, c.client_ip, d.server_ip, d.server_site, c.city, c.country_name
```

### Configuração do Geomap no Grafana:

**Camada 1 — Servidores:**

1. Adicione uma nova layer → tipo **Markers**
2. **Display name:** `Servidores`
3. **Location:** Coords → lat = `lat`, lon = `lon`
4. **Style → Color:** Fixed → `blue` (ou outra cor de destaque)
5. **Style → Size:** Fixed → `10` (pontos maiores)
6. **Style → Symbol:** `img/icons/marker/circle.svg`
7. **Tooltip:** mostrar `server_ip`, `site`, `city`, `server_isp`

**Camada 2 — Clientes:**

1. Adicione outra layer → tipo **Markers**
2. **Display name:** `Clientes`
3. **Location:** Coords → lat = `lat`, lon = `lon`
4. **Style → Color:** mode = `Value` → field = `server_ip`
   - Color scheme: `Palette classic` (cada servidor = uma cor)
5. **Style → Size:** mode = `Value` → field = `total_testes` → min 2, max 8
6. **Style → Symbol:** `img/icons/marker/circle.svg`
7. **Tooltip:** mostrar `client_ip`, `server_ip`, `server_site`, `city`, `total_testes`

> **Conceito-chave:** Ao colorir os clientes pelo `server_ip`, todos os clientes que testaram contra o mesmo servidor ficam da mesma cor. Isso permite ver geograficamente qual área cada servidor atende.

---

## 3. Clientes por Servidor (Bar Chart)

**Tipo de painel:** Bar Chart  
**Descrição:** Quantos clientes únicos cada servidor atendeu.

```sql
SELECT
    d.server_site AS servidor,
    count(DISTINCT d.client_ip) AS total_clientes
FROM download d
WHERE $__timeFilter(d.test_time)
GROUP BY d.server_site
ORDER BY total_clientes DESC
```

> **Pergunta para refletir:** Por que agrupar por `server_site` e não `server_ip`?  
> **Resposta:** `server_site` é o nome da localização (ex: "sao-paulo", "rio-de-janeiro") — mais legível que um IP. Se preferir, pode trocar por `server_ip` ou combinar os dois.

### Variação — Com mais detalhes (tabela):

```sql
SELECT
    d.server_site AS site,
    d.server_ip AS ip,
    count(DISTINCT d.client_ip) AS total_clientes,
    count() AS total_testes
FROM download d
WHERE $__timeFilter(d.test_time)
GROUP BY d.server_site, d.server_ip
ORDER BY total_clientes DESC
```

---

## 4. Localização dos Servidores (Tabela)

**Tipo de painel:** Table  
**Descrição:** Lista todos os servidores com sua localização.

```sql
SELECT
    s.site,
    s.machine,
    s.server_ip,
    s.country_name,
    s.region,
    s.city,
    s.as_name AS isp,
    s.machine_zone,
    s.machine_type
FROM server s
ORDER BY s.site, s.machine
```

> Esta query não tem filtro de tempo porque a tabela `server` é cadastral (não tem `test_time`).

---

## 5. Bônus — Testes por Servidor ao longo do tempo (Time Series)

**Tipo de painel:** Time Series  
**Descrição:** Volume de testes por servidor ao longo do tempo.

```sql
SELECT
    $__timeGroup(d.test_time, '5m') AS time,
    d.server_site AS servidor,
    count() AS total_testes
FROM download d
WHERE $__timeFilter(d.test_time)
GROUP BY 1, 2
ORDER BY 1 ASC
```

> **Nota:** `$__timeGroup` é uma macro do Grafana que agrupa os dados em intervalos de tempo (neste caso, 5 minutos). Cada servidor vira uma linha no gráfico.

---

## 6. Resumo — Estrutura do Painel 2

| #   | Visualização        | Query                                            | O que mostra                                          |
| --- | ------------------- | ------------------------------------------------ | ----------------------------------------------------- |
| 1   | Stat                | `count(DISTINCT server_ip)`                      | Total de servidores                                   |
| 2   | Geomap (2 camadas)  | Servidores + Clientes                            | Mapa com servidores e clientes coloridos por servidor |
| 3   | Bar Chart           | `count(DISTINCT client_ip) GROUP BY server_site` | Clientes por servidor                                 |
| 4   | Table               | `SELECT * FROM server`                           | Lista de servidores                                   |
| 5   | Time Series (bônus) | `count() GROUP BY server_site, time`             | Volume de testes por servidor ao longo do tempo       |

---

## 7. Ordem de execução

1. ✅ Criar painel Stat (total de servidores)
2. ✅ Criar painel Geomap com 2 camadas (servidores + clientes)
3. ✅ Criar painel Bar Chart (clientes por servidor)
4. ✅ Criar painel Table (localização dos servidores)
5. ✅ Testar no Grafana

> **Dica de professor:** O Geomap com 2 camadas é a parte mais complexa. Configure primeiro a camada de servidores (pontos grandes, cor fixa) e depois adicione a camada de clientes (pontos pequenos, cor por servidor). Assim você isola possíveis erros.

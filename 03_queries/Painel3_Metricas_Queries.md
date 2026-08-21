# Painel 3 — Métricas | Queries para Grafana + QuestDB

> **Banco:** QuestDB  
> **Plugin Grafana:** QuestDB Data Source  
> **Tabelas base:** `download`, `upload`, `client`

---

## Visão geral do painel

```
┌─────────────────────────────────────────────────────────┐
│                   PAINEL: MÉTRICAS                       │
│                                                          │
│  [Filtro ISP: ▼ All]  [Período: ▼ Last 7 days]          │
│                                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │ Download │ │ Upload   │ │ RTT      │ │ Loss     │    │
│  │ Médio    │ │ Médio    │ │ Médio    │ │ Rate     │    │
│  │ (Stat)  │ │ (Stat)  │ │ (Stat)  │ │ (Stat)  │    │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │
│                                                          │
│  ┌────────────────────────┐  ┌────────────────────────┐ │
│  │ Download por Servidor  │  │ Upload por Servidor    │ │
│  │ (Bar Chart)            │  │ (Bar Chart)            │ │
│  └────────────────────────┘  └────────────────────────┘ │
│                                                          │
│  ┌────────────────────────┐  ┌────────────────────────┐ │
│  │ RTT por Servidor       │  │ Loss Rate por Servidor │ │
│  │ (Bar Chart)            │  │ (Bar Chart)            │ │
│  └────────────────────────┘  └────────────────────────┘ │
│                                                          │
│  ┌──────────────────────────────────────────────────────┐│
│  │  Download ao longo do tempo (Time Series)            ││
│  └──────────────────────────────────────────────────────┘│
│  ┌──────────────────────────────────────────────────────┐│
│  │  Upload ao longo do tempo (Time Series)               ││
│  └──────────────────────────────────────────────────────┘│
│  ┌──────────────────────────────────────────────────────┐│
│  │  RTT ao longo do tempo (Time Series)                  ││
│  └──────────────────────────────────────────────────────┘│
│  ┌──────────────────────────────────────────────────────┐│
│  │  Loss Rate ao longo do tempo (Time Series)            ││
│  └──────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

---

## 1. Velocidade Média Geral — Download (Stat)

```sql
SELECT avg(mean_throughput_mbps) AS download_medio_mbps
FROM download
WHERE $__timeFilter(test_time)
```

---

## 2. Velocidade Média Geral — Upload (Stat)

```sql
SELECT avg(mean_throughput_mbps) AS upload_medio_mbps
FROM upload
WHERE $__timeFilter(test_time)
```

---

## 3. Min RTT Médio Geral (Stat)

```sql
SELECT avg(min_rtt) AS rtt_medio_ms
FROM download
WHERE $__timeFilter(test_time)
```

> **Pergunta para refletir:** Por que usar a tabela `download` para o RTT e não `upload`?  
> **Resposta:** Ambas têm `min_rtt`. Você pode usar qualquer uma, ou até combinar com `UNION`. O RTT é medido em ambos os testes, mas geralmente é similar. Se quiser ser mais preciso, pode fazer a média das duas tabelas.

### Variação — RTT combinando download e upload:

```sql
SELECT avg(min_rtt) AS rtt_medio_ms
FROM (
    SELECT min_rtt FROM download WHERE $__timeFilter(test_time)
    UNION ALL
    SELECT min_rtt FROM upload WHERE $__timeFilter(test_time)
)
```

---

## 4. Loss Rate Médio Geral (Stat)

```sql
SELECT avg(loss_rate) AS loss_rate_medio
FROM download
WHERE $__timeFilter(test_time)
```

> **Dica de exibição:** No Grafana, configure o **Unit** deste painel para `percentunit` (0.0-1.0 → 0%-100%). Assim o valor `0.02` aparece como `2%`.

---

## 5. Velocidade Média por Servidor — Download (Bar Chart)

```sql
SELECT
    server_site AS servidor,
    avg(mean_throughput_mbps) AS download_medio_mbps
FROM download
WHERE $__timeFilter(test_time)
GROUP BY server_site
ORDER BY download_medio_mbps DESC
```

---

## 6. Velocidade Média por Servidor — Upload (Bar Chart)

```sql
SELECT
    server_site AS servidor,
    avg(mean_throughput_mbps) AS upload_medio_mbps
FROM upload
WHERE $__timeFilter(test_time)
GROUP BY server_site
ORDER BY upload_medio_mbps DESC
```

---

## 7. Min RTT Médio por Servidor (Bar Chart)

```sql
SELECT
    server_site AS servidor,
    avg(min_rtt) AS rtt_medio_ms
FROM download
WHERE $__timeFilter(test_time)
GROUP BY server_site
ORDER BY rtt_medio_ms ASC
```

> **Atenção:** Aqui ordenamos por `ASC` (menor RTT primeiro) — menor RTT é melhor. Nos gráficos de throughput, ordenamos por `DESC` (maior velocidade primeiro).

---

## 8. Loss Rate Médio por Servidor (Bar Chart)

```sql
SELECT
    server_site AS servidor,
    avg(loss_rate) AS loss_rate_medio
FROM download
WHERE $__timeFilter(test_time)
GROUP BY server_site
ORDER BY loss_rate_medio ASC
```

> **Atenção:** Menor loss rate é melhor, por isso `ASC`. Configure o Unit para `percentunit`.

---

## 9. Download ao longo do tempo (Time Series)

```sql
SELECT
    $__timeGroup(test_time, '5m') AS time,
    avg(mean_throughput_mbps) AS download_mbps
FROM download
WHERE $__timeFilter(test_time)
GROUP BY 1
ORDER BY 1 ASC
```

### Variação — Colorir por servidor:

```sql
SELECT
    $__timeGroup(test_time, '5m') AS time,
    server_site AS servidor,
    avg(mean_throughput_mbps) AS download_mbps
FROM download
WHERE $__timeFilter(test_time)
GROUP BY 1, 2
ORDER BY 1 ASC
```

> Quando você adiciona a coluna `servidor` no SELECT, o Grafana cria uma linha para cada servidor no gráfico de séries temporais.

---

## 10. Upload ao longo do tempo (Time Series)

```sql
SELECT
    $__timeGroup(test_time, '5m') AS time,
    avg(mean_throughput_mbps) AS upload_mbps
FROM upload
WHERE $__timeFilter(test_time)
GROUP BY 1
ORDER BY 1 ASC
```

### Variação — Colorir por servidor:

```sql
SELECT
    $__timeGroup(test_time, '5m') AS time,
    server_site AS servidor,
    avg(mean_throughput_mbps) AS upload_mbps
FROM upload
WHERE $__timeFilter(test_time)
GROUP BY 1, 2
ORDER BY 1 ASC
```

---

## 11. RTT ao longo do tempo (Time Series)

```sql
SELECT
    $__timeGroup(test_time, '5m') AS time,
    avg(min_rtt) AS rtt_ms
FROM download
WHERE $__timeFilter(test_time)
GROUP BY 1
ORDER BY 1 ASC
```

### Variação — Colorir por servidor:

```sql
SELECT
    $__timeGroup(test_time, '5m') AS time,
    server_site AS servidor,
    avg(min_rtt) AS rtt_ms
FROM download
WHERE $__timeFilter(test_time)
GROUP BY 1, 2
ORDER BY 1 ASC
```

---

## 12. Loss Rate ao longo do tempo (Time Series)

```sql
SELECT
    $__timeGroup(test_time, '5m') AS time,
    avg(loss_rate) AS loss_rate
FROM download
WHERE $__timeFilter(test_time)
GROUP BY 1
ORDER BY 1 ASC
```

### Variação — Colorir por servidor:

```sql
SELECT
    $__timeGroup(test_time, '5m') AS time,
    server_site AS servidor,
    avg(loss_rate) AS loss_rate
FROM download
WHERE $__timeFilter(test_time)
GROUP BY 1, 2
ORDER BY 1 ASC
```

---

## 13. Bônus — Tabela resumo por servidor (Table)

**Tipo de painel:** Table  
**Descrição:** Tabela com todas as métricas agrupadas por servidor.

```sql
SELECT
    server_site AS site,
    count() AS total_testes,
    count(DISTINCT client_ip) AS clientes_unicos,
    round(avg(mean_throughput_mbps), 2) AS download_medio_mbps,
    round(avg(min_rtt), 2) AS rtt_medio_ms,
    round(avg(loss_rate), 4) AS loss_rate_medio
FROM download
WHERE $__timeFilter(test_time)
GROUP BY server_site
ORDER BY total_testes DESC
```

> **Nota:** O `round()` arredonda os valores para facilitar a leitura.
>
> - Throughput: 2 casas decimais (ex: 45.23 Mbps)
> - RTT: 2 casas decimais (ex: 25.50 ms)
> - Loss rate: 4 casas decimais (ex: 0.0023 = 0.23%)

---

## 14. Configurações do Grafana — Units

| Métrica                      | Unit no Grafana         | Formato    |
| ---------------------------- | ----------------------- | ---------- |
| Throughput (download/upload) | `Mbps` ou `Mbits/sec`   | 45.23 Mbps |
| RTT (min_rtt)                | `ms` ou `milliseconds`  | 25.50 ms   |
| Loss Rate                    | `percentunit` (0.0-1.0) | 2.3%       |

> **Dica de professor:** Configurar as units corretas é fundamental. Sem isso, o Grafana mostra números "crus" que podem confundir quem lê o dashboard. Por exemplo, loss rate de `0.02` sem unit parece pequeno, mas com `percentunit` mostra `2%` — muito mais claro!

---

## 15. Resumo — Estrutura do Painel 3

| #   | Visualização  | Métrica                     | Tabela   |
| --- | ------------- | --------------------------- | -------- |
| 1   | Stat          | Download médio geral        | download |
| 2   | Stat          | Upload médio geral          | upload   |
| 3   | Stat          | RTT médio geral             | download |
| 4   | Stat          | Loss rate médio geral       | download |
| 5   | Bar Chart     | Download por servidor       | download |
| 6   | Bar Chart     | Upload por servidor         | upload   |
| 7   | Bar Chart     | RTT por servidor            | download |
| 8   | Bar Chart     | Loss rate por servidor      | download |
| 9   | Time Series   | Download ao longo do tempo  | download |
| 10  | Time Series   | Upload ao longo do tempo    | upload   |
| 11  | Time Series   | RTT ao longo do tempo       | download |
| 12  | Time Series   | Loss rate ao longo do tempo | download |
| 13  | Table (bônus) | Resumo por servidor         | download |

---

## 16. Ordem de execução

1. ✅ Criar os 4 painéis Stat (métricas gerais)
2. ✅ Criar os 4 painéis Bar Chart (métricas por servidor)
3. ✅ Criar os 4 painéis Time Series (métricas ao longo do tempo)
4. ✅ Criar a tabela resumo (bônus)
5. ✅ Configurar as Units corretas em cada painel
6. ✅ Testar no Grafana

> **Dica de professor:** Comece pelos painéis Stat (mais simples) para validar que as queries funcionam. Depois vá para os Bar Charts e por último os Time Series (que têm o `$__timeGroup` e são um pouco mais complexos).

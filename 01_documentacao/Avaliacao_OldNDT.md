# Avaliação do Dashboard Antigo (oldndt.md)

> Análise dos dashboards NDT anteriores para identificar boas práticas, problemas e ideias a aproveitar nos novos painéis.

---

## 1. Visão geral dos dashboards antigos

O arquivo contém **8 dashboards** diferentes, organizados em 3 seções:

### Seção: Big Query

| #   | Dashboard                       | Fonte de dados        | Descrição                                                                                 |
| --- | ------------------------------- | --------------------- | ----------------------------------------------------------------------------------------- |
| 1   | `NDT_7_Big_Query`               | BigQuery (PostgreSQL) | Dashboard principal com gráficos de download, upload, RTT, loss rate, box plots e tabelas |
| 2   | `NDT_7_Big_Query_tables_export` | BigQuery (PostgreSQL) | Dashboard simplificado com apenas uma tabela de exportação de testes                      |

### Seção: QuestDB

| #   | Dashboard              | Fonte de dados       | Descrição                                                                                                                                |
| --- | ---------------------- | -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| 3   | `Agrupado`             | QuestDB (PostgreSQL) | Dashboard agrupado por MAC — time series de download, upload, latência e loss rate, com tabelas de estatísticas (avg, min, max, mediana) |
| 4   | `Individual`           | QuestDB (PostgreSQL) | Dashboard individual por dispositivo (MAC) com time series, violin plots, estatísticas, agendamento e histograma                         |
| 5   | `Measurements Details` | QuestDB (PostgreSQL) | Detalhes de um teste específico (por test_uuid) com resumo e measurements                                                                |
| 6   | `Monitoramento e Logs` | QuestDB (PostgreSQL) | Monitoramento de dispositivos: online/offline, apagões, erros de aplicação e testes                                                      |

### Seção: Timescale

| #   | Dashboard                 | Fonte de dados           | Descrição                                                                             |
| --- | ------------------------- | ------------------------ | ------------------------------------------------------------------------------------- |
| 7   | `Measurements Details`    | TimescaleDB (PostgreSQL) | Mesmo dashboard de detalhes, mas em TimescaleDB                                       |
| 8   | `QuestDB` (monitoramento) | QuestDB (PostgreSQL)     | Dashboard de monitoramento de dispositivos com status, resumo de testes e agendamento |

---

## 2. Estrutura do dashboard principal (NDT_7_Big_Query)

### Painéis:

| #   | Tipo        | Título             | O que mostra                                                            |
| --- | ----------- | ------------------ | ----------------------------------------------------------------------- |
| 1   | Time Series | Download           | Throughput de download ao longo do tempo, colorido por provedor ou zona |
| 2   | Table       | Download dados     | Tabela com média, mínimo e máximo de download por servidor/zona         |
| 3   | Time Series | Upload             | Throughput de upload ao longo do tempo                                  |
| 4   | Table       | Upload dados       | Tabela com estatísticas de upload                                       |
| 5   | Time Series | Loss rate          | Taxa de perda de pacotes ao longo do tempo (escala log)                 |
| 6   | Time Series | RTT min            | RTT mínimo ao longo do tempo (escala log, filtro ≤ 1500000µs)           |
| 7   | Time Series | Duração dos testes | Duração em segundos (filtro ≤ 15000ms)                                  |
| 8   | Box Plot    | Download           | Box plot de download por provedor/zona (Plotly)                         |
| 9   | Violin Plot | Download           | Violin plot de download                                                 |
| 10  | Box Plot    | Upload             | Box plot de upload                                                      |
| 11  | Violin Plot | Upload             | Violin plot de upload                                                   |
| 12  | Box Plot    | RTT                | Box plot de RTT por zona                                                |
| 13  | Violin Plot | RTT                | Violin plot de RTT                                                      |

### Variáveis (filtros):

| Variável   | Tipo               | Descrição                                                |
| ---------- | ------------------ | -------------------------------------------------------- |
| `Provedor` | Custom (hardcoded) | Lista manual de 19 provedores                            |
| `Location` | Query              | Localizações filtradas por provedor                      |
| `OS`       | Query              | Clientes (sistemas) filtrados por provedor e localização |
| `Zone`     | Query              | Zonas filtradas por provedor, localização e OS           |

---

## 3. O que funciona bem (manter)

### ✅ Boas práticas identificadas:

1. **Filtros em cascata** — as variáveis se filtram entre si (Provedor → Location → OS → Zone). Isso é uma boa UX.

2. **Coloração condicional inteligente** — o `CASE WHEN '${Provedor:csv}' LIKE '%,%'` colore por provedor quando há múltiplos selecionados, e por zona quando só há um. Isso evita que todas as linhas fiquem da mesma cor.

3. **Filtros de outliers** — `min_rtt <= 1500000` e `duration_ms <= 15000` removem valores absurdos que distorcem os gráficos.

4. **Escala logarítmica** — loss rate e RTT usam escala log (`scaleDistribution: { type: "log", log: 2 }`) porque esses valores variam várias ordens de grandeza.

5. **Tabela com TOTAL GERAL** — usa `UNION ALL` para adicionar uma linha de total no final da tabela. Útil para visão consolidada.

6. **Box plots e violin plots** — ótimos para visualizar a distribuição dos dados, não só a média.

7. **Legendas com estatísticas** — as time series mostram mean, variance, p30, p50, p70, p90, p95, p99 na legenda. Muito rico.

8. **Units configuradas** — Mbps para throughput, µs para RTT, percentunit para loss rate, s para duração.

---

## 4. O que precisa melhorar (evitar)

### ❌ Problemas identificados:

1. **Provedores hardcoded** — a variável `Provedor` é do tipo `custom` com 19 valores digitados manualmente. Se um provedor novo aparecer, precisa editar o dashboard. **Solução:** usar query + CASE WHEN (como já fizemos).

2. **Variações de nome não normalizadas** — `Claro S/A` e `CLARO S.A.` aparecem como provedores separados. **Solução:** nosso mapeamento por ASN já resolve isso.

3. **Tabela única `tests_union_grafana_ht`** — o dashboard antigo usa uma tabela unificada com `test_type` ('download'/'upload'). No seu caso, são tabelas separadas (`download` e `upload`). **Solução:** adaptar as queries para usar as tabelas separadas.

4. **Sem mapa geográfico** — o dashboard antigo não tem Geomap. **Solução:** nosso Painel 1 e Painel 2 já incluem mapas.

5. **Sem visão de servidores** — não há painel dedicado aos servidores. **Solução:** nosso Painel 2 cobre isso.

6. **Filtros complexos demais** — 4 variáveis em cascata podem confundir. **Solução:** manter filtros essenciais (ISP + tempo).

7. **`COUNT(_)` em vez de `COUNT(*)`** — algumas queries usam `COUNT(_)` que não é SQL padrão. Funciona no BigQuery mas pode causar problemas em outros bancos.

---

## 5. Dashboard "Agrupado" (QuestDB) — Visão agrupada por dispositivo

Dashboard que mostra métricas de **múltiplos dispositivos** (MACs) ao mesmo tempo, com time series e tabelas de estatísticas.

### Painéis:

| #   | Tipo        | Título           | O que mostra                                                      |
| --- | ----------- | ---------------- | ----------------------------------------------------------------- |
| 1   | Time Series | Download         | Throughput de download ao longo do tempo, colorido por MAC        |
| 2   | Table       | Download dados   | Estatísticas por MAC: total de testes, avg, min, max, **mediana** |
| 3   | Time Series | Upload           | Throughput de upload ao longo do tempo, colorido por MAC          |
| 4   | Table       | Upload dados     | Estatísticas por MAC: total, avg, min, max, mediana               |
| 5   | Time Series | Latency Download | Latência de download ao longo do tempo, colorido por MAC          |
| 6   | Time Series | Latency Upload   | Latência de upload ao longo do tempo, colorido por MAC            |
| 7   | Time Series | Packet Loss      | Loss rate ao longo do tempo, colorido por MAC                     |

### Variáveis:

| Variável | Tipo               | Descrição                                                       |
| -------- | ------------------ | --------------------------------------------------------------- |
| `mac`    | Query (multi)      | Dispositivos com MAC + nome do dono, ordenados por nº de testes |
| `server` | Query (multi, All) | Servidores (IP + FQDN), ordenados por nº de testes              |

### Boas práticas encontradas:

1. **Agregação temporal manual** — usa `cast(cast(test_timestamp as long) / 300000 * 300000 as timestamp)` para agrupar em buckets de 5 minutos. É uma alternativa ao `SAMPLE BY` do QuestDB.

2. **Tabelas com mediana** — usa `approx_median(download_tp_bps, 0)` além de avg, min, max. Visão estatística completa.

3. **Coloração por MAC** — cada dispositivo tem sua cor nas time series, facilitando comparação.

4. **Thresholds na tabela** — a tabela de download tem thresholds de cor: vermelho < 50, amarelo 50-100, verde > 100 (em bps).

5. **Filtro de outlier** — `download_tp_bps >= 0` em todas as queries.

6. **Footer com soma** — as tabelas mostram o total de testes no rodapé (`show: true` no footer).

---

## 6. Dashboard "Individual" (QuestDB) — Análise por dispositivo

Este é o dashboard mais rico e interessante dos novos que você adicionou. Ele mostra dados de **um dispositivo específico** (filtrado por MAC).

### Painéis:

| #   | Tipo        | Título                    | O que mostra                                                                                |
| --- | ----------- | ------------------------- | ------------------------------------------------------------------------------------------- |
| 1   | Stat        | Status                    | Tempo desde último ping (Online/Offline com threshold de 300s)                              |
| 2   | Table       | Resume                    | Últimos 4 testes + próximo teste agendado                                                   |
| 3   | Stat        | General Statistics        | Testes no período, hoje, total histórico, recordes (maior download/upload, melhor latência) |
| 4   | Time Series | Tp. Download              | Throughput de download ao longo do tempo, com links para Measurements e Traceroute          |
| 5   | Violin Plot | Tp. Download Box Plot     | Densidade de download por servidor (Plotly)                                                 |
| 6   | Time Series | Latency Download          | Latência de download ao longo do tempo                                                      |
| 7   | Violin Plot | Latency Download Box Plot | Densidade de latência por servidor                                                          |
| 8   | Time Series | Tp. Upload                | Throughput de upload ao longo do tempo                                                      |
| 9   | Violin Plot | Tp. Upload Box Plot       | Densidade de upload por servidor                                                            |
| 10  | Time Series | Latency Upload            | Latência de upload ao longo do tempo                                                        |
| 11  | Violin Plot | Latency Upload Box Plot   | Densidade de latência de upload por servidor                                                |
| 12  | Time Series | Packet Loss               | Retransmissão ao longo do tempo                                                             |
| 13  | Violin Plot | Packet Loss Box Plot      | Densidade de perda por servidor                                                             |
| 14  | Bar Chart   | Median Between Servers    | Mediana de todas as métricas por servidor                                                   |
| 15  | Time Series | Ping Variation            | Variação de ping para diferentes destinos (com `SAMPLE BY 1m`)                              |
| 16  | Bar Chart   | Tests by Servers          | Total de testes por servidor                                                                |
| 17  | Time Series | Tests Schedules           | Testes agendados vs. realizados                                                             |
| 18  | Time Series | IP Variation              | Variação de IP do cliente ao longo do tempo                                                 |
| 19  | Histogram   | Exponential Distribution  | Distribuição de intervalos entre testes                                                     |

### Variáveis:

| Variável | Tipo  | Descrição                                                       |
| -------- | ----- | --------------------------------------------------------------- |
| `mac`    | Query | Dispositivos com MAC + nome do dono, ordenados por nº de testes |
| `server` | Query | Servidores (IP + FQDN), ordenados por nº de testes              |

### Boas práticas encontradas:

1. **Links entre dashboards** — cada ponto no gráfico tem link para "Measurements Details" e "Traceroute" passando o `test_uuid`. Navegação rica entre dashboards.

2. **Violin plots com cores temáticas** — cada métrica tem sua cor:
   - Download: roxo (`#8e44ad`)
   - Upload: laranja (`#e67e22`)
   - Latência Download: azul (`#33a2e5`)
   - Latência Upload: verde (`#2ecc71`)
   - Packet Loss: vermelho (`#e74c3c`)

3. **Mediana em vez de média** — usa `approx_median()` que é mais robusto que `avg()` contra outliers.

4. **Filtros de outlier** — `download_tp_bps >= 0 AND < 1e9`, `latency >= 0`, `retrans >= 0`.

5. **`SAMPLE BY 1m`** — o painel de ping usa `SAMPLE BY 1m ALIGN TO CALENDAR` (recurso nativo do QuestDB).

6. **Status Online/Offline** — usa threshold de 300s (5 min) desde o último ping, com mapeamento de cor (verde = online, vermelho = offline).

7. **Distribuição exponencial** — histograma dos intervalos entre testes, mostrando o padrão de agendamento.

8. **Conversão de unidades no Plotly** — os violin plots convertem bps → Mbps no script JavaScript (`val / 1000000`).

---

## 7. Dashboard "Measurements Details" (QuestDB + Timescale)

Dashboard de detalhe de um teste específico, acessado via link do dashboard Individual.

### Painéis:

| #   | Tipo  | Título       | O que mostra                                                         |
| --- | ----- | ------------ | -------------------------------------------------------------------- |
| 1   | Table | Resumo       | Dados do teste: MAC, IP, download, upload, latência, perda, servidor |
| 2   | Table | Measurements | Todas as medições do teste (por `test_uuid`)                         |

### Variável:

| Variável    | Tipo    | Descrição                                               |
| ----------- | ------- | ------------------------------------------------------- |
| `test_uuid` | Textbox | UUID do teste (passado via URL do dashboard Individual) |

> **Observação:** Existe uma versão em TimescaleDB que é praticamente idêntica à versão QuestDB, mas com `public.ndt_tests` e `round()::numeric` (sintaxe PostgreSQL padrão).

---

## 8. Dashboard "Monitoramento e Logs" (QuestDB)

Dashboard de monitoramento de infraestrutura — dispositivos, apagões e erros.

### Painéis:

| #   | Tipo  | Título               | O que mostra                                              |
| --- | ----- | -------------------- | --------------------------------------------------------- |
| 1   | Stat  | Online               | Dispositivos online (último ping < 5 min)                 |
| 2   | Stat  | Offline              | Dispositivos offline (sem ping há mais de 5 min)          |
| 3   | Table | Registro de Apagões  | Log de apagões com início, fim, duração e testes perdidos |
| 4   | Table | Dispositivos Offline | Lista de dispositivos offline com tempo desde último ping |
| 5   | Table | Erros de Aplicação   | Log de erros por dispositivo                              |
| 6   | Table | Erros de Testes      | Testes com falha (download, upload, traceroute UDP/ICMP)  |

### Variável:

| Variável | Tipo  | Descrição                           |
| -------- | ----- | ----------------------------------- |
| `mac`    | Query | Dispositivos com MAC + nome do dono |

### Boas práticas:

1. **Cálculo de tempo offline** — usa aritmética de timestamp do QuestDB: `(now() - last_ping) / 86400000000` para dias, `% 24` para horas, etc.

2. **Threshold de 5 minutos** — `dateadd('m', -5, now())` para definir online/offline.

3. **Join com tabela de dispositivos** — `LEFT JOIN devices d ON d.mac = o.mac_address` para mostrar o nome do dono.

---

## 9. Ideias para aproveitar nos novos painéis

### 🎯 Recomendar adicionar:

1. **Filtros de outlier** — adicionar nos painéis de métricas:

   ```sql
   AND min_rtt <= 1500000  -- remove RTT absurdamente alto
   AND mean_throughput_mbps >= 0  -- remove valores negativos
   ```

2. **Escala logarítmica** — configurar no Grafana para loss rate e RTT:
   - Panel → Field → Scale → Distribution = `Log`, base = `2`

3. **Coloração condicional** — a ideia de colorir por provedor quando há múltiplos e por servidor quando há só um:

   ```sql
   CASE
       WHEN '${isp:csv}' LIKE '%,%' THEN 'provedor'
       ELSE 'servidor'
   END
   ```

4. **Box plots / Violin plots** — adicionar nos painéis de métricas para mostrar distribuição (não só média).

5. **Tabela com total geral** — adicionar linha de total no final das tabelas.

6. **Legendas com percentis** — configurar nas time series: mean, p50, p90, p95, p99.

7. **Mediana em vez de média** — usar `approx_median()` do QuestDB que é mais robusto contra outliers.

8. **Links entre dashboards** — adicionar links nos pontos do gráfico para navegar entre painéis (passando `test_uuid` ou `server_ip`).

9. **Cores temáticas por métrica** — padronizar cores:
   - Download: roxo
   - Upload: laranja
   - RTT/Latência: azul/verde
   - Loss rate: vermelho

10. **`SAMPLE BY` do QuestDB** — usar para agregação temporal eficiente em vez de `$__timeGroup`.

---

## 10. Comparação: Dashboard antigo vs. Novos painéis

| Aspecto                    | Dashboard antigo                       | Novos painéis                     |
| -------------------------- | -------------------------------------- | --------------------------------- |
| Fonte                      | BigQuery + QuestDB + Timescale         | QuestDB                           |
| Tabela                     | `tests_union_grafana_ht` / `ndt_tests` | `download` + `upload` (separadas) |
| Provedores                 | Hardcoded (19)                         | Query + CASE WHEN (33 ASNs)       |
| Nomes normalizados         | ❌ Não                                 | ✅ Sim (Claro, Telefônica, etc.)  |
| Mapa geográfico            | ❌ Não                                 | ✅ Sim (Geomap)                   |
| Painel de servidores       | ❌ Não                                 | ✅ Sim                            |
| Box/Violin plots           | ✅ Sim (Plotly)                        | 🔲 A adicionar                    |
| Filtros em cascata         | ✅ Sim (4 níveis)                      | ✅ Sim (ISP + tempo)              |
| Escala log                 | ✅ Sim (RTT, loss)                     | 🔲 A configurar                   |
| Filtros de outlier         | ✅ Sim                                 | 🔲 A adicionar                    |
| Links entre dashboards     | ✅ Sim (test_uuid)                     | 🔲 A adicionar                    |
| Mediana (approx_median)    | ✅ Sim                                 | 🔲 A adicionar                    |
| SAMPLE BY (QuestDB)        | ✅ Sim                                 | 🔲 A adicionar                    |
| Monitoramento dispositivos | ✅ Sim                                 | ❌ Fora de escopo                 |

---

## 11. Resumo — o que levar para os novos painéis

### Prioridade alta:

1. ✅ Filtros de outlier (`min_rtt <= 1500000`, `mean_throughput_mbps >= 0`)
2. ✅ Escala logarítmica para RTT e loss rate
3. ✅ Legendas com percentis (mean, p50, p90, p95, p99)
4. ✅ Coloração condicional (provedor vs. servidor)
5. ✅ Mediana (`approx_median`) em vez de média onde fizer sentido

### Prioridade média:

6. 🔲 Violin/Box plots para distribuição de métricas
7. 🔲 Tabela com linha de total geral
8. 🔲 Filtros em cascata (ISP → Servidor → Localização)
9. 🔲 Links entre dashboards (navegação por test_uuid)
10. 🔲 Cores temáticas por métrica (roxo=download, laranja=upload, etc.)
11. 🔲 `SAMPLE BY` do QuestDB em vez de `$__timeGroup`

### Não levar:

12. ❌ Provedores hardcoded
13. ❌ Nomes sem normalização
14. ❌ `COUNT(_)` (usar `count()` no QuestDB)

---

> **Conclusão:** O dashboard antigo evoluiu bastante — do BigQuery para o QuestDB, e do dashboard global para dashboards individuais por dispositivo. As melhores ideias para aproveitar são: **filtros de outlier**, **escala log**, **violin plots**, **mediana**, **links entre dashboards** e **cores temáticas**. A estrutura de dados (tabelas `download`/`upload` separadas) e a normalização de ISPs por ASN já são melhorias que implementamos nos novos painéis.

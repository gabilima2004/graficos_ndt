# Plano de Ação — O que falta e por quê

> Objetivo: organizar as demandas restantes e dar propósito claro a cada gráfico.
> Data: 2026-08-21

---

## 1. O que o chefe pediu (originais)

1. ✅ Entender o NDT e os dados da base
2. ✅ Copiar os gráficos antigos
3. ✅ Fazer gráficos no Grafana (incluindo mapa cliente→servidor + filtro por provedor)
4. ⏳ Identificar padrões nos dados

---

## 2. O que já está pronto

| Item | Status | Arquivo |
|------|--------|---------|
| Documentação NDT | ✅ | `01_documentacao/` |
| Mapeamento de 33 ISPs | ✅ | `04_isp_mapping/` |
| Parte 1 — Visão Geral (stats + bar chart) | ✅ | `02_dashboards/ndt_dashboard_parte1.json` |
| Parte 2 — Métricas no tempo | ✅ | `02_dashboards/ndt_dashboard_parte2.json` |
| Parte 3 — Estatísticas por provedor | ✅ | `02_dashboards/ndt_dashboard_parte3.json` |
| Parte 4 — Box plots e violin plots | ✅ | `02_dashboards/ndt_dashboard_parte4.json` |
| Análise Claro vs Telefônica vs Gigalink | ✅ (superficial) | `08_analise/ANALISE_RESULTADOS.md` |
| Mapa cliente→servidor | ⚠️ Bug na query de clientes | `02_dashboards/painel_mapa_corrigido.json` |

---

## 3. Demandas mapeadas — organizadas por propósito

### Demanda A: Finalizar o mapa

**Por quê:** O chefe pediu especificamente "mapa relacionando clientes e servidores". É a entrega mais visível.

**O que fazer:**
1. Resolver o bug da query de clientes (não renderiza as bolinhas azuis)
2. Validar com um servidor específico (ex: `gru02`)
3. Documentar o que o mapa mostra

**Bloqueador atual:** A query de clientes não retorna dados ou não renderiza. Preciso do Query Inspector para debugar.

---

### Demanda B: Gráfico cidade↔servidor

**Por quê:** O mapa mostra a relação geográfica, mas não dá para ver números. Um gráfico de tabela/barra responde:
- "Quais servidores são mais usados em São Paulo?"
- "De quantas cidades diferentes os clientes do servidor gru02 vêm?"

**O que fazer:**
- **Painel 1:** Tabela — top 10 cidades que mais usam cada servidor (com filtro `$server`)
- **Painel 2:** Tabela — top 10 servidores mais usados em cada cidade (com filtro de cidade ou texto livre)
- **Painel 3:** Bar chart — distribuição de servidores por cidade (quão concentrado/disperso é)

**Queries sugeridas:**

```sql
-- Painel 1: Cidades que mais usam o servidor selecionado
SELECT
    c.city,
    count() AS total_testes,
    count(DISTINCT d.client_ip) AS clientes_unicos
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE $__timeFilter(d.test_time)
    AND d.server_site IN ($server)
    AND c.country_code = 'BR'
GROUP BY c.city
ORDER BY total_testes DESC
LIMIT 20
```

```sql
-- Painel 2: Servidores mais usados (visão geral)
SELECT
    d.server_site,
    count() AS total_testes,
    count(DISTINCT d.client_ip) AS clientes_unicos,
    count(DISTINCT c.city) AS cidades_atendidas
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE $__timeFilter(d.test_time)
    AND c.country_code = 'BR'
GROUP BY d.server_site
ORDER BY total_testes DESC
```

---

### Demanda C: Aprofundar a análise de padrões

**Por quê:** A análise atual é descritiva ("Claro tem RTT de 81,5 ms") mas não explica **por quê** nem **o que isso significa**. O chefe quer "identificar padrões" — isso significa achar relações não-óbvias nos dados.

**O que é "identificar padrões" na prática:**

Não é "Claro é mais lenta que Telefônica" (isso é descrição). Padrão é:

1. **"Clientes que usam servidor distante têm RTT X% maior"** — relação entre distância e latência
2. **"O download cai 30% no horário de pico (19h-22h)"** — padrão temporal de saturação
3. **"Provedores pequenos têm loss rate mais variável que grandes"** — relação entre porte e estabilidade
4. **"Cidades com mais servidores têm RTT menor"** — relação entre infraestrutura e qualidade
5. **"A Gigalink entrega o que promete (dados NDT ≈ dados dos roteadores)"** — validação cruzada

**O que fazer (queries para rodar):**

```sql
-- Padrão 1: RTT vs distância cliente→servidor
-- (precisa calcular distância aproximada entre lat/lon do cliente e do servidor)
SELECT
    d.server_site,
    avg(d.min_rtt) AS rtt_medio,
    avg(c.latitude) AS cliente_lat,
    avg(c.longitude) AS cliente_lon,
    s.latitude AS servidor_lat,
    s.longitude AS servidor_lon
FROM download d
JOIN client c ON d.client_ip = c.client_ip
JOIN server s ON d.server_ip = s.server_ip
WHERE $__timeFilter(d.test_time)
    AND c.country_code = 'BR'
    AND d.min_rtt > 0
    AND d.min_rtt <= 1500000
GROUP BY d.server_site, s.latitude, s.longitude
```

```sql
-- Padrão 2: Download por hora do dia (saturação em horário de pico?)
SELECT
    hour(d.test_time) AS hora,
    avg(d.mean_throughput_mbps) AS download_medio,
    approx_median(d.mean_throughput_mbps) AS download_mediana
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE $__timeFilter(d.test_time)
    AND c.country_code = 'BR'
    AND CASE WHEN ... END IN ($isp)
GROUP BY hora
ORDER BY hora
```

```sql
-- Padrão 3: Variabilidade do loss rate por provedor (estabilidade)
SELECT
    CASE WHEN ... END AS provedor,
    avg(d.loss_rate) AS loss_medio,
    stddev(d.loss_rate) AS loss_stddev,
    count() AS total_testes
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE $__timeFilter(d.test_time)
    AND c.country_code = 'BR'
GROUP BY provedor
ORDER BY loss_stddev DESC
```

---

### Demanda D: Validar NDT vs dados dos roteadores (Gigalink)

**Por quê:** Você mencionou que tem dados de roteadores da Gigalink. Comparar os dois conjuntos responde:
- "O NDT mede corretamente?" (validação da ferramenta)
- "A Gigalink entrega o que os roteadores reportam?" (validação do provedor)

**O que fazer:**
1. Pegar dados de throughput/latência dos roteadores da Gigalink
2. Comparar com os dados NDT da Gigalink (mesmo período, mesma região se possível)
3. Se NDT ≈ roteador → NDT é confiável
4. Se NDT < roteador → NDT pode estar subestimando (ou o roteador superestimando)

**Não tenho acesso aos dados dos roteadores** — você precisa me fornecer a estrutura (colunas, formato, período).

---

### Demanda E: Revisar os gráficos existentes com propósito

**Por quê:** Você disse "taquei vários gráficos lá meio sem propósito". Cada gráfico deve responder uma pergunta.

**Mapeamento gráfico → pergunta:**

| Gráfico | Pergunta que responde | Tem propósito? |
|---------|----------------------|----------------|
| Stat: Total de clientes | Qual a amostra? | ✅ Sim |
| Stat: Total de servidores | Qual a infraestrutura? | ✅ Sim |
| Stat: Total de testes | Qual o volume? | ✅ Sim |
| Bar chart: Clientes por provedor | Quem domina o mercado? | ✅ Sim |
| Mapa cliente→servidor | Há padrão geográfico? | ✅ Sim (quando funcionar) |
| Time series: Download por provedor | A velocidade é estável no tempo? | ✅ Sim |
| Time series: Upload por provedor | Upload é assimétrico? | ✅ Sim |
| Time series: RTT por provedor | A latência é estável? | ✅ Sim |
| Time series: Loss rate por provedor | Há perda de pacotes? | ✅ Sim |
| Tabela: Estatísticas por provedor | Qual o ranking? | ✅ Sim |
| Bar chart: Mediana download por provedor | Quem é mais rápido? | ✅ Sim |
| Bar chart: RTT médio por provedor | Quem tem menos latência? | ✅ Sim |
| Box plot: Download por provedor | Qual a distribuição? | ⚠️ Redundante com tabela |
| Violin plot: Download por provedor | Qual a forma da distribuição? | ⚠️ Redundante com box plot |

**Sugestão:** Box plots e violin plots são redundantes entre si. Mantenha só um dos dois (box plot é mais fácil de ler). O violin plot só vale a pena se quiser mostrar bimodalidade (ex: Gigalink com 2 clusters de planos).

---

## 4. Prioridade sugerida

| Prioridade | Demanda | Esforço | Impacto |
|------------|---------|---------|--------|
| 🔴 1 | **A: Finalizar o mapa** | Baixo (debug) | Alto (chefe pediu) |
| 🟠 2 | **C: Padrão temporal (horário de pico)** | Médio | Alto (insight real) |
| 🟠 3 | **B: Gráfico cidade↔servidor** | Baixo | Médio (complementa o mapa) |
| 🟡 4 | **C: Padrão RTT vs distância** | Médio | Médio (insight) |
| 🟡 5 | **D: Validar NDT vs roteadores** | Alto | Alto (mas depende de dados externos) |
| 🟢 6 | **E: Limpar gráficos redundantes** | Baixo | Baixo (organização) |

---

## 5. Próximos passos concretos

1. **Resolver o mapa** — me manda o erro do Query Inspector da query "Clientes"
2. **Criar o gráfico cidade↔servidor** — posso gerar o JSON do dashboard
3. **Rodar a query de horário de pico** — posso criar um novo painel time series com `hour()` no GROUP BY
4. **Definir o que você tem dos roteadores** — colunas, formato, período

Me diz por qual você quer começar.
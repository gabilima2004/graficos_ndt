# To-Do List — Projeto NDT

> Última atualização: 2026-08-25
> Objetivo do chefe: entender NDT, replicar gráficos antigos, fazer mapa cliente→servidor, identificar padrões.

---

## ✅ Concluído

- [x] Entender o NDT e documentar métricas (`01_documentacao/NDT_Documentacao.md`)
- [x] Avaliar dashboards antigos (`01_documentacao/Avaliacao_OldNDT.md`)
- [x] Mapear 33 ISPs por ASN (`04_isp_mapping/`)
- [x] Dashboard Parte 1 — Visão Geral (stats + bar chart)
- [x] Dashboard Parte 2 — Métricas no tempo (download, upload, RTT, loss rate)
- [x] Dashboard Parte 3 — Estatísticas por provedor (tabelas + bar charts)
- [x] Dashboard Parte 4 — Box plots e violin plots
- [x] Análise inicial Claro vs Telefônica vs Gigalink (`08_analise/ANALISE_RESULTADOS.md`)

---

## 🔴 Fase 1 — Ajustes Técnicos e Visualização

### 1.1 Finalizar o Geomap (mapa cliente→servidor)

- [ ] **Debugar a query de clientes** — o quadrado vermelho (servidor) aparece, mas as bolinhas azuis (clientes) não
  - Abrir Query Inspector no painel → query "Clientes"
  - Verificar: dá erro? retorna 0 linhas? retorna linhas mas não renderiza?
  - Arquivo: `02_dashboards/painel_mapa_corrigido.json`
- [ ] **Validar com servidor específico** (ex: `gru02`) — selecionar no filtro `$server` e confirmar que clientes aparecem
- [ ] **Documentar o que o mapa mostra** — atualizar `CONTEXTO_PROJETO.md` removendo "Problema conhecido"

**Bloqueador:** preciso do erro do Query Inspector para continuar.

### 1.2 Criar visualização Cidade ↔ Servidor

- [ ] **Painel: Cidades que mais usam o servidor selecionado** (tabela, com filtro `$server`)
  - Query: `GROUP BY c.city ORDER BY total_testes DESC LIMIT 20`
- [ ] **Painel: Servidores mais usados por cidade** (tabela, com filtro de cidade)
  - Query: `GROUP BY d.server_site ORDER BY total_testes DESC`
- [ ] **Painel: Dispersão cidade→servidor** (bar chart — quantas cidades cada servidor atende)
  - Query: `count(DISTINCT c.city) AS cidades_atendidas GROUP BY d.server_site`
- [ ] **Criar dashboard JSON** com esses painéis + variáveis `$isp` e `$server`

---

## 🟠 Fase 2 — Análise de Padrões (Hipóteses)

> Padrão = relação entre duas variáveis, não número isolado.
> "Claro tem RTT de 81ms" = descrição. "RTT cresce com distância" = padrão.

### 2.1 Hipótese Geográfica — Roteamento/Peering

**Pergunta:** Clientes distantes do servidor têm RTT proporcionalmente maior?

- [ ] **Rodar query:** RTT médio por servidor + lat/lon do cliente e do servidor
- [ ] **Calcular distância aproximada** entre cliente e servidor (fórmula de Haversine ou diferença simples de lat/lon)
- [ ] **Criar gráfico:** scatter plot RTT vs distância
- [ ] **Conclusão:** se RTT correlaciona com distância → problema geográfico; se não → problema de roteamento
- [ ] **Comparar Claro vs Telefônica** — a Telefônica tem RTT 3x menor. É porque clientes estão mais perto ou roteamento melhor?

### 2.2 Hipótese de Qualidade — Saturação e Estabilidade

**Pergunta:** Provedores grandes são mais estáveis que pequenos?

- [ ] **Rodar query:** stddev do loss rate e download por provedor
- [ ] **Criar gráfico:** bar chart de variabilidade (stddev) por provedor
- [ ] **Conclusão:** provedores com maior volume têm menos variabilidade? Ou independe do porte?

### 2.3 Hipótese Temporal — Horários de Pico

**Pergunta:** O download/RTT/loss rate degrada em horário de pico (19h-22h)?

- [ ] **Rodar query:** `hour(test_time)` no GROUP BY, avg e mediana de download/RTT/loss
- [ ] **Criar gráfico:** time series por hora do dia (0-23h)
- [ ] **Comparar provedores** — a degradação acontece em todos ou só em alguns?
- [ ] **Conclusão:** se download cai 30% às 20h → evidência de saturação de rede

---

## 🟡 Fase 3 — Cruzamento Interno (Gigalink NDT vs Roteadores)

**Pergunta:** O NDT mede o mesmo que os roteadores da Gigalink reportam?

- [ ] **Definir dados disponíveis** — que colunas/formato/período tenho dos roteadores?
- [ ] **Extrair dados NDT da Gigalink** — mesmo período dos dados dos roteadores
- [ ] **Comparar throughput** — NDT vs roteador (mesmo cliente/IP se possível)
- [ ] **Comparar latência** — RTT do NDT vs latência do roteador
- [ ] **Conclusão:**
  - Se NDT ≈ roteador → NDT é confiável como ferramenta de medição
  - Se NDT < roteador → NDT subestima (ou roteador superestima)
  - Se NDT > roteador → possível gargalo no trânsito IP (fora da rede local)

---

## 🟢 Fase 4 — Consolidação e Apresentação

- [ ] **Sintetizar achados** em conclusões práticas (atualizar `08_analise/ANALISE_RESULTADOS.md`)
- [ ] **Mapear cada gráfico a uma pergunta** — garantir que nenhum painel está "sem propósito"
- [ ] **Remover redundâncias** — box plots e violin plots são redundantes; manter só box plots
- [ ] **Preparar resumo para o chefe** — 1 página com: o que fiz, o que descobri, o que recomendo
- [ ] **Atualizar `RESUMO_PROGRESSO.md`** com status final

---

## 📊 Prioridade e Esforço

| Fase | Item | Prioridade | Esforço | Bloqueador |
|------|------|------------|---------|------------|
| 1 | Finalizar mapa | 🔴 Alta | Baixo | Erro do Query Inspector |
| 1 | Gráfico cidade↔servidor | 🔴 Alta | Baixo | Nenhum |
| 2 | Horário de pico | 🟠 Média | Baixo | Nenhum |
| 2 | RTT vs distância | 🟠 Média | Médio | Nenhum |
| 2 | Estabilidade por porte | 🟠 Média | Baixo | Nenhum |
| 3 | NDT vs roteadores | 🟡 Baixa | Alto | Dados dos roteadores |
| 4 | Consolidação | 🟢 Final | Baixo | Terminar as fases acima |

---

## 📁 Arquivos de referência

| Arquivo | Para que serve |
|---------|---------------|
| `01_documentacao/CONTEXTO_PROJETO.md` | Contexto geral do projeto |
| `01_documentacao/RESUMO_PROGRESSO.md` | Resumo do que foi feito |
| `08_analise/ANALISE_RESULTADOS.md` | Análise atual (Claro vs Telefônica vs Gigalink) |
| `08_analise/PLANO_ACAO.md` | Plano detalhado com queries sugeridas |
| `02_dashboards/painel_mapa_corrigido.json` | Dashboard do mapa (em debug) |
# To-Do List — Projeto NDT

> Última atualização: 2026-09-02 (pós-reorganização)
> Estrutura nova: `graficos/` (dashboards) e `analise_selecao_servidores/` (pesquisa concluída).
> Ver `ESTRUTURA_PASTAS.md` para o mapa completo e a lista do que é inútil/legado.

---

## ✅ Concluído

- [x] Entender o NDT e documentar métricas (`01_documentacao/NDT_Documentacao.md`)
- [x] Avaliar dashboards antigos (`01_documentacao/Avaliacao_OldNDT.md`)
- [x] Mapear 33 ISPs por ASN (`graficos/isp_mapping/`)
- [x] Dashboard Parte 1 — Visão Geral (stats + bar chart)
- [x] Dashboard Parte 2 — Métricas no tempo (download, upload, RTT, loss rate)
- [x] Dashboard Parte 3 — Estatísticas por provedor (tabelas + bar charts)
- [x] Dashboard Parte 4 — Box plots e violin plots
- [x] Análise inicial Claro vs Telefônica vs Gigalink (`analise_selecao_servidores/ANALISE_RESULTADOS.md`)
- [x] **Mapa cliente→servidor funcionando** (`graficos/dashboards/painel_mapa_corrigido.json`) — clientes azuis + servidores vermelhos, cor/tamanho por volume, filtros `$isp`/`$server`/`$cidade`
- [x] Painéis cidade↔servidor (Top 10 Cidades, Dispersão, Servidores por cidade)
- [x] Mapa standalone de servidores (`graficos/dashboards/mapa_servidores.json`)
- [x] **PESQUISA DE SELEÇÃO DE SERVIDORES — CONCLUÍDA** (`analise_selecao_servidores/PESQUISA_SELECAO_SERVIDOR.md`, 12 seções): GeoIP + haversine + sorteio 95/5; ISP refutado; validada por código fonte + RTT + split de máquinas

---

## 🔴 Fase 1 — Ajustes Técnicos e Visualização

### 1.1 Geomap (mapa cliente→servidor) — ✅ RESOLVIDO

- [x] Query de clientes renderiza (corrigido: `selectedFormat: 1` TABLE + config de location mode/fields — ver `graficos/fixes_e_scripts/debug_mapa_parte1_v2.md`)
- [x] Validado com servidor específico (`gru02`, `gig1916` etc.)
- [ ] **Opcional:** atualizar `01_documentacao/CONTEXTO_PROJETO.md` removendo "Problema conhecido" do mapa

### 1.2 Visualização Cidade ↔ Servidor — ✅ RESOLVIDO

- [x] Painel: Cidades que mais usam o servidor selecionado
- [x] Painel: Servidores mais usados por cidade
- [x] Painel: Dispersão cidade→servidor
- [x] Dashboard com variáveis `$isp`, `$server`, `$cidade`

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

- [ ] **Sintetizar achados** em conclusões práticas (atualizar `analise_selecao_servidores/ANALISE_RESULTADOS.md`)
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
| `analise_selecao_servidores/PESQUISA_SELECAO_SERVIDOR.md` | ⭐ Pesquisa de seleção (concluída, 12 seções) |
| `analise_selecao_servidores/ANALISE_RESULTADOS.md` | Análise Claro vs Telefônica vs Gigalink |
| `graficos/dashboards/painel_mapa_corrigido.json` | ⭐ Dashboard do mapa (funcionando) |
| `ESTRUTURA_PASTAS.md` | Mapa das pastas + lista do que é inútil/legado |
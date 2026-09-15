# Resumo do Progresso — Projeto NDT

> Dashboard no Grafana com dados do NDT (Network Diagnostic Tool) do M-Lab, armazenados em QuestDB.
> Objetivo: entender o NDT, refazer os dashboards antigos, criar novos e achar padrões nos dados.

---

## ✅ O que JÁ FOI FEITO

### 1. Entendimento do NDT e dos dados

- `NDT_Documentacao.md` — documentação completa do que é o NDT, métricas (download, upload, RTT, loss rate) e estrutura das 4 tabelas (`client`, `download`, `upload`, `server`).
- `NDT_Insights_e_Interpretacao.md` — guia de interpretação de cada gráfico e que decisões ele embasa.

### 2. Avaliação dos dashboards antigos

- `Avaliacao_OldNDT.md` — análise de 8 dashboards antigos, identificando boas práticas (filtros de outlier, escala log, legendas com percentis, `approx_median()`, tabela com TOTAL GERAL) e problemas (provedores hardcoded, nomes não normalizados, sem mapa).

### 3. Mapeamento de ISPs (33 ASNs)

- `isp_mapping.csv`, `isp_mapping_doc.md`, `isp_mapping_query.md` — `CASE WHEN` por ASN normalizando nomes de provedores (resolve o problema de "CLARO S.A." vs "Claro S/A").

### 4. Dashboards novos (4 partes, todas com JSON pronto)

| Parte | Arquivo                     | Conteúdo                                                              | Status                                             |
| ----- | --------------------------- | --------------------------------------------------------------------- | -------------------------------------------------- |
| **1** | `ndt_dashboard_parte1.json` | Visão geral: totais, clientes por provedor, mapa cliente→servidor     | ✅ Pronto (mapa precisa de ajuste manual de cores) |
| **2** | `ndt_dashboard_parte2.json` | Métricas no tempo: download, upload, RTT, loss rate por provedor      | ✅ Pronto (corrigido `AS "time"`)                  |
| **3** | `ndt_dashboard_parte3.json` | Estatísticas por provedor: tabelas + bar charts (unificação de 3a+3b) | ✅ Pronto                                          |
| **4** | `ndt_dashboard_parte4.json` | Box plots e violin plots (Plotly) por provedor                        | ✅ Pronto                                          |

### 5. Documentação de queries

- `Dashboard_Parte1_VisaoGeral.md` até `Dashboard_Parte4_Distribuicao.md` — queries SQL e configuração de cada painel.
- `Painel1_Clientes_Queries.md`, `Painel2_Servidores_Queries.md`, `Painel3_Metricas_Queries.md` — queries auxiliares.

### 6. Validações de dados

- `validacao_clientes_por_pais.md` — queries para validar 467.400 clientes e distribuição por país.
- `validacao_servidores_usados.md` — queries para entender quais servidores os clientes brasileiros usam.

### 7. Correções aplicadas

- `fix_parte2.py`, `fix_parte3.py` — scripts Python para corrigir queries (QuestDB exige aspas duplas em palavras reservadas como `AS "time"`).

---

## ⏳ O que FALTA FAZER

| #   | Item                                                                                   | Prioridade |
| --- | -------------------------------------------------------------------------------------- | ---------- |
| 1   | **Ajustar o mapa da Parte 1** (cores das camadas do Geomap) — ajuste manual no Grafana | Alta       |
| 2   | **Análise temporal** — verificar se download cai em horário de pico                    | Média      |
| 3   | **Importar e validar os 4 dashboards no Grafana**                                      | Alta       |
| 4   | **Unificar tudo em um único JSON** (opcional)                                          | Baixa      |

---

## 📊 Achados da análise de dados

> Documentação completa: `08_analise/ANALISE_RESULTADOS.md`

### Visão geral

- **2.205.685 clientes**, **404 servidores**, **12.649.720 testes** (30 dias)
- **Claro** é o provedor com mais clientes (113.216) e mais testes (41% do total)
- **Telefônica** é a 2ª maior (1.130.726 clientes)

### Comparação justa: Claro vs Telefônica (mesmo porte)

| Métrica          | Claro   | Telefônica | Conclusão                                       |
| ---------------- | ------- | ---------- | ----------------------------------------------- |
| RTT médio        | 81,5 ms | 26,4 ms    | **Telefônica 3x melhor** (não depende do plano) |
| Loss rate        | 2,9%    | 2,88%      | Empate (ambos têm ~3% de perda)                 |
| Mediana download | 52 Mbps | 88 Mbps    | Telefônica vende planos melhores                |
| Mediana upload   | 24 Mbps | 54 Mbps    | Telefônica vende planos melhores                |

### Padrão identificado: RTT é roteamento, não geografia

**A descoberta principal:** comparando Claro e Telefônica na **mesma cidade**, a Claro tem 2-4x mais latência:

| Cidade    | Claro RTT | Telefônica RTT | Diferença       |
| --------- | --------- | -------------- | --------------- |
| São Paulo | 13,4 ms   | 4,9 ms         | Claro 2,7x pior |
| Guarulhos | 13,4 ms   | 5,2 ms         | Claro 2,6x pior |
| Osasco    | 17,9 ms   | 4,7 ms         | Claro 3,8x pior |
| Santos    | 17,9 ms   | 5,9 ms         | Claro 3x pior   |
| Campinas  | 21,9 ms   | 6,9 ms         | Claro 3,2x pior |

**Conclusão:** Na mesma cidade, usando provavelmente os mesmos servidores, a Claro tem 2-4x mais latência. **Não é geografia, é roteamento.** A infraestrutura de rede da Telefônica é mais eficiente.

### Gigalink: caso à parte

- RTT excelente (8-16 ms) e loss rate ~0% (muitos testes com perda zero)
- Mas atende nicho específico (Região dos Lagos/RJ) — não é comparável com os grandes
- Tem clusters de planos definidos (provavelmente 1 Gbps e 400 Mbps)

---

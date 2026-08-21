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
| 2   | **Rodar as queries de validação no QuestDB** e documentar os padrões encontrados       | Alta       |
| 3   | **Importar e validar os 4 dashboards no Grafana**                                      | Alta       |
| 4   | **Unificar tudo em um único JSON** (opcional)                                          | Baixa      |

---

## 🗣️ Como falar para o chefe

> **Resumo do progresso do projeto NDT**
>
> **O que eu fiz:**
>
> 1. **Entendi o NDT e a base de dados** — documentei o que é o NDT (ferramenta do M-Lab que mede download, upload, latência e perda de pacotes), a estrutura das 4 tabelas no QuestDB e o que cada métrica significa.
> 2. **Analisei os dashboards antigos** — mapeei 8 dashboards antigos, identificando boas práticas para manter (filtros de outlier, escala log, legendas com percentis, mediana) e problemas para corrigir (provedores hardcoded, nomes não normalizados, falta de mapa).
> 3. **Normalizei os provedores** — criei um mapeamento de 33 ASNs para nomes padronizados de ISPs, resolvendo o problema de variações como "CLARO S.A." vs "Claro S/A".
> 4. **Refiz os dashboards em 4 partes:**
>    - **Parte 1 — Visão Geral:** totais de clientes, servidores e testes, gráfico de clientes por provedor e mapa cliente→servidor.
>    - **Parte 2 — Métricas no tempo:** evolução de download, upload, RTT e loss rate por provedor, com escala log e legendas com percentis.
>    - **Parte 3 — Estatísticas por provedor:** tabelas com média/mediana/min/max + bar charts ranqueando provedores.
>    - **Parte 4 — Distribuição:** box plots e violin plots mostrando a distribuição completa por provedor.
> 5. **Criei queries de validação** para confirmar os números de clientes e entender quais servidores os clientes brasileiros usam.
>
> **O que falta:**
>
> - Ajustar as cores do mapa (ajuste manual no Grafana).
> - Rodar as queries de validação no QuestDB e documentar os padrões encontrados.
> - Importar e validar os 4 dashboards no Grafana.
>
> **Próximos passos:** rodar as análises de padrão geográfico e consolidar os achados em um relatório de insights.

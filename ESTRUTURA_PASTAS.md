# Estrutura de Pastas — graficos_ndt

> Última atualização: 2026-08-21

---

## Estrutura

```
graficos_ndt/
│
├── 01_documentacao/          ← Documentação geral do projeto
│   ├── CONTEXTO_PROJETO.md          Visão geral, banco, mapeamento, status
│   ├── NDT_Documentacao.md          O que é o NDT, métricas, tabelas
│   ├── NDT_Insights_e_Interpretacao.md  Guia de interpretação dos gráficos
│   ├── Avaliacao_OldNDT.md          Análise dos dashboards antigos
│   └── RESUMO_PROGRESSO.md          Resumo do que foi feito e o que falta
│
├── 02_dashboards/             ← JSONs dos dashboards (importar no Grafana)
│   ├── ndt_dashboard_parte1.json    Visão geral (stats + mapa + bar chart)
│   ├── ndt_dashboard_parte2.json    Métricas no tempo (time series)
│   ├── ndt_dashboard_parte3.json    Estatísticas por provedor (tabelas + bars)
│   ├── ndt_dashboard_parte3a.json  (legado) Tabelas separadas
│   ├── ndt_dashboard_parte3b.json  (legado) Bar charts separados
│   └── ndt_dashboard_parte4.json    Box plots e violin plots (Plotly)
│
├── 03_queries/                ← Documentação das queries SQL
│   ├── Dashboard_Parte1_VisaoGeral.md
│   ├── Dashboard_Parte2_MetricasTempo.md
│   ├── Dashboard_Parte3_Estatisticas.md
│   ├── Dashboard_Parte4_Distribuicao.md
│   ├── Painel1_Clientes_Queries.md
│   ├── Painel2_Servidores_Queries.md
│   ├── Painel3_Metricas_Queries.md
│   └── oldndt_Queries.md
│
├── 04_isp_mapping/            ← Mapeamento de ISPs (ASN → nome)
│   ├── isp_mapping.csv              Tabela de ASNs
│   ├── isp_mapping_doc.md            Documentação do mapeamento
│   └── isp_mapping_query.md         CASE WHEN completo
│
├── 05_validacoes/             ← Queries de validação de dados
│   ├── validacao_clientes_por_pais.md
│   └── validacao_servidores_usados.md
│
├── 06_fixes_e_scripts/        ← Correções e scripts Python
│   ├── fix_parte1_heap.md            Documentação do fix de Java heap space
│   ├── fix_parte2.py                Script de correção do Parte 2
│   ├── fix_parte3.py                Script de correção do Parte 3
│   ├── inspect_parte3.py            Script de inspeção do Parte 3
│   └── debug_mapa_parte1.md          Debug do mapa da Parte 1
│
├── 07_dados_csv/              ← CSVs exportados do QuestDB
│   └── questdb-query-*.csv
│
└── 08_analise/                ← Análise de dados e padrões
    └── GUIA_ANALISE.md              Guia passo a passo de análise
```

## Status dos dashboards

| Parte                 | Status         | Observação                                       |
| --------------------- | -------------- | ------------------------------------------------ |
| 1 — Visão Geral       | ⚠️ Parcial     | Stats e bar chart OK; mapa precisa de otimização |
| 2 — Métricas no tempo | ✅ Funcionando | Recarregar variáveis após restart do QuestDB     |
| 3 — Estatísticas      | ✅ Pronto      | JSON unificado (3a + 3b)                         |
| 4 — Distribuição      | ⏳ Pendente    | Erro de servidor, investigar depois              |

## Comandos úteis

### Reiniciar QuestDB (se travar de novo)

```bash
# Na VM do QuestDB (IP final 177)
kill -9 PID_DO_PROCESSO_JAVA
# Ele reinicia sozinho via questdb.sh
```

### Reimportar dashboard no Grafana

1. Dashboards → New → Import
2. Selecionar o JSON da pasta `02_dashboards/`
3. Escolher o datasource do QuestDB
4. Import

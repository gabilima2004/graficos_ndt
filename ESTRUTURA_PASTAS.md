# Estrutura de Pastas — graficos_ndt

> Última atualização: 2026-09-02 — **REORGANIZADO**
> O projeto foi dividido em duas frentes: `graficos/` (dashboards e visualização) e `analise_selecao_servidores/` (pesquisa de como o cliente escolhe o servidor — CONCLUÍDA em 28/08).

---

## Estrutura

```
graficos_ndt/
│
├── 01_documentacao/                  ← Documentação geral (compartilhada)
│   ├── CONTEXTO_PROJETO.md           Visão geral, banco, mapeamento, status
│   ├── NDT_Documentacao.md           O que é o NDT, métricas, tabelas
│   ├── NDT_Insights_e_Interpretacao.md  Guia de interpretação dos gráficos
│   ├── Avaliacao_OldNDT.md           Análise dos dashboards antigos
│   └── RESUMO_PROGRESSO.md           Resumo do que foi feito
│
├── graficos/                         ← FRENTE 1: dashboards e visualização
│   ├── dashboards/                   JSONs dos dashboards (importar no Grafana)
│   │   ├── ndt_dashboard_parte1.json     Visão geral (stats + bar chart)
│   │   ├── ndt_dashboard_parte2.json     Métricas no tempo
│   │   ├── ndt_dashboard_parte3.json     Estatísticas por provedor (unificado)
│   │   ├── ndt_dashboard_parte3a.json    (legado) — ver "o que é inútil"
│   │   ├── ndt_dashboard_parte3b.json    (legado) — ver "o que é inútil"
│   │   ├── ndt_dashboard_parte4.json     Box plots e violin plots
│   │   ├── painel_mapa_corrigido.json ⭐ Mapa cliente→servidor (4 painéis)
│   │   └── mapa_servidores.json          Mapa standalone de servidores
│   ├── queries/                      Documentação das queries SQL
│   │   ├── Dashboard_Parte1..4_*.md      Queries de cada parte
│   │   ├── Painel1/2/3_*_Queries.md      Queries auxiliares
│   │   └── oldndt_Queries.md             (legado) JSON antigo embutido
│   ├── isp_mapping/                  Mapeamento ASN → nome (33 ISPs)
│   │   └── isp_mapping.csv / _doc.md / _query.md
│   ├── fixes_e_scripts/              Correções e scripts (histórico)
│   │   ├── fix_parte1_heap.md            Otimizações de query (lições válidas)
│   │   ├── fix_parte2.py / fix_parte3.py / inspect_parte3.py   (one-shot)
│   │   └── debug_mapa_parte1.md / debug_mapa_parte1_v2.md      (resolvido)
│   └── dados_csv/                    CSVs de dashboards (regeneráveis)
│
├── analise_selecao_servidores/       ← FRENTE 2: pesquisa de seleção (CONCLUÍDA)
│   ├── PESQUISA_SELECAO_SERVIDOR.md  ⭐ Documento principal (12 seções)
│   ├── ANALISE_RESULTADOS.md         Análise Claro vs Telefônica vs Gigalink
│   ├── GUIA_ANALISE.md               Guia de queries por provedor
│   ├── PLANO_ACAO.md                 (histórico) Plano de 21/08 — executado
│   ├── validacoes/                   Validações de clientes e servidores
│   └── dados_csv/                    Evidências da pesquisa
│       ├── c.csv                     ⭐ RTT nordestinos no gig1916 (seção 11)
│       └── questdb-query-*.csv       Servidores por site/volume/lat-lon
│
├── ESTRUTURA_PASTAS.md               Este arquivo
└── TODO.md                           To-do list (atualizada 02/09)
```

## As duas frentes

| Frente | Pasta | Status | Documento-chave |
|--------|-------|--------|-----------------|
| 1. Gráficos | `graficos/` | ✅ Dashboards funcionando | `01_documentacao/RESUMO_PROGRESSO.md` |
| 2. Seleção de servidores | `analise_selecao_servidores/` | ✅ Pesquisa CONCLUÍDA | `PESQUISA_SELECAO_SERVIDOR.md` |

**Conclusão da frente 2 em 1 frase:** o cliente NDT não escolhe o servidor — o Locate API do M-Lab localiza o cliente por GeoIP, ordena os sites por distância haversine (linha reta) e sorteia (~95% o mais próximo, ~5% o 2º). ISP não é fator direto (é volume). Validado por código fonte + RTT + split de máquinas (seções 9, 11 e 12).

---

## O que é INÚTIL (candidatos a apagar — decidir)

| Arquivo | Por quê |
|---------|---------|
| `graficos/dashboards/ndt_dashboard_parte3a.json` | Substituído pelo `parte3.json` unificado |
| `graficos/dashboards/ndt_dashboard_parte3b.json` | Idem |
| `graficos/fixes_e_scripts/fix_parte2.py` | Script one-shot já executado (correção `AS "time"` já aplicada no JSON) |
| `graficos/fixes_e_scripts/fix_parte3.py` | Idem — correção já aplicada |
| `graficos/fixes_e_scripts/inspect_parte3.py` | Inspeção one-shot já usada, não será rodada de novo |
| `graficos/fixes_e_scripts/debug_mapa_parte1.md` | v1 superseded pela v2 — e o bug do mapa já foi resolvido |
| `analise_selecao_servidores/PLANO_ACAO.md` | Todas as demandas A-E foram executadas; valor histórico apenas |
| `graficos/dados_csv/*.csv` | Exports pontuais, regeneráveis do QuestDB a qualquer momento |

## Legado (manter — tem valor de referência)

| Arquivo | Por quê manter |
|---------|----------------|
| `graficos/queries/oldndt_Queries.md` | Contém o JSON dos dashboards ANTIGOS embutido — referência do que o chefe pedia replicar |
| `graficos/fixes_e_scripts/debug_mapa_parte1_v2.md` | Documenta a solução do Geomap vazio (`selectedFormat: 1`) — se o bug voltar, é o primeiro lugar a olhar |
| `graficos/fixes_e_scripts/fix_parte1_heap.md` | Lições de otimização (GROUP BY cidade, evitar `count(DISTINCT)`) — aplicáveis a queries futuras |
| `01_documentacao/Avaliacao_OldNDT.md` | Base das decisões de design dos dashboards novos |
| `analise_selecao_servidores/dados_csv/c.csv` | Evidência citada na seção 11 da pesquisa |

---

## Status dos dashboards

| Dashboard | Status | Observação |
|-----------|--------|------------|
| Parte 1 — Visão Geral | ⚠️ Parcial | Stats/bar chart OK; mapa superseded pelo `painel_mapa_corrigido.json` |
| Parte 2 — Métricas no tempo | ✅ Funcionando | Recarregar variáveis após restart do QuestDB |
| Parte 3 — Estatísticas | ✅ Pronto | JSON unificado (3a/3b são legado) |
| Parte 4 — Distribuição | ⏳ Pendente | Erro de servidor, investigar depois |
| painel_mapa_corrigido | ✅ Funcionando | ⭐ Mapa cliente→servidor + 3 painéis de análise |
| mapa_servidores | ✅ Funcionando | Mapa standalone de todos os servidores |

## Comandos úteis

### Reiniciar QuestDB (se travar de novo)

```bash
# Na VM do QuestDB (IP final 177)
kill -9 PID_DO_PROCESSO_JAVA
# Ele reinicia sozinho via questdb.sh
```

### Reimportar dashboard no Grafana

1. Dashboards → New → Import
2. Selecionar o JSON da pasta `graficos/dashboards/`
3. Escolher o datasource do QuestDB
4. Import

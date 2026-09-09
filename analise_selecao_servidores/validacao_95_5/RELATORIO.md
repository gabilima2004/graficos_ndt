# Relatório Oficial — Validação do Algoritmo de Seleção de Servidores NDT

> **Status:** RASCUNHO — preencher números finais após reexecutar o pipeline (ver Apêndice C)
> **Período analisado:** junho-julho/2026 | **Base:** 4.024.184 testes, 2.280.443 clientes, 38 sites ativos
> **Autor:** [SEU NOME] | **Data:** [PREENCHER]

---

## 1. Sumário executivo

### Pergunta

Como o cliente NDT (Network Diagnostic Tool, do M-Lab) escolhe qual servidor usar para o teste de velocidade? A escolha segue o algoritmo documentado no código fonte do M-Lab?

### Resposta

**Sim — o algoritmo está validado, com uma condição.** O código do serviço de localização do M-Lab (`m-lab/locate`) define que o cliente é direcionado ao site geograficamente mais próximo com ~95% de probabilidade (sorteio exponencial, rate=6), ao 2º mais próximo com ~5%, e raramente além. A validação empírica contra 4 milhões de testes reais confirmou esse comportamento — **condicionado à lista de sites que o Locate ofereceu naquele momento**.

### O número-herói

| | Valor |
|---|---|
| Rank 0 previsto pela decomposição do modelo (soma das capturas ponderadas) | **62,0%** |
| Rank 0 observado nos dados | **61,9%** |
| **Precisão** | **0,1 ponto percentual** |

### O achado principal

O desvio em relação ao 95% teórico **não é bug, não é GeoIP e não é ISP** — é o campo **`Probability` do cadastro de sites**. A maioria dos sites RNP brasileiros (sufixo `1916` e nomenclatura nova de 5 dígitos) tem `Probability ≈ 0,08`: entram na lista de sites disponíveis só ~9% das vezes. Quando o site local é filtrado, o cliente vai **corretamente** para o próximo site disponível — que pode estar a centenas de km.

### Implicação prática

Para análises de qualidade de rede no Brasil usando dados NDT: a localização do servidor **não é um bom proxy de proximidade**. Um teste "no Rio" pode ser de um cliente de Curitiba cujo site local estava filtrado. Recomenda-se usar a taxa de captura por site (metodologia da seção 3) para contextualizar qualquer análise geográfica.

---

## 2. Contexto e método

### 2.1 O algoritmo (extraído do código fonte)

O serviço Locate (`locate.measurementlab.net/v2/nearest/ndt/ndt7`) decide em 4 etapas — código em [`m-lab/locate/heartbeat/location.go`](https://github.com/m-lab/locate/blob/main/heartbeat/location.go):

1. **Filtrar** (`filterSites`): remove sites não saudáveis (`isHealthy()`) e aplica o sorteio de entrada `pickWithProbability(Probability)` — cada site tem um campo `Probability` estático no cadastro
2. **Ordenar** (`sortSites`): por distância **haversine** (linha reta no globo, R = 6.371 km) entre a coordenada do cliente (GeoIP) e a do site
3. **Ranquear** (`rank`): posição na fila + rank metropolitano (sites co-localizados empatam)
4. **Sortear** (`pickTargets`): distribuição exponencial rate=6 — índice 0 ≈ 95%, índice 1 ≈ 5%, demais ≈ 0,01%

**Dois mecanismos de probabilidade independentes:**

| | Mecanismo 1: `Probability` do cadastro | Mecanismo 2: exponencial 95/5 |
|---|---|---|
| Quando | `filterSites()` — antes de ordenar | `pickTargets()` — depois de ordenar |
| O que decide | Se o site **entra na lista** | Qual site da lista **vence** |
| Base | Campo estático por site | Posição na fila |
| Código | `pickWithProbability(v.registration.Probability)` | `GetExpDistributedInt(6) % len(sites)` |

Composição: $P(\text{site vence}) = P(\text{entra na lista}) \times P(\text{vence} \mid \text{na lista})$

### 2.2 Quem define as probabilidades

| Tipo de site | Cadastro | Quem define | P típico |
|---|---|---|---|
| Físicos do núcleo M-Lab (gru02, fln01...) | `m-lab/siteinfo` (jsonnet) | Engenheiros do M-Lab | **1,0** |
| Virtuais GCP novos (gru07, dfw12...) | `m-lab/siteinfo` (jsonnet) | M-Lab (canary/rollout) | **0,05-0,25** |
| Parceiros autojoin (RNP: sufixo 1916, 5 dígitos) | **API Autojoin** (`m-lab/autojoin`) | Parceria: P pedida pelo nó × multiplicador da organização (Datastore) | **≈ 0,08** (RNP) |

A RNP é uma organização autojoin real — confirmada nos testes do próprio M-Lab (`internal/dnsname/names_test.go`, `org: "rnp"`) e no domínio dos hostnames da base: `.rnp.autojoin.measurement-lab.org`.

### 2.3 O pipeline (reproduzível)

```
extract.py  →  QuestDB → CSVs (sites, clients, tests por mês)
analyze.py  →  rank haversine por grupo de distância → out_N/*.csv
```

Detalhes de reprodução no Apêndice C.

---

## 3. Resultados

### 3.1 O histograma e o desvio inicial

Com o rank calculado offline (usando a lista completa de 38 sites ativos):

| rank | Observado | Esperado (código, lista completa) |
| ---- | --------- | ---------------------------------- |
| 0 | 61,9% | ~95% |
| 1 | 20,1% | ~5% |
| 2+ | 18,0% | ~0,01% |

**[INSERIR GRÁFICO 1: histograma de ranks — observado vs esperado]**

O desvio era grande e sistemático. As hipóteses de erro foram testadas e descartadas: lista inflada, coordenadas erradas, GeoIP (o erro se cancela — o Locate usou a mesma coordenada da base), deriva temporal do MaxMind.

### 3.2 A jornada de correções metodológicas

| Correção | Efeito no rank 0 |
|---|---|
| Filtrar sites com < 1000 testes (163 → 38) | 25,5% → 26,6% |
| Rank por **GRUPO de distância** (co-localizados empatam) | 26,6% → **61,9%** |
| Descartar maio/2026 (mês fantasma, 10 testes) | higiene |
| **Taxa de captura por site** | **revelou o mecanismo** |

### 3.3 Taxa de captura por site — a evidência central

**Definição:** dos testes cujo grupo mais próximo era o site X, qual fração realmente usou X?

- Site sempre oferecido → captura ≈ 95% (o sorteio natural)
- Site filtrado em parte das requisições → captura abaixo de 95%

| Grupo de sites | Cidade | Elegíveis | Captura | P implícito* |
|---|---|---|---|---|
| gru02, gru03, gru06, gru07, gru15830, gru1916 | São Paulo | 2.103.267 | **99,5%** | ~1,0 |
| fln01, fln11242 | Florianópolis | 127.799 | **91,4%** | ~0,96 |
| vix1916, vix53078 | Vitória | 75.401 | **56,7%** | ~0,60 |
| gig1916 | Rio de Janeiro | 561.114 | **25,8%** | ~0,27 |
| cwb10881 | Curitiba | 310.979 | **9,1%** | ~0,096 |
| poa2716, ssa53164, gyn1916, slz1916, rec1916, cgb1916, bel1916, mao1916, nat1916, the1916, cpv1916, mcz1916, aju1916, for1916, cgr1916, bsb1916, bvb1916, rbr1916, mcp1916, pmw1916, pvh1916 | Demais | ~500k | **2-9%** | **~0,05-0,10** |

\* P implícito = captura ÷ 0,95. Captura de 9,1% → o site estava na lista ~9,6% das vezes → `Probability ≈ 0,096`.

**[INSERIR GRÁFICO 2: barras da taxa de captura por grupo, linha tracejada em 95%]**

**A assinatura:** a taxa é estável mês a mês (cwb10881: 9,2% → 9,0%; poa2716: 8,7% → 8,7%) — campo estático de cadastro, não saúde flutuante.

**[INSERIR GRÁFICO 3: captura por mês para os principais grupos]**

### 3.4 A prova aritmética

O rank 0 observado é a média ponderada das capturas:

| Grupo | % dos testes | Captura | Contribuição |
|---|---|---|---|
| SP (6 sites co-localizados) | 52,3% | 99,5% | 52,0% |
| Florianópolis | 3,2% | 91,4% | 2,9% |
| Rio (gig1916) | 13,9% | 25,8% | 3,6% |
| Vitória | 1,9% | 56,7% | 1,1% |
| Demais (P ≈ 0,08) | 28,7% | ~8,5% | 2,4% |
| **Total previsto** | | | **62,0%** |

**Observado: 61,9%.** O histograma inteiro está explicado.

Detalhe do grupo SP: captura 99,5% (não 95%) porque os 6 sites são co-localizados — o escape de 5% cai em outro site de SP, invisível dentro do grupo. O 95/5 só aparece no nível de grupo quando o grupo tem um site só (cwb10881: 9,1% ≈ 0,95 × 0,096).

### 3.5 Confirmação documental

O campo `Probability` foi confirmado no cadastro público (`m-lab/siteinfo`):

- Default 1,0 (`sites/_default.jsonnet` e `_default_virtual.jsonnet`)
- Sites com valores baixos explícitos: `gru07` = 0,25; `dfw12` = 0,05; `hnd07` = 0,05
- Caminho: `annotations.probability` (jsonnet) → `registration.json` → heartbeat → `filterSites`
- Para sites autojoin (RNP): P = probability pedida pelo nó × multiplicador da organização (Datastore) — `m-lab/autojoin`, `handler/handler.go`

---

## 4. Conclusões e recomendações

### 4.1 Conclusões

1. **O algoritmo 95/5 do M-Lab opera conforme o código** — a decomposição do histograma bate com precisão de 0,1 p.p.
2. **O mecanismo dos desvios é o campo `Probability` do cadastro** — sites RNP brasileiros entram na lista só ~9% das vezes
3. **A escolha não considera qualidade de rede** — não há probe de RTT; a distância é haversine (linha reta), e o RTT real pode ser alto (nordestinos no RJ: ~100 ms)
4. **ISP não é fator direto** — Claro/Telefônica aparecem em servidores distantes por volume (5% de milhões = centenas de milhares de testes)

### 4.2 Recomendações para análises futuras

1. **Nunca usar a localização do servidor como proxy de proximidade do cliente** — usar a taxa de captura para contextualizar
2. **A unidade de análise é o teste** — agregar por cliente destrói o sinal do 5%
3. **Sites co-localizados devem ser tratados como grupo** — o rank individual não é reproduzível
4. **A lista de sites do Locate é dinâmica** — health e Probability filtram por requisição; o rank offline com lista completa é sistematicamente inflado

### 4.3 Limitações

- `client_name` é null na maioria dos testes — não foi possível identificar apps que fixam servidor manualmente (`config.server`)
- Rejeições por capacidade não ficam registradas na base (só testes completados)
- O valor exato de `Probability` de cada site RNP vive no registro dinâmico (Datastore) — a confirmação numérica exata requer a API do autojoin
- Divergência de fonte de GeoIP (AppEngine/Google vs MaxMind) pode afetar parte do tráfego do widget do Google

---

## Apêndice A — Evidências (CSVs)

| Arquivo | Conteúdo |
|---|---|
| `out_N/rank_histogram.csv` | histograma final (rank por grupo) |
| `out_N/captura_por_site.csv` | **evidência central** — taxa de captura por site |
| `out_N/captura_por_site_mes.csv` | taxa por mês (estável = campo estático) |
| `out_N/diagnostico_coordenadas.csv` | rank mediano por cidade |
| `out_N/por_provedor.csv` | desvios por ISP |
| `out_N/por_hora.csv` | desvios por hora do dia |
| `out_N/outliers_extra_km.csv` | distância extra dos desvios |

## Apêndice B — Fontes (código fonte)

- [`m-lab/locate/heartbeat/location.go`](https://github.com/m-lab/locate/blob/main/heartbeat/location.go) — `Nearest()` [L92-111], `filterSites()` [L115-161], `sortSites()` [L242-245], `rank()` [L247-260], `pickTargets()` [L266-308], `isHealthy()` [L213-224], `pickWithProbability()` [L310-315]
- [`m-lab/go/mathx/rand.go`](https://github.com/m-lab/go/blob/main/mathx/rand.go) — `GetExpDistributedInt(6)`, `GetRandomInt`
- [`m-lab/go/mathx/haversine.go`](https://github.com/m-lab/go/blob/main/mathx/haversine.go) — `GetHaversineDistance`
- [`m-lab/ndt-server/html/ndt7.js`](https://github.com/m-lab/ndt-server/blob/main/html/ndt7.js) — cliente oficial (`results[0]`, `config.server`)
- [`m-lab/ndt-server/spec/ndt7-protocol.md`](https://github.com/m-lab/ndt-server/blob/main/spec/ndt7-protocol.md) — "Server discovery" (aleatoriedade documentada)
- [`m-lab/siteinfo`](https://github.com/m-lab/siteinfo) — cadastro jsonnet (`annotations.probability`)
- [`m-lab/autojoin`](https://github.com/m-lab/autojoin) — registro dinâmico de parceiros (`ProbabilityMultiplier`)

## Apêndice C — Como reproduzir

```bash
cd analise_selecao_servidores/validacao_95_5

# 1. Extração (QuestDB em 10.246.47.159:9000, endpoint /exp)
python extract.py          # baixa sites.csv, clients.csv, tests_YYYY-MM.csv

# 2. Análise (gera out_N/ com todos os CSVs de evidência)
python analyze.py

# 3. Gráficos do relatório
python gerar_graficos.py   # gera fig1_histograma.png, fig2_captura.png, fig3_captura_mes.png
```

Requisitos: Python 3.10+, `requests`, `pandas`, `numpy`, `matplotlib`. Acesso à rede do QuestDB.

---

*Relatório gerado a partir de `RESULTADO_VALIDACAO.md` (validação 07-08/09/2026) e `PESQUISA_SELECAO_SERVIDOR.md` (pesquisa concluída 28/08/2026).*
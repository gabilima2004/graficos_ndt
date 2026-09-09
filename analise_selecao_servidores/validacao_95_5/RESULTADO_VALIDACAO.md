# Validação do algoritmo 95/5 — Resultados e conclusão

> Data: 07-08/09/2026
> Contexto: validação empírica do algoritmo de seleção de servidor do M-Lab Locate
> (documentado em `../PESQUISA_SELECAO_SERVIDOR.md`, seção 9) contra a base de dados.
> **Status: validação concluída com sucesso — com uma condição importante descoberta.**

---

## 1. O que foi feito

Pipeline nesta pasta (`analise_selecao_servidores/validacao_95_5/`):

1. **`extract.py`** — extrai do QuestDB (IP interno `10.246.47.159:9000`, endpoint `/exp`):
   - `sites.csv` — 163 sites distintos + coordenadas
   - `clients.csv` — 2.280.443 clientes (ip, lat/lon, asn, city)
   - `tests_YYYY-MM.csv` — 4.024.184 testes (maio/junho/julho de 2026), particionado por mês
2. **`analyze.py`** — calcula o rank haversine do site usado em cada teste e gera os outputs em `out*/`

**Correções conceituais feitas durante o caminho** (cada uma mudou o resultado):

| Correção                                                       | Efeito no histograma                                 |
| -------------------------------------------------------------- | ---------------------------------------------------- |
| Filtrar sites com < 1000 testes no período (163 → 38)          | rank 0: 25,5% → 26,6% (pouco — o problema era outro) |
| Rank por **GRUPO de distância** (sites co-localizados empatam) | rank 0: 26,6% → **61,9%** (grande salto)             |
| Descartar maio/2026 (10 testes na base inteira — mês fantasma) | higiene dos dados                                    |
| **Taxa de captura por site**                                   | **revelou o mecanismo** (ver abaixo)                 |

---

## 2. O problema que travava a validação

Com o rank por grupo, o histograma ficou:

| rank | Observado | Esperado (código) |
| ---- | --------- | ----------------- |
| 0    | 61,9%     | ~95%              |
| 1    | 20,1%     | ~5%               |
| 2+   | 18,0%     | ~0,01%            |

Longe do 95/5. As hipóteses testadas e descartadas:

- ❌ **Lista de sites inflada** — filtrar para 38 sites ativos não resolveu
- ❌ **Coordenadas de sites erradas** — validadas no mapa do Grafana
- ❌ **GeoIP errado (em geral)** — o erro se cancela: o Locate usou a mesma coordenada que está na tabela `client`, então o "mais próximo" calculado offline é o mesmo que o Locate calculou
- ❌ **Deriva temporal do GeoIP** — MaxMind é estável semana a semana para IP residencial; fator secundário
- ⚠️ **Divergência de fonte (AppEngine/Google vs MaxMind)** — possível para parte do tráfego (widget do Google), mas não explica o padrão sistemático por site

## 3. O achado: taxa de captura por site

Métrica nova: para cada localização, dos testes cujo grupo mais próximo era ela, qual fração realmente a usou?

| Grupo de sites                                                                                                                                                                                   | Elegíveis      | Taxa de captura | P implícito (taxa ÷ 0,95) |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------- | --------------- | ------------------------- |
| **gru02, gru03, gru06, gru07, gru15830, gru1916** (SP)                                                                                                                                           | 2.103.267      | **99,5%**       | ~1,0                      |
| **fln01, fln11242** (Florianópolis)                                                                                                                                                              | 127.799        | **91,4%**       | ~0,96                     |
| **vix1916, vix53078** (Vitória)                                                                                                                                                                  | 75.401         | **56,7%**       | ~0,60                     |
| **gig1916** (Rio)                                                                                                                                                                                | 561.114        | **25,8%**       | ~0,27                     |
| **cwb10881** (Curitiba)                                                                                                                                                                          | 310.979        | **9,1%**        | ~0,096                    |
| **poa2716, ssa53164, gyn1916, slz1916, rec1916, cgb1916, bel1916, mao1916, nat1916, the1916, cpv1916, mcz1916, aju1916, for1916, cgr1916, bsb1916, bvb1916, rbr1916, mcp1916, pmw1916, pvh1916** | ~500k no total | **2-9%**        | **~0,05-0,10**            |

**Dois grupos nítidos:**

1. **Sites M-Lab OTI** (nomes antigos: gru02, gru03, fln01) — sempre oferecidos, captura ~95-99%
2. **Sites RNP (sufixo 1916) e nomenclatura nova de 5 dígitos** — captura 2-9%, ou seja, **Probability ≈ 0,05-0,10 no cadastro**

E a taxa é **estável mês a mês** (cwb10881: 9,2% em junho → 9,0% em julho; poa2716: 8,7% → 8,7%) — assinatura de um campo **estático de cadastro** (`registration.Probability`), não de problema de saúde flutuante.

## 4. A prova aritmética: o histograma se decompõe exatamente

O rank 0 observado é a média ponderada das capturas, ponderada pelos testes elegíveis:

| Grupo                       | % dos testes | Captura | Contribuição para o rank 0 |
| --------------------------- | ------------ | ------- | -------------------------- |
| SP (6 sites co-localizados) | 52,3%        | 99,5%   | 52,0%                      |
| Florianópolis               | 3,2%         | 91,4%   | 2,9%                       |
| Rio (gig1916)               | 13,9%        | 25,8%   | 3,6%                       |
| Vitória                     | 1,9%         | 56,7%   | 1,1%                       |
| Demais (P ≈ 0,08)           | 28,7%        | ~8,5%   | 2,4%                       |
| **Total previsto**          |              |         | **62,0%**                  |

**Observado: 61,9%.** Precisão de 0,1 ponto percentual. O histograma inteiro está explicado.

Detalhe elegante do grupo SP: por que 99,5% e não 95%? Porque os 6 sites são **co-localizados** (mesma coordenada registrada) — quando o sorteio de 5% escapa para o índice 1, cai em **outro site de SP** (os 6 empatam no topo da ordenação). O escape fica invisível dentro do grupo. O 95/5 só aparece no nível de grupo quando o grupo tem **um site só** — exatamente o que se vê: cwb10881 com captura 9,1% ≈ 0,95 × P(0,096).

## 5. Conclusão

**O algoritmo 95/5 está validado — condicionado à lista de sites que o Locate ofereceu.**

A cadeia completa:

1. O Locate filtra sites por `isHealthy()` e `pickWithProbability(Probability)` **antes** de ordenar por distância
2. A maioria dos sites RNP brasileiros tem `Probability ≈ 0,08` — entram na lista só ~9% das vezes
3. Quando o site local é filtrado, o cliente vai **corretamente** para o próximo site disponível (Curitiba → rank 1; Salvador → rank 5, pulando os sites de baixa P)
4. O cálculo offline usava a lista completa → marcava rank != 0 para o que era **comportamento correto** na época

Isso explica todos os mistérios pendentes:

- Histograma esparramado (cada cidade tem um "P" diferente para seu site local)
- Curitiba rank mediano 1 (cwb10881 com P ≈ 0,096)
- Salvador rank mediano 5 (ssa53164 com P ≈ 0,09; os ranks 1-4 são sites também de baixa P)
- Claro/Telefônica com ~73% de desvio (presentes em todas as cidades, inclusive as de baixa P)
- ISPs pequenos com ~100% de desvio (clientes em cidades servidas por sites RNP)
- gru15830 saltando de 97k (junho) para 418k (julho) testes — **rollout avançando** (o Probability dele subiu; a taxa de captura do grupo SP não mudou porque os outros 5 sites de SP já capturavam ~100%)

**Não é erro do algoritmo, não é GeoIP, não é ISP — é o campo `Probability` do cadastro de sites.**

## 6. Confirmação documental pendente (próximo passo)

O campo `Probability` vem do **cadastro público de sites do M-Lab**:

- Repositório: https://github.com/m-lab/siteinfo
- API: https://siteinfo.m-lab.dev

**Verificação a fazer:** consultar os registros de `cwb10881`, `ssa53164`, `poa2716`, `gig1916`, `vix53078` (esperado: `probability ≈ 0,08-0,10`) e de `gru02`, `gru03`, `fln01` (esperado: `probability = 1,0`). Se bater, é a confirmação documental direta do mecanismo.

## 7. Arquivos de evidência

| Arquivo                             | Conteúdo                                                                                   |
| ----------------------------------- | ------------------------------------------------------------------------------------------ |
| `out_4/rank_histogram.csv`          | histograma final (rank por grupo)                                                          |
| `out_4/captura_por_site.csv`        | **a evidência central** — taxa de captura por site                                         |
| `out_4/captura_por_site_mes.csv`    | taxa por mês (estável = campo estático)                                                    |
| `out_4/diagnostico_coordenadas.csv` | rank mediano por cidade (com nomes)                                                        |
| `out_4/por_provedor.csv`            | desvios por ISP (reinterpretar com rank de grupo)                                          |
| `out_4/por_hora.csv`                | desvios por hora (verificar se há componente de carga)                                     |
| `out_4/outliers_extra_km.csv`       | distância extra dos desvios                                                                |
| `out/`, `out_2/`, `out_3/`          | execuções anteriores (rank por site individual, com/sem filtro) — mantidas para comparação |

## 8. Lições metodológicas (para o relatório final)

1. **A unidade de análise é o teste** — agregar por cliente/coordenada destruiria justamente o sinal do 5%
2. **Sites co-localizados empatam** — o rank individual dentro do grupo não é reproduzível; o que vale é o rank do grupo
3. **A lista de sites do Locate não é estática** — health e Probability filtram sites por requisição; o rank calculado offline com a lista completa é sistematicamente inflado
4. **O erro do GeoIP se cancela** — desde que a coordenada usada na análise seja a mesma que o Locate usou (mesma fonte, mesmo momento). A divergência de fonte (Google vs MaxMind) é o caso que não cancela
5. **Taxa de captura por site** é a métrica que separa "algoritmo funcionando com lista diferente" de "algoritmo falhando"

## 9. Pendências

- [ ] Confirmar `Probability` no siteinfo do M-Lab (seção 6)
- [ ] Atualizar `08_analise/PESQUISA_SELECAO_SERVIDOR.md` com esta validação (nova seção 13)
- [ ] Atualizar `01_documentacao/RESUMO_PROGRESSO.md` (achado para o chefe)
- [ ] Opcional: reavaliar o corte de 1000 testes (1486 testes descartados; sites em rollout com pouco volume saem da lista — mas o efeito é marginal)
- [ ] Opcional: investigar bsb1916 e gig1916 (nomes antigos com captura baixa — não fecham com a narrativa de rollout; podem ter Probability baixa também, confirmar no siteinfo)

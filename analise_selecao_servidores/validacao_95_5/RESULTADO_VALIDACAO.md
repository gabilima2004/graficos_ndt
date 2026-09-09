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

### 3.1 O que é "taxa de captura"

A métrica responde uma pergunta simples, site a site:

> **Dos testes que deveriam ir para o site X (porque X era o grupo mais próximo do cliente), quantos % realmente foram para o X?**

- Se o site foi oferecido pelo Locate em **todas** as requisições → captura ≈ 95% (o sorteio manda ~95% para o mais próximo)
- Se o site foi **filtrado** pelo Locate em parte das requisições (health ou `Probability` baixo) → captura bem abaixo de 95%, porque nesses casos o cliente cai no 2º, 3º... site mais próximo disponível

### 3.2 Resultado por grupo de sites

| Grupo de sites | Cidade | Testes elegíveis | Taxa de captura | P implícito* |
|---|---|---|---|---|
| gru02, gru03, gru06, gru07, gru15830, gru1916 | São Paulo | 2.103.267 | **99,5%** | ~1,0 |
| fln01, fln11242 | Florianópolis | 127.799 | **91,4%** | ~0,96 |
| vix1916, vix53078 | Vitória | 75.401 | **56,7%** | ~0,60 |
| gig1916 | Rio de Janeiro | 561.114 | **25,8%** | ~0,27 |
| cwb10881 | Curitiba | 310.979 | **9,1%** | ~0,096 |
| poa2716, ssa53164, gyn1916, slz1916, rec1916, cgb1916, bel1916, mao1916, nat1916, the1916, cpv1916, mcz1916, aju1916, for1916, cgr1916, bsb1916, bvb1916, rbr1916, mcp1916, pmw1916, pvh1916 | Demais capitais/cidades | ~500k no total | **2-9%** | **~0,05-0,10** |

\* **P implícito** = taxa de captura ÷ 0,95. Como o sorteio manda ~95% dos testes para o site mais próximo **quando ele está na lista**, uma captura de 9,1% implica que o site estava na lista só ~9,6% das vezes (9,1% ÷ 0,95) — ou seja, `Probability ≈ 0,096` no cadastro.

### 3.3 Os dois grupos nítidos

1. **Sites M-Lab OTI** (nomes antigos: gru02, gru03, fln01) — sempre oferecidos, captura ~95-99%
2. **Sites RNP (sufixo 1916) e nomenclatura nova de 5 dígitos** — captura 2-9%, ou seja, **Probability ≈ 0,05-0,10 no cadastro**

### 3.4 A assinatura: taxa estável mês a mês

| Site | Junho | Julho |
|------|-------|-------|
| cwb10881 (Curitiba) | 9,2% | 9,0% |
| poa2716 (Porto Alegre) | 8,7% | 8,7% |

A taxa **não flutua** — é praticamente idêntica mês a mês. Isso é a assinatura de um **campo estático de cadastro** (`registration.Probability`), não de um problema de saúde flutuante (que variaria de um mês para o outro).

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

## 6. Confirmação documental — ✅ CONFIRMADA (09/09/2026)

O campo `Probability` vem do **cadastro público de sites do M-Lab** (`m-lab/siteinfo`) e foi **confirmado no repositório**:

### 6.1 O campo existe no cadastro, por site, em arquivos jsonnet

**Default = 1,0** (físico e virtual):
```jsonnet
// sites/_default.jsonnet (físico)
annotations: { probability: 1.0, ... }
// sites/_default_virtual.jsonnet (virtual)
annotations: { probability: 1.0, ... }
```

**Sites com valores baixos explícitos** (sobrescrevem o default):
```jsonnet
// sites/gru07.jsonnet — São Paulo
annotations+: { probability: 0.25, provider: 'gcp' }
// sites/dfw12.jsonnet — Dallas
annotations+: { probability: 0.05, ... }
// sites/hnd07.jsonnet — Tóquio
annotations+: { probability: 0.05, ... }
```

### 6.2 O caminho exato até o Locate

`formats/v2/sites/registration.json.jsonnet` gera o registro que a máquina carrega:
```jsonnet
{
  [site.Machine(machine).Hostname()]: {
    ...
    Probability: site.annotations.probability,  // ← do cadastro direto
    ...
  }
}
```

Fluxo completo: `annotations.probability` (jsonnet) → `registration.json` → máquina carrega via `cmd/heartbeat/registration` → envia no `HeartbeatMessage` → `filterSites` usa em `pickWithProbability(v.registration.Probability)`.

### 6.3 Esclarecimento: são DOIS mecanismos de probabilidade no código

| | Mecanismo 1: `Probability` do cadastro | Mecanismo 2: exponencial 95/5 |
|---|---|---|
| **Onde** | `filterSites()` — antes da ordenação | `pickTargets()` — depois da ordenação |
| **O que decide** | Se o site **entra na lista** | Qual site da lista **vence** |
| **Base** | Campo **estático por site** (jsonnet) | **Posição** na fila ordenada por distância |
| **Código** | `pickWithProbability(v.registration.Probability)` | `GetExpDistributedInt(6) % len(sites)` |

Os dois se compõem:

$$P(\text{site X vence}) = \underbrace{P(\text{X entra na lista})}_{\text{Probability do cadastro}} \times \underbrace{P(\text{X vence} \mid \text{na lista})}_{\text{exponencial pela posição}}$$

Para o cwb10881: $0{,}096 \times 0{,}95 \approx 9{,}1\%$ — exatamente a captura observada. A posição na lista só "vale" quando o site passa pelo filtro; o filtro usa o valor estático do cadastro.

### 6.4 Bônus: gru07 com P = 0,25 no cadastro

O `gru07` (SP) tem `probability: 0,25` no jsonnet — mas a captura do **grupo SP** foi 99,5%. Não contradiz: o grupo entra na lista quando **qualquer** um dos 6 sites passa o filtro, e os outros (gru02, gru03 etc., provavelmente P = 1,0) bastam. O grupo SP é "sempre oferecido" porque tem sites com P = 1,0 nele.

**Verificação pendente restante:** consultar os registros de `cwb10881`, `ssa53164`, `poa2716`, `gig1916`, `vix53078`, `bsb1916` na API (https://siteinfo.m-lab.dev ou raw do GitHub) para confirmar os valores exatos (esperado: `probability ≈ 0,05-0,10`). O mecanismo já está confirmado; falta só o número exato de cada site.

## 6.5 Quem define as probabilidades? (investigação 09/09)

**Resposta curta: pessoas do M-Lab e das organizações parceiras, em dois cadastros diferentes — não é automático.**

### 6.5.1 Dois cadastros, dois caminhos

| | Sites no siteinfo (nomes antigos: gru02, fln01...) | Sites autojoin (sufixo 1916 e nomenclatura de 5 dígitos) |
|---|---|---|
| **Cadastro** | `m-lab/siteinfo` (arquivos jsonnet por site) | **API Autojoin** (`m-lab/autojoin`) — registro dinâmico |
| **Quem define** | Engenheiros do M-Lab, no jsonnet do site | A **organização parceira** no momento do registro (flag `-probability` do `cmd/register`) × **multiplicador da organização** no Datastore |
| **Default** | `probability: 1.0` | `defaultProb = 1.0` (mas o parceiro pode passar outro valor na query) |
| **Fórmula** | valor fixo no jsonnet | `probability = getProbability(req) × orgMultiplier` |

### 6.5.2 O caminho autojoin (o dos sites RNP)

Confirmado no código do `m-lab/autojoin`:

```go
// handler/handler.go (registro de um nó)
orgEntity, err := s.dsm.GetOrganization(req.Context(), param.Org)
orgMultiplier := 1.0
if err == nil && orgEntity != nil && orgEntity.ProbabilityMultiplier != nil {
    orgMultiplier = *orgEntity.ProbabilityMultiplier
}
// Assign the probability by multiplying the org multiplier with the
// probability requested by the client.
param.Probability = getProbability(req) * orgMultiplier
```

- A **organização** (ex: RNP) obtém uma API key; o `org` vem do JWT da chave (`validateJWTAndExtractOrg`)
- O **multiplicador da organização** (`ProbabilityMultiplier`) vive no Google Datastore (`token-exchange/store/autojoin.go`: `ProbabilityMultiplier *float64 \`datastore:"probability_multiplier"\``) — configurável pelo M-Lab por organização
- O **nó** ao se registrar passa `probability` na query (`cmd/register/main.go`: flag `-probability`, "Default probability of returning this site for a Locate result", default 1.0)
- O teste do próprio M-Lab documenta a semântica: `wantProbability: 1.0, // 0.5 * 2.0` — request × multiplicador

### 6.5.3 A RNP é uma organização autojoin real

O teste `internal/dnsname/names_test.go` do próprio autojoin usa `org: "rnp"`:

```go
{
    name:    "success",
    org:     "rnp",
    project: "mlab-autojoin",
    want:    "autojoin-rnp-autojoin-measurement-lab-org",
},
```

E o domínio bate com os hostnames da sua base: `ndt-gig1916-c89ffeef.rnp.autojoin.measurement-lab.org` — o sufixo `.rnp.autojoin.measurement-lab.org` é exatamente a zona DNS da organização RNP no autojoin.

### 6.5.4 Por que não são todos iguais? (a resposta ao "por quê")

**Porque a probabilidade é o mecanismo de controle de capacidade e rollout — decidido caso a caso:**

1. **Sites físicos do núcleo M-Lab** (gru02, fln01...): P = 1,0 — infraestrutura própria, capacidade garantida, sempre oferecidos
2. **Sites virtuais GCP novos** (gru07, dfw12, hnd07...): P = 0,05-0,25 no jsonnet — **canary/rollout**: entram com tráfego mínimo e vão sendo liberados conforme validação
3. **Sites de parceiros via autojoin** (RNP, nomenclatura nova): P definido na parceria — o parceiro pede um valor (ou aceita o default) e o M-Lab modula pelo multiplicador da organização. Sites RNP com P ≈ 0,08 = **acordo de tráfego limitado** (a RNP hospeda o hardware, mas o M-Lab limita a fração de testes que ela recebe)

A taxa estável mês a mês que você observou (cwb10881: 9,2%→9,0%) é exatamente o esperado: o valor vem de **configuração** (jsonnet ou Datastore), não de telemetria.

### 6.5.5 O que ainda não dá para saber daqui

- O valor exato de cada site RNP (o jsonnet deles não está no siteinfo — são autojoin; o valor vive no registro dinâmico/Datastore)
- Se o P ≈ 0,08 veio do pedido da RNP, do multiplicador da org, ou da combinação (ex: nó pediu 1,0 × multiplicador 0,08 da org RNP — o teste `0.5 * 2.0` mostra que a multiplicação é o mecanismo)
- **Como verificar:** a API `https://autojoin.measurementlab.net/autojoin/v0/node/list?format=sites&org=rnp` lista os sites da RNP; o `registration.json` servido ao Locate expõe o `Probability` efetivo de cada hostname

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

- [x] Confirmar `Probability` no siteinfo do M-Lab (seção 6) — ✅ **CONFIRMADO 09/09**: campo existe no cadastro jsonnet, default 1,0, sites com valores baixos explícitos (gru07 = 0,25; dfw12/hnd07 = 0,05); caminho jsonnet → registration.json → heartbeat → filterSites
- [x] **Quem define as probabilidades** (seção 6.5) — ✅ **ESCLARECIDO 09/09**: dois cadastros — siteinfo (jsonnet, M-Lab) para sites físicos; API Autojoin para parceiros (RNP), onde P = probability pedida pelo nó × multiplicador da organização (Datastore). RNP confirmada como org autojoin nos testes do próprio M-Lab (domínio `.rnp.autojoin.measurement-lab.org`)
- [ ] Confirmar valores exatos de `cwb10881`, `ssa53164`, `poa2716`, `gig1916`, `vix53078`, `bsb1916` — via `https://autojoin.measurementlab.net/autojoin/v0/node/list?org=rnp` ou o registration.json servido ao Locate (sites RNP não estão no siteinfo — são autojoin)
- [ ] Atualizar `PESQUISA_SELECAO_SERVIDOR.md` com esta validação (nova seção 13)
- [ ] Atualizar `01_documentacao/RESUMO_PROGRESSO.md` (achado para o chefe)
- [ ] Opcional: reavaliar o corte de 1000 testes (1486 testes descartados; sites em rollout com pouco volume saem da lista — mas o efeito é marginal)
- [ ] Opcional: investigar bsb1916 e gig1916 (nomes antigos com captura baixa — não fecham com a narrativa de rollout; podem ter Probability baixa também, confirmar no siteinfo)

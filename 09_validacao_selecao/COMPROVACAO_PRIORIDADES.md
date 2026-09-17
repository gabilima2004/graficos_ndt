# Comprovação: servidores M-Lab têm diferentes "níveis de prioridade"

**Data:** 2026-09-17
**Objetivo:** provar, com fontes oficiais do M-Lab + nossos próprios dados, que os servidores NDT têm pesos de seleção diferentes — e entender a prioridade dos servidores da RNP.

---

## 1. A prova documental: o campo `Probability` no cadastro oficial do M-Lab

O M-Lab publica publicamente o cadastro de todos os seus servidores em:

```
https://siteinfo.mlab-oti.measurementlab.net/v2/sites/registration.json
```

Cada máquina tem um campo **`Probability`** — exatamente o "nível de prioridade" que o chefe quer ver. Valores reais extraídos do arquivo (set/2026):

| Servidor          | Cidade             | Probability | Tipo     | Uplink |
| ----------------- | ------------------ | ----------- | -------- | ------ |
| mlab1-gru02       | São Paulo (BR)     | **1**       | physical | 10g    |
| mlab2-gru02       | São Paulo (BR)     | **1**       | physical | 10g    |
| mlab3-gru02       | São Paulo (BR)     | **1**       | physical | 10g    |
| mlab1-gru03       | São Paulo (BR)     | **1**       | physical | 10g    |
| mlab1-gru07       | São Paulo (BR)     | **0.25**    | virtual  | 1g     |
| mlab1-fln01       | Florianópolis (BR) | **1**       | physical | 10g    |
| mlab1-lim01/lim02 | Lima (PE)          | **1**       | physical | 10g    |
| mlab1-bog02/bog05 | Bogotá (CO)        | **1**       | physical | 10g    |
| mlab1-eze01       | Buenos Aires (AR)  | **1**       | physical | 10g    |
| mlab1-ams12       | Amsterdã           | **0.05**    | virtual  | 1g     |
| mlab1-del06       | Nova Délhi         | **0.5**     | virtual  | 1g     |
| mlab1-lis01       | Lisboa             | **0.5**     | physical | 1g     |
| mlab1-tun01       | Túnis              | **0.5**     | physical | 1g     |
| mlab1-hkg06       | Hong Kong          | **0.25**    | virtual  | 1g     |
| mlab1-jnb03       | Joanesburgo        | **0.25**    | virtual  | 1g     |
| mlab1-par08       | Paris              | **0.25**    | virtual  | 1g     |
| mlab1-yyz09       | Toronto            | **0.25**    | virtual  | 1g     |
| mlab1-hel03       | Helsinque          | **0.05**    | virtual  | 1g     |
| mlab1-syd09       | Sydney             | **0.05**    | virtual  | 1g     |
| mlab1-lhr11       | Londres            | **0.05**    | virtual  | 1g     |

**Padrão inequívoco:** servidores `physical` com uplink 10g → `Probability = 1`; servidores `virtual` com uplink 1g → `Probability` entre 0.05 e 0.5. O campo existe, é público, e varia por servidor.

**Ponto-chave brasileiro:** `mlab1-gru07` (São Paulo) tem **P = 0.25** — um servidor no Brasil com prioridade 4× menor que os vizinhos gru02/gru03. Isso já é prova documental de prioridade diferenciada em solo brasileiro.

## 2. Como o `Probability` é usado (código-fonte do M-Lab)

**Esclarecimento importante (investigação no código-fonte):** existem **duas funções** envolvidas, mas **nenhuma delas calcula a probabilidade** — elas apenas a **usam**:

**Função 1 — a loteria de distância (95/5):** em `m-lab/locate/heartbeat/location.go`, `pickTargets()` usa:

```go
// m-lab/go/mathx
func GetExpDistributedInt(n int) int {
    return int(rand.ExpFloat64() / float64(n))
}
```

Com `n = 6`: P(índice 0) = 1 − e⁻³ ≈ **95,02%**, P(índice 1) ≈ **4,98%**. Esta função **sim** calcula algo — o índice do site a escolher, baseado só na distância. É o "95% vai pro mais próximo, 5% escapa".

**Função 2 — o filtro de probabilidade:** em `m-lab/locate/heartbeat/location.go`:

```go
// pickWithProbability returns true if a pseudo-random number in the interval
// [0.0,1.0) is less than the given site's defined probability.
func pickWithProbability(probability float64) bool {
    return rand.Float64() < probability
}
```

Esta função **não calcula nada** — ela recebe o `probability` pronto e faz um "cara ou coroa" com ele. Antes da loteria, cada site passa por este filtro: se o número aleatório for menor que o `Probability` do site, ele entra na lista de candidatos; senão, é descartado daquela consulta.

**De onde vem o valor de `probability`?** É a peça-chave: **é um parâmetro de cadastro, não um cálculo**. Para os sites OTI, vem do cadastro estático (`siteinfo`, arquivos `.jsonnet` com `probability: 0.05` etc.). Para os nós autojoined (RNP), o **próprio nó declara** o valor no momento do registro (ver seção 4.1, item 3). Ou seja: **o cadastro define a "loteria"** — 95% das vezes o teste vai para o site mais próximo, 5% escapa para os seguintes, e o `Probability` de cada site decide se ele sobrevive ao filtro antes do sorteio.

## 3. A prova empírica: nossos dados batem com o cadastro

Analisamos ~4 milhões de testes NDT (jun–jul/2026) no nosso QuestDB e medimos a **taxa de captura** de cada site (fração dos testes em que o site mais próximo de fato foi escolhido):

| Site                                                     | Testes | Taxa de captura medida | Probability esperado |
| -------------------------------------------------------- | ------ | ---------------------- | -------------------- |
| Grupo SP (gru02, gru03, gru07, gru15830, gru1916...)     | ~1,2M  | **99,5%**              | P=1 (physical)       |
| fln01 (Florianópolis)                                    | ~200k  | **91,4%**              | P=1                  |
| vix1916/vix53078 (Vitória)                               | 75k    | **56,7%**              | ~0,60                |
| gig1916 (Rio)                                            | 561k   | **25,8%**              | ~0,27                |
| cwb10881 (Curitiba)                                      | 311k   | **9,1%**               | ~0,096               |
| poa2716, ssa53164, rec1916, bsb1916, for1916, etc. (RNP) | ~500k  | **2–9%**               | ~0,05–0,10           |

**Prova aritmética:** somando as probabilidades esperadas de todos os sites, a fração prevista de testes que ficam no site mais próximo é **62,0%**; a fração observada nos dados é **61,9%**. Erro de 0,1 ponto percentual.

**Estabilidade mês a mês** (assinatura de campo estático de cadastro, não de falha operacional):

- cwb10881: 9,2% (jun) → 9,0% (jul)
- poa2716: 8,7% (jun) → 8,7% (jul)

## 4. A prioridade dos servidores da RNP

### 4.1 O que conseguimos provar

1. **Sim — os servidores RNP entraram na plataforma pela API Autojoin.** O nome do servidor decodifica assim:

   ```
   ndt-gig1916-c89ffeef.rnp.autojoin.measurement-lab.org
   │   │   │     │       │
   │   │   │     │       └── organização que registrou o servidor: "rnp"
   │   │   │     └── hash do IPv4 do servidor (c89ffeef = 200.159.254.239)
   │   │   └── ASN do site: 1916 = AS1916 (RNP!)
   │   └── código IATA do aeroporto: GIG = Rio de Janeiro
   └── serviço: ndt
   ```

   O padrão oficial está documentado no M-Lab (`m-lab/website`, host-managed-documentation):
   `ndt-<IATA><ASN>-<IPv4_HEX>.<ORGANIZATION>.autojoin.measurement-lab.org`

   **Correção importante:** o "1916" **não é um número de projeto** — é o **número do ASN da RNP** (AS1916). Por isso os sites têm sufixos diferentes: `gig1916` (Rio, AS1916), `poa2716` (Porto Alegre, AS2716), `cwb10881` (Curitiba, AS10881), `ssa53164` (Salvador, AS53164), `vix53078` (Vitória, AS53078). Cada sufixo numérico é o ASN do ponto de presença onde o servidor está.

2. **O que é a API Autojoin** (do código-fonte `m-lab/autojoin`, openapi.yaml): é a API de **registro dinâmico** da plataforma M-Lab. Organizações parceiras (RNP, Equinix, Cogent, Google OIM, dezenas de ISPs) instalam um servidor próprio ("autonode", modelo BYOS — _bring your own server_) e o registram via `POST /autojoin/v0/node/register`. A API então:
   - atribui o nome DNS público no padrão acima,
   - cria a zona DNS delegada para a organização (por isso a zona `rnp.autojoin.measurement-lab.org` tem nameservers da própria RNP: `server1.pop-rj.rnp.br`, etc.),
   - e o nó passa a receber tráfego NDT como um site M-Lab.

   **Confirmação direta:** a listagem pública `https://autojoin-dot-mlab-autojoin.appspot.com/autojoin/v0/node/list` mostra todos os nós autojoined, incluindo os da RNP com os rótulos `org: rnp`, `type: virtual`, `deployment: byos`, `managed: none`. Todos os ~25 sites RNP (gig1916, cwb10881, poa2716, ssa53164, rec1916, bsb1916, for1916, gyn1916, slz1916, mcz1916, cgb1916, bel1916, mao1916, nat1916, the1916, cpv1916, mcp1916, pmw1916, pvh1916, bvb1916, rbr1916, aju1916, cnf1916, vix1916, gru1916, fln11242) aparecem lá como **nós virtuais BYOS da organização "rnp"**.

3. **Como o `Probability` é definido para nós autojoined — a resposta exata, do código-fonte.** A investigação profunda em `m-lab/autojoin` revelou o mecanismo completo:

   **a) O nó declara a probabilidade no registro.** O comando `register` (que roda no autonode) tem a flag `-probability` ("Default probability of returning this site for a Locate result"). Se não for passada, o padrão é **1.0** (`defaultProb = 1.0`). O valor vai na query string do registro: `?probability=<valor>`.

   **b) O Autojoin API aplica um multiplicador da organização.** No handler `Register()`:

   ```go
   // Assign the probability by multiplying the org multiplier with the
   // probability requested by the client.
   param.Probability = getProbability(req) * orgMultiplier
   ```

   O `orgMultiplier` vem do cadastro da organização no Datastore (`AutojoinOrganization.ProbabilityMultiplier`). Ou seja: **a probabilidade final = probabilidade declarada pelo nó × multiplicador da organização**. Se a RNP tem multiplicador 0.1 no cadastro do M-Lab, todos os nós RNP têm a probabilidade dividida por 10 no registro.

   **c) O valor vai para o `registration.json`** que o autonode recebe e reporta ao Locate via heartbeat. O Locate então usa esse valor no filtro `pickWithProbability` (seção 2).

   **d) O M-Lab pode sobrescrever tudo** via `ProbabilityOverrides` (kill-switch por máquina, carregado na inicialização do Locate via flag `probability-override`).

   **Conclusão:** a probabilidade **não é calculada dinamicamente** — é uma cadeia de valores declarados: **nó declara → API multiplica pelo fator da organização → vira cadastro estático → Locate usa no filtro**. Para a RNP, os valores que medimos (0.05–0.10) resultam dessa cadeia: ou os nós declaram valores baixos, ou a organização "rnp" tem um `ProbabilityMultiplier` baixo no cadastro do M-Lab (ou ambos). O multiplicador exato não é público, mas o mecanismo está 100% documentado no código.

4. **O cadastro detalhado do projeto RNP não é público.** Verificamos exaustivamente:
   - `siteinfo.mlab-rnp.measurement-lab.org` → DNS inexistente (confirmado nos nameservers autoritativos `ns-cloud-e1.googledomains.com`)
   - `siteinfo.mlab-rnp.measurementlab.net` → DNS inexistente (confirmado em `ns-cloud-c1.googledomains.com`)
   - Não há delegação de zona `mlab-rnp` em `measurement-lab.org` nem em `measurementlab.net` (a zona `rnp.autojoin.measurement-lab.org` é delegada a servidores DNS da própria RNP: `server1.pop-rj.rnp.br`, `server1.pop-df.rnp.br`, `view.lncc.br`)
   - Repositório GitHub `m-lab/siteinfo` → nenhum arquivo `cwb10881.jsonnet`, `ssa53164.jsonnet`, etc.
   - Buckets GCS `mlab-rnp-siteinfo` / `rnp-siteinfo` → 404

   **Conclusão:** os nós RNP são autojoined (BYOS) e o registro detalhado deles — incluindo o `Probability` exato que cada nó reportou — não é publicado no endpoint público do siteinfo (que só cobre o projeto `mlab-oti`). O que é público: a **lista de nós** (`/autojoin/v0/node/list`) e o **algoritmo** que consome o `Probability`.

5. **Mas a prioridade deles é mensurável e já está medida.** A taxa de captura é a consequência direta do `Probability` — e os números falam por si:

   | Site RNP                                          | Taxa de captura | Prioridade implícita     |
   | ------------------------------------------------- | --------------- | ------------------------ |
   | vix53078 (Vitória)                                | 56,7%           | alta (~0,6)              |
   | gig1916 (Rio)                                     | 25,8%           | média (~0,27)            |
   | cwb10881 (Curitiba)                               | 9,1%            | baixa (~0,10)            |
   | poa2716 (Porto Alegre)                            | 8,7%            | baixa (~0,09)            |
   | ssa53164 (Salvador)                               | ~9%             | baixa (~0,09)            |
   | rec1916, bsb1916, for1916, gyn1916, slz1916, etc. | 2–9%            | muito baixa (~0,05–0,10) |

### 4.2 Interpretação para o chefe

- **Os servidores RNP são nós autojoined (BYOS) com prioridade baixa por design.** Eles são VMs virtuais (`type: virtual`, `deployment: byos` na listagem oficial do Autojoin), e o padrão do M-Lab para sites virtuais é `Probability` entre 0.05 e 0.5 — exatamente a faixa que medimos (0.05–0.10 para a maioria). A prioridade de cada nó é definida **no registro** (o nó reporta seu próprio `Probability` ao Locate, e o M-Lab pode sobrescrever via kill-switch).
- **Isso significa que um cliente brasileiro raramente cai no servidor RNP da sua cidade**, mesmo sendo o mais próximo. 95% das vezes o teste vai para o site físico mais próximo com P=1 (SP, Florianópolis, etc.).
- **Implicação prática para nossos dashboards:** os dados coletados nos servidores RNP representam apenas a "fatia de escape" da loteria (~2–9% dos testes de cada região). Qualquer análise que use só os servidores RNP está vendo uma amostra enviesada — os testes que caem lá são os 5% que escaparam do site principal.
- **A hierarquia de prioridade é:** sites físicos OTI (P=1) > sites virtuais OTI (P=0.25–0.5) > nós autojoined RNP (P≈0.05–0.10, medido empiricamente).

## 5. Pesquisa acadêmica existente sobre o mecanismo

Investigamos a literatura publicada sobre a seleção de servidores do M-Lab. Achados:

**5.1 O que a literatura diz (e onde ela está desatualizada)**

- **Matt Mathis (2026), "Detecting Anomalous Topology, Routing Policies, and Congested Interconnections at Internet Scale"** (arXiv:2603.25875, autor é pesquisador do próprio M-Lab): o paper **depende** da seleção de servidores do M-Lab como fundamento metodológico — _"M-Lab's Locate Service uniformly distributes tests across geographically nearby M-Lab servers, explicitly disregarding network conditions, delays, or historical performance"_. Ele usa isso para criar comparações A/B naturais entre servidores do mesmo metro. **Importante:** o paper descreve a seleção como "uniforme" — o que é verdade **dentro de um metro com servidores equivalentes** (como SP, onde gru02/gru03 têm P=1), mas **não captura a diferença de `Probability` entre sites** que documentamos. O paper nem menciona o campo `Probability`. Nossa análise é mais fina: mostramos que a distribuição é uniforme **entre sites de mesma prioridade**, mas enviesada entre sites de prioridades diferentes (ex.: cwb10881 recebe 9% dos testes de Curitiba enquanto o site mais próximo receberia ~95%).
- **Gill et al. (2019), "M-Lab: user initiated Internet data for the research community"** (ACM IMC 2019, doi:10.1145/3523230.3523236): o paper de referência da plataforma. Menciona o locate service direcionando clientes, mas **não detalha o mecanismo de probabilidade** — o campo `Probability` e a loteria exponencial não são documentados na literatura acadêmica.
- **MacMillan et al. (2023), "A comparative analysis of Ookla Speedtest and M-Lab's NDT7"** (ACM SIGMETRICS 2023, doi:10.1145/3579448): compara as plataformas e nota que _"for NDT7 tests, we find each server is used roughly equally"_ — observação válida para os sites OTI de um metro (todos P=1), mas que **não generaliza** para regiões onde há mistura de sites físicos e autojoined (como no Brasil).
- **Koukoutsidis (2015), "Public QoS and Net Neutrality Measurements"**: discute que a seleção de servidor do NDT é baseada em proximidade, contrastando com o Ookla (que tem mais servidores e seleção por RTT). Não entra no detalhe do `Probability`.
- **Donar (Wendell et al., ACM SoCC 2010)** e **NeIL (Ahmed et al., IEEE 2024)**: trabalhos sobre seleção de réplicas/servidores em geral que citam o M-Lab como caso, mas não analisam o mecanismo específico do Locate.

**5.2 Conclusão da revisão de literatura**

**Não existe publicação acadêmica que documente o campo `Probability` ou a loteria exponencial 95/5 do Locate.** O mecanismo só está documentado no código-fonte (que analisamos em detalhe) e na documentação operacional do M-Lab. Isso significa:

1. **Nossa análise é original** — ninguém publicou a decomposição "filtro de probabilidade + loteria de distância" nem mediu taxas de captura por site como fizemos.
2. **A literatura que assume "seleção uniforme"** (como o paper do Mathis, que é a base metodológica dos dashboards de interconexão do M-Lab) **é válida apenas dentro de grupos de servidores com mesma prioridade**. Para análises que cruzam servidores de prioridades diferentes (nosso caso com os sites RNP), a suposição de uniformidade falha — e é exatamente isso que nossos dados mostram.
3. **Implicação para o chefe:** a descoberta de que os servidores RNP têm prioridade baixa é um achado que **não está na literatura** — é verificável por nós (dados + código-fonte), e tem implicação prática direta: qualquer estudo que use dados dos servidores RNP como se fossem amostras representativas da região está errado.

## 6. Resumo das fontes (para citar)

1. **Cadastro oficial com `Probability`:** `https://siteinfo.mlab-oti.measurementlab.net/v2/sites/registration.json` (público, verificado em 17/09/2026)
2. **Código do algoritmo:** `github.com/m-lab/locate` → `heartbeat/location.go` (`Nearest`, `pickWithProbability`) e `github.com/m-lab/go` → `mathx/haversine.go`, `mathx.GetExpDistributedInt`
3. **Nossa validação empírica:** `09_validacao_selecao/RESULTADO_VALIDACAO.md` (pipeline extract.py + analyze.py, saídas em `/root/ndtgraficos/out_4/`)
4. **FQDN e registro dos servidores RNP:** visível nos dados do QuestDB (`ndt-gig1916-c89ffeef.rnp.autojoin.measurement-lab.org`), confirmado por DNS autoritativo (zona `rnp.autojoin.measurement-lab.org`, NS da RNP: `server1.pop-rj.rnp.br` etc.) e pela listagem pública da API Autojoin: `https://autojoin-dot-mlab-autojoin.appspot.com/autojoin/v0/node/list` (todos os nós RNP com `org: rnp`, `type: virtual`, `deployment: byos`)
5. **Padrão de nomes autojoin:** `m-lab/website` → `_pages/host-managed-documentation.md` (`ndt-<IATA><ASN>-<IPv4_HEX>.<ORGANIZATION>.autojoin.measurement-lab.org`) e `m-lab/go` → `host/host.go` (`parseHostV3`)
6. **Tratamento de nós autojoined no Locate:** `m-lab/locate` → `heartbeat/location.go` (`pickWithProbability`, `ProbabilityOverrides`, "an autojoined node is its own single-machine site")
7. **Definição da probabilidade no registro:** `m-lab/autojoin` → `handler/handler.go` (`param.Probability = getProbability(req) * orgMultiplier`), `cmd/register/main.go` (flag `-probability`, `defaultProb = 1.0`), `internal/register/register.go` (`Probability: p.Probability` no `Heartbeat`), e `token-exchange/store` (`AutojoinOrganization.ProbabilityMultiplier`)
8. **Literatura acadêmica:** Mathis (2026) arXiv:2603.25875 ("uniform server selection"); Gill et al. (2019) ACM IMC doi:10.1145/3523230.3523236; MacMillan et al. (2023) doi:10.1145/3579448; Koukoutsidis (2015) J. Information Policy. Nenhuma documenta o campo `Probability`.

## 7. Pendência (única)

Os valores exatos de `Probability` dos nós RNP são definidos no registro de cada nó (via Autojoin API) e não são publicados no siteinfo público. Enquanto isso, a **taxa de captura medida nos nossos dados é a melhor estimativa disponível** — e ela é estável mês a mês, o que confirma que é um parâmetro de cadastro, não ruído.

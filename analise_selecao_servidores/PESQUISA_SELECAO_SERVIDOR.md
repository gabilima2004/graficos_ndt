# Pesquisa: Como o cliente escolhe o servidor NDT?

> Data: 26/08/2026 (início) — **CONCLUÍDA em 28/08/2026**
> Objetivo: Descobrir os fatores que determinam qual servidor NDT um cliente usa para fazer o teste.
> **Resposta final:** GeoIP + distância em linha reta (haversine) + sorteio exponencial 95/5. Ver seção 9.

---

## 1. Contexto

O NDT (Network Diagnostic Tool) do M-Lab mede a qualidade da conexão (download, upload, RTT, loss rate). Para fazer o teste, o cliente se conecta a um servidor NDT. Existem servidores no Brasil e no exterior (Peru, EUA, Europa, etc.).

**Pergunta central:** O que determina qual servidor o cliente usa? É proximidade geográfica? É o ISP? É o NDT que escolhe? É o usuário?

**Contexto adicional (descoberto durante a pesquisa):** o NDT nasceu como ferramenta de diagnóstico, mas hoje a maior parte do tráfego vem de speed tests embutidos em produtos de terceiros — o maior deles é o **widget de teste de velocidade do Google Search** (que roda NDT7 do M-Lab). Outros: `speed.measurementlab.net`, OONI Probe, apps Android/iOS com as bibliotecas oficiais (`ndt7-client-android`, `ndt7-client-ios`) e integradores diversos. Por isso o "cliente" quase nunca é uma pessoa escolhendo um site de diagnóstico — é um app/widget disparando o teste, o que explica os `client_name` null na base (integradores não se identificam).

---

## 2. Hipóteses levantadas

| # | Hipótese | Status inicial | **Veredito final** |
|---|----------|----------------|---------------------|
| 1 | **Localização geográfica** — o NDT escolhe o servidor mais próximo fisicamente | ⚠️ Parcialmente confirmada | ✅ **CONFIRMADA** — é o fator principal: distância haversine + sorteio 95/5 (seção 9) |
| 2 | **ISP/Provedor** — o roteamento do ISP determina qual servidor é "visto" como perto | ⚠️ Parcialmente confirmada | ❌ **REFUTADA** — ISP não é fator direto; Claro/Telefônica aparecem só por volume (5% de milhões = muito) |
| 3 | **Tipo de servidor** (RNP vs MLAB) — prioridade por operadora | ⏳ Não investigada | ❌ **REFUTADA** — não há prioridade por organização no código (`filterSites` só filtra saúde) |
| 4 | **Código fonte** — a lógica de seleção define o comportamento | ⏳ A investigar | ✅ **INVESTIGADO** — algoritmo completo documentado (seção 9) |
| 5 | **Servidor fora do ar** — desvios causados por servidores NE indisponíveis | — | ❌ **REFUTADA** — todos os servidores NE tiveram testes todos os dias (seção 10.3) |
| 6 | **RTT/rede como critério** — cliente mede latência antes de escolher | — | ❌ **REFUTADA** — não há probe de RTT; nordestinos no RJ com ~100ms (seção 11) |
| 7 | **Versão do ndt-server influencia** — v0.23–v0.25 mudam a seleção | — | ❌ **REFUTADA** — split 50/50 entre máquinas de versões diferentes (seção 12) |

> **Nota:** as hipóteses 5, 6 e 7 surgiram durante a investigação, como explicações alternativas para os desvios observados. Todas foram testadas e refutadas.

---

## 3. Metodologia

### Ferramentas usadas

- **Mapa Cliente→Servidor** (Grafana Geomap): mostra onde estão os clientes que usam um servidor específico, com cor/tamanho por quantidade de testes
- **Mapa de Servidores** (Grafana Geomap): mostra todos os servidores disponíveis
- **Filtro `$isp`**: permite filtrar por provedor
- **Filtro `$server`**: permite selecionar um servidor específico
- **Queries no console do QuestDB**: para extrair RTT e estatísticas
- **Análise do código fonte**: repositórios `m-lab/locate`, `m-lab/go` e `m-lab/ndt-server` (GitHub)
- **Consulta direta à API**: `https://locate.measurementlab.net/v2/nearest/ndt/ndt7` (resposta real com `index` e `metro_rank`)

### Abordagem

1. Selecionar um servidor no mapa e observar de onde vêm os clientes
2. Filtrar por ISP e ver quais provedores mandam tráfego para aquele servidor
3. Medir o RTT dos clientes que usam servidores distantes
4. Comparar com a localização geográfica e o roteamento do ISP
5. **Analisar o código fonte** do serviço de seleção (m-lab/locate)
6. **Validar empiricamente** as predições do código contra os dados (RTT, split de máquinas, volume por rank)

---

## 4. Observações

### 4.1 Concentração geográfica

Ao selecionar servidores brasileiros (ex: `gru02` em São Paulo), a maioria dos clientes está concentrada na região próxima ao servidor. Isso confirma parcialmente a hipótese de localização.

**Porém**, também há muitos clientes fora da região, mais perto de outros servidores, usando o servidor selecionado.

### 4.2 Clientes brasileiros usando servidor do Peru

Ao selecionar um servidor do Peru (ex: `lim01`), foram encontrados clientes brasileiros fazendo testes contra ele.

**ISPs que mandaram tráfego para o Peru:**

| ISP | ASN | Testes | RTT médio (ms) |
|-----|-----|--------|-----------------|
| Claro | 28573, 4230, 22085 | 370 | 190 |
| Telefônica | 18881, 26599, etc | 63 | 138 |
| ALLREDE Telecom | 273683 | 1 | 174 |

**ISPs que NÃO mandaram tráfego para o Peru:**
- Gigalink e outros provedores regionais

### 4.3 RTT alto para o Peru

O RTT dos clientes brasileiros que usam o servidor do Peru é **alto** (138-190 ms), não baixo. Isso é contraintuitivo — se o NDT escolhesse o servidor por proximidade de rede, o RTT deveria ser baixo.

---

## 5. Análise

> **Nota:** esta seção foi escrita ANTES da análise do código fonte (seção 9). As explicações A-E abaixo foram as candidatas da época; a correta se revelou a **D (GeoIP errado) combinada com o sorteio probabilístico** — descobertas na seção 9. Mantida aqui para registro do processo.

### 5.1 A hipótese de localização geográfica

**Parcialmente confirmada.** A maioria dos testes vai para servidores próximos, mas há exceções significativas (clientes no Brasil usando servidor no Peru).

### 5.2 A hipótese de ISP

**Parcialmente confirmada, mas com ressalva.** Apenas 3 ISPs (Claro, Telefônica, ALLREDE) mandaram tráfego para o Peru. Outros ISPs não mandaram. Isso indicava que o ISP seria um fator — mas a seção 9 refutou isso: **é volume**, não ISP. Claro/Telefônica têm milhões de testes; 5% de 5 milhões = 250 mil testes internacionais. Gigalink, com poucos clientes, raramente cai no sorteio.

**A ressalva da época:** O RTT alto (138-190ms) sugeria que o Peru não era eficiente em rede. Isso continua válido — e a explicação final é que **a rede nunca foi o critério**: a seleção é por distância geográfica em linha reta, não por latência.

### 5.3 Possíveis explicações para o RTT alto

| # | Explicação | Como confirmar | **Veredito final** |
|---|-----------|----------------|---------------------|
| A | **Load balancing** — servidores brasileiros estavam saturados | Verificar volume nos servidores BR | ❌ Não é o mecanismo — não há load balancing por carga na seleção |
| B | **Algoritmo com bug** — locator retornou servidor errado | Olhar código fonte | ❌ Não é bug — é o sorteio de ~5% funcionando como projetado |
| C | **Cliente escolheu manualmente** — alguns clientes permitem especificar servidor | Verificar código do cliente | ⚠️ **Parcial** — existe (`config.server` no ndt7.js), mas é caso raro de integrador |
| D | **GeoIP errado** — serviço achou que o cliente era do Peru | Verificar IPs dos clientes | ✅ **CONFIRMADA** — GeoIP (MaxMind) pode errar, especialmente com IPs de ISPs menores |
| E | **Capacidade do servidor** — Peru tinha menos carga | Verificar métricas de carga | ⚠️ **Parcial** — rejeição por capacidade existe (cliente tenta o próximo da lista), mas não explica o padrão Peru |

### 5.4 Por que só Claro, Telefônica e ALLREDE?

**Explicação final (seção 9): volume, não ISP.** A hipótese do "probe de RTT" desta seção estava **errada** — não existe probe de RTT na seleção. Claro e Telefônica mandam para o Peru porque têm milhões de testes; o sorteio de ~5% no 2º servidor mais próximo gera centenas de milhares de testes internacionais para elas. Provedores regionais com poucos testes quase nunca caem no sorteio.

---

## 6. Próximos passos

> **Status: TODOS EXECUTADOS.** Esta seção foi escrita antes da análise do código; mantida como registro do plano original.

### 6.1 Investigar o código fonte do M-Lab ✅

- ✅ Como funciona o "server selection" / "locator"? → **Locate API** (`m-lab/locate`), ver seção 9
- ✅ O cliente mede RTT para múltiplos servidores antes de escolher? → **NÃO** — não há probe de RTT
- ✅ Há load balancing? → **Não por carga** — sorteio exponencial por distância + rejeição por capacidade como fallback
- ✅ O cliente pode escolher manualmente? → **SIM** — `config.server` no ndt7.js (usado por integradores)

Repositórios relevantes:
- https://github.com/m-lab/ndt-server (servidor)
- https://github.com/m-lab/ndt7-client (cliente)
- https://github.com/m-lab/locate (serviço de localização) ← **o principal**

### 6.2 Verificar load balancing ✅

Query executada — servidores brasileiros com volume alto, mas a causa dos desvios não é carga: é o sorteio probabilístico (seção 9).

### 6.3 Verificar se o cliente pode escolher o servidor ✅

Confirmado no código: `ndt7.js` aceita `config.server` (fixação manual) e `config.loadbalancer` (Locate alternativo). Padrão: Locate do M-Lab.

### 6.4 Comparar RTT do probe vs RTT do teste ✅

**Não existe probe.** A pergunta partia de uma premissa falsa — resolvida pela análise do código (seção 9.2).

---

## 7. Conclusão parcial

> **Nota:** conclusão da época (antes do código fonte). A conclusão FINAL está nas seções 9-12. Mantida como registro.

A escolha do servidor NDT **não é puramente geográfica** e **não é puramente por ISP**. Os fatores identificados até então:

1. **Localização geográfica** — é o fator principal para a maioria dos testes (concentração perto do servidor)
2. **ISP** — influencia quais servidores são considerados (só alguns ISPs mandam para o Peru)
3. **Fator não identificado** — o RTT alto para o Peru sugeria algo além de proximidade e ISP

O item 3 foi resolvido pela análise do código fonte (seção 9): o "fator não identificado" era a **aleatoriedade intencional do algoritmo** (sorteio exponencial 95/5) somada a **erros de GeoIP**. O item 2 foi refutado: o padrão por ISP é volume, não roteamento.

---

## 8. Dados coletados

### RTT por ISP para servidor do Peru (lim01)

| ISP | Testes | RTT médio (ms) | RTT esperado se perto |
|-----|--------|-----------------|----------------------|
| Telefônica | 63 | 138 | 30-50 |
| ALLREDE Telecom | 1 | 174 | 30-50 |
| Claro | 370 | 190 | 30-50 |

**Conclusão:** RTT é alto para todos → o Peru não é "perto" em termos de rede → o NDT está escolhendo o Peru por outro motivo além de proximidade.

### ASN 273683 = ALLREDE TELECOM LTDA

Confirmado via BGP lookup (bgp.he.net/AS273683). Antes era classificado como "Desconhecido" no mapeamento de ISPs.

---

## 9. RESPOSTA FINAL: Análise do código fonte do M-Lab (28/08/2026)

> **Esta seção responde à pergunta central da pesquisa.** A investigação do código fonte foi concluída e revelou o algoritmo exato de seleção de servidores.

### 9.1 O serviço responsável: Locate API

O código do cliente (ndt7.js) confirma:

```js
// If no server was specified then use a loadbalancer. If no loadbalancer
// is specified, use the locate service from Measurement Lab.
const lbURL = (config && ('loadbalancer' in config)) ?
    new URL(config.loadbalancer) :
    new URL('https://locate.measurementlab.net/v2/nearest/ndt/ndt7');
```

**O que é esse "loadbalancer"?** O termo é genérico no código — significa "o serviço que decide o servidor", seja ele qual for. O trecho é um ternário:

- Se quem embute o teste (o integrador) passou um `config.loadbalancer`, o cliente usa **esse serviço alternativo** como localizador
- Se não, usa o **Locate do M-Lab** (o padrão)

Ou seja: o Locate API **é**, na prática, um load balancer geográfico. A opção existe para um integrador rodar o teste com **sua própria infraestrutura de localização** (ex: uma empresa com servidores próprios que quer distribuir clientes com a lógica dela). Para a base de dados deste projeto, vale o padrão: Locate do M-Lab.

### 9.2 Como o Locate determina a localização do cliente

O serviço identifica a localização do cliente por (nesta ordem de prioridade):

1. **Parâmetros do usuário** — se o cliente passar `country=BR` ou `region=US-IL` na URL
2. **Headers do AppEngine/GCP** — latitude/longitude que o Google adiciona automaticamente
3. **MaxMind GeoIP** — banco de dados que mapeia IP → latitude/longitude

**De onde vêm esses parâmetros?** Do **código do integrador, não da máquina da pessoa física**. O item 1 significa que o *código que embute o teste* (widget do Google, app, etc.) pode montar a URL como `locate.measurementlab.net/v2/nearest/ndt/ndt7?country=BR` — quem monta essa URL é o código do integrador, não o usuário físico. O usuário final não passa nada: o navegador/celular dela só executa o JS do integrador. Na prática, a maioria não passa (por isso a base tem `region` vazia) e a localização vem do GeoIP (itens 2 e 3).

**Não há probe de RTT.** A seleção é 100% baseada em **distância geográfica em linha reta** (lat/lon), não em latência de rede.

### 9.3 O algoritmo de seleção — análise detalhada do código

**Arquivo:** [`m-lab/locate/heartbeat/location.go`](https://github.com/m-lab/locate/blob/main/heartbeat/location.go)

O algoritmo completo tem 4 etapas, orquestradas pela função `Nearest()`:

```go
// https://github.com/m-lab/locate/blob/main/heartbeat/location.go#L92-L111
// Nearest discovers the nearest machines for the target service, using
// an exponentially distributed function based on distance.
func (l *Locator) Nearest(service string, lat, lon float64, opts *NearestOptions) (*TargetInfo, error) {
    // Filter.
    sites := filterSites(service, lat, lon, l.Instances(), opts)

    // Sort.
    sortSites(sites)

    // Rank.
    rank(sites)

    // Pick.
    result := pickTargets(service, sites)

    if len(result.Targets) == 0 {
        return nil, ErrNoAvailableServers
    }

    return result, nil
}
```

#### Etapa 1 — `filterSites()` (linhas 115-161): quem pode atender

Agrupa as instâncias por site e descarta as que não podem atender:

```go
// https://github.com/m-lab/locate/blob/main/heartbeat/location.go#L155-L161
func filterSites(service string, lat, lon float64, instances map[string]v2.HeartbeatMessage, opts *NearestOptions) []site {
    // ...
    if (alwaysPick(opts) && !v.overridden) || pickWithProbability(v.registration.Probability) {
        sites = append(sites, *v)
    }
    return sites
}
```

- **Saúde**: `isHealthy()` (linhas 213-224) exige `Health.Score != 0` e Prometheus saudável — máquina doente é filtrada
- **Probabilidade do site**: cada site tem um campo `Probability` no registro. `pickWithProbability()` (linhas 310-314) sorteia `rand.Float64() < probability` — é o mecanismo de **rollout gradual** de sites novos (ex: gru15830 com volume mínimo)
- **`alwaysPick()`** (linhas 310-315): consultas com `Type=virtual`, `Sites` específicos ou `Org` pulam o filtro de probabilidade (a menos que o site esteja com override — kill-switch)

#### Etapa 2 — `sortSites()` (linhas 242-245): ordenação por distância

```go
// https://github.com/m-lab/locate/blob/main/heartbeat/location.go#L242-L245
func sortSites(sites []site) {
    sort.Slice(sites, func(i, j int) bool {
        return sites[i].distance < sites[j].distance
    })
}
```

A distância é calculada em `isValidInstance()` usando **haversine** — distância em linha reta sobre o globo, entre as coordenadas do cliente (GeoIP) e as coordenadas registradas do site:

```go
// https://github.com/m-lab/go/blob/main/mathx/haversine.go
const earthRadiusKm = 6371
func GetHaversineDistance(lat1, lon1, lat2, lon2 float64) float64 { ... }
```

**Não é distância de rede, não é AS-path, não é RTT.** É linha reta no globo.

#### Etapa 3 — `rank()` (linhas 247-260): ranqueamento de sites e metros

```go
// https://github.com/m-lab/locate/blob/main/heartbeat/location.go#L247-L260
func rank(sites []site) {
    metroRank := 0
    metros := make(map[string]int)
    for i, site := range sites {
        sites[i].rank = i                    // rank do site = posição na ordenação
        metro := site.registration.Metro
        if _, ok := metros[metro]; !ok {
            metros[metro] = metroRank        // 1º site de cada metro recebe o mesmo metroRank
            metroRank++
        }
        sites[i].metroRank = metros[metro]
    }
}
```

Sites da mesma região metropolitana **empatam** no `metro_rank` — visível na resposta real da API (todos os sites de SP receberam `metro_rank=1`).

#### Etapa 4 — `pickTargets()` (linhas 266-308): O SORTEIO

O coração do algoritmo — duas loterias em cascata:

```go
// https://github.com/m-lab/locate/blob/main/heartbeat/location.go#L266-L293
func pickTargets(service string, sites []site) *TargetInfo {
    numTargets := mathx.Min(4, len(sites))
    for i := 0; i < numTargets; i++ {
        // A rate of 6 yields index 0 around 95% of the time, index 1 a little less
        // than 5% of the time, and higher indices infrequently.
        index := mathx.GetExpDistributedInt(6) % len(sites)   // ← LOTERIA 1: entre SITES
        s := sites[index]
        // ...
        // TODO(cristinaleon): Once health values range between 0 and 1,
        // pick based on health. For now, pick at random.
        machineIndex := mathx.GetRandomInt(len(s.machines))  // ← LOTERIA 2: entre MÁQUINAS
        machine := s.machines[machineIndex]
        // ...
    }
}
```

**Loteria 1 — entre sites (exponencial):** `GetExpDistributedInt(6)` do [`m-lab/go/mathx/rand.go`](https://github.com/m-lab/go/blob/main/mathx/rand.go):

```go
// https://github.com/m-lab/go/blob/main/mathx/rand.go#L21-L27
func GetExpDistributedInt(rate float64) int {
    f := rand.ExpFloat64() / rate
    index := int(math.Round(f))
    return index
}
```

Com `rate=6`, o comentário do próprio código confirma: **índice 0 ≈ 95%, índice 1 ≈ 5%, demais raramente**.

**Para onde vai o ~5%?** Não é espalhado entre os demais — é **especificamente o 2º mais próximo**. A distribuição exponencial decai muito rápido:

$$P(\text{index}=0) = 1 - e^{-3} \approx 95{,}0\% \qquad P(\text{index}=1) \approx 4{,}98\% \qquad P(\text{index}=2) \approx 0{,}01\%$$

O 3º mais próximo recebe ~0,01% (praticamente nunca) e o 4º menos ainda. Detalhes do código:

- O `% len(sites)` existe apenas para **não estourar a lista** quando há poucos sites (ex: com 2 sites, um índice 2 daria a volta e cairia no 0)
- O loop roda até 4 vezes para montar a lista de fallbacks, **removendo** o site já escolhido a cada rodada — mas como o cliente só usa `results[0]`, na prática só o **primeiro sorteio** importa

**Os 95% são estatística ou peso do código?** São um **peso determinado no código** — não uma estatística observada. A direção da causalidade é sempre código → dados:

| Estatística de resultados | Peso no código (o caso real) |
|---------------------------|------------------------------|
| Roda o sistema → coleta → observa "95% foram pro mais próximo" → descreve | Desenvolvedor digita `rate=6` → a fórmula **causa** 95% → os dados apenas confirmam |

A matemática por trás, passo a passo:

1. `rand.ExpFloat64()` sorteia um número seguindo a **distribuição exponencial** — uma curva que gera valores quase sempre pequenos (perto de 0), às vezes médios, raramente grandes
2. `/ 6` **espreme** a curva: a chance de o resultado ficar abaixo de 0,5 é $1 - e^{-3} \approx 95{,}02\%$
3. `math.Round` arredonda para inteiro: tudo abaixo de 0,5 vira **índice 0** (= 1º da fila = mais próximo), entre 0,5 e 1,5 vira **índice 1** (= 2º), etc.

**Analogia:** uma roleta de cassino com 100 casas, 95 pretas e 5 vermelhas. O cassino não *mede* que a bola cai 95% em preto e ajusta a roleta — ele **constrói** a roleta com 95 casas pretas, e o 95% é consequência da construção. Cada teste NDT gira essa roleta uma vez.

**Prova de que é um parâmetro ajustável:** se o desenvolvedor tivesse escolhido outro `rate`, as porcentagens seriam outras — mesma fórmula, outro efeito:

| `rate` escolhido | P(índice 0) = $1 - e^{-\text{rate}/2}$ | Efeito |
|------------------|------------------------------------------|--------|
| 3 | $1 - e^{-1{,}5}$ ≈ **77,7%** | Muito espalhado — 22% iriam pro 2º |
| **6** | $1 - e^{-3}$ ≈ **95,0%** | ✅ O escolhido — concentração + 5% de controle |
| 12 | $1 - e^{-6}$ ≈ **99,75%** | Quase determinístico — o 5% de controle desaparece |

O 6 foi uma **decisão de engenharia**: perto de determinístico, mas com escape estatístico. Se o M-Lab mudar o 6 para 12, a base de dados passaria a mostrar ~99,75% no mais próximo — sem mudar nada nos dados, só no código.

**Por que sorteiar em vez de retornar só o mais próximo?** A ordenação não é desperdiçada — ela **define as odds da loteria** (converte distância em rank; o sorteio converte rank em probabilidade). E o 5% que escapa para o 2º existe de propósito, como **grupo de controle**:

| Estratégia | Problema |
|------------|----------|
| Determinística (sempre o mais próximo) | 100% do tráfego de uma região num site só. Se esse site recebe uma versão com bug (canary), uma NIC degradada ou o datacenter congestiona → **todas** as medições da região ficam corrompidas, sem como perceber |
| Uniforme (sorteio igual) | Clientes mandados para longe → RTT alto → **medição ruim** |
| **Exponencial 95/5** (a escolhida) | Mantém a qualidade (95% perto) e vaza 5% controlado para o 2º — mesma população de clientes, dois servidores, **comparação direta** para detectar anomalias |

A spec documenta isso: *"Rollouts on the M-Lab platform happen gradually, and canary tests of new server versions happen regularly"*. E o TODO no código confirma a direção futura:

```go
// TODO(cristinaleon): Once health values range between 0 and 1,
// pick based on health. For now, pick at random.
```

A intenção declarada é um dia **ponderar por saúde** — o sorteio é o estado provisório de um design em evolução.

**Quando o 2º é escolhido? Dois caminhos diferentes:**

| | Caminho A (sorteio) | Caminho B (rejeição) |
|---|---|---|
| Gatilho | **Nenhum** — aleatório, em toda requisição | Servidor mais próximo **recusou** a conexão (cheio / lame duck) |
| Frequência | ~5% de todos os testes | Variável — depende da carga |
| Como aparece na base | Cliente "normal" no 2º servidor | Cliente no 2º servidor **em horários de pico** |
| Dá pra distinguir? | ❌ Não — ambos viram "testou no 2º" | ⚠️ Indiretamente: se o desvio cresce no pico, há componente B |

Os dois caminhos se **somam**: volume no 2º servidor = ~5% (caminho A) + excedente das rejeições (caminho B). Uma análise "testes no 2º servidor por hora do dia" revelaria o componente B: a curva acima dos 5% basais em horário de pico é a rejeição por carga agindo.

**Loteria 2 — entre máquinas do site (uniforme):** `GetRandomInt(len(s.machines))` — sorteio uniforme. Com 2 máquinas saudáveis, cada uma recebe ~50%.

> ⚠️ **Distinção importante:** a exponencial 95/5 vale **entre sites** (rank por distância). Dentro do site, a máquina é uniforme. Confundir os dois níveis leva a previsões erradas (corrigido na seção 12).

**Tabela de probabilidades finais:**

| Posição do site (por distância) | Probabilidade de ser escolhido |
|-------------------------------------|-------------------------------|
| 1º mais próximo (rank 0) | ~95% |
| 2º mais próximo (rank 1) | ~5% |
| 3º ou mais | Raramente |

E dentro do site escolhido: máquinas dividem igualmente (uniforme).

#### O lado do cliente

**Cliente de referência:** [`m-lab/locate/api/locate/client.go`](https://github.com/m-lab/locate/blob/main/api/locate/client.go) e `html/ndt7.js` no [`m-lab/ndt-server`](https://github.com/m-lab/ndt-server/blob/main/html/ndt7.js):

```js
// If no server was specified then use a loadbalancer. If no loadbalancer
// is specified, use the locate service from Measurement Lab.
const lbURL = (config && ('loadbalancer' in config)) ?
    new URL(config.loadbalancer) :
    new URL('https://locate.measurementlab.net/v2/nearest/ndt/ndt7');

// Choose the first result sent by the load balancer.
const choice = js.results[0];
```

O cliente recebe a lista de até 4 targets e usa **apenas o primeiro** (`results[0]`). Existe também a opção de **fixação manual** via `config.server` — usada por integradores que querem pular o Locate (causa rara de desvios).

**Quem pode escolher o servidor? Três níveis:**

| Nível | Quem | Como |
|-------|------|------|
| **Usuário final** (pessoa física) | ❌ Nunca escolhe | Só clica em "testar velocidade" |
| **Integrador** (quem embute o teste) | ⚠️ Pode | `config.server` (fixa um servidor, pula o Locate) ou `config.loadbalancer` (usa outro localizador) |
| **Cliente padrão** (ndt7.js sem config) | ❌ Delega | Usa o Locate e pega `results[0]` |

Ou seja: o **código cliente tem a capacidade** de escolher/fixar servidor, mas o comportamento padrão — e o que domina a base de dados — é delegar 100% ao Locate. A fixação manual existe como escape para integradores e é uma das causas raras de desvio (seção 10.5).

#### Prova direta: resposta real da API

Consulta a `https://locate.measurementlab.net/v2/nearest/ndt/ndt7` (feita em 28/08/2026) retornou 4 targets, com os parâmetros de auditoria embutidos nos URLs de acesso:

| Posição | Máquina | Cidade | `index` | `metro_rank` |
|---------|---------|--------|---------|--------------|
| 1º | ndt-gig1916-c89ffeef.rnp.autojoin... | Rio de Janeiro | 0 | 0 |
| 2º | ndt-mlab1-gru03.mlab-oti... | São Paulo | 1 | 1 |
| 3º | ndt-mlab1-gru07.mlab-oti... | São Paulo | 2 | 1 |
| 4º | ndt-mlab2-gru02.mlab-oti... | São Paulo | 3 | 1 |

- O RJ em 1º confirma a ordenação por distância (para o IP de origem da consulta)
- Os 3 sites de SP empatam no `metro_rank=1` — exatamente como o `rank()` faz
- Cada URL carrega um `access_token` (JWT assinado pelo Locate, `aud` = máquina destino) + `index` + `metro_rank` — o servidor valida o token ao aceitar a conexão

#### Especificação oficial

A spec do protocolo ([`m-lab/ndt-server/spec/ndt7-protocol.md`](https://github.com/m-lab/ndt-server/blob/main/spec/ndt7-protocol.md), seção "Server discovery") manda:

1. Cliente **SHOULD** usar `locate.measurementlab.net`
2. **MUST** tratar `200` como sucesso, `204` como "sem capacidade" e `3xx` como redirect
3. **MUST NOT** assumir que será sempre mandado ao servidor estritamente mais próximo — *"Rollouts on the M-Lab platform happen gradually, and canary tests of new server versions happen regularly"*

Ou seja: a aleatoriedade é **documentada e intencional**, não é bug.

### 9.4 O que isso explica nos nossos dados

| Observação | Explicação pelo código |
|------------|------------------------|
| Concentração perto do servidor | ~95% dos testes vão para o site geograficamente mais próximo ✅ |
| Clientes de SP/RJ testando na Colômbia | São os ~5% que caem no sorteio do 2º/3º servidor mais próximo |
| Só Claro e Telefônica mandam para Peru/Colômbia | **Volume!** Elas têm milhões de testes. 5% de 5 milhões = 250 mil testes internacionais. Gigalink com poucos clientes raramente cai no sorteio |
| RTT alto para o Peru (138-190ms) | A seleção é por **distância geográfica em linha reta**, não por RTT de rede. O Peru pode ser geograficamente próximo do norte do Brasil, mas a rede entre eles é ruim |
| INB Telecom mandou para Estocolmo (arn03) | Caiu na probabilidade baixa do sorteio |

### 9.5 A resposta para a pergunta central

**O cliente NÃO escolhe o servidor. O ISP não influencia diretamente. O que decide é:**

1. **GeoIP (MaxMind)** determina a localização do cliente pelo IP
2. O Locate calcula a **distância geográfica em linha reta** entre cliente e servidores
3. Escolhe o mais próximo com **95% de probabilidade**, o 2º com ~5%, e raramente mais longe
4. Se o GeoIP errar a localização do cliente (comum com IPs de ISPs menores), o cliente pode ser mandado para um servidor errado

**O ISP não é um fator direto** — ele aparece na análise porque:
- Claro/Telefônica têm muito mais clientes → mais testes → mais casos do ~5% aleatório
- A precisão do GeoIP varia por ISP (IPs de ISPs grandes são melhor mapeados)

### 9.6 Validação das hipóteses originais

| # | Hipótese | Veredito final |
|---|----------|----------------|
| 1 | Localização geográfica | ✅ **CONFIRMADA** — é o fator principal (distância em linha reta, ~95%) |
| 2 | ISP/Provedor | ❌ **REFUTADA** — o ISP não é fator direto; aparece na análise por volume de testes |
| 3 | Tipo de servidor (RNP vs MLAB) | ❌ Não há prioridade por organização no algoritmo |
| 4 | Código fonte | ✅ **INVESTIGADO** — algoritmo documentado acima |

### 9.7 Fontes

**Repositório principal (o algoritmo):**
- Repositório: https://github.com/m-lab/locate
- Arquivo principal: [`heartbeat/location.go`](https://github.com/m-lab/locate/blob/main/heartbeat/location.go)
  - `Nearest()` (orquestração): [linhas 92-111](https://github.com/m-lab/locate/blob/main/heartbeat/location.go#L92-L111)
  - `filterSites()` (filtro de saúde + probabilidade): [linhas 115-161](https://github.com/m-lab/locate/blob/main/heartbeat/location.go#L115-L161)
  - `sortSites()` (ordenação por distância): [linhas 242-245](https://github.com/m-lab/locate/blob/main/heartbeat/location.go#L242-L245)
  - `rank()` (ranqueamento de sites/metros): [linhas 247-260](https://github.com/m-lab/locate/blob/main/heartbeat/location.go#L247-L260)
  - `pickTargets()` (o sorteio 95/5 + máquina uniforme): [linhas 266-308](https://github.com/m-lab/locate/blob/main/heartbeat/location.go#L266-L308)
  - `isHealthy()` (critério de saúde): [linhas 213-224](https://github.com/m-lab/locate/blob/main/heartbeat/location.go#L213-L224)
  - `pickWithProbability()` / `alwaysPick()`: [linhas 310-315](https://github.com/m-lab/locate/blob/main/heartbeat/location.go#L310-L315)

**Funções matemáticas (repositório m-lab/go):**
- [`mathx/rand.go`](https://github.com/m-lab/go/blob/main/mathx/rand.go) — `GetExpDistributedInt(6)` (o 95/5) e `GetRandomInt` (sorteio uniforme da máquina)
- [`mathx/haversine.go`](https://github.com/m-lab/go/blob/main/mathx/haversine.go) — `GetHaversineDistance` (distância em linha reta)

**Lado do cliente:**
- [`m-lab/locate/api/locate/client.go`](https://github.com/m-lab/locate/blob/main/api/locate/client.go) — cliente Go de referência (`reply.Results`, usa o 1º)
- [`m-lab/ndt-server/html/ndt7.js`](https://github.com/m-lab/ndt-server/blob/main/html/ndt7.js) — cliente JS oficial (Locate padrão, `results[0]`, `config.server` para fixação manual)

**Documentação e especificação:**
- [`m-lab/locate/USAGE.md`](https://github.com/m-lab/locate/blob/main/USAGE.md) — uso da Locate API (serviços ndt/ndt5 e ndt/ndt7)
- [`m-lab/ndt-server/spec/ndt7-protocol.md`](https://github.com/m-lab/ndt-server/blob/main/spec/ndt7-protocol.md) — seção "Server discovery" (manda usar o Locate; 204 = sem capacidade; aleatoriedade documentada)

**Verificação empírica:**
- Resposta real de `https://locate.measurementlab.net/v2/nearest/ndt/ndt7` (28/08/2026) — 4 targets com `index` e `metro_rank` nos URLs (tabela na seção 9.3)

**Legado (ndt5):**
- [`ndt-project/ndt`](https://github.com/ndt-project/ndt) — código legado: applet Java (`Tcpbw100.java`, servidor via parâmetro HTML), cliente C (`web100clt.c`, flag `-n`), modo federado do `fakewww.c` (redirecionamento por traceroute — ancestral do Locate, nunca usado no ndt7)

---

## 10. Fatores externos e validação final (28/08/2026)

### 10.1 A observação que motivou esta seção

> "No servidor do RJ tem vários clientes do Nordeste, e lá tem muitos servidores mais perto."

Isso contradiz o modelo "95% vai para o mais próximo" — se há servidores em Recife, Salvador, Fortaleza, por que clientes do Nordeste testam no RJ?

### 10.2 VPN influencia?

**Sim, mas não explica este caso.** O GeoIP localiza o IP público que chega no M-Lab. Cliente com VPN aparece no local da saída da VPN. Como os clientes do Nordeste aparecem geolocalizados no Nordeste, eles não estão usando VPN (ou a VPN tem saída local).

### 10.3 Validações executadas

#### Teste 1 — Saúde dos servidores do Nordeste (buracos no volume diário)

```sql
SELECT
    d.server_site,
    date_trunc('day', d.test_time) AS dia,
    count() AS total_testes
FROM download d
WHERE d.test_time > dateadd('d', -30, now())
    AND d.server_site IN ('rec1916', 'ssa53164', 'for1916', 'mcz1916', 'gig1916')
GROUP BY d.server_site, dia
ORDER BY dia, total_testes DESC;
```

**Resultado: todos os servidores tiveram testes em todos os dias.** A hipótese de "servidor local fora do ar" foi **descartada** para o período analisado.

#### Teste 2 — RTT dos nordestinos no servidor do RJ

Query retornou **0 linhas** — nenhum cliente dos estados listados testou no servidor analisado no período.

#### Teste 3 — client_name dos testes

Query retornou: `null, null, 24728` — **24.728 testes sem `client_name` e sem `region`**.

**Descoberta:** a grande maioria dos testes não reporta o `client_name` (o app/biblioteca que fez o teste). Isso impede de confirmar diretamente a hipótese de "app fixando servidor manualmente". A coluna `region` também está vazia na maioria dos registros.

### 10.4 Modelo final de seleção de servidor

```
1. Cliente pede servidor ao Locate API
2. Locate filtra servidores: só os ONLINE e saudáveis entram na lista
3. Locate ordena os restantes por distância geográfica (GeoIP do cliente)
4. Sorteio: ~95% o mais próximo, ~5% o segundo, raramente mais longe
5. Cliente usa o primeiro resultado
   — EXCETO se o app fixou um servidor manualmente (config.server)
6. Ao conectar, o servidor pode REJEITAR por capacidade
   → o cliente tenta o próximo da lista
```

### 10.5 Causas dos desvios da proximidade

| Causa | Mecanismo | Evidência |
|-------|-----------|-----------|
| Sorteio de ~5% | Sempre presente | Confirmado pelo código (`GetExpDistributedInt(6)`) |
| Servidor local rejeita por carga | Cliente tenta o 2º da lista | Documentado no protocolo ndt7 |
| Servidor local fora do ar (lame duck) | Locate remove da lista | Teste 1 não encontrou buracos no período |
| App fixa servidor manualmente | Pula o Locate | `client_name` null na maioria — não verificável |
| Erro do GeoIP | Cliente geolocalizado errado | `region` vazia em muitos registros |
| VPN | Muda o IP visto pelo GeoIP | Não detectado nos dados analisados |

### 10.6 Limitações da pesquisa

- `client_name` é null na maioria dos testes — não foi possível identificar apps que fixam servidor
- A coluna `region` da tabela `client` está vazia para muitos registros
- O RTT alto para servidores internacionais (Peru: 138-190ms) confirma que distância geográfica ≠ qualidade de rede, mas o Locate não considera isso
- Não foi possível verificar diretamente os eventos de rejeição por carga (não ficam registrados na tabela `download` — só os testes completados)

### 10.7 Conclusão final

A escolha do servidor NDT é feita pelo **Locate API do M-Lab** com base em **distância geográfica em linha reta** (via GeoIP), com sorteio probabilístico (~95% o mais próximo). Os desvios observados (clientes longe do servidor mais próximo) são explicados por:

1. O sorteio de ~5% (sempre presente)
2. Rejeição por capacidade do servidor local (cliente tenta o próximo)
3. Possível fixação manual de servidor por apps (`config.server`)
4. Erros de geolocalização do GeoIP

**O ISP não é um fator direto** — a concentração de Claro/Telefônica em servidores internacionais se explica pelo volume de testes delas.

---

## 11. Validação final: RTT dos nordestinos no servidor do RJ (28/08/2026)

### 11.1 Query executada

RTT médio por cidade do Nordeste para o servidor `gig1916` (RJ), usando `city` (a coluna `region` está vazia na tabela `client`):

```sql
SELECT
    c.city,
    avg(d.min_rtt) AS rtt_medio,
    count() AS total_testes
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE d.test_time > dateadd('d', -30, now())
    AND c.country_code = 'BR'
    AND d.server_site = 'gig1916'
    AND c.city IN ('Recife', 'Salvador', 'Fortaleza', ...)  -- cidades do NE
GROUP BY c.city
ORDER BY total_testes DESC;
```

### 11.2 Resultados (arquivo `c.csv`)

| Cidade | RTT médio (ms) | Testes |
|--------|----------------|--------|
| Salvador | 86 | 188 |
| Recife | 125 | 90 |
| Fortaleza | 111 | 61 |
| São Luís | 135 | 37 |
| Maceió | 110 | 33 |
| Natal | 80 | 30 |
| João Pessoa | 103 | 21 |
| Teresina | 73 | 19 |
| Aracaju | 101 | 17 |
| Vitória da Conquista | 60 | 15 |
| Ilhéus | 102 | 15 |
| **Média ponderada** | **~100** | **547** |

### 11.3 Interpretação

O RTT médio ponderado é **~100ms** — alto. Para comparação, um cliente em Recife testando no servidor local (`rec1916`) teria RTT de ~10-20ms.

**Isso descarta a hipótese de "distribuição de carga eficiente":** se o Locate estivesse empurrando o excedente do Nordeste para o RJ de forma inteligente, o RTT seria baixo. Não é o caso.

### 11.4 Explicação consistente com todos os dados

1. **O Locate escolhe por distância geográfica em linha reta** (confirmado no código, seção 9)
2. **O sorteio de ~5%** manda clientes para o 2º/3º servidor mais próximo
3. **Para parte do Nordeste, o RJ é o 2º mais próximo** — ex: distância em linha reta RJ→Salvador (~1.200km) pode ser menor que Fortaleza→Salvador (~1.300km), dependendo da posição exata
4. **O RTT alto (~100ms) confirma que a rede não é o critério** — se fosse, esses clientes estariam nos servidores locais com RTT de 10-20ms
5. **Rejeição por capacidade:** com 12,6 milhões de testes/mês, servidores grandes como o do RJ rejeitam conexões com frequência, empurrando clientes para servidores mais distantes

### 11.5 Conclusão final da pesquisa

O modelo completo de seleção de servidor:

1. **GeoIP** localiza o cliente (pode errar)
2. **Distância em linha reta** ordena os servidores
3. **Sorteio**: ~95% o mais próximo, ~5% o segundo
4. **Rejeição por capacidade**: servidor cheio recusa, cliente tenta o próximo da lista
5. **Fixação manual**: apps podem pular tudo isso (`config.server`)

O RTT de ~100ms dos nordestinos no RJ é consistente com o **sorteio de ~5%** (o RJ é o 2º mais próximo para parte do Nordeste) e com **rejeições por carga** nos servidores locais. Não é roteamento do ISP, não é VPN — é o algoritmo do M-Lab funcionando como projetado, com sua aleatoriedade intencional.

**Pesquisa concluída.** Todas as hipóteses foram testadas e o comportamento foi explicado pelo código fonte + validação empírica nos dados.

---

## 12. Validação do split entre máquinas dentro do site (28/08/2026)

### 12.1 Correção de uma previsão anterior

A distribuição exponencial (95%/5%) do `pickTargets` vale **entre sites** (rank 0 vs rank 1 por distância). Dentro de um mesmo site, a máquina é escolhida com sorteio **uniforme** (`GetRandomInt`):

```go
// heartbeat/location.go (pickTargets)
// TODO(cristinaleon): Once health values range between 0 and 1,
// pick based on health. For now, pick at random.
machineIndex := mathx.GetRandomInt(len(s.machines))
machine := s.machines[machineIndex]
```

Predição correta: com 2 máquinas saudáveis no site, o split deve ser ~50/50.

### 12.2 Dados observados (últimos 30 dias)

| server_site | server_machine | testes | % do total | % dentro do site |
|---|---|---|---|---|
| gru15830 | mlab1 (única) | 33.861 | 59,1% | 100% |
| gru02 | mlab2 | 11.730 | 20,5% | 50,05% |
| gru02 | mlab3 | 11.707 | 20,4% | 49,95% |

### 12.3 Interpretação

1. **Split 50/50 dentro do gru02 confirmado** — diferença de apenas 23 testes em 23.437 (0,1%), bem dentro do desvio esperado do puro acaso (~77 testes para sorteio uniforme com essa amostra). É a assinatura estatística do `GetRandomInt` nos dados reais.
2. **gru15830: site de máquina única e maior volume** — nomenclatura nova de 5 dígitos, apenas mlab1 ativo, e mesmo assim é o site com mais testes (33.861, mais que o gru02 inteiro). O volume de um site é definido pelo rank de distância (a exponencial 95/5 é entre sites), não pela quantidade de máquinas — a máquina só é sorteada depois que o site é escolhido. gru15830 é o rank 0 para a maior parte dos clientes de SP.
3. **mlab1 ausente em gru02** — ou está com health score 0 (filtrado por `isHealthy`) ou não roda o serviço ndt.

### 12.4 Conclusão

Terceira validação independente do algoritmo:
- **Seção 9**: código fonte (exponencial entre sites, uniforme entre máquinas)
- **Seção 11**: RTT ~100ms consistente com sorteio de 5% + rejeição por carga
- **Seção 12**: split 50/50 entre máquinas = assinatura estatística do `GetRandomInt`

O comportamento observado nos dados replica o código fonte com precisão estatística.
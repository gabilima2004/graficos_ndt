# Análise NDT — Resultados e Padrões

> Análise baseada nos dashboards do Grafana (Partes 1-4) e dados do QuestDB.
> Período: últimos 30 dias | Foco: provedor Claro (maior volume)

---

## 1. Visão Geral

| Métrica                    | Valor                    |
| -------------------------- | ------------------------ |
| Total de clientes          | 2.205.685                |
| Total de servidores        | 404                      |
| Total de testes (download) | 12.649.720               |
| Provedor com mais clientes | Claro (113.216 clientes) |

**Insight:** A Claro concentra ~41% dos testes de download (5,1M de 12,6M) e ~43% dos clientes. É o provedor dominante em volume — qualquer padrão encontrado nela tem grande impacto.

---

## 2. Métricas ao longo do tempo (Parte 2 — Time Series)

### 2.1 Download ao longo do tempo

**O que o gráfico mostra:**

- Faixa constante entre 0 e 200 Mbps (maior parte dos testes)
- Faixa diminuindo entre 200 e 400 Mbps
- Pontos esporádicos acima de 400 Mbps

**Interpretação:**

- A maioria dos clientes Claro tem download até 200 Mbps — compatível com planos residenciais de entrada (50, 100, 200 Mbps)
- A faixa 200-400 Mbps representa planos intermediários
- Acima de 400 Mbps são poucos clientes (planos premium/empresariais)
- A faixa ser **constante ao longo do tempo** significa que não há degradação sistemática — a qualidade da Claro é estável, não está piorando

### 2.2 Upload ao longo do tempo

**O que o gráfico mostra:**

- Faixa constante entre 0 e 100 Mbps
- Faixa diminuindo entre 100 e 200 Mbps
- Pontos esporádicos acima de 200 Mbps

**Interpretação:**

- Upload é significativamente menor que download (0-100 vs 0-200) — isso é **assimetria de plano**, típico de provedores brasileiros
- A Claro limita o upload nos planos residenciais (ex: plano de 100 Mbps download costuma ter 50 Mbps ou menos de upload)
- Upload acima de 200 Mbps é raro — provavelmente planos empresariais ou fibra simétrica

### 2.3 RTT ao longo do tempo (escala log)

**O que o gráfico mostra:**

- Faixa constante entre 32 e 128 ms
- Faixas menores entre 16-32 ms e 128-256 ms
- Pontos esporádicos abaixo de 16 ms e acima de 256 ms

**Interpretação:**

- RTT entre 32-128 ms é típico para conexões no Brasil (distância geográfica + roteamento)
- RTT abaixo de 16 ms seria ideal (cliente próximo ao servidor), mas é raro
- RTT acima de 256 ms indica problemas — cliente muito longe do servidor ou roteamento ineficiente
- **Por que escala log?** Porque RTT varia de 1 ms a 1000+ ms. Em escala linear, tudo abaixo de 100 ms ficaria amassado perto do zero. A escala log espalha os valores para conseguir ver a variação entre 16, 32, 64, 128 ms — cada "degrau" dobra o anterior.

### 2.4 Loss Rate ao longo do tempo (escala log)

**O que o gráfico mostra:**

- Faixa constante entre 0,8% e 6,3%
- Faixa menor entre 0,1% e 0,8%
- Pontos esporádicos abaixo de 0,1%

**Interpretação:**

- Loss rate de 0,8%-6,3% é **alto** — o ideal seria abaixo de 0,1%
- Isso indica que a rede da Claro tem perda de pacotes significativa para a maioria dos clientes
- Loss rate acima de 1% já causa impacto em videochamadas, jogos e VoIP
- **Por que escala log?** Porque loss rate varia de 0,001% a 50%. Em escala linear, tudo abaixo de 5% ficaria colado no zero. A escala log mostra a diferença entre 0,01%, 0,1%, 1% e 10% — cada degrau multiplica por 10.

---

## 3. Estatísticas por provedor (Parte 3 — Tabelas e Bar Charts)

### 3.1 Download — Comparação Claro vs Geral

| Métrica         | Geral      | Claro     | Diferença                              |
| --------------- | ---------- | --------- | -------------------------------------- |
| Total de testes | 12.618.647 | 5.152.269 | Claro = 41% do total                   |
| Clientes únicos | 2.202.968  | 951.704   | Claro = 43% dos clientes               |
| Média download  | 220 Mbps   | 121 Mbps  | Claro é **45% mais lenta** que a média |

**Insight:** A Claro tem média de download (121 Mbps) quase **metade** da média geral (220 Mbps). Isso significa que a Claro está **puxando a média geral para baixo**. Sem a Claro, a média geral seria ainda mais alta.

### 3.2 Upload — Comparação Claro vs Geral

| Métrica         | Geral      | Claro     | Diferença                              |
| --------------- | ---------- | --------- | -------------------------------------- |
| Total de testes | 10.217.304 | 4.017.473 | Claro = 39% do total                   |
| Clientes únicos | 1.801.708  | 782.519   | Claro = 43% dos clientes               |
| Média upload    | 163 Mbps   | 48,6 Mbps | Claro é **70% mais lenta** que a média |

**Insight:** O upload da Claro é ainda pior em relação à média. 48,6 Mbps vs 163 Mbps geral — a Claro entrega só **30%** da média geral de upload. Isso confirma a assimetria forte nos planos da Claro.

### 3.3 Ranking de medianas — Claro vs Gigalink

| Métrica          | Claro     | Gigalink  | Diferença                          |
| ---------------- | --------- | --------- | ---------------------------------- |
| Mediana download | 52 Mbps   | 672 Mbps  | Gigalink é **13x mais rápido**     |
| Mediana upload   | 24 Mbps   | 400 Mbps  | Gigalink é **17x mais rápido**     |
| RTT médio        | 81,5 ms   | 10,2 ms   | Gigalink tem **8x menos latência** |
| Loss rate médio  | 2,9%      | 3,84%     | Claro tem **menos perda**          |
| Total de testes  | 5.168.236 | 1.985.099 | Claro tem 2,6x mais testes         |

**Insights:**

- Gigalink domina em download, upload e RTT — é um provedor de nicho (provavelmente atende empresas ou regiões específicas com infraestrutura melhor)
- A Claro, apesar de ser a maior, está **muito atrás** em qualidade. Mediana de 52 Mbps significa que metade dos clientes Claro tem download abaixo de 52 Mbps
- **Curiosidade:** a Claro tem loss rate MENOR que Gigalink (2,9% vs 3,84%). Ou seja, a rede da Claro perde menos pacotes, mas é mais lota. Pode indicar que a Claro tem infraestrutura estável mas saturada, enquanto Gigalink pode ter menos perda em valor absoluto mas mais variabilidade

### 3.4 Por que a Claro não está no Top 10 de mediana?

A Claro tem 113 mil clientes — a maioria em planos residenciais de baixo custo. Provedores menores como Gigalink atendem menos clientes, provavelmente com planos melhores ou em regiões com infraestrutura superior. **Volume não significa qualidade.**

---

## 4. Padrões identificados

### 4.1 Padrão de download

- Distribuição assimétrica: maioria entre 0-200 Mbps, cauda longa até 400+
- Estável ao longo do tempo (sem degradação sazonal visível)
- Claro puxa a média geral para baixo

### 4.2 Padrão de upload

- Assimetria forte: upload é 50-70% menor que download
- Claro tem upload particularmente baixo (48,6 Mbps vs 163 Mbps geral)
- Indica planos com upload limitado (política comercial, não técnica)

### 4.3 Padrão de RTT

- Concentrado em 32-128 ms (típico do Brasil)
- Claro tem RTT alto (81,5 ms) — pode indicar roteamento ineficiente ou clientes distantes dos servidores
- Gigalink consegue 10,2 ms — mostra que é possível ter latência baixa no Brasil

### 4.4 Padrão de loss rate

- Maioria entre 0,8%-6,3% — **alto** para padrões internacionais
- Claro tem 2,9% — estável mas não ideal
- Loss rate alto + RTT alto = experiência degradada para aplicações sensíveis (jogos, videochamadas)

### 4.5 Padrão de volume — CUIDADO com comparações injustas

> **Aviso importante:** Comparar a mediana da Claro (52 Mbps) com a Gigalink (672 Mbps) e concluir "Claro é pior" é **enganoso**.

**Por que a comparação direta é injusta:**

- **Claro** tem 113 mil clientes — gente com plano de R$ 50 (10 Mbps), plano de R$ 100 (300 Mbps), empresa com fibra dedicada... tudo misturado. A mediana reflete o **mix de planos vendidos**, não a qualidade técnica.
- **Gigalink** tem poucos clientes — provavelmente um nicho específico (empresas, condomínios premium, região com fibra nova). Os dados são mais concentrados porque o público é mais homogêneo.

Se 80% dos clientes Claro têm plano de 50 Mbps, a mediana vai ser ~50 Mbps — e isso não significa que a Claro é ruim, significa que a maioria comprou plano barato.

**O que a mediana de download realmente indica:** qual é o plano típico que o provedor vende, não a qualidade da rede.

---

## 5. Como analisar de forma justa

### 5.1 Compare provedores do mesmo porte

Em vez de Claro vs Gigalink, compare:

- **Claro vs Telefônica** — ambas são grandes, atendem o mesmo mercado (residencial + empresarial)
- **Gigalink vs outros pequenos** — provedores regionais de tamanho similar

Isso é comparar "maçãs com maçãs".

### 5.2 RTT e Loss Rate são métricas mais justas

RTT e loss rate **não dependem do plano** — dependem da qualidade da infraestrutura:

- Um cliente de 10 Mbps pode ter RTT de 10 ms (excelente)
- Um cliente de 500 Mbps pode ter RTT de 200 ms (ruim)

Então comparar RTT e loss rate entre provedores é **mais justo** que comparar download.

| Métrica         | Depende do plano?                  | Justo para comparar? |
| --------------- | ---------------------------------- | -------------------- |
| Download/upload | ✅ Sim (plano define a velocidade) | ❌ Não diretamente   |
| RTT             | ❌ Não (depende da infraestrutura) | ✅ Sim               |
| Loss rate       | ❌ Não (depende da infraestrutura) | ✅ Sim               |

### 5.3 Consistência = qualidade

Um provedor bom entrega **sempre a mesma velocidade**. Um provedor ruim entrega 100 Mbps às 3h da manhã e 10 Mbps às 20h.

Para medir isso, olhe a **largura da faixa** no gráfico de time series (Parte 2):

- Faixa constante e estreita = consistente (bom)
- Faixa que varia muito ao longo do dia = inconsistente (ruim)

### 5.4 Padrões temporais são os mais reveladores

A pergunta mais interessante não é "quem é mais rápido" mas sim:

- **O download cai em horário de pico?** Se sim, a rede está saturada
- **O RTT aumenta à noite?** Se sim, há congestionamento
- **O loss rate sobe em algum período?** Se sim, há problema de capacidade

Isso sim indica qualidade técnica, independente do plano.

---

## 6. Comparação: Claro vs Telefônica (mesmo porte)

> Esta é a comparação **justa** — ambos são grandes provedores que atendem o mesmo mercado
> (residencial + empresarial) no Brasil.

### 6.1 Volume

| Métrica                    | Claro     | Telefônica | Diferença                            |
| -------------------------- | --------- | ---------- | ------------------------------------ |
| Testes download            | 5.152.269 | 4.665.566  | Claro 10% a mais                     |
| Clientes únicos (download) | 951.704   | 1.130.726  | **Telefônica tem 19% mais clientes** |
| Testes upload              | 4.017.473 | 3.521.244  | Claro 14% a mais                     |
| Clientes únicos (upload)   | 782.519   | 917.384    | **Telefônica tem 17% mais clientes** |

**Insight:** A Telefônica tem **mais clientes** que a Claro, mas a Claro tem **mais testes por cliente**. Isso significa que os clientes Claro fazem mais testes (talvez mais insatisfeitos? ou mais monitoramento automatizado?).

### 6.2 Download e Upload (depende do plano — interpretar com cuidado)

| Métrica          | Claro     | Telefônica | Geral    |
| ---------------- | --------- | ---------- | -------- |
| Média download   | 121 Mbps  | 181 Mbps   | 220 Mbps |
| Mediana download | 52 Mbps   | 88 Mbps    | —        |
| Média upload     | 48,6 Mbps | 108 Mbps   | 163 Mbps |
| Mediana upload   | 24 Mbps   | 54 Mbps    | —        |

**Interpretação (cuidado — depende do mix de planos):**

- A Telefônica vende planos com velocidades maiores que a Claro (mediana 88 vs 52 Mbps)
- A Telefônica tem upload significativamente maior (mediana 54 vs 24 Mbps)
- Ambas estão abaixo da média geral (220 Mbps) — os provedores grandes vendem planos mais baratos que os pequenos
- **Não podemos concluir que a Telefônica tem rede melhor** — pode ser que ela venda planos mais caros

### 6.3 RTT e Loss Rate (métricas justas — não dependem do plano)

| Métrica         | Claro   | Telefônica | Diferença                  |
| --------------- | ------- | ---------- | -------------------------- |
| RTT médio       | 81,5 ms | 26,4 ms    | **Telefônica é 3x melhor** |
| Loss rate médio | 2,9%    | 2,88%      | Praticamente igual         |

**Esta é a comparação que importa:**

1. **RTT: Telefônica é MUITO melhor (26,4 ms vs 81,5 ms)** — a rede da Telefônica tem 3x menos latência. Isso significa:
   - Clientes Telefônica estão mais próximos dos servidores NDT, OU
   - A infraestrutura de roteamento da Telefônica é muito mais eficiente
   - Para o usuário: videochamadas, jogos e VoIP funcionam muito melhor na Telefônica

2. **Loss rate: praticamente igual (2,9% vs 2,88%)** — ambos perdem a mesma quantidade de pacotes. Isso é ~3% de perda, que é **alto** para os dois. Ambos têm problema de qualidade na rede.

### 6.4 Padrões nos gráficos de time series

#### Claro (Parte 2)

- Download: faixa 0-200 Mbps, estável ao longo do tempo
- Upload: faixa 0-100 Mbps, estável
- RTT: faixa 32-128 ms (escala log)
- Loss rate: faixa 0,8%-6,3% (escala log)

#### Telefônica (Parte 2)

- Download: faixa 0-300 Mbps, estável — **faixa mais larga que a Claro** = mais variedade de planos
- Upload: faixa 0-200 Mbps, estável — **também mais larga que a Claro**
- RTT: faixa 8-64 ms (escala log) — **muito melhor que a Claro** (8-64 vs 32-128)
- Loss rate: faixa 0,8%-6,3% (escala log) — **igual à Claro**

#### Gigalink (Parte 2 — referência, não comparação justa)

- Download: faixas contínuas perto de 1000 Mbps e 400 Mbps — **dois clusters de planos** (provavelmente planos de 1 Gbps e 400 Mbps)
- Upload: faixas perto de 1000 Mbps e 200 Mbps — mesmos clusters
- RTT: faixa 8-16 ms — **excelente** (praticamente perfeito)
- Loss rate: faixa 0%-0,1% com pontos em 6,3% — a maioria tem perda quase zero, mas alguns têm perda alta

**Sobre os 0% no loss rate da Gigalink:** o NDT registra `loss_rate = 0` quando não houve nenhuma perda de pacotes durante o teste. Isso é comum em redes de alta qualidade (fibra dedicada). Aparece como linha no gráfico porque muitos testes tiveram perda exatamente zero. Na escala log, 0 não tem valor logarítmico, por isso aparece como linha no fundo do gráfico.

### 6.5 Resumo da comparação justa

| Métrica                  | Claro   | Telefônica | Quem ganha?                      |
| ------------------------ | ------- | ---------- | -------------------------------- |
| RTT (justo)              | 81,5 ms | 26,4 ms    | **Telefônica** (3x melhor)       |
| Loss rate (justo)        | 2,9%    | 2,88%      | Empate                           |
| Download mediano (plano) | 52 Mbps | 88 Mbps    | Telefônica vende planos melhores |
| Upload mediano (plano)   | 24 Mbps | 54 Mbps    | Telefônica vende planos melhores |
| Consistência temporal    | Estável | Estável    | Empate                           |

**Conclusão justa:** A Telefônica tem infraestrutura de rede **significativamente melhor** que a Claro (RTT 3x menor), vende planos com velocidades maiores, e tem a mesma estabilidade. A Claro perde em qualidade técnica (RTT) e em mix de planos.

---

## 7. Padrões identificados nos gráficos

### 7.1 Padrão de clusters (Gigalink)

O gráfico de download da Gigalink mostra **duas faixas contínuas distintas**: uma perto de 1000 Mbps e outra perto de 400 Mbps. Isso indica que a Gigalink vende **planos específicos** (provavelmente 1 Gbps e 400 Mbps) e os clientes recebem exatamente o que pagam — por isso as faixas são contínuas e estreitas.

Compare com a Claro, que tem uma faixa contínua de 0 a 200 Mbps — isso indica que a Claro vende **muitos planos diferentes** nessa faixa (10, 50, 100, 200 Mbps) e os clientes recebem velocidades variáveis.

**Padrão:** faixas estreitas e bem definidas = provedor com poucos planos específicos. Faixas largas e contínuas = provedor com muitos planos variados.

### 7.2 Padrão de RTT por porte de provedor

| Provedor   | RTT       | Porte   |
| ---------- | --------- | ------- |
| Gigalink   | 8-16 ms   | Pequeno |
| Telefônica | 8-64 ms   | Grande  |
| Claro      | 32-128 ms | Grande  |

**Padrão:** a Claro tem RTT pior que a Telefônica, mesmo sendo do mesmo porte. Isso não é questão de tamanho — é questão de **infraestrutura de roteamento**. A Telefônica provavelmente tem servidores NDT mais próximos de seus clientes ou roteamento mais eficiente.

### 7.3 Padrão de loss rate

Todos os provedores grandes (Claro e Telefônica) têm loss rate de ~2,9%. A Gigalink tem a maioria em 0%-0,1% mas com alguns picos em 6,3%.

**Padrão:** provedores grandes têm loss rate consistentemente alto (~3%). Provedores pequenos têm loss rate baixo na maioria, mas com variabilidade. Isso pode indicar que provedores grandes têm redes mais congestionadas.

### 7.4 Por que o loss rate da Gigalink tem vários 0%?

O NDT registra `loss_rate = 0` quando **nenhum pacote foi perdido** durante o teste. Em redes de alta qualidade (fibra dedicada, como provavelmente é o caso da Gigalink), é comum ter perda zero. No gráfico de escala log, o valor 0 não tem logaritmo (log(0) = -∞), por isso aparece como uma linha no fundo do gráfico.

Isso é na verdade um **bom sinal** — significa que muitos testes da Gigalink não tiveram nenhuma perda de pacotes.

---

## 8. Conclusões finais

### O que podemos afirmar com confiança

1. **Telefônica tem melhor infraestrutura que Claro** — RTT 26,4 ms vs 81,5 ms (comparação justa, não depende do plano)

2. **Claro e Telefônica têm loss rate igual** — ~2,9% para ambos. Ambos têm problema de perda de pacotes

3. **Telefônica vende planos melhores que Claro** — mediana 88 vs 52 Mbps de download, 54 vs 24 Mbps de upload

4. **Gigalink é um caso à parte** — rede de alta qualidade (RTT 8-16 ms, loss rate ~0%) mas atende nicho diferente, não é comparável com os grandes

5. **A Claro tem mais testes por cliente que a Telefônica** — pode indicar mais insatisfação ou mais monitoramento automatizado

### O que NÃO podemos afirmar

1. ❌ "A Claro é pior que a Gigalink" — públicos diferentes
2. ❌ "A Telefônica é melhor que a Claro em download" — a mediana reflete o mix de planos, não a qualidade técnica
3. ❌ "Provedores pequenos são sempre melhores" — a Gigalink é um caso específico

### Próximos passos sugeridos

1. **Rodar a query de padrão temporal** (Fase 4.1 do GUIA_ANALISE.md) para Claro e Telefônica — ver se o download cai em horário de pico
2. **Investigar quais servidores os clientes Claro usam** — se usam servidores distantes, o RTT alto é esperado
3. **Analisar a distribuição de download da Claro** — identificar clusters de velocidade (planos) e ver se a Claro entrega o que promete em cada faixa
4. **Comparar loss rate por horário** — o loss rate sobe em horário de pico? Se sim, há congestionamento

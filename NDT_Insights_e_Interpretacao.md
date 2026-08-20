# NDT — Insights e Interpretação dos Gráficos

> Guia prático para entender o que cada visualização do dashboard NDT revela e que decisões ela pode embasar.

---

## 1. Visão Geral (Parte 1)

### Total de Clientes

**O que mostra:** quantos clientes únicos fizeram testes no período filtrado.

**Insights:**

- Número alto = boa adesão/amostra estatística.
- Número baixo = poucos dispositivos testando; cuidado ao generalizar conclusões.
- Comparar com "Total de Testes" mostra se poucos clientes fizeram muitos testes ou muitos clientes fizeram poucos testes.

### Total de Servidores

**O que mostra:** quantos servidores de medição estão disponíveis.

**Insights:**

- Poucos servidores podem concentrar testes e criar gargalos geográficos.
- Muitos servidores espalhados permitem comparar performance por região.

### Total de Testes

**O que mostra:** volume total de medições no período.

**Insights:**

- Volume alto aumenta a confiança nas medianas e percentis.
- Se houver muito mais testes que clientes, pode indicar monitoramento automatizado ou poucos clientes testando repetidamente.

### Clientes por Provedor (Bar Chart)

**O que mostra:** distribuição de clientes entre os ISPs mapeados.

**Insights:**

- Provedores com muitos clientes têm peso maior nas análises agregadas.
- Provedores com poucos clientes podem ter mediana instável (outliers pesam mais).
- Útil para priorizar quais provedores merecem atenção.

### Mapa Cliente → Servidor (Geomap)

**O que mostra:** localização geográfica dos servidores e dos clientes que testaram.

**Insights:**

- Aglomerados de clientes longe dos servidores podem explicar RTT alto.
- Padrão geográfico pode indicar onde novos servidores seriam úteis.
- Comparação entre regiões ajuda a identificar problemas locais de infraestrutura.

---

## 2. Métricas no Tempo (Parte 2)

### Download ao longo do tempo

**O que mostra:** evolução da velocidade de download por provedor ao longo do tempo.

**Insights:**

- Quedas súbitas em todos os provedores = problema no servidor ou na infraestrutura de rede.
- Queda isolada em um provedor = problema específico daquele ISP.
- Picos fora do padrão podem ser outliers; a mediana (Parte 3) é mais confiável.

### Upload ao longo do tempo

**O que mostra:** evolução da velocidade de upload por provedor.

**Insights:**

- Upload geralmente é menor que download; se estiver muito baixo, afeta videoconferências e backup na nuvem.
- Assimetria muito grande entre download e upload pode indicar política de tráfego do provedor.

### RTT ao longo do tempo (escala log)

**O que mostra:** latência média por provedor ao longo do tempo.

**Insights:**

- RTT baixo (< 50 ms) = conexão responsiva, boa para jogos e chamadas.
- RTT alto (> 150 ms) = experiência degradada, possível roteamento ineficiente.
- Escala log ajuda a visualizar variações quando há valores muito discrepantes.

### Loss Rate ao longo do tempo (escala log)

**O que mostra:** taxa de perda de pacotes por provedor ao longo do tempo.

**Insights:**

- Loss rate próximo de 0 = rede estável.
- Loss rate > 1% já indica instabilidade perceptível em aplicações sensíveis.
- Picos de loss rate costumam acompanhar picos de RTT.

---

## 3. Estatísticas por Provedor (Parte 3)

### Tabelas de Download e Upload por Provedor

**O que mostra:** média, mediana, mínimo, máximo, total de testes e clientes únicos por ISP.

**Insights:**

- Compare **média** e **mediana**: se a média for muito maior que a mediana, há outliers puxando para cima (poucos testes muito rápidos).
- Mínimo e máximo mostram a amplitude de experiências dos clientes.
- A linha **TOTAL GERAL** permite comparar cada provedor contra a média/ mediana geral.

### Mediana de Download por Provedor (Bar Chart)

**O que mostra:** velocidade de download mediana por ISP.

**Insights:**

- Mediana representa a experiência do cliente típico.
- Provedores com mediana muito abaixo da média geral estão entregando menos do que o mercado.
- Útil para ranquear ISPs de forma justa (sem distorção de outliers).

### Mediana de Upload por Provedor (Bar Chart)

**O que mostra:** velocidade de upload mediana por ISP.

**Insights:**

- Upload baixo prejudica serviços em nuvem, streaming de vídeo e trabalho remoto.
- Provedores com upload muito assimétrico em relação ao download podem ter planos com upload limitado.

### RTT Médio por Provedor (Bar Chart)

**O que mostra:** latência média por ISP.

**Insights:**

- Ordenado do menor para o maior RTT: os primeiros são os mais responsivos.
- RTT alto pode indicar roteamento ineficiente, concentração de clientes longe dos servidores ou congestionamento.

### Loss Rate Médio por Provedor (Bar Chart)

**O que mostra:** taxa média de perda de pacotes por ISP.

**Insights:**

- Ordenado do menor para o maior loss rate: os primeiros são os mais estáveis.
- Loss rate alto indica problemas de qualidade de link, bufferbloat ou congestionamento.

### Total de Testes por Provedor (Bar Chart)

**O que mostra:** volume de testes por ISP.

**Insights:**

- Provedores com muitos testes têm amostra confiável.
- Provedores com poucos testes devem ser analisados com cautela.
- Pode indicar onde há mais interesse/insatisfação dos usuários.

---

## 4. Distribuição (Parte 4)

### Box Plot / Violin Plot de Download

**O que mostra:** distribuição completa das medições de download por provedor.

**Insights:**

- Caixa estreita e mediana alta = experiência consistente e boa.
- Caixa larga ou muitos outliers = grande variação de experiência entre clientes.
- Violin plot mostra se os valores se concentram em torno de poucas velocidades (planos) ou estão espalhados.

### Box Plot / Violin Plot de Upload

**O que mostra:** distribuição das medições de upload por provedor.

**Insights:**

- Similar ao download, mas revela assimetria entre download e upload.
- Provedores com upload concentrado em valores baixos provavelmente limitam upload nos planos.

### Box Plot / Violin Plot de RTT

**O que mostra:** distribuição da latência por provedor.

**Insights:**

- Mediana baixa com caixa pequena = latência estável e boa.
- Cauda longa para cima = alguns clientes sofrem com latência muito alta.
- Escala log ajuda a enxergar diferenças quando há valores extremos.

### Box Plot / Violin Plot de Loss Rate

**O que mostra:** distribuição da taxa de perda de pacotes por provedor.

**Insights:**

- Mediana próxima de 0 = rede estável para a maioria.
- Outliers altos = grupos de clientes com experiência ruim.
- Provedores com caixa alta têm instabilidade generalizada.

---

## Regras gerais de interpretação

| Métrica           | Quanto maior         | Quanto menor          |
| ----------------- | -------------------- | --------------------- |
| Download / Upload | Melhor               | Pior                  |
| RTT               | Pior (mais lento)    | Melhor (mais rápido)  |
| Loss Rate         | Pior (mais instável) | Melhor (mais estável) |
| Total de Testes   | Mais confiável       | Menos confiável       |

### Mediana vs Média

- Use a **mediana** para entender a experiência típica do cliente.
- Use a **média** para entender a capacidade agregada da rede.
- Se média >> mediana, existem outliers de alta velocidade.
- Se média << mediana, existem outliers de baixa velocidade.

### Filtros de outlier

Os dashboards já aplicam filtros padrão:

- `mean_throughput_mbps >= 0`
- `min_rtt >= 0 AND min_rtt <= 1500000`
- `loss_rate >= 0`

Esses filtros evitam que valores inválidos distorçam as visualizações.

---

## Possíveis ações a partir dos insights

1. **Provedor com mediana de download baixa:** investigar planos comerciais, infraestrutura ou capacidade de backbone.
2. **RTT alto em região específica:** verificar se há servidor próximo; se não houver, avaliar instalação.
3. **Loss rate alto:** sinalizar instabilidade de rede, possivelmente congestionamento ou falha de equipamento.
4. **Poucos clientes de um provedor:** ampliar amostra antes de tomar decisões drásticas.
5. **Mapa mostrando clientes distantes dos servidores:** planejar expansão de pontos de presença.

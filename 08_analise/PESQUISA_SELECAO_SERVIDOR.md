# Pesquisa: Como o cliente escolhe o servidor NDT?

> Data: 26/08/2026
> Objetivo: Descobrir os fatores que determinam qual servidor NDT um cliente usa para fazer o teste.

---

## 1. Contexto

O NDT (Network Diagnostic Tool) do M-Lab mede a qualidade da conexão (download, upload, RTT, loss rate). Para fazer o teste, o cliente se conecta a um servidor NDT. Existem servidores no Brasil e no exterior (Peru, EUA, Europa, etc.).

**Pergunta central:** O que determina qual servidor o cliente usa? É proximidade geográfica? É o ISP? É o NDT que escolhe? É o usuário?

---

## 2. Hipóteses levantadas

| # | Hipótese | Status |
|---|----------|--------|
| 1 | **Localização geográfica** — o NDT escolhe o servidor mais próximo fisicamente | ⚠️ Parcialmente confirmada |
| 2 | **ISP/Provedor** — o roteamento do ISP determina qual servidor é "visto" como perto | ⚠️ Parcialmente confirmada |
| 3 | **Tipo de servidor** (RNP vs MLAB) — servidores de diferentes operadoras têm prioridade diferente | ⏳ Não investigada |
| 4 | **Código fonte** — a lógica de seleção no código do NDT define o comportamento | ⏳ A investigar |

---

## 3. Metodologia

### Ferramentas usadas

- **Mapa Cliente→Servidor** (Grafana Geomap): mostra onde estão os clientes que usam um servidor específico, com cor/tamanho por quantidade de testes
- **Mapa de Servidores** (Grafana Geomap): mostra todos os servidores disponíveis
- **Filtro `$isp`**: permite filtrar por provedor
- **Filtro `$server`**: permite selecionar um servidor específico
- **Queries no console do QuestDB**: para extrair RTT e estatísticas

### Abordagem

1. Selecionar um servidor no mapa e observar de onde vêm os clientes
2. Filtrar por ISP e ver quais provedores mandam tráfego para aquele servidor
3. Medir o RTT dos clientes que usam servidores distantes
4. Comparar com a localização geográfica e o roteamento do ISP

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

### 5.1 A hipótese de localização geográfica

**Parcialmente confirmada.** A maioria dos testes vai para servidores próximos, mas há exceções significativas (clientes no Brasil usando servidor no Peru).

### 5.2 A hipótese de ISP

**Parcialmente confirmada, mas com ressalva.** Apenas 3 ISPs (Claro, Telefônica, ALLREDE) mandaram tráfego para o Peru. Outros ISPs não mandaram. Isso indica que o ISP é um fator — mas não o único.

**A ressalva:** O RTT alto (138-190ms) sugere que o Peru **não é eficiente** em termos de rede para esses clientes. Se o ISP tivesse roteamento eficiente para o Peru, o RTT seria baixo. O fato de ser alto significa que:

- O ISP **influencia** qual servidor é escolhido (só alguns ISPs mandam para o Peru)
- Mas **não é porque o Peru é perto** em termos de rede para esses ISPs
- O NDT está mandando clientes para um servidor distante mesmo com RTT alto

### 5.3 Possíveis explicações para o RTT alto

| # | Explicação | Como confirmar |
|---|-----------|----------------|
| A | **Load balancing** — servidores brasileiros estavam saturados e o NDT distribuiu para o Peru | Verificar se o volume de testes nos servidores BR era alto no período |
| B | **Algoritmo de seleção com bug** — o "locator" do M-Lab retornou servidor errado | Olhar código fonte do M-Lab |
| C | **Cliente escolheu manualmente** — alguns clientes NDT permitem especificar servidor | Verificar se o NDT client permite isso |
| D | **GeoIP/DNS errado** — o serviço de localização achou que o cliente era do Peru | Verificar se os IPs dos clientes são brasileiros |
| E | **Capacidade do servidor** — o servidor do Peru tinha menos carga | Verificar métricas de carga dos servidores |

### 5.4 Por que só Claro, Telefônica e ALLREDE?

Se a explicação for **load balancing** (A), todos os ISPs deveriam mandar para o Peru ocasionalmente. Mas só 3 mandaram. Isso sugere que **há um fator do ISP** além do load balancing.

Possível explicação: o NDT faz um "probe" inicial (mede RTT para alguns servidores) e escolhe o de menor RTT. Se o roteamento da Claro/Telefônica/ALLREDE faz o probe para o Peru retornar RTT menor do que o probe para SP (mesmo que o RTT real do teste seja alto depois), o NDT escolhe o Peru.

**Isso seria um problema do algoritmo de seleção** — o RTT do probe pode ser diferente do RTT do teste real.

---

## 6. Próximos passos

### 6.1 Investigar o código fonte do M-Lab

- Como funciona o "server selection" / "locator"?
- O cliente mede RTT para múltiplos servidores antes de escolher?
- Há load balancing?
- O cliente pode escolher manualmente?

Repositórios relevantes:
- https://github.com/m-lab/ndt-server (servidor)
- https://github.com/m-lab/ndt7-client (cliente)
- https://github.com/m-lab/locate (serviço de localização)

### 6.2 Verificar load balancing

Rodar query para ver o volume de testes por servidor no período:

```sql
SELECT
    d.server_site,
    count() AS total_testes
FROM download d
WHERE d.test_time > dateadd('d', -30, now())
GROUP BY d.server_site
ORDER BY total_testes DESC
LIMIT 20;
```

Se os servidores brasileiros estavam com volume muito alto, a hipótese de load balancing ganha força.

### 6.3 Verificar se o cliente pode escolher o servidor

Olhar no código do ndt7-client se há opção de especificar servidor manualmente.

### 6.4 Comparar RTT do probe vs RTT do teste

Se possível, verificar se o NDT mede RTT para múltiplos servidores antes de escolher (probe) e se esse RTT do probe difere do RTT do teste real.

---

## 7. Conclusão parcial

A escolha do servidor NDT **não é puramente geográfica** e **não é puramente por ISP**. Os fatores identificados até agora:

1. **Localização geográfica** — é o fator principal para a maioria dos testes (concentração perto do servidor)
2. **ISP** — influencia quais servidores são considerados (só alguns ISPs mandam para o Peru)
3. **Fator não identificado** — o RTT alto para o Peru sugere que há algo além de proximidade e ISP (possivelmente load balancing, bug no algoritmo, ou escolha manual)

A investigação do código fonte do M-Lab é necessária para confirmar qual é o fator não identificado.

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
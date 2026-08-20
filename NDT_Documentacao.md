# Documentação — NDT (Network Diagnostic Tool)

## 1. O que é o NDT?

O **NDT (Network Diagnostic Tool)** é uma ferramenta de medição de desempenho de rede desenvolvida e mantida pelo **M-Lab (Measurement Lab)**, um consórcio de pesquisa que estuda o desempenho da Internet em escala global.

### Em termos simples:

O NDT mede a **capacidade de uma conexão de internet** para transferência de dados em "volume" (bulk transport), ou seja, o quanto de dados consegue fluir pela conexão de forma sustentada. É o tipo de teste que você faz quando quer saber "qual a minha velocidade de internet?".

### O que o NDT mede:

- **Velocidade de download** (dados vindo do servidor até o cliente)
- **Velocidade de upload** (dados indo do cliente até o servidor)
- **Latência** (tempo de ida e volta — RTT)
- **Taxa de perda de pacotes** (quantos pacotes se perdem no caminho)

### Como funciona:

1. Um **cliente** (seu computador, celular, etc.) se conecta a um **servidor** NDT
2. O servidor envia dados para o cliente (teste de **download**)
3. O cliente envia dados para o servidor (teste de **upload**)
4. Durante a transferência, são coletadas estatísticas da conexão TCP
5. Os resultados são armazenados com informações sobre quem testou, de onde, e quando

### Por que isso é importante?

Os dados do NDT são usados por pesquisadores, governos e organizações para:

- Estudar a qualidade da internet em diferentes regiões
- Comparar o desempenho entre provedores (ISPs)
- Identificar problemas de infraestrutura
- Embasar políticas públicas de telecomunicações

---

## 2. Estrutura do Banco de Dados

A base contém **4 tabelas** principais:

| Tabela     | Descrição                                                                    |
| ---------- | ---------------------------------------------------------------------------- |
| `client`   | Informações sobre o cliente que realizou o teste (geolocalização, ASN, etc.) |
| `download` | Resultados dos testes de download                                            |
| `upload`   | Resultados dos testes de upload                                              |
| `server`   | Informações sobre os servidores NDT                                          |

### Relacionamentos:

- As tabelas `download` e `upload` referenciam o `client` através de `client_ip` e `client_name`
- As tabelas `download` e `upload` referenciam o `server` através de `server_ip`, `server_site` e `server_machine`

---

## 3. Tabela `client` — Informações do Cliente

Esta tabela armazena dados sobre **quem** realizou o teste e **de onde**.

| Coluna           | Descrição                                                           |
| ---------------- | ------------------------------------------------------------------- |
| `client_ip`      | Endereço IP do cliente que realizou o teste                         |
| `continent_code` | Código do continente (ex: SA, NA, EU)                               |
| `country_code`   | Código do país (ex: BR, US, PT)                                     |
| `country_name`   | Nome completo do país (ex: Brazil)                                  |
| `region`         | Estado ou região dentro do país                                     |
| `city`           | Cidade do cliente                                                   |
| `postal_code`    | Código postal / CEP                                                 |
| `latitude`       | Latitude geográfica                                                 |
| `longitude`      | Longitude geográfica                                                |
| `cidr`           | Bloco CIDR do IP (notação de roteamento de rede)                    |
| `asn`            | Número do Sistema Autônomo (AS) — identifica o provedor de internet |
| `as_name`        | Nome do Sistema Autônomo (nome do provedor/ISP)                     |
| `client_name`    | Nome/identificador do cliente                                       |
| `early_exit`     | Indica se o cliente encerrou o teste antes de concluí-lo            |
| `update_time`    | Data/hora da última atualização do registro                         |

### Conceito-chave: ASN (Autonomous System Number)

Um **ASN** é um número único que identifica uma rede autônoma na internet — geralmente um provedor de internet (ISP) ou uma grande organização. Por exemplo, o ASN 28571 é a Telefônica/Vivo no Brasil. Isso permite agrupar testes por provedor.

---

## 4. Tabela `download` — Testes de Download

Esta tabela armazena os resultados dos testes de **download** (servidor → cliente).

| Coluna                 | Descrição                                                     |
| ---------------------- | ------------------------------------------------------------- |
| `uuid`                 | Identificador único do teste                                  |
| `test_time`            | Data/hora em que o teste foi realizado                        |
| `mean_throughput_mbps` | Velocidade média de download em Mbps (megabits por segundo)   |
| `min_rtt`              | Menor tempo de ida e volta (Round Trip Time) em milissegundos |
| `loss_rate`            | Taxa de perda de pacotes (0 a 1, onde 0 = sem perda)          |
| `version`              | Versão do software NDT usado                                  |
| `git_short_commit`     | Hash curto do commit do código-fonte                          |
| `server_ip`            | IP do servidor NDT usado no teste                             |
| `server_port`          | Porta do servidor                                             |
| `client_ip`            | IP do cliente (chave para a tabela `client`)                  |
| `client_port`          | Porta do cliente                                              |
| `client_name`          | Nome/identificador do cliente                                 |
| `server_site`          | Site (localização) do servidor                                |
| `server_machine`       | Máquina específica dentro do site do servidor                 |
| `server_asn`           | ASN do servidor                                               |
| `client_asn`           | ASN do cliente                                                |

### Conceito-chave: Throughput (Vazão)

O **throughput** é a quantidade de dados que consegue passar pela conexão por segundo. É o que chamamos popularmente de "velocidade da internet". Medido em **Mbps** (megabits por segundo).

### Conceito-chave: RTT (Round Trip Time)

O **RTT** é o tempo que um pacote leva para ir do cliente até o servidor e voltar. É uma medida de **latência**. Um RTT baixo (ex: 20ms) significa uma conexão mais responsiva. RTT alto (ex: 200ms+) causa lag em jogos, videochamadas, etc.

### Conceito-chave: Loss Rate (Taxa de Perda)

A **taxa de perda de pacotes** indica a porcentagem de pacotes que se perdem no caminho entre cliente e servidor. Perdas altas degradam significativamente a conexão, causando retransmissões e lentidão.

---

## 5. Tabela `upload` — Testes de Upload

Esta tabela armazena os resultados dos testes de **upload** (cliente → servidor).

> **Atenção:** A estrutura é **idêntica** à tabela `download`! As colunas são as mesmas, com os mesmos significados. A única diferença é a **direção** do teste.

| Coluna                 | Descrição                              |
| ---------------------- | -------------------------------------- |
| `uuid`                 | Identificador único do teste           |
| `test_time`            | Data/hora em que o teste foi realizado |
| `mean_throughput_mbps` | Velocidade média de upload em Mbps     |
| `min_rtt`              | Menor RTT em milissegundos             |
| `loss_rate`            | Taxa de perda de pacotes               |
| `version`              | Versão do software NDT                 |
| `git_short_commit`     | Hash curto do commit                   |
| `server_ip`            | IP do servidor                         |
| `server_port`          | Porta do servidor                      |
| `client_ip`            | IP do cliente                          |
| `client_port`          | Porta do cliente                       |
| `client_name`          | Nome do cliente                        |
| `server_site`          | Site do servidor                       |
| `server_machine`       | Máquina do servidor                    |
| `server_asn`           | ASN do servidor                        |
| `client_asn`           | ASN do cliente                         |

---

## 6. Tabela `server` — Informações dos Servidores

Esta tabela armazena dados sobre os **servidores NDT** que realizam os testes.

| Coluna           | Descrição                                     |
| ---------------- | --------------------------------------------- |
| `site`           | Nome do site (localização) do servidor        |
| `machine`        | Nome da máquina específica dentro do site     |
| `server_ip`      | IP do servidor                                |
| `continent_code` | Código do continente onde o servidor está     |
| `country_code`   | Código do país                                |
| `country_name`   | Nome do país                                  |
| `region`         | Estado/região                                 |
| `city`           | Cidade                                        |
| `postal_code`    | Código postal                                 |
| `latitude`       | Latitude geográfica                           |
| `longitude`      | Longitude geográfica                          |
| `cidr`           | Bloco CIDR do servidor                        |
| `asn`            | ASN do servidor                               |
| `as_name`        | Nome do AS do servidor                        |
| `machine_zone`   | Zona/datacenter onde a máquina está hospedada |
| `machine_type`   | Tipo da máquina (configuração de hardware)    |
| `update_time`    | Data/hora da última atualização               |

---

## 7. Resumo Visual — Como as Tabelas se Conectam

```
┌─────────────┐         ┌──────────────┐
│   client    │◄────────│   download   │
│             │ client_ │              │
│  client_ip  │  ip     │  server_ip   │
│  client_name│         │  server_site │
│  asn        │         │  server_machine│
└─────────────┘         └──────┬───────┘
                               │
                               │ server_ip
                               │ server_site
                               │ server_machine
                               ▼
┌─────────────┐         ┌──────────────┐
│   server    │◄────────│   upload     │
│             │         │              │
│  server_ip  │         │  client_ip   │
│  site       │         │  client_name │
│  machine    │         │  server_ip   │
└─────────────┘         └──────────────┘
```

---

## 8. Glossário de Termos Técnicos

| Termo          | Significado                                                      |
| -------------- | ---------------------------------------------------------------- |
| **NDT**        | Network Diagnostic Tool — ferramenta de teste de velocidade      |
| **M-Lab**      | Measurement Lab — organização que mantém o NDT                   |
| **Throughput** | Vazão — quantidade de dados transferidos por segundo (Mbps)      |
| **RTT**        | Round Trip Time — tempo de ida e volta de um pacote (ms)         |
| **Loss Rate**  | Taxa de perda de pacotes (0 a 1)                                 |
| **ASN**        | Autonomous System Number — identificador do provedor de internet |
| **AS**         | Autonomous System — rede autônoma na internet                    |
| **ISP**        | Internet Service Provider — provedor de internet                 |
| **CIDR**       | Classless Inter-Domain Routing — notação para blocos de IP       |
| **TCP**        | Transmission Control Protocol — protocolo de transporte          |
| **UUID**       | Universally Unique Identifier — identificador único do teste     |

---

## 9. Referências

- [M-Lab — NDT (Network Diagnostic Tool)](https://www.measurementlab.net/tests/ndt/)
- [M-Lab — Data Overview](https://www.measurementlab.net/data/)
- [Repositório ndt-server no GitHub](https://github.com/m-lab/ndt-server)

---

> **Nota:** Esta documentação serve como base para a criação de gráficos no Grafana. Compreender o significado de cada coluna é essencial para construir visualizações corretas e significativas.

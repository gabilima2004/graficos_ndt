# Mapeamento de ISPs — Normalização de as_name

## O problema

A coluna `as_name` da tabela `client` vem do registro de ASNs no LACNIC.
Cada ASN é registrado independentemente, gerando variações no nome da mesma empresa:

- `CLARO S.A.` / `Claro S/A` → mesma empresa (Claro)
- `TELEFÔNICA BRASIL S.A` / `Telefonica Data S.A.` → mesma empresa (Telefônica)

## A solução

Criar um mapeamento `asn → nome_normalizado` e usar como filtro no Grafana.

### Arquivo de mapeamento

O arquivo `isp_mapping.csv` contém duas colunas:

| Coluna     | Descrição                                  |
| ---------- | ------------------------------------------ |
| `asn`      | O número do ASN (chave na tabela `client`) |
| `isp_name` | O nome normalizado do provedor             |

### Como usar no Grafana

1. Criar uma tabela no QuestDB com o mapeamento
2. Fazer JOIN nas queries com essa tabela
3. Criar a variável do Grafana baseada no nome normalizado

---

## Mapeamento completo (baseado no CSV fornecido)

| asn    | as_name original                                   | isp_name (normalizado) |
| ------ | -------------------------------------------------- | ---------------------- |
| 18881  | TELEFÔNICA BRASIL S.A                              | Telefônica             |
| 26599  | TELEFÔNICA BRASIL S.A                              | Telefônica             |
| 27699  | TELEFÔNICA BRASIL S.A                              | Telefônica             |
| 19182  | TELEFÔNICA BRASIL S.A                              | Telefônica             |
| 10429  | Telefonica Data S.A.                               | Telefônica             |
| 28573  | CLARO S.A.                                         | Claro                  |
| 4230   | CLARO S.A.                                         | Claro                  |
| 22085  | Claro S/A                                          | Claro                  |
| 265303 | TV Alphaville Sistema de TV por Assinatura LTDA    | TV Alphaville          |
| 14868  | COPEL Telecomunicações S.A.                        | COPEL Telecom          |
| 53184  | INB Telecom EIRELI - ME                            | INB Telecom            |
| 262907 | AVATO TECNOLOGIA                                   | Avato Tecnologia       |
| 61844  | NEW MASTER PROVEDOR DE ACESSO A INTERNET           | New Master             |
| 28258  | Powerline Internet                                 | Powerline Internet     |
| 273683 | (sem nome)                                         | Desconhecido           |
| 22689  | Sercomtel Participações S.A.                       | Sercomtel              |
| 53062  | G G NET - Telecomunicações LTDA EPP                | G G Net                |
| 264228 | BRASIL STARLINK TELECOMUNICACOES LTDA - EPP        | Brasil Starlink        |
| 28669  | America-NET Ltda.                                  | America Net            |
| 263645 | FIXTELL TELECOM                                    | Fixtell Telecom        |
| 266949 | DIVIFIBRA TELECOMUNICAÇÕES LTDA EPP                | Divifibra              |
| 262700 | Efibra Telecom LTDA - EPP                          | Efibra Telecom         |
| 28658  | Gigalink de Nova Friburgo Soluções em Rede Multimi | Gigalink               |
| 262673 | Lafaiete Provedor de Internet e Telecomunic Ltda   | Lafaiete               |
| 52900  | QUALITY TELECOM SERVIÇOS DE COMUNICAÇÃO LTDA EPP   | Quality Telecom        |
| 263629 | CELLONI DIST. DE EQUIP. DE INF. E TECNOLOGIA LTDA  | Celloni                |
| 52940  | NEMESIS Provedor de Acesso as Redes de Comunicação | Nemesis                |
| 262671 | S & M Informática Ltda.                            | S & M Informática      |
| 28241  | Viaceu Internet Ltda                               | Viaceu Internet        |
| 53191  | PLUG Telecom                                       | Plug Telecom           |
| 28263  | Ensite Brasil Telecomunicações Ltda - ME           | Ensite Brasil          |
| 263072 | BD Fibra Telecom Ltda - EPP                        | BD Fibra Telecom       |
| 53171  | Omni Telecomunicacoes Ltda                         | Omni Telecom           |

> **Nota:** Se novos ASNs aparecerem no futuro, basta adicionar linhas ao mapeamento.

# Documentação da Base NDT — QuestDB (setembro/2025)

> **Atualizado em:** 29/09/2026
> **QuestDB:** 10.246.47.179:9000 (console HTTP em `/console`, extração via `/exp`)
> **Plugin Grafana:** `questdb-questdb-datasource` (UID: `dfudvhox4xudce`)
> **Compatibilidade:** QuestDB é compatível com o protocolo PostgreSQL — o Grafana usa o datasource PostgreSQL.

---

## 1. Visão geral

Base reimportada em setembro/2026. A grande mudança: **as colunas do cliente foram EMBUTIDAS nas tabelas de teste** (`download`/`upload`) — não existe mais a tabela `client` separada. Isso elimina o JOIN nas queries e acelera tudo.

| Tabela | O que é | Linhas (aprox.) |
|--------|---------|-----------------|
| `download` | 1 linha por teste de download | ~33M |
| `upload` | 1 linha por teste de upload | ~33M |
| `server` | Cadastro dos sites/servidores | ~20k |
| `ASNS` | Dimensão de ASNs (nome + dono) | ~100k |

---

## 2. Tabela `download`

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `uuid` | string | Identificador único do teste |
| `test_time` | timestamp | Momento do teste (**use `$__timeFilter(test_time)`**) |
| `mean_throughput_mbps` | double | Throughput médio do teste (Mbps) |
| `min_rtt` | double | Menor RTT observado (ms) |
| `loss_rate` | double | Taxa de perda de pacotes (fração 0-1; multiplique por 100 para %) |
| `version` | string | Versão do ndt-server (ex: v0.25.3) |
| `git_short_commit` | string | Commit do código do servidor |
| `server_ip` | string | IP do servidor usado |
| `server_port` | int | Porta |
| `client_ip` | string | IP do cliente |
| `client_port` | int | Porta |
| `client_name` | string | Nome do app/biblioteca (null na maioria) |
| `server_site` | string | **Código do site** (ex: gru02, gig1916) — chave de agrupamento |
| `server_machine` | string | Máquina dentro do site (mlab1, mlab2, mlab3) |
| `server_asn` | string | ASN do servidor |
| `client_asn` | string | **ASN do cliente (STRING — sempre entre aspas: `'28573'`)** |
| `client_country_code` | string | País do cliente (ex: `BR`) |
| `client_city` | string | Cidade do cliente (GeoIP, city-level) |
| `client_postalcode` | string | CEP |
| `client_latitude` | double | Latitude do cliente |
| `client_longitude` | double | Longitude do cliente |
| `client_cidr` | string | CIDR do IP |
| `client_asname` | string | Nome do ASN do cliente (bruto, sem normalizar) |

## 3. Tabela `upload`

Mesmas colunas do `download`, com **um typo**: `client_longitute` (sem o "d") **além de** `client_longitude`. Nas queries, prefira `client_longitude` (existe nas duas tabelas).

## 4. Tabela `server` — cadastro dos sites

| Coluna | Descrição |
|--------|-----------|
| `site` | Código do site (gru02, gig1916...) — **equivale ao `server_site` do download** |
| `machine` | Máquina (mlab1, mlab2...) |
| `server_ip` | IP do servidor |
| `continent_code`, `country_code`, `country_name`, `region`, `city`, `postal_code` | Localização |
| `latitude`, `longitude` | Coordenadas registradas do site |
| `cidr` | Faixa de IP |
| `asn`, `as_name` | ASN do site (ex: AS1916 = RNP) |
| `server_type` | `physical` ou `virtual` |
| `machine_zone`, `machine_type` | Zona/tipo da máquina |
| `update_time` | Atualização do cadastro (dedup por site: manter o mais recente) |

**Nota:** a tabela `server` tem ~20k linhas (uma por máquina × atualização de cadastro). Para a lista de sites, deduplique por `site` mantendo o `update_time` mais recente.

## 5. Tabela `ASNS` — dimensão de provedores

| Coluna | Descrição |
|--------|-----------|
| `ASN` | Número do ASN (string) |
| `ASN_name` | Nome do registro do ASN |
| `ASN_owner` | **Dono da empresa (nome normalizado — use como "provedor")** |
| `update_at` | Atualização |

**Uso:** substitui o antigo `CASE WHEN` hardcoded de 33 ASNs. Para filtrar por provedor:

```sql
JOIN ASNS a ON d.client_asn = a.ASN
-- e use a.ASN_owner como nome do provedor
```

---

## 6. Mudanças vs. schema antigo (o que quebra)

| Antes | Agora | Ação nas queries |
|-------|-------|------------------|
| Tabela `client` + JOIN `ON d.client_ip = c.client_ip` | Colunas embutidas em `download`/`upload` | **Remover o JOIN**; usar `d.client_city`, `d.client_latitude` etc. direto |
| `c.asn`, `c.as_name` | `d.client_asn`, `d.client_asname` | Trocar a referência |
| `CASE WHEN c.asn IN (...) THEN 'Nome'` | `JOIN ASNS a ON d.client_asn = a.ASN` → `a.ASN_owner` | Substituir o CASE pelo JOIN |
| `c.latitude`, `c.longitude` | `d.client_latitude`, `d.client_longitude` | Trocar a referência |
| `c.country_code` | `d.client_country_code` | Trocar |
| `c.city` | `d.client_city` | Trocar |
| — | `server_type` na tabela `server` | Novo: physical/virtual |
| — | `ASNS.ASN_owner` | Nome normalizado do provedor |

## 7. Macros e convenções do Grafana

- `$__timeFilter(d.test_time)` — filtro de período (dois underscores)
- `$__conditionalAll(condição, $var)` — evite; prefira `= '$var'` direto ou `IN ($var)` com variável multi-value
- ASN é **STRING**: `d.client_asn IN ('28573', '4230')`
- `count()` sem argumentos = `count(*)`
- `approx_median(col)` = mediana no QuestDB
- Coluna de tempo para séries temporais: `AS "time"` (aspas duplas obrigatórias)

## 8. Variáveis de dashboard (padrão dos dashboards)

### `$isp` (filtro por provedor) — versão nova com a tabela ASNS

```sql
SELECT ASN_owner AS __text, ASN_owner AS __value
FROM ASNS
WHERE ASN_owner IS NOT NULL AND ASN_owner != ''
GROUP BY ASN_owner
ORDER BY ASN_owner
```

(multi-value, includeAll)

### `$server` (filtro por servidor)

```sql
SELECT DISTINCT server_site AS __text, server_site AS __value
FROM download
WHERE server_site IS NOT NULL
ORDER BY server_site
```

### `$cidade` (filtro por cidade)

```sql
SELECT DISTINCT client_city AS __text, client_city AS __value
FROM download
WHERE client_country_code = 'BR' AND client_city IS NOT NULL
ORDER BY client_city
```

---

## 9. Contexto do mecanismo de seleção (resumo para as queries)

- O Locate do M-Lab escolhe o servidor por **distância haversine** (linha reta) + sorteio exponencial 95/5
- Cada site tem um campo `Probability` no cadastro (sites físicos OTI = 1,0; virtuais = 0,05-0,5; RNP autojoin ≈ 0,08)
- **Consequência:** a localização do servidor NÃO é proxy de proximidade do cliente — um teste "no Rio" pode ser de um cliente de Curitiba
- Documentação completa: `analise_selecao_servidores/PESQUISA_SELECAO_SERVIDOR.md` e `09_validacao_selecao/COMPROVACAO_PRIORIDADES.md`
# Mapeamento de ISPs — CASE WHEN direto nas queries (sem VIEW)

> O `CASE WHEN` é repetido em cada query. Se um novo ASN aparecer, atualize em todas as queries.
>
> **Importante:** No QuestDB, a coluna `asn` é do tipo STRING. Todos os ASNs vão entre aspas simples.

---

## Bloco CASE WHEN (usado em todas as queries)

```sql
CASE
    WHEN c.asn IN ('18881', '26599', '27699', '19182', '10429') THEN 'Telefônica'
    WHEN c.asn IN ('28573', '4230', '22085') THEN 'Claro'
    WHEN c.asn IN ('265303') THEN 'TV Alphaville'
    WHEN c.asn IN ('14868') THEN 'COPEL Telecom'
    WHEN c.asn IN ('53184') THEN 'INB Telecom'
    WHEN c.asn IN ('262907') THEN 'Avato Tecnologia'
    WHEN c.asn IN ('61844') THEN 'New Master'
    WHEN c.asn IN ('28258') THEN 'Powerline Internet'
    WHEN c.asn IN ('273683') THEN 'Desconhecido'
    WHEN c.asn IN ('22689') THEN 'Sercomtel'
    WHEN c.asn IN ('53062') THEN 'G G Net'
    WHEN c.asn IN ('264228') THEN 'Brasil Starlink'
    WHEN c.asn IN ('28669') THEN 'America Net'
    WHEN c.asn IN ('263645') THEN 'Fixtell Telecom'
    WHEN c.asn IN ('266949') THEN 'Divifibra'
    WHEN c.asn IN ('262700') THEN 'Efibra Telecom'
    WHEN c.asn IN ('28658') THEN 'Gigalink'
    WHEN c.asn IN ('262673') THEN 'Lafaiete'
    WHEN c.asn IN ('52900') THEN 'Quality Telecom'
    WHEN c.asn IN ('263629') THEN 'Celloni'
    WHEN c.asn IN ('52940') THEN 'Nemesis'
    WHEN c.asn IN ('262671') THEN 'S & M Informática'
    WHEN c.asn IN ('28241') THEN 'Viaceu Internet'
    WHEN c.asn IN ('53191') THEN 'Plug Telecom'
    WHEN c.asn IN ('28263') THEN 'Ensite Brasil'
    WHEN c.asn IN ('263072') THEN 'BD Fibra Telecom'
    WHEN c.asn IN ('53171') THEN 'Omni Telecom'
    ELSE c.as_name
END
```

> **Nota:** O `ELSE c.as_name` garante que ASNs não mapeados mostrem o nome original em vez de NULL.

---

## 1. Variável do Grafana — Filtro por ISP

Na configuração da variável `isp`, use esta query:

```sql
SELECT DISTINCT
    CASE
        WHEN asn IN ('18881', '26599', '27699', '19182', '10429') THEN 'Telefônica'
        WHEN asn IN ('28573', '4230', '22085') THEN 'Claro'
        WHEN asn IN ('265303') THEN 'TV Alphaville'
        WHEN asn IN ('14868') THEN 'COPEL Telecom'
        WHEN asn IN ('53184') THEN 'INB Telecom'
        WHEN asn IN ('262907') THEN 'Avato Tecnologia'
        WHEN asn IN ('61844') THEN 'New Master'
        WHEN asn IN ('28258') THEN 'Powerline Internet'
        WHEN asn IN ('273683') THEN 'Desconhecido'
        WHEN asn IN ('22689') THEN 'Sercomtel'
        WHEN asn IN ('53062') THEN 'G G Net'
        WHEN asn IN ('264228') THEN 'Brasil Starlink'
        WHEN asn IN ('28669') THEN 'America Net'
        WHEN asn IN ('263645') THEN 'Fixtell Telecom'
        WHEN asn IN ('266949') THEN 'Divifibra'
        WHEN asn IN ('262700') THEN 'Efibra Telecom'
        WHEN asn IN ('28658') THEN 'Gigalink'
        WHEN asn IN ('262673') THEN 'Lafaiete'
        WHEN asn IN ('52900') THEN 'Quality Telecom'
        WHEN asn IN ('263629') THEN 'Celloni'
        WHEN asn IN ('52940') THEN 'Nemesis'
        WHEN asn IN ('262671') THEN 'S & M Informática'
        WHEN asn IN ('28241') THEN 'Viaceu Internet'
        WHEN asn IN ('53191') THEN 'Plug Telecom'
        WHEN asn IN ('28263') THEN 'Ensite Brasil'
        WHEN asn IN ('263072') THEN 'BD Fibra Telecom'
        WHEN asn IN ('53171') THEN 'Omni Telecom'
        ELSE as_name
    END AS __text,
    CASE
        WHEN asn IN ('18881', '26599', '27699', '19182', '10429') THEN 'Telefônica'
        WHEN asn IN ('28573', '4230', '22085') THEN 'Claro'
        WHEN asn IN ('265303') THEN 'TV Alphaville'
        WHEN asn IN ('14868') THEN 'COPEL Telecom'
        WHEN asn IN ('53184') THEN 'INB Telecom'
        WHEN asn IN ('262907') THEN 'Avato Tecnologia'
        WHEN asn IN ('61844') THEN 'New Master'
        WHEN asn IN ('28258') THEN 'Powerline Internet'
        WHEN asn IN ('273683') THEN 'Desconhecido'
        WHEN asn IN ('22689') THEN 'Sercomtel'
        WHEN asn IN ('53062') THEN 'G G Net'
        WHEN asn IN ('264228') THEN 'Brasil Starlink'
        WHEN asn IN ('28669') THEN 'America Net'
        WHEN asn IN ('263645') THEN 'Fixtell Telecom'
        WHEN asn IN ('266949') THEN 'Divifibra'
        WHEN asn IN ('262700') THEN 'Efibra Telecom'
        WHEN asn IN ('28658') THEN 'Gigalink'
        WHEN asn IN ('262673') THEN 'Lafaiete'
        WHEN asn IN ('52900') THEN 'Quality Telecom'
        WHEN asn IN ('263629') THEN 'Celloni'
        WHEN asn IN ('52940') THEN 'Nemesis'
        WHEN asn IN ('262671') THEN 'S & M Informática'
        WHEN asn IN ('28241') THEN 'Viaceu Internet'
        WHEN asn IN ('53191') THEN 'Plug Telecom'
        WHEN asn IN ('28263') THEN 'Ensite Brasil'
        WHEN asn IN ('263072') THEN 'BD Fibra Telecom'
        WHEN asn IN ('53171') THEN 'Omni Telecom'
        ELSE as_name
    END AS __value
FROM client
ORDER BY 1
```

> **Atenção:** O Grafana precisa de `__text` (o que aparece no dropdown) e `__value` (o que é usado nas queries). Como não temos view, repetimos o CASE duas vezes — uma para text, uma para value.
>
> Marque **"Include All option"** e **"Multi-value"**.

---

## 2. Total de Clientes Únicos (Stat)

```sql
SELECT count(DISTINCT client_ip) AS total_clientes
FROM download
WHERE $__timeFilter(test_time)
```

> Esta query não precisa de JOIN nem filtro de ISP — mostra o total geral.

---

## 3. Localização dos Clientes (Geomap)

```sql
SELECT
    c.latitude AS lat,
    c.longitude AS lon,
    c.client_ip,
    CASE
        WHEN c.asn IN ('18881', '26599', '27699', '19182', '10429') THEN 'Telefônica'
        WHEN c.asn IN ('28573', '4230', '22085') THEN 'Claro'
        WHEN c.asn IN ('265303') THEN 'TV Alphaville'
        WHEN c.asn IN ('14868') THEN 'COPEL Telecom'
        WHEN c.asn IN ('53184') THEN 'INB Telecom'
        WHEN c.asn IN ('262907') THEN 'Avato Tecnologia'
        WHEN c.asn IN ('61844') THEN 'New Master'
        WHEN c.asn IN ('28258') THEN 'Powerline Internet'
        WHEN c.asn IN ('273683') THEN 'Desconhecido'
        WHEN c.asn IN ('22689') THEN 'Sercomtel'
        WHEN c.asn IN ('53062') THEN 'G G Net'
        WHEN c.asn IN ('264228') THEN 'Brasil Starlink'
        WHEN c.asn IN ('28669') THEN 'America Net'
        WHEN c.asn IN ('263645') THEN 'Fixtell Telecom'
        WHEN c.asn IN ('266949') THEN 'Divifibra'
        WHEN c.asn IN ('262700') THEN 'Efibra Telecom'
        WHEN c.asn IN ('28658') THEN 'Gigalink'
        WHEN c.asn IN ('262673') THEN 'Lafaiete'
        WHEN c.asn IN ('52900') THEN 'Quality Telecom'
        WHEN c.asn IN ('263629') THEN 'Celloni'
        WHEN c.asn IN ('52940') THEN 'Nemesis'
        WHEN c.asn IN ('262671') THEN 'S & M Informática'
        WHEN c.asn IN ('28241') THEN 'Viaceu Internet'
        WHEN c.asn IN ('53191') THEN 'Plug Telecom'
        WHEN c.asn IN ('28263') THEN 'Ensite Brasil'
        WHEN c.asn IN ('263072') THEN 'BD Fibra Telecom'
        WHEN c.asn IN ('53171') THEN 'Omni Telecom'
        ELSE c.as_name
    END AS isp_name,
    c.country_name,
    c.city,
    count() AS total_testes
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE $__timeFilter(d.test_time)
    AND CASE
        WHEN c.asn IN ('18881', '26599', '27699', '19182', '10429') THEN 'Telefônica'
        WHEN c.asn IN ('28573', '4230', '22085') THEN 'Claro'
        WHEN c.asn IN ('265303') THEN 'TV Alphaville'
        WHEN c.asn IN ('14868') THEN 'COPEL Telecom'
        WHEN c.asn IN ('53184') THEN 'INB Telecom'
        WHEN c.asn IN ('262907') THEN 'Avato Tecnologia'
        WHEN c.asn IN ('61844') THEN 'New Master'
        WHEN c.asn IN ('28258') THEN 'Powerline Internet'
        WHEN c.asn IN ('273683') THEN 'Desconhecido'
        WHEN c.asn IN ('22689') THEN 'Sercomtel'
        WHEN c.asn IN ('53062') THEN 'G G Net'
        WHEN c.asn IN ('264228') THEN 'Brasil Starlink'
        WHEN c.asn IN ('28669') THEN 'America Net'
        WHEN c.asn IN ('263645') THEN 'Fixtell Telecom'
        WHEN c.asn IN ('266949') THEN 'Divifibra'
        WHEN c.asn IN ('262700') THEN 'Efibra Telecom'
        WHEN c.asn IN ('28658') THEN 'Gigalink'
        WHEN c.asn IN ('262673') THEN 'Lafaiete'
        WHEN c.asn IN ('52900') THEN 'Quality Telecom'
        WHEN c.asn IN ('263629') THEN 'Celloni'
        WHEN c.asn IN ('52940') THEN 'Nemesis'
        WHEN c.asn IN ('262671') THEN 'S & M Informática'
        WHEN c.asn IN ('28241') THEN 'Viaceu Internet'
        WHEN c.asn IN ('53191') THEN 'Plug Telecom'
        WHEN c.asn IN ('28263') THEN 'Ensite Brasil'
        WHEN c.asn IN ('263072') THEN 'BD Fibra Telecom'
        WHEN c.asn IN ('53171') THEN 'Omni Telecom'
        ELSE c.as_name
    END IN ($isp)
    AND c.latitude IS NOT NULL
    AND c.longitude IS NOT NULL
GROUP BY c.latitude, c.longitude, c.client_ip, isp_name, c.country_name, c.city
```

> **Atenção:** O CASE aparece **duas vezes** aqui — uma no SELECT (para mostrar no tooltip) e uma no WHERE (para filtrar). Não tem como referenciar o alias `isp_name` no WHERE porque o WHERE é avaliado antes do SELECT.

### Configuração do Geomap no Grafana (cores por provedor)

Para que cada provedor tenha uma cor diferente e a legenda mostre o nome do provedor:

1. **No painel Geomap → Layer 1:**
   - **Display name:** troque "Layer 1" por `Provedor` (é o nome que aparece na legenda)

2. **Em Style → Color:**
   - Mude o modo de **Fixed** (cor fixa) para **`Value`** (cor por valor)
   - Selecione o campo: **`isp_name`**
   - Em **Color scheme:** escolha um esquema com múltiplas cores (ex: `Palette classic` ou `Threshsolds`)

3. **Em Style → Size:**
   - Mude para **`Value`**
   - Selecione o campo: **`total_testes`**
   - Defina min e max (ex: 2 a 15) — pontos maiores = mais testes

4. **Em Tooltip:**
   - Ative e configure para mostrar: `client_ip`, `city`, `isp_name`, `total_testes`

5. **Em Legend:**
   - Ative a legenda
   - Ela vai mostrar cada provedor com sua cor

> **Resumo:**
>
> - **Cor por provedor:** Style → Color → mode = `Value` → field = `isp_name`
> - **Tamanho por nº de testes:** Style → Size → mode = `Value` → field = `total_testes`
> - **Nome da legenda:** Display name = `Provedor`

---

## 4. Clientes por Provedor (Bar Chart)

```sql
SELECT
    CASE
        WHEN c.asn IN ('18881', '26599', '27699', '19182', '10429') THEN 'Telefônica'
        WHEN c.asn IN ('28573', '4230', '22085') THEN 'Claro'
        WHEN c.asn IN ('265303') THEN 'TV Alphaville'
        WHEN c.asn IN ('14868') THEN 'COPEL Telecom'
        WHEN c.asn IN ('53184') THEN 'INB Telecom'
        WHEN c.asn IN ('262907') THEN 'Avato Tecnologia'
        WHEN c.asn IN ('61844') THEN 'New Master'
        WHEN c.asn IN ('28258') THEN 'Powerline Internet'
        WHEN c.asn IN ('273683') THEN 'Desconhecido'
        WHEN c.asn IN ('22689') THEN 'Sercomtel'
        WHEN c.asn IN ('53062') THEN 'G G Net'
        WHEN c.asn IN ('264228') THEN 'Brasil Starlink'
        WHEN c.asn IN ('28669') THEN 'America Net'
        WHEN c.asn IN ('263645') THEN 'Fixtell Telecom'
        WHEN c.asn IN ('266949') THEN 'Divifibra'
        WHEN c.asn IN ('262700') THEN 'Efibra Telecom'
        WHEN c.asn IN ('28658') THEN 'Gigalink'
        WHEN c.asn IN ('262673') THEN 'Lafaiete'
        WHEN c.asn IN ('52900') THEN 'Quality Telecom'
        WHEN c.asn IN ('263629') THEN 'Celloni'
        WHEN c.asn IN ('52940') THEN 'Nemesis'
        WHEN c.asn IN ('262671') THEN 'S & M Informática'
        WHEN c.asn IN ('28241') THEN 'Viaceu Internet'
        WHEN c.asn IN ('53191') THEN 'Plug Telecom'
        WHEN c.asn IN ('28263') THEN 'Ensite Brasil'
        WHEN c.asn IN ('263072') THEN 'BD Fibra Telecom'
        WHEN c.asn IN ('53171') THEN 'Omni Telecom'
        ELSE c.as_name
    END AS provedor,
    count(DISTINCT d.client_ip) AS total_clientes
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE $__timeFilter(d.test_time)
    AND CASE
        WHEN c.asn IN ('18881', '26599', '27699', '19182', '10429') THEN 'Telefônica'
        WHEN c.asn IN ('28573', '4230', '22085') THEN 'Claro'
        WHEN c.asn IN ('265303') THEN 'TV Alphaville'
        WHEN c.asn IN ('14868') THEN 'COPEL Telecom'
        WHEN c.asn IN ('53184') THEN 'INB Telecom'
        WHEN c.asn IN ('262907') THEN 'Avato Tecnologia'
        WHEN c.asn IN ('61844') THEN 'New Master'
        WHEN c.asn IN ('28258') THEN 'Powerline Internet'
        WHEN c.asn IN ('273683') THEN 'Desconhecido'
        WHEN c.asn IN ('22689') THEN 'Sercomtel'
        WHEN c.asn IN ('53062') THEN 'G G Net'
        WHEN c.asn IN ('264228') THEN 'Brasil Starlink'
        WHEN c.asn IN ('28669') THEN 'America Net'
        WHEN c.asn IN ('263645') THEN 'Fixtell Telecom'
        WHEN c.asn IN ('266949') THEN 'Divifibra'
        WHEN c.asn IN ('262700') THEN 'Efibra Telecom'
        WHEN c.asn IN ('28658') THEN 'Gigalink'
        WHEN c.asn IN ('262673') THEN 'Lafaiete'
        WHEN c.asn IN ('52900') THEN 'Quality Telecom'
        WHEN c.asn IN ('263629') THEN 'Celloni'
        WHEN c.asn IN ('52940') THEN 'Nemesis'
        WHEN c.asn IN ('262671') THEN 'S & M Informática'
        WHEN c.asn IN ('28241') THEN 'Viaceu Internet'
        WHEN c.asn IN ('53191') THEN 'Plug Telecom'
        WHEN c.asn IN ('28263') THEN 'Ensite Brasil'
        WHEN c.asn IN ('263072') THEN 'BD Fibra Telecom'
        WHEN c.asn IN ('53171') THEN 'Omni Telecom'
        ELSE c.as_name
    END IN ($isp)
GROUP BY provedor
ORDER BY total_clientes DESC
LIMIT 20
```

---

## 5. Mapeamento de referência

| ISP (normalizado)  | ASNs                              | as_name original                                   |
| ------------------ | --------------------------------- | -------------------------------------------------- |
| Telefônica         | 18881, 26599, 27699, 19182, 10429 | TELEFÔNICA BRASIL S.A, Telefonica Data S.A.        |
| Claro              | 28573, 4230, 22085                | CLARO S.A., Claro S/A                              |
| TV Alphaville      | 265303                            | TV Alphaville Sistema de TV por Assinatura LTDA    |
| COPEL Telecom      | 14868                             | COPEL Telecomunicações S.A.                        |
| INB Telecom        | 53184                             | INB Telecom EIRELI - ME                            |
| Avato Tecnologia   | 262907                            | AVATO TECNOLOGIA                                   |
| New Master         | 61844                             | NEW MASTER PROVEDOR DE ACESSO A INTERNET           |
| Powerline Internet | 28258                             | Powerline Internet                                 |
| Desconhecido       | 273683                            | (vazio)                                            |
| Sercomtel          | 22689                             | Sercomtel Participações S.A.                       |
| G G Net            | 53062                             | G G NET - Telecomunicações LTDA EPP                |
| Brasil Starlink    | 264228                            | BRASIL STARLINK TELECOMUNICACOES LTDA - EPP        |
| America Net        | 28669                             | America-NET Ltda.                                  |
| Fixtell Telecom    | 263645                            | FIXTELL TELECOM                                    |
| Divifibra          | 266949                            | DIVIFIBRA TELECOMUNICAÇÕES LTDA EPP                |
| Efibra Telecom     | 262700                            | Efibra Telecom LTDA - EPP                          |
| Gigalink           | 28658                             | Gigalink de Nova Friburgo Soluções em Rede Multimi |
| Lafaiete           | 262673                            | Lafaiete Provedor de Internet e Telecomunic Ltda   |
| Quality Telecom    | 52900                             | QUALITY TELECOM SERVIÇOS DE COMUNICAÇÃO LTDA EPP   |
| Celloni            | 263629                            | CELLONI DIST. DE EQUIP. DE INF. E TECNOLOGIA LTDA  |
| Nemesis            | 52940                             | NEMESIS Provedor de Acesso as Redes de Comunicação |
| S & M Informática  | 262671                            | S & M Informática Ltda.                            |
| Viaceu Internet    | 28241                             | Viaceu Internet Ltda                               |
| Plug Telecom       | 53191                             | PLUG Telecom                                       |
| Ensite Brasil      | 28263                             | Ensite Brasil Telecomunicações Ltda - ME           |
| BD Fibra Telecom   | 263072                            | BD Fibra Telecom Ltda - EPP                        |
| Omni Telecom       | 53171                             | Omni Telecomunicacoes Ltda                         |

---

## 6. Ordem de execução

1. ✅ Atualizar a variável `isp` no Grafana com a query da seção 1
2. ✅ Atualizar a query do painel Stat (seção 2)
3. ✅ Atualizar a query do painel Geomap (seção 3) e configurar cores por provedor
4. ✅ Atualizar a query do painel Bar Chart (seção 4)
5. ✅ Testar no Grafana

> **Dica de professor:** Sem a view, o CASE WHEN é repetido em cada query. Se um novo ASN aparecer, você precisa atualizar em **todos** os painéis. Por isso a view é mais prática — mas para começar e testar, assim funciona perfeitamente!

# Debug: Mapa da Parte 1 — Geomap vazio (v2)

> **Sintoma:** a query retorna 500 linhas de clientes (confirmado no Query Inspector),
> mas o mapa não renderiza nenhum marcador.
> **Data:** 2026-08-21

---

## Correção já aplicada no JSON

### `selectedFormat: 2` (AUTO) → `selectedFormat: 1` (TABLE)

O plugin do QuestDB define:

```typescript
export enum Format {
  TIMESERIES = 0,
  TABLE = 1,
  AUTO = 2,
}
```

Com `selectedFormat: 2` (AUTO), o plugin decide o formato automaticamente:
- Se a query tem `AS "time"` no primeiro campo **E** 2+ campos → TIMESERIES
- Senão → TABLE

A query do mapa **não tem** `AS "time"`, então AUTO deveria resolver para TABLE.
Mas o `format: 1` hardcoded no target pode conflitar com o AUTO,
fazendo o plugin retornar um data frame em formato errado.

**Correção:** `selectedFormat` alterado de `2` para `1` (TABLE explícito)
no arquivo `02_dashboards/ndt_dashboard_parte1.json`.

---

## Passos para validar no Grafana

### Passo 1 — Reimportar o dashboard

1. Dashboards → New → Import
2. Selecionar `02_dashboards/ndt_dashboard_parte1.json`
3. Escolher o datasource do QuestDB
4. Import

### Passo 2 — Verificar se o mapa renderiza

Se ainda estiver vazio, continue nos passos abaixo.

### Passo 3 — Query simplificada para isolar o problema

Troque temporariamente a query do mapa por esta versão mínima
(no editor de query do painel):

```sql
SELECT
    c.latitude AS lat,
    c.longitude AS lon,
    c.city,
    count() AS total_testes
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE $__timeFilter(d.test_time)
    AND c.country_code = 'BR'
    AND c.latitude IS NOT NULL
    AND c.longitude IS NOT NULL
GROUP BY c.latitude, c.longitude, c.city
LIMIT 100
```

**Se esta query renderizar no mapa:** o problema está no CASE WHEN do ISP
ou no filtro `IN ($isp)`. Pule para o Passo 4.

**Se esta query NÃO renderizar:** o problema está na configuração do Geomap
ou no tipo de dado das colunas. Pule para o Passo 5.

### Passo 4 — Testar com o filtro ISP

Adicione o CASE WHEN de volta, gradualmente:

```sql
SELECT
    avg(c.latitude) AS lat,
    avg(c.longitude) AS lon,
    c.city,
    t.server_site,
    sum(t.total_testes) AS total_testes
FROM (
    SELECT client_ip, server_site, count() AS total_testes
    FROM download
    WHERE $__timeFilter(test_time)
    GROUP BY client_ip, server_site
) t
JOIN client c ON t.client_ip = c.client_ip
WHERE c.country_code = 'BR'
    AND c.latitude IS NOT NULL
    AND c.longitude IS NOT NULL
GROUP BY c.city, t.server_site
LIMIT 100
```

Se funcionar **sem** o filtro `IN ($isp)`, o problema é a variável `$isp`.
Quando `$isp = All`, o Grafana expande para `IN ($__all)` que pode não funcionar
corretamente com o CASE WHEN. Solução: usar `$__conditionalAll`:

```sql
AND $__conditionalAll(CASE WHEN ... END IN ($isp), $isp)
```

### Passo 5 — Verificar o tipo de dado das colunas

No Query Inspector, olhe a aba "Data" (não "Request") e verifique:
- `lat` e `lon` estão como tipo **number** (não string)
- Se estiverem como string, o Geomap não consegue plotar

Se estiverem como string, force conversão numérica na query:

```sql
CAST(c.latitude AS DOUBLE) AS lat,
CAST(c.longitude AS DOUBLE) AS lon,
```

### Passo 6 — Verificar se o Geomap está lendo os campos corretos

No editor do painel Geomap:
1. Abra a camada "Clientes por Cidade e Servidor"
2. Em **Location**, verifique:
   - Mode: **Coordinates**
   - Latitude field: **lat**
   - Longitude field: **lon**
3. Se os campos não aparecerem no dropdown, o data frame não está chegando
   como tabela — confirme que `format: 1` e `selectedFormat: 1` estão setados

---

## Possíveis causas restantes (se nada acima resolver)

| # | Causa | Como verificar | Solução |
|---|-------|----------------|---------|
| 1 | `lat`/`lon` retornam como string | Query Inspector → aba Data | `CAST(... AS DOUBLE)` |
| 2 | Variável `$isp` com `All` não expande corretamente | Trocar `IN ($isp)` por hardcoded | Usar `$__conditionalAll` |
| 3 | `avg(c.latitude)` retorna NULL para algum grupo | Rodar query sem `LIMIT` e contar NULLs | Adicionar `AND avg(c.latitude) IS NOT NULL` |
| 4 | Geomap plugin bug no Grafana 12 | Testar com panel type "Table" primeiro | Atualizar Grafana ou usar plugin antigo |
| 5 | O dataframe vem como "long format" em vez de "wide" | Query Inspector → ver estrutura | Adicionar transformação "Partition by values" |

---

## Query de teste: verificar se lat/lon são numéricos

```sql
SELECT
    typeof(c.latitude) AS tipo_lat,
    typeof(c.longitude) AS tipo_lon,
    c.latitude,
    c.longitude
FROM client c
WHERE c.country_code = 'BR'
    AND c.latitude IS NOT NULL
LIMIT 5;
```

> **Nota:** QuestDB não tem `typeof()`. Em vez disso, no Query Inspector
> do Grafana, olhe a aba "Data" para ver o tipo de cada campo.

---

## Query de teste: verificar se o JOIN funciona

```sql
SELECT count() AS total
FROM download d
JOIN client c ON d.client_ip = c.client_ip
WHERE d.test_time > dateadd('d', -7, now())
    AND c.country_code = 'BR'
    AND c.latitude IS NOT NULL;
```

Se retornar 0, o problema é o JOIN ou o `country_code`.
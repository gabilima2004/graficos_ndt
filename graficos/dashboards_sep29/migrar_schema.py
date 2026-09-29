#!/usr/bin/env python3
"""Migra dashboards Grafana do schema antigo (tabela client) para o novo (colunas embutidas + ASNS).

Mudanças aplicadas:
1. Remove `JOIN client c ON d.client_ip = c.client_ip`
2. Adiciona `LEFT JOIN ASNS a ON d.client_asn = a.ASN` após `FROM download/upload d`
3. Substitui blocos `CASE WHEN c.asn IN (...) ... ELSE c.as_name END` por
   `COALESCE(a.ASN_owner, d.client_asname, 'Desconhecido')`
4. Variável $isp passa a usar a tabela ASNS

Uso: python3 migrar_schema.py arquivo1.json arquivo2.json ...
"""
import json
import re
import sys

# Bloco CASE de mapeamento de ASN (com ou sem prefixo c.)
CASE_RE = re.compile(
    r"CASE\s+WHEN (?:c\.)?asn IN .*?ELSE (?:c\.)?as_name\s+END",
    re.DOTALL,
)
PROVEDOR_EXPR = "COALESCE(a.ASN_owner, d.client_asname, 'Desconhecido')"

ISP_QUERY = (
    "SELECT ASN_owner AS __text, ASN_owner AS __value\n"
    "FROM ASNS\n"
    "WHERE ASN_owner IS NOT NULL AND ASN_owner != ''\n"
    "GROUP BY ASN_owner\n"
    "ORDER BY ASN_owner"
)


def migrar_sql(sql: str) -> str:
    # 3. CASE blocks -> expressão do provedor
    sql = CASE_RE.sub(PROVEDOR_EXPR, sql)
    # 1. remove JOIN client
    sql = re.sub(
        r"[ \t]*JOIN client c ON d\.client_ip = c\.client_ip[ \t]*\n", "", sql
    )
    # 2. adiciona LEFT JOIN ASNS logo após o FROM da tabela de testes
    sql = re.sub(
        r"FROM (download|upload) d\n",
        r"FROM \1 d\n    LEFT JOIN ASNS a ON d.client_asn = a.ASN\n",
        sql,
    )
    return sql


def migrar_dashboard(path: str) -> None:
    with open(path, encoding="utf-8") as fp:
        d = json.load(fp)

    n_sql = 0
    for panel in d.get("panels", []):
        for target in panel.get("targets", []):
            raw = target.get("rawSql")
            if raw and ("JOIN client" in raw or "c.asn" in raw):
                target["rawSql"] = migrar_sql(raw)
                n_sql += 1

    n_vars = 0
    for var in d.get("templating", {}).get("list", []):
        if var.get("name") == "isp" and var.get("type") == "query":
            q = var.get("query", "")
            if "CASE" in q or "FROM client" in q:
                var["query"] = ISP_QUERY
                var["definition"] = ISP_QUERY
                n_vars += 1

    with open(path, "w", encoding="utf-8") as fp:
        json.dump(d, fp, ensure_ascii=False, indent=2)
        fp.write("\n")

    print(f"{path}: {n_sql} query(ies) migrada(s), {n_vars} variavel(is) $isp atualizada(s)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("uso: migrar_schema.py <dashboard.json> ...")
    for p in sys.argv[1:]:
        migrar_dashboard(p)
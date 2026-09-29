"""
Fase 1 — Extração: QuestDB -> CSVs (particionado por mês, período completo)

SCHEMA NOVO (pós-reimportação, QuestDB 10.246.47.179):
  - As colunas de cliente foram EMBUTIDAS nas tabelas download/upload
    (client_ip, client_latitude, client_longitude, client_city, client_asn,
    client_asname, client_country_code) — não existe mais tabela `client`.
  - A tabela `server` tem o cadastro completo dos sites (com ASN e tipo).
  - A tabela `ASNS` tem o dono de cada ASN de cliente (ASN_owner).

Baixa 2 conjuntos para a pasta data/:
  - sites.csv         : cadastro dos sites usados no período (com ASN/tipo)
  - tests_YYYY-MM.csv : 1 linha por teste, um arquivo por mês (tudo embutido)

Os meses são DESCOBERTOS da própria base, então não precisa saber de antemão.
O particionamento permite retomar: meses já baixados são pulados.

Uso:  python extract.py                # extrai tudo (descobre os meses da base)
      python extract.py 2026-07        # reprocessa só um mês específico

Requisitos: requests, pandas
"""

import sys
from pathlib import Path

import pandas as pd
import requests

# ---------------------------------------------------------------------------
# Configuração — ajuste aqui para o seu ambiente
# ---------------------------------------------------------------------------
QUESTDB_URL = "http://10.246.47.179:9000"  # host:porta do QuestDB (console HTTP)
DATA_DIR = Path(__file__).parent / "data"

# País a filtrar (None = todos os países). 'BR' = só Brasil.
PAIS_FILTRO = "BR"

# ---------------------------------------------------------------------------


def query_csv(sql: str) -> pd.DataFrame:
    """Executa uma query no QuestDB via endpoint /exp (CSV streaming).

    O /exp aceita a query como parâmetro e devolve o resultado inteiro como CSV.
    Para queries grandes, o QuestDB faz streaming na resposta — o requests
    baixa em chunks para não estourar memória.
    """
    url = f"{QUESTDB_URL}/exp"
    print(f"  Executando: {sql[:80]}...")
    with requests.get(url, params={"query": sql}, stream=True, timeout=1800) as r:
        r.raise_for_status()
        chunks = []
        for chunk in r.iter_content(chunk_size=1 << 20, decode_unicode=True):
            chunks.append(chunk)
    from io import StringIO

    return pd.read_csv(StringIO("".join(chunks)))


def descobrir_meses() -> list[str]:
    """Descobre quais meses existem na base, direto dos dados.

    Não assume nada: pergunta ao QuestDB quais meses têm testes.
    """
    print("Descobrindo meses existentes na base...")
    df = query_csv(
        """
        SELECT year(test_time) AS ano, month(test_time) AS mes, count() AS testes
        FROM download
        WHERE server_site IS NOT NULL
        GROUP BY ano, mes
        ORDER BY ano, mes
        """
    )
    meses = [f"{int(r.ano):04d}-{int(r.mes):02d}" for r in df.itertuples()]
    print(f"  Meses encontrados: {', '.join(meses)}")
    print(f"  Volume por mês: {dict(zip(meses, df['testes']))}")
    return meses


def limites_mes(mes: str) -> tuple[str, str]:
    """Retorna (inicio, fim) do mês no formato que o QuestDB entende.

    Intervalo meio-aberto [inicio, fim): não duplica nem pula testes
    na virada do mês.
    """
    y, m = map(int, mes.split("-"))
    if m == 12:
        fim = f"{y + 1}-01-01"
    else:
        fim = f"{y}-{m + 1:02d}-01"
    return f"{mes}-01", fim


def extract_sites() -> None:
    """Cadastro dos sites usados no período — da tabela `server`.

    A tabela server tem: coordenadas, ASN do site, tipo (physical/virtual),
    cidade, país. O dono (org) é derivado no analyze.py a partir do ASN
    do site + do padrão de nomes autojoin.

    Distintos da própria download = aproximação da lista de sites disponíveis
    que o Locate considerou. Um site sem nenhum teste no período provavelmente
    estava morto (filtrado pelo isHealthy do Locate) e não deve entrar na lista.
    """
    print("[1/2] Extraindo sites (cadastro completo da tabela server)...")
    # A tabela server é o cadastro dos sites (pequena, ~20k linhas).
    # Não precisa JOIN com download: o analyze.py filtra por volume de testes.
    # Dedup por site+update_time: mantém o registro mais recente de cada site.
    sites = query_csv(
        """
        SELECT site AS server_site, latitude, longitude,
               asn AS site_asn, as_name AS site_as_name,
               server_type, city AS site_city, country_code AS site_country,
               update_time
        FROM server
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        ORDER BY update_time
        """
    )
    # Um site aparece várias vezes (uma por machine e por atualização de
    # cadastro) — mantém o registro mais recente de cada site
    sites = sites.drop_duplicates(subset=["server_site"], keep="last").reset_index(drop=True)
    sites = sites.drop(columns=["update_time"])
    sites.to_csv(DATA_DIR / "sites.csv", index=False)
    print(f"  -> {len(sites)} sites salvos em data/sites.csv")


def extract_tests_mes(mes: str) -> bool:
    """Extrai os testes de um mês para data/tests_YYYY-MM.csv.

    SCHEMA NOVO: tudo embutido em `download` — coordenadas do cliente,
    ASN, cidade, país, e as métricas de qualidade (throughput, RTT, loss).
    Sem JOIN com tabela de clientes.

    Retorna True se o mês tem dados, False se vazio.
    Pula o mês se o arquivo já existe (permite retomar de onde parou).
    """
    arquivo = DATA_DIR / f"tests_{mes}.csv"
    if arquivo.exists():
        print(f"[2/2] {mes}: já existe ({arquivo.stat().st_size / 1e6:.0f} MB) — pulando")
        return True

    inicio, fim = limites_mes(mes)
    print(f"[2/2] Extraindo testes de {mes}...")
    filtro_pais = f" AND client_country_code = '{PAIS_FILTRO}'" if PAIS_FILTRO else ""
    tests = query_csv(
        f"""
        SELECT test_time, server_site, server_machine, server_asn,
               client_ip, client_asn, client_asname, client_city,
               client_country_code, client_latitude, client_longitude,
               mean_throughput_mbps, min_rtt, loss_rate,
               hour(test_time) AS hora
        FROM download
        WHERE test_time >= '{inicio}' AND test_time < '{fim}'
          AND server_site IS NOT NULL
          AND client_latitude IS NOT NULL AND client_longitude IS NOT NULL
          {filtro_pais}
        """
    )
    if len(tests) == 0:
        print(f"  -> {mes}: vazio")
        return False

    tests.to_csv(arquivo, index=False)
    print(f"  -> {len(tests)} testes salvos em {arquivo.name}")
    return True


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)

    # Modo reprocessar: python extract.py 2026-07 -> extrai só esse mês
    if len(sys.argv) > 1:
        extract_tests_mes(sys.argv[1])
        return

    # sites é pequeno: sempre re-extrai (garante consistência)
    extract_sites()

    # testes: particionado por mês, meses descobertos da própria base
    meses = descobrir_meses()
    for mes in meses:
        extract_tests_mes(mes)

    print("\nExtração concluída. Arquivos em data/:")
    for f in sorted(DATA_DIR.glob("*.csv")):
        print(f"  {f.name} ({f.stat().st_size / 1e6:.0f} MB)")


if __name__ == "__main__":
    main()
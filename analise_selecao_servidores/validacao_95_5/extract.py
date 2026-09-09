"""
Fase 1 — Extração: QuestDB -> CSVs (particionado por mês, período completo)

Baixa 3 conjuntos para a pasta data/:
  - sites.csv         : sites usados em TODO o período + coordenadas
  - clients.csv       : dimensão de clientes (ip, lat/lon, asn)
  - tests_YYYY-MM.csv : 1 linha por teste, um arquivo por mês

Os meses são DESCOBERTOS da própria base (query que agrupa por mês),
então não precisa saber de antemão quais meses existem.

O particionamento permite retomar de onde parou: meses já baixados são pulados.

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
QUESTDB_URL = "http://10.246.47.159:9000"  # host:porta do QuestDB (console HTTP)
DATA_DIR = Path(__file__).parent / "data"

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
        SELECT year(d.test_time) AS ano, month(d.test_time) AS mes, count() AS testes
        FROM download d
        WHERE d.server_site IS NOT NULL
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
    """Sites usados em TODO o período + coordenadas.

    Distintos da própria download = aproximação da lista de sites disponíveis
    que o Locate considerou. Um site sem nenhum teste no período provavelmente
    estava morto (filtrado pelo isHealthy do Locate) e não deve entrar na lista.
    """
    print("[1/3] Extraindo sites (período completo)...")
    sites = query_csv(
        """
        SELECT DISTINCT d.server_site, s.latitude, s.longitude
        FROM download d
        JOIN server s ON d.server_ip = s.server_ip
        WHERE d.server_site IS NOT NULL
          AND s.latitude IS NOT NULL AND s.longitude IS NOT NULL
        """
    )
    sites.to_csv(DATA_DIR / "sites.csv", index=False)
    print(f"  -> {len(sites)} sites salvos em data/sites.csv")


def extract_clients() -> None:
    """Dimensão de clientes (ip, lat/lon, asn) — tabela inteira.

    Sem filtro de período: um cliente que testou no início pode ter registro
    atualizado depois. Deduplicação por update_time fica no pandas (Fase 2).
    """
    print("[2/3] Extraindo clientes...")
    clients = query_csv(
        """
        SELECT client_ip, latitude, longitude, asn, as_name, city, update_time
        FROM client
        """
    )
    clients.to_csv(DATA_DIR / "clients.csv", index=False)
    print(f"  -> {len(clients)} registros salvos em data/clients.csv")


def extract_tests_mes(mes: str) -> bool:
    """Extrai os testes de um mês para data/tests_YYYY-MM.csv.

    Retorna True se o mês tem dados, False se vazio.
    Pula o mês se o arquivo já existe (permite retomar de onde parou).
    """
    arquivo = DATA_DIR / f"tests_{mes}.csv"
    if arquivo.exists():
        print(f"[3/3] {mes}: já existe ({arquivo.stat().st_size / 1e6:.0f} MB) — pulando")
        return True

    inicio, fim = limites_mes(mes)
    print(f"[3/3] Extraindo testes de {mes}...")
    tests = query_csv(
        f"""
        SELECT d.client_ip, d.server_site, hour(d.test_time) AS hora
        FROM download d
        WHERE d.test_time >= '{inicio}' AND d.test_time < '{fim}'
          AND d.server_site IS NOT NULL
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

    # sites e clients são pequenos: sempre re-extrai (garante consistência)
    extract_sites()
    extract_clients()

    # testes: particionado por mês, meses descobertos da própria base
    meses = descobrir_meses()
    for mes in meses:
        extract_tests_mes(mes)

    print("\nExtração concluída. Arquivos em data/:")
    for f in sorted(DATA_DIR.glob("*.csv")):
        print(f"  {f.name} ({f.stat().st_size / 1e6:.0f} MB)")


if __name__ == "__main__":
    main()
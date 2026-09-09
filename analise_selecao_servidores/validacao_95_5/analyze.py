"""
Fase 2 e 3 — Rank do servidor usado + proporção por rank

Lê os CSVs de data/ (gerados por extract.py), calcula o rank haversine do
server_site usado em cada teste e produz os arquivos de saída em out/:
  - rank_histogram.csv : testes e proporção por rank (comparação com 95/5)
  - por_hora.csv       : proporção de rank != 0 por hora do dia
  - por_provedor.csv   : proporção de rank != 0 por provedor
  - outliers_extra_km.csv : estatísticas de distância extra dos desvios

Uso:  python analyze.py

Requisitos: pandas, numpy
"""

from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
OUT_DIR = Path(__file__).parent / "out"

# Maio/2026 tem apenas 10 testes na base inteira (mês fantasma do início da
# coleta). Tudo antes deste mês é descartado.
MES_INICIO_VALIDO = "2026-06"

EARTH_RADIUS_KM = 6371.0  # mesmo valor do m-lab/go/mathx/haversine.go

# ---------------------------------------------------------------------------


def haversine(lat1, lon1, lat2, lon2):
    """Distância haversine em km — vetorial, aceita arrays.

    Mesma fórmula de m-lab/go/mathx/haversine.go (linha reta no globo).
    """
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))


def load_data():
    sites = pd.read_csv(DATA_DIR / "sites.csv")
    clients = pd.read_csv(DATA_DIR / "clients.csv")

    # ------------------------------------------------------------------
    # FILTRO DE SITES: só sites com volume relevante entram na lista.
    # Justificativa: sites com pouquíssimos testes no período inteiro
    # (ex: 30-90 testes) estavam quase certamente mortos ou em rollout
    # (Probability baixa) na maior parte do tempo — o Locate não os
    # oferecia regularmente. Incluí-los na lista infla o rank calculado:
    # um cliente em SP "ganha" dezenas de sites europeus mais próximos
    # (mas mortos) e o site real usado cai no rank 10-20 sem ser desvio.
    # ------------------------------------------------------------------
    volume_sites = (
        pd.concat(
            [pd.read_csv(f, usecols=["server_site"]) for f in DATA_DIR.glob("tests_*.csv")]
        )["server_site"]
        .value_counts()
    )

    MIN_TESTES_SITE = 1000
    sites_ativos = set(volume_sites[volume_sites >= MIN_TESTES_SITE].index.astype(str))
    antes = len(sites)
    sites = sites[sites["server_site"].astype(str).isin(sites_ativos)].reset_index(drop=True)
    print(
        f"  Filtro de sites: {antes} -> {len(sites)} "
        f"(min {MIN_TESTES_SITE} testes no período)"
    )
    if len(sites) == 0:
        raise RuntimeError(
            "Filtro de sites zerou a lista — verifique os nomes de server_site "
            "em sites.csv vs tests_*.csv (espaços/aspas/encoding)."
        )

    # Testes: particionado por mês (tests_YYYY-MM.csv) — lê todos e concatena
    arquivos_tests = sorted(DATA_DIR.glob("tests_*.csv"))
    if not arquivos_tests:
        raise FileNotFoundError(
            f"Nenhum tests_YYYY-MM.csv encontrado em {DATA_DIR}. "
            "Rode extract.py primeiro."
        )
    print(f"  Lendo {len(arquivos_tests)} arquivo(s) de testes:")
    partes = []
    for f in arquivos_tests:
        # Descarta meses fantasma (ex: maio/2026 tem 10 testes na base inteira)
        mes = f.stem.replace("tests_", "")
        if mes < MES_INICIO_VALIDO:
            print(f"    {f.name} — descartado (antes de {MES_INICIO_VALIDO})")
            continue
        print(f"    {f.name}...")
        df_mes = pd.read_csv(f)
        df_mes["mes"] = mes  # preserva o mês (usado na captura por mês)
        partes.append(df_mes)
    tests = pd.concat(partes, ignore_index=True)
    del partes

    # Deduplica clientes: mantém o update_time mais recente por client_ip
    clients["update_time"] = pd.to_datetime(clients["update_time"], errors="coerce")
    clients = (
        clients.sort_values("update_time")
        .drop_duplicates(subset="client_ip", keep="last")
    )

    # Remove clientes sem coordenada (não dá para calcular rank sem lat/lon)
    clients = clients.dropna(subset=["latitude", "longitude"])

    # Junta testes com a coordenada do cliente
    colunas_client = ["client_ip", "latitude", "longitude", "asn", "as_name"]
    if "city" in clients.columns:
        colunas_client.append("city")
    tests = tests.merge(
        clients[colunas_client],
        on="client_ip",
        how="inner",
    )
    tests = tests.dropna(subset=["latitude", "longitude"])

    return sites, clients, tests


def compute_ranks(sites: pd.DataFrame, tests: pd.DataFrame) -> pd.DataFrame:
    """Calcula o rank (por GRUPO de distância) do server_site usado em cada teste.

    CORREÇÃO CONCEITUAL: sites co-localizados (mesma coordenada registrada —
    comum no mesmo metro, ex: gru02/gru03/gru06/gru07 em SP) têm distâncias
    IGUAIS até o cliente. No Locate, a ordem entre distâncias iguais é
    arbitrária (iteração de map em Go é randomizada e sort.Slice não é
    estável), então o rank INDIVIDUAL do site dentro do grupo não é
    reproduzível offline. O que valida o 95/5 é o rank do GRUPO de distância:
    se o site usado está no grupo mais próximo, rank = 0, independente de
    qual site do grupo o sorteio escolheu.

    A otimização (matriz por coordenada distinta, lookup por teste) continua:
    a distância é determinística dado (coordenada, lista de sites).
    """
    # 1. Agrupa sites por coordenada registrada (empate = mesma coordenada)
    sites = sites.copy()
    sites["loc_key"] = (
        sites["latitude"].round(6).astype(str)
        + "|"
        + sites["longitude"].round(6).astype(str)
    )
    locs = (
        sites.groupby("loc_key")
        .agg(
            latitude=("latitude", "first"),
            longitude=("longitude", "first"),
            n_sites=("server_site", "size"),
            sites_no_grupo=("server_site", lambda s: ", ".join(sorted(s))),
        )
        .reset_index()
    )
    print(f"  {len(sites)} sites -> {len(locs)} localizações distintas (grupos de empate)")
    for _, r in (
        locs[locs["n_sites"] > 1]
        .sort_values("n_sites", ascending=False)
        .head(10)
        .iterrows()
    ):
        print(f"    grupo com {r['n_sites']} sites: {r['sites_no_grupo']}")

    # 2. Coordenadas distintas de clientes (GeoIP é city-level: milhares, não milhões)
    coords = (
        tests[["latitude", "longitude"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    print(f"  {len(coords)} coordenadas distintas de clientes x {len(locs)} localizações")

    # 3. Matriz de distâncias: coordenada de cliente × localização de site
    loc_lats = locs["latitude"].to_numpy()
    loc_lons = locs["longitude"].to_numpy()

    rank_matrix = np.empty((len(coords), len(locs)), dtype=np.int32)
    dist_matrix = np.empty((len(coords), len(locs)), dtype=np.float64)

    for i, (lat, lon) in enumerate(
        zip(coords["latitude"].to_numpy(), coords["longitude"].to_numpy())
    ):
        d = haversine(lat, lon, loc_lats, loc_lons)
        order = np.argsort(d, kind="stable")  # ordenação estrita, como sortSites()
        ranks = np.empty_like(order)
        ranks[order] = np.arange(len(order))
        rank_matrix[i] = ranks
        dist_matrix[i] = d

    # 4. Lookup: para cada teste, o rank do GRUPO do site usado
    coord_index = {
        (lat, lon): i
        for i, (lat, lon) in enumerate(
            zip(coords["latitude"].to_numpy(), coords["longitude"].to_numpy())
        )
    }
    loc_index = {name: j for j, name in enumerate(locs["loc_key"])}
    site_to_loc = dict(zip(sites["server_site"], sites["loc_key"]))

    tests = tests.copy()
    tests["coord_idx"] = [
        coord_index[(lat, lon)]
        for lat, lon in zip(tests["latitude"], tests["longitude"])
    ]
    tests["loc_idx"] = tests["server_site"].map(site_to_loc).map(loc_index)

    # Testes cujo server_site não está na lista (sites filtrados pelo volume
    # mínimo) — descartados e contabilizados
    missing = tests["loc_idx"].isna()
    if missing.any():
        print(f"  AVISO: {missing.sum()} testes com server_site fora da lista de sites — descartados")
        tests = tests[~missing]

    tests["rank"] = rank_matrix[
        tests["coord_idx"].to_numpy(), tests["loc_idx"].to_numpy(dtype=int)
    ]
    tests["dist_usada_km"] = dist_matrix[
        tests["coord_idx"].to_numpy(), tests["loc_idx"].to_numpy(dtype=int)
    ]
    tests["dist_min_km"] = dist_matrix[tests["coord_idx"].to_numpy()].min(axis=1)
    tests["dist_extra_km"] = tests["dist_usada_km"] - tests["dist_min_km"]

    # 5. Identifica a LOCALIZAÇÃO mais próxima de cada teste (rank 0).
    #    A taxa de captura de um site = fração dos testes cujo grupo mais
    #    próximo é ele que realmente o usaram. Se o site foi filtrado pelo
    #    Locate (health/rollout), a captura fica abaixo de ~95%.
    argmin_matrix = np.argmin(dist_matrix, axis=1)  # loc mais próxima por coordenada
    tests["loc_mais_proxima"] = argmin_matrix[tests["coord_idx"].to_numpy()]
    tests["usou_mais_proxima"] = tests["loc_idx"] == tests["loc_mais_proxima"]

    return tests


def novo_out_dir() -> Path:
    """Retorna um diretório de saída livre: out/, out_2/, out_3/, ...

    Se out/ já existe (execução anterior), cria o próximo número disponível.
    Assim cada execução fica preservada para comparação.
    """
    if not OUT_DIR.exists():
        return OUT_DIR
    n = 2
    while (DATA_DIR.parent / f"out_{n}").exists():
        n += 1
    return DATA_DIR.parent / f"out_{n}"


def main():
    out_dir = novo_out_dir()
    out_dir.mkdir(exist_ok=True)
    print(f"Saídas em: {out_dir}")

    print("Carregando dados...")
    sites, clients, tests = load_data()
    print(f"  {len(sites)} sites, {len(clients)} clientes, {len(tests)} testes")

    print("Calculando ranks...")
    tests = compute_ranks(sites, tests)

    # ------------------------------------------------------------------
    # Fase 3 — histograma de ranks
    # ------------------------------------------------------------------
    print("Proporção por rank...")
    hist = (
        tests.groupby("rank")
        .size()
        .rename("testes")
        .reset_index()
    )
    hist["proporcao"] = hist["testes"] / hist["testes"].sum()
    hist.to_csv(out_dir / "rank_histogram.csv", index=False)
    print(hist.to_string(index=False))

    # ------------------------------------------------------------------
    # Fase 4 — autópsia dos rank != 0
    # ------------------------------------------------------------------
    print("Recortes para autópsia...")

    # Por hora do dia (rejeição por carga aparece como excedente no pico)
    por_hora = (
        tests.assign(desvio=(tests["rank"] != 0))
        .groupby("hora")["desvio"]
        .agg(["sum", "count"])
        .reset_index()
        .rename(columns={"sum": "desvios", "count": "testes"})
    )
    por_hora["prop_desvios"] = por_hora["desvios"] / por_hora["testes"]
    por_hora.to_csv(out_dir / "por_hora.csv", index=False)

    # Por provedor (GeoIP ruim aparece concentrado em ISPs pequenos)
    tests["provedor"] = tests["as_name"].fillna("desconhecido")
    por_prov = (
        tests.assign(desvio=(tests["rank"] != 0))
        .groupby("provedor")["desvio"]
        .agg(["sum", "count"])
        .reset_index()
        .rename(columns={"sum": "desvios", "count": "testes"})
    )
    por_prov["prop_desvios"] = por_prov["desvios"] / por_prov["testes"]
    por_prov = por_prov.sort_values("testes", ascending=False)
    por_prov.to_csv(out_dir / "por_provedor.csv", index=False)

    # Distância extra dos desvios (o 5% deveria ir pro 2º mais próximo:
    # dist_extra pequena; dist_extra gigante sugere GeoIP errado)
    outliers = tests[tests["rank"] != 0]
    stats = outliers["dist_extra_km"].describe()
    stats.to_csv(out_dir / "outliers_extra_km.csv")

    # ------------------------------------------------------------------
    # DIAGNÓSTICO: quais coordenadas geram os piores ranks?
    # Se uma coordenada tem rank alto para TODOS os seus testes, o problema
    # é a coordenada em si (divergência entre a coordenada usada pelo Locate
    # e a armazenada) — não o algoritmo.
    # ------------------------------------------------------------------
    colunas_diag = ["latitude", "longitude"]
    if "city" in tests.columns:
        colunas_diag.append("city")
    diag = (
        tests.groupby(colunas_diag)
        .agg(
            testes=("rank", "size"),
            rank_mediano=("rank", "median"),
            rank_max=("rank", "max"),
            dist_min_km=("dist_min_km", "first"),
        )
        .reset_index()
        .sort_values("testes", ascending=False)
    )
    diag.to_csv(out_dir / "diagnostico_coordenadas.csv", index=False)

    # Top 20 coordenadas por volume, com o rank mediano — para inspeção rápida
    if "city" in diag.columns:
        colunas_print = ["city", "testes", "rank_mediano", "dist_min_km"]
    else:
        colunas_print = ["latitude", "longitude", "testes", "rank_mediano", "dist_min_km"]
    print("\nTop 20 coordenadas por volume (rank mediano):")
    print(diag.head(20)[colunas_print].to_string(index=False))

    # ------------------------------------------------------------------
    # TAXA DE CAPTURA por site
    # Dos testes cujo grupo mais próximo é o site X, qual fração realmente
    # o usou? ~95% esperado se o site foi oferecido em todas as requisições.
    # Taxa baixa e estável mês a mês = assinatura do pickWithProbability
    # (rollout: o site é filtrado da lista em uma fração fixa das vezes).
    # ------------------------------------------------------------------
    print("\nTaxa de captura por site...")

    # Mapeia loc_idx -> nomes dos sites do grupo (para legibilidade)
    locs = tests[["loc_idx", "server_site"]].drop_duplicates()
    loc_para_site = locs.groupby("loc_idx")["server_site"].apply(
        lambda s: ", ".join(sorted(s))
    )

    # a) Por site (período todo): dos testes cujo grupo mais próximo é o site,
    #    qual fração realmente o usou?
    elegiveis_total = tests.groupby("loc_mais_proxima").size().rename("elegiveis")
    capturados = (
        tests[tests["usou_mais_proxima"]]
        .groupby("loc_mais_proxima")
        .size()
        .rename("capturados")
    )
    captura = pd.concat([elegiveis_total, capturados], axis=1).fillna(0)
    captura["taxa_captura"] = captura["capturados"] / captura["elegiveis"]
    captura["sites_do_grupo"] = captura.index.map(loc_para_site)
    captura = captura.sort_values("elegiveis", ascending=False)
    captura.to_csv(out_dir / "captura_por_site.csv", index=True, index_label="loc_idx")
    print(captura[["sites_do_grupo", "elegiveis", "capturados", "taxa_captura"]].to_string())

    # b) Por site e por mês (a assinatura do rollout é a taxa ESTÁVEL mês a mês;
    #    um site com problema de saúde flutuaria)
    captura_mes = (
        tests.pivot_table(
            index="loc_mais_proxima",
            columns="mes",
            values="usou_mais_proxima",
            aggfunc="mean",
        )
    )
    captura_mes["sites_do_grupo"] = captura_mes.index.map(loc_para_site)
    captura_mes.to_csv(out_dir / "captura_por_site_mes.csv", index=True, index_label="loc_idx")
    print("\nTaxa de captura por site e mês:")
    print(captura_mes.to_string())

    print("\nConcluído. Saídas em:")
    for f in sorted(out_dir.glob("*.csv")):
        print(f"  {f.name}")


if __name__ == "__main__":
    main()
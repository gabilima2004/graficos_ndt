"""
Fase 2 e 3 — Rank do servidor usado + proporção por rank

Lê os CSVs de data/ (gerados por extract.py), calcula o rank haversine do
server_site usado em cada teste e produz os arquivos de saída em out/:
  - rank_histogram.csv : testes e proporção por rank (comparação com 95/5)
  - por_hora.csv       : proporção de rank != 0 por hora do dia
  - por_provedor.csv   : proporção de rank != 0 por provedor
  - outliers_extra_km.csv : estatísticas de distância extra dos desvios
  - RELATORIO.md       : relatório em Markdown com todos os resultados

Uso:  python analyze.py

Requisitos: pandas, numpy
"""

from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
OUT_DIR = Path(__file__).parent / "out"

EARTH_RADIUS_KM = 6371.0  # mesmo valor do m-lab/go/mathx/haversine.go

# ---------------------------------------------------------------------------
# Relatório — coleta de linhas e escrita em Markdown
# ---------------------------------------------------------------------------

RELATORIO_LINHAS: list[str] = []


def rel(titulo: str = "", texto: str = "", tabela: pd.DataFrame | None = None,
        max_linhas: int = 30) -> None:
    """Adiciona uma seção ao relatório (imprime no console e acumula em Markdown).

    - titulo: cria um cabeçalho de seção (## no md)
    - texto: parágrafo livre
    - tabela: DataFrame para incluir como tabela Markdown (limitado a max_linhas)
    """
    if titulo:
        linha = f"\n## {titulo}\n"
        print(linha.strip())
        RELATORIO_LINHAS.append(linha)
    if texto:
        print(texto)
        RELATORIO_LINHAS.append(texto + "\n")
    if tabela is not None and len(tabela) > 0:
        t = tabela.head(max_linhas)
        md = t.to_markdown(index=False)
        print(t.to_string(index=False))
        RELATORIO_LINHAS.append(md + "\n")
        if len(tabela) > max_linhas:
            nota = f"_(tabela completa em CSV — {len(tabela)} linhas, mostrando {max_linhas})_"
            RELATORIO_LINHAS.append(nota + "\n")


def salvar_relatorio(out_dir: Path, meta: dict) -> None:
    """Escreve o relatório acumulado em out_dir/RELATORIO.md."""
    cab = [
        "# Relatório — Validação da seleção de servidores M-Lab",
        "",
        f"**Gerado em:** {meta['quando']}  ",
        f"**Período dos dados:** {meta['periodo']}  ",
        f"**Volume:** {meta['testes']:,} testes, {meta['n_sites']} sites, "
        f"{meta['n_cidades']} cidades  ",
        f"**Filtro de país:** {meta['pais']}  ",
        "",
        "Mecanismo validado: filtro `pickWithProbability` (cadastro) + loteria "
        "de distância 95/5 (`GetExpDistributedInt(6)`). A taxa de captura de um "
        "site é a consequência direta do `Probability` do cadastro.",
        "",
        "---",
    ]
    conteudo = "\n".join(cab) + "\n" + "\n".join(RELATORIO_LINHAS)
    arquivo = out_dir / "RELATORIO.md"
    arquivo.write_text(conteudo, encoding="utf-8")
    print(f"\nRelatório salvo em: {arquivo}")


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


def derivar_dono(site: str, site_asn, server_machine: str = "") -> str:
    """Deriva o dono (organização) de um site.

    Regras (do estudo do mecanismo M-Lab):
      - Sites autojoined têm FQDN ndt-<IATA><ASN>-<hash>.<org>.autojoin...
        O org está no hostname. Sem FQDN, usamos o ASN do site:
        AS1916=RNP, AS2716=RNP/POA, AS10881=RNP/CWB, AS53164=RNP/SSA, AS53078=RNP/VIX.
      - Sites mlabN-<metro><num> (padrão antigo) = mlab-oti.
    """
    s = str(site).strip()
    # Padrão autojoin: <iata><asn> com ASN numérico grande no fim do nome
    ASN_ORGS = {
        1916: "rnp", 2716: "rnp", 10881: "rnp", 53164: "rnp", 53078: "rnp",
        15830: "equinix", 11242: "rnp",
    }
    # Tenta extrair o ASN do sufixo do nome do site (ex: gig1916 -> 1916)
    import re
    m = re.search(r"([a-z]{3})(\d+)$", s)
    if m:
        asn_num = int(m.group(2))
        if asn_num in ASN_ORGS:
            return ASN_ORGS[asn_num]
    # Padrão mlabN-... = OTI
    if s.startswith("mlab") or re.match(r"^[a-z]{3}\d{2}$", s):
        return "mlab-oti"
    # Fallback: ASN do cadastro do server
    try:
        asn_num = int(str(site_asn).replace("AS", ""))
        if asn_num in ASN_ORGS:
            return ASN_ORGS[asn_num]
    except (ValueError, TypeError):
        pass
    return "outros"


def load_data():
    sites = pd.read_csv(DATA_DIR / "sites.csv")

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

    # Dono (organização) de cada site — derivado do nome/ASN
    sites["owner"] = [
        derivar_dono(site, asn)
        for site, asn in zip(sites["server_site"], sites.get("site_asn", pd.Series(dtype=str)))
    ]
    print("  Donos dos sites:", sites["owner"].value_counts().to_dict())

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
        print(f"    {f.name}...")
        df_mes = pd.read_csv(f)
        df_mes["mes"] = f.stem.replace("tests_", "")  # preserva o mês (usado na captura por mês)
        partes.append(df_mes)
    tests = pd.concat(partes, ignore_index=True)
    del partes

    # SCHEMA NOVO: as coordenadas do cliente já vêm embutidas por teste
    # (client_latitude/client_longitude) — sem dedup, sem merge.
    # Normaliza nomes: o analyze usa latitude/longitude genéricos.
    if "client_latitude" in tests.columns:
        tests = tests.rename(
            columns={
                "client_latitude": "latitude",
                "client_longitude": "longitude",
                "client_asn": "asn",
                "client_asname": "as_name",
                "client_city": "city",
            }
        )
    # upload tem typo no schema (client_longitute) — corrige se vier de upload
    if "client_longitute" in tests.columns and "longitude" not in tests.columns:
        tests = tests.rename(columns={"client_longitute": "longitude"})

    tests = tests.dropna(subset=["latitude", "longitude"])

    return sites, tests


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
    from datetime import datetime

    out_dir = novo_out_dir()
    out_dir.mkdir(exist_ok=True)
    print(f"Saídas em: {out_dir}")

    print("Carregando dados...")
    sites, tests = load_data()
    print(f"  {len(sites)} sites, {len(tests)} testes")

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
    rel("Distribuição por rank (validação do 95/5)",
        "O Locate escolhe o site mais próximo em ~95% das vezes (rank 0) e "
        "escapa para os seguintes nos ~5% restantes. A proporção observada "
        "abaixo deve casar com essa expectativa.",
        hist, max_linhas=15)

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
    rel("Desvios por hora do dia",
        "Pico de desvios no horário de carga sugere rejeição por saúde/carga; "
        "desvios uniformes ao longo do dia sugerem GeoIP ou probabilidade.",
        por_hora, max_linhas=24)

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
    rel("Desvios por provedor (top 15)",
        "ISPs pequenos com desvio alto = GeoIP impreciso para aqueles IPs.",
        por_prov.head(15), max_linhas=15)

    # Distância extra dos desvios (o 5% deveria ir pro 2º mais próximo:
    # dist_extra pequena; dist_extra gigante sugere GeoIP errado)
    outliers = tests[tests["rank"] != 0]
    stats = outliers["dist_extra_km"].describe()
    stats.to_csv(out_dir / "outliers_extra_km.csv")
    rel("Distância extra dos desvios (rank != 0)",
        "O 5% de escape deveria ir para o 2º mais próximo (dist_extra pequena). "
        "dist_extra gigante sugere coordenada GeoIP errada.",
        stats.reset_index().rename(columns={"index": "estatística", 0: "valor"}),
        max_linhas=10)

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
    rel("Diagnóstico de coordenadas (top 20 por volume)",
        "Coordenada com rank mediano alto para TODOS os seus testes = problema "
        "da coordenada (GeoIP), não do algoritmo.",
        diag.head(20)[colunas_print], max_linhas=20)

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
    rel("Taxa de captura por site",
        "Dos testes cujo grupo mais próximo é o site, qual fração realmente o "
        "usou. ~95% esperado para site com Probability=1. Taxa baixa e estável "
        "= assinatura do pickWithProbability (cadastro), não de falha operacional.",
        captura[["sites_do_grupo", "elegiveis", "capturados", "taxa_captura"]].reset_index(drop=True),
        max_linhas=30)

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
    rel("Taxa de captura por site e mês",
        "A estabilidade mês a mês é a assinatura de um campo estático de "
        "cadastro (Probability), não de problema de saúde flutuante.",
        captura_mes.reset_index(), max_linhas=30)

    # ------------------------------------------------------------------
    # DIMENSÃO DONO (organização)
    # ------------------------------------------------------------------
    print("\nDistribuição por dono do servidor...")

    # Mapa site -> owner (do cadastro de sites)
    site_owner = dict(zip(sites["server_site"], sites["owner"]))
    tests["owner"] = tests["server_site"].map(site_owner).fillna("outros")

    # a) Distribuição global: % dos testes por dono
    por_dono = (
        tests.groupby("owner")
        .agg(testes=("rank", "size"), prop_desvios=("rank", lambda r: (r != 0).mean()))
        .reset_index()
        .sort_values("testes", ascending=False)
    )
    por_dono["pct"] = por_dono["testes"] / por_dono["testes"].sum() * 100
    por_dono.to_csv(out_dir / "distribuicao_por_dono.csv", index=False)
    rel("Distribuição global por dono do servidor",
        "Fração dos testes brasileiros que vai para cada organização "
        "(mlab-oti, rnp, equinix, ...).",
        por_dono, max_linhas=15)

    # b) Distribuição cidade × dono: para cada cidade, % que vai a cada dono
    if "city" in tests.columns:
        dist_cidade_dono = (
            tests.groupby(["city", "owner"])
            .size()
            .rename("testes")
            .reset_index()
        )
        dist_cidade_dono["pct_na_cidade"] = (
            dist_cidade_dono.groupby("city")["testes"].transform(lambda s: s / s.sum() * 100)
        )
        dist_cidade_dono = dist_cidade_dono.sort_values(["city", "testes"], ascending=[True, False])
        dist_cidade_dono.to_csv(out_dir / "distribuicao_cidade_dono.csv", index=False)
        # No relatório: só as 15 maiores cidades
        top_cidades_vol = tests["city"].value_counts().head(15).index.tolist()
        rel("Distribuição cidade × dono (15 maiores cidades)",
            "Para cada cidade, para onde vão os testes — por organização. "
            "Cidades onde rnp aparece com % alto mas captura baixa = prioridade baixa.",
            dist_cidade_dono[dist_cidade_dono["city"].isin(top_cidades_vol)],
            max_linhas=45)

    # ------------------------------------------------------------------
    # PERFIL DE CLIENTES POR SITE (o pedido do chefe)
    # Para cada site: de onde vêm seus clientes (cidade), distância mediana
    # e ASN dominante. Responde "quem mede para cwb10881?"
    # ------------------------------------------------------------------
    print("\nPerfil de clientes por site...")
    perfis = []
    for site, g in tests.groupby("server_site"):
        total = len(g)
        top_cidades = g["city"].value_counts().head(5) if "city" in g.columns else pd.Series(dtype=str)
        perf = {
            "server_site": site,
            "owner": g["owner"].iloc[0],
            "testes": total,
            "n_cidades": g["city"].nunique() if "city" in g.columns else np.nan,
            "cidade_1": top_cidades.index[0] if len(top_cidades) else "",
            "cidade_1_pct": (top_cidades.iloc[0] / total * 100) if len(top_cidades) else np.nan,
            "cidade_2": top_cidades.index[1] if len(top_cidades) > 1 else "",
            "cidade_2_pct": (top_cidades.iloc[1] / total * 100) if len(top_cidades) > 1 else np.nan,
            "dist_mediana_km": g["dist_usada_km"].median(),
            "pct_local": (
                (g["dist_usada_km"] <= 100).mean() * 100
            ),  # % dos clientes a <=100km do site
        }
        perfis.append(perf)
    perfil_df = pd.DataFrame(perfis).sort_values("testes", ascending=False)
    perfil_df.to_csv(out_dir / "perfil_clientes_por_site.csv", index=False)
    rel("Perfil de clientes por site (top 20)",
        "De onde vêm os clientes de cada servidor: principais cidades, "
        "distância mediana e % de clientes locais (<=100 km).",
        perfil_df.head(15), max_linhas=15)

    # ------------------------------------------------------------------
    # PRIORIDADE IMPLÍCITA por site
    # prioridade = taxa_captura / 0.95 (um site P=1 captura ~95%)
    # ------------------------------------------------------------------
    print("\nPrioridade implícita por site...")
    # captura está indexada por loc_idx (grupo); expande para sites individuais
    prior = captura.copy()
    prior["prioridade_implícita"] = prior["taxa_captura"] / 0.95
    # Classificação (limite superior infinito: captura >95% = alta)
    prior["classe"] = pd.cut(
        prior["prioridade_implícita"],
        bins=[0, 0.15, 0.5, 0.8, np.inf],
        labels=["muito baixa", "baixa", "média", "alta"],
    )
    # Dono do primeiro site do grupo
    prior["owner"] = prior["sites_do_grupo"].str.split(", ").str[0].map(site_owner)
    prior.to_csv(out_dir / "prioridade_por_site.csv", index=True, index_label="loc_idx")
    rel("Prioridade implícita por site",
        "prioridade = taxa_captura / 0.95. Um site com Probability=1 captura "
        "~95% dos testes elegíveis; valores abaixo indicam o Probability do "
        "cadastro (nó declara → API multiplica pelo fator da organização).",
        prior[["sites_do_grupo", "owner", "taxa_captura", "prioridade_implícita", "classe"]].reset_index(drop=True),
        max_linhas=30)

    # ------------------------------------------------------------------
    # QUALIDADE por dono (throughput/RTT, se disponíveis)
    # ------------------------------------------------------------------
    if "mean_throughput_mbps" in tests.columns:
        print("\nQualidade mediana por dono...")
        qual = (
            tests.groupby("owner")
            .agg(
                testes=("rank", "size"),
                throughput_mediana=("mean_throughput_mbps", "median"),
                rtt_mediano=("min_rtt", "median"),
                loss_mediana=("loss_rate", "median"),
            )
            .reset_index()
        )
        qual.to_csv(out_dir / "qualidade_por_dono.csv", index=False)
        rel("Qualidade mediana por dono",
            "Cuidado com viés: os testes que caem em sites de baixa prioridade "
            "são a 'fatia de escape' da loteria — amostra não representativa "
            "da região, mas útil para comparar a qualidade ofertada por dono.",
            qual, max_linhas=15)

    # ------------------------------------------------------------------
    # Salva o relatório
    # ------------------------------------------------------------------
    periodo = ", ".join(sorted(tests["mes"].unique()))
    n_cidades = tests["city"].nunique() if "city" in tests.columns else 0
    meta = {
        "quando": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "periodo": periodo,
        "testes": len(tests),
        "n_sites": len(sites),
        "n_cidades": n_cidades,
        "pais": "BR" if tests.get("client_country_code", pd.Series(dtype=str)).eq("BR").all() else "todos",
    }
    salvar_relatorio(out_dir, meta)

    print("\nConcluído. Saídas em:")
    for f in sorted(out_dir.glob("*.csv")):
        print(f"  {f.name}")
    print(f"  RELATORIO.md")


if __name__ == "__main__":
    main()
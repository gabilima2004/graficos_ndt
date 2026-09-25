"""
Comparação pareada: gru02 (MLAB) vs gru1916 (RNP) — São Paulo.

Os dois sites são CO-LOCALIZADOS na mesma coordenada registrada
(-23.4322, -46.4692): competem pelo mesmo cliente, mas têm donos e
prioridades diferentes (mlab-oti P=1 vs rnp P≈0,08).

PASSO 1 (este arquivo): visão geral de cada servidor
  - volume de testes, clientes únicos, cidades atendidas
  - distância mediana, % de clientes locais (<=100 km)
  - qualidade mediana (RTT, throughput, loss)

Uso:
    python comparacao_sp.py            # usa o out_N/ mais recente (referência)
    python comparacao_sp.py out_6      # usa um diretório específico

Requisitos:
    - data/sites.csv e data/tests_*.csv (rode extract.py primeiro)
    - pandas

Saídas (em pizza_<out_N>/):
    comparacao_sp_passo1.csv — a tabela-resumo dos 2 sites
"""

import sys
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
BASE_OUT = Path(__file__).parent

# O par comparado
SITE_MLAB = "gru02"
SITE_RNP = "gru1916"

# Distância máxima para considerar um cliente "local" do site
LIMITE_LOCAL_KM = 100


def mais_recente_out() -> Path:
    candidatos = sorted(
        BASE_OUT.glob("out*"),
        key=lambda p: int(p.name.split("_")[1]) if "_" in p.name else 1,
    )
    if not candidatos:
        raise FileNotFoundError("Nenhum out*/ encontrado. Rode analyze.py primeiro.")
    return candidatos[-1]


def carregar() -> pd.DataFrame:
    """Carrega os tests_*.csv (schema novo: tudo embutido por teste).

    SCHEMA NOVO (pós-reimportação): as tabelas download/upload já têm as
    colunas do cliente embutidas (client_city, client_latitude, ...) —
    não existe mais tabela `client`, então não há merge.
    """
    partes = []
    for f in sorted(DATA_DIR.glob("tests_*.csv")):
        df = pd.read_csv(f)
        partes.append(df)
    tests = pd.concat(partes, ignore_index=True)

    # Normaliza nomes para o padrão usado na análise
    renomear = {
        "client_latitude": "latitude",
        "client_longitude": "longitude",
        "client_city": "city",
        "client_asn": "asn",
        "client_asname": "as_name",
        "client_country_code": "country_code",
    }
    tests = tests.rename(columns={k: v for k, v in renomear.items() if k in tests.columns})
    if "client_longitute" in tests.columns and "longitude" not in tests.columns:
        tests = tests.rename(columns={"client_longitute": "longitude"})

    return tests.dropna(subset=["latitude", "longitude"])


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    """Distância haversine em km (fórmula do m-lab/go/mathx/haversine.go)."""
    import numpy as np

    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(a))


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out_dir = Path(args[0]) if args else None
    if out_dir and not out_dir.is_absolute():
        out_dir = BASE_OUT / out_dir

    if not (DATA_DIR / "sites.csv").exists():
        raise FileNotFoundError(
            "data/sites.csv não existe. Rode extract.py primeiro "
            "(os dados ficam na máquina do QuestDB)."
        )

    print("Carregando dados...")
    tests = carregar()
    print(f"  {len(tests):,} testes no total")

    # Filtra os 2 sites do par
    par = tests[tests["server_site"].isin([SITE_MLAB, SITE_RNP])].copy()
    print(f"  Par comparado: {SITE_MLAB} (MLAB) vs {SITE_RNP} (RNP)")
    print(f"  {len(par):,} testes nos 2 sites")

    # Coordenada registrada de cada site (do sites.csv, se disponível)
    sites_csv = DATA_DIR / "sites.csv"
    coords_sites = {}
    if sites_csv.exists():
        sites = pd.read_csv(sites_csv)
        for s in [SITE_MLAB, SITE_RNP]:
            linha = sites[sites["server_site"] == s]
            if len(linha):
                coords_sites[s] = (
                    linha["latitude"].iloc[0],
                    linha["longitude"].iloc[0],
                )
    print(f"  Coordenadas registradas: {coords_sites}")

    # Distância cliente → site (usando a coordenada registrada do site)
    for site, (slat, slon) in coords_sites.items():
        mask = par["server_site"] == site
        par.loc[mask, "dist_site_km"] = haversine_km(
            par.loc[mask, "latitude"],
            par.loc[mask, "longitude"],
            slat,
            slon,
        )

    # ------------------------------------------------------------------
    # PASSO 1 — visão geral de cada servidor
    # ------------------------------------------------------------------
    linhas = []
    for site in [SITE_MLAB, SITE_RNP]:
        g = par[par["server_site"] == site]
        if len(g) == 0:
            continue
        linha = {
            "server_site": site,
            "rede": "MLAB" if site == SITE_MLAB else "RNP",
            "testes": len(g),
            "clientes_unicos": g["client_ip"].nunique(),
            "cidades_atendidas": g["city"].nunique() if "city" in g.columns else None,
            "dist_mediana_km": (
                round(g["dist_site_km"].median(), 1) if "dist_site_km" in g.columns else None
            ),
            "pct_local_100km": (
                round((g["dist_site_km"] <= LIMITE_LOCAL_KM).mean() * 100, 1)
                if "dist_site_km" in g.columns
                else None
            ),
        }
        # Qualidade — schema novo: métricas embutidas em cada teste
        for col, nome in [
            ("min_rtt", "rtt_mediano_ms"),
            ("mean_throughput_mbps", "throughput_mediana"),
            ("loss_rate", "loss_mediana_pct"),
        ]:
            if col in g.columns:
                valor = g[col].median()
                if col == "loss_rate":
                    valor = valor * 100  # fração → %
                linha[nome] = round(valor, 2)
        linhas.append(linha)

    resumo = pd.DataFrame(linhas)
    print("\n=== PASSO 1 — Visão geral dos 2 sites ===")
    print(resumo.to_string(index=False))

    # Salva na pasta de saída (pizza_<out>/ se out_dir dado, senão na base)
    saida_dir = out_dir if out_dir else BASE_OUT
    saida_dir.mkdir(exist_ok=True)
    resumo.to_csv(saida_dir / "comparacao_sp_passo1.csv", index=False)
    print(f"\n  -> {saida_dir / 'comparacao_sp_passo1.csv'}")

    print(
        "\nPróximos passos (passo 2): distribuição de origem dos clientes "
        "de cada site — as cidades devem ser as mesmas (co-localizados)."
    )


if __name__ == "__main__":
    main()
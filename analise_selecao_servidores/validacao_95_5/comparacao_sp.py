"""
Comparação pareada: gru02 (MLAB) vs gru1916 (RNP) — São Paulo.

Os dois sites são CO-LOCALIZADOS na mesma coordenada registrada
(-23.4322, -46.4692): competem pelo mesmo cliente, mas têm donos e
prioridades diferentes (mlab-oti P=1 vs rnp P≈0,08).

PASSO 1: visão geral de cada servidor
  - volume de testes, clientes únicos, cidades atendidas
  - distância mediana, % de clientes locais (<=100 km)
  - qualidade mediana (RTT, throughput, loss)

PASSO 2: distribuição de origem dos clientes (cidade × site)
  - para cada cidade: % dos testes que foi para gru02 vs gru1916
  - esperado: distribuição praticamente idêntica (co-localizados)

PASSO 3: proximidade comparada
  - distância mediana até CADA site, por cidade
  - diferença ~0 = os 2 são igualmente próximos (co-localizados)
  - diferença grande = coordenada GeoIP da cidade deslocada

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

    # ------------------------------------------------------------------
    # PASSO 2 — distribuição de origem dos clientes (cidade × site)
    # Os 2 sites são co-localizados: a distribuição de origem deve ser
    # praticamente idêntica (o mesmo cliente "deveria" ir para qualquer
    # um dos dois; quem vai para o RNP é a fatia de escape da loteria).
    # ------------------------------------------------------------------
    print("\n=== PASSO 2 — Distribuição de origem (cidade) ===")

    if "city" not in par.columns:
        print("  (sem coluna city — passo 2 pulado)")
    else:
        dist = (
            par.groupby(["city", "server_site"])
            .size()
            .rename("testes")
            .reset_index()
        )
        # % dentro de cada site (linha = cidade, coluna = site)
        piv = dist.pivot_table(index="city", columns="server_site", values="testes", fill_value=0)
        for s in [SITE_MLAB, SITE_RNP]:
            if s not in piv.columns:
                piv[s] = 0
        piv["total"] = piv[SITE_MLAB] + piv[SITE_RNP]
        piv["pct_mlab"] = piv[SITE_MLAB] / piv["total"] * 100
        piv["pct_rnp"] = piv[SITE_RNP] / piv["total"] * 100
        piv = piv.sort_values("total", ascending=False)

        piv.to_csv(saida_dir / "comparacao_sp_passo2_origem.csv", index_label="city")
        print(f"  -> comparacao_sp_passo2_origem.csv ({len(piv)} cidades)")

        # Top 15 cidades para inspeção
        top = piv.head(15)
        print("\nTop 15 cidades por volume (distribuição entre os 2 sites):")
        print(
            top[["total", "pct_mlab", "pct_rnp"]].round(1).to_string()
        )

        # ------------------------------------------------------------------
        # PASSO 3 — os 2 sites seriam os mais próximos para os mesmos clientes?
        # Para cada cidade: distância mediana até CADA site. Como são
        # co-localizados, as distâncias devem ser praticamente iguais —
        # qualquer diferença grande indica coordenada GeoIP divergente.
        # ------------------------------------------------------------------
        print("\n=== PASSO 3 — Proximidade: os 2 são os mais próximos? ===")
        if "dist_site_km" in par.columns:
            prox = (
                par.groupby(["city", "server_site"])["dist_site_km"]
                .median()
                .rename("dist_mediana_km")
                .reset_index()
            )
            prox_piv = prox.pivot_table(
                index="city", columns="server_site", values="dist_mediana_km"
            )
            for s in [SITE_MLAB, SITE_RNP]:
                if s not in prox_piv.columns:
                    prox_piv[s] = None
            prox_piv["diferenca_km"] = (
                prox_piv[SITE_RNP] - prox_piv[SITE_MLAB]
            ).round(1)
            prox_piv["total_testes"] = piv["total"]
            prox_piv = prox_piv.sort_values("total_testes", ascending=False)

            prox_piv.to_csv(
                saida_dir / "comparacao_sp_passo3_proximidade.csv", index_label="city"
            )
            print(f"  -> comparacao_sp_passo3_proximidade.csv")

            top_prox = prox_piv.head(15)
            print(
                top_prox[
                    [SITE_MLAB, SITE_RNP, "diferenca_km", "total_testes"]
                ].round(1).to_string()
            )
            print(
                "\nLeitura: diferenca_km ~0 = os 2 sites são igualmente próximos "
                "para os mesmos clientes (co-localizados). Diferença grande em "
                "uma cidade = a coordenada GeoIP daquela cidade está deslocada."
            )

    print(
        "\nFim. Passo 1 = visão geral; passo 2 = origem por cidade; "
        "passo 3 = proximidade comparada."
    )


if __name__ == "__main__":
    main()
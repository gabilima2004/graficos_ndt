"""
Gera gráficos a partir dos resultados do analyze.py (schema novo).

Gráficos:
  1. PIZZA por cidade: para onde vão as medições da cidade, POR DONO
     (mlab-oti / rnp / equinix / outros) — responde "quem atende cada cidade".
  2. COMPARAÇÃO RNP × M-Lab: painel 2x2 com distribuição global de testes,
     taxa de captura (prioridade) por site, RTT mediano e throughput mediano
     por dono.

Uso:
    python gerar_graficos.py            # usa o out_N/ mais recente
    python gerar_graficos.py out_3      # usa um diretório específico

Requisitos:
    - data/tests_*.csv (rode extract.py primeiro)
    - out_N/ com os CSVs do analyze.py (rode analyze.py primeiro)
    - pandas, matplotlib

Saídas (em graficos_<out_N>/):
    pizzas_cidades.png        — UMA figura com grade de pizzas (top cidades)
    comparacao_rnp_mlab.png   — painel comparativo RNP × mlab-oti
    proporcao_dono.png        — rosca: proporção global rnp/mlab/equinix
    fuga_mais_proximo.png     — quando o mais próximo era X, p/ onde foi o teste
    resumo_pizzas.csv         — tabela cidade × dono
"""

import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
BASE_OUT = Path(__file__).parent

# Quantas cidades entram na grade única de pizzas
TOP_CIDADES = 12

# Paleta fixa por DONO (consistência entre todos os gráficos)
CORES_DONO = {
    "mlab-oti": "#1f77b4",  # azul
    "rnp": "#d62728",       # vermelho
    "equinix": "#7f7f7f",   # cinza
    "outros": "#bbbbbb",
}
COR_OUTROS = "#bbbbbb"

# Mesmos ASN_ORGS do analyze.py (manter em sincronia)
ASN_ORGS = {
    1916: "rnp", 2716: "rnp", 10881: "rnp", 53164: "rnp", 53078: "rnp",
    15830: "equinix", 11242: "rnp",
}


def derivar_dono(site: str, site_asn=None) -> str:
    """Deriva o dono (organização) de um site — mesma lógica do analyze.py."""
    s = str(site).strip()
    m = re.search(r"([a-z]{3})(\d+)$", s)
    if m:
        asn_num = int(m.group(2))
        if asn_num in ASN_ORGS:
            return ASN_ORGS[asn_num]
    if s.startswith("mlab") or re.match(r"^[a-z]{3}\d{2}$", s):
        return "mlab-oti"
    try:
        asn_num = int(str(site_asn).replace("AS", ""))
        if asn_num in ASN_ORGS:
            return ASN_ORGS[asn_num]
    except (ValueError, TypeError):
        pass
    return "outros"


def mais_recente_out() -> Path:
    """Retorna o diretório out*/ mais recente."""
    candidatos = sorted(
        BASE_OUT.glob("out*"),
        key=lambda p: int(p.name.split("_")[1]) if "_" in p.name else 1,
    )
    if not candidatos:
        raise FileNotFoundError("Nenhum out*/ encontrado. Rode analyze.py primeiro.")
    return candidatos[-1]


def carregar() -> pd.DataFrame:
    """Carrega tests_*.csv (schema novo: cliente embutido por teste)."""
    if not list(DATA_DIR.glob("tests_*.csv")):
        raise FileNotFoundError(
            "data/tests_*.csv não existe. Rode extract.py primeiro."
        )
    partes = []
    for f in sorted(DATA_DIR.glob("tests_*.csv")):
        df = pd.read_csv(f, low_memory=False)
        df["mes"] = f.stem.replace("tests_", "")
        partes.append(df)
    tests = pd.concat(partes, ignore_index=True)

    # Normaliza nomes das colunas de cliente (embutidas no schema novo)
    tests = tests.rename(
        columns={
            "client_city": "city",
            "client_latitude": "latitude",
            "client_longitude": "longitude",
        }
    )
    # typo do upload (client_longitute), se vier de upload
    if "client_longitute" in tests.columns and "longitude" not in tests.columns:
        tests = tests.rename(columns={"client_longitute": "longitude"})

    return tests.dropna(subset=["latitude", "longitude"])


def mapa_dono() -> dict[str, str]:
    """Mapa server_site -> owner, a partir do cadastro de sites."""
    sites = pd.read_csv(DATA_DIR / "sites.csv")
    return {
        str(site): derivar_dono(site, asn)
        for site, asn in zip(sites["server_site"], sites.get("site_asn", pd.Series(dtype=str)))
    }


def grade_pizzas(tests: pd.DataFrame, cidades: list[str], arquivo: Path) -> None:
    """UMA figura com grade de pizzas: distribuição por dono das top cidades."""
    n = len(cidades)
    ncols = 4
    nrows = (n + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(4 * ncols, 4 * nrows))
    axes = axes.flatten()

    for ax, cidade in zip(axes, cidades):
        dist = tests[tests["city"] == cidade]["owner"].value_counts()
        total = dist.sum()
        labels = [f"{donor_label(d)}\n{v / total * 100:.1f}%" for d, v in dist.items()]
        cores = [CORES_DONO.get(d, COR_OUTROS) for d in dist.index]
        ax.pie(
            dist.values,
            labels=labels,
            colors=cores,
            startangle=90,
            counterclock=False,
            wedgeprops={"edgecolor": "white", "linewidth": 1},
            textprops={"fontsize": 8},
        )
        ax.set_title(f"{cidade}\nn = {total:,.0f}", fontsize=10)

    # Esconde eixos sobrando (grade não preenchida)
    for ax in axes[n:]:
        ax.axis("off")

    fig.suptitle("Para onde vão as medições — por cidade (top por volume)",
                 fontsize=14, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(arquivo, dpi=150)
    plt.close(fig)
    print(f"  -> {arquivo.name}")


def donor_label(dono: str) -> str:
    """Rótulo legível para o dono."""
    return {"mlab-oti": "M-Lab (OTI)", "rnp": "RNP", "equinix": "Equinix"}.get(dono, dono)


EARTH_RADIUS_KM = 6371.0  # mesmo valor de m-lab/go/mathx/haversine.go


def haversine(lat1, lon1, lat2, lon2):
    """Distância haversine em km — vetorial (mesma fórmula do Locate)."""
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))


def grafico_proporcao_dono(tests: pd.DataFrame, arquivo: Path) -> None:
    """Rosca: proporção global dos testes por dono (rnp/mlab/equinix/...)."""
    dist = tests["owner"].value_counts()
    total = dist.sum()

    labels = [f"{donor_label(d)}\n{v / total * 100:.1f}%\n({v:,.0f} testes)"
              for d, v in dist.items()]
    cores = [CORES_DONO.get(d, COR_OUTROS) for d in dist.index]

    fig, ax = plt.subplots(figsize=(9, 7))
    ax.pie(
        dist.values,
        labels=labels,
        colors=cores,
        startangle=90,
        counterclock=False,
        wedgeprops={"edgecolor": "white", "linewidth": 2, "width": 0.45},
        textprops={"fontsize": 11},
        pctdistance=0.78,
    )
    ax.text(0, 0, f"{total:,.0f}\ntestes", ha="center", va="center",
            fontsize=13, fontweight="bold")
    ax.set_title("Proporção global por dono do servidor\n(todos os testes brasileiros, fev–ago 2026)",
                 fontsize=13, fontweight="bold")
    fig.tight_layout()
    fig.savefig(arquivo, dpi=150)
    plt.close(fig)
    print(f"  -> {arquivo.name}")


def grafico_fuga(tests: pd.DataFrame, sites: pd.DataFrame, arquivo: Path) -> None:
    """Quando o servidor MAIS PRÓXIMO era de X, para onde o teste foi de fato.

    Reproduz a lógica do Locate offline: para cada coordenada distinta de
    cliente, calcula a distância a todas as localizações de sites e identifica
    o dono do mais próximo. Depois cruza com o dono do site realmente usado.

    Matriz de origem (dono do mais próximo) × destino (dono usado):
      - diagonal alta  = dono capturou seus elegíveis (Probability alto)
      - fora da diagonal = fuga (Probability baixo do mais próximo)
    """
    # Localizações distintas de sites (empate = mesma coordenada)
    sites = sites.copy()
    sites["loc_key"] = (
        sites["latitude"].round(6).astype(str) + "|" + sites["longitude"].round(6).astype(str)
    )
    locs = (
        sites.groupby("loc_key")
        .agg(latitude=("latitude", "first"), longitude=("longitude", "first"))
        .reset_index()
    )
    # Dono de cada localização: se o grupo tem sites de donos diferentes,
    # usa o dono do primeiro (co-localizados raramente divergem)
    site_owner = dict(zip(sites["server_site"].astype(str), sites["owner"]))
    loc_owner = (
        sites.assign(owner=sites["server_site"].astype(str).map(site_owner))
        .groupby("loc_key")["owner"]
        .agg(lambda s: s.mode().iloc[0] if len(s.mode()) else "outros")
    )
    locs["owner"] = locs["loc_key"].map(loc_owner)

    # Coordenadas distintas de clientes
    coords = tests[["latitude", "longitude"]].drop_duplicates().reset_index(drop=True)
    print(f"  {len(coords)} coordenadas distintas x {len(locs)} localizações")

    # Distância de cada coordenada a cada localização
    dist = np.empty((len(coords), len(locs)), dtype=np.float64)
    loc_lats = locs["latitude"].to_numpy()
    loc_lons = locs["longitude"].to_numpy()
    for i, (lat, lon) in enumerate(
        zip(coords["latitude"].to_numpy(), coords["longitude"].to_numpy())
    ):
        dist[i] = haversine(lat, lon, loc_lats, loc_lons)

    argmin = dist.argmin(axis=1)
    coord_mais_proximo = locs["owner"].to_numpy()[argmin]  # dono do mais próximo

    # Mapeia cada teste: dono do mais próximo da SUA coordenada + dono usado
    coord_index = {
        (lat, lon): i
        for i, (lat, lon) in enumerate(
            zip(coords["latitude"].to_numpy(), coords["longitude"].to_numpy())
        )
    }
    tests = tests.copy()
    tests["dono_mais_proximo"] = [
        coord_mais_proximo[coord_index[(lat, lon)]]
        for lat, lon in zip(tests["latitude"], tests["longitude"])
    ]

    # Matriz origem × destino
    ordem = ["rnp", "mlab-oti", "equinix", "outros"]
    matriz = (
        tests.groupby(["dono_mais_proximo", "owner"])
        .size()
        .rename("testes")
        .reset_index()
    )
    piv = matriz.pivot(index="dono_mais_proximo", columns="owner", values="testes").fillna(0)
    piv = piv.reindex(index=[o for o in ordem if o in piv.index],
                      columns=[o for o in ordem if o in piv.columns])
    pct = piv.div(piv.sum(axis=1), axis=0) * 100

    # Heatmap com anotações
    fig, ax = plt.subplots(figsize=(9, 6.5))
    im = ax.imshow(pct.values, cmap="Blues", vmin=0, vmax=100, aspect="auto")
    ax.set_xticks(range(len(pct.columns)), [donor_label(c) for c in pct.columns], fontsize=10)
    ax.set_yticks(range(len(pct.index)), [donor_label(r) for r in pct.index], fontsize=10)
    ax.set_xlabel("Para onde o teste foi de fato (dono usado)", fontsize=11)
    ax.set_ylabel("Dono do servidor MAIS PRÓXIMO", fontsize=11)
    ax.set_title("A fuga: quando o mais próximo era X, para onde foi o teste?\n"
                 "(% dos testes, fev–ago 2026)", fontsize=12, fontweight="bold")
    for i in range(pct.shape[0]):
        for j in range(pct.shape[1]):
            v = pct.values[i, j]
            cor = "white" if v > 55 else "black"
            ax.text(j, i, f"{v:.1f}%", ha="center", va="center", color=cor, fontsize=11)
    fig.colorbar(im, ax=ax, label="% dos testes")
    fig.tight_layout()
    fig.savefig(arquivo, dpi=150)
    plt.close(fig)
    print(f"  -> {arquivo.name}")

    # Impressão da leitura no console
    print("\n  Leitura da matriz (linha = dono do mais próximo):")
    print(pct.round(1).to_string())


def grafico_comparacao(out_dir: Path, arquivo: Path) -> None:
    """Painel 2x2 comparando RNP × mlab-oti (lê os CSVs do analyze.py).

    (a) Distribuição global dos testes por dono
    (b) Taxa de captura por site (prioridade implícita), colorido por dono
    (c) RTT mediano por dono
    (d) Throughput mediano por dono
    """
    prior = pd.read_csv(out_dir / "prioridade_por_site.csv")
    dono = pd.read_csv(out_dir / "distribuicao_por_dono.csv")
    qual = pd.read_csv(out_dir / "qualidade_por_dono.csv")

    fig, axes = plt.subplots(2, 2, figsize=(15, 10.5))
    fig.suptitle("Comparação RNP × M-Lab — quem recebe os testes e a qualidade ofertada",
                 fontsize=14, fontweight="bold")

    # ------------------------------------------------------------------
    # (a) Distribuição global por dono
    # ------------------------------------------------------------------
    ax = axes[0, 0]
    d = dono.sort_values("testes", ascending=False)
    cores = [CORES_DONO.get(o, COR_OUTROS) for o in d["owner"]]
    bars = ax.bar([donor_label(o) for o in d["owner"]], d["pct"], color=cores)
    for b, pct in zip(bars, d["pct"]):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.8,
                f"{pct:.1f}%", ha="center", fontsize=10)
    ax.set_title("(a) Para onde vão os testes brasileiros", fontsize=11)
    ax.set_ylabel("% dos testes")
    ax.set_ylim(0, max(d["pct"]) * 1.18)

    # ------------------------------------------------------------------
    # (b) Taxa de captura por site (prioridade implícita)
    # ------------------------------------------------------------------
    ax = axes[0, 1]
    p = prior.dropna(subset=["taxa_captura"]).copy()
    p = p[p["elegiveis"] >= 1000]  # ruído estatístico em grupos pequenos
    p = p.sort_values("taxa_captura")
    cores = [CORES_DONO.get(o, COR_OUTROS) for o in p["owner"]]
    ax.barh(p["sites_do_grupo"], p["taxa_captura"] * 100, color=cores)
    ax.axvline(95, color="black", linestyle="--", linewidth=1.2)
    ax.text(95, len(p) - 0.4, " teto teórico 95%\n (Probability=1)",
            fontsize=8, va="top")
    ax.set_title("(b) Taxa de captura por site = prioridade no cadastro", fontsize=11)
    ax.set_xlabel("% dos testes elegíveis capturados")
    ax.tick_params(axis="y", labelsize=7)

    # Legenda manual de donos
    from matplotlib.patches import Patch
    legendas = [Patch(facecolor=CORES_DONO["mlab-oti"], label="M-Lab (OTI)"),
                Patch(facecolor=CORES_DONO["rnp"], label="RNP"),
                Patch(facecolor=CORES_DONO["equinix"], label="Equinix"),
                Patch(facecolor=CORES_DONO["outros"], label="Outros")]
    ax.legend(handles=legendas, fontsize=8, loc="lower right")

    # ------------------------------------------------------------------
    # (c) RTT mediano por dono
    # ------------------------------------------------------------------
    ax = axes[1, 0]
    q = qual.sort_values("rtt_mediano")
    cores = [CORES_DONO.get(o, COR_OUTROS) for o in q["owner"]]
    bars = ax.bar([donor_label(o) for o in q["owner"]], q["rtt_mediano"], color=cores)
    for b, v in zip(bars, q["rtt_mediano"]):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.3,
                f"{v:.1f} ms", ha="center", fontsize=10)
    ax.set_title("(c) RTT mediano por dono (menor = melhor)", fontsize=11)
    ax.set_ylabel("RTT mediano (ms)")
    ax.set_ylim(0, max(q["rtt_mediano"]) * 1.18)

    # ------------------------------------------------------------------
    # (d) Throughput mediano por dono
    # ------------------------------------------------------------------
    ax = axes[1, 1]
    q = qual.sort_values("throughput_mediana", ascending=False)
    cores = [CORES_DONO.get(o, COR_OUTROS) for o in q["owner"]]
    bars = ax.bar([donor_label(o) for o in q["owner"]], q["throughput_mediana"], color=cores)
    for b, v in zip(bars, q["throughput_mediana"]):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1,
                f"{v:.1f} Mbps", ha="center", fontsize=10)
    ax.set_title("(d) Throughput mediano por dono", fontsize=11)
    ax.set_ylabel("Throughput mediano (Mbps)")
    ax.set_ylim(0, max(q["throughput_mediana"]) * 1.18)

    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(arquivo, dpi=150)
    plt.close(fig)
    print(f"  -> {arquivo.name}")


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out_dir = Path(args[0]) if args else mais_recente_out()
    if not out_dir.is_absolute():
        out_dir = BASE_OUT / out_dir
    if not out_dir.exists():
        raise FileNotFoundError(f"Diretório {out_dir} não existe.")

    print(f"Carregando dados (referência: {out_dir.name}/)...")
    tests = carregar()
    tests = tests.dropna(subset=["city"])

    # Dono de cada server_site
    dono_map = mapa_dono()
    tests["owner"] = tests["server_site"].astype(str).map(dono_map).fillna("outros")

    volumes = tests.groupby("city").size().sort_values(ascending=False)
    alvos = volumes.head(TOP_CIDADES).index.tolist()
    print(f"  {len(tests):,} testes, {volumes.shape[0]} cidades distintas")
    print(f"  Grade de pizzas para as {len(alvos)} maiores cidades")

    saida_dir = BASE_OUT / f"graficos_{out_dir.name}"
    saida_dir.mkdir(exist_ok=True)

    # Tabela-resumo: distribuição completa cidade × dono
    resumo = (
        tests.groupby(["city", "owner"])
        .size()
        .rename("testes")
        .reset_index()
    )
    resumo["pct_na_cidade"] = (
        resumo.groupby("city")["testes"].transform(lambda s: s / s.sum() * 100)
    )
    resumo = resumo.sort_values(["city", "testes"], ascending=[True, False])
    resumo.to_csv(saida_dir / "resumo_pizzas.csv", index=False)
    print(f"  -> resumo_pizzas.csv (distribuição completa por cidade)")

    # UMA figura com as top cidades
    print(f"\nGerando grade de pizzas em {saida_dir.name}/ ...")
    grade_pizzas(tests, alvos, saida_dir / "pizzas_cidades.png")

    # Proporção global por dono
    print("\nGerando proporção global por dono...")
    grafico_proporcao_dono(tests, saida_dir / "proporcao_dono.png")

    # Fuga: mais próximo era X, teste foi para Y
    print("\nGerando matriz de fuga (mais próximo × usado)...")
    sites = pd.read_csv(DATA_DIR / "sites.csv")
    sites["owner"] = (
        sites["server_site"].astype(str).map(dono_map).fillna("outros")
    )
    grafico_fuga(tests, sites, saida_dir / "fuga_mais_proximo.png")

    # Gráfico comparativo RNP × M-Lab (lê os CSVs do analyze.py)
    print("\nGerando comparação RNP × M-Lab...")
    grafico_comparacao(out_dir, saida_dir / "comparacao_rnp_mlab.png")

    print(f"\nConcluído. Saídas em {saida_dir.name}/:")
    print("  pizzas_cidades.png, proporcao_dono.png, fuga_mais_proximo.png,")
    print("  comparacao_rnp_mlab.png, resumo_pizzas.csv")


if __name__ == "__main__":
    main()
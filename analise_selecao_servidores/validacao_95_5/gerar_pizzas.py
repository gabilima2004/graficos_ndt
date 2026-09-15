"""
Gera gráficos de PIZZA: para cada cidade, para onde vão as medições.

Cada pizza responde: "dos testes feitos pelos clientes da cidade X,
qual % foi para cada servidor?"

Uso:
    python gerar_graficos.py            # usa o out_N/ mais recente (referência)
    python gerar_graficos.py out_5      # usa um diretório específico
    python gerar_graficos.py out_5 --min 50000   # muda o corte mínimo de testes

Requisitos:
    - data/clients.csv e data/tests_*.csv (rode extract.py primeiro)
    - pandas, matplotlib

Saídas (em pizza_<out_N>/):
    pizza_<cidade>.png  — um gráfico por cidade com volume relevante
    resumo_pizzas.csv   — a tabela de distribuição cidade × servidor
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
BASE_OUT = Path(__file__).parent

# Cidades com volume mínimo para ganhar pizza própria
MIN_TESTES_CIDADE = 20_000
# Top N servidores na pizza; o resto vira "Outros"
TOP_N_SERVIDORES = 6

# Paleta fixa por site (consistência entre pizzas)
CORES_SITES = {
    "gru02": "#1f77b4", "gru03": "#aec7e8", "gru06": "#4c72b0",
    "gru07": "#8c6d31", "gru15830": "#e377c2", "gru1916": "#c5b0d5",
    "gig1916": "#d62728", "cwb10881": "#ff7f0e", "poa2716": "#2ca02c",
    "bsb1916": "#9467bd", "ssa53164": "#8c564b", "rec1916": "#17becf",
    "fln01": "#bcbd22", "fln11242": "#7f7f7f", "vix1916": "#e7969c",
    "vix53078": "#c49c94", "for1916": "#f7b6d2", "bel1916": "#98df8a",
    "cgb1916": "#aec7e8", "gyn1916": "#ffbb78", "slz1916": "#c7c7c7",
    "mao1916": "#b5cf6b", "nat1916": "#fdd9a7", "the1916": "#e6ba7d",
    "aju1916": "#ad494a", "cpv1916": "#f9d4a5", "mcz1916": "#c49c94",
    "cgr1916": "#d9a0a0", "bvb1916": "#a0cbe8", "rbr1916": "#b0a0d9",
    "mcp1916": "#a0d9c0", "pmw1916": "#d9c0a0", "pvh1916": "#c0d9a0",
}
COR_OUTROS = "#bbbbbb"


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
    """Carrega clients.csv + tests_*.csv, junta e devolve testes com cidade."""
    clients = pd.read_csv(DATA_DIR / "clients.csv", low_memory=False)
    clients["update_time"] = pd.to_datetime(clients["update_time"], errors="coerce")
    clients = (
        clients.sort_values("update_time")
        .drop_duplicates(subset="client_ip", keep="last")
    )
    clients = clients.dropna(subset=["latitude", "longitude"])

    partes = []
    for f in sorted(DATA_DIR.glob("tests_*.csv")):
        mes = f.stem.replace("tests_", "")
        df = pd.read_csv(f)
        df["mes"] = mes
        partes.append(df)
    tests = pd.concat(partes, ignore_index=True)

    tests = tests.merge(
        clients[["client_ip", "latitude", "longitude", "city"]],
        on="client_ip",
        how="inner",
    ).dropna(subset=["latitude", "longitude"])
    return tests


def pizza(df_grupo: pd.DataFrame, titulo: str, arquivo: Path) -> None:
    """Gera um gráfico de pizza da distribuição de servidores de um grupo."""
    dist = df_grupo["server_site"].value_counts()
    total = dist.sum()

    # Top N + Outros
    top = dist.head(TOP_N_SERVIDORES).copy()
    if len(dist) > TOP_N_SERVIDORES:
        top["Outros"] = dist.iloc[TOP_N_SERVIDORES:].sum()

    labels, valores, cores = [], [], []
    for site, n in top.items():
        pct = n / total * 100
        labels.append(f"{site}\n{pct:.1f}%")
        valores.append(n)
        cores.append(COR_OUTROS if site == "Outros" else CORES_SITES.get(site, COR_OUTROS))

    fig, ax = plt.subplots(figsize=(8, 6.5))
    ax.pie(
        valores,
        labels=labels,
        colors=cores,
        startangle=90,
        counterclock=False,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
        textprops={"fontsize": 9},
    )
    ax.set_title(f"{titulo}\nn = {total:,.0f} testes", fontsize=12)
    fig.tight_layout()
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

    min_testes = MIN_TESTES_CIDADE
    for a in sys.argv[1:]:
        if a.startswith("--min="):
            min_testes = int(a.split("=")[1])

    if not (DATA_DIR / "clients.csv").exists():
        raise FileNotFoundError(
            "data/clients.csv não existe. Rode extract.py primeiro "
            "(os dados ficam na máquina do QuestDB)."
        )

    print(f"Carregando dados (referência: {out_dir.name}/)...")
    tests = carregar()
    tests = tests.dropna(subset=["city"])

    volumes = tests.groupby("city").size().sort_values(ascending=False)
    alvos = volumes[volumes >= min_testes]
    print(f"  {len(tests):,} testes, {volumes.shape[0]} cidades distintas")
    print(f"  Pizzas para {len(alvos)} cidades com >= {min_testes:,} testes")

    # Lista de coordenadas distintas por cidade (para inspeção do GeoIP)
    coords = (
        tests.groupby("city")
        .agg(
            latitude=("latitude", "first"),
            longitude=("longitude", "first"),
            n_coords=("latitude", "nunique"),
            testes=("latitude", "size"),
        )
        .sort_values("testes", ascending=False)
    )
    coords.to_csv(BASE_OUT / "coordenadas_por_cidade.csv", index_label="city")
    print(f"  -> coordenadas_por_cidade.csv (lat/lon de cada cidade)")
    print("\nTop 20 cidades por volume (com coordenadas):")
    print(coords.head(20).to_string())

    saida_dir = BASE_OUT / f"pizza_{out_dir.name}"
    saida_dir.mkdir(exist_ok=True)

    # Tabela-resumo: distribuição completa cidade × servidor
    resumo = (
        tests.groupby(["city", "server_site"])
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

    print(f"\nGerando pizzas em {saida_dir.name}/ ...")
    for cidade in alvos.index:
        df_cidade = tests[tests["city"] == cidade]
        titulo = f"Para onde vão as medições — {cidade}"
        pizza(df_cidade, titulo, saida_dir / f"pizza_{cidade.replace(' ', '_').replace('/', '-')}.png")

    print(f"\nConcluído. {len(alvos)} pizzas em {saida_dir.name}/")


if __name__ == "__main__":
    main()
"""
SÍNTESE VISUAL — figuras de comunicação do experimento co-localizado de SP

Lê APENAS os CSVs já gerados pelo foco_gru.py em out_foco/ (não reprocessa
os 33M de testes — roda em segundos) e gera as 2 figuras para apresentação:

  1. volumes_por_site.png — barras horizontais ABSOLUTAS por site, empilhadas
     (pool = do próprio pool SP; escape = de fora do pool) + linha do pool.
     Mensagem: "quanto cada servidor atendeu, e de onde veio o volume".

  2. fatias_mensais.png — série mensal da fatia (%) de cada site.
     Mensagem: "o RNP é estável como cadastro; os M-Lab/Equinix são
     gerenciados dinamicamente (entram, saem, ramp-up)".

Uso:
    python sintese.py                 # lê out_foco/ e gera os 2 PNGs em sintese/
    python sintese.py out_foco_2      # usa outro diretório de entrada

Requisitos: pandas, matplotlib
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

BASE = Path(__file__).parent

CORES_DONO = {"mlab-oti": "#1f77b4", "rnp": "#d62728", "equinix": "#7f7f7f", "outros": "#bbbbbb"}
COR_POOL = {"mlab-oti": "#1f77b4", "rnp": "#d62728", "equinix": "#7f7f7f", "outros": "#bbbbbb"}
COR_ESCAPE = {"mlab-oti": "#9ecae1", "rnp": "#f4a582", "equinix": "#bdbdbd", "outros": "#e0e0e0"}
LABEL_DONO = {"mlab-oti": "M-Lab (OTI)", "rnp": "RNP", "equinix": "Equinix", "outros": "Outros"}


def dono_de(site: str) -> str:
    """Deriva o dono pelo sufixo do nome (mesma regra do foco_gru/analyze)."""
    import re
    ASN_ORGS = {1916: "rnp", 2716: "rnp", 10881: "rnp", 53164: "rnp",
                53078: "rnp", 15830: "equinix", 11242: "rnp"}
    s = str(site).strip()
    m = re.search(r"([a-z]{3})(\d+)$", s)
    if m and int(m.group(2)) in ASN_ORGS:
        return ASN_ORGS[int(m.group(2))]
    # Padrões mlab-oti: xxxNN (2 dígitos, ex: gru02, lim01) e nomes físicos conhecidos
    if s.startswith("mlab") or re.match(r"^[a-z]{3}\d{2}$", s) or s in ("fln01",):
        return "mlab-oti"
    return "outros"


def carregar_dados(out_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Lê fatias_grupo.csv (com owner) e fatias_por_mes.csv do out_dir."""
    fatias = pd.read_csv(out_dir / "fatias_grupo.csv")
    # normaliza nome da coluna de índice (server_site)
    col0 = fatias.columns[0]
    fatias = fatias.rename(columns={col0: "server_site"})
    if "owner" not in fatias.columns:
        fatias["owner"] = fatias["server_site"].map(dono_de)

    fatias_mes = pd.read_csv(out_dir / "fatias_por_mes.csv")
    col0m = fatias_mes.columns[0]
    fatias_mes = fatias_mes.rename(columns={col0m: "server_site"})
    return fatias, fatias_mes


def fig_volumes(out_dir: Path, fatias: pd.DataFrame, arquivo: Path) -> None:
    """Barras horizontais absolutas: pool (escuro) + escape (claro), por site."""
    # escape por site (se existir o CSV)
    esc_col = "capturados_escape"
    if (out_dir / "escape_por_site.csv").exists():
        esc = pd.read_csv(out_dir / "escape_por_site.csv")
        col0 = esc.columns[0]
        esc = esc.rename(columns={col0: "server_site"}).set_index("server_site")
        fatias = fatias.set_index("server_site")
        fatias[esc_col] = esc[esc_col].reindex(fatias.index).fillna(0).astype(int)
        fatias = fatias.reset_index()
    else:
        fatias[esc_col] = 0
        print("  AVISO: escape_por_site.csv não encontrado — só pool será plotado")

    d = fatias.sort_values("capturados")  # menor no fundo → maior no topo
    y = range(len(d))

    fig, ax = plt.subplots(figsize=(12, 6.5))
    for dono in d["owner"].unique():
        mask = d["owner"] == dono
        ax.barh(
            [y[i] for i in mask.to_numpy().nonzero()[0]],
            d.loc[mask, "capturados"],
            color=COR_POOL.get(dono, "#bbb"),
            label=f"{LABEL_DONO.get(dono, dono)} — do pool",
        )
        ax.barh(
            [y[i] for i in mask.to_numpy().nonzero()[0]],
            d.loc[mask, esc_col],
            left=d.loc[mask, "capturados"],
            color=COR_ESCAPE.get(dono, "#ddd"),
            label=f"{LABEL_DONO.get(dono, dono)} — de fora do pool",
        )

    # anotações: volume total + % do pool
    for i, (_, r) in enumerate(d.iterrows()):
        total = r["capturados"] + r[esc_col]
        pct = r.get("fatia_obs", r["capturados"] / d["capturados"].sum())
        ax.text(total + d["capturados"].max() * 0.01, i,
                f"{total:,.0f}  ({pct * 100:.1f}% do pool)",
                va="center", fontsize=10)

    # linha de referência: tamanho do pool
    pool = d["capturados"].sum()
    ax.axvline(pool, color="black", linestyle="--", linewidth=1.2)
    ax.text(pool, len(d) - 0.35, f" pool SP = {pool:,.0f} elegíveis",
            fontsize=9, style="italic")

    ax.set_yticks(list(y), d["server_site"], fontsize=11)
    ax.set_xlabel("testes atendidos (volume absoluto)", fontsize=11)
    ax.set_title("Grupo co-localizado de SP — quanto cada servidor atendeu\n"
                 "(fev–ago 2026; segmento claro = testes de fora do pool SP)",
                 fontsize=13, fontweight="bold")
    ax.legend(fontsize=9, loc="lower right")
    ax.margins(x=0.18)
    fig.tight_layout()
    fig.savefig(arquivo, dpi=150)
    plt.close(fig)
    print(f"  -> {arquivo.name}")


def fig_fatias_mensais(fatias_mes: pd.DataFrame, arquivo: Path) -> None:
    """Série mensal da fatia (%) de cada site — gru1916 destacado."""
    d = fatias_mes.set_index("server_site")
    meses = [c for c in d.columns if c[:2] == "20"]
    d = d[meses]

    fig, ax = plt.subplots(figsize=(12, 6.5))
    x = range(len(meses))

    # sites de referência da narrativa
    destaque = {"gru1916": dict(color=CORES_DONO["rnp"], linewidth=3, marker="o", zorder=5),
                "gru15830": dict(color=CORES_DONO["equinix"], linewidth=2, marker="s"),
                "gru02": dict(color=CORES_DONO["mlab-oti"], linewidth=2, marker="o"),
                "gru03": dict(color="#6baed6", linewidth=2, marker="o", linestyle="--"),
                "gru06": dict(color="#2171b5", linewidth=1.5, marker="v", linestyle=":"),
                "gru07": dict(color="#08519c", linewidth=1.5, marker="^", linestyle=":")}

    for site, linha in d.iterrows():
        estilo = destaque.get(site, dict(color="#cccccc", linewidth=1, alpha=0.6))
        ax.plot(x, linha.values * 100, label=site, **estilo)

    ax.set_xticks(list(x), meses, fontsize=10)
    ax.set_ylabel("fatia do pool SP (%)", fontsize=11)
    ax.set_title("Fatia do pool SP por site, mês a mês\n"
                 "linha reta = campo estático de cadastro; variação = gestão dinâmica",
                 fontsize=13, fontweight="bold")
    ax.legend(fontsize=9, ncol=2, loc="upper right")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(arquivo, dpi=150)
    plt.close(fig)
    print(f"  -> {arquivo.name}")


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    in_dir = BASE / (args[0] if args else "out_foco")
    if not in_dir.exists():
        raise FileNotFoundError(f"{in_dir} não existe — rode foco_gru.py primeiro.")

    # Saída em pasta própria (sintese/) para não bagunçar o out_foco/
    out_dir = BASE / "sintese"
    out_dir.mkdir(exist_ok=True)

    print(f"Lendo CSVs de {in_dir}/ ...")
    fatias, fatias_mes = carregar_dados(in_dir)
    print(f"  {len(fatias)} sites, {len(fatias_mes.columns) - 1} meses")

    print(f"Gerando figuras em {out_dir.name}/ ...")
    fig_volumes(in_dir, fatias, out_dir / "volumes_por_site.png")
    fig_fatias_mensais(fatias_mes, out_dir / "fatias_mensais.png")

    print(f"\nConcluído. Figuras em {out_dir}/:")
    print("  volumes_por_site.png  (slide principal: volume absoluto + origem)")
    print("  fatias_mensais.png    (slide principal: estabilidade = cadastro)")


if __name__ == "__main__":
    main()
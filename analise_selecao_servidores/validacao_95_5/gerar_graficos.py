"""
Gera os gráficos do relatório oficial a partir dos CSVs de evidência (out_N/).

Uso:
    python gerar_graficos.py            # usa o out_N/ mais recente
    python gerar_graficos.py out_4      # usa um diretório específico

Saídas (na mesma pasta do out_N/):
    fig1_histograma.png  — histograma de ranks: observado vs esperado (95/5)
    fig2_captura.png     — taxa de captura por grupo de sites (a evidência central)
    fig3_captura_mes.png — captura por mês (assinatura do campo estático)

Requisitos: pandas, matplotlib
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# ---------------------------------------------------------------------------

# Rótulos amigáveis para os grupos de sites (chave = sites_do_grupo do CSV)
ROTULOS = {
    "gru02, gru03, gru06, gru07, gru15830, gru1916": "São Paulo (6 sites)",
    "fln01, fln11242": "Florianópolis",
    "vix1916, vix53078": "Vitória",
    "gig1916": "Rio de Janeiro",
    "cwb10881": "Curitiba",
}

CAPTURA_ESPERADA = 0.95  # se o site foi oferecido em todas as requisições


def mais_recente_out() -> Path:
    """Retorna o diretório out*/ mais recente (out, out_2, out_3, ...)."""
    base = Path(__file__).parent
    candidatos = sorted(
        base.glob("out*"), key=lambda p: int(p.name.split("_")[1]) if "_" in p.name else 1
    )
    if not candidatos:
        raise FileNotFoundError(
            "Nenhum diretório out*/ encontrado. Rode analyze.py primeiro."
        )
    return candidatos[-1]


def rotulo_grupo(sites_do_grupo: str) -> str:
    """Rótulo curto para o grupo; grupos grandes viram 'Demais (N sites)'."""
    if sites_do_grupo in ROTULOS:
        return ROTULOS[sites_do_grupo]
    n = len(sites_do_grupo.split(","))
    return f"Demais ({n} sites)"


def fig1_histograma(out_dir: Path) -> None:
    """Histograma de ranks: observado vs esperado pelo código (95/5/0,01)."""
    df = pd.read_csv(out_dir / "rank_histogram.csv")
    df = df[df["rank"] <= 5].copy()  # ranks 0-5 (2+ é residual)
    df["rotulo"] = df["rank"].map(
        {0: "rank 0\n(mais próximo)", 1: "rank 1\n(2º)", 2: "rank 2", 3: "rank 3", 4: "rank 4", 5: "rank 5"}
    )

    # Esperado pelo código: exponencial rate=6
    esperado = {0: 0.9502, 1: 0.0498}
    esperado.update({r: 0.0001 for r in range(2, 6)})

    fig, ax = plt.subplots(figsize=(9, 5))
    x = range(len(df))
    largura = 0.38
    ax.bar(
        [i - largura / 2 for i in x],
        df["proporcao"] * 100,
        largura,
        label="Observado",
        color="#2c7bb6",
    )
    ax.bar(
        [i + largura / 2 for i in x],
        [esperado[r] * 100 for r in df["rank"]],
        largura,
        label="Esperado (código, lista completa)",
        color="#f4a582",
    )
    ax.set_xticks(list(x))
    ax.set_xticklabels(df["rotulo"])
    ax.set_ylabel("% dos testes")
    ax.set_title(
        "Rank do servidor usado vs esperado pelo código\n"
        "(rank calculado offline com a lista completa de sites)"
    )
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "fig1_histograma.png", dpi=150)
    plt.close(fig)
    print(f"  -> {out_dir / 'fig1_histograma.png'}")


def fig2_captura(out_dir: Path) -> None:
    """Taxa de captura por grupo de sites — a evidência central."""
    df = pd.read_csv(out_dir / "captura_por_site.csv")
    df = df[df["elegiveis"] >= 1000].copy()  # grupos com amostra relevante
    df["rotulo"] = df["sites_do_grupo"].map(rotulo_grupo)
    df = df.sort_values("taxa_captura", ascending=False)

    fig, ax = plt.subplots(figsize=(10, 5.5))
    cores = ["#2c7bb6" if t >= 0.90 else "#f4a582" if t >= 0.50 else "#d73027" for t in df["taxa_captura"]]
    barras = ax.bar(df["rotulo"], df["taxa_captura"] * 100, color=cores)

    # Linha tracejada em 95% (esperado se sempre oferecido)
    ax.axhline(95, color="#444444", linestyle="--", linewidth=1.2)
    ax.text(
        len(df) - 0.4, 96.5, "95% esperado\n(se sempre oferecido)",
        ha="right", fontsize=9, color="#444444",
    )

    for barra, taxa, elegiveis in zip(barras, df["taxa_captura"], df["elegiveis"]):
        ax.text(
            barra.get_x() + barra.get_width() / 2,
            barra.get_height() + 1.5,
            f"{taxa * 100:.1f}%\n(n={elegiveis:,.0f})",
            ha="center", fontsize=8,
        )

    ax.set_ylabel("Taxa de captura (%)")
    ax.set_title(
        "Taxa de captura por grupo de sites\n"
        "dos testes cujo grupo mais próximo era ele, quantos % o usaram?"
    )
    ax.set_ylim(0, 112)
    ax.grid(axis="y", alpha=0.3)
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right", fontsize=9)
    fig.tight_layout()
    fig.savefig(out_dir / "fig2_captura.png", dpi=150)
    plt.close(fig)
    print(f"  -> {out_dir / 'fig2_captura.png'}")


def fig3_captura_mes(out_dir: Path) -> None:
    """Captura por mês — a assinatura do campo estático (taxa não flutua)."""
    df = pd.read_csv(out_dir / "captura_por_site_mes.csv", index_col=0)
    colunas_mes = [c for c in df.columns if c not in ("sites_do_grupo",)]
    df = df[df["sites_do_grupo"].notna()]

    # Só grupos com amostra relevante e mais de um mês de dados
    df = df[df["elegiveis"] >= 1000] if "elegiveis" in df.columns else df
    df = df[df[colunas_mes].notna().sum(axis=1) >= 2]

    fig, ax = plt.subplots(figsize=(9, 5))
    for idx, linha in df.iterrows():
        rotulo = rotulo_grupo(linha["sites_do_grupo"])
        ax.plot(
            colunas_mes,
            [linha[c] * 100 for c in colunas_mes],
            marker="o",
            label=rotulo,
        )

    ax.axhline(95, color="#444444", linestyle="--", linewidth=1.2, label="95% esperado")
    ax.set_ylabel("Taxa de captura (%)")
    ax.set_xlabel("Mês")
    ax.set_title(
        "Taxa de captura por mês\n"
        "taxa estável = campo estático de cadastro (Probability), não saúde flutuante"
    )
    ax.legend(fontsize=8, ncol=2)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "fig3_captura_mes.png", dpi=150)
    plt.close(fig)
    print(f"  -> {out_dir / 'fig3_captura_mes.png'}")


def main() -> None:
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else mais_recente_out()
    if not out_dir.is_absolute():
        out_dir = Path(__file__).parent / out_dir
    if not out_dir.exists():
        raise FileNotFoundError(f"Diretório {out_dir} não existe.")
    print(f"Gerando gráficos a partir de {out_dir.name}/ ...")

    fig1_histograma(out_dir)
    fig2_captura(out_dir)
    fig3_captura_mes(out_dir)

    print("\nConcluído. Insira os PNGs no RELATORIO.md nas marcações [INSERIR GRÁFICO N].")


if __name__ == "__main__":
    main()
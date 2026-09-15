"""
Gera o gráfico MLAB vs RNP: distribuição das medições entre as duas redes.

Classificação dos sites:
  - MLAB (núcleo M-Lab OTI): nomes antigos sem sufixo 1916 e sem 5 dígitos
    (gru02, gru03, gru06, gru07, gru15830, fln01, fln11242, lim01, lim02, ...)
  - RNP (parceiros autojoin): sufixo 1916 (gig1916, cwb10881, poa2716, ...)
    — nomenclatura nova de 5 dígitos (gru15830, ams15830...) é tratada à parte
      ou como MLAB, conforme o parâmetro --cinco-digitos

Uso:
    python grafico_mlab_rnp.py            # usa o out_N/ mais recente
    python grafico_mlab_rnp.py out_5      # usa um diretório específico
    python grafico_mlab_rnp.py out_5 --cinco-digitos-rnp  # trata 5 dígitos como RNP

Requisitos:
    - data/clients.csv e data/tests_*.csv (rode extract.py primeiro)
    - pandas, matplotlib

Saídas (em pizza_<out_N>/):
    fig_mlab_rnp.png   — barras: % das medições em MLAB vs RNP (total e por mês)
    resumo_mlab_rnp.csv — a tabela completa por site
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
BASE_OUT = Path(__file__).parent

COR_MLAB = "#1f77b4"   # azul
COR_RNP = "#d62728"    # vermelho


def mais_recente_out() -> Path:
    candidatos = sorted(
        BASE_OUT.glob("out*"),
        key=lambda p: int(p.name.split("_")[1]) if "_" in p.name else 1,
    )
    if not candidatos:
        raise FileNotFoundError("Nenhum out*/ encontrado. Rode analyze.py primeiro.")
    return candidatos[-1]


# Sites de nomenclatura nova (5 dígitos) com hostname .rnp.autojoin — RNP
# (verificado nos hostnames da base: ndt-<site>-<hash>.rnp.autojoin.measurement-lab.org)
# Os demais 5 dígitos (fln11242) têm hostname .mlab-oti — MLAB
RNP_CINCO_DIGITOS = {
    "gru15830", "ams15830", "fra15830", "lim15830", "scl15830",
    "cwb10881", "bsb1916", "vix53078", "ssa53164", "poa2716",
}


def classificar(site: str) -> str:
    """Classifica um server_site como MLAB ou RNP.

    Regras (baseadas nos hostnames reais da base):
      - sufixo 1916 (RNP) → RNP
      - sufixo de 4 dígitos != 1916 (poa2716) → RNP
      - nomenclatura de 5 dígitos → RNP se estiver em RNP_CINCO_DIGITOS
        (hostname .rnp.autojoin), senão MLAB (hostname .mlab-oti, ex: fln11242)
      - sufixo de 2 dígitos (01, 02, 03...) → MLAB (núcleo M-Lab OTI)
    """
    if site.endswith("1916"):
        return "RNP"
    sufixo = site[3:]
    if sufixo.isdigit():
        if len(sufixo) == 4:
            return "RNP"  # poa2716 e similares (autojoin RNP)
        if len(sufixo) == 5:
            return "RNP" if site in RNP_CINCO_DIGITOS else "MLAB"
    return "MLAB"


def carregar() -> pd.DataFrame:
    """Carrega clients.csv + tests_*.csv e junta pelo client_ip."""
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
        if mes < "2026-06":  # mês fantasma
            continue
        df = pd.read_csv(f)
        df["mes"] = mes
        partes.append(df)
    tests = pd.concat(partes, ignore_index=True)

    return tests.merge(
        clients[["client_ip"]],
        on="client_ip",
        how="inner",
    )


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out_dir = Path(args[0]) if args else mais_recente_out()
    if not out_dir.is_absolute():
        out_dir = BASE_OUT / out_dir
    if not out_dir.exists():
        raise FileNotFoundError(f"Diretório {out_dir} não existe.")

    cinco_digitos_rnp = "--cinco-digitos-rnp" in sys.argv

    if not (DATA_DIR / "clients.csv").exists():
        raise FileNotFoundError(
            "data/clients.csv não existe. Rode extract.py primeiro "
            "(os dados ficam na máquina do QuestDB)."
        )

    print(f"Carregando dados (referência: {out_dir.name}/)...")
    tests = carregar()
    print(f"  {len(tests):,} testes")

    # Classifica cada site
    sites = tests["server_site"].value_counts()
    classificacao = {s: classificar(s) for s in sites.index}
    tests["rede"] = tests["server_site"].map(classificacao)

    # Tabela por site
    por_site = (
        tests.groupby(["rede", "server_site"])
        .size()
        .rename("testes")
        .reset_index()
        .sort_values("testes", ascending=False)
    )
    total = por_site["testes"].sum()
    por_site["pct_total"] = por_site["testes"] / total * 100

    saida_dir = BASE_OUT / f"pizza_{out_dir.name}"
    saida_dir.mkdir(exist_ok=True)
    por_site.to_csv(saida_dir / "resumo_mlab_rnp.csv", index=False)
    print(f"  -> resumo_mlab_rnp.csv")

    # Totais por rede
    totais = por_site.groupby("rede")["testes"].sum()
    pct_mlab = totais.get("MLAB", 0) / total * 100
    pct_rnp = totais.get("RNP", 0) / total * 100
    print(f"\n  MLAB: {totais.get('MLAB', 0):,} testes ({pct_mlab:.1f}%)")
    print(f"  RNP:  {totais.get('RNP', 0):,} testes ({pct_rnp:.1f}%)")

    # ------------------------------------------------------------------
    # Figura: 2 painéis
    #   (a) pizza total MLAB vs RNP
    #   (b) barras por mês (junho vs julho)
    # ------------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # (a) Pizza total
    ax1.pie(
        [totais.get("MLAB", 0), totais.get("RNP", 0)],
        labels=[f"MLAB\n{pct_mlab:.1f}%", f"RNP\n{pct_rnp:.1f}%"],
        colors=[COR_MLAB, COR_RNP],
        startangle=90,
        counterclock=False,
        wedgeprops={"edgecolor": "white", "linewidth": 2},
        textprops={"fontsize": 12},
    )
    ax1.set_title(f"Distribuição total\n(n = {total:,.0f} testes)", fontsize=12)

    # (b) Barras por mês
    por_mes = (
        tests.groupby(["mes", "rede"])
        .size()
        .rename("testes")
        .reset_index()
    )
    por_mes["pct"] = por_mes.groupby("mes")["testes"].transform(
        lambda s: s / s.sum() * 100
    )
    meses = sorted(por_mes["mes"].unique())
    largura = 0.35
    for i, rede in enumerate(["MLAB", "RNP"]):
        vals = [
            por_mes[(por_mes["mes"] == m) & (por_mes["rede"] == rede)]["pct"].sum()
            for m in meses
        ]
        ax2.bar(
            [idx + (i - 0.5) * largura for idx in range(len(meses))],
            vals,
            largura,
            label=rede,
            color=COR_MLAB if rede == "MLAB" else COR_RNP,
        )
        for idx, v in enumerate(vals):
            ax2.text(
                idx + (largura / 2 if rede == "RNP" else -largura / 2),
                v + 1,
                f"{v:.1f}%",
                ha="center",
                fontsize=10,
            )
    ax2.set_xticks(list(range(len(meses))))
    ax2.set_xticklabels([m.replace("2026-", "") for m in meses])
    ax2.set_ylabel("% das medições")
    ax2.set_title("Por mês", fontsize=12)
    ax2.legend()
    ax2.set_ylim(0, 100)
    ax2.grid(axis="y", alpha=0.3)

    sufixo = " (5 dígitos = RNP)" if cinco_digitos_rnp else ""
    fig.suptitle(
        "Para onde vão as medições: MLAB vs RNP", fontsize=13, y=1.02
    )
    fig.tight_layout()
    arquivo = saida_dir / "fig_mlab_rnp.png"
    fig.savefig(arquivo, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  -> {arquivo.name}")

    # Top sites de cada rede (para o relatório)
    print("\nTop 10 sites por volume:")
    print(por_site.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
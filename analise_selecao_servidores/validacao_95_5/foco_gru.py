"""
FOCO SP — comparação justa gru02 (mlab-oti) × gru1916 (rnp) × gru15830 (equinix)

DESENHO EXPERIMENTAL (o pedido do chefe):
  gru02, gru03, gru06, gru07, gru15830 e gru1916 são CO-LOCALIZADOS (mesma
  coordenada registrada). Logo, todo cliente elegível a um é elegível a todos:
  o pool é idêntico e a única diferença entre eles é o Probability no cadastro.

  Para cada site do grupo:
    1. ELEGÍVEIS  = testes cujo servidor mais próximo é o grupo (o pool)
    2. CAPTURADOS = testes que de fato foram para aquele site
    3. fatia_i    = capturados_i / elegíveis_do_grupo
    4. P_rel_i    = fatia_i / fatia_âncora   (âncora = gru02, assume P=1)

  Hipótese testada: dentro de um grupo co-localizado, fatia_i ∝ P_i.
  Se valer, P_rel é a estimativa do Probability relativo — e o perfil de
  clientes de cada site deve ser ESTATISTICAMENTE IGUAL (mesmo pool, sorteio
  aleatório). Divergência de perfil = outro fator além do Probability.

GROUND TRUTH (opcional): se houver um registration.json baixado do siteinfo
  na pasta do script, extrai o Probability oficial das máquinas gru* e compara
  com a estimativa. Baixe com:
    curl -o registration.json https://siteinfo.mlab-oti.measurement-lab.net/v2/sites/registration.json

Uso:
    python foco_gru.py                  # análise completa
    python foco_gru.py registration.json  # idem + ground truth do cadastro

Saídas (em out_foco/):
    fatias_grupo.csv, fatias_por_mes.csv, p_abs_por_mes.csv, perfis_por_site.csv,
    comparacao_perfis.csv, cidades_pool.csv, escape_por_site.csv,
    faixas_distancia.csv, cidades_gru02_vs_gru1916.csv, RELATORIO_FOCO.md,
    fatias_grupo.png, perfis_comparados.png, localizacao_clientes.png,
    comparacao_gru02_gru1916.png
"""

import itertools
import json
import math
import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
OUT_DIR = Path(__file__).parent / "out_foco"

ANCORA = "gru02"        # site de referência (mlab-oti, assume P=1)
MIN_TESTES_SITE = 1000  # mesmo filtro do analyze.py
EARTH_RADIUS_KM = 6371.0

CORES_DONO = {"mlab-oti": "#1f77b4", "rnp": "#d62728", "equinix": "#7f7f7f", "outros": "#bbbbbb"}
ASN_ORGS = {
    1916: "rnp", 2716: "rnp", 10881: "rnp", 53164: "rnp", 53078: "rnp",
    15830: "equinix", 11242: "rnp",
}

RELATORIO_LINHAS: list[str] = []


def rel(titulo: str = "", texto: str = "", tabela: pd.DataFrame | None = None,
        max_linhas: int = 25) -> None:
    if titulo:
        linha = f"\n## {titulo}\n"
        print(linha.strip())
        RELATORIO_LINHAS.append(linha)
    if texto:
        print(texto)
        RELATORIO_LINHAS.append(texto + "\n")
    if tabela is not None and len(tabela) > 0:
        print(tabela.to_string(index=False))
        RELATORIO_LINHAS.append(tabela.to_markdown(index=False) + "\n")


def derivar_dono(site: str, site_asn=None) -> str:
    s = str(site).strip()
    m = re.search(r"([a-z]{3})(\d+)$", s)
    if m and int(m.group(2)) in ASN_ORGS:
        return ASN_ORGS[int(m.group(2))]
    if s.startswith("mlab") or re.match(r"^[a-z]{3}\d{2}$", s):
        return "mlab-oti"
    try:
        if int(str(site_asn).replace("AS", "")) in ASN_ORGS:
            return ASN_ORGS[int(str(site_asn).replace("AS", ""))]
    except (ValueError, TypeError):
        pass
    return "outros"


def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))


def carregar() -> tuple[pd.DataFrame, pd.DataFrame]:
    sites = pd.read_csv(DATA_DIR / "sites.csv")
    sites["owner"] = [
        derivar_dono(s, a) for s, a in zip(sites["server_site"], sites.get("site_asn", pd.Series(dtype=str)))
    ]

    partes = []
    for f in sorted(DATA_DIR.glob("tests_*.csv")):
        df = pd.read_csv(f, low_memory=False)
        df["mes"] = f.stem.replace("tests_", "")
        partes.append(df)
    tests = pd.concat(partes, ignore_index=True)
    tests = tests.rename(columns={
        "client_city": "city", "client_latitude": "latitude",
        "client_longitude": "longitude", "client_asname": "as_name",
    })
    tests = tests.dropna(subset=["latitude", "longitude"])

    # Mesmo filtro de volume do analyze.py (consistência entre análises)
    vol = tests["server_site"].value_counts()
    ativos = set(vol[vol >= MIN_TESTES_SITE].index.astype(str))
    sites = sites[sites["server_site"].astype(str).isin(ativos)].reset_index(drop=True)
    return sites, tests


def ground_truth_registration(arquivo: Path) -> dict[str, float]:
    """Extrai o Probability oficial das máquinas de sites gru* do registration.json.

    Estrutura (defensiva): {"sites": [{"name": ..., "machines": [{"name": ..., "probability": ...}]}]}
    Para sites autojoin, o campo pode não existir — aí registra ausência.
    """
    dados = json.loads(arquivo.read_text(encoding="utf-8"))
    resultado: dict[str, float] = {}
    for site in dados.get("sites", []):
        nome = site.get("name", "")
        if not nome.startswith("gru"):
            continue
        for maq in site.get("machines", []):
            p = maq.get("probability")
            if p is not None:
                resultado[maq.get("name", "?")] = float(p)
            else:
                resultado[maq.get("name", "?")] = float("nan")
    return resultado


def ajustar_probabilidades(fatias: pd.Series) -> pd.Series:
    """Estima os P absolutos a partir das fatias observadas dentro do grupo.

    MODELO DO LOCATE (confirmado no código m-lab/locate, heartbeat/location.go):

      1. MOEDA (filterSites -> pickWithProbability): cada site participa da
         requisição se rand() < P_i. Quem perde a moeda nem entra na lista
         de candidatos daquela requisição.
      2. EMPATE (sortSites + pickTargets): sites co-localizados empatam na
         distância; a ordem entre eles é aleatória (iteração de map em Go) e
         o sorteio exponencial 95/5 escolhe a posição 0 — uniforme entre os
         sobreviventes do empate.

    Logo, para o grupo co-localizado:

        fatia_i = P_i * c_i,   com  c_i = E[1/k | i sobreviveu à moeda]

    onde k = número de sobreviventes da moeda. c_i soma EXATAMENTE sobre os
    subconjuntos T dos outros sites (n=6 -> 32 subconjuntos por site):

        c_i = Σ_T [ 1/(1+|T|) * Π_{j∈T} P_j * Π_{j∉T, j≠i} (1-P_j) ]

    Propriedade-chave: c_i NÃO depende de P_i (T percorre os outros sites
    apenas). Por isso a escala absoluta é identificável neste modelo —
    diferente do modelo de fila sequencial (antigo, errado), onde só razões
    eram observáveis e o solver colapsava.

    Resolve por ponto fixo: dado P, prevê fatias P_i*c_i e corrige
    P_i <- P_i * f_obs_i / prev_i, até convergir.

    Ressalva: as fatias observadas são condicionadas ao pool "mais próximo
    é o grupo". O tráfego de escape (seção 2b — 43,6% do capturado!) entra
    como volume extra também proporcional a P_i, o que infla os P absolutos
    de forma aproximadamente uniforme. As RAZÕES entre os P estimados
    permanecem comparáveis ao P_rel da seção 3.
    """
    sites = list(fatias.index)
    f_obs = fatias.to_numpy()
    f_obs = f_obs / f_obs.sum()  # modelo prevê fatias somando 1
    n = len(sites)

    def c_de(i: int, p: np.ndarray) -> float:
        """E[1/(1+|T|)] com T ⊆ outros sites, Bernoulli independente P_j."""
        outros = [j for j in range(n) if j != i]
        m = len(outros)
        total = 0.0
        for mask in range(1 << m):
            prob, tamanho = 1.0, 0
            for bit, j in enumerate(outros):
                if mask & (1 << bit):
                    prob *= p[j]
                    tamanho += 1
                else:
                    prob *= 1.0 - p[j]
            total += prob / (1 + tamanho)
        return total

    def fatias_previstas(p: np.ndarray) -> np.ndarray:
        return np.array([p[i] * c_de(i, p) for i in range(n)])

    # Ponto fixo — inicialização: fatias normalizadas pela maior
    p = (f_obs / f_obs.max()).copy()
    convergiu = False
    for _ in range(2000):
        prev = fatias_previstas(p)
        razao = f_obs / np.maximum(prev, 1e-12)
        p = np.clip(p * razao, 1e-6, 1.0)
        if np.max(np.abs(fatias_previstas(p) - f_obs)) < 1e-6:
            convergiu = True
            break

    if not convergiu:
        print("  AVISO: ponto fixo não convergiu em 500 iterações "
              "(pode indicar P real > 1 para algum site — modelo com tensão)")
    no_teto = [sites[i] for i in range(n) if p[i] >= 1.0 - 1e-9]
    if no_teto:
        print(f"  Sites no teto P=1.0: {', '.join(no_teto)}")

    # Normaliza pela âncora declarada (gru02), se presente no grupo
    if ANCORA in sites:
        p = p / p[sites.index(ANCORA)]
    return pd.Series(p, index=sites, name="P_abs_estimado")


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    sites, tests = carregar()
    print(f"{len(sites)} sites, {len(tests):,} testes")

    # ------------------------------------------------------------------
    # 1. Identifica o grupo co-localizado da âncora
    # ------------------------------------------------------------------
    sites["loc_key"] = (
        sites["latitude"].round(6).astype(str) + "|" + sites["longitude"].round(6).astype(str)
    )
    loc_ancora = sites.loc[sites["server_site"] == ANCORA, "loc_key"].iloc[0]
    grupo = sites[sites["loc_key"] == loc_ancora].copy()
    nomes_grupo = sorted(grupo["server_site"])
    print(f"Grupo co-localizado de {ANCORA}: {', '.join(nomes_grupo)}")
    rel("Grupo co-localizado (pool idêntico)",
        f"Sites na mesma coordenada registrada de **{ANCORA}**: "
        f"{', '.join(nomes_grupo)}. Todo cliente elegível a um é elegível a "
        "todos — a única diferença entre eles é o Probability do cadastro.",
        grupo[["server_site", "owner", "site_city", "server_type", "site_asn"]])

    # ------------------------------------------------------------------
    # 2. Elegíveis: testes cujo site mais próximo é o grupo
    # ------------------------------------------------------------------
    locs = sites.groupby("loc_key").agg(
        latitude=("latitude", "first"), longitude=("longitude", "first")
    ).reset_index()
    coords = tests[["latitude", "longitude"]].drop_duplicates().reset_index(drop=True)
    print(f"  {len(coords):,} coordenadas x {len(locs)} localizações...")

    loc_lats, loc_lons = locs["latitude"].to_numpy(), locs["longitude"].to_numpy()
    argmin = np.empty(len(coords), dtype=np.int32)
    for i, (lat, lon) in enumerate(zip(coords["latitude"], coords["longitude"])):
        argmin[i] = int(np.argmin(haversine(lat, lon, loc_lats, loc_lons)))

    coord_idx = {(a, b): i for i, (a, b) in
                 enumerate(zip(coords["latitude"], coords["longitude"]))}
    tests["loc_mais_proxima"] = [
        argmin[coord_idx[(a, b)]] for a, b in zip(tests["latitude"], tests["longitude"])
    ]

    idx_grupo = locs.index[locs["loc_key"] == loc_ancora][0]
    eleg = tests[tests["loc_mais_proxima"] == idx_grupo].copy()
    # Propaga o dono do site para os testes (usado nos perfis)
    site_owner = dict(zip(sites["server_site"].astype(str), sites["owner"]))
    eleg["owner"] = eleg["server_site"].astype(str).map(site_owner).fillna("outros")
    print(f"  Elegíveis do grupo: {len(eleg):,} testes")
    rel("Pool elegível do grupo",
        f"Testes cujo servidor mais próximo é o grupo SP: **{len(eleg):,}**. "
        "Este é o denominador comum a todos os sites do grupo.",
        eleg.groupby("mes").size().rename("elegiveis").reset_index())

    # ------------------------------------------------------------------
    # 2b. ESCAPE: testes que foram para sites do grupo mas cujo site mais
    #     próximo NÃO é o grupo (a fatia ~5% do pickTargets que escapa da
    #     fila por distância). O pool "mais próximo" é uma aproximação do
    #     denominador real — aqui medimos o quanto ela deixa de fora.
    # ------------------------------------------------------------------
    sites_grupo = set(nomes_grupo)
    esc = tests[tests["server_site"].isin(sites_grupo) & (tests["loc_mais_proxima"] != idx_grupo)].copy()
    esc_por_site = esc["server_site"].value_counts().reindex(nomes_grupo).fillna(0).astype(int)
    # capturados dentro do pool (fatia definida na seção 3; aqui calculamos direto)
    capt_pool = eleg["server_site"].value_counts().reindex(nomes_grupo).fillna(0).astype(int)
    esc_df = pd.DataFrame({
        "capturados_no_pool": capt_pool,
        "capturados_escape": esc_por_site,
    })
    esc_df["pct_escape"] = (esc_df["capturados_escape"] /
                            (esc_df["capturados_no_pool"] + esc_df["capturados_escape"]) * 100).round(2)
    esc_df.to_csv(OUT_DIR / "escape_por_site.csv", index_label="server_site")
    rel("Escape — testes de fora do pool que foram para o grupo",
        f"O Locate oferece os 6 alvos mais próximos e a fatia de escape "
        f"(~5%) pode mandar o teste para um site distante. Estes testes "
        f"foram para sites do grupo mas o mais próximo do cliente era outro "
        f"pool: **{len(esc):,}** ({len(esc) / (len(esc) + len(eleg)) * 100:.2f}% "
        "do total capturado pelo grupo). O denominador 'mais próximo' é uma "
        "aproximação — a fatia real de cada site é um pouco maior do que a "
        "calculada só com o pool.",
        esc_df.reset_index())

    # ------------------------------------------------------------------
    # 3. Fatias e P relativo (hipótese: fatia_i ∝ P_i dentro do grupo)
    # ------------------------------------------------------------------
    fatia = eleg["server_site"].value_counts().reindex(nomes_grupo).fillna(0)
    share = fatia / fatia.sum()
    p_rel = share / share[ANCORA]  # âncora: P=1 assumido

    res = pd.DataFrame({
        "owner": grupo.set_index("server_site")["owner"].reindex(nomes_grupo),
        "capturados": fatia.astype(int),
        "fatia_obs": share,
        "fatia_uniforme": 1 / len(nomes_grupo),
        "P_rel_ancora": p_rel,
    })
    res.to_csv(OUT_DIR / "fatias_grupo.csv", index_label="server_site")
    rel("Fatias observadas e Probability relativo",
        f"fatia_i = capturados_i / elegíveis. Se a seleção dentro do grupo é "
        f"proporcional ao Probability, então P_rel_i = fatia_i / fatia_{ANCORA} "
        "estima o Probability relativo (âncora com P=1).",
        res.reset_index())

    # ------------------------------------------------------------------
    # 3b. P ABSOLUTO via modelo do Locate (moeda + posição uniforme)
    #     Roda POR MÊS: a composição do grupo muda com o tempo (sites entram
    #     e saem do ar), e fatias agregadas de períodos diferentes não são
    #     explicáveis por um único conjunto de P estático.
    # ------------------------------------------------------------------
    linhas_p = []
    for mes in sorted(eleg["mes"].unique()):
        g = eleg[eleg["mes"] == mes]
        f_m = g["server_site"].value_counts().reindex(nomes_grupo).fillna(0)
        ativos = f_m[f_m >= MIN_TESTES_SITE]  # sites ativos no mês
        if len(ativos) < 2:
            continue
        p_m = ajustar_probabilidades(ativos)
        for site, v in p_m.items():
            linhas_p.append({
                "mes": mes, "server_site": site, "P_abs": round(float(v), 4),
                "testes": int(f_m[site]), "n_sites_ativos": len(ativos),
            })
    p_mes_df = pd.DataFrame(linhas_p)
    p_mes_df.to_csv(OUT_DIR / "p_abs_por_mes.csv", index=False)

    piv = p_mes_df.pivot(index="server_site", columns="mes", values="P_abs")
    n_ativos = p_mes_df.groupby("mes")["n_sites_ativos"].first()
    janela_limpa = n_ativos[n_ativos == len(nomes_grupo)].index.tolist()
    texto_janela = (
        f"Meses com o grupo completo ({len(nomes_grupo)} sites no ar): "
        f"{', '.join(janela_limpa) if janela_limpa else 'nenhum'}. "
        "Nesses meses o modelo é aplicável sem ressalvas; nos demais, a "
        "composição parcial distorce a estimativa (sites ausentes mudam o "
        "denominador da moeda)."
    )
    rel("Probability ABSOLUTO estimado POR MÊS (modelo: moeda + empate uniforme)",
        "Mecanismo real (confirmado no código m-lab/locate): (1) MOEDA — cada "
        "site participa da requisição se rand() < P_i (pickWithProbability em "
        "filterSites); (2) EMPATE — co-localizados empatam na distância e a "
        "posição 0 do sorteio 95/5 é uniforme entre os sobreviventes. Logo "
        "fatia_i = P_i * c_i com c_i = E[1/k | i sobreviveu], calculado "
        "exatamente sobre os subconjuntos dos outros sites. Como c_i não "
        "depende de P_i, a escala absoluta é identificável (âncora gru02=1). "
        "O modelo roda por mês porque a composição do grupo muda (sites "
        "entram/saem do ar). " + texto_janela,
        piv.reset_index(), max_linhas=10)

    # Estabilidade mês a mês (assinatura de cadastro)
    fatia_mes = eleg.pivot_table(index="server_site", columns="mes",
                                 values="test_time", aggfunc="size").reindex(nomes_grupo)
    share_mes = fatia_mes.div(fatia_mes.sum(axis=0), axis=1)
    share_mes.to_csv(OUT_DIR / "fatias_por_mes.csv")
    rel("Fatia por site e mês",
        "Estabilidade mês a mês = assinatura de campo estático de cadastro.",
        share_mes.reset_index(), max_linhas=10)

    # ------------------------------------------------------------------
    # 4. Perfil de clientes por site (o pedido literal do chefe)
    #    Hipótese nula: perfis idênticos (mesmo pool, sorteio aleatório)
    # ------------------------------------------------------------------
    print("\nPerfis de clientes por site...")
    perfis = []
    for site in nomes_grupo:
        g = eleg[eleg["server_site"] == site]
        if len(g) == 0:
            continue
        dist_km = haversine(
            g["latitude"].to_numpy(), g["longitude"].to_numpy(),
            float(grupo.loc[grupo["server_site"] == site, "latitude"].iloc[0]),
            float(grupo.loc[grupo["server_site"] == site, "longitude"].iloc[0]),
        )
        g = g.assign(dist_km=dist_km)
        top_cidades = g["city"].value_counts().head(5)
        perfis.append({
            "server_site": site,
            "owner": g["owner"].iloc[0],
            "testes": len(g),
            "n_cidades": g["city"].nunique(),
            "cidade_1": top_cidades.index[0] if len(top_cidades) else "",
            "cidade_1_pct": top_cidades.iloc[0] / len(g) * 100 if len(top_cidades) else np.nan,
            "dist_mediana_km": float(np.median(dist_km)),
            "p90_dist_km": float(np.percentile(dist_km, 90)),
            "pct_local_100km": (dist_km <= 100).mean() * 100,
        })
    perfil_df = pd.DataFrame(perfis)
    perfil_df.to_csv(OUT_DIR / "perfis_por_site.csv", index=False)
    rel("Perfil de clientes por site (dentro do pool)",
        "Se o mecanismo é só Probability, os perfis devem ser iguais "
        "(mesmo pool, sorteio aleatório). Divergência = outro fator em jogo.",
        perfil_df)

    # Comparação direta gru02 × gru1916: distribuição de cidades
    # (TVD = distância total de variação; 0 = idênticas, 1 = disjuntas)
    comp = []
    g_anc = eleg[eleg["server_site"] == ANCORA]["city"].value_counts(normalize=True)
    for site in nomes_grupo:
        if site == ANCORA:
            continue
        g_outro = eleg[eleg["server_site"] == site]["city"].value_counts(normalize=True)
        cats = g_anc.index.union(g_outro.index)
        p = g_anc.reindex(cats).fillna(0)
        q = g_outro.reindex(cats).fillna(0)
        tvd = 0.5 * np.abs(p - q).sum()
        # chi2 manual (sem scipy): soma (obs-exp)²/exp sobre cidades do pool
        n_outro = eleg["server_site"].value_counts()[site]
        exp = p * n_outro
        obs = q * n_outro
        mask = exp > 5
        chi2 = float(((obs[mask] - exp[mask]) ** 2 / exp[mask]).sum())
        comp.append({
            "par": f"{ANCORA} × {site}",
            "tvd_cidades": round(tvd, 4),
            "chi2_top_cidades": round(chi2, 1),
            "n_cidades_comparadas": int(mask.sum()),
        })
    comp_df = pd.DataFrame(comp)
    comp_df.to_csv(OUT_DIR / "comparacao_perfis.csv", index=False)
    rel("Teste de igualdade de perfis (gru02 × demais)",
        "TVD próximo de 0 = perfis de clientes idênticos (esperado se só o "
        "Probability difere). chi2 será grande por serem milhões de amostras — "
        "o tamanho do efeito (TVD) é o que importa.",
        comp_df)

    # ------------------------------------------------------------------
    # 5. Ground truth do registration.json (se existir)
    # ------------------------------------------------------------------
    reg_args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if reg_args and Path(reg_args[0]).exists():
        gt = ground_truth_registration(Path(reg_args[0]))
        if gt:
            gt_df = pd.DataFrame(
                [(k, v) for k, v in sorted(gt.items())],
                columns=["maquina", "probability_oficial"],
            )
            gt_df.to_csv(OUT_DIR / "ground_truth_registration.csv", index=False)
            rel("Ground truth — registration.json (siteinfo)",
                "Probability oficial publicado por máquina dos sites gru*. "
                "Compare com P_rel acima: bater = prova fechada; ausência em "
                "sites autojoin = a estimativa pelos dados é a única disponível.",
                gt_df, max_linhas=30)
        else:
            rel("Ground truth — registration.json",
                "Arquivo lido, mas nenhuma máquina gru* com campo probability. "
                "Confirma que sites autojoin não publicam o valor final — "
                "a inferência pelos dados é necessária.")

    # ------------------------------------------------------------------
    # 6. Gráficos
    # ------------------------------------------------------------------
    # (i) fatias observadas vs uniforme, com P_rel anotado
    fig, ax = plt.subplots(figsize=(10, 6))
    cores = [CORES_DONO.get(o, "#bbb") for o in res["owner"]]
    bars = ax.bar(res.index, res["fatia_obs"] * 100, color=cores)
    ax.axhline(100 / len(nomes_grupo), color="black", linestyle="--", linewidth=1,
               label=f"uniforme ({100 / len(nomes_grupo):.1f}%)")
    for b, pr in zip(bars, res["P_rel_ancora"]):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.5,
                f"P≈{pr:.2f}", ha="center", fontsize=10)
    ax.set_title(f"Fatia do pool SP por site (elegíveis = {len(eleg):,})\n"
                 "P relativo estimado pela hipótese fatia ∝ Probability",
                 fontsize=12, fontweight="bold")
    ax.set_ylabel("% do pool capturado")
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(facecolor=CORES_DONO["mlab-oti"], label="M-Lab (OTI)"),
                       Patch(facecolor=CORES_DONO["rnp"], label="RNP"),
                       Patch(facecolor=CORES_DONO["equinix"], label="Equinix")]
              + [plt.Line2D([0], [0], color="black", linestyle="--", label="uniforme")],
              fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fatias_grupo.png", dpi=150)
    plt.close(fig)
    print(f"  -> {OUT_DIR / 'fatias_grupo.png'}")

    # (ii) perfis comparados: gru02 vs gru1916 (e gru15830)
    alvos_perfis = [ANCORA] + [s for s in ("gru1916", "gru15830") if s in nomes_grupo]
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # cidades: top 8 do pool, % por site
    ax = axes[0]
    top_cids = eleg["city"].value_counts().head(8).index
    largura = 0.8 / len(alvos_perfis)
    for k, site in enumerate(alvos_perfis):
        g = eleg[eleg["server_site"] == site]["city"].value_counts(normalize=True)
        vals = (g.reindex(top_cids).fillna(0) * 100).values
        ax.bar(np.arange(len(top_cids)) + k * largura, vals, largura,
               label=f"{site} ({CORES_DONO.get(dict(zip(grupo['server_site'], grupo['owner']))[site], '#bbb')})",
               color=CORES_DONO.get(dict(zip(grupo['server_site'], grupo['owner']))[site], "#bbb"))
    ax.set_xticks(np.arange(len(top_cids)) + largura, top_cids, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("% dos testes do site")
    ax.set_title("Origem dos clientes (top 8 cidades do pool)", fontsize=11)
    ax.legend(fontsize=9)

    # distância: faixas de distância por site (barras, mais legível que decis)
    ax = axes[1]
    FAIXAS_P = [(0, 50), (50, 100), (100, 200), (200, 500), (500, 3000)]
    rotulos_p = ["0–50", "50–100", "100–200", "200–500", "500+"]
    larg_p = 0.8 / len(alvos_perfis)
    for k, site in enumerate(alvos_perfis):
        g = eleg[eleg["server_site"] == site]
        d = haversine(g["latitude"].to_numpy(), g["longitude"].to_numpy(),
                      float(grupo.loc[grupo["server_site"] == site, "latitude"].iloc[0]),
                      float(grupo.loc[grupo["server_site"] == site, "longitude"].iloc[0]))
        vals = [((d >= a) & (d < b)).mean() * 100 for a, b in FAIXAS_P]
        pos = np.arange(len(FAIXAS_P)) + k * larg_p
        ax.bar(pos, vals, larg_p, label=site,
               color=CORES_DONO.get(dict(zip(grupo['server_site'], grupo['owner']))[site], "#bbb"))
    ax.set_xticks(np.arange(len(FAIXAS_P)) + larg_p * (len(alvos_perfis) - 1) / 2, rotulos_p)
    ax.set_xlabel("distância cliente→site (km)")
    ax.set_ylabel("% dos testes do site")
    ax.set_title("Perfil de distância por site (faixas)", fontsize=11)
    ax.legend(fontsize=9)

    fig.suptitle("Perfis de clientes condicionados ao mesmo pool — devem ser IGUAIS se só o Probability difere",
                 fontsize=12, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(OUT_DIR / "perfis_comparados.png", dpi=150)
    plt.close(fig)
    print(f"  -> {OUT_DIR / 'perfis_comparados.png'}")

    # ------------------------------------------------------------------
    # 5b. LOCALIZAÇÃO dos clientes do pool — BARRAS (sem mapa)
    #     (a) top 10 cidades do pool
    #     (b) distribuição por faixa de distância ao grupo
    # ------------------------------------------------------------------
    print("\nLocalização dos clientes do pool...")

    # distância de cada teste do pool ao grupo (co-localizados: 1 valor serve)
    dist_grupo = haversine(
        eleg["latitude"].to_numpy(), eleg["longitude"].to_numpy(),
        float(grupo["latitude"].iloc[0]), float(grupo["longitude"].iloc[0]),
    )
    eleg = eleg.assign(dist_grupo_km=dist_grupo)

    # Tabela: cidades do pool com coordenadas e volume por site
    cidades = (
        eleg.groupby(["city", "latitude", "longitude"])
        .agg(
            testes=("server_site", "size"),
            gru02=("server_site", lambda s: (s == "gru02").sum()),
            gru1916=("server_site", lambda s: (s == "gru1916").sum()),
            gru15830=("server_site", lambda s: (s == "gru15830").sum()),
        )
        .reset_index()
        .sort_values("testes", ascending=False)
    )
    cidades.to_csv(OUT_DIR / "cidades_pool.csv", index=False)
    rel("Localização dos clientes do pool (top 20 cidades)",
        "Coordenadas GeoIP das cidades que medem para o grupo SP, com o "
        "volume que cada site de referência recebeu delas.",
        cidades.head(20), max_linhas=20)

    # Faixas de distância (barras)
    FAIXAS = [(0, 50), (50, 100), (100, 200), (200, 500), (500, 3000)]
    rotulos = ["0–50", "50–100", "100–200", "200–500", "500+"]
    faixa_pct = pd.Series(
        [((eleg["dist_grupo_km"] >= a) & (eleg["dist_grupo_km"] < b)).mean() * 100
         for a, b in FAIXAS],
        index=rotulos, name="pct_testes",
    )
    faixa_pct.to_csv(OUT_DIR / "faixas_distancia.csv")
    rel("Distribuição de distância cliente→grupo SP",
        "Percentual de testes do pool por faixa de distância (km).",
        faixa_pct.rename_axis("faixa_km").reset_index())

    # Gráfico: (a) top 10 cidades | (b) faixas de distância
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    ax = axes[0]
    top10 = cidades.head(10).iloc[::-1]
    ax.barh(top10["city"], top10["testes"], color="#1f77b4")
    for y, v in enumerate(top10["testes"]):
        ax.text(v, y, f" {v:,}", va="center", fontsize=9)
    ax.set_xlabel("testes")
    ax.set_title(f"Top 10 cidades do pool SP ({len(eleg):,} testes)", fontsize=11)
    ax.tick_params(axis="y", labelsize=9)

    ax = axes[1]
    bars = ax.bar(rotulos, faixa_pct.values, color="#1f77b4")
    for b, v in zip(bars, faixa_pct.values):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.5,
                f"{v:.1f}%", ha="center", fontsize=10)
    ax.set_xlabel("distância ao grupo SP (km)")
    ax.set_ylabel("% dos testes do pool")
    ax.set_title("De onde vêm os clientes (faixa de distância)", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "localizacao_clientes.png", dpi=150)
    plt.close(fig)
    print(f"  -> {OUT_DIR / 'localizacao_clientes.png'}")

    # ------------------------------------------------------------------
    # 5c. COMPARAÇÃO gru02 × gru1916 — BARRAS (sem mapa)
    #     (a) top 10 cidades, % de cada site lado a lado
    #     (b) faixas de distância, % de cada site lado a lado
    #     Se só o Probability difere, as barras devem ser iguais.
    # ------------------------------------------------------------------
    print("\nComparação gru02 × gru1916 (barras)...")
    alvos_mapa = [s for s in (ANCORA, "gru1916") if s in nomes_grupo]
    if len(alvos_mapa) == 2:
        s1, s2 = alvos_mapa
        g1 = eleg[eleg["server_site"] == s1]
        g2 = eleg[eleg["server_site"] == s2]

        # (a) top 10 cidades do pool, % por site
        top_cids = eleg["city"].value_counts().head(10).index
        p1 = g1["city"].value_counts(normalize=True).reindex(top_cids).fillna(0) * 100
        p2 = g2["city"].value_counts(normalize=True).reindex(top_cids).fillna(0) * 100
        x = np.arange(len(top_cids))
        larg = 0.38
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        ax = axes[0]
        ax.bar(x - larg / 2, p1.values, larg, label=s1, color=CORES_DONO["mlab-oti"])
        ax.bar(x + larg / 2, p2.values, larg, label=s2, color=CORES_DONO["rnp"])
        ax.set_xticks(x, top_cids, rotation=30, ha="right", fontsize=9)
        ax.set_ylabel("% dos testes do site")
        ax.set_title("Origem dos clientes (top 10 cidades do pool)", fontsize=11)
        ax.legend(fontsize=9)

        # (b) faixas de distância, % por site
        f1 = pd.Series([((g1["dist_grupo_km"] >= a) & (g1["dist_grupo_km"] < b)).mean() * 100
                        for a, b in FAIXAS], index=rotulos)
        f2 = pd.Series([((g2["dist_grupo_km"] >= a) & (g2["dist_grupo_km"] < b)).mean() * 100
                        for a, b in FAIXAS], index=rotulos)
        ax = axes[1]
        x = np.arange(len(FAIXAS))
        ax.bar(x - larg / 2, f1.values, larg, label=s1, color=CORES_DONO["mlab-oti"])
        ax.bar(x + larg / 2, f2.values, larg, label=s2, color=CORES_DONO["rnp"])
        for xi, (v1, v2) in enumerate(zip(f1.values, f2.values)):
            ax.text(xi - larg / 2, v1 + 0.4, f"{v1:.1f}", ha="center", fontsize=8)
            ax.text(xi + larg / 2, v2 + 0.4, f"{v2:.1f}", ha="center", fontsize=8)
        ax.set_xticks(x, rotulos)
        ax.set_xlabel("distância ao grupo SP (km)")
        ax.set_ylabel("% dos testes do site")
        ax.set_title("Perfil de distância por site", fontsize=11)
        ax.legend(fontsize=9)

        fig.suptitle(f"{s1} × {s2} — barras iguais = perfis idênticos (só o Probability difere)",
                     fontsize=12, fontweight="bold")
        fig.tight_layout(rect=(0, 0, 1, 0.94))
        fig.savefig(OUT_DIR / "comparacao_gru02_gru1916.png", dpi=150)
        plt.close(fig)
        print(f"  -> {OUT_DIR / 'comparacao_gru02_gru1916.png'}")

        # Tabela: top 10 cidades de cada site, lado a lado, com % e diferença
        c1 = g1["city"].value_counts(normalize=True).head(10)
        c2 = g2["city"].value_counts(normalize=True).head(10)
        cats = c1.index.union(c2.index)
        tab = pd.DataFrame({
            f"{s1}_%": (c1.reindex(cats).fillna(0) * 100).round(2),
            f"{s2}_%": (c2.reindex(cats).fillna(0) * 100).round(2),
        })
        tab["dif_pp"] = (tab[f"{s1}_%"] - tab[f"{s2}_%"]).round(2)
        tab = tab.sort_values(f"{s1}_%", ascending=False)
        tab.to_csv(OUT_DIR / "cidades_gru02_vs_gru1916.csv")
        rel("Top cidades — gru02 × gru1916 (lado a lado)",
            "Distribuição % das cidades de origem de cada site. dif_pp = "
            "diferença em pontos percentuais. Valores grandes = perfis "
            "geográficos diferentes (não é só o Probability agindo).",
            tab.reset_index(), max_linhas=12)


if __name__ == "__main__":
    main()
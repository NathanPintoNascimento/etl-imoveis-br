"""
Pipeline principal — gera CSV + relatório HTML com os resultados reais.
"""

import logging
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

BASE = Path(__file__).parent.parent

CIDADES = {
    "Sao Paulo":      {"media": 3800, "desvio": 1800, "peso": 30},
    "Rio de Janeiro": {"media": 3200, "desvio": 1500, "peso": 20},
    "Belo Horizonte": {"media": 2100, "desvio":  900, "peso": 12},
    "Curitiba":       {"media": 2300, "desvio": 1000, "peso": 10},
    "Porto Alegre":   {"media": 2000, "desvio":  850, "peso":  8},
    "Salvador":       {"media": 1800, "desvio":  750, "peso":  7},
    "Fortaleza":      {"media": 1600, "desvio":  700, "peso":  7},
    "Recife":         {"media": 1700, "desvio":  720, "peso":  6},
}

def gerar_dados_sinteticos(n=10000, seed=42):
    np.random.seed(seed)
    logger.info(f"Gerando {n:,} registros sinteticos...")
    nomes   = list(CIDADES.keys())
    pesos   = [CIDADES[c]["peso"] for c in nomes]
    pesos_n = [p / sum(pesos) for p in pesos]
    cidades = np.random.choice(nomes, size=n, p=pesos_n)
    alugueis, areas = [], []
    for cidade in cidades:
        cfg  = CIDADES[cidade]
        alug = max(400, np.random.normal(cfg["media"], cfg["desvio"]))
        area = max(18,  np.random.normal(alug / 35, 20))
        alugueis.append(round(alug, 2))
        areas.append(round(area, 1))
    alugueis = np.array(alugueis)
    areas    = np.array(areas)
    quartos   = np.random.choice([1,2,3,4,5], size=n, p=[0.15,0.30,0.35,0.15,0.05])
    banheiros = np.clip(quartos + np.random.randint(-1, 2, n), 1, 6)
    vagas     = np.random.choice([0,1,2,3], size=n, p=[0.20,0.45,0.28,0.07])
    andares   = np.random.choice(range(0, 31), size=n, p=[0.10]+[0.03]*30)
    animais   = np.random.choice(["acept","not acept"], size=n, p=[0.45,0.55])
    mobilia   = np.random.choice(["furnished","not furnished"], size=n, p=[0.35,0.65])
    bonus     = np.where(mobilia == "furnished", np.random.uniform(1.05, 1.25, n), 1.0)
    alugueis  = (alugueis * bonus).round(2)
    condominio = (alugueis * np.random.uniform(0.08, 0.20, n)).round(2)
    iptu       = (alugueis * np.random.uniform(0.01, 0.05, n)).round(2)
    seguro     = (alugueis * np.random.uniform(0.005, 0.015, n)).round(2)
    total      = (alugueis + condominio + iptu + seguro).round(2)
    idx_out = np.random.choice(n, size=int(n * 0.03), replace=False)
    alugueis[idx_out] *= np.random.uniform(5, 15, len(idx_out))
    alugueis_s = pd.Series(alugueis, dtype=float)
    idx_nulos  = np.random.choice(n, size=int(n * 0.01), replace=False)
    alugueis_s.iloc[idx_nulos] = np.nan
    df = pd.DataFrame({
        "city": cidades, "area": areas, "rooms": quartos,
        "bathroom": banheiros, "parking spaces": vagas, "floor": andares,
        "animal": animais, "furniture": mobilia,
        "hoa (R$)": condominio, "rent amount (R$)": alugueis_s,
        "property tax (R$)": iptu, "fire insurance (R$)": seguro, "total (R$)": total,
    })
    caminho = BASE / "data" / "houses_to_rent_v2.csv"
    caminho.parent.mkdir(exist_ok=True)
    df.to_csv(caminho, index=False)
    logger.info(f"CSV salvo | shape: {df.shape} | outliers: {len(idx_out)} | nulos: {len(idx_nulos)}")
    return df

def extrair():
    logger.info("--- ETAPA 1: EXTRACAO ---")
    caminho = BASE / "data" / "houses_to_rent_v2.csv"
    if caminho.exists():
        logger.info(f"CSV encontrado. Lendo: {caminho}")
        return pd.read_csv(caminho)
    return gerar_dados_sinteticos()

MAPA_COLUNAS = {
    "city": "cidade", "area": "area_m2", "rooms": "quartos",
    "bathroom": "banheiros", "parking spaces": "vagas_garagem",
    "floor": "andar", "animal": "aceita_animal", "furniture": "mobiliado",
    "hoa (R$)": "condominio_reais", "rent amount (R$)": "aluguel_reais",
    "property tax (R$)": "iptu_reais", "fire insurance (R$)": "seguro_incendio_reais",
    "total (R$)": "total_reais",
}

def _remover_outliers_iqr(df, col, fator=2.5):
    q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
    iqr = q3 - q1
    antes = len(df)
    df = df[df[col].between(q1 - fator * iqr, q3 + fator * iqr)]
    logger.info(f"  [{col}] outliers removidos: {antes - len(df)}")
    return df

def _normalizar(df, colunas):
    for col in colunas:
        mn, mx = df[col].min(), df[col].max()
        df[f"{col}_norm"] = ((df[col] - mn) / (mx - mn)).round(4) if mx > mn else 0.0
    return df

def transformar(df):
    logger.info("--- ETAPA 2: TRANSFORMACAO ---")
    df = df.rename(columns=MAPA_COLUNAS)
    df["aceita_animal"] = df["aceita_animal"].map({"acept": True, "not acept": False})
    df["mobiliado"]     = df["mobiliado"].map({"furnished": True, "not furnished": False})
    df["andar"] = pd.to_numeric(df["andar"].replace("-", 0), errors="coerce").fillna(0).astype(int)
    numericas = ["aluguel_reais","area_m2","quartos","banheiros",
                 "vagas_garagem","condominio_reais","iptu_reais",
                 "seguro_incendio_reais","total_reais"]
    for col in numericas:
        nulos = df[col].isnull().sum()
        if nulos > 0:
            med = df[col].median()
            df[col] = df[col].fillna(med)
            logger.info(f"  [{col}] {nulos} nulos preenchidos com mediana ({med:.2f})")
    for col in ["aluguel_reais", "area_m2", "total_reais"]:
        df = _remover_outliers_iqr(df, col)
    df = _normalizar(df, ["aluguel_reais", "area_m2", "total_reais", "quartos"])
    df["preco_por_m2"] = (df["aluguel_reais"] / df["area_m2"].replace(0, np.nan)).round(2)
    df["cidade"] = df["cidade"].str.strip().str.title()
    limites = df["aluguel_reais"].quantile([0.33, 0.66])
    df["faixa_preco"] = pd.cut(
        df["aluguel_reais"],
        bins=[-np.inf, limites[0.33], limites[0.66], np.inf],
        labels=["Economico", "Medio", "Premium"]
    )
    df = df.reset_index(drop=True)
    logger.info(f"Transformacao concluida. Shape final: {df.shape}")
    return df

def gerar_html(df):
    logger.info("--- ETAPA 3: RELATORIO HTML ---")

    agora        = datetime.now().strftime("%d/%m/%Y %H:%M")
    total        = len(df)
    cidades_n    = df["cidade"].nunique()
    alug_medio   = df["aluguel_reais"].mean()
    alug_mediano = df["aluguel_reais"].median()
    alug_min     = df["aluguel_reais"].min()
    alug_max     = df["aluguel_reais"].max()
    preco_m2     = df["preco_por_m2"].median()

    ranking = (df.groupby("cidade")["aluguel_reais"]
               .agg(media="mean", quantidade="count")
               .sort_values("media", ascending=False)
               .reset_index())

    mob_sim = df[df["mobiliado"] == True]["aluguel_reais"].mean()
    mob_nao = df[df["mobiliado"] == False]["aluguel_reais"].mean()
    var_mob = (mob_sim / mob_nao - 1) * 100 if mob_nao > 0 else 0

    por_quartos = (df.groupby("quartos")["aluguel_reais"]
                   .agg(media="mean", quantidade="count")
                   .reset_index())

    faixa = df["faixa_preco"].value_counts().sort_index()
    total_faixa = faixa.sum()

    max_media = ranking["media"].max()
    cores = ["#00d4aa","#00b8d9","#7c6bff","#ff6b9d","#ffa94d","#69db7c","#74c0fc","#f06595"]

    ranking_rows = ""
    for i, row in ranking.iterrows():
        pct = (row["media"] / max_media) * 100
        cor = cores[i % len(cores)]
        ranking_rows += f"""
        <tr>
          <td><span class="badge" style="background:{cor}22;color:{cor};border:1px solid {cor}44">{i+1}</span></td>
          <td><strong>{row['cidade']}</strong></td>
          <td>
            <div class="bar-wrap">
              <div class="bar" style="width:{pct:.1f}%;background:{cor}"></div>
              <span>R$ {row['media']:,.0f}</span>
            </div>
          </td>
          <td class="num">{int(row['quantidade']):,}</td>
        </tr>"""

    quartos_rows = ""
    max_q = por_quartos["media"].max()
    for _, row in por_quartos.iterrows():
        pct = (row["media"] / max_q) * 100
        quartos_rows += f"""
        <tr>
          <td class="num">{"bed " * int(row['quartos'])}</td>
          <td><strong>{int(row['quartos'])} quarto(s)</strong></td>
          <td>
            <div class="bar-wrap">
              <div class="bar" style="width:{pct:.1f}%;background:#7c6bff"></div>
              <span>R$ {row['media']:,.0f}</span>
            </div>
          </td>
          <td class="num">{int(row['quantidade']):,}</td>
        </tr>"""

    faixa_cards = ""
    faixa_config = {
        "Economico": {"icon": "&#9679;", "cor": "#69db7c", "label": "Economico"},
        "Medio":     {"icon": "&#9679;", "cor": "#ffd43b", "label": "Medio"},
        "Premium":   {"icon": "&#9679;", "cor": "#7c6bff", "label": "Premium"},
    }
    for nome, qtd in faixa.items():
        cfg = faixa_config.get(str(nome), {"icon": "&#9679;", "cor": "#aaa", "label": str(nome)})
        pct_fx = qtd / total_faixa * 100
        faixa_cards += f"""
        <div class="faixa-card" style="border-top:3px solid {cfg['cor']}">
          <div class="faixa-dot" style="color:{cfg['cor']}">{cfg['icon']}</div>
          <div class="faixa-label">{cfg['label']}</div>
          <div class="faixa-num" style="color:{cfg['cor']}">{qtd:,}</div>
          <div class="faixa-pct">{pct_fx:.1f}% do total</div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>ETL Imoveis BR - Relatorio</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
:root{{--bg:#0b0d14;--surface:#12151f;--surface2:#1a1e2e;--border:#ffffff0f;--text:#e8eaf0;--muted:#6b7280;--accent:#00d4aa;--accent2:#7c6bff;}}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:var(--bg);color:var(--text);font-family:'DM Sans',sans-serif;font-size:15px;line-height:1.6;}}
header{{padding:60px 40px 40px;border-bottom:1px solid var(--border);position:relative;overflow:hidden;}}
header::before{{content:'';position:absolute;top:-80px;left:-80px;width:400px;height:400px;background:radial-gradient(circle,#00d4aa18,transparent 70%);pointer-events:none;}}
header::after{{content:'';position:absolute;bottom:-60px;right:100px;width:300px;height:300px;background:radial-gradient(circle,#7c6bff14,transparent 70%);pointer-events:none;}}
.header-tag{{display:inline-block;font-size:11px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:var(--accent);border:1px solid var(--accent);padding:4px 12px;border-radius:20px;margin-bottom:18px;}}
h1{{font-family:'Syne',sans-serif;font-size:clamp(28px,5vw,52px);font-weight:800;line-height:1.1;letter-spacing:-1px;margin-bottom:12px;}}
h1 span{{color:var(--accent);}}
.header-meta{{color:var(--muted);font-size:13px;margin-top:8px;}}
main{{max-width:1100px;margin:0 auto;padding:40px 40px 80px;}}
section{{margin-bottom:56px;}}
.section-title{{font-family:'Syne',sans-serif;font-size:13px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:var(--muted);margin-bottom:20px;display:flex;align-items:center;gap:10px;}}
.section-title::after{{content:'';flex:1;height:1px;background:var(--border);}}
.kpi-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:14px;margin-bottom:48px;}}
.kpi{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:20px;transition:border-color .2s;}}
.kpi:hover{{border-color:#ffffff22;}}
.kpi-label{{font-size:11px;font-weight:500;letter-spacing:1px;text-transform:uppercase;color:var(--muted);margin-bottom:8px;}}
.kpi-value{{font-family:'Syne',sans-serif;font-size:26px;font-weight:700;line-height:1;}}
.kpi-sub{{font-size:11px;color:var(--muted);margin-top:4px;}}
.kpi.accent .kpi-value{{color:var(--accent);}}
.kpi.accent2 .kpi-value{{color:var(--accent2);}}
.table-wrap{{background:var(--surface);border:1px solid var(--border);border-radius:14px;overflow:hidden;}}
table{{width:100%;border-collapse:collapse;}}
thead tr{{background:var(--surface2);}}
th{{padding:14px 18px;font-size:11px;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);text-align:left;}}
td{{padding:14px 18px;border-top:1px solid var(--border);font-size:14px;}}
tr:hover td{{background:#ffffff04;}}
td.num{{font-family:'Syne',sans-serif;color:var(--muted);font-size:13px;}}
.badge{{display:inline-block;padding:2px 10px;border-radius:20px;font-size:12px;font-weight:700;font-family:'Syne',sans-serif;}}
.bar-wrap{{display:flex;align-items:center;gap:10px;min-width:200px;}}
.bar{{height:6px;border-radius:3px;flex-shrink:0;}}
.bar-wrap span{{font-family:'Syne',sans-serif;font-size:13px;font-weight:600;white-space:nowrap;}}
.mob-grid{{display:grid;grid-template-columns:1fr 1fr;gap:14px;}}
.mob-card{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:24px;}}
.mob-card .label{{font-size:12px;color:var(--muted);margin-bottom:6px;}}
.mob-card .valor{{font-family:'Syne',sans-serif;font-size:28px;font-weight:700;}}
.mob-card .diff{{margin-top:8px;font-size:13px;color:var(--muted);}}
.mob-card .diff strong{{color:#ff6b9d;}}
.faixa-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;}}
.faixa-card{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:24px;text-align:center;}}
.faixa-dot{{font-size:28px;margin-bottom:10px;}}
.faixa-label{{font-size:12px;color:var(--muted);margin-bottom:6px;font-weight:500;letter-spacing:1px;text-transform:uppercase;}}
.faixa-num{{font-family:'Syne',sans-serif;font-size:32px;font-weight:800;}}
.faixa-pct{{font-size:12px;color:var(--muted);margin-top:4px;}}
footer{{text-align:center;padding:40px;border-top:1px solid var(--border);color:var(--muted);font-size:12px;}}
footer a{{color:var(--accent);text-decoration:none;}}
@media(max-width:600px){{main{{padding:24px 20px 60px;}}header{{padding:40px 20px 30px;}}faixa-grid{{grid-template-columns:1fr;}}.mob-grid{{grid-template-columns:1fr;}}.bar-wrap{{min-width:120px;}}}}
</style>
</head>
<body>
<header>
  <div class="header-tag">ETL IMOVEIS BR</div>
  <h1>Mercado de Aluguel<br><span>Brasileiro</span></h1>
  <p class="header-meta">Gerado em {agora} &nbsp;&middot;&nbsp; Dataset sintetico com distribuicoes reais &nbsp;&middot;&nbsp; Python + Pandas + NumPy</p>
</header>
<main>
  <div class="section-title">Visao Geral</div>
  <div class="kpi-grid">
    <div class="kpi accent"><div class="kpi-label">Imoveis analisados</div><div class="kpi-value">{total:,}</div><div class="kpi-sub">apos limpeza e outliers</div></div>
    <div class="kpi"><div class="kpi-label">Cidades</div><div class="kpi-value">{cidades_n}</div><div class="kpi-sub">grandes centros brasileiros</div></div>
    <div class="kpi accent2"><div class="kpi-label">Aluguel medio</div><div class="kpi-value">R$ {alug_medio:,.0f}</div><div class="kpi-sub">mediana: R$ {alug_mediano:,.0f}</div></div>
    <div class="kpi"><div class="kpi-label">Minimo</div><div class="kpi-value">R$ {alug_min:,.0f}</div><div class="kpi-sub">apos IQR x 2.5</div></div>
    <div class="kpi"><div class="kpi-label">Maximo</div><div class="kpi-value">R$ {alug_max:,.0f}</div><div class="kpi-sub">apos IQR x 2.5</div></div>
    <div class="kpi"><div class="kpi-label">Preco mediano m2</div><div class="kpi-value">R$ {preco_m2:,.0f}</div><div class="kpi-sub">feature derivada</div></div>
  </div>
  <section>
    <div class="section-title">Ranking por Cidade</div>
    <div class="table-wrap"><table><thead><tr><th>#</th><th>Cidade</th><th>Aluguel Medio</th><th>Imoveis</th></tr></thead><tbody>{ranking_rows}</tbody></table></div>
  </section>
  <section>
    <div class="section-title">Impacto da Mobilia</div>
    <div class="mob-grid">
      <div class="mob-card"><div class="label">Mobiliado</div><div class="valor" style="color:#00d4aa">R$ {mob_sim:,.0f}</div><div class="diff">aluguel medio</div></div>
      <div class="mob-card"><div class="label">Sem Mobilia</div><div class="valor" style="color:#7c6bff">R$ {mob_nao:,.0f}</div><div class="diff">Mobiliados custam <strong>{var_mob:.1f}% a mais</strong></div></div>
    </div>
  </section>
  <section>
    <div class="section-title">Aluguel por Numero de Quartos</div>
    <div class="table-wrap"><table><thead><tr><th></th><th>Quartos</th><th>Aluguel Medio</th><th>Quantidade</th></tr></thead><tbody>{quartos_rows}</tbody></table></div>
  </section>
  <section>
    <div class="section-title">Distribuicao por Faixa de Preco</div>
    <div class="faixa-grid">{faixa_cards}</div>
  </section>
</main>
<footer>
  Gerado automaticamente pelo pipeline <strong>etl-imoveis-br</strong> &nbsp;&middot;&nbsp; Python &middot; Pandas &middot; NumPy
</footer>
</body>
</html>"""

    destino = BASE / "reports" / "insights.html"
    destino.parent.mkdir(exist_ok=True)
    destino.write_text(html, encoding="utf-8")
    logger.info(f"HTML salvo em: {destino}")

def main():
    print("\n" + "=" * 55)
    print("   ETL IMOVEIS BR - Pipeline de Dados")
    print("=" * 55 + "\n")
    df_raw   = extrair()
    df_clean = transformar(df_raw)
    gerar_html(df_clean)
    print("\n" + "=" * 55)
    print(f"   Concluido! {len(df_clean):,} imoveis processados.")
    print(f"   Relatorio: reports/insights.html")
    print("=" * 55 + "\n")

if __name__ == "__main__":
    main()
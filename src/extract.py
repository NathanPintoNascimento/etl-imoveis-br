import pandas as pd
import numpy as np
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CIDADES = {
    "Sao Paulo":      {"media": 3800, "desvio": 1800, "peso": 30},
    "Rio de Janeiro": {"media": 3200, "desvio": 1500, "peso": 20},
    "Belo Horizonte": {"media": 2100, "desvio": 900,  "peso": 12},
    "Curitiba":       {"media": 2300, "desvio": 1000, "peso": 10},
    "Porto Alegre":   {"media": 2000, "desvio": 850,  "peso": 8},
    "Salvador":       {"media": 1800, "desvio": 750,  "peso": 7},
    "Fortaleza":      {"media": 1600, "desvio": 700,  "peso": 7},
    "Recife":         {"media": 1700, "desvio": 720,  "peso": 6},
}

def gerar_dados_sinteticos(n_registros=10000, seed=42):
    np.random.seed(seed)
    logger.info(f"Gerando {n_registros} registros sinteticos...")
    cidades_lista = list(CIDADES.keys())
    pesos = [CIDADES[c]["peso"] for c in cidades_lista]
    pesos_norm = [p / sum(pesos) for p in pesos]
    cidades_col = np.random.choice(cidades_lista, size=n_registros, p=pesos_norm)
    alugueis, areas = [], []
    for cidade in cidades_col:
        cfg = CIDADES[cidade]
        aluguel = max(400, np.random.normal(cfg["media"], cfg["desvio"]))
        area = max(18, np.random.normal(aluguel / 35, 20))
        alugueis.append(round(aluguel, 2))
        areas.append(round(area, 1))
    alugueis = np.array(alugueis)
    areas = np.array(areas)
    quartos = np.random.choice([1,2,3,4,5], size=n_registros, p=[0.15,0.30,0.35,0.15,0.05])
    banheiros = np.clip(quartos + np.random.randint(-1,2,n_registros), 1, 6)
    vagas = np.random.choice([0,1,2,3], size=n_registros, p=[0.20,0.45,0.28,0.07])
    andares = np.random.choice(list(range(0,31)), size=n_registros, p=[0.10]+[0.03]*30)
    animais = np.random.choice(["acept","not acept"], size=n_registros, p=[0.45,0.55])
    mobilia = np.random.choice(["furnished","not furnished"], size=n_registros, p=[0.35,0.65])
    bonus_mob = np.where(mobilia == "furnished", np.random.uniform(1.05,1.25,n_registros), 1.0)
    alugueis = (alugueis * bonus_mob).round(2)
    condominio = (alugueis * np.random.uniform(0.08,0.20,n_registros)).round(2)
    iptu = (alugueis * np.random.uniform(0.01,0.05,n_registros)).round(2)
    seguro = (alugueis * np.random.uniform(0.005,0.015,n_registros)).round(2)
    total = (alugueis + condominio + iptu + seguro).round(2)
    idx_out = np.random.choice(n_registros, size=int(n_registros*0.03), replace=False)
    alugueis[idx_out] *= np.random.uniform(5, 15, len(idx_out))
    alugueis_s = pd.Series(alugueis, dtype=float)
    idx_nulos = np.random.choice(n_registros, size=int(n_registros*0.01), replace=False)
    alugueis_s.iloc[idx_nulos] = np.nan
    df = pd.DataFrame({
        "city": cidades_col, "area": areas, "rooms": quartos,
        "bathroom": banheiros, "parking spaces": vagas, "floor": andares,
        "animal": animais, "furniture": mobilia,
        "hoa (R$)": condominio, "rent amount (R$)": alugueis_s,
        "property tax (R$)": iptu, "fire insurance (R$)": seguro, "total (R$)": total,
    })
    Path("data").mkdir(exist_ok=True)
    df.to_csv("data/houses_to_rent_v2.csv", index=False)
    logger.info(f"CSV salvo | Shape: {df.shape} | Outliers: {len(idx_out)} | Nulos: {len(idx_nulos)}")
    return df

def extrair_dados(caminho_csv="data/houses_to_rent_v2.csv"):
    p = Path(caminho_csv)
    if p.exists():
        logger.info(f"CSV encontrado. Lendo: {caminho_csv}")
        return pd.read_csv(caminho_csv)
    logger.info("CSV nao encontrado. Gerando dados sinteticos...")
    return gerar_dados_sinteticos()

if __name__ == "__main__":
    df = extrair_dados()
    print(df.head())

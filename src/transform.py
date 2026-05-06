import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

MAPA_COLUNAS = {
    "city": "cidade", "area": "area_m2", "rooms": "quartos",
    "bathroom": "banheiros", "parking spaces": "vagas_garagem",
    "floor": "andar", "animal": "aceita_animal", "furniture": "mobiliado",
    "hoa (R$)": "condominio_reais", "rent amount (R$)": "aluguel_reais",
    "property tax (R$)": "iptu_reais", "fire insurance (R$)": "seguro_incendio_reais",
    "total (R$)": "total_reais",
}

def _limpar_coluna_monetaria(serie):
    return (serie.astype(str)
            .str.replace(r"[R$\.\s]", "", regex=True)
            .str.replace(",", ".")
            .pipe(pd.to_numeric, errors="coerce"))

def _remover_outliers_iqr(df, coluna, fator=2.5):
    q1, q3 = df[coluna].quantile(0.25), df[coluna].quantile(0.75)
    iqr = q3 - q1
    antes = len(df)
    df = df[(df[coluna] >= q1 - fator*iqr) & (df[coluna] <= q3 + fator*iqr)]
    logger.info(f"  [{coluna}] outliers removidos: {antes - len(df)}")
    return df

def _normalizar_min_max(df, colunas):
    for col in colunas:
        mn, mx = df[col].min(), df[col].max()
        df[f"{col}_norm"] = ((df[col]-mn)/(mx-mn)).round(4) if mx > mn else 0.0
    return df

def transformar(df):
    df = df.rename(columns=MAPA_COLUNAS)
    logger.info("Colunas renomeadas.")
    for col in ["aceita_animal","mobiliado"]:
        df[col] = df[col].map({"acept":True,"not acept":False,"furnished":True,"not furnished":False})
    df["andar"] = pd.to_numeric(df["andar"].replace("-",0), errors="coerce").fillna(0).astype(int)
    monetarias = ["condominio_reais","aluguel_reais","iptu_reais","seguro_incendio_reais","total_reais"]
    for col in monetarias:
        if df[col].dtype == object:
            df[col] = _limpar_coluna_monetaria(df[col])
    for col in monetarias + ["area_m2","quartos","banheiros","vagas_garagem"]:
        if df[col].isnull().any():
            med = df[col].median()
            df[col] = df[col].fillna(med)
            logger.info(f"  Nulos em '{col}' preenchidos com mediana ({med:.2f})")
    logger.info("Removendo outliers via IQR:")
    for col in ["aluguel_reais","area_m2","total_reais"]:
        df = _remover_outliers_iqr(df, col)
    df = _normalizar_min_max(df, ["aluguel_reais","area_m2","total_reais","quartos"])
    df["preco_por_m2"] = (df["aluguel_reais"] / df["area_m2"].replace(0, np.nan)).round(2)
    df["cidade"] = df["cidade"].str.strip().str.title()
    logger.info(f"Transformacao concluida. Shape final: {df.shape}")
    return df

import pandas as pd, logging, os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def _criar_engine():
    host  = os.getenv("DB_HOST","localhost")
    porta = os.getenv("DB_PORT","5432")
    user  = os.getenv("DB_USER","etl_user")
    senha = os.getenv("DB_PASS","etl_pass")
    banco = os.getenv("DB_NAME","imoveis_br")
    return create_engine(f"postgresql+psycopg2://{user}:{senha}@{host}:{porta}/{banco}", pool_pre_ping=True)

def carregar_dados(df, tabela="imoveis"):
    engine = _criar_engine()
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Conexao com PostgreSQL OK.")
        logger.info(f"Carregando {len(df)} registros na tabela '{tabela}'...")
        df.to_sql(tabela, con=engine, if_exists="replace", index=False, chunksize=500, method="multi")
        logger.info("Carga concluida.")
        with engine.connect() as conn:
            conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_cidade ON {tabela}(cidade); CREATE INDEX IF NOT EXISTS idx_aluguel ON {tabela}(aluguel_reais);"))
            conn.commit()
        logger.info("Indices criados.")
    except SQLAlchemyError as e:
        logger.error(f"Erro na carga: {e}"); raise
    finally:
        engine.dispose()

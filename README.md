# etl-imoveis-br

Pipeline ETL completo para analise do mercado de aluguel de imoveis no Brasil.
Roda 100% local sem banco de dados - apenas Python e as libs do requirements.txt.
O carregamento no PostgreSQL e opcional e esta documentado abaixo.

---

## Pipeline de Dados

    [Geracao sintetica] -> [Extracao CSV] -> [Transformacao] -> [Relatorio Markdown]
        NumPy/Pandas          Pandas          limpeza, IQR       reports/insights.md
                                              normalizacao
                                              tipagem

Para quem quiser ir alem:

    ... -> [Carga PostgreSQL] -> [Queries Analiticas SQL]
            SQLAlchemy              CTEs, Window Functions

---

## Tecnologias

| Camada          | Tecnologia          | Versao     |
|-----------------|---------------------|------------|
| Linguagem       | Python              | 3.11+      |
| Manipulacao     | Pandas + NumPy      | 2.2 / 1.26 |
| Banco de dados  | PostgreSQL          | 15         |
| ORM / Carga     | SQLAlchemy          | 2.0        |
| Driver DB       | psycopg2-binary     | 2.9        |
| Infraestrutura  | Docker + Compose    | 3.9        |

---

## Estrutura do Projeto

    etl-imoveis-br/
    â”œâ”€â”€ src/
    â”‚   â”œâ”€â”€ pipeline.py      <- orquestrador principal (rode este)
    â”‚   â”œâ”€â”€ extract.py       <- extracao detalhada
    â”‚   â”œâ”€â”€ transform.py     <- transformacao detalhada
    â”‚   â””â”€â”€ load.py          <- carga no PostgreSQL (opcional)
    â”œâ”€â”€ sql/
    â”‚   â””â”€â”€ queries.sql      <- 6 queries analiticas complexas
    â”œâ”€â”€ data/                <- CSV gerado automaticamente
    â”œâ”€â”€ reports/             <- relatorio .md gerado automaticamente
    â”œâ”€â”€ docker-compose.yml   <- PostgreSQL + pgAdmin (opcional)
    â”œâ”€â”€ requirements.txt
    â”œâ”€â”€ .env                 <- credenciais do banco (nao versionar)
    â”œâ”€â”€ .gitignore
    â””â”€â”€ README.md

---

## Como Rodar (sem banco de dados)

Pre-requisitos: Python 3.11 ou superior instalado.

1. Acesse a pasta do projeto

    cd "C:\Users\suzys\Desktop\etl-imoveis-br"

2. Crie e ative um ambiente virtual (recomendado)

    python -m venv .venv
    .venv\Scripts\Activate.ps1

   Se aparecer erro de permissao:
    Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

3. Instale as dependencias

    pip install -r requirements.txt

4. Execute o pipeline

    python src/pipeline.py

5. Veja o relatorio gerado

    type reports\insights.md

Ao rodar, o pipeline:
- Gera 10.000 registros sinteticos com distribuicoes reais por cidade
- Injeta ~300 outliers e ~100 nulos para demonstrar o tratamento
- Aplica limpeza, tipagem, normalizacao Min-Max e remocao de outliers via IQR
- Salva data/houses_to_rent_v2.csv e reports/insights.md

---

## Opcional: Carregar no PostgreSQL com Docker

Pre-requisitos adicionais: Docker Desktop instalado e rodando.

1. Suba o banco

    docker compose up -d

2. Aguarde o banco ficar saudavel (~15 segundos)

    docker compose ps

3. Instale dependencias adicionais

    pip install sqlalchemy==2.0.30 psycopg2-binary==2.9.9 python-dotenv==1.0.1

4. Execute a carga

    python src/load.py

5. Execute as queries analiticas

    docker exec -i imoveis_postgres psql -U etl_user -d imoveis_br < sql/queries.sql

6. Acesse o pgAdmin (interface visual)

   Abra: http://localhost:8080
   Login: admin@etl.com / admin123
   Conectar ao servidor: host=postgres, porta=5432, banco=imoveis_br

7. Para derrubar o banco

    docker compose down

---

## Opcional: Carregar em PostgreSQL ja existente (sem Docker)

1. Crie o banco

    CREATE DATABASE imoveis_br;

2. Edite o arquivo .env

    DB_HOST=seu-servidor.com
    DB_PORT=5432
    DB_USER=seu_usuario
    DB_PASS=sua_senha
    DB_NAME=imoveis_br

3. Instale dependencias e execute

    pip install sqlalchemy==2.0.30 psycopg2-binary==2.9.9 python-dotenv==1.0.1
    python src/load.py

---

## Queries SQL Implementadas

| #  | Query                              | Conceitos SQL                            |
|----|------------------------------------|------------------------------------------|
| 1  | Ranking de cidades por aluguel     | CTE + RANK() + STDDEV + PERCENTILE_CONT  |
| 2  | Percentil de preco por cidade      | NTILE(4) + PERCENT_RANK()                |
| 3  | Variacao entre cidades             | LAG() + CTE + variacao percentual        |
| 4  | Segmentacao por custo-beneficio    | CTEs encadeadas + CASE WHEN              |
| 5  | Top 3 mais baratos por cidade      | ROW_NUMBER() + filtro top-N              |
| 6  | Correlacao faixa de area x aluguel | CASE + SUM() OVER() + percentual         |

---

## Decisoes Tecnicas

| Decisao | Justificativa |
|---|---|
| IQR x 2.5 para outliers | Mais conservador que 1.5 - preserva dados validos em distribuicoes assimetricas |
| Mediana para imputacao | Robusta a outliers, mais representativa que a media em dados de aluguel |
| Min-Max Scaling | Normaliza sem assumir distribuicao normal |
| if_exists=replace no SQLAlchemy | Garante idempotencia - re-executar nao duplica dados |
| Indices automaticos | Criados em cidade e aluguel_reais para otimizar as queries |
| Dados sinteticos | Seed fixo = resultados reprodutiveis |

---

*Pipeline 100% local - sem dependencias externas de dados.*

---

**Autor:** Nathan Pinto Nascimento

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Nathan-blue)](https://www.linkedin.com/in/nathan-nascimento-) [![GitHub](https://img.shields.io/badge/GitHub-NathanPintoNascimento-black)](https://github.com/NathanPintoNascimento)


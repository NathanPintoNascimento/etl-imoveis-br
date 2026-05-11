# 🏠 etl-imoveis-br

> Pipeline ETL completo para análise do mercado de aluguel de imóveis no Brasil.
> Do dado bruto ao relatório HTML — 100% local, sem dependências externas.

**Autor:** Nathan Pinto Nascimento
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Nathan-0077B5?style=flat&logo=linkedin)](https://www.linkedin.com/in/nathan-nascimento-)
[![GitHub](https://img.shields.io/badge/GitHub-NathanPintoNascimento-181717?style=flat&logo=github)](https://github.com/NathanPintoNascimento)

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.2-150458?style=flat&logo=pandas)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=flat&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)
![Status](https://img.shields.io/badge/status-concluído-00d4aa?style=flat)

---

##  Insights Encontrados

- 🥇 **São Paulo** lidera com o maior aluguel médio entre todas as cidades analisadas
- 🛋️ Imóveis **mobiliados custam até 15% a mais** — mas eliminam custos iniciais de instalação
- 📐 O **preço por m²** é o indicador mais justo para comparar imóveis entre cidades de tamanhos diferentes
- 🧹 **~300 outliers e ~100 nulos** tratados automaticamente pelo pipeline a cada execução
- 🏆 **Fortaleza e Recife** apresentam o melhor custo-benefício entre as capitais analisadas

---

##  Pipeline de Dados

    [Geração]  ──►  [Extração]  ──►  [Transformação]  ──►  [Relatório HTML]
     NumPy           Pandas           limpeza · IQR          reports/insights.html
                                      normalização
                                      tipagem
                                           │
                                           ▼
                                [Carga PostgreSQL]  ──►  [Queries SQL]
                                 SQLAlchemy               CTEs · Window Functions

---

##  Tecnologias

| Camada | Tecnologia | Versão |
|---|---|---|
| Linguagem | Python | 3.11+ |
| Manipulação | Pandas + NumPy | 2.2 / 1.26 |
| Banco de dados | PostgreSQL | 15 |
| ORM / Carga | SQLAlchemy | 2.0 |
| Driver DB | psycopg2-binary | 2.9 |
| Infraestrutura | Docker + Compose | 3.9 |

---

##  Estrutura do Projeto

    etl-imoveis-br/
    ├── src/
    │   ├── pipeline.py      ← orquestrador principal (rode este)
    │   ├── extract.py       ← extração detalhada
    │   ├── transform.py     ← transformação detalhada
    │   └── load.py          ← carga no PostgreSQL (opcional)
    ├── sql/
    │   └── queries.sql      ← 6 queries analíticas complexas
    ├── data/                ← CSV gerado automaticamente
    ├── reports/             ← relatório HTML gerado automaticamente
    ├── docker-compose.yml   ← PostgreSQL + pgAdmin (opcional)
    ├── requirements.txt
    ├── .env                 ← credenciais do banco (não versionar)
    ├── .gitignore
    └── README.md

---

##  Como Rodar (sem banco de dados)

**Pré-requisito:** Python 3.11+

    # 1. Entre na pasta
    cd etl-imoveis-br

    # 2. Crie e ative o ambiente virtual
    python -m venv .venv
    .venv\Scripts\Activate.ps1

    # Se der erro de permissão:
    Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

    # 3. Instale as dependências
    pip install -r requirements.txt

    # 4. Execute o pipeline
    python src/pipeline.py

    # 5. Abra o relatório no navegador
    Start-Process reports\insights.html

O pipeline vai:
- Processar **10.000 registros** com distribuições reais por cidade
- Tratar ~300 outliers e ~100 nulos automaticamente
- Aplicar limpeza, tipagem, normalização Min-Max e remoção de outliers via IQR
- Gerar `reports/insights.html` com dashboard completo de insights

---

##  Opcional: PostgreSQL com Docker

    # 1. Suba o banco
    docker compose up -d

    # 2. Instale as dependências extras
    pip install sqlalchemy==2.0.30 psycopg2-binary==2.9.9 python-dotenv==1.0.1

    # 3. Execute a carga
    python src/load.py

    # 4. Execute as queries analíticas
    docker exec -i imoveis_postgres psql -U etl_user -d imoveis_br < sql/queries.sql

**pgAdmin:** http://localhost:8080
Login: `admin@etl.com` / `admin123`
Conectar: host `postgres` · porta `5432` · banco `imoveis_br`

---

##  Queries SQL Implementadas

| # | Query | Conceitos |
|---|---|---|
| 1 | Ranking de cidades por aluguel | `CTE` + `RANK()` + `STDDEV` + `PERCENTILE_CONT` |
| 2 | Percentil de preço por cidade | `NTILE(4)` + `PERCENT_RANK()` |
| 3 | Variação entre cidades | `LAG()` + `CTE` + variação percentual |
| 4 | Segmentação por custo-benefício | CTEs encadeadas + `CASE WHEN` |
| 5 | Top 3 mais baratos por cidade | `ROW_NUMBER()` + filtro top-N |
| 6 | Correlação faixa de área × aluguel | `CASE` + `SUM() OVER()` + percentual |

---

##  Decisões Técnicas

| Decisão | Justificativa |
|---|---|
| **IQR × 2.5** | Mais conservador que 1.5 — preserva dados válidos em distribuições assimétricas |
| **Mediana para imputação** | Robusta a outliers, mais representativa que a média em dados de aluguel |
| **Min-Max Scaling** | Normaliza sem assumir distribuição normal |
| **if_exists=replace** | Garante idempotência — re-executar não duplica dados |
| **Índices automáticos** | Criados em `cidade` e `aluguel_reais` para otimizar as queries |
| **Seed fixo** | Resultados 100% reprodutíveis |

---

##  Licença

Este projeto está sob a licença MIT.

---

*Pipeline 100% local — sem dependências externas de dados.*

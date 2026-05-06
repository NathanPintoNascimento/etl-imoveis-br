-- ==================================================
-- QUERIES ANALITICAS - etl-imoveis-br
-- ==================================================

-- 1. RANKING DE CIDADES POR ALUGUEL MEDIO
WITH stats_cidade AS (
    SELECT cidade, COUNT(*) AS total_imoveis,
        ROUND(AVG(aluguel_reais)::NUMERIC,2) AS aluguel_medio,
        ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY aluguel_reais)::NUMERIC,2) AS aluguel_mediano,
        ROUND(STDDEV(aluguel_reais)::NUMERIC,2) AS desvio_padrao
    FROM imoveis GROUP BY cidade
)
SELECT *, RANK() OVER (ORDER BY aluguel_medio DESC) AS ranking
FROM stats_cidade ORDER BY ranking;

-- 2. PERCENTIL DE PRECO POR CIDADE (Window Function)
SELECT cidade, aluguel_reais, area_m2, quartos,
    NTILE(4) OVER (PARTITION BY cidade ORDER BY aluguel_reais) AS quartil,
    ROUND(PERCENT_RANK() OVER (PARTITION BY cidade ORDER BY aluguel_reais)::NUMERIC*100,1) AS percentil
FROM imoveis ORDER BY cidade, aluguel_reais;

-- 3. VARIACAO ENTRE CIDADES COM LAG
WITH medias AS (
    SELECT cidade,
        ROUND(AVG(aluguel_reais)::NUMERIC,2) AS aluguel_medio,
        ROUND(AVG(preco_por_m2)::NUMERIC,2) AS preco_m2_medio
    FROM imoveis GROUP BY cidade
)
SELECT *, LAG(aluguel_medio) OVER (ORDER BY aluguel_medio DESC) AS cidade_anterior,
    ROUND((aluguel_medio - LAG(aluguel_medio) OVER (ORDER BY aluguel_medio DESC))
        / NULLIF(LAG(aluguel_medio) OVER (ORDER BY aluguel_medio DESC),0)*100,2) AS variacao_pct
FROM medias ORDER BY aluguel_medio DESC;

-- 4. SEGMENTACAO POR CUSTO-BENEFICIO
WITH base AS (
    SELECT *, CASE
        WHEN preco_por_m2 <= 20 THEN 'Excelente custo-beneficio'
        WHEN preco_por_m2 <= 40 THEN 'Bom custo-beneficio'
        WHEN preco_por_m2 <= 70 THEN 'Preco medio'
        ELSE 'Premium' END AS segmento
    FROM imoveis
),
resumo AS (
    SELECT cidade, segmento, COUNT(*) AS qtd,
        ROUND(AVG(aluguel_reais)::NUMERIC,2) AS aluguel_medio
    FROM base GROUP BY cidade, segmento
)
SELECT *, ROUND(qtd::NUMERIC / SUM(qtd) OVER (PARTITION BY cidade)*100,1) AS pct_na_cidade
FROM resumo ORDER BY cidade, aluguel_medio;

-- 5. TOP 3 MAIS BARATOS POR CIDADE (ROW_NUMBER)
WITH ranked AS (
    SELECT cidade, area_m2, quartos, aluguel_reais, mobiliado, aceita_animal,
        ROW_NUMBER() OVER (PARTITION BY cidade ORDER BY aluguel_reais ASC) AS posicao
    FROM imoveis WHERE aluguel_reais > 0
)
SELECT * FROM ranked WHERE posicao <= 3 ORDER BY cidade, posicao;

-- 6. CORRELACAO FAIXA DE AREA x ALUGUEL
SELECT CASE WHEN area_m2 < 30  THEN 'Micro (< 30m2)'
            WHEN area_m2 < 60  THEN 'Pequeno (30-60m2)'
            WHEN area_m2 < 100 THEN 'Medio (60-100m2)'
            WHEN area_m2 < 200 THEN 'Grande (100-200m2)'
            ELSE 'Mansao (> 200m2)' END AS faixa_area,
    COUNT(*) AS total,
    ROUND(AVG(aluguel_reais)::NUMERIC,2) AS aluguel_medio,
    ROUND(AVG(preco_por_m2)::NUMERIC,2) AS preco_m2_medio,
    ROUND(MIN(aluguel_reais)::NUMERIC,2) AS aluguel_min,
    ROUND(MAX(aluguel_reais)::NUMERIC,2) AS aluguel_max,
    ROUND(COUNT(*)::NUMERIC / SUM(COUNT(*)) OVER ()*100,1) AS pct_total
FROM imoveis GROUP BY faixa_area ORDER BY aluguel_medio;

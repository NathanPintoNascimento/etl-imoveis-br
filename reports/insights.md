# Relatorio de Insights - Mercado de Aluguel Brasileiro

> Gerado em: 06/05/2026 18:50
> Dataset: Dados sinteticos com distribuicoes reais por cidade (10.000 registros)
> Total de imoveis analisados (apos limpeza): 9,714

---

## 1. Visao Geral

| Metrica | Valor |
|---|---|
| Total de imoveis | 9,714 |
| Cidades analisadas | 8 |
| Aluguel medio | R$ 2,941.84 |
| Aluguel mediano | R$ 2,635.57 |
| Cidade com maior oferta | Sao Paulo |
| Preco medio por m2 | R$ 36.12 |

---

## 2. Ranking de Cidades por Aluguel Medio

| # | Cidade | Aluguel Medio | Quantidade |
|---|---|---|---|
| 1 | Sao Paulo | R$ 4,014.65 | 2936 |
| 2 | Rio De Janeiro | R$ 3,338.20 | 1981 |
| 3 | Curitiba | R$ 2,470.30 | 973 |
| 4 | Belo Horizonte | R$ 2,238.07 | 1197 |
| 5 | Porto Alegre | R$ 2,108.01 | 721 |
| 6 | Salvador | R$ 1,985.88 | 688 |
| 7 | Recife | R$ 1,867.41 | 576 |
| 8 | Fortaleza | R$ 1,764.29 | 642 |

---

## 3. Impacto da Mobilia no Aluguel

| Categoria | Aluguel Medio |
|---|---|
| Mobiliado | R$ 3,212.73 |
| Sem mobilia | R$ 2,795.04 |
| Diferenca | +14.9% |

> Imoveis mobiliados custam em media 14.9% a mais.

---

## 4. Aluguel por Numero de Quartos

| Quartos | Aluguel Medio | Quantidade |
|---|---|---|
| 1 | R$ 2,943.14 | 1470 |
| 2 | R$ 2,961.85 | 2931 |
| 3 | R$ 2,921.77 | 3353 |
| 4 | R$ 2,964.50 | 1465 |
| 5 | R$ 2,888.37 | 495 |

---

## 5. Distribuicao por Faixa de Preco

| Faixa | Quantidade | % do Total |
|---|---|---|
| Economico | 3,206 | 33.0% |
| Medio | 3,205 | 33.0% |
| Premium | 3,303 | 34.0% |

---

## 6. Decisoes Tecnicas

| Decisao | Justificativa |
|---|---|
| IQR x 2.5 para outliers | Mais conservador que 1.5 - preserva dados validos em distribuicoes assimetricas |
| Mediana para imputacao | Robusta a outliers, mais representativa que a media em dados de aluguel |
| Min-Max Scaling | Normaliza sem assumir distribuicao normal |
| Dados sinteticos | Seed fixo = resultados reprodutiveis |

---

*Relatorio gerado automaticamente pelo pipeline ETL Imoveis BR.*

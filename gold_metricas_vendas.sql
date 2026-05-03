{{ config(materialized='table') }}

SELECT
    mes_venda,
    produto_id,
    COUNT(*)                    AS total_pedidos,
    SUM(quantidade)             AS unidades_vendidas,
    SUM(valor)                  AS receita_total,
    AVG(valor)                  AS ticket_medio,
    MAX(valor)                  AS maior_venda,
    MIN(valor)                  AS menor_venda
FROM {{ ref('silver_vendas') }}
GROUP BY mes_venda, produto_id
ORDER BY mes_venda DESC, receita_total DESC
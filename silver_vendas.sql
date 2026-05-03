{{
  config(
    materialized='incremental',
    unique_key='venda_id',
    incremental_strategy='merge'
  )
}}

SELECT
    venda_id,
    cliente_id,
    produto_id,
    ROUND(valor::NUMERIC, 2)          AS valor,
    quantidade,
    data_venda::TIMESTAMP             AS data_venda,
    DATE_TRUNC('month', data_venda)   AS mes_venda,
    created_at
FROM {{ ref('bronze_vendas') }}
WHERE valor > 0   -- remove registros inválidos

{% if is_incremental() %}
    AND created_at > (SELECT MAX(created_at) FROM {{ this }})
{% endif %}
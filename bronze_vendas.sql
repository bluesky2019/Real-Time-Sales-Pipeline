{{ config(materialized='view') }}

SELECT * FROM {{ source('public', 'bronze_vendas') }}
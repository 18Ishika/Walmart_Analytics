{{
    config(
        materialized='table',
    )
}}
SELECT * FROM {{ source('walmart_source','products')}};
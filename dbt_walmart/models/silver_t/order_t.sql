{{
    config(
        materialized='incremental',
        unique_key='order_id'
    )
}}
SELECT order_id, customer_id,store_id,order_timestamp,payment_method,order_status,total_amount, created_timestamp,updated_timestamp, current_timestamp() as processed_at
FROM
{{ source('walmart_source','orders')}}
WHERE is_active = 'Y'
{% if is_incremental() %}
    AND updated_at > (SELECT COALESCE(MAX(updated_at), '1970-01-01') FROM {{ this }})
{% endif %}
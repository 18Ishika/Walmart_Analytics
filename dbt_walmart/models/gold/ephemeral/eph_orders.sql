SELECT DISTINCT
order_id,
order_item_id,
payment_method,
order_status,
order_timestamp,
order_created_timestamp,
order_updated_timestamp,
order_processed_at,
order_is_active,
obt_b_processed_at,
CURRENT_TIMESTAMP() AS order_gold_processed_at

FROM 
{{ref("obt_b")}}
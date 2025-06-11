SELECT
    state_id,
    state_symbol,
    state_name
FROM {{ ref('dim_states')}}

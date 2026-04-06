select
    count(*) as row_count,
    sum(amount) as total_amount,
    min(loaded_at) as first_loaded_at,
    max(loaded_at) as last_loaded_at
from {{ ref('stg_test_asset') }}

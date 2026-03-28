select
    cast(id as {{ dbt.type_int() }}) as id,
    platform_name,
    cast(amount as {{ dbt.type_numeric() }}) as amount,
    cast(loaded_at as {{ dbt.type_timestamp() }}) as loaded_at
from {{ source('warehouse_smoke', 'warehouse_test_input') }}

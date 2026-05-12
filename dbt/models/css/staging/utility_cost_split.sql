with electricity as (
    select cast(amount as {{ dbt.type_numeric() }}) as amount
    from {{ source('raw_uploads_css', 'electricity_production_report') }}
    where lower(trim(item)) = 'generated'
),

steam as (
    select cast(amount as {{ dbt.type_numeric() }}) as amount
    from {{ source('raw_uploads_css', 'steam_production_report') }}
    where lower(trim(item)) = 'production'
),

chilled as (
    select cast(amount as {{ dbt.type_numeric() }}) as amount
    from {{ source('raw_uploads_css', 'chilled_water_production_report') }}
    where lower(trim(item)) = 'production'
),

mthw as (
    select sum(cast("final_bill_-_kbtu" as {{ dbt.type_numeric() }})) as amount
    from {{ source('raw_uploads_css', 'mthw_consumption_pi') }}
),

mmbtu as (
    select
        round(e.amount * 0.01) as electricity_mmbtu,
        round(s.amount * 0.00115) as steam_mmbtu,
        round(m.amount / 1000.0) as mthw_mmbtu,
        round(c.amount * 0.012) as chilled_water_mmbtu
    from electricity as e
    cross join steam as s
    cross join mthw as m
    cross join chilled as c
),

totals as (
    select
        electricity_mmbtu,
        steam_mmbtu,
        mthw_mmbtu,
        chilled_water_mmbtu,
        electricity_mmbtu + steam_mmbtu
        + mthw_mmbtu + chilled_water_mmbtu as total_mmbtu
    from mmbtu
)

select
    'electricity' as utility_type,
    electricity_mmbtu as mmbtu,
    round(electricity_mmbtu * 100.0 / total_mmbtu) as pct
from totals
union all
select
    'steam' as utility_type,
    steam_mmbtu as mmbtu,
    round(steam_mmbtu * 100.0 / total_mmbtu) as pct
from totals
union all
select
    'mthw' as utility_type,
    mthw_mmbtu as mmbtu,
    round(mthw_mmbtu * 100.0 / total_mmbtu) as pct
from totals
union all
select
    'chilled_water' as utility_type,
    chilled_water_mmbtu as mmbtu,
    round(chilled_water_mmbtu * 100.0 / total_mmbtu) as pct
from totals

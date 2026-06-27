with channel_stats as (
    select
        channel_name,
        channel_title,
        min(message_date) as first_post_date,
        max(message_date) as last_post_date,
        count(*) as total_posts,
        round(avg(view_count), 2) as avg_views
    from {{ ref('stg_telegram_messages') }}
    group by channel_name, channel_title
)

select
    row_number() over (order by channel_name) as channel_key,
    channel_name,
    channel_title,
    case
        when lower(channel_name) like '%pharma%' or lower(channel_name) like '%drug%' or lower(channel_name) like '%medicine%'
            then 'Pharmaceutical'
        when lower(channel_name) like '%cosmetic%' or lower(channel_name) like '%beauty%' or lower(channel_name) like '%skin%'
            then 'Cosmetics'
        when lower(channel_name) like '%medical%' or lower(channel_name) like '%health%' or lower(channel_name) like '%clinic%'
            then 'Medical'
        else 'General'
    end as channel_type,
    first_post_date,
    last_post_date,
    total_posts,
    avg_views
from channel_stats

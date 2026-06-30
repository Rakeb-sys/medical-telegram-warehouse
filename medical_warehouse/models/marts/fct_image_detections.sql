with detections as (
    select * from {{ source('raw', 'yolo_detections') }}
),

channels as (
    select channel_key, channel_name
    from {{ ref('dim_channels') }}
),

dates as (
    select date_key, full_date
    from {{ ref('dim_dates') }}
),

messages as (
    select message_id, channel_name, message_date
    from {{ ref('stg_telegram_messages') }}
)

select
    det.message_id::integer as message_id,
    c.channel_key,
    d.date_key,
    det.detected_class,
    det.confidence as confidence_score,
    det.image_category
from detections det
left join messages m
    on det.message_id::integer = m.message_id
    and det.channel_name = m.channel_name
left join channels c on det.channel_name = c.channel_name
left join dates d on cast(m.message_date as date) = d.full_date

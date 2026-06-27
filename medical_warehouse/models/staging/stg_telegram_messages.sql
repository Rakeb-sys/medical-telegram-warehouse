with source as (
    select * from {{ source('raw', 'telegram_messages') }}
),

cleaned as (
    select
        message_id,
        channel_name,
        channel_title,
        cast(message_date as timestamp) as message_date,
        coalesce(message_text, '') as message_text,
        length(coalesce(message_text, '')) as message_length,
        coalesce(has_media, false) as has_media,
        case when image_path is not null then true else false end as has_image,
        image_path,
        coalesce(views, 0) as view_count,
        coalesce(forwards, 0) as forward_count
    from source
    where message_id is not null
      and channel_name is not null
)

select * from cleaned

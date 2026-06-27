-- Ensure no messages have dates in the future.
-- This test passes when 0 rows are returned.
select message_id, message_date
from {{ ref('stg_telegram_messages') }}
where message_date > current_timestamp

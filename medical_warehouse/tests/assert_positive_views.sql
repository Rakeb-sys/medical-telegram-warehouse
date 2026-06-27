-- Ensure view counts are non-negative.
-- This test passes when 0 rows are returned.
select message_id, view_count
from {{ ref('fct_messages') }}
where view_count < 0

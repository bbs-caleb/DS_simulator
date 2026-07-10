WITH events_with_previous AS (
    SELECT
        timestamp,
        cookie_id,
        lagInFrame(timestamp, 1) OVER (
            PARTITION BY cookie_id
            ORDER BY timestamp
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS previous_timestamp,
        row_number() OVER (
            PARTITION BY cookie_id
            ORDER BY timestamp
        ) AS event_number
    FROM default.karpovexpress_session_log
),
session_starts AS (
    SELECT
        toDate(timestamp) AS day,
        if(
            event_number = 1
            OR dateDiff('second', previous_timestamp, timestamp) > 1800,
            1,
            0
        ) AS is_new_session
    FROM events_with_previous
)
SELECT
    day,
    sum(is_new_session) AS sessions_per_day
FROM session_starts
GROUP BY day
ORDER BY day;

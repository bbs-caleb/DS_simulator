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
events_with_session_start AS (
    SELECT
        timestamp,
        cookie_id,
        if(
            event_number = 1
            OR dateDiff('second', previous_timestamp, timestamp) > 1800,
            1,
            0
        ) AS is_new_session
    FROM events_with_previous
),
events_with_session_number AS (
    SELECT
        timestamp,
        cookie_id,
        sum(is_new_session) OVER (
            PARTITION BY cookie_id
            ORDER BY timestamp
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS session_number
    FROM events_with_session_start
),
sessions AS (
    SELECT
        cookie_id,
        session_number,
        toDate(min(timestamp)) AS day,
        count() AS requests_per_session
    FROM events_with_session_number
    GROUP BY
        cookie_id,
        session_number
)
SELECT
    day,
    avg(requests_per_session) AS avg_requests_per_session
FROM sessions
GROUP BY day
ORDER BY day;

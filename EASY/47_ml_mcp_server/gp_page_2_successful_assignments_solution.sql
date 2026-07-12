SELECT COUNT(*) AS users_count
FROM (
    SELECT user_id
    FROM completions
    GROUP BY user_id
    HAVING AVG(
        CASE
            WHEN score >= 90 THEN 1.0
            ELSE 0.0
        END
    ) >= 0.9
) AS qualified_users;

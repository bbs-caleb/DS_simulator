SELECT
    sales.user_id AS user_id,
    sales.item_id AS item_id,
    sales.qty AS qty,
    prices.price AS price
FROM
(
    SELECT
        user_id,
        item_id,
        sum(units) AS qty
    FROM default.karpov_express_orders
    WHERE toDate(timestamp) >= toDate(%(start_date)s)
      AND toDate(timestamp) <= toDate(%(end_date)s)
    GROUP BY
        user_id,
        item_id
) AS sales
INNER JOIN
(
    SELECT
        item_id,
        round(avg(price), 2) AS price
    FROM default.karpov_express_orders
    WHERE toDate(timestamp) >= toDate(%(start_date)s)
      AND toDate(timestamp) <= toDate(%(end_date)s)
    GROUP BY item_id
) AS prices
USING (item_id)
ORDER BY
    user_id,
    item_id

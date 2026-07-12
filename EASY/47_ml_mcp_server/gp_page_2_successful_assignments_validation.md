# Проверка SQL на приложенных CSV

## 1. Набор данных

Архив содержит:

| Файл | Число строк данных |
|---|---:|
| users.csv | 100 |
| assignments.csv | 100 |
| completions.csv | 100 |

В `completions.csv` присутствуют 62 уникальных пользователя с хотя бы одним выполнением.

## 2. Диагностический запрос

```sql
SELECT
    user_id,
    COUNT(*) AS completed_assignments,
    SUM(
        CASE
            WHEN score >= 90 THEN 1
            ELSE 0
        END
    ) AS successful_assignments,
    AVG(
        CASE
            WHEN score >= 90 THEN 1.0
            ELSE 0.0
        END
    ) AS success_share
FROM completions
GROUP BY user_id
HAVING AVG(
    CASE
        WHEN score >= 90 THEN 1.0
        ELSE 0.0
    END
) >= 0.9
ORDER BY user_id;
```

## 3. Подходящие пользователи

| user_id | выполнено | успешно | доля |
|---:|---:|---:|---:|
| 63 | 1 | 1 | 1.0 |
| 87 | 1 | 1 | 1.0 |

Итог:

```text
users_count = 2
```

## 4. Почему строк score >= 90 больше

В таблице есть 12 успешных строк, но многие принадлежат пользователям, имеющим также неуспешные результаты.

### user_id = 2

```text
92, 87, 94
```

Доля:

```text
2 / 3 = 66.67%
```

### user_id = 12

```text
40, 96, 14
```

Доля:

```text
1 / 3 = 33.33%
```

### user_id = 33

```text
90, 76
```

Доля:

```text
1 / 2 = 50%
```

### user_id = 88

```text
60, 90
```

Доля:

```text
1 / 2 = 50%
```

Поэтому `COUNT(DISTINCT user_id) WHERE score >= 90` дал бы неправильный ответ.

## 5. Финальная проверка

```sql
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
```

Результат:

| users_count |
|---:|
| 2 |

## 6. Что намеренно отсутствует в solution.sql

- создание таблиц;
- импорт данных;
- диагностический список;
- лишние JOIN;
- минимальное число выполнений;
- обработка повторных попыток;
- дополнительные комментарии;
- сортировка.

Файл содержит только запрос, необходимый для автопроверки.

# SKU Embeddings — тестирование и частые ошибки

# 1. Что проверяет автотест

SQL-часть обычно проверяет:

- точные имена колонок;
- количество строк;
- порядок строк;
- значения `qty`;
- значения `price`;
- корректность временного фильтра;
- правильный уровень агрегации.

Python-часть проверяет:

- `user_count`;
- `item_count`;
- `user_map`;
- `item_map`;
- тип `csr_matrix`;
- форму матрицы;
- значения матрицы;
- качество кода через pylint.

---

# 2. Главная ошибка в SQL

Неправильно:

```sql
SELECT
    user_id,
    item_id,
    sum(units) AS qty,
    round(avg(price), 2) AS price
FROM ...
GROUP BY
    user_id,
    item_id
```

Почему неправильно:

`price` начинает зависеть от пользователя.

Условие требует среднюю цену товара среди всех транзакций периода.

---

# 3. Вторая возможная ошибка

Неправильно считать цену без временного фильтра:

```sql
SELECT
    item_id,
    avg(price)
FROM table
GROUP BY item_id
```

Тогда:

- `qty` относится к выбранному периоду;
- `price` относится ко всей истории.

Правильно использовать одинаковый фильтр в обеих подвыборках.

---

# 4. Почему `sum`, а не `count`

Пример:

```text
transaction 1: units = 3
transaction 2: units = 2
```

```text
count(units) = 2
sum(units)   = 5
```

`count` считает количество строк.

`sum` считает проданные единицы.

---

# 5. Проверка Python вручную

```python
import pandas as pd
import numpy as np

sales_data = pd.DataFrame(
    {
        "user_id": [5, 1, 4, 1, 2],
        "item_id": [2068, 118, 1688, 285, 1229],
        "qty": [1, 1, 2, 1, 3],
        "price": [571.36, 626.66, 940.84, 1016.57, 518.99],
    }
)

obj = UserItemMatrix(sales_data)
```

Проверяем счётчики:

```python
assert obj.user_count == 4
assert obj.item_count == 5
```

Проверяем mapping пользователей:

```python
assert obj.user_map == {
    1: 0,
    2: 1,
    4: 2,
    5: 3,
}
```

Проверяем mapping товаров:

```python
assert obj.item_map == {
    118: 0,
    285: 1,
    1229: 2,
    1688: 3,
    2068: 4,
}
```

Проверяем матрицу:

```python
expected = np.array(
    [
        [1, 1, 0, 0, 0],
        [0, 0, 3, 0, 0],
        [0, 0, 0, 2, 0],
        [0, 0, 0, 0, 1],
    ]
)

np.testing.assert_array_equal(
    obj.csr_matrix.toarray(),
    expected,
)
```

---

# 6. Проверка независимости от порядка строк

Создайте второй DataFrame:

```python
shuffled = sales_data.sample(
    frac=1,
    random_state=42,
).reset_index(drop=True)
```

Затем:

```python
obj_1 = UserItemMatrix(sales_data)
obj_2 = UserItemMatrix(shuffled)

assert obj_1.user_map == obj_2.user_map
assert obj_1.item_map == obj_2.item_map
```

Это проходит благодаря сортировке ID.

---

# 7. Проверка пустого DataFrame

```python
empty = pd.DataFrame(
    columns=["user_id", "item_id", "qty", "price"]
)

obj = UserItemMatrix(empty)

assert obj.user_count == 0
assert obj.item_count == 0
assert obj.csr_matrix.shape == (0, 0)
```

---

# 8. Повторяющиеся координаты

Если в DataFrame случайно остались строки:

```text
user_id=1, item_id=10, qty=2
user_id=1, item_id=10, qty=3
```

`csr_matrix` суммирует одинаковые координаты.

Получится:

```text
matrix[0, 0] = 5
```

Но правильный пайплайн всё равно должен агрегировать данные в SQL.

---

# 9. Частые Python-ошибки

## Использовать реальные ID как индексы

Плохо:

```python
row_ind = sales_data["user_id"]
```

Большой ID создаст огромное число пустых строк.

## Не сортировать ID

Плохо:

```python
user_ids = sales_data["user_id"].unique()
```

Mapping станет зависеть от порядка строк.

## Создать плотную матрицу

Плохо:

```python
np.zeros((user_count, item_count))
```

Это может потребовать сотни гигабайт.

## Использовать `price` вместо `qty`

Условие говорит, что значением матрицы является количество покупок.

## Пересчитывать матрицу в property

Плохо:

```python
@property
def csr_matrix(self):
    return build_matrix()
```

Тяжёлая операция будет выполняться повторно.

---

# 10. Чек-лист перед загрузкой

## `query.sql`

- две отдельные подвыборки;
- `qty = sum(units)`;
- qty group by `user_id, item_id`;
- `price = round(avg(price), 2)`;
- price group by только `item_id`;
- одинаковый фильтр дат в обеих подвыборках;
- обе границы периода включены;
- `JOIN` по `item_id`;
- `ORDER BY user_id, item_id`.

## `solution.py`

- класс называется `UserItemMatrix`;
- аргумент называется `sales_data`;
- mappings отсортированы;
- индексы начинаются с нуля;
- значения берутся из `qty`;
- создаётся `csr_matrix`;
- форма равна `(user_count, item_count)`;
- properties возвращают приватные переменные;
- нет лишних зависимостей.

---

# 11. Что означает успешный результат

Успешный результат подтверждает, что:

- SQL правильно подготовил user-item взаимодействия;
- цена рассчитана на нужном уровне;
- Python построил компактную sparse-матрицу;
- интерфейс класса совпал с контрактом задания;
- решение можно использовать как основу следующего шага с embeddings.

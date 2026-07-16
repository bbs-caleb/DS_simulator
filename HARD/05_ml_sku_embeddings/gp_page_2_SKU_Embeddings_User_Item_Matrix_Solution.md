# SKU Embeddings — финальное решение User-Item Matrix

## Какие файлы загружать в проверяющую систему

Проверяющая система требует ровно два файла:

```text
query.sql
solution.py
```

В итоговом архиве эти файлы уже имеют правильные имена.

---

# 1. Финальный `query.sql`

```sql
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
```

## Почему запрос устроен именно так

В задаче есть два показателя с разными уровнями агрегации.

### Количество `qty`

Количество должно считаться для конкретной пары:

```text
user_id + item_id
```

Поэтому первая подвыборка использует:

```sql
sum(units) AS qty
GROUP BY user_id, item_id
```

### Цена `price`

Цена должна быть единой средней ценой товара среди всех транзакций выбранного периода.

Поэтому вторая подвыборка использует:

```sql
round(avg(price), 2) AS price
GROUP BY item_id
```

В группировке цены нет `user_id`.

### Временной фильтр

Обе агрегации используют один и тот же период:

```sql
toDate(timestamp) >= toDate(%(start_date)s)
AND
toDate(timestamp) <= toDate(%(end_date)s)
```

Обе границы включены.

### Соединение

```sql
USING (item_id)
```

добавляет среднюю цену товара к каждой строке пользователь–товар.

---

# 2. Финальный `solution.py`

```python
from typing import Dict

import pandas as pd
from scipy.sparse import csr_matrix


class UserItemMatrix:
    """Create a sparse user-item matrix from aggregated sales data."""

    def __init__(self, sales_data: pd.DataFrame):
        """Initialize mappings, counters, and the CSR matrix.

        Args:
            sales_data: Aggregated sales data with columns
                user_id, item_id, qty, and price.
        """
        self._sales_data = sales_data.copy()

        user_ids = sorted(self._sales_data["user_id"].unique())
        item_ids = sorted(self._sales_data["item_id"].unique())

        self._user_count = len(user_ids)
        self._item_count = len(item_ids)

        self._user_map = {
            int(user_id): index
            for index, user_id in enumerate(user_ids)
        }
        self._item_map = {
            int(item_id): index
            for index, item_id in enumerate(item_ids)
        }

        row_ind = (
            self._sales_data["user_id"]
            .map(self._user_map)
            .to_numpy(dtype=int)
        )
        col_ind = (
            self._sales_data["item_id"]
            .map(self._item_map)
            .to_numpy(dtype=int)
        )
        values = pd.to_numeric(
            self._sales_data["qty"]
        ).to_numpy()

        self._matrix = csr_matrix(
            (values, (row_ind, col_ind)),
            shape=(self._user_count, self._item_count),
        )

    @property
    def user_count(self) -> int:
        """Return the number of unique users."""
        return self._user_count

    @property
    def item_count(self) -> int:
        """Return the number of unique items."""
        return self._item_count

    @property
    def user_map(self) -> Dict[int, int]:
        """Return a mapping from user IDs to matrix row indexes."""
        return self._user_map

    @property
    def item_map(self) -> Dict[int, int]:
        """Return a mapping from item IDs to matrix column indexes."""
        return self._item_map

    @property
    def csr_matrix(self) -> csr_matrix:
        """Return the user-item matrix in CSR format."""
        return self._matrix
```

---

# 3. Соответствие требованиям задания

Решение:

- принимает `pandas.DataFrame`;
- создаёт копию входных данных;
- считает уникальных пользователей;
- считает уникальные товары;
- сортирует исходные ID;
- создаёт `user_map`;
- создаёт `item_map`;
- использует индексы с нуля;
- использует `qty` как значения матрицы;
- создаёт `scipy.sparse.csr_matrix`;
- задаёт правильную форму матрицы;
- выполняет вычисления один раз в `__init__`;
- properties возвращают готовые приватные переменные;
- сохраняет требуемые имена методов и класса.

---

# 4. Почему решение минимальное

Здесь нет:

- плотной матрицы;
- `pivot`;
- лишних классов;
- дополнительных зависимостей;
- повторного вычисления матрицы;
- изменения заданного интерфейса;
- ненужной бизнес-логики внутри учебного класса.

Каждая часть кода напрямую соответствует требованию автотеста.

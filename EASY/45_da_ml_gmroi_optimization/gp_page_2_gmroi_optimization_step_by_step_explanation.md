# Страница 2. GMROI Optimization — пошаговое объяснение с нуля

# 1. Импорты

```python
from typing import List

import pandas as pd
```

`List` используется для аннотации списка колонок.

`pandas` нужен для работы с таблицами.

---

# 2. Что делает `__init__`

Когда выполняется:

```python
gmroi = GMROI(
    "products.csv",
    "sales.csv",
    "stocks.csv",
    "purchases.csv",
)
```

Python:

1. Загружает четыре файла.
2. Сохраняет их внутри объекта.
3. Считает GMROI по продавцам.
4. Считает GMROI по категориям.
5. Строит таблицу закупок.

---

# 3. Что означает `self`

`self` — текущий объект.

Например:

```python
self._products_df
```

означает:

> Сохранить таблицу товаров внутри этого объекта.

Подчёркивание показывает, что атрибут внутренний.

---

# 4. Загрузка CSV

```python
return pd.read_csv(file_path)
```

`pd.read_csv` читает файл и возвращает `DataFrame`.

## Ошибка отсутствующего файла

```python
except FileNotFoundError:
    raise
```

Ошибка передаётся дальше без изменения.

## Остальные ошибки

```python
except Exception as error:
    raise RuntimeError from error
```

Пользователь получает `RuntimeError`, а исходная причина сохраняется.

---

# 5. Проверка группировки

Допустимы только:

```python
["week"]
["week", "seller_id"]
["week", "category_id"]
```

Если передать другое:

```python
raise ValueError
```

Это защищает API от неправильного использования.

---

# 6. Первое объединение

```python
data = self._products_df.merge(
    self._sales_df,
    on=["week", "seller_id", "product_id"],
    how="inner",
)
```

После этого в одной строке есть:

- категория;
- цена;
- себестоимость;
- проданное количество;
- логистика.

---

# 7. Второе объединение

```python
data = data.merge(
    self._stocks_df,
    on=["week", "seller_id", "product_id"],
    how="inner",
    suffixes=("_sales", "_stocks"),
)
```

Добавляются:

- количество на складе;
- стоимость хранения единицы.

Поскольку обе таблицы имеют колонку `qty`, появляются:

```text
qty_sales
qty_stocks
```

---

# 8. Маржа

```python
data["margin"] = (
    data["price"] - data["cost"]
) * data["qty_sales"]
```

Пример:

```text
price = 1000
cost = 700
qty_sales = 20
```

\[
(1000 - 700) \times 20 = 6000
\]

---

# 9. Стоимость запаса

```python
data["avg_inventory_cost"] = (
    data["qty_stocks"] * data["cost"]
)
```

Пример:

```text
qty_stocks = 50
cost = 700
```

\[
50 \times 700 = 35000
\]

---

# 10. Расходы хранения

```python
data["storage_cost"] = (
    data["qty_stocks"] * data["unit_storage_cost"]
)
```

Пример:

```text
qty_stocks = 50
unit_storage_cost = 8
```

\[
50 \times 8 = 400
\]

---

# 11. Группировка

```python
data.groupby(group_columns, as_index=False)
```

Для продавцов строки собираются по:

```text
week + seller_id
```

Для категорий:

```text
week + category_id
```

---

# 12. Агрегация

```python
.agg(
    margin=("margin", "sum"),
    logistic_costs=("logistic_costs", "sum"),
    avg_inventory_cost=("avg_inventory_cost", "sum"),
    storage_cost=("storage_cost", "sum"),
)
```

Все товары группы складываются.

Это важно: мы не усредняем GMROI отдельных товаров.

---

# 13. Итоговый GMROI

```python
grouped["gmroi"] = (
    (
        grouped["margin"]
        - grouped["logistic_costs"]
        - grouped["storage_cost"]
    )
    / grouped["avg_inventory_cost"]
).round(2)
```

Порядок:

1. Берём общую маржу.
2. Вычитаем логистику.
3. Вычитаем хранение.
4. Делим на стоимость запасов.
5. Округляем.

---

# 14. Оставляем точные колонки

```python
result_columns = group_columns + ["gmroi"]
```

Для продавцов:

```python
["week", "seller_id", "gmroi"]
```

Для категорий:

```python
["week", "category_id", "gmroi"]
```

---

# 15. Сортировка и индекс

```python
.sort_values(group_columns)
.reset_index(drop=True)
```

Результат сортируется и получает обычный индекс:

```text
0, 1, 2, 3...
```

---

# 16. Закупки KarpovExpress

```python
self._products_df["seller_id"] == 0
```

Оставляет только собственный ассортимент.

Нужные колонки:

```python
[
    "week",
    "product_id",
    "category_id",
    "cost",
]
```

---

# 17. Стоимость покупки

```python
purchases["purchase_cost"] = (
    purchases["qty"] * purchases["cost"]
)
```

Пример:

```text
qty = 100
cost = 500
```

\[
100 \times 500 = 50000
\]

---

# 18. Сводная таблица

До `pivot`:

```text
week        category_id  purchase_cost
2023-01-02  1            5129792
2023-01-02  3            9231286
```

После `pivot`:

```text
week        1        3
2023-01-02  5129792  9231286
```

---

# 19. Почему `result.columns.name = None`

`pivot` назначает техническое имя уровню колонок:

```text
category_id
```

Условие ожидает обычный набор колонок, поэтому имя уровня удаляется.

---

# 20. Типичные ошибки

## Перепутать два `qty`

- `qty_sales` — для маржи;
- `qty_stocks` — для запаса и хранения.

## Умножить логистику на количество

Нельзя: `logistic_costs` уже дана общей суммой.

## Соединить только по product_id

Это создаст many-to-many merge.

## Усреднить GMROI

Нужно делить агрегированные суммы.

## Не отфильтровать seller_id = 0

Закупки размножатся на продавцов.

## Забыть округление

Требуется два знака после запятой.

## Вернуть лишние колонки

Автотест может сравнивать структуру целиком.

---

# 21. Как запустить

Файлы должны лежать рядом:

```text
solution.py
products.csv
sales.csv
stocks.csv
purchases.csv
```

Пример:

```python
from solution import GMROI


gmroi = GMROI(
    "products.csv",
    "sales.csv",
    "stocks.csv",
    "purchases.csv",
)

print(gmroi.seller_gmroi.head())
print(gmroi.category_gmroi.head())
print(gmroi.purchases.head())
```

На платформу загружается только `solution.py`.

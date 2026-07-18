# Page 3 — GMROI Optimization: пошаговое объяснение с нуля

# 1. Создание объекта

```python
gmroi = GMROI(
    "products.csv",
    "sales.csv",
    "stocks.csv",
    "purchases.csv",
)
```

Python вызывает `__init__`.

Конструктор:

1. загружает четыре файла;
2. рассчитывает GMROI продавцов;
3. рассчитывает GMROI категорий;
4. рассчитывает закупки.

---

# 2. Атрибут `self`

`self` означает текущий объект.

```python
self._products_df
```

Это таблица товаров, сохранённая внутри конкретного объекта `GMROI`.

---

# 3. Загрузка CSV

```python
return pd.read_csv(file_path)
```

`pandas` читает CSV и возвращает `DataFrame`.

Если файла нет:

```python
except FileNotFoundError:
    raise
```

Если возникла другая ошибка:

```python
raise RuntimeError(...) from error
```

---

# 4. Проверка группировки

Разрешены:

```python
["week"]
["week", "seller_id"]
["week", "category_id"]
```

Любой другой вариант вызывает:

```python
ValueError
```

Это требуется документацией метода.

---

# 5. Объединение товаров и продаж

```python
data = products.merge(
    sales,
    on=["week", "seller_id", "product_id"],
    how="inner",
)
```

После merge строка содержит:

- цену;
- себестоимость;
- категорию;
- проданное количество;
- логистические расходы.

---

# 6. Присоединение остатков

```python
data = data.merge(
    stocks,
    on=["week", "seller_id", "product_id"],
    how="inner",
    suffixes=("_sales", "_stocks"),
)
```

И в `sales.csv`, и в `stocks.csv` есть колонка `qty`.

После merge они становятся:

```text
qty_sales
qty_stocks
```

---

# 7. Расчёт маржи

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

# 8. Стоимость запаса

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

# 9. Хранение

```python
data["storage_cost"] = (
    data["qty_stocks"]
    * data["unit_storage_cost"]
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

# 10. Группировка

Для продавцов:

```python
["week", "seller_id"]
```

Для категорий:

```python
["week", "category_id"]
```

`groupby` собирает все товары одной группы.

---

# 11. Суммирование компонентов

```python
.agg(
    margin=("margin", "sum"),
    logistic_costs=("logistic_costs", "sum"),
    avg_inventory_cost=("avg_inventory_cost", "sum"),
    storage_cost=("storage_cost", "sum"),
)
```

Почему используется `sum`?

Потому что продавец или категория состоит из множества товаров.

---

# 12. Расчёт GMROI группы

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

Сначала рассчитывается общая прибыль после расходов, затем она делится на общую стоимость запасов.

---

# 13. Формирование результата

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

Сортировка:

```python
.sort_values(group_columns)
```

Сброс индекса:

```python
.reset_index(drop=True)
```

---

# 14. Расчёт закупок

Сначала выбираются товары KarpovExpress:

```python
self._products_df["seller_id"] == 0
```

Нужны колонки:

```python
[
    "week",
    "product_id",
    "category_id",
    "cost",
]
```

---

# 15. Присоединение закупок

```python
purchases.merge(
    karpov_products,
    on=["week", "product_id"],
    how="inner",
)
```

Теперь у каждой закупки есть:

- категория;
- себестоимость.

---

# 16. Стоимость закупки

```python
purchase_cost = qty * cost
```

Например:

```text
qty = 100
cost = 500
```

\[
100 \times 500 = 50000
\]

---

# 17. Pivot

До преобразования:

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

# 18. Основные ошибки

## Неправильный ключ merge

Нельзя соединять только по `product_id`.

## Перепутать количества

- `qty_sales` — продажи;
- `qty_stocks` — остаток.

## Повторно умножить логистику

`logistic_costs` уже является полной недельной суммой.

## Усреднить GMROI товаров

Нужно делить агрегированные суммы.

## Не отфильтровать продавца 0

Тогда закупки размножатся.

## Не округлить результат

Колонка `gmroi` должна быть округлена до двух знаков.

---

# 19. Запуск

Положите рядом:

```text
solution.py
products.csv
sales.csv
stocks.csv
purchases.csv
```

Запустите:

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

На проверку загружается только `solution.py`.

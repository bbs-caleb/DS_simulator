# Page 3 — GMROI Optimization: готовое решение

## Что загрузить на платформу

Нужно загрузить только:

```text
solution.py
```

Файл находится рядом с этим документом.

---

# Что делает решение

## `_load_csv`

```python
pd.read_csv(file_path)
```

- корректно читает CSV;
- сохраняет `FileNotFoundError`;
- остальные ошибки превращает в `RuntimeError`.

## `_process_gmroi`

1. Проверяет список колонок группировки.
2. Объединяет товары и продажи.
3. Присоединяет остатки.
4. Различает:
   - `qty_sales`;
   - `qty_stocks`.
5. Рассчитывает:
   - `margin`;
   - `avg_inventory_cost`;
   - `storage_cost`.
6. Суммирует компоненты по группе.
7. Рассчитывает GMROI.
8. Округляет до двух знаков.
9. Возвращает только нужные колонки.
10. Сортирует результат.

## `_process_purchases`

1. Выбирает товары продавца `0`.
2. Присоединяет категорию и себестоимость к закупкам.
3. Рассчитывает `purchase_cost`.
4. Суммирует по неделе и категории.
5. Преобразует категории в отдельные столбцы.
6. Сортирует недели.

---

# Точный API

```python
gmroi = GMROI(
    "products.csv",
    "sales.csv",
    "stocks.csv",
    "purchases.csv",
)
```

Итоговые таблицы:

```python
gmroi.seller_gmroi
gmroi.category_gmroi
gmroi.purchases
```

Форматы:

```text
seller_gmroi:
week | seller_id | gmroi

category_gmroi:
week | category_id | gmroi

purchases:
week | category columns
```

---

# Почему решение минимальное

Использованы только базовые операции pandas:

- `read_csv`;
- `merge`;
- `groupby`;
- `agg`;
- `pivot`;
- `sort_values`;
- `reset_index`.

В коде нет ручных циклов, лишних зависимостей и изменения API.

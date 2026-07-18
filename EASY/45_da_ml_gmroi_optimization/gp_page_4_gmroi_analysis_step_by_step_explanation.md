# Page 4 — Анализ GMROI: пошаговое объяснение с нуля

# 1. Какие данные уже есть

После создания объекта:

```python
gmroi = GMROI(
    "products.csv",
    "sales.csv",
    "stocks.csv",
    "purchases.csv",
)
```

доступны:

```python
gmroi.seller_gmroi
gmroi.category_gmroi
gmroi.purchases
```

---

# 2. График продавцов

Минимальный код:

```python
import matplotlib.pyplot as plt


for seller_id, seller_data in (
    gmroi.seller_gmroi.groupby("seller_id")
):
    plt.plot(
        seller_data["week"],
        seller_data["gmroi"],
        label=f"Seller {seller_id}",
    )

plt.xlabel("Week")
plt.ylabel("GMROI")
plt.title("Weekly GMROI by Seller")
plt.legend()
plt.show()
```

## Как читать график

Каждая линия — отдельный продавец.

Нужно смотреть:

- какая линия почти всегда выше;
- какая почти всегда ниже;
- пересекаются ли линии;
- как выглядят начало и конец года.

---

# 3. Что видно по продавцам

## Продавец 0

Это KarpovExpress.

Его линия находится выше остальных почти весь год.

Средний GMROI:

```text
около 1.53
```

## Продавец 1

Лучший внешний продавец.

Средний GMROI:

```text
около 1.33
```

## Продавец 2

Худший продавец.

Средний GMROI:

```text
около 1.14
```

## Продавцы 3 и 4

Находятся между продавцами 1 и 2.

---

# 4. Проверка начала и конца года

Для каждого продавца можно выполнить:

```python
seller_summary = (
    gmroi.seller_gmroi
    .groupby("seller_id")
    .agg(
        start_gmroi=("gmroi", "first"),
        end_gmroi=("gmroi", "last"),
    )
)

seller_summary["change"] = (
    seller_summary["end_gmroi"]
    - seller_summary["start_gmroi"]
)
```

У всех продавцов `change > 0`.

Следовательно, конечное значение выше начального.

---

# 5. Почему утверждение про 1.5 неверно

Последняя неделя:

```text
seller 0 -> 1.57
seller 1 -> 1.37
seller 2 -> 1.16
seller 3 -> 1.24
seller 4 -> 1.21
```

Только продавец `0` выше `1.5`.

---

# 6. График категорий

```python
for category_id, category_data in (
    gmroi.category_gmroi.groupby("category_id")
):
    plt.plot(
        category_data["week"],
        category_data["gmroi"],
        label=f"Category {category_id}",
    )

plt.xlabel("Week")
plt.ylabel("GMROI")
plt.title("Weekly GMROI by Category")
plt.legend()
plt.show()
```

---

# 7. Как определить лучшие и худшие категории

Одного графика иногда недостаточно, поэтому полезно рассчитать средние:

```python
category_average = (
    gmroi.category_gmroi
    .groupby("category_id", as_index=False)["gmroi"]
    .mean()
    .sort_values("gmroi")
)
```

## Нижняя группа

```text
2, 7, 4
```

Именно эти категории имеют самые низкие средние значения.

В утверждении порядок записан как:

```text
2, 4, 7
```

Порядок внутри группы неважен. Это те же три категории.

## Верхняя группа

```text
9, 1, 10, 5, 6, 8
```

В задании они перечислены в числовом порядке:

```text
1, 5, 6, 8, 9, 10
```

---

# 8. Почему категория 3 не входит в лучшие

Категория `3` показывает средний GMROI около:

```text
1.20
```

Она лучше слабых категорий `2`, `4`, `7`, но заметно ниже сильной группы.

Поэтому это промежуточная категория.

---

# 9. Проверка изменения всех категорий

```python
category_summary = (
    gmroi.category_gmroi
    .groupby("category_id")
    .agg(
        start_gmroi=("gmroi", "first"),
        end_gmroi=("gmroi", "last"),
    )
)

category_summary["change"] = (
    category_summary["end_gmroi"]
    - category_summary["start_gmroi"]
)
```

У всех категорий `change > 0`.

Следовательно, утверждение о более высоком GMROI на конец года верно.

---

# 10. Определение закупаемых категорий

В `purchases` категория уже представлена отдельным столбцом.

Колонки:

```text
week, 1, 3, 5, 8, 9
```

Следовательно, KarpovExpress закупает:

```text
1, 3, 5, 8, 9
```

---

# 11. Почему среди закупаемых категорий есть аутсайдер

Средние значения приблизительно:

```text
category 1 -> 1.32
category 3 -> 1.20
category 5 -> 1.30
category 8 -> 1.27
category 9 -> 1.33
```

Категория `3` заметно ниже остальных.

Поэтому аутсайдера выделить можно.

---

# 12. Почему приоритетного продавца выделить можно

Если анализировать внешних продавцов:

```text
seller 1 -> около 1.33
seller 3 -> около 1.21
seller 4 -> около 1.19
seller 2 -> около 1.14
```

Продавец `1` явно лидирует.

Но в настоящем бизнесе одного GMROI недостаточно. Перед продвижением нужно дополнительно проверить:

- абсолютную прибыль;
- число заказов;
- возвраты;
- наличие;
- рейтинг;
- скорость доставки;
- способность увеличить запас.

---

# 13. Финальный набор чекбоксов

```text
✓ 1
✓ 2
✓ 3
✗ 4
✓ 5
✗ 6
✓ 7
✗ 8
✗ 9
✓ 10
```

# Page 5 — Анализ стратегии закупок 1: готовое решение

## Файл для загрузки

На платформу нужно загрузить:

```text
solution.py
```

Файл содержит оба обязательных класса:

```python
GMROI
CategoryImpactEval
```

---

# Проверенный результат

```python
{
    "r2_score": 0.0402,
    "coeffs": {
        1: -0.002,
        3: -0.0017,
        5: 0.0038,
        8: -0.0001,
        9: -0.0051,
        "intercept": 1.5267,
    },
}
```

Результат полностью совпадает с примером задания.

---

# Логика `CategoryImpactEval.__init__`

Сначала выполняется родительский класс:

```python
super().__init__(
    products_path,
    sales_path,
    stocks_path,
    purchases_path,
)
```

Затем выбирается GMROI продавца `0`:

```python
ke_gmroi = self.seller_gmroi.loc[
    self.seller_gmroi["seller_id"] == 0,
    ["week", "gmroi"],
]
```

После этого закупки объединяются с GMROI:

```python
self._eval_data = self.purchases.merge(
    ke_gmroi,
    on="week",
    how="inner",
)
```

Если таблица пустая:

```python
raise ValueError(
    "DataFrame for evaluation is empty."
)
```

---

# Логика `lin_reg_evaluate`

## Признаки

Все колонки, кроме:

```text
week
gmroi
```

## Цель

```python
target = self._eval_data["gmroi"]
```

## Стандартизация

```python
scaled_features = scaler.fit_transform(features)
```

## Обучение

```python
model.fit(scaled_features, target)
```

## Прогноз

```python
predictions = model.predict(scaled_features)
```

## R²

```python
r2_score(target, predictions)
```

## Коэффициенты

Коэффициенты связываются с именами категорий через `zip`.

## Округление

R², коэффициенты и intercept округляются до четырёх знаков.

---

# Почему решение соответствует API

Сохранены:

- класс `GMROI`;
- класс `CategoryImpactEval`;
- наследование;
- четыре аргумента конструктора;
- атрибут `_eval_data`;
- метод `lin_reg_evaluate`;
- структура возвращаемого словаря.

Итоговый формат:

```python
{
    "r2_score": float,
    "coeffs": {
        category_id: float,
        "intercept": float,
    },
}
```

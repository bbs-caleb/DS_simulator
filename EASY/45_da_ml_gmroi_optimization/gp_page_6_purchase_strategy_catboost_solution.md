# Page 6 — Анализ стратегии закупок 2: готовое решение

## Файл для загрузки

На платформу нужно загрузить:

```text
solution.py
```

Файл содержит:

```python
GMROI
CategoryImpactEval
```

В `CategoryImpactEval` сохранён метод:

```python
lin_reg_evaluate
```

и добавлен новый метод:

```python
gb_evaluate
```

---

# Проверенный результат

```python
{
    "r2_score": 0.9998,
    "feature_importances": {
        8: 23.2793,
        9: 22.1107,
        3: 18.8606,
        1: 18.7533,
        5: 16.9962,
    },
}
```

Результат полностью совпадает с эталоном задания.

---

# Реализация `gb_evaluate`

```python
def gb_evaluate(self) -> dict:
    feature_columns = [
        column
        for column in self._eval_data.columns
        if column not in ["week", "gmroi"]
    ]

    features = self._eval_data[feature_columns]
    target = self._eval_data["gmroi"]

    model = CatBoostRegressor(
        random_seed=42,
        verbose=False,
    )
    model.fit(features, target)

    predictions = model.predict(features)

    importances = {
        column: round(float(importance), 4)
        for column, importance in zip(
            feature_columns,
            model.feature_importances_,
        )
    }
    sorted_importances = dict(
        sorted(
            importances.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    )

    return {
        "r2_score": round(
            float(r2_score(target, predictions)),
            4,
        ),
        "feature_importances": sorted_importances,
    }
```

---

# Почему решение соответствует требованиям

## CatBoostRegressor

Используется:

```python
CatBoostRegressor
```

## Параметры по умолчанию

Не меняются:

- глубина;
- learning rate;
- iterations;
- loss function;
- регуляризация.

Добавлены только:

```python
random_seed=42
verbose=False
```

`verbose=False` отключает вывод обучения и не меняет математическую логику.

## R²

Рассчитывается через:

```python
r2_score(target, predictions)
```

## Feature importance

Получается через:

```python
model.feature_importances_
```

## Сортировка

Важности сортируются по убыванию.

## Округление

R² и importance округляются до четырёх знаков.

---

# Формат результата

```python
{
    "r2_score": float,
    "feature_importances": {
        category_id: float,
    },
}
```

Имена категорий остаются целыми числами.

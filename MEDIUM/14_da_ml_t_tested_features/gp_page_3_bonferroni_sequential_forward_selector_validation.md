# Page 3 — Bonferroni SFS: валидация и граничные случаи

## 1. Что должен проверить API-тест

Конструктор:

```python
selector = SequentialForwardSelector(
    model=model,
    cv=cv,
    max_features=10,
    verbose=0,
    alpha=0.05,
    bonferroni=True,
)
```

Обязательные атрибуты:

```python
selector.model
selector.cv
selector.max_features
selector.verbose
selector.alpha
selector.bonferroni
selector.n_features_
selector.selected_features_
```

---

# 2. Проверка новых параметров

```python
assert selector.alpha == 0.05
assert selector.bonferroni is True
```

Отдельно:

```python
selector_without_correction = (
    SequentialForwardSelector(
        model,
        cv,
        bonferroni=False,
    )
)

assert (
    selector_without_correction.bonferroni
    is False
)
```

---

# 3. Проверка threshold

При:

```text
alpha = 0.05
excluded = 50
```

ожидается:

```text
0.001
```

После одного выбранного признака:

```text
alpha = 0.05
excluded = 49
```

ожидается:

```text
0.001020408...
```

Значит denominator меняется на каждой внешней итерации.

---

# 4. Проверка режима без поправки

При:

```python
bonferroni=False
```

на каждой итерации:

```python
corrected_alpha == self.alpha
```

Количество excluded не должно влиять на threshold.

---

# 5. Проверка transform

После fit:

```python
X_selected = selector.transform(X)
```

Должно быть:

```python
np.testing.assert_array_equal(
    X_selected,
    X[:, selector.selected_features_],
)
```

---

# 6. Проверка числа колонок

```python
assert X_selected.shape[0] == X.shape[0]

assert X_selected.shape[1] == (
    selector.n_selected_features_
)
```

---

# 7. Проверка сортировки

```python
assert selector.selected_features_ == sorted(
    selector.selected_features_
)
```

---

# 8. Проверка уникальности

```python
assert len(selector.selected_features_) == len(
    set(selector.selected_features_)
)
```

---

# 9. Проверка верхней границы

```python
assert selector.n_selected_features_ <= (
    selector.max_features
)
```

И:

```python
assert selector.n_selected_features_ <= (
    X.shape[1]
)
```

---

# 10. Граничный случай: max_features больше n_features

Используется:

```python
min(self.max_features, self.n_features_)
```

Поэтому выход за число колонок невозможен.

---

# 11. Граничный случай: max_features = 0

Внешний цикл не запускается.

После fit:

```python
selected_features_ == []
```

---

# 12. Граничный случай: ноль колонок

Если:

```python
X.shape == (n_samples, 0)
```

то:

```python
features_to_select == 0
```

Деления на `len(excluded_features)` не происходит, потому что цикл не запускается.

---

# 13. Граничный случай: ни один кандидат не прошёл

```python
significant_candidates == []
```

Выполняется:

```python
break
```

Это корректный результат, а не ошибка.

---

# 14. Граничный случай: p-value равен threshold

Условие строгое:

```python
p_value < corrected_alpha
```

При равенстве кандидат не проходит.

---

# 15. Граничный случай: p-value равен NaN

Такое возможно при нулевой дисперсии парных разностей.

Сравнение:

```python
np.nan < corrected_alpha
```

возвращает `False`.

Кандидат не будет добавлен.

---

# 16. Типичная ошибка: неправильный denominator

Неправильно:

```python
self.alpha / self.n_features_
```

Правильно:

```python
self.alpha / len(excluded_features)
```

Причина:

```text
на каждой итерации тестируются только
ещё не выбранные признаки
```

---

# 17. Типичная ошибка: corrected_alpha вне цикла

Неправильно:

```python
corrected_alpha = (
    self.alpha / len(excluded_features)
)

for ...:
    ...
```

Размер excluded далее меняется, но threshold остаётся старым.

Правильно вычислять внутри внешнего цикла.

---

# 18. Типичная ошибка: делить alpha после каждого кандидата

Внутри одной итерации семейство гипотез фиксировано.

Все кандидаты текущего шага должны сравниваться с одинаковым threshold.

---

# 19. Типичная ошибка: сравнить только средние

Page 3 сохраняет t-test из page 2.

Недостаточно:

```python
candidate_scores.mean() > (
    current_scores.mean()
)
```

Нужно:

```python
_, p_value = ttest_rel(
    candidate_scores,
    current_scores,
    alternative="greater",
)
```

---

# 20. Типичная ошибка: независимый t-test

Нельзя использовать:

```python
ttest_ind
```

CV scores связаны одинаковыми folds.

Нужен:

```python
ttest_rel
```

---

# 21. Типичная ошибка: перепутать направление

Правильно:

```python
ttest_rel(
    candidate_scores,
    current_scores,
    alternative="greater",
)
```

Проверяется:

```text
candidate > current
```

---

# 22. Типичная ошибка: выбрать минимальный p-value

После статистического фильтра SFS выбирает максимальное среднее качество.

Правильно:

```python
max(
    significant_candidates,
    key=lambda result: result[1].mean(),
)
```

---

# 23. Типичная ошибка: добавить всех прошедших

Одна итерация SFS добавляет один признак.

Остальные кандидаты должны быть переоценены после изменения текущего набора.

---

# 24. Типичная ошибка: не обновить current_scores

После выбора:

```python
current_scores = best_scores
```

Иначе каждый следующий кандидат будет сравниваться с устаревшей моделью.

---

# 25. Минимальный API smoke test

```python
model = LinearRegression()

cv = RepeatedKFold(
    n_splits=3,
    n_repeats=2,
    random_state=42,
)

selector = SequentialForwardSelector(
    model,
    cv,
    max_features=3,
    verbose=0,
    alpha=0.05,
    bonferroni=True,
)

assert selector.model is model
assert selector.cv is cv
assert selector.max_features == 3
assert selector.verbose == 0
assert selector.alpha == 0.05
assert selector.bonferroni is True
assert selector.n_features_ is None
assert selector.selected_features_ is None
```

---

# 26. Минимальный функциональный smoke test

```python
X, y = generate_dataset(
    n_samples=1000,
    n_features=10,
    n_informative=3,
    random_state=42,
)

selector.fit(X, y)

assert selector.n_features_ == 10
assert isinstance(
    selector.selected_features_,
    list,
)

assert selector.n_selected_features_ == len(
    selector.selected_features_
)

assert selector.n_selected_features_ <= 3
```

---

# 27. Финальный checklist перед загрузкой

```text
[ ] файл называется gp_page_3_...
[ ] класс называется SequentialForwardSelector
[ ] __init__ принимает alpha
[ ] __init__ принимает bonferroni
[ ] есть self.alpha
[ ] есть self.bonferroni
[ ] baseline = DummyRegressor
[ ] используется cross_val_score
[ ] используется ttest_rel
[ ] alternative="greater"
[ ] corrected_alpha зависит от len(excluded)
[ ] corrected_alpha пересчитывается на каждом шаге
[ ] bonferroni=False оставляет обычный alpha
[ ] среди прошедших выбирается max mean R²
[ ] current_scores обновляется
[ ] selected_features_ сортируется
[ ] transform использует selected_features_
[ ] n_selected_features_ — property
```

---

# 28. Файл для отправки

```text
gp_page_3_bonferroni_sequential_forward_selector_solution.py
```

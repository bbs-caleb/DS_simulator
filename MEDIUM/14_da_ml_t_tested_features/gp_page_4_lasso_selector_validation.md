# Page 4 — LassoSelector: валидация и типичные ошибки

## 1. Проверка шаблона

В загруженном шаблоне ожидается класс:

```python
LassoSelector
```

Сигнатура конструктора:

```python
def __init__(
    self,
    cv,
    alphas,
    random_state=42,
):
```

Нельзя добавлять обязательные аргументы.

---

# 2. API конструктора

После:

```python
selector = LassoSelector(
    cv,
    alphas=[2, 10],
    random_state=42,
)
```

должны существовать:

```python
selector.cv
selector.alphas
selector.random_state
selector.n_features_
selector.selected_features_
```

До fit:

```python
assert selector.n_features_ is None
assert selector.selected_features_ is None
```

---

# 3. API fit

После:

```python
selector.fit(X, y)
```

проверяем:

```python
assert selector.n_features_ == X.shape[1]

assert isinstance(
    selector.selected_features_,
    list,
)
```

Метод по шаблону возвращает `None`.

---

# 4. API property

```python
assert selector.n_selected_features_ == len(
    selector.selected_features_
)
```

Это должно быть свойство:

```python
selector.n_selected_features_
```

Неправильно:

```python
selector.n_selected_features_()
```

---

# 5. API transform

```python
X_selected = selector.transform(X)
```

Проверка:

```python
np.testing.assert_array_equal(
    X_selected,
    X[:, selector.selected_features_],
)
```

---

# 6. Проверка числа строк

```python
assert X_selected.shape[0] == X.shape[0]
```

Feature selection не удаляет наблюдения.

---

# 7. Проверка числа колонок

```python
assert X_selected.shape[1] == (
    selector.n_selected_features_
)
```

---

# 8. Проверка порядка индексов

```python
assert selector.selected_features_ == sorted(
    selector.selected_features_
)
```

`np.where` возвращает индексы по возрастанию.

---

# 9. Проверка уникальности

```python
assert len(selector.selected_features_) == len(
    set(selector.selected_features_)
)
```

Каждый коэффициент соответствует одной колонке, поэтому дублей нет.

---

# 10. Контрольный пример из задания

Параметры:

```text
random_state = 42
n_samples = 10 000
n_features = 50
n_informative = 5
n_splits = 3
n_repeats = 10
alphas = [2, 10]
```

В текущем окружении получено:

```python
selected_features_ == [
    5,
    6,
    8,
    14,
    24,
    29,
    41,
    45,
]
```

Количество:

```python
n_selected_features_ == 8
```

Lasso оставила пять сильных информативных признаков и несколько слабых ненулевых коэффициентов при выбранном `alpha=2`.

Скрытый grader может использовать другие `random_state`, `alphas` и размеры датасета, поэтому код не должен хардкодить этот список.

---

# 11. Контроль random_state = 69

При тех же остальных параметрах:

```python
selected_features_ == [
    17,
    20,
    26,
    44,
    46,
]
```

Количество:

```python
5
```

Это совпадает с пятью информативными признаками конкретного синтетического датасета.

---

# 12. Граничный случай: все коэффициенты нулевые

При очень сильной регуляризации может получиться:

```python
selected_features_ == []
```

Тогда:

```python
n_selected_features_ == 0
```

А:

```python
transform(X).shape
```

будет:

```text
(n_samples, 0)
```

Это корректно.

---

# 13. Граничный случай: все коэффициенты ненулевые

При слабой регуляризации:

```python
selected_features_ == list(
    range(X.shape[1])
)
```

Тогда transform вернёт все колонки.

---

# 14. Повторный fit

Метод повторно записывает:

```python
self.n_features_
self.selected_features_
```

Поэтому старое состояние заменяется новым.

---

# 15. Ошибка: использовать обычный Lasso

Неправильно:

```python
Lasso(alpha=self.alphas)
```

`alphas` — список, а задание требует `LassoCV`.

Правильно:

```python
LassoCV(
    alphas=self.alphas,
    cv=self.cv,
)
```

---

# 16. Ошибка: выбрать alpha вручную

Нельзя писать:

```python
alpha = self.alphas[0]
```

Задача `LassoCV` — выбрать alpha через CV.

---

# 17. Ошибка: забыть передать alphas

Если не передать список, LassoCV создаст собственную сетку.

Hidden tests ожидают использование аргумента класса.

---

# 18. Ошибка: забыть передать cv

Нельзя позволять LassoCV использовать default CV, когда объект `cv` был передан selector.

---

# 19. Ошибка: не сохранить random_state

API-тест может проверить:

```python
selector.random_state
```

---

# 20. Ошибка: считать selected по знаку

Неправильно:

```python
model.coef_ > 0
```

Отрицательный коэффициент тоже является выбранным.

Правильно:

```python
model.coef_ != 0
```

---

# 21. Ошибка: использовать только положительные коэффициенты

Пример:

```python
coef = -15
```

Признак оказывает отрицательное влияние, но остаётся полезным для предсказания.

Он должен быть выбран.

---

# 22. Ошибка: вернуть boolean mask

Неправильно:

```python
self.selected_features_ = (
    model.coef_ != 0
)
```

API ожидает список индексов:

```python
[2, 4, 7]
```

---

# 23. Ошибка: оставить NumPy array

Неправильно:

```python
np.where(...)[0]
```

Это `np.ndarray`.

Правильно:

```python
np.where(...)[0].tolist()
```

---

# 24. Ошибка: использовать coef_ до fit

До:

```python
model.fit(X, y)
```

атрибут `coef_` ещё не рассчитан.

---

# 25. Ошибка: property возвращает n_features_

Неправильно:

```python
return self.n_features_
```

Нужно:

```python
return len(self.selected_features_)
```

---

# 26. Ошибка: transform использует исходное число

Неправильно:

```python
X[:, :self.n_selected_features_]
```

Выбранные признаки не обязаны быть первыми колонками.

Правильно:

```python
X[:, self.selected_features_]
```

---

# 27. Ошибка: обязательная стандартизация в учебном решении

В production стандартизация важна.

Но в текущем задании она прямо объявлена ненужной.

Добавление Pipeline может изменить структуру и усложнить hidden tests.

---

# 28. Ошибка: случайный epsilon

Не нужно писать:

```python
np.abs(model.coef_) > 1e-5
```

Это меняет определение выбранного признака.

Условие ожидает ненулевой коэффициент.

---

# 29. Минимальный smoke test

```python
model_cv = RepeatedKFold(
    n_splits=3,
    n_repeats=2,
    random_state=42,
)

selector = LassoSelector(
    model_cv,
    alphas=[2, 10],
    random_state=42,
)

assert selector.cv is model_cv
assert selector.alphas == [2, 10]
assert selector.random_state == 42
assert selector.n_features_ is None
assert selector.selected_features_ is None
```

---

# 30. Функциональный smoke test

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
```

---

# 31. Финальный checklist

```text
[ ] импортирован LassoCV
[ ] конструктор принимает cv
[ ] конструктор принимает alphas
[ ] конструктор принимает random_state
[ ] сохранён self.cv
[ ] сохранён self.alphas
[ ] сохранён self.random_state
[ ] n_features_ до fit равен None
[ ] selected_features_ до fit равен None
[ ] fit сохраняет X.shape[1]
[ ] LassoCV получает self.cv
[ ] LassoCV получает self.alphas
[ ] LassoCV получает self.random_state
[ ] model.fit вызывается до coef_
[ ] берутся все coef_ != 0
[ ] индексы превращаются в list
[ ] transform использует selected_features_
[ ] n_selected_features_ является property
```

---

# 32. Файл для загрузки

```text
gp_page_4_lasso_selector_solution.py
```

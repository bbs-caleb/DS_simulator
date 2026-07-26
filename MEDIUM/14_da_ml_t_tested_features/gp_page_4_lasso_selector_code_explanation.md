# Page 4 — LassoSelector: максимально подробное объяснение кода

## 1. Что требуется реализовать

Нужен класс:

```python
LassoSelector
```

Он должен:

1. получить CV-схему;
2. получить список `alphas`;
3. получить `random_state`;
4. обучить `LassoCV`;
5. найти ненулевые коэффициенты;
6. сохранить индексы соответствующих признаков;
7. уметь трансформировать `X`;
8. вычислять число выбранных признаков через property.

---

# 2. Импорт Tuple

```python
from typing import Tuple
```

Он используется только в type hint:

```python
def generate_dataset(...) -> Tuple:
```

Функция возвращает:

```python
X, y
```

---

# 3. Импорт NumPy

```python
import numpy as np
```

NumPy нужен для:

- типа `np.ndarray`;
- поиска ненулевых коэффициентов;
- среза матрицы;
- преобразования индексов.

---

# 4. Импорт LassoCV

```python
from sklearn.linear_model import LassoCV
```

`LassoCV`:

1. обучает Lasso;
2. перебирает переданные `alpha`;
3. оценивает их через CV;
4. выбирает лучший вариант;
5. после fit хранит коэффициенты в `coef_`.

---

# 5. Конструктор

```python
def __init__(
    self,
    cv,
    alphas,
    random_state=42,
):
```

## `cv`

Объект схемы кросс-валидации.

Например:

```python
RepeatedKFold(
    n_splits=3,
    n_repeats=10,
    random_state=42,
)
```

## `alphas`

Список кандидатов:

```python
[2, 10]
```

Важно не путать его с `alpha` t-теста на предыдущих страницах.

Здесь `alpha` — сила L1-регуляризации Lasso.

## `random_state`

Параметр воспроизводимости.

---

# 6. Сохранение параметров

```python
self.cv = cv
self.alphas = alphas
self.random_state = random_state
```

Почему нужен `self`?

После завершения `__init__` локальные переменные исчезают.

Атрибуты объекта остаются доступны:

```python
selector.cv
selector.alphas
selector.random_state
```

---

# 7. Атрибуты, которые появятся после fit

```python
self.n_features_ = None
self.selected_features_ = None
```

Символ `_` в конце имени соответствует sklearn-конвенции:

```text
значение вычисляется в результате fit
```

Это не private attribute.

Private convention обычно выглядит так:

```python
_name
```

Здесь:

```python
name_
```

означает fitted attribute.

---

# 8. Метод fit

```python
def fit(
    self,
    X: np.ndarray,
    y: np.ndarray,
) -> None:
```

`X` — матрица признаков.

`y` — таргет.

По шаблону метод возвращает:

```python
None
```

Поэтому в конце нет:

```python
return self
```

Хотя многие sklearn-классы возвращают `self`, здесь нужно сохранять API задания.

---

# 9. Число входных признаков

```python
self.n_features_ = X.shape[1]
```

Если:

```python
X.shape == (10000, 50)
```

то:

```python
self.n_features_ == 50
```

---

# 10. Создание LassoCV

```python
model = LassoCV(
    cv=self.cv,
    alphas=self.alphas,
    random_state=self.random_state,
    n_jobs=-1,
)
```

Разберём каждый аргумент.

## `cv=self.cv`

Используется схема, переданная пользователем класса.

Нельзя создавать внутри новый случайный KFold, потому что grader ожидает использование аргумента.

## `alphas=self.alphas`

Передаётся список значений регуляризации.

LassoCV сама выберет лучший вариант.

## `random_state=self.random_state`

Сохраняется воспроизводимость там, где алгоритм использует случайность.

## `n_jobs=-1`

Разрешает использовать доступные CPU cores.

Это не меняет математическую логику.

---

# 11. Обучение

```python
model.fit(X, y)
```

После fit объект содержит:

```python
model.coef_
```

Это NumPy-массив длиной:

```python
X.shape[1]
```

Пример:

```python
array([
    0.0,
    0.0,
    15.3,
    0.0,
    -8.7,
])
```

---

# 12. Поиск ненулевых коэффициентов

```python
model.coef_ != 0
```

Для массива:

```python
[0.0, 0.0, 15.3, 0.0, -8.7]
```

результат:

```python
[False, False, True, False, True]
```

---

# 13. np.where

```python
np.where(model.coef_ != 0)
```

`np.where` возвращает tuple с массивом индексов.

Для примера:

```python
(array([2, 4]),)
```

Поэтому берём первый элемент:

```python
np.where(model.coef_ != 0)[0]
```

Получаем:

```python
array([2, 4])
```

---

# 14. Преобразование в list

```python
.tolist()
```

Нужно, потому что API ожидает:

```python
List[int]
```

а не NumPy array.

Итог:

```python
self.selected_features_ = (
    np.where(model.coef_ != 0)[0].tolist()
)
```

---

# 15. Почему список уже отсортирован

`np.where` возвращает индексы в порядке обхода массива:

```text
слева направо
```

Поэтому список автоматически упорядочен:

```python
[2, 4, 9, 15]
```

Отдельный `sorted` не требуется.

---

# 16. Метод transform

```python
def transform(
    self,
    X: np.ndarray,
) -> np.ndarray:
```

Он получает исходную или новую матрицу с теми же колонками.

---

# 17. Проверка fit

```python
assert self.selected_features_ is not None, (
    "Fit the model first"
)
```

До fit:

```python
selected_features_ is None
```

После fit:

```python
selected_features_ is list
```

Даже если Lasso не выбрала ни одной колонки, будет:

```python
[]
```

Это отличается от `None`.

---

# 18. NumPy-срез

```python
return X[:, self.selected_features_]
```

Первая часть:

```python
:
```

означает:

```text
взять все строки
```

Вторая часть:

```python
self.selected_features_
```

означает:

```text
взять выбранные колонки
```

Если:

```python
selected_features_ == [2, 4]
```

возвращаются только третья и пятая колонки.

---

# 19. Property

```python
@property
def n_selected_features_(self):
```

Благодаря декоратору обращение выглядит:

```python
selector.n_selected_features_
```

а не:

```python
selector.n_selected_features_()
```

---

# 20. Вычисление на лету

```python
return len(self.selected_features_)
```

Отдельно хранить число не нужно.

Преимущество:

```text
значение не может рассинхронизироваться со списком
```

---

# 21. Почему проверяется selected_features_, а не n_features_

```python
assert self.selected_features_ is not None
```

Именно этот атрибут необходим для подсчёта.

`n_features_` показывает исходное число колонок, но не доказывает, что список selected готов.

---

# 22. Что происходит в run

```python
alphas = [2, 10]
```

LassoCV сравнивает два уровня регуляризации.

---

```python
selector = LassoSelector(
    cv,
    alphas,
    random_state,
)
```

Создаётся selector.

---

```python
selector.fit(X, y)
```

Обучается LassoCV и заполняются fitted attributes.

---

```python
selector.selected_features_
```

Показывает индексы выбранных признаков.

---

```python
selector.n_selected_features_
```

Показывает их количество.

---

# 23. Полный алгоритм в пяти строках

```text
n_features_ = число колонок X

model = LassoCV(...)

model.fit(X, y)

selected_features_ =
    индексы ненулевых model.coef_

transform =
    X только с selected_features_
```

---

# 24. Почему не сохраняем model

Задание требует только три fitted attributes:

```python
n_features_
selected_features_
n_selected_features_
```

Для прохождения текущего API хранить:

```python
self.model_
```

не требуется.

Минимальное решение не добавляет лишнюю публичную поверхность.

---

# 25. Почему не делаем стандартизацию

Условие прямо говорит, что признаки имеют одинаковые `mean` и `std`.

Поэтому добавление scaler:

- не требуется;
- изменит код шаблона;
- усложнит grader compatibility.

Для production-данных scaler обычно нужен.

---

# 26. Почему не используем маленький epsilon

В задании отбор сформулирован так:

```text
коэффициент не равен нулю
```

Поэтому используется:

```python
model.coef_ != 0
```

а не:

```python
abs(model.coef_) > 1e-6
```

Lasso вычисляет sparse coefficients и зануляет часть коэффициентов.

Самовольный epsilon может изменить ожидаемые hidden-test результаты.

---

# 27. Минимальность решения

В файл не добавлены:

- pandas;
- StandardScaler;
- Pipeline;
- GridSearchCV;
- отдельная модель после selection;
- дополнительные thresholds;
- логирование;
- custom exceptions;
- дополнительные fitted attributes.

Это снижает риск расхождения с API.

---

# 28. Главная строка

```python
self.selected_features_ = np.where(
    model.coef_ != 0
)[0].tolist()
```

Она превращает результат LassoCV в список выбранных индексов.

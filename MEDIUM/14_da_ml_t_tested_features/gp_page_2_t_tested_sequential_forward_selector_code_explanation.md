# Page 2 — T-Tested SequentialForwardSelector: пошаговое объяснение кода

## 1. Главная причина ошибки grader

Grader написал:

```text
SequentialForwardSelector should have attribute alpha
```

Это означает, что код не дошёл даже до проверки алгоритма.

API-тест создал объект и ожидал найти:

```python
selector.alpha
```

В старом файле такого атрибута не было.

Исправление состоит из двух частей:

```python
alpha: float = 0.05
```

в аргументах конструктора и:

```python
self.alpha = alpha
```

внутри конструктора.

Но `alpha` не должен быть мёртвым параметром. Он используется в решении:

```python
if p_value < self.alpha:
```

---

## 2. Импорты

```python
from typing import Tuple
```

`Tuple` используется в type hint функции `generate_dataset`.

Она возвращает два объекта:

```python
X, y
```

---

```python
import numpy as np
```

NumPy нужен для:

- типа `np.ndarray`;
- матричных срезов;
- хранения данных `X`;
- хранения таргета `y`.

---

```python
from scipy.stats import ttest_rel
```

Это ключевой новый импорт page_2.

`ttest_rel` выполняет парный t-тест.

---

```python
from sklearn.dummy import DummyRegressor
```

`DummyRegressor` создаёт начальный baseline.

Без него на первой итерации не было бы массива `current_scores`.

---

```python
from sklearn.model_selection import cross_val_score
```

Функция:

1. получает model;
2. получает данные;
3. выполняет обучение на каждом CV split;
4. возвращает массив validation scores.

---

## 3. Конструктор

```python
def __init__(
    self,
    model,
    cv,
    max_features: int = 10,
    verbose: int = 0,
    alpha: float = 0.05,
) -> None:
```

### `model`

ML-модель, качество которой оценивается.

В примере:

```python
LinearRegression()
```

### `cv`

Готовая схема разбиения.

В примере:

```python
RepeatedKFold(...)
```

### `max_features`

Верхний предел числа выбранных колонок.

Это не означает, что признаки обязательно будут выбраны до этого количества.

### `verbose`

Управляет печатью прогресса.

### `alpha`

Порог статистической значимости.

---

## 4. Сохранение параметров

```python
self.model = model
self.cv = cv
self.max_features = max_features
self.verbose = verbose
self.alpha = alpha
```

Почему обязательно писать `self.`?

Параметр:

```python
alpha
```

существует только во время выполнения `__init__`.

Атрибут:

```python
self.alpha
```

остаётся внутри объекта после завершения конструктора.

---

## 5. Начальное состояние обучаемых атрибутов

```python
self.n_features_ = None
self.selected_features_ = None
```

До `fit` класс ещё не знает:

- число колонок;
- выбранные признаки.

Поэтому используется `None`.

Это также позволяет отличить:

```text
fit ещё не вызывали
```

от:

```text
fit выполнился, но не выбрал ни одного признака
```

После успешного `fit` второй случай будет представлен пустым списком:

```python
[]
```

---

## 6. Метод fit

```python
def fit(self, X: np.ndarray, y: np.ndarray) -> None:
```

### `X`

Матрица признаков:

```text
число строк × число колонок
```

### `y`

Таргет:

```text
одно значение на каждую строку X
```

---

## 7. Сохраняем число признаков

```python
self.n_features_ = X.shape[1]
```

`X.shape` может выглядеть так:

```python
(10000, 50)
```

Тогда:

```python
X.shape[0] == 10000
X.shape[1] == 50
```

---

## 8. Included и excluded

```python
included_features = []
excluded_features = list(range(self.n_features_))
```

При 5 колонках:

```python
included_features = []
excluded_features = [0, 1, 2, 3, 4]
```

`included_features` — уже выбранные.

`excluded_features` — ещё доступные кандидаты.

---

## 9. Начальные scores

```python
current_scores = cross_val_score(
    DummyRegressor(),
    X,
    y,
    scoring="r2",
    cv=self.cv,
    n_jobs=-1,
)
```

Разберём каждый аргумент.

### `DummyRegressor()`

Baseline без полезных признаков.

### `X`

Передаётся полная матрица, но DummyRegressor не использует её как обычная модель.

### `y`

Истинный таргет.

### `scoring="r2"`

На каждом split считается `R²`.

### `cv=self.cv`

Используется именно переданная схема валидации.

### `n_jobs=-1`

Можно использовать доступные CPU cores.

Результат:

```python
current_scores
```

является массивом, например:

```python
array([
    -0.0012,
    -0.0005,
    ...
])
```

При 30 разбиениях в нём 30 элементов.

---

## 10. Верхняя граница

```python
features_to_select = min(
    self.max_features,
    self.n_features_,
)
```

Если:

```text
max_features = 10
n_features_ = 6
```

делать больше шести попыток бессмысленно.

---

## 11. Внешний цикл

```python
for step in range(features_to_select):
```

Одна итерация — попытка добавить один признак.

Алгоритм может завершиться раньше через:

```python
break
```

---

## 12. Список значимых кандидатов

```python
significant_candidates = []
```

Сюда попадут только кандидаты, у которых:

```python
p_value < self.alpha
```

Каждый элемент хранит:

```python
(candidate, candidate_scores)
```

Например:

```python
(17, array([...30 scores...]))
```

---

## 13. Внутренний цикл

```python
for candidate in excluded_features:
```

Проверяется каждый ещё не выбранный индекс.

---

## 14. Создание временного subset

```python
subset = included_features + [candidate]
```

Пусть:

```python
included_features = [20, 46]
candidate = 17
```

Тогда:

```python
subset = [20, 46, 17]
```

Исходный список не меняется.

---

## 15. CV scores кандидата

```python
candidate_scores = cross_val_score(
    self.model,
    X[:, subset],
    y,
    scoring="r2",
    cv=self.cv,
    n_jobs=-1,
)
```

### `X[:, subset]`

Первая часть `:` означает:

```text
взять все строки
```

Вторая часть `subset` означает:

```text
взять только выбранные колонки
```

---

## 16. Парный односторонний t-тест

```python
_, p_value = ttest_rel(
    candidate_scores,
    current_scores,
    alternative="greater",
)
```

### Почему первый аргумент — candidate

Потому что проверяется гипотеза:

```text
candidate_scores имеют большее среднее,
чем current_scores
```

### Почему `alternative="greater"`

Нас не интересует любое различие.

Нам нужно только улучшение.

### Почему результат распаковывается так

`ttest_rel` возвращает:

```text
t-statistic
p-value
```

T-statistic дальше не нужен, поэтому:

```python
_
```

---

## 17. Проверка alpha

```python
if p_value < self.alpha:
```

Например:

```text
p-value = 0.003
alpha   = 0.05
```

Кандидат проходит.

Если:

```text
p-value = 0.21
```

кандидат не проходит.

---

## 18. Сохранение значимого кандидата

```python
significant_candidates.append(
    (candidate, candidate_scores)
)
```

Мы сохраняем не только индекс.

Scores нужны, чтобы:

- сравнить средние кандидатов;
- после выбора использовать победителя как новый baseline.

---

## 19. Ранняя остановка

```python
if not significant_candidates:
    break
```

Пустой список трактуется как `False`.

Если ни один признак не дал статистически значимого улучшения, дальнейший SFS прекращается.

---

## 20. Выбор лучшего среди значимых

```python
best_feature, best_scores = max(
    significant_candidates,
    key=lambda result: result[1].mean(),
)
```

Разберём структуру `result`:

```python
result[0] — feature index
result[1] — CV scores
```

Ключ сравнения:

```python
result[1].mean()
```

То есть максимальный средний CV `R²`.

---

## 21. Обновление состояния

```python
included_features.append(best_feature)
```

Победитель добавляется.

```python
excluded_features.remove(best_feature)
```

Победитель больше не проверяется.

```python
current_scores = best_scores
```

На следующей итерации новые кандидаты сравниваются уже с улучшенной моделью.

Это критически важно.

Нельзя всегда сравнивать с `DummyRegressor`.

---

## 22. verbose

```python
if self.verbose > 0:
    print(...)
```

На работу алгоритма это не влияет.

---

## 23. Итоговая сортировка

```python
self.selected_features_ = sorted(
    included_features
)
```

Порядок выбора может быть:

```python
[20, 46, 17, 44, 26]
```

Grader ожидает список, упорядоченный по индексу:

```python
[17, 20, 26, 44, 46]
```

---

## 24. transform

```python
assert self.selected_features_ is not None, (
    "Fit the model first"
)
```

Если `fit` не выполнялся, использование transform является ошибкой.

После fit:

```python
return X[:, self.selected_features_]
```

---

## 25. property

```python
@property
def n_selected_features_(self) -> int:
```

Благодаря `@property` обращение выглядит так:

```python
selector.n_selected_features_
```

а не:

```python
selector.n_selected_features_()
```

---

## 26. Человеческий псевдокод

```text
current = DummyRegressor CV scores

пока не достигнут max_features:

    для каждого кандидата:
        new = model CV scores на current features + candidate
        p = paired t-test(new, current)

        если p < alpha:
            кандидат статистически допустим

    если допустимых нет:
        stop

    выбрать допустимого с максимальным mean R²
    сохранить его
    current = его CV scores
```

---

## 27. Самое важное различие

### Неправильный page_2

```python
if best_score > current_score:
```

### Правильный page_2

```python
_, p_value = ttest_rel(
    candidate_scores,
    current_scores,
    alternative="greater",
)

if p_value < self.alpha:
```

На page_2 мы сравниваем не только средние, а парные распределения CV-оценок.

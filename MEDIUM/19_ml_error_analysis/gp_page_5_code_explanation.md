# gp_page_5 — Подробное объяснение решения Residual Fairness

## 1. Что находится в Python-файле

Файл:

```text
gp_page_5_residual_fairness.py
```

содержит две функции:

```python
fairness
best_prediction
```

Первая функция оценивает равномерность распределения ошибок.

Вторая выбирает модель, которая:

- имеет лучший LogLoss;
- не нарушает ограничение по fairness.

---

# 2. Импорты

```python
from typing import List
```

`List` используется в аннотации:

```python
y_preds: List[np.ndarray]
```

Это означает:

```text
y_preds — список NumPy-массивов
```

Каждый массив содержит вероятностные прогнозы одной модели.

---

```python
import numpy as np
```

NumPy используется для:

- преобразования данных в массив;
- модуля;
- среднего;
- попарных разностей;
- логарифма;
- суммирования.

---

```python
from sklearn.metrics import log_loss
```

`log_loss` рассчитывает агрегированный LogLoss модели.

Для бинарной классификации:

```text
LogLoss =
-mean(
    y × log(p)
    + (1 - y) × log(1 - p)
)
```

Чем меньше LogLoss, тем лучше вероятностный прогноз.

---

# 3. Разбор функции `fairness`

## 3.1 Заголовок

```python
def fairness(residuals: np.ndarray) -> float:
```

Функция принимает массив псевдоостатков и возвращает одно число типа `float`.

---

## 3.2 Берём абсолютные значения

```python
absolute_residuals = np.abs(
    np.asarray(residuals, dtype=float)
)
```

### `np.asarray`

Преобразует вход в NumPy-массив.

### `dtype=float`

Гарантирует вещественный тип данных.

### `np.abs`

Берёт модуль каждого значения.

Пример:

```text
[-0.1, -0.7, -0.3]
```

превращается в:

```text
[0.1, 0.7, 0.3]
```

Для Gini важен размер ошибки, а не её знак.

---

## 3.3 Проверка пустого массива

```python
if absolute_residuals.size == 0:
    raise ValueError("residuals must not be empty")
```

Для пустого массива невозможно вычислить:

- среднее;
- Gini;
- fairness.

Поэтому функция явно сообщает об ошибке.

---

## 3.4 Среднее значение

```python
mean_residual = np.mean(absolute_residuals)
```

Это средний размер псевдоостатка.

Он входит в знаменатель формулы Gini.

---

## 3.5 Все ошибки равны нулю

```python
if mean_residual == 0:
    return 1.0
```

Если среднее абсолютное значение равно нулю, все остатки равны нулю.

Это идеальная ситуация:

```text
ошибок нет вообще
```

Ошибки распределены максимально равномерно, поэтому:

```text
fairness = 1
```

Эта проверка также защищает от деления на ноль.

---

## 3.6 Матрица попарных различий

```python
pairwise_differences = np.abs(
    absolute_residuals[:, None]
    - absolute_residuals[None, :]
)
```

Это самая непривычная часть кода.

Пусть:

```python
absolute_residuals = np.array([1, 2, 4])
```

### `absolute_residuals[:, None]`

Получается столбец:

```text
[[1],
 [2],
 [4]]
```

### `absolute_residuals[None, :]`

Получается строка:

```text
[[1, 2, 4]]
```

При вычитании NumPy применяет broadcasting:

```text
[[1-1, 1-2, 1-4],
 [2-1, 2-2, 2-4],
 [4-1, 4-2, 4-4]]
```

После модуля:

```text
[[0, 1, 3],
 [1, 0, 2],
 [3, 2, 0]]
```

Это все попарные расстояния между ошибками.

---

## 3.7 Количество объектов

```python
n_samples = len(absolute_residuals)
```

`n_samples` входит в знаменатель формулы Gini:

```text
2 × n² × mean
```

---

## 3.8 Gini

```python
gini = np.sum(pairwise_differences) / (
    2 * n_samples**2 * mean_residual
)
```

Числитель:

```python
np.sum(pairwise_differences)
```

содержит сумму всех попарных абсолютных различий.

Знаменатель нормирует эту сумму.

Если все значения равны:

```text
|xi - xj| = 0
```

для каждой пары.

Тогда:

```text
Gini = 0
```

---

## 3.9 Fairness

```python
return float(1 - gini)
```

Так как большой Gini означает большое неравенство, fairness определяется наоборот:

```text
fairness = 1 - Gini
```

Если:

```text
Gini = 0
```

то:

```text
fairness = 1
```

---

# 4. Разбор функции `best_prediction`

## 4.1 Заголовок

```python
def best_prediction(
    y_true: np.ndarray,
    y_preds: List[np.ndarray],
    fairness_drop: float = 0.05,
) -> int:
```

Функция принимает:

- `y_true` — правильные бинарные ответы;
- `y_preds` — список прогнозов;
- `fairness_drop` — максимально допустимое относительное падение fairness.

Возвращает индекс выбранной модели.

---

## 4.2 Baseline

```python
baseline_prediction = np.asarray(
    y_preds[0],
    dtype=float,
)
```

По условию нулевой элемент списка — baseline.

---

## 4.3 Псевдоостатки baseline

```python
baseline_residuals = (
    y_true * np.log(baseline_prediction)
    + (1 - y_true)
    * np.log(1 - baseline_prediction)
)
```

Рассмотрим один объект.

### Если `y_true = 1`

Вторая часть обнуляется:

```text
logloss term = log(p)
```

### Если `y_true = 0`

Первая часть обнуляется:

```text
logloss term = log(1 - p)
```

Чем хуже вероятность правильного класса, тем больше модуль псевдоостатка.

---

## 4.4 Fairness baseline

```python
baseline_fairness = fairness(
    baseline_residuals
)
```

Она используется для построения фиксированного порога допуска.

---

## 4.5 Начальный победитель

```python
best_index = 0
```

Если ни один кандидат не удовлетворяет условиям, возвращается baseline.

---

## 4.6 Начальный лучший LogLoss

```python
best_loss = log_loss(
    y_true,
    baseline_prediction,
    labels=[0, 1],
)
```

В начале лучшей допустимой моделью является baseline.

Аргумент:

```python
labels=[0, 1]
```

явно задаёт оба класса и позволяет корректно считать LogLoss даже на выборке, где случайно присутствует только один класс.

---

## 4.7 Минимально допустимая fairness

```python
minimum_fairness = baseline_fairness * (
    1 - fairness_drop
)
```

Пример:

```text
baseline fairness = 0.80
fairness_drop      = 0.05
```

Тогда:

```text
minimum fairness = 0.80 × 0.95 = 0.76
```

Кандидат с fairness 0.75 будет отклонён.

Кандидат с fairness 0.76 разрешён, потому что условие использует:

```python
>=
```

---

## 4.8 Перебор кандидатов

```python
for index, prediction in enumerate(
    y_preds[1:],
    start=1,
):
```

Почему начинается с `y_preds[1:]`:

- baseline уже обработан;
- повторно проверять его не нужно.

Почему `start=1`:

- первый элемент среза `y_preds[1:]` имеет исходный индекс 1.

---

## 4.9 Расчёт показателей кандидата

Для каждой модели считаются:

```python
current_residuals
current_fairness
current_loss
```

---

## 4.10 Условие выбора

```python
if (
    current_loss < best_loss
    and current_fairness >= minimum_fairness
):
```

Кандидат должен одновременно:

1. иметь меньший LogLoss, чем текущий победитель;
2. пройти фиксированный fairness-порог baseline.

---

## 4.11 Обновление победителя

```python
best_index = index
best_loss = current_loss
```

Обновлять нужно не только индекс, но и `best_loss`.

Иначе более поздняя модель, которая лучше baseline, но хуже уже найденной модели, может ошибочно стать победителем.

---

# 5. Пример ошибки без обновления `best_loss`

Дано:

```text
baseline loss = 0.50
model 1 loss = 0.40
model 2 loss = 0.45
```

Если сравнивать каждый раз только с baseline:

```text
0.40 < 0.50 — выбираем model 1
0.45 < 0.50 — ошибочно заменяем на model 2
```

Хотя model 1 лучше.

С обновлением:

```text
best_loss = 0.40
```

проверка model 2:

```text
0.45 < 0.40 — False
```

Победителем остаётся model 1.

---

# 6. Сложность алгоритма

## Fairness

Матрица попарных разностей имеет размер:

```text
n × n
```

Поэтому:

```text
время:  O(n²)
память: O(n²)
```

Это напрямую соответствует формуле задания и удобно для учебной реализации.

Для миллионов объектов в production следует использовать более эффективную формулу Gini после сортировки:

```text
O(n log n)
```

Но для задания предпочтительно сохранить максимально прозрачную реализацию формулы.

---

## Best prediction

Пусть:

- `m` — количество моделей;
- `n` — количество объектов.

Для каждой модели вызывается fairness со сложностью `O(n²)`.

Итого:

```text
O(m × n²)
```

Для учебного задания это нормально.

---

# 7. Почему код должен пройти проверку

Учтены ключевые требования:

- берётся модуль псевдоостатков;
- Gini рассчитывается по формуле задания;
- возвращается `1 - gini`;
- baseline расположен в `y_preds[0]`;
- LogLoss сравнивается корректно;
- fairness сравнивается с фиксированным baseline-порогом;
- используется `>=`;
- при нахождении лучшей модели обновляется `best_loss`;
- код соответствует PEP8.

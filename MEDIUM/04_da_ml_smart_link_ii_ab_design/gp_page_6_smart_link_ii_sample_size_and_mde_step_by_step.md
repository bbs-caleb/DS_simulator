# Smart-Link II: Sample size and MDE — пошаговый разбор кода с нуля

## 1. Общая архитектура решения

В одном файле находятся шесть функций:

```python
cpc_sample
t_test
aa_test
ab_test
select_sample_size
select_mde
```

Они образуют цепочку:

```text
cpc_sample
    ↓
t_test
    ↓
aa_test и ab_test
    ↓
select_sample_size и select_mde
```

Новые функции не дублируют статистическую логику. Они вызывают функции прошлых шагов.

---

## 2. `select_sample_size`: сигнатура

```python
def select_sample_size(
    n_samples_grid: List[int],
    n_simulations: int,
    conversion_rate: float,
    mde: float,
    reward_avg: float,
    reward_std: float,
    alpha: float = 0.05,
    beta: float = 0.2,
) -> Tuple[int, float, float]:
```

### `n_samples_grid`

Список размеров одной группы, которые нужно проверить.

```python
[500, 1000, 2000, 5000]
```

### `n_simulations`

Количество повторных A/A- и A/B-симуляций для каждого размера.

### `conversion_rate`

Базовая конверсия контрольной группы.

### `mde`

Относительное увеличение CVR в группе B.

### `reward_avg`, `reward_std`

Параметры распределения вознаграждения.

### `alpha`

Порог t-теста и допустимая ошибка I рода.

### `beta`

Максимально допустимая ошибка II рода.

### Возвращаемое значение

```python
(n_samples, type_1_error, type_2_error)
```

---

## 3. Диагностические переменные

```python
last_n_samples = None
last_type_1_error = float("nan")
last_type_2_error = float("nan")
```

Они запоминают последнюю проверку.

Это нужно, если сетка закончится и ни один размер не подойдет.

`nan` означает `not a number`. Если сетка пустая, реальные ошибки еще не были вычислены.

---

## 4. Перебор размеров

```python
for n_samples in n_samples_grid:
```

Python берет элементы в исходном порядке.

Для:

```python
[500, 1000, 2000]
```

итерации будут:

```text
500 → 1000 → 2000
```

Поэтому сетка должна быть отсортирована заранее.

---

## 5. Оценка ошибки I рода

```python
type_1_error = aa_test(
    n_simulations,
    n_samples,
    conversion_rate,
    reward_avg,
    reward_std,
    alpha,
)
```

`aa_test` много раз создает две одинаково распределенные CPC-выборки.

Если t-test объявляет различие, это ложноположительный результат.

Возвращаемое число — доля ошибок I рода.

---

## 6. Оценка ошибки II рода

```python
type_2_error = ab_test(
    n_simulations,
    n_samples,
    conversion_rate,
    mde,
    reward_avg,
    reward_std,
    alpha,
)
```

`ab_test` создает:

```text
A: conversion_rate
B: conversion_rate × (1 + mde)
```

Если t-test не обнаруживает существующий эффект, это ошибка II рода.

---

## 7. Сохранение последней попытки

```python
last_n_samples = n_samples
last_type_1_error = type_1_error
last_type_2_error = type_2_error
```

Если текущий размер не подойдет и окажется последним, сообщение об ошибке покажет именно эти значения.

---

## 8. Главное условие выбора

```python
if type_1_error <= alpha and type_2_error <= beta:
```

Оператор `and` требует выполнения обоих условий.

Пример:

```text
type_1_error = 0.048
alpha = 0.05
0.048 <= 0.05 → True

type_2_error = 0.17
beta = 0.20
0.17 <= 0.20 → True

True and True → True
```

Размер подходит.

---

## 9. Почему используется `<=`

Если оценка равна пределу:

```text
type_2_error = beta
```

она находится в допустимых границах.

Поэтому используется `<=`, а не `<`.

---

## 10. Ранний возврат

```python
return n_samples, type_1_error, type_2_error
```

Как только найден первый подходящий размер, функция заканчивается.

Следующие элементы сетки не проверяются.

Это одновременно:

- экономит вычисления;
- возвращает минимальный подходящий элемент отсортированной сетки.

---

## 11. `RuntimeError`

Если цикл завершился без `return`:

```python
raise RuntimeError(...)
```

Это означает, что сетка недостаточна.

Функция не возвращает последнее значение, потому что оно не выполнило требования дизайна.

---

## 12. `select_mde`: сигнатура

```python
def select_mde(
    n_samples: int,
    n_simulations: int,
    conversion_rate: float,
    mde_grid: List[float],
    reward_avg: float,
    reward_std: float,
    alpha: float = 0.05,
    beta: float = 0.2,
) -> Tuple[float, float]:
```

Здесь размер группы фиксирован.

Изменяется только MDE.

Возвращается:

```python
(mde, type_2_error)
```

---

## 13. Перебор MDE

```python
for mde in mde_grid:
```

Пример:

```python
[0.01, 0.02, 0.05, 0.10, 0.20]
```

Функция начинает с самого маленького эффекта.

---

## 14. Оценка ошибки II рода

```python
type_2_error = ab_test(
    n_simulations,
    n_samples,
    conversion_rate,
    mde,
    reward_avg,
    reward_std,
    alpha,
)
```

Для каждого MDE проводится отдельная серия A/B-симуляций.

Чем больше MDE, тем обычно ниже ошибка II рода.

---

## 15. Условие выбора MDE

```python
if type_2_error <= beta:
```

Если `beta=0.20`, требуемая мощность равна:

```text
1 - 0.20 = 0.80
```

То есть MDE подходит, когда эффект обнаруживается хотя бы примерно в 80% симуляций.

---

## 16. Почему `select_mde` не вызывает `aa_test`

MDE отсутствует в A/A-дизайне.

При фиксированном `n_samples` ошибка I рода не должна пересчитываться отдельно для каждого MDE.

Поэтому API возвращает только MDE и ошибку II рода.

---

## 17. Пример запуска `select_sample_size`

```python
import numpy as np

np.random.seed(42)

result = select_sample_size(
    n_samples_grid=[
        500,
        1000,
        2000,
        5000,
        10000,
    ],
    n_simulations=2000,
    conversion_rate=0.10,
    mde=0.20,
    reward_avg=10.0,
    reward_std=2.0,
    alpha=0.05,
    beta=0.20,
)

print(result)
```

Результат зависит от seed и случайного Monte Carlo шума.

---

## 18. Интерпретация результата

Допустим, возвращено:

```python
(5000, 0.047, 0.14)
```

Это означает:

- требуется 5 000 кликов на группу;
- оцененная ошибка I рода — 4.7%;
- оцененная ошибка II рода — 14%;
- оцененная мощность — 86%.

---

## 19. Пример запуска `select_mde`

```python
np.random.seed(42)

result = select_mde(
    n_samples=5000,
    n_simulations=2000,
    conversion_rate=0.10,
    mde_grid=[
        0.01,
        0.02,
        0.05,
        0.10,
        0.20,
        0.30,
    ],
    reward_avg=10.0,
    reward_std=2.0,
    alpha=0.05,
    beta=0.20,
)

print(result)
```

Допустим, получено:

```python
(0.20, 0.13)
```

Значит, первый обнаружимый эффект из сетки — относительный рост 20%, а мощность примерно 87%.

---

## 20. Почему нельзя сортировать сетку внутри функции

Нельзя без требования добавлять:

```python
sorted(n_samples_grid)
```

или:

```python
sorted(mde_grid)
```

Это изменит:

- порядок перебора;
- порядок случайных вызовов;
- воспроизводимый результат при seed;
- поведение, которое могут проверять автотесты.

Пользователь должен подготовить сетку правильно.

---

## 21. Почему нельзя использовать `default_rng`

В условии прямо сказано не использовать:

```python
np.random.default_rng(...)
```

Решение сохраняет старый API:

```python
np.random.binomial(...)
np.random.normal(...)
```

Это позволяет внешнему коду управлять случайностью через:

```python
np.random.seed(...)
```

---

## 22. Почему seed не задается внутри функций

Неправильно:

```python
def aa_test(...):
    np.random.seed(42)
```

Тогда каждый вызов начинает одну и ту же последовательность.

Правильно:

```python
np.random.seed(42)
result = select_sample_size(...)
```

Функции остаются универсальными, а воспроизводимость контролируется снаружи.

---

## 23. Почему нельзя вернуть мощность вместо β

`ab_test` возвращает ошибку II рода:

```text
beta
```

Условие:

```python
type_2_error <= beta
```

Если случайно использовать `1 - type_2_error`, получится мощность, и логика сравнения перевернется.

---

## 24. Почему нельзя вернуть последнее значение после цикла

Плохой вариант:

```python
for value in grid:
    ...

return value, error
```

Так функция вернет последний элемент, даже если он не удовлетворяет условиям.

Правильный вариант:

- возвращать только внутри успешного `if`;
- после цикла вызывать `RuntimeError`.

---

## 25. Вычислительная стоимость

Для каждого sample size запускаются:

```text
n_simulations A/A-тестов
+
n_simulations A/B-тестов.
```

Каждая симуляция создает две CPC-выборки.

Поэтому ранний `return` особенно важен: после найденного решения лишние вычисления прекращаются.

---

## 26. Самая короткая логика страницы

```text
для каждого sample size:
    оценить alpha-фактическую
    оценить beta-фактическую
    вернуть первый дизайн, прошедший оба ограничения
```

и:

```text
для каждого MDE:
    оценить beta
    вернуть первый MDE с нужной мощностью
```

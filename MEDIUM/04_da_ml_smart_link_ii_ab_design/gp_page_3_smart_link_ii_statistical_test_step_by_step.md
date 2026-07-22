# Smart-Link II: Statistical test — пошаговый разбор кода с нуля

# 1. Полный файл решения

```python
"""CPC sampling and statistical comparison for an A/B experiment."""

from typing import Tuple

import numpy as np
from scipy.stats import ttest_ind


def cpc_sample(
    n_samples: int,
    conversion_rate: float,
    reward_avg: float,
    reward_std: float,
) -> np.ndarray:
    """Generate a sample of cost-per-click values.

    Parameters
    ----------
    n_samples:
        Number of clicks in the sample.
    conversion_rate:
        Probability that a click leads to an action.
    reward_avg:
        Mean reward for an action.
    reward_std:
        Standard deviation of the reward.

    Returns
    -------
    np.ndarray
        Simulated CPC values.
    """
    actions = np.random.binomial(
        n=1,
        p=conversion_rate,
        size=n_samples,
    )
    rewards = np.random.normal(
        loc=reward_avg,
        scale=reward_std,
        size=n_samples,
    )

    cpc = actions * rewards

    return cpc


def t_test(
    cpc_a: np.ndarray,
    cpc_b: np.ndarray,
    alpha: float = 0.05,
) -> Tuple[bool, float]:
    """Compare two independent CPC samples using Welch's t-test.

    Parameters
    ----------
    cpc_a:
        CPC sample from the first group.
    cpc_b:
        CPC sample from the second group.
    alpha:
        Statistical significance level.

    Returns
    -------
    Tuple[bool, float]
        Significance flag and p-value.
    """
    test_result = ttest_ind(
        cpc_a,
        cpc_b,
        equal_var=False,
    )
    p_value = float(test_result.pvalue)
    is_significant = bool(p_value < alpha)

    return is_significant, p_value
```

---

# 2. Импорт `Tuple`

```python
from typing import Tuple
```

Функция `t_test` возвращает два значения:

```text
логическое значение + число
```

Аннотация:

```python
Tuple[bool, float]
```

означает:

```text
первый элемент — bool;
второй элемент — float.
```

Пример:

```python
(True, 0.012)
```

---

# 3. Импорт NumPy

```python
import numpy as np
```

`numpy` используется для:

- генерации случайных значений;
- хранения массивов;
- поэлементного умножения.

Сокращение `np` — общепринятое имя NumPy.

---

# 4. Импорт t-теста

```python
from scipy.stats import ttest_ind
```

`scipy.stats` — модуль статистических функций.

`ttest_ind` означает:

```text
t-test independent
```

То есть t-тест для двух независимых выборок.

В нашем случае:

- `cpc_a` — клики группы A;
- `cpc_b` — клики группы B.

---

# 5. Объявление `cpc_sample`

```python
def cpc_sample(
    n_samples: int,
    conversion_rate: float,
    reward_avg: float,
    reward_std: float,
) -> np.ndarray:
```

Разберем параметры.

## `n_samples`

Количество кликов.

Пример:

```python
n_samples=10_000
```

Функция должна вернуть массив длиной 10 000.

## `conversion_rate`

Вероятность действия.

Пример:

```python
conversion_rate=0.05
```

Это означает примерно 5% успешных кликов.

## `reward_avg`

Среднее вознаграждение за действие.

Пример:

```python
reward_avg=20.0
```

## `reward_std`

Стандартное отклонение вознаграждения.

Пример:

```python
reward_std=3.0
```

## Возвращаемый тип

```python
-> np.ndarray
```

Функция возвращает массив NumPy.

---

# 6. Генерация действий

```python
actions = np.random.binomial(
    n=1,
    p=conversion_rate,
    size=n_samples,
)
```

## Параметр `n=1`

Проводится одно испытание для каждого элемента.

Поэтому результат:

```text
0 или 1
```

## Параметр `p`

Вероятность успеха.

```python
p=conversion_rate
```

Если:

```python
conversion_rate=0.10
```

примерно 10% элементов должны быть единицами.

## Параметр `size`

Количество генерируемых значений.

```python
size=n_samples
```

Пример возможного массива:

```python
[0, 0, 1, 0, 0, 1]
```

---

# 7. Генерация rewards

```python
rewards = np.random.normal(
    loc=reward_avg,
    scale=reward_std,
    size=n_samples,
)
```

## `loc`

Среднее нормального распределения.

```python
loc=reward_avg
```

## `scale`

Стандартное отклонение.

```python
scale=reward_std
```

## `size`

Количество значений.

Пример:

```python
[18.3, 20.5, 21.1, 17.9, 23.0, 19.4]
```

---

# 8. Почему массивы имеют одинаковую длину

`actions` содержит результат для каждого клика.

`rewards` также содержит потенциальное вознаграждение для каждого клика.

Если:

```text
n_samples = 6
```

оба массива имеют длину 6.

Это позволяет перемножить элементы с одинаковыми индексами.

---

# 9. Расчет CPC

```python
cpc = actions * rewards
```

NumPy выполняет поэлементное умножение.

Пример:

```text
actions = [0, 0, 1, 0, 1]
rewards = [10, 12, 9, 11, 15]
```

Результат:

```text
cpc = [0, 0, 9, 0, 15]
```

Для неуспешного клика:

```text
0 × reward = 0
```

Для успешного:

```text
1 × reward = reward
```

---

# 10. Возврат массива

```python
return cpc
```

После `return` функция завершает работу и отдает массив вызывающему коду.

Пример:

```python
sample = cpc_sample(
    n_samples=1000,
    conversion_rate=0.10,
    reward_avg=20,
    reward_std=3,
)
```

Теперь `sample` содержит 1 000 CPC-наблюдений.

---

# 11. Объявление `t_test`

```python
def t_test(
    cpc_a: np.ndarray,
    cpc_b: np.ndarray,
    alpha: float = 0.05,
) -> Tuple[bool, float]:
```

## `cpc_a`

Выборка контрольной группы.

## `cpc_b`

Выборка тестовой группы.

## `alpha`

Уровень статистической значимости.

По умолчанию:

```python
0.05
```

## Возвращаемый тип

```python
Tuple[bool, float]
```

Пример:

```python
(True, 0.003)
```

---

# 12. Запуск t-теста

```python
test_result = ttest_ind(
    cpc_a,
    cpc_b,
    equal_var=False,
)
```

## Первые два аргумента

```python
cpc_a
cpc_b
```

Это сравниваемые выборки.

## `equal_var=False`

Мы не предполагаем, что дисперсии двух групп равны.

SciPy использует Welch t-test.

Это более надежный вариант для групп с разным разбросом и разным размером.

---

# 13. Результат SciPy

`test_result` содержит несколько полей.

Основные:

```python
test_result.statistic
test_result.pvalue
```

Для задания нужна только вероятность `pvalue`.

---

# 14. Преобразование p-value в `float`

```python
p_value = float(test_result.pvalue)
```

SciPy может возвращать специальный числовой тип NumPy.

По API задания требуется обычное числовое значение.

`float(...)` гарантирует стандартный Python `float`.

---

# 15. Сравнение с alpha

```python
is_significant = bool(p_value < alpha)
```

Пример:

```text
p_value = 0.02
alpha = 0.05
```

Сравнение:

```text
0.02 < 0.05 → True
```

Другой пример:

```text
p_value = 0.20
alpha = 0.05
```

Сравнение:

```text
0.20 < 0.05 → False
```

`bool(...)` гарантирует стандартный Python `bool`.

---

# 16. Возврат результата

```python
return is_significant, p_value
```

Python автоматически упаковывает значения в кортеж.

Например:

```python
(True, 0.0124)
```

---

# 17. Полный пример использования

```python
import numpy as np

np.random.seed(42)

cpc_a = cpc_sample(
    n_samples=10_000,
    conversion_rate=0.10,
    reward_avg=10.0,
    reward_std=2.0,
)

cpc_b = cpc_sample(
    n_samples=10_000,
    conversion_rate=0.11,
    reward_avg=10.0,
    reward_std=2.0,
)

is_significant, p_value = t_test(
    cpc_a,
    cpc_b,
    alpha=0.05,
)

print(is_significant)
print(p_value)
```

---

# 18. Что делает `np.random.seed`

```python
np.random.seed(42)
```

Псевдослучайный генератор становится воспроизводимым.

Это означает, что при одинаковом seed и одинаковом порядке вызовов будут получены одинаковые числа.

Seed нужен:

- в тестах;
- в учебных примерах;
- в симуляциях;
- для воспроизводимости анализа.

Функция задания не должна самостоятельно устанавливать seed.

Почему?

Если внутри функции всегда делать:

```python
np.random.seed(42)
```

каждый вызов будет генерировать одинаковую выборку.

Это сломает нормальную симуляцию и может не соответствовать тестам.

Seed должен задавать внешний код.

---

# 19. Почему сначала генерируются actions, потом rewards

Автоматические тесты могут устанавливать seed и ожидать определенный порядок случайных вызовов.

Поэтому порядок из условия сохраняется:

1. биномиальная выборка;
2. нормальная выборка;
3. умножение.

Если поменять порядок, статистические свойства останутся похожими, но конкретные сгенерированные числа при фиксированном seed изменятся.

---

# 20. Почему не применяется округление

Нельзя делать:

```python
cpc = np.round(cpc, 2)
```

В условии округление не требуется.

Округление:

- меняет выборку;
- меняет среднее;
- меняет p-value;
- может сломать тесты.

---

# 21. Почему не удаляются отрицательные rewards

Нельзя делать:

```python
rewards[rewards < 0] = 0
```

Условие требует нормальное распределение без дополнительного ограничения.

Даже если бизнесово отрицательные значения выглядят странно, учебную модель нужно реализовать буквально.

---

# 22. Почему не используется `np.random.choice`

Для action можно было бы использовать:

```python
np.random.choice(
    [0, 1],
    size=n_samples,
    p=[1 - conversion_rate, conversion_rate],
)
```

Но условие прямо говорит о биномиальном распределении.

Поэтому используется:

```python
np.random.binomial(...)
```

---

# 23. Почему не реализуется t-test вручную

Ручная реализация потребовала бы:

- вычислить средние;
- вычислить несмещенные дисперсии;
- вычислить стандартную ошибку;
- вычислить степени свободы Welch–Satterthwaite;
- получить вероятность из t-распределения;
- корректно обработать крайние случаи.

SciPy уже реализует и тестирует этот алгоритм.

В условии прямо разрешено использовать статистический пакет.

---

# 24. Сложность

## Генерация выборки

Для `n_samples` значений:

```text
O(n_samples)
```

Память:

- массив actions;
- массив rewards;
- массив cpc.

## T-test

Для двух массивов общей длины `n + m`:

```text
O(n + m)
```

Нужно вычислить статистики по обеим выборкам.

---

# 25. Самая короткая логика решения

```text
actions ~ Binomial(1, conversion_rate)
rewards ~ Normal(reward_avg, reward_std)
cpc = actions × rewards

p_value = Welch_t_test(cpc_a, cpc_b)
significant = p_value < alpha
```

Это и есть вся математическая основа двух функций.

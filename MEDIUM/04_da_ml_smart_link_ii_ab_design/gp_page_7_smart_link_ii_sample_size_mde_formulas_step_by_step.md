# Smart-Link II: формулы Sample Size и MDE — пошаговый разбор кода

# 1. Полный файл решения

```python
"""Analytical sample-size and MDE calculations for an A/B test."""

import numpy as np
from scipy import stats


def calculate_sample_size(
    reward_avg: float,
    reward_std: float,
    mde: float,
    alpha: float,
    beta: float,
) -> int:
    """Calculate the required sample size for each experiment group."""
    assert mde > 0, "mde should be greater than 0"

    absolute_mde = reward_avg * mde
    alpha_quantile = stats.norm.ppf(1.0 - alpha / 2.0)
    beta_quantile = stats.norm.ppf(1.0 - beta)

    sample_size = (
        2.0
        * reward_std**2
        * (alpha_quantile + beta_quantile) ** 2
        / absolute_mde**2
    )

    return int(np.ceil(sample_size))


def calculate_mde(
    reward_std: float,
    sample_size: int,
    alpha: float,
    beta: float,
) -> float:
    """Calculate the absolute minimum detectable effect."""
    alpha_quantile = stats.norm.ppf(1.0 - alpha / 2.0)
    beta_quantile = stats.norm.ppf(1.0 - beta)

    mde = (
        (alpha_quantile + beta_quantile)
        * np.sqrt(2.0)
        * reward_std
        / np.sqrt(sample_size)
    )

    return float(mde)
```

---

# 2. Импорт NumPy

```python
import numpy as np
```

NumPy нужен для:

```python
np.ceil(...)
np.sqrt(...)
```

## `np.ceil`

Округляет вверх.

```python
np.ceil(10.01)
```

дает:

```text
11.0
```

## `np.sqrt`

Вычисляет квадратный корень.

```python
np.sqrt(4)
```

дает:

```text
2.0
```

---

# 3. Импорт SciPy

```python
from scipy import stats
```

Через `stats` используется нормальное распределение:

```python
stats.norm.ppf(...)
```

---

# 4. Сигнатура `calculate_sample_size`

```python
def calculate_sample_size(
    reward_avg: float,
    reward_std: float,
    mde: float,
    alpha: float,
    beta: float,
) -> int:
```

Функция возвращает:

```python
int
```

Это размер **каждой** группы, а не суммарный размер A+B.

---

# 5. Проверка MDE

```python
assert mde > 0, "mde should be greater than 0"
```

Если:

```python
mde=0
```

в формуле возникло бы деление на ноль.

Отрицательный MDE также не соответствует задаче расчета размера для величины эффекта.

---

# 6. Перевод MDE в абсолютные единицы

```python
absolute_mde = reward_avg * mde
```

Пример:

```text
reward_avg = 50
mde = 0.10
```

Результат:

```text
absolute_mde = 5
```

---

# 7. Квантиль alpha

```python
alpha_quantile = stats.norm.ppf(
    1.0 - alpha / 2.0
)
```

При:

```text
alpha = 0.05
```

внутри:

```text
1 - 0.05 / 2
= 1 - 0.025
= 0.975
```

Результат:

```text
≈ 1.95996
```

---

# 8. Квантиль beta

```python
beta_quantile = stats.norm.ppf(1.0 - beta)
```

При:

```text
beta = 0.20
```

внутри:

```text
1 - 0.20 = 0.80
```

Результат:

```text
≈ 0.84162
```

---

# 9. Квадрат стандартного отклонения

```python
reward_std**2
```

Это дисперсия:

```text
σ²
```

Если:

```text
reward_std = 3
```

то:

```text
reward_std**2 = 9
```

---

# 10. Сумма квантилей

```python
alpha_quantile + beta_quantile
```

При стандартных параметрах:

```text
1.96 + 0.84 ≈ 2.80
```

В формуле сумма возводится в квадрат:

```python
(alpha_quantile + beta_quantile) ** 2
```

---

# 11. Полная формула sample size

```python
sample_size = (
    2.0
    * reward_std**2
    * (alpha_quantile + beta_quantile) ** 2
    / absolute_mde**2
)
```

Порядок:

```text
1. 2 × дисперсия;
2. умножить на квадрат суммы квантилей;
3. разделить на квадрат абсолютного MDE.
```

---

# 12. Округление и тип

```python
return int(np.ceil(sample_size))
```

Сначала:

```python
np.ceil(sample_size)
```

округляет вверх, но возвращает число NumPy/float.

Затем:

```python
int(...)
```

создает обычный Python `int`.

---

# 13. Сигнатура `calculate_mde`

```python
def calculate_mde(
    reward_std: float,
    sample_size: int,
    alpha: float,
    beta: float,
) -> float:
```

В функцию не передается `reward_avg`.

Поэтому результат невозможно сразу выразить относительно среднего.

Возвращается абсолютный MDE.

---

# 14. Квантили в `calculate_mde`

Они рассчитываются точно так же:

```python
alpha_quantile = stats.norm.ppf(
    1.0 - alpha / 2.0
)
beta_quantile = stats.norm.ppf(1.0 - beta)
```

Это важно: обе функции должны быть математически согласованы.

---

# 15. Квадратный корень из двух

```python
np.sqrt(2.0)
```

Появляется из суммы дисперсий двух средних одинакового размера:

```text
sqrt(σ²/n + σ²/n)
= sqrt(2σ²/n)
= sqrt(2) × σ / sqrt(n)
```

---

# 16. Деление на корень размера

```python
/ np.sqrt(sample_size)
```

Это показывает фундаментальный закон:

```text
MDE уменьшается как 1 / sqrt(n).
```

Чтобы MDE уменьшился в два раза:

```text
n нужно увеличить примерно в четыре раза.
```

---

# 17. Полная формула MDE

```python
mde = (
    (alpha_quantile + beta_quantile)
    * np.sqrt(2.0)
    * reward_std
    / np.sqrt(sample_size)
)
```

Результат находится в тех же единицах, что и `reward_std`.

---

# 18. Приведение к `float`

```python
return float(mde)
```

`np.sqrt` и операции NumPy могут вернуть тип:

```text
numpy.float64
```

Задание ожидает числовой результат.

Явное преобразование дает обычный Python:

```python
float
```

---

# 19. Пример расчета sample size

```python
result = calculate_sample_size(
    reward_avg=100.0,
    reward_std=30.0,
    mde=0.10,
    alpha=0.05,
    beta=0.20,
)

print(result)
```

Пошагово:

```text
absolute MDE = 100 × 0.10 = 10
z_alpha ≈ 1.96
z_beta ≈ 0.84
```

Формула дает примерно 141–142 наблюдения в зависимости от точных квантилей.

Результат округляется вверх.

---

# 20. Обратная проверка

Можно взять рассчитанный sample size:

```python
n = calculate_sample_size(...)
```

и посчитать абсолютный MDE:

```python
absolute_mde = calculate_mde(
    reward_std=30.0,
    sample_size=n,
    alpha=0.05,
    beta=0.20,
)
```

Из-за округления вверх полученный MDE будет:

```text
не больше исходного абсолютного MDE.
```

Это ожидаемо.

---

# 21. Перевод абсолютного MDE обратно в относительный

```python
relative_mde = absolute_mde / reward_avg
```

Пример:

```text
absolute_mde = 5
reward_avg = 50
```

Тогда:

```text
relative_mde = 0.10 = 10%
```

---

# 22. Почему нельзя использовать `alpha`, а не `alpha / 2`

Если написать:

```python
stats.norm.ppf(1 - alpha)
```

получится формула для односторонней логики.

Условие показывает:

```text
z_(alpha/2)
```

и говорит передать:

```text
1 - alpha / 2
```

Поэтому двусторонний квантиль обязателен.

---

# 23. Почему нельзя забыть квадрат MDE

Неверно:

```python
... / absolute_mde
```

Правильно:

```python
... / absolute_mde**2
```

Sample size обратно пропорционален квадрату эффекта.

---

# 24. Почему нельзя округлять `round`

```python
round(141.2)
```

дает:

```text
141
```

Но нужен запас вверх:

```python
ceil(141.2) = 142
```

Поэтому используется только `ceil`.

---

# 25. Почему `calculate_mde` не округляется

MDE — непрерывная величина.

Нет требования округлять до целого числа.

Возвращается точный `float`.

---

# 26. Сложность

Обе функции выполняют фиксированное число математических операций:

```text
O(1)
```

В отличие от симуляционного подбора здесь нет зависимости времени выполнения от:

- числа симуляций;
- размера выборки;
- длины сетки.

---

# 27. Самая короткая памятка

```text
relative MDE → умножить на mean → absolute MDE

sample size:
n = 2σ²(zα + zβ)² / MDE²

absolute MDE:
MDE = (zα + zβ)√2σ / √n

sample size всегда округлять вверх.
```

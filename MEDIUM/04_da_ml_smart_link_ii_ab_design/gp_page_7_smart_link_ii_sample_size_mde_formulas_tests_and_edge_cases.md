# Smart-Link II: формулы Sample Size и MDE — проверки и граничные случаи

# 1. Проверка импорта

```python
from solution import (
    calculate_mde,
    calculate_sample_size,
)
```

---

# 2. Проверка типов

```python
sample_size = calculate_sample_size(
    reward_avg=100.0,
    reward_std=30.0,
    mde=0.10,
    alpha=0.05,
    beta=0.20,
)

assert type(sample_size) is int
```

Для MDE:

```python
mde = calculate_mde(
    reward_std=30.0,
    sample_size=1000,
    alpha=0.05,
    beta=0.20,
)

assert type(mde) is float
```

---

# 3. Эталонный расчет sample size

Можно вручную проверить формулу:

```python
import numpy as np
from scipy import stats

reward_avg = 100.0
reward_std = 30.0
relative_mde = 0.10
alpha = 0.05
beta = 0.20

absolute_mde = reward_avg * relative_mde
z_alpha = stats.norm.ppf(1 - alpha / 2)
z_beta = stats.norm.ppf(1 - beta)

expected = int(
    np.ceil(
        2
        * reward_std**2
        * (z_alpha + z_beta) ** 2
        / absolute_mde**2
    )
)

actual = calculate_sample_size(
    reward_avg,
    reward_std,
    relative_mde,
    alpha,
    beta,
)

assert actual == expected
```

---

# 4. Эталонный расчет MDE

```python
reward_std = 30.0
sample_size = 1000
alpha = 0.05
beta = 0.20

z_alpha = stats.norm.ppf(1 - alpha / 2)
z_beta = stats.norm.ppf(1 - beta)

expected = (
    (z_alpha + z_beta)
    * np.sqrt(2)
    * reward_std
    / np.sqrt(sample_size)
)

actual = calculate_mde(
    reward_std,
    sample_size,
    alpha,
    beta,
)

assert np.isclose(actual, expected)
```

---

# 5. Проверка относительного MDE

Два случая с одинаковым абсолютным эффектом должны дать одинаковый sample size.

## Случай 1

```text
reward_avg = 100
relative MDE = 0.10
absolute MDE = 10
```

## Случай 2

```text
reward_avg = 200
relative MDE = 0.05
absolute MDE = 10
```

Проверка:

```python
n_1 = calculate_sample_size(
    100,
    30,
    0.10,
    0.05,
    0.20,
)

n_2 = calculate_sample_size(
    200,
    30,
    0.05,
    0.05,
    0.20,
)

assert n_1 == n_2
```

---

# 6. MDE уменьшается — sample size растет

```python
n_large_effect = calculate_sample_size(
    100,
    30,
    0.20,
    0.05,
    0.20,
)

n_small_effect = calculate_sample_size(
    100,
    30,
    0.10,
    0.05,
    0.20,
)

assert n_small_effect > n_large_effect
```

---

# 7. Проверка квадратичной зависимости

Если абсолютный MDE уменьшается в два раза, sample size должен увеличиться примерно в четыре раза.

Из-за округления отношение может быть не идеально равно 4.

```python
n_10_percent = calculate_sample_size(
    100,
    30,
    0.10,
    0.05,
    0.20,
)

n_5_percent = calculate_sample_size(
    100,
    30,
    0.05,
    0.05,
    0.20,
)

assert np.isclose(
    n_5_percent / n_10_percent,
    4.0,
    rtol=0.02,
)
```

---

# 8. Стандартное отклонение растет — sample size растет

```python
n_low_noise = calculate_sample_size(
    100,
    10,
    0.10,
    0.05,
    0.20,
)

n_high_noise = calculate_sample_size(
    100,
    20,
    0.10,
    0.05,
    0.20,
)

assert n_high_noise > n_low_noise
```

При удвоении `reward_std` выборка увеличивается примерно в четыре раза.

---

# 9. Более строгий alpha увеличивает sample size

```python
n_alpha_005 = calculate_sample_size(
    100,
    30,
    0.10,
    0.05,
    0.20,
)

n_alpha_001 = calculate_sample_size(
    100,
    30,
    0.10,
    0.01,
    0.20,
)

assert n_alpha_001 > n_alpha_005
```

---

# 10. Более высокая мощность увеличивает sample size

Мощность 90%:

```text
beta = 0.10
```

Мощность 80%:

```text
beta = 0.20
```

Проверка:

```python
n_power_80 = calculate_sample_size(
    100,
    30,
    0.10,
    0.05,
    0.20,
)

n_power_90 = calculate_sample_size(
    100,
    30,
    0.10,
    0.05,
    0.10,
)

assert n_power_90 > n_power_80
```

---

# 11. Sample size растет — MDE уменьшается

```python
mde_small_sample = calculate_mde(
    reward_std=30,
    sample_size=100,
    alpha=0.05,
    beta=0.20,
)

mde_large_sample = calculate_mde(
    reward_std=30,
    sample_size=400,
    alpha=0.05,
    beta=0.20,
)

assert mde_large_sample < mde_small_sample
```

При увеличении sample size в четыре раза MDE должен уменьшиться примерно в два раза:

```python
assert np.isclose(
    mde_small_sample / mde_large_sample,
    2.0,
)
```

---

# 12. Обратная согласованность

```python
reward_avg = 100.0
reward_std = 30.0
relative_mde = 0.10
alpha = 0.05
beta = 0.20

sample_size = calculate_sample_size(
    reward_avg,
    reward_std,
    relative_mde,
    alpha,
    beta,
)

calculated_absolute_mde = calculate_mde(
    reward_std,
    sample_size,
    alpha,
    beta,
)

target_absolute_mde = reward_avg * relative_mde

assert calculated_absolute_mde <= target_absolute_mde
```

Почему `<=`, а не точное равенство?

Потому что sample size округлен вверх.

---

# 13. Проверка assert для нулевого MDE

```python
try:
    calculate_sample_size(
        reward_avg=100,
        reward_std=30,
        mde=0,
        alpha=0.05,
        beta=0.20,
    )
except AssertionError as error:
    assert str(error) == "mde should be greater than 0"
```

---

# 14. Отрицательный MDE

```python
try:
    calculate_sample_size(
        100,
        30,
        -0.10,
        0.05,
        0.20,
    )
except AssertionError:
    pass
```

---

# 15. Граничный случай `reward_avg = 0`

Тогда:

```text
absolute_mde = reward_avg × mde = 0
```

Формула делит на ноль.

В реальном дизайне относительный MDE относительно нулевого среднего не определен.

Условие предполагает положительное ненулевое среднее.

---

# 16. Граничный случай `reward_std = 0`

Если метрика не имеет никакого разброса:

```text
все наблюдения одинаковы.
```

Формула sample size даст 0 до округления.

Математически любой ненулевой эффект различим без шума, но реальный эксперимент с нулевой дисперсией — особый вырожденный случай.

---

# 17. Граничный случай `sample_size = 0`

В `calculate_mde` возникнет деление на ноль.

Условие предполагает положительный размер группы.

Не нужно самовольно менять API дополнительными assert, если они не требуются автотестом.

---

# 18. Недопустимые alpha и beta

Для `stats.norm.ppf` нужны вероятности в диапазоне `[0, 1]`.

Обычно:

```text
0 < alpha < 1
0 < beta < 1
```

Задание предполагает корректные значения.

---

# 19. Не использовать симуляции

В этих функциях не должно быть:

```python
for
np.random
cpc_sample
t_test
```

Решение должно применять прямую формулу.

---

# 20. Не использовать `default_rng`

Для этой страницы случайные числа вообще не нужны.

Поэтому вопрос о `default_rng` не возникает.

---

# 21. Проверка компиляции

```bash
python -m py_compile solution.py
```

---

# 22. Что загружать на платформу

Основной файл:

```text
gp_page_7_smart_link_ii_sample_size_mde_formulas_solution.py
```

Если загрузчик требует:

```text
solution.py
```

нужно использовать содержимое основного файла под этим именем.

---

# 23. Соответствие баллам

## 40% — `calculate_sample_size`

Реализовано:

- точная сигнатура;
- assert для MDE;
- относительный MDE преобразован в абсолютный;
- `norm.ppf(1 - alpha / 2)`;
- `norm.ppf(1 - beta)`;
- коэффициент `2`;
- квадрат дисперсии и эффекта;
- округление вверх;
- возврат `int`.

## 40% — `calculate_mde`

Реализовано:

- точная сигнатура;
- оба квантиля;
- `sqrt(2)`;
- деление на `sqrt(sample_size)`;
- абсолютный результат;
- возврат `float`.

## 20% — качество кода

Есть:

- PEP8;
- docstrings;
- type hints;
- понятные переменные;
- минимальный код;
- только необходимые библиотеки.

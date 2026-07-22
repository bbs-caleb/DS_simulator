# Smart-Link II: Statistical test — проверки, симуляции и граничные случаи

# 1. Что проверяют баллы

Условие делит оценку так:

```text
40% — cpc_sample
40% — t_test
20% — качество кода
```

Если API не совпадает, остальные проверки могут дать 0.

Поэтому особенно важны:

- точные имена функций;
- точный порядок аргументов;
- значение `alpha=0.05` по умолчанию;
- возврат `np.ndarray`;
- возврат кортежа `(bool, float)`.

---

# 2. Проверка импорта

Если файл переименован платформой в `solution.py`:

```python
from solution import cpc_sample, t_test
```

При локальной работе с текущим именем:

```python
from gp_page_3_smart_link_ii_statistical_test_solution import (
    cpc_sample,
    t_test,
)
```

---

# 3. Проверка формы и типа CPC

```python
sample = cpc_sample(
    n_samples=1000,
    conversion_rate=0.10,
    reward_avg=20.0,
    reward_std=3.0,
)

assert isinstance(sample, np.ndarray)
assert sample.shape == (1000,)
```

---

# 4. Проверка conversion_rate = 0

```python
sample = cpc_sample(
    n_samples=1000,
    conversion_rate=0.0,
    reward_avg=20.0,
    reward_std=3.0,
)

assert np.all(sample == 0)
```

Почему?

При вероятности 0 все actions равны нулю.

---

# 5. Проверка conversion_rate = 1

```python
np.random.seed(42)

sample = cpc_sample(
    n_samples=1000,
    conversion_rate=1.0,
    reward_avg=20.0,
    reward_std=3.0,
)

assert np.all(sample != 0)
```

При `conversion_rate=1` все actions равны единице.

Следовательно, CPC равен rewards.

Теоретически нормальное распределение может очень редко дать ровно ноль, но для обычных параметров это практически невозможно.

---

# 6. Проверка доли ненулевых значений

```python
np.random.seed(42)

sample = cpc_sample(
    n_samples=100_000,
    conversion_rate=0.10,
    reward_avg=20.0,
    reward_std=3.0,
)

non_zero_share = np.mean(sample != 0)

print(non_zero_share)

assert abs(non_zero_share - 0.10) < 0.01
```

Доля ненулевых значений должна быть близка к CVR.

---

# 7. Проверка среднего CPC

Теоретическое среднее:

```text
conversion_rate × reward_avg
```

Проверка:

```python
np.random.seed(42)

conversion_rate = 0.10
reward_avg = 20.0

sample = cpc_sample(
    n_samples=500_000,
    conversion_rate=conversion_rate,
    reward_avg=reward_avg,
    reward_std=3.0,
)

expected_mean = conversion_rate * reward_avg
actual_mean = sample.mean()

print(expected_mean)
print(actual_mean)

assert abs(actual_mean - expected_mean) < 0.05
```

---

# 8. Проверка воспроизводимости через внешний seed

```python
np.random.seed(123)

sample_1 = cpc_sample(
    n_samples=100,
    conversion_rate=0.10,
    reward_avg=20.0,
    reward_std=3.0,
)

np.random.seed(123)

sample_2 = cpc_sample(
    n_samples=100,
    conversion_rate=0.10,
    reward_avg=20.0,
    reward_std=3.0,
)

assert np.array_equal(sample_1, sample_2)
```

Функция уважает глобальный seed NumPy.

---

# 9. Проверка, что функция сама не фиксирует seed

```python
np.random.seed(123)

sample_1 = cpc_sample(
    100,
    0.10,
    20.0,
    3.0,
)

sample_2 = cpc_sample(
    100,
    0.10,
    20.0,
    3.0,
)

assert not np.array_equal(sample_1, sample_2)
```

Последовательные вызовы должны давать новые выборки.

---

# 10. Проверка одинаковых выборок

```python
sample = np.array([0.0, 1.0, 0.0, 2.0, 0.0])

is_significant, p_value = t_test(
    sample,
    sample.copy(),
)

assert is_significant is False
assert p_value == 1.0
```

Средние и все наблюдения одинаковы.

---

# 11. Проверка очевидно разных выборок

```python
cpc_a = np.array([0.0, 0.0, 1.0, 0.0, 1.0] * 1000)
cpc_b = np.array([10.0, 11.0, 12.0, 10.0, 11.0] * 1000)

is_significant, p_value = t_test(cpc_a, cpc_b)

assert is_significant is True
assert p_value < 0.05
```

---

# 12. Проверка alpha

```python
cpc_a = np.array([1, 2, 3, 4, 5], dtype=float)
cpc_b = np.array([2, 3, 4, 5, 6], dtype=float)

result_strict = t_test(
    cpc_a,
    cpc_b,
    alpha=0.01,
)

result_soft = t_test(
    cpc_a,
    cpc_b,
    alpha=0.50,
)

print(result_strict)
print(result_soft)
```

Один и тот же p-value сравнивается с разными порогами.

---

# 13. Проверка типов возвращаемых значений

```python
cpc_a = np.arange(10, dtype=float)
cpc_b = np.arange(10, dtype=float) + 1

is_significant, p_value = t_test(cpc_a, cpc_b)

assert type(is_significant) is bool
assert type(p_value) is float
```

В решении используется явное преобразование:

```python
bool(...)
float(...)
```

---

# 14. Симуляция отсутствия эффекта

```python
np.random.seed(42)

cpc_a = cpc_sample(
    n_samples=20_000,
    conversion_rate=0.10,
    reward_avg=10.0,
    reward_std=2.0,
)

cpc_b = cpc_sample(
    n_samples=20_000,
    conversion_rate=0.10,
    reward_avg=10.0,
    reward_std=2.0,
)

print(t_test(cpc_a, cpc_b))
```

Параметры распределений одинаковы.

Но отдельный запуск иногда может случайно дать `p < 0.05`.

Это и есть ошибка I рода.

При множестве повторений ее частота должна быть близка к alpha при выполнении предпосылок.

---

# 15. Симуляция эффекта через CVR

```python
np.random.seed(42)

cpc_a = cpc_sample(
    n_samples=100_000,
    conversion_rate=0.10,
    reward_avg=10.0,
    reward_std=2.0,
)

cpc_b = cpc_sample(
    n_samples=100_000,
    conversion_rate=0.11,
    reward_avg=10.0,
    reward_std=2.0,
)

print(cpc_a.mean())
print(cpc_b.mean())
print(t_test(cpc_a, cpc_b))
```

Группа B имеет более высокий conversion rate.

Ожидаемый CPC:

```text
A: 0.10 × 10 = 1.0
B: 0.11 × 10 = 1.1
```

---

# 16. Симуляция эффекта через CPA

```python
np.random.seed(42)

cpc_a = cpc_sample(
    n_samples=100_000,
    conversion_rate=0.10,
    reward_avg=10.0,
    reward_std=2.0,
)

cpc_b = cpc_sample(
    n_samples=100_000,
    conversion_rate=0.10,
    reward_avg=11.0,
    reward_std=2.0,
)

print(cpc_a.mean())
print(cpc_b.mean())
print(t_test(cpc_a, cpc_b))
```

CVR одинаков, но средняя награда B выше.

---

# 17. Симуляция одинакового ожидаемого CPC разными способами

Группа A:

```text
CVR = 0.10
reward_avg = 10
expected CPC = 1.0
```

Группа B:

```text
CVR = 0.05
reward_avg = 20
expected CPC = 1.0
```

Код:

```python
np.random.seed(42)

cpc_a = cpc_sample(
    100_000,
    0.10,
    10.0,
    2.0,
)

cpc_b = cpc_sample(
    100_000,
    0.05,
    20.0,
    2.0,
)

print(cpc_a.mean())
print(cpc_b.mean())
print(t_test(cpc_a, cpc_b))
```

Средние ожидаемо близки, но дисперсии различаются.

Именно поэтому Welch t-test является разумным выбором.

---

# 18. Почему p-value может немного меняться

Если не установить seed, каждый запуск генерирует новые случайные выборки.

Поэтому:

- средние меняются;
- t-статистика меняется;
- p-value меняется.

Это нормальное свойство симуляции.

---

# 19. Граничный случай: нулевая дисперсия

Если обе выборки состоят только из нулей:

```python
cpc_a = np.zeros(100)
cpc_b = np.zeros(100)
```

В некоторых версиях SciPy t-test может вернуть:

```text
p-value = nan
```

Причина:

- разница средних равна нулю;
- стандартная ошибка также равна нулю;
- возникает неопределенная математическая операция.

Условие не требует особой обработки этого случая.

Не стоит добавлять собственную логику без требования, потому что она может расходиться с ожидаемым поведением тестов.

---

# 20. Граничный случай: очень маленькие выборки

Для выборки из одного элемента невозможно надежно оценить дисперсию.

SciPy может вернуть `nan` и предупреждение.

Реальный t-test требует достаточного числа наблюдений.

Задание предполагает нормальные тестовые выборки.

---

# 21. Граничный случай: NaN во входе

Если массив содержит `np.nan`, стандартное поведение SciPy обычно приводит к `nan` в результате.

Можно использовать:

```python
nan_policy="omit"
```

Но условие этого не требует.

Добавление параметра изменило бы поведение API, поэтому в минимальном решении его нет.

---

# 22. Почему нельзя использовать парный t-test

Нельзя использовать:

```python
ttest_rel(...)
```

Он предназначен для парных наблюдений:

- до и после для одного человека;
- два измерения одного объекта;
- matched pairs.

В нашей задаче группы A и B независимы.

Поэтому нужен:

```python
ttest_ind(...)
```

---

# 23. Почему не используется одновыборочный t-test

Нельзя использовать:

```python
ttest_1samp(...)
```

Он сравнивает одну выборку с фиксированным числом.

Нам нужно сравнить две выборки.

---

# 24. Локальная комплексная проверка

```python
import numpy as np

from solution import cpc_sample, t_test


def run_checks():
    np.random.seed(42)

    sample = cpc_sample(
        n_samples=100_000,
        conversion_rate=0.10,
        reward_avg=10.0,
        reward_std=2.0,
    )

    assert isinstance(sample, np.ndarray)
    assert sample.shape == (100_000,)
    assert abs(np.mean(sample != 0) - 0.10) < 0.01
    assert abs(sample.mean() - 1.0) < 0.05

    np.random.seed(1)
    cpc_a = cpc_sample(
        50_000,
        0.10,
        10.0,
        2.0,
    )

    np.random.seed(2)
    cpc_b = cpc_sample(
        50_000,
        0.12,
        10.0,
        2.0,
    )

    is_significant, p_value = t_test(cpc_a, cpc_b)

    assert type(is_significant) is bool
    assert type(p_value) is float
    assert is_significant
    assert p_value < 0.05

    same_result = t_test(cpc_a, cpc_a.copy())

    assert same_result == (False, 1.0)


run_checks()
print("All checks passed.")
```

---

# 25. Что отправлять на платформу

Файл решения:

```text
gp_page_3_smart_link_ii_statistical_test_solution.py
```

Если загрузчик требует имя:

```text
solution.py
```

нужно использовать содержимое этого файла, но сохранить под требуемым платформой именем.

Markdown-файлы нужны для обучения и объяснения, но основным отправляемым решением является `.py`.

---

# 26. Соответствие критериям

## 40% — выборка CPC

Реализованы:

- биномиальные actions;
- нормальные rewards;
- поэлементный CPC;
- возврат `np.ndarray`.

## 40% — t-test

Реализованы:

- независимый t-test;
- Welch-вариант;
- сравнение с alpha;
- возврат флага и p-value.

## 20% — качество

Код содержит:

- PEP8-форматирование;
- docstrings;
- type hints;
- понятные имена;
- минимальную структуру;
- отсутствие лишних зависимостей и логики.

Закрытые тесты платформы недоступны, поэтому абсолютную гарантию результата дать невозможно. Однако код напрямую реализует API и математическую модель из условия.

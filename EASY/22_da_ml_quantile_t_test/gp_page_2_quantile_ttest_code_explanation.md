# QUANTILE T-TEST — построчное объяснение кода с абсолютного нуля

## 1. Полный код

```python
from typing import List, Tuple

import numpy as np
from scipy.stats import ttest_ind


def quantile_ttest(
    control: List[float],
    experiment: List[float],
    alpha: float = 0.05,
    quantile: float = 0.95,
    n_bootstraps: int = 1000,
) -> Tuple[float, bool]:
    """
    Bootstrapped t-test for quantiles of two samples.
    """
    control_quantiles = []
    experiment_quantiles = []

    for _ in range(n_bootstraps):
        control_sample = np.random.choice(
            control,
            size=len(control),
            replace=True,
        )
        experiment_sample = np.random.choice(
            experiment,
            size=len(experiment),
            replace=True,
        )

        control_quantiles.append(
            np.quantile(control_sample, quantile)
        )
        experiment_quantiles.append(
            np.quantile(experiment_sample, quantile)
        )

    _, p_value = ttest_ind(
        control_quantiles,
        experiment_quantiles,
    )
    result = bool(p_value < alpha)

    return float(p_value), result
```

---

# 2. Что должна делать функция

Функция получает две исходные выборки:

```python
control
experiment
```

Она должна:

1. много раз пересэмплировать каждую выборку с возвращением;
2. в каждой искусственной выборке вычислять заданный квантиль;
3. получить два списка bootstrap-квантилей;
4. сравнить эти списки через `ttest_ind`;
5. вернуть p-value и статистический вердикт.

---

# 3. Импорт типов

```python
from typing import List, Tuple
```

## `List`

Используется в аннотации:

```python
control: List[float]
```

Это означает, что ожидается список чисел.

Пример:

```python
[1.2, 3.5, 8.0]
```

## `Tuple`

Используется в аннотации результата:

```python
Tuple[float, bool]
```

Функция возвращает два значения:

1. `float` — p-value;
2. `bool` — `True` или `False`.

---

# 4. Импорт NumPy

```python
import numpy as np
```

`numpy` — библиотека для численных операций.

Мы даём ей короткий псевдоним:

```python
np
```

Поэтому пишем:

```python
np.random.choice
```

вместо:

```python
numpy.random.choice
```

И:

```python
np.quantile
```

вместо:

```python
numpy.quantile
```

---

# 5. Импорт t-теста

```python
from scipy.stats import ttest_ind
```

Импортируется готовая функция независимого двухвыборочного t-теста.

Она будет применена не к исходным ошибкам, а к двум спискам bootstrap-квантилей.

---

# 6. Объявление функции

```python
def quantile_ttest(
```

Ключевое слово:

```python
def
```

создаёт функцию.

Имя функции должно быть точно:

```python
quantile_ttest
```

Проверяющая система будет искать именно это имя.

---

# 7. Параметры функции

```python
control: List[float],
experiment: List[float],
alpha: float = 0.05,
quantile: float = 0.95,
n_bootstraps: int = 1000,
```

- `control` — ошибки группы A;
- `experiment` — ошибки группы B;
- `alpha` — порог статистической значимости;
- `quantile` — уровень вычисляемого квантиля;
- `n_bootstraps` — количество повторений bootstrap.

Порядок и значения по умолчанию являются частью API задания.

---

# 8. Тип результата

```python
) -> Tuple[float, bool]:
```

Функция должна вернуть:

```python
(p_value, result)
```

Например:

```python
(0.0032, True)
```

---

# 9. Docstring

```python
"""
Bootstrapped t-test for quantiles of two samples.
"""
```

Это документационная строка.

Она объясняет, что функция реализует bootstrap t-тест для квантилей двух выборок.

---

# 10. Пустые списки результатов

```python
control_quantiles = []
experiment_quantiles = []
```

В них будут накапливаться квантильные оценки, полученные на каждой bootstrap-итерации.

После нескольких повторений списки могут выглядеть так:

```python
control_quantiles = [18.5, 20.0, 19.2]
experiment_quantiles = [14.2, 15.1, 13.8]
```

---

# 11. Цикл bootstrap

```python
for _ in range(n_bootstraps):
```

Если:

```python
n_bootstraps = 1000
```

тело цикла выполнится ровно 1000 раз.

Имя `_` используется потому, что номер текущей итерации нам не нужен.

---

# 12. Bootstrap control

```python
control_sample = np.random.choice(
    control,
    size=len(control),
    replace=True,
)
```

Разберём аргументы.

## Источник данных

```python
control
```

Элементы выбираются из контрольной выборки.

## Размер

```python
size=len(control)
```

Новая выборка имеет такой же размер, как исходная.

## Возвращение

```python
replace=True
```

Один исходный элемент может быть выбран несколько раз.

Например, из:

```python
[1, 2, 3, 4]
```

можно получить:

```python
[1, 1, 4, 2]
```

Число `1` выбрано два раза, а `3` не выбрано ни разу.

Это нормальное и необходимое поведение bootstrap.

---

# 13. Bootstrap experiment

```python
experiment_sample = np.random.choice(
    experiment,
    size=len(experiment),
    replace=True,
)
```

Экспериментальная группа пересэмплируется отдельно.

Обратите внимание:

```python
size=len(experiment)
```

а не `len(control)`.

Группы могут быть разного размера.

---

# 14. Расчёт квантиля

```python
np.quantile(control_sample, quantile)
```

Функция принимает:

1. выборку;
2. уровень квантиля от 0 до 1.

Примеры:

```python
quantile=0.95
```

95-й персентиль.

```python
quantile=0.50
```

медиана.

```python
quantile=0.05
```

5-й персентиль.

---

# 15. Добавление квантиля control

```python
control_quantiles.append(
    np.quantile(control_sample, quantile)
)
```

Метод `append` добавляет одно значение в конец списка.

После каждой итерации список становится длиннее на один элемент.

---

# 16. Добавление квантиля experiment

```python
experiment_quantiles.append(
    np.quantile(experiment_sample, quantile)
)
```

То же самое выполняется для группы B.

После цикла длины обоих списков равны:

```python
n_bootstraps
```

---

# 17. Независимый t-тест

```python
_, p_value = ttest_ind(
    control_quantiles,
    experiment_quantiles,
)
```

`ttest_ind` возвращает:

1. t-статистику;
2. p-value.

T-статистика по API не нужна, поэтому она записывается в `_`.

P-value сохраняется в переменную:

```python
p_value
```

---

# 18. Почему параметры SciPy не меняются

Задание просит bootstrapped t-тест и импортирует `ttest_ind`.

Поэтому вызывается стандартный вариант:

```python
ttest_ind(control_quantiles, experiment_quantiles)
```

Не следует самовольно добавлять:

```python
equal_var=False
```

или менять альтернативную гипотезу.

Автопроверка может сравнивать результат с эталоном на дефолтных параметрах.

---

# 19. Статистический вердикт

```python
result = bool(p_value < alpha)
```

Если:

```python
p_value = 0.01
alpha = 0.05
```

то:

```python
0.01 < 0.05
```

равно:

```python
True
```

Различие считается статистически значимым.

Если:

```python
p_value = 0.30
```

то результат:

```python
False
```

---

# 20. Почему используется параметр alpha

Автотест проверяет не только значение по умолчанию, но и:

```python
alpha=0.01
```

Поэтому неправильно писать:

```python
result = p_value < 0.05
```

Правильно:

```python
result = p_value < alpha
```

---

# 21. Возвращаемые типы

```python
return float(p_value), result
```

`float(p_value)` гарантирует обычный Python `float`.

`result` после `bool(...)` является обычным Python `bool`.

Итоговый объект:

```python
Tuple[float, bool]
```

---

# 22. Мини-пример одной bootstrap-итерации

Пусть:

```python
control = [1, 2, 3]
experiment = [5, 6, 7]
```

Возможные bootstrap-выборки:

```python
control_sample = [1, 1, 3]
experiment_sample = [5, 7, 7]
```

После этого вычисляются:

```python
np.quantile(control_sample, 0.95)
np.quantile(experiment_sample, 0.95)
```

Оба результата добавляются в соответствующие списки.

На следующей итерации создаются уже другие случайные выборки.

---

# 23. Почему результат немного меняется между запусками

В функции используется случайный выбор:

```python
np.random.choice
```

Поэтому набор bootstrap-реплик может меняться.

Для воспроизводимой ручной проверки можно перед вызовом написать:

```python
np.random.seed(42)
```

Но задавать seed внутри самой функции не нужно.

Автотест может самостоятельно задавать seed.

---

# 24. Частая ошибка: `replace=False`

Неправильно:

```python
replace=False
```

При полном размере получится только перестановка исходных данных.

Правильно:

```python
replace=True
```

---

# 25. Частая ошибка: неверный размер

Неправильно:

```python
size=n_bootstraps
```

`n_bootstraps` — число повторений, а не размер одной искусственной выборки.

Правильно:

```python
size=len(control)
size=len(experiment)
```

---

# 26. Частая ошибка: считать среднее

Неправильно:

```python
np.mean(control_sample)
```

Задание требует квантиль.

Правильно:

```python
np.quantile(control_sample, quantile)
```

---

# 27. Частая ошибка: жёстко использовать 0.95

Неправильно:

```python
np.quantile(sample, 0.95)
```

Автотест передаёт `quantile=0.05`.

Правильно:

```python
np.quantile(sample, quantile)
```

---

# 28. Частая ошибка: жёстко использовать 1000

Неправильно:

```python
for _ in range(1000):
```

Правильно:

```python
for _ in range(n_bootstraps):
```

---

# 29. Частая ошибка: объединять A и B

Нельзя делать:

```python
all_values = control + experiment
```

и пересэмплировать общий массив.

Группы должны сохраняться отдельно, иначе исчезает исследуемый эффект.

---

# 30. Частая ошибка: один список квантилей

Нельзя складывать квантильные оценки обеих групп в один список.

Нужны:

```python
control_quantiles
experiment_quantiles
```

Именно эти два списка сравнивает t-тест.

---

# 31. Частая ошибка: перепутать результаты SciPy

Неправильно:

```python
p_value, _ = ttest_ind(...)
```

В `p_value` попадёт t-статистика.

Правильно:

```python
_, p_value = ttest_ind(...)
```

---

# 32. Частая ошибка: неверное сравнение

Неправильно:

```python
result = p_value > alpha
```

Правильно:

```python
result = p_value < alpha
```

---

# 33. Частая ошибка: вернуть только bool

Неправильно:

```python
return result
```

Правильно:

```python
return float(p_value), result
```

---

# 34. Частая ошибка: использовать `print`

Автотест ожидает возвращаемый результат.

Неправильно:

```python
print(p_value, result)
```

Правильно:

```python
return float(p_value), result
```

---

# 35. Частая ошибка: изменить API

Нельзя менять:

- имя `quantile_ttest`;
- порядок параметров;
- значения параметров по умолчанию;
- порядок возвращаемых значений.

Иначе автопроверка может начислить 0 баллов.

---

# 36. Почему решение не векторизовано

Можно сгенерировать большую матрицу индексов и вычислить все квантили сразу.

Но простая версия с циклом:

- соответствует примеру курса;
- понятнее новичку;
- использует меньше сложных конструкций;
- достаточна для 1000 повторений;
- легче проверить.

---

# 37. Ручная проверка A/A

В отдельном тестовом файле:

```python
import numpy as np

from gp_page_2_quantile_ttest_solution import quantile_ttest


np.random.seed(42)

sample = [1.0, 2.0, 3.0, 4.0, 5.0]

print(
    quantile_ttest(
        sample,
        sample,
    )
)
```

Для одинаковых распределений обычно ожидается:

```python
result is False
```

---

# 38. Ручная проверка A/B

```python
np.random.seed(42)

control = [1.0, 2.0, 3.0, 40.0, 50.0, 60.0]
experiment = [1.0, 2.0, 3.0, 8.0, 10.0, 12.0]

print(
    quantile_ttest(
        control,
        experiment,
        quantile=0.95,
    )
)
```

Верхние хвосты сильно различаются, поэтому p-value должен быть маленьким.

---

# 39. Проверка `quantile=0.05`

```python
quantile_ttest(
    control,
    experiment,
    quantile=0.05,
)
```

Переданное значение используется непосредственно в:

```python
np.quantile(sample, quantile)
```

---

# 40. Проверка `alpha=0.01`

```python
quantile_ttest(
    control,
    experiment,
    alpha=0.01,
)
```

Теперь критерий значимости строже:

```python
p_value < 0.01
```

---

# 41. Проверка типов

```python
p_value, result = quantile_ttest(
    control,
    experiment,
)

print(type(p_value))
print(type(result))
```

Ожидается:

```text
<class 'float'>
<class 'bool'>
```

---

# 42. PEP8

Решение соблюдает базовые требования:

- стандартные импорты идут первыми;
- сторонние библиотеки отделены пустой строкой;
- перед функцией две пустые строки;
- длинные вызовы разбиты на строки;
- используются понятные имена;
- сохранён docstring;
- нет лишнего тестового кода;
- нет неиспользуемых импортов.

---

# 43. Методологическая оговорка

Для учебной платформы нужно строго реализовать:

```text
bootstrap квантилей
→ ttest_ind по bootstrap-оценкам
```

В реальной аналитике часто строят bootstrap-распределение **разницы квантилей** и доверительный интервал либо используют пермутационный тест.

Но замена метода в отправляемом файле может не совпасть с эталоном курса.

---

# 44. Финальный чек-лист

Перед загрузкой проверьте:

- файл `.py`;
- функция называется `quantile_ttest`;
- `alpha=0.05`;
- `quantile=0.95`;
- `n_bootstraps=1000`;
- используется `np.random.choice`;
- установлено `replace=True`;
- размер каждой bootstrap-выборки равен размеру своей группы;
- группы пересэмплируются отдельно;
- используется `np.quantile`;
- используется переданный параметр `quantile`;
- цикл использует `n_bootstraps`;
- вызывается `ttest_ind`;
- p-value взят вторым результатом;
- используется `p_value < alpha`;
- возвращается `float`, затем `bool`;
- нет `print`;
- нет тестовых данных.

---

# 45. Финальное решение ещё раз

```python
from typing import List, Tuple

import numpy as np
from scipy.stats import ttest_ind


def quantile_ttest(
    control: List[float],
    experiment: List[float],
    alpha: float = 0.05,
    quantile: float = 0.95,
    n_bootstraps: int = 1000,
) -> Tuple[float, bool]:
    """
    Bootstrapped t-test for quantiles of two samples.
    """
    control_quantiles = []
    experiment_quantiles = []

    for _ in range(n_bootstraps):
        control_sample = np.random.choice(
            control,
            size=len(control),
            replace=True,
        )
        experiment_sample = np.random.choice(
            experiment,
            size=len(experiment),
            replace=True,
        )

        control_quantiles.append(
            np.quantile(control_sample, quantile)
        )
        experiment_quantiles.append(
            np.quantile(experiment_sample, quantile)
        )

    _, p_value = ttest_ind(
        control_quantiles,
        experiment_quantiles,
    )
    result = bool(p_value < alpha)

    return float(p_value), result
```

Это минимальное решение, которое буквально соответствует API и алгоритму задания.

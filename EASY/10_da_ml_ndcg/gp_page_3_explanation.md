# gp_page_3 — Пошаговое объяснение кода DCG с полного нуля

# 1. Какой файл загружать в проверяющую систему

Нужно загружать:

```text
gp_page_3_solution.py
```

Markdown-файлы предназначены для обучения.

Python-файл содержит точную функцию, которую вызовут автотесты.

---

# 2. Полный код решения

```python
"""Calculate the Discounted Cumulative Gain ranking metric."""

from typing import List

import numpy as np


def discounted_cumulative_gain(
    relevance: List[float],
    k: int,
    method: str = "standard",
) -> float:
    """Calculate Discounted Cumulative Gain at k.

    Parameters
    ----------
    relevance : List[float]
        Video relevance list.
    k : int
        Number of relevance values to include.
    method : str, optional
        Metric implementation method:
        "standard" uses relevance as gain;
        "industry" uses 2 ** relevance - 1 as gain.

    Returns
    -------
    float
        Discounted Cumulative Gain score.

    Raises
    ------
    ValueError
        If method is neither "standard" nor "industry".
    """
    if method not in ("standard", "industry"):
        raise ValueError

    relevance_array = np.asarray(relevance[:k], dtype=float)
    positions = np.arange(1, relevance_array.size + 1)
    discounts = np.log2(positions + 1)

    if method == "industry":
        relevance_array = np.power(2, relevance_array) - 1

    score = np.sum(relevance_array / discounts)
    return float(score)
```

---

# 3. Docstring модуля

```python
"""Calculate the Discounted Cumulative Gain ranking metric."""
```

Это документация всего файла.

Она сообщает назначение модуля.

Она нужна для:

- читаемости;
- Pylint;
- документации;
- поддержки кода.

---

# 4. Импорт `List`

```python
from typing import List
```

`List` используется в аннотации:

```python
relevance: List[float]
```

Это означает:

> `relevance` ожидается как список вещественных чисел.

Пример:

```python
[0.99, 0.94, 0.88]
```

---

# 5. Импорт NumPy

```python
import numpy as np
```

NumPy используется для:

- преобразования списка в массив;
- построения последовательности позиций;
- вычисления логарифмов;
- возведения в степень;
- суммирования.

`np` — стандартное короткое имя NumPy.

---

# 6. Почему импорты разделены пустой строкой

`typing` относится к стандартной библиотеке.

`numpy` — сторонняя библиотека.

PEP8 рекомендует разделять такие группы пустой строкой.

---

# 7. Объявление функции

```python
def discounted_cumulative_gain(
    relevance: List[float],
    k: int,
    method: str = "standard",
) -> float:
```

Сигнатура перенесена на несколько строк, чтобы не нарушать ограничение длины строки.

Это не меняет API.

---

# 8. Имя функции

```python
discounted_cumulative_gain
```

Имя должно совпадать с заданием.

Автотест импортирует именно его.

Нельзя заменить на:

```python
dcg
calculate_dcg
discount_gain
```

---

# 9. Аргумент `relevance`

```python
relevance: List[float]
```

Это список релевантностей в фактическом порядке выдачи.

Пример:

```python
[0.99, 0.83, 0.89]
```

Означает:

- позиция 1: `0.99`;
- позиция 2: `0.83`;
- позиция 3: `0.89`.

Список нельзя сортировать.

---

# 10. Аргумент `k`

```python
k: int
```

Показывает число первых объектов для оценки.

Пример:

```python
k = 5
```

Означает:

> учитывать только первые пять объектов.

---

# 11. Аргумент `method`

```python
method: str = "standard"
```

`str` означает строку.

Значение по умолчанию:

```python
"standard"
```

Поэтому вызов:

```python
discounted_cumulative_gain(relevance, 5)
```

равносилен:

```python
discounted_cumulative_gain(relevance, 5, "standard")
```

---

# 12. Возвращаемый тип

```python
-> float
```

Функция должна вернуть одно вещественное число.

---

# 13. Docstring функции

Docstring описывает:

- параметры;
- значения метода;
- возвращаемый результат;
- возможное исключение.

Раздел `Raises` важен, потому что функция обязана вызвать `ValueError` при неправильном методе.

---

# 14. Проверка метода

```python
if method not in ("standard", "industry"):
    raise ValueError
```

Разберём буквально.

## `("standard", "industry")`

Это кортеж допустимых строк.

## `method not in ...`

Проверяет, отсутствует ли переданный метод среди разрешённых.

## `if`

Выполняет блок только при истинном условии.

## `raise ValueError`

Останавливает функцию и выбрасывает исключение.

---

# 15. Почему ValueError без текста

Условие специально говорит:

```python
raise ValueError
```

без дополнений.

Правильно:

```python
raise ValueError
```

Неправильно:

```python
raise ValueError("Incorrect method")
```

Неправильно:

```python
raise ValueError(method)
```

Даже полезное пояснение может не пройти строгий тест.

---

# 16. Какие значения проходят проверку

Допустимы:

```python
"standard"
```

```python
"industry"
```

Не допустимы:

```python
"Standard"
"INDUSTRY"
"dcg"
""
None
```

Условие не просит приводить регистр или исправлять ввод.

---

# 17. Выбор первых `k` значений

```python
relevance[:k]
```

Для:

```python
relevance = [0.99, 0.94, 0.88, 0.74, 0.71, 0.68]
k = 5
```

получаем:

```python
[0.99, 0.94, 0.88, 0.74, 0.71]
```

Шестой объект не участвует.

---

# 18. Преобразование в NumPy-массив

```python
relevance_array = np.asarray(relevance[:k], dtype=float)
```

## `np.asarray`

Преобразует последовательность в NumPy-массив.

## `dtype=float`

Приводит элементы к вещественному типу.

## Зачем массив

Он позволяет выполнить операцию сразу над всеми элементами:

```python
relevance_array / discounts
```

---

# 19. Что находится в `relevance_array`

Для примера:

```python
array([0.99, 0.94, 0.88, 0.74, 0.71])
```

Это уже не обычный список, а NumPy-массив.

---

# 20. Число выбранных элементов

```python
relevance_array.size
```

Возвращает количество элементов.

Для пяти релевантностей:

```python
relevance_array.size == 5
```

Это важнее, чем слепо использовать `k`.

Если `k = 10`, а элементов 3, размер массива будет 3.

---

# 21. Построение позиций

```python
positions = np.arange(1, relevance_array.size + 1)
```

## `np.arange(start, stop)`

Создаёт числа от `start` до `stop`, не включая `stop`.

Для размера 5:

```python
np.arange(1, 6)
```

получаем:

```python
array([1, 2, 3, 4, 5])
```

Это позиции выдачи.

---

# 22. Почему начало равно 1

Математические позиции начинаются с 1.

Первый объект имеет позицию 1, а не 0.

Если начать с 0, формула будет неверной.

---

# 23. Почему добавляется `+ 1` к размеру

Правая граница `np.arange` не включается.

Чтобы получить позицию 5, нужно остановиться на 6:

```python
np.arange(1, 6)
```

Поэтому:

```python
relevance_array.size + 1
```

---

# 24. Расчёт discounts

```python
discounts = np.log2(positions + 1)
```

Для позиций:

```python
[1, 2, 3, 4, 5]
```

сначала прибавляется 1:

```python
[2, 3, 4, 5, 6]
```

Затем считается логарифм по основанию 2:

```python
[
    log2(2),
    log2(3),
    log2(4),
    log2(5),
    log2(6),
]
```

Приблизительно:

```python
[1.0, 1.58496, 2.0, 2.32193, 2.58496]
```

---

# 25. Почему именно `np.log2`

В формуле указан логарифм по основанию 2.

Поэтому правильно:

```python
np.log2(...)
```

Неправильно:

```python
np.log(...)
```

`np.log` вычисляет натуральный логарифм.

---

# 26. Почему `positions + 1`

Без `+ 1` первая позиция дала бы:

```python
log2(1) = 0
```

И затем произошло бы деление на ноль.

С `+ 1`:

```python
log2(2) = 1
```

Первый объект не штрафуется.

---

# 27. Ветвление для industry

```python
if method == "industry":
    relevance_array = np.power(2, relevance_array) - 1
```

Если метод standard, этот блок пропускается.

Если industry, выполняется преобразование gain.

---

# 28. Что делает `np.power`

```python
np.power(2, relevance_array)
```

Возводит 2 в степень каждого элемента.

Для:

```python
[0.0, 1.0, 2.0, 3.0]
```

получим:

```python
[1.0, 2.0, 4.0, 8.0]
```

После вычитания 1:

```python
[0.0, 1.0, 3.0, 7.0]
```

---

# 29. Почему standard не требует отдельного блока

Для standard gain уже равен:

```python
relevance_array
```

Поэтому можно не выполнять преобразование.

После проверки method остаются только два варианта.

Если industry — меняем gain.

Иначе это гарантированно standard.

---

# 30. Общий расчёт score

```python
score = np.sum(relevance_array / discounts)
```

NumPy делит элементы попарно.

Для трёх элементов:

```python
relevance_array = [0.99, 0.94, 0.88]
discounts = [1.0, 1.58496, 2.0]
```

Результат деления:

```python
[
    0.99 / 1.0,
    0.94 / 1.58496,
    0.88 / 2.0,
]
```

Приблизительно:

```python
[0.99, 0.5931, 0.44]
```

`np.sum` складывает:

```python
2.0231
```

---

# 31. Возврат результата

```python
return float(score)
```

NumPy может вернуть:

```python
numpy.float64
```

`float(score)` преобразует значение в стандартный Python `float`.

Это соответствует аннотации:

```python
-> float
```

---

# 32. Полный проход standard

Вызов:

```python
discounted_cumulative_gain(
    [0.99, 0.94, 0.88],
    3,
    "standard",
)
```

## Шаг 1

Метод допустим.

## Шаг 2

Массив:

```python
[0.99, 0.94, 0.88]
```

## Шаг 3

Позиции:

```python
[1, 2, 3]
```

## Шаг 4

Discounts:

```python
[1.0, 1.58496, 2.0]
```

## Шаг 5

Industry-преобразование не выполняется.

## Шаг 6

Деление:

```python
[0.99, 0.5931, 0.44]
```

## Шаг 7

Сумма:

```python
2.02307396835717
```

---

# 33. Полный проход industry

Вызов:

```python
discounted_cumulative_gain(
    [3.0, 2.0, 1.0],
    3,
    "industry",
)
```

## Gain

```python
2 ** 3 - 1 = 7
2 ** 2 - 1 = 3
2 ** 1 - 1 = 1
```

Получаем:

```python
[7.0, 3.0, 1.0]
```

## Discounts

```python
[1.0, 1.58496, 2.0]
```

## Вклады

```python
[
    7 / 1,
    3 / 1.58496,
    1 / 2,
]
```

## Сумма

Примерно:

```python
9.3928
```

---

# 34. Проверка примера задания

```python
relevance = [0.99, 0.94, 0.88, 0.74, 0.71, 0.68]
k = 5
method = "standard"

result = discounted_cumulative_gain(relevance, k, method)
print(result)
```

Результат:

```text
2.6164401144680056
```

То есть ожидаемое:

```text
2.6164...
```

---

# 35. Проверка метода по умолчанию

Эти вызовы эквивалентны:

```python
discounted_cumulative_gain(relevance, 5)
```

```python
discounted_cumulative_gain(relevance, 5, "standard")
```

Потому что default:

```python
method="standard"
```

---

# 36. Проверка неправильного метода

```python
discounted_cumulative_gain(
    [0.9, 0.8],
    2,
    "wrong",
)
```

Функция выполнит:

```python
raise ValueError
```

Вычисления дальше не продолжатся.

---

# 37. Проверка `k = 0`

```python
discounted_cumulative_gain([0.9, 0.8], 0)
```

Срез:

```python
[]
```

Позиции:

```python
[]
```

Discounts:

```python
[]
```

Сумма:

```python
0.0
```

---

# 38. Проверка пустого списка

```python
discounted_cumulative_gain([], 5)
```

Результат:

```python
0.0
```

---

# 39. Проверка `k` больше длины

```python
discounted_cumulative_gain([0.9, 0.8], 10)
```

Используются только два существующих элемента.

Позиции строятся как:

```python
[1, 2]
```

Это важно: размеры массивов совпадают.

---

# 40. Почему нельзя строить позиции через `k`

Плохой вариант:

```python
positions = np.arange(1, k + 1)
```

При:

```python
relevance = [0.9, 0.8]
k = 10
```

получится:

- relevance_array длины 2;
- positions длины 10.

Деление массивов завершится ошибкой формы.

Наш вариант использует:

```python
relevance_array.size
```

поэтому размеры всегда совпадают.

---

# 41. Почему нельзя сортировать

Плохой код:

```python
relevance_array = np.sort(relevance_array)[::-1]
```

Он меняет порядок модели.

DCG должен оценивать именно тот порядок, который увидел пользователь.

Сортировка будет нужна при IDCG, а не здесь.

---

# 42. Почему нельзя округлять

Плохой код:

```python
return round(float(score), 4)
```

Условие показывает `2.6164...`, но многоточие означает продолжение числа, а не требование округлить до четырёх знаков.

Нужно вернуть полную точность.

---

# 43. Почему нельзя использовать `sum(relevance)`

Это:

- игнорирует discount;
- игнорирует `k`;
- фактически считает CG, а не DCG.

---

# 44. Почему нельзя использовать один знаменатель

Неправильно:

```python
np.sum(relevance_array) / np.log2(k + 1)
```

В DCG каждый объект имеет собственный позиционный штраф.

Нужно:

```python
relevance_array / discounts
```

а затем сумма.

---

# 45. Почему решение векторизовано

Векторизация означает, что операции применяются сразу ко всему массиву.

Вместо ручного цикла:

```python
score = 0.0

for position, value in enumerate(relevance[:k], start=1):
    score += value / np.log2(position + 1)
```

мы используем:

```python
score = np.sum(relevance_array / discounts)
```

Преимущества:

- компактность;
- наглядное соответствие формуле;
- меньше ручной логики;
- привычный стиль NumPy.

---

# 46. Был бы цикл неправильным?

Нет.

Цикл мог бы быть математически правильным.

Но предоставленный вариант:

- короткий;
- понятный;
- использует импорт NumPy;
- хорошо проходит Pylint;
- естественен для DA/ML-задачи.

---

# 47. PEP8 и Pylint

В решении соблюдены:

- module docstring;
- function docstring;
- `snake_case`;
- группировка импортов;
- две пустые строки перед функцией;
- перенос длинной сигнатуры;
- понятные имена;
- отсутствие неиспользуемых импортов;
- явный возврат `float`.

---

# 48. Почему решение должно получить полный балл

## Корректность

- standard formula реализована;
- industry formula реализована;
- используется `log2`;
- позиции начинаются с 1;
- учитываются первые `k`;
- invalid method вызывает ValueError;
- ValueError без сообщения;
- возвращается одно число.

## Качество

- API сохранён;
- код компактный;
- PEP8 соблюдён;
- docstrings присутствуют;
- переменные названы осмысленно;
- нет лишней логики.

---

# 49. Что нужно запомнить

Standard gain:

```python
gain = relevance
```

Industry gain:

```python
gain = 2 ** relevance - 1
```

Discount:

```python
np.log2(position + 1)
```

Полная идея:

```python
sum(gain / discount)
```

И главное требование обработки ошибки:

```python
raise ValueError
```

без текста.

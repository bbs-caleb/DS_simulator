# gp_page_4 — Пошаговое объяснение решения nDCG с полного нуля

# 1. Какой файл отправлять в систему

Для сдачи нужен файл:

```text
gp_page_4_solution.py
```

Именно этот Python-файл содержит функцию, которую вызовут автотесты.

Markdown-файлы нужны для подробного обучения и не заменяют `.py`.

---

# 2. Полный код решения

```python
"""Calculate the Normalized Discounted Cumulative Gain metric."""

from typing import List

import numpy as np


def normalized_dcg(
    relevance: List[float],
    k: int,
    method: str = "standard",
) -> float:
    """Calculate Normalized Discounted Cumulative Gain at k.

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
        Normalized Discounted Cumulative Gain score.

    Raises
    ------
    ValueError
        If method is neither "standard" nor "industry".
    """
    if method not in ("standard", "industry"):
        raise ValueError

    relevance_array = np.asarray(relevance, dtype=float)
    actual_relevance = relevance_array[:k]
    ideal_relevance = np.sort(relevance_array)[::-1][:k]

    positions = np.arange(1, actual_relevance.size + 1)
    discounts = np.log2(positions + 1)

    if method == "industry":
        actual_gain = np.power(2, actual_relevance) - 1
        ideal_gain = np.power(2, ideal_relevance) - 1
    else:
        actual_gain = actual_relevance
        ideal_gain = ideal_relevance

    actual_dcg = np.sum(actual_gain / discounts)
    ideal_dcg = np.sum(ideal_gain / discounts)

    if ideal_dcg == 0:
        return 0.0

    score = actual_dcg / ideal_dcg
    return float(score)
```

Теперь разберём каждую часть.

---

# 3. Docstring всего файла

```python
"""Calculate the Normalized Discounted Cumulative Gain metric."""
```

Это документация модуля.

Она кратко объясняет:

> Этот файл вычисляет nDCG.

Docstring полезен для:

- людей;
- IDE;
- документации;
- Pylint;
- поддержки проекта.

---

# 4. Импорт `List`

```python
from typing import List
```

`List` используется в type hint:

```python
relevance: List[float]
```

Это означает:

> Ожидается список, содержащий вещественные числа.

Пример:

```python
[0.99, 0.94, 0.74, 0.88]
```

Type hint не выполняет вычисление.

Он описывает контракт функции.

---

# 5. Импорт NumPy

```python
import numpy as np
```

NumPy нужен для:

- массивов;
- сортировки;
- построения позиций;
- логарифма;
- возведения в степень;
- суммирования.

`np` — общепринятое сокращение.

---

# 6. Почему импорты разделены

```python
from typing import List

import numpy as np
```

`typing` — стандартная библиотека.

`numpy` — сторонняя библиотека.

PEP8 рекомендует разделять группы импортов пустой строкой.

---

# 7. Сигнатура функции

```python
def normalized_dcg(
    relevance: List[float],
    k: int,
    method: str = "standard",
) -> float:
```

Сигнатура перенесена на несколько строк для читаемости и PEP8.

API при этом остаётся тем же.

---

# 8. Имя функции

```python
normalized_dcg
```

Это точное имя из задания.

Нельзя заменить на:

```python
ndcg
normalized_discounted_gain
calculate_ndcg
```

Проверяющая система ищет именно `normalized_dcg`.

---

# 9. Аргумент `relevance`

```python
relevance: List[float]
```

Это список истинных оценок релевантности в фактическом порядке модели.

Пример:

```python
[0.99, 0.94, 0.74, 0.88, 0.71]
```

Порядок важен.

В нём видно, что `0.88` ошибочно находится ниже `0.74`.

---

# 10. Аргумент `k`

```python
k: int
```

Количество первых позиций, которые входят в оценку.

Пример:

```python
k = 5
```

Означает:

> Посчитать nDCG по первым пяти позициям.

---

# 11. Аргумент `method`

```python
method: str = "standard"
```

`method` — строка.

Допустимы:

```python
"standard"
```

и:

```python
"industry"
```

Значение по умолчанию — standard.

Поэтому:

```python
normalized_dcg(relevance, 5)
```

равносильно:

```python
normalized_dcg(relevance, 5, "standard")
```

---

# 12. Возвращаемый тип

```python
-> float
```

Функция должна вернуть одно вещественное число.

Например:

```python
0.9962906539247515
```

---

# 13. Docstring функции

Docstring описывает:

- входные параметры;
- методы;
- возвращаемый тип;
- исключение.

Это часть качественного API.

---

# 14. Проверка метода

```python
if method not in ("standard", "industry"):
    raise ValueError
```

Разбираем.

## Кортеж разрешённых значений

```python
("standard", "industry")
```

## Проверка принадлежности

```python
method not in ...
```

Возвращает `True`, если значение не разрешено.

## Исключение

```python
raise ValueError
```

немедленно останавливает функцию.

---

# 15. Почему ValueError без сообщения

Условие подчёркивает:

```python
raise ValueError
```

без строк.

Правильно:

```python
raise ValueError
```

Неправильно:

```python
raise ValueError("Wrong method")
```

Неправильно:

```python
raise ValueError(method)
```

Строгий тест может проверять пустой текст исключения.

---

# 16. Преобразование исходных данных в массив

```python
relevance_array = np.asarray(relevance, dtype=float)
```

## `np.asarray`

Преобразует входную последовательность в NumPy-массив.

## `dtype=float`

Приводит значения к вещественному типу.

Пример:

```python
relevance = [1, 0.5, 0]
```

После преобразования:

```python
array([1.0, 0.5, 0.0])
```

---

# 17. Почему в массив преобразуется весь список

Для фактического DCG нужны первые `k`.

Но для идеального DCG нужно сначала рассмотреть весь список и выбрать глобально лучшие `k` объектов.

Поэтому нельзя сразу написать:

```python
np.asarray(relevance[:k])
```

Иначе хороший объект за пределами top-k потеряется и не попадёт в IDCG.

---

# 18. Фактический top-k

```python
actual_relevance = relevance_array[:k]
```

Пример:

```python
relevance_array = [0.99, 0.94, 0.74, 0.88, 0.71, 0.68]
k = 5
```

Получаем:

```python
actual_relevance = [0.99, 0.94, 0.74, 0.88, 0.71]
```

Это именно тот порядок, который показала модель.

---

# 19. Почему actual нельзя сортировать

Если отсортировать actual, мы исправим ошибку модели вручную.

Тогда фактический порядок станет идеальным.

nDCG почти всегда будет `1.0`.

Метрика потеряет смысл.

---

# 20. Построение идеальной выдачи

```python
ideal_relevance = np.sort(relevance_array)[::-1][:k]
```

Эта строка состоит из трёх операций.

---

# 21. Операция 1: сортировка

```python
np.sort(relevance_array)
```

NumPy по умолчанию сортирует по возрастанию.

Для:

```python
[0.99, 0.94, 0.74, 0.88, 0.71, 0.68]
```

получаем:

```python
[0.68, 0.71, 0.74, 0.88, 0.94, 0.99]
```

---

# 22. Операция 2: разворот

```python
[::-1]
```

Разворачивает массив.

Получаем порядок по убыванию:

```python
[0.99, 0.94, 0.88, 0.74, 0.71, 0.68]
```

---

# 23. Операция 3: выбор top-k

```python
[:k]
```

При `k = 5`:

```python
[0.99, 0.94, 0.88, 0.74, 0.71]
```

Это идеальная первая пятёрка.

---

# 24. Почему порядок операций критически важен

Правильно:

```python
np.sort(relevance_array)[::-1][:k]
```

То есть:

1. сортировать всё;
2. развернуть;
3. взять top-k.

Неправильно:

```python
np.sort(relevance_array[:k])[::-1]
```

То есть:

1. сначала выбросить всё после k;
2. затем сортировать только оставшееся.

Рассмотрим:

```python
relevance = [0.9, 0.8, 0.1, 1.0]
k = 3
```

Неправильный ideal:

```python
[0.9, 0.8, 0.1]
```

Правильный ideal:

```python
[1.0, 0.9, 0.8]
```

Объект `1.0` должен влиять на идеал, даже если модель поставила его на четвёртое место.

---

# 25. Построение позиций

```python
positions = np.arange(1, actual_relevance.size + 1)
```

Для пяти элементов:

```python
actual_relevance.size == 5
```

Получаем:

```python
np.arange(1, 6)
```

Результат:

```python
[1, 2, 3, 4, 5]
```

---

# 26. Почему используется фактический размер

Если:

```python
k = 10
```

а список содержит 4 элемента, actual содержит только 4 элемента.

Тогда позиции должны быть:

```python
[1, 2, 3, 4]
```

Если строить позиции через `k`, размеры массивов не совпадут.

Поэтому используется:

```python
actual_relevance.size
```

---

# 27. Расчёт discounts

```python
discounts = np.log2(positions + 1)
```

Для позиций:

```python
[1, 2, 3, 4, 5]
```

после `+ 1`:

```python
[2, 3, 4, 5, 6]
```

После логарифма:

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

# 28. Почему discounts одинаковые для actual и ideal

Обе выдачи оцениваются на одинаковых позициях:

```text
1, 2, 3, ..., k
```

Мы сравниваем только порядок релевантностей.

Если использовать разные discounts, сравнение станет нечестным.

---

# 29. Ветвление по методу

```python
if method == "industry":
    ...
else:
    ...
```

После первой проверки возможны только два метода.

Поэтому `else` гарантированно означает standard.

---

# 30. Industry gain

```python
actual_gain = np.power(2, actual_relevance) - 1
ideal_gain = np.power(2, ideal_relevance) - 1
```

Для каждого значения считается:

\[
2^{rel} - 1
\]

Важно преобразовать и actual, и ideal одинаково.

---

# 31. Почему нужны две переменные gain

```python
actual_gain
ideal_gain
```

Они содержат один и тот же набор значений релевантности, но в разном порядке.

Это делает последующий код понятным:

```python
actual_gain / discounts
ideal_gain / discounts
```

---

# 32. Standard gain

```python
else:
    actual_gain = actual_relevance
    ideal_gain = ideal_relevance
```

Для standard gain равен исходной релевантности.

Никакого экспоненциального преобразования не нужно.

---

# 33. Расчёт actual DCG

```python
actual_dcg = np.sum(actual_gain / discounts)
```

NumPy выполняет поэлементное деление.

Пример:

```python
actual_gain = [0.99, 0.94, 0.74, 0.88, 0.71]
discounts = [1.0, 1.58496, 2.0, 2.32193, 2.58496]
```

Получаются вклады каждого места.

Затем `np.sum` их складывает.

---

# 34. Расчёт IDCG

```python
ideal_dcg = np.sum(ideal_gain / discounts)
```

Используется тот же discount, но ideal gain расположен в правильном порядке.

По определению этот результат должен быть не меньше actual DCG при неотрицательных labels.

---

# 35. Проверка деления на ноль

```python
if ideal_dcg == 0:
    return 0.0
```

Если все gains нулевые, IDCG равен нулю.

Без проверки выполнялось бы:

```python
0 / 0
```

Результатом мог стать:

```python
nan
```

и warning.

---

# 36. Почему возвращается 0.0

В этом решении запрос без релевантных объектов получает:

```python
0.0
```

Это:

- предотвращает `NaN`;
- сохраняет числовой тип;
- не завышает среднее;
- делает отсутствие релевантности заметным.

В настоящей компании правило обязательно документируется.

---

# 37. Расчёт нормализованного score

```python
score = actual_dcg / ideal_dcg
```

Это точная формула:

\[
nDCG =
\frac{DCG}{IDCG}
\]

Не наоборот.

---

# 38. Почему нельзя делить IDCG на DCG

Если сделать:

```python
ideal_dcg / actual_dcg
```

для неидеальной выдачи значение будет больше 1.

Но nDCG должен показывать долю достигнутого идеала.

Правильно:

```python
actual / ideal
```

---

# 39. Возврат обычного float

```python
return float(score)
```

NumPy может вернуть:

```python
numpy.float64
```

`float(score)` преобразует его в стандартный Python-тип.

Это соответствует:

```python
-> float
```

---

# 40. Полный проход примера

Вызов:

```python
normalized_dcg(
    [0.99, 0.94, 0.74, 0.88, 0.71, 0.68],
    5,
    "standard",
)
```

## Шаг 1. Проверка метода

`standard` разрешён.

## Шаг 2. Массив

```python
[0.99, 0.94, 0.74, 0.88, 0.71, 0.68]
```

## Шаг 3. Actual top-5

```python
[0.99, 0.94, 0.74, 0.88, 0.71]
```

## Шаг 4. Ideal top-5

```python
[0.99, 0.94, 0.88, 0.74, 0.71]
```

## Шаг 5. Позиции

```python
[1, 2, 3, 4, 5]
```

## Шаг 6. Discounts

```python
[1.0, 1.58496, 2.0, 2.32193, 2.58496]
```

## Шаг 7. Standard gains

Они равны relevance.

## Шаг 8. Actual DCG

```python
2.6067348325982804
```

## Шаг 9. Ideal DCG

```python
2.6164401144680056
```

## Шаг 10. Деление

```python
2.6067348325982804 / 2.6164401144680056
```

Результат:

```python
0.9962906539247512
```

---

# 41. Почему результат не округляется

В условии:

```text
0.9962...
```

Многоточие означает, что число продолжается.

Это не команда округлить до четырёх знаков.

Неправильно:

```python
return round(score, 4)
```

Правильно вернуть полную точность.

---

# 42. Проверка идеального порядка

```python
normalized_dcg(
    [0.99, 0.94, 0.88, 0.74],
    4,
)
```

Фактический и идеальный порядок совпадают.

Поэтому:

```python
1.0
```

или значение, численно очень близкое к 1.

---

# 43. Проверка плохого порядка

```python
normalized_dcg(
    [0.0, 0.2, 0.5, 1.0],
    4,
)
```

Идеальный порядок:

```python
[1.0, 0.5, 0.2, 0.0]
```

Высокие значения в actual находятся внизу.

Поэтому nDCG заметно ниже 1.

---

# 44. Проверка объекта за пределами k

```python
normalized_dcg(
    [0.9, 0.8, 0.1, 1.0],
    3,
)
```

Actual:

```python
[0.9, 0.8, 0.1]
```

Ideal:

```python
[1.0, 0.9, 0.8]
```

Метрика наказывает систему за то, что лучший объект оказался четвёртым и не вошёл в top-3.

---

# 45. Проверка всех нулей

```python
normalized_dcg(
    [0.0, 0.0, 0.0],
    3,
)
```

Actual DCG:

```python
0.0
```

IDCG:

```python
0.0
```

Срабатывает:

```python
return 0.0
```

---

# 46. Проверка пустого списка

```python
normalized_dcg([], 5)
```

Actual и ideal пустые.

Обе суммы равны нулю.

Результат:

```python
0.0
```

---

# 47. Проверка k = 0

```python
normalized_dcg([0.9, 0.8], 0)
```

Срезы пустые.

Результат:

```python
0.0
```

---

# 48. Проверка k больше длины

```python
normalized_dcg([0.9, 0.8], 10)
```

Используются все доступные два объекта.

Позиции:

```python
[1, 2]
```

Если порядок идеальный, результат:

```python
1.0
```

---

# 49. Проверка industry

```python
normalized_dcg(
    [3.0, 1.0, 2.0],
    3,
    "industry",
)
```

Actual gains:

```python
[
    2 ** 3 - 1,
    2 ** 1 - 1,
    2 ** 2 - 1,
]
```

То есть:

```python
[7.0, 1.0, 3.0]
```

Ideal relevance:

```python
[3.0, 2.0, 1.0]
```

Ideal gains:

```python
[7.0, 3.0, 1.0]
```

Затем actual DCG делится на ideal DCG.

---

# 50. Проверка неправильного метода

```python
normalized_dcg(
    [0.9, 0.8],
    2,
    "wrong",
)
```

Должен возникнуть:

```python
ValueError
```

С пустым текстом.

---

# 51. Типичная ошибка: сортировка только top-k

Неправильно:

```python
ideal_relevance = np.sort(actual_relevance)[::-1]
```

Почему:

- actual уже обрезан;
- лучший объект может находиться после позиции k;
- IDCG получится заниженным;
- nDCG получится искусственно высоким.

Правильно:

```python
ideal_relevance = np.sort(relevance_array)[::-1][:k]
```

---

# 52. Типичная ошибка: один gain для двух методов

Нельзя всегда писать:

```python
gain = relevance
```

Для industry нужно:

```python
2 ** relevance - 1
```

---

# 53. Типичная ошибка: разные методы actual и ideal

Неправильно:

```python
actual_gain = actual_relevance
ideal_gain = 2 ** ideal_relevance - 1
```

Тогда числитель и знаменатель находятся на разных шкалах.

Нормализация теряет смысл.

---

# 54. Типичная ошибка: забыть сортировку по убыванию

```python
np.sort(relevance_array)[:k]
```

возьмёт самые маленькие значения.

Это худший, а не идеальный порядок.

Нужно:

```python
np.sort(relevance_array)[::-1][:k]
```

---

# 55. Типичная ошибка: печать вместо return

Неправильно:

```python
print(score)
```

Автотест получит:

```python
None
```

Правильно:

```python
return float(score)
```

---

# 56. Типичная ошибка: изменение исходного списка

Например:

```python
relevance.sort(reverse=True)
```

Этот метод изменяет список пользователя на месте.

После вызова функции исходные данные будут испорчены.

Наше решение использует NumPy-массив и не меняет входной список.

---

# 57. Почему не используется функция с прошлой страницы

Можно было бы импортировать `discounted_cumulative_gain`.

Но в проверяющую систему обычно загружается только текущий файл.

Если написать:

```python
from gp_page_3_solution import discounted_cumulative_gain
```

этого файла может не быть в окружении проверяющей системы.

Поэтому решение самодостаточно.

---

# 58. Почему не создаётся отдельный helper

Отдельная вспомогательная функция допустима.

Но текущая реализация остаётся достаточно короткой и позволяет явно видеть:

- actual;
- ideal;
- standard;
- industry;
- нулевой IDCG.

Для новичка это проще проследить пошагово.

---

# 59. PEP8

Решение соблюдает:

- `snake_case`;
- понятные имена;
- группы импортов;
- пустые строки;
- многострочную сигнатуру;
- docstrings;
- длину строк;
- четыре пробела отступа.

---

# 60. Почему решение рассчитано на полный балл

## 80% корректности

- правильный actual DCG;
- правильный ideal DCG;
- сортируется весь список;
- учитывается `k`;
- два метода;
- одинаковый gain в числителе и знаменателе;
- обработан нулевой IDCG;
- invalid method вызывает ValueError;
- результат возвращается.

## 20% качества

- API сохранён;
- PEP8;
- docstrings;
- type hints;
- понятные переменные;
- нет лишних зависимостей;
- входные данные не изменяются.

---

# 61. Самая короткая мысленная модель

Нужно запомнить:

```text
actual = фактический порядок
ideal = те же релевантности, отсортированные по убыванию
DCG = качество actual
IDCG = качество ideal
nDCG = DCG / IDCG
```

Формула:

\[
nDCG@k =
\frac{DCG@k}{IDCG@k}
\]

Интерпретация:

> Какую долю от идеального качества набрала фактическая выдача?

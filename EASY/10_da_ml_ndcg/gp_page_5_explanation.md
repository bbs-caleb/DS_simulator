# gp_page_5 — Пошаговое объяснение кода Average nDCG с полного нуля

# 1. Какой файл отправлять

В проверяющую систему загружается:

```text
gp_page_5_solution.py
```

Файлы `.md` нужны для обучения.

---

# 2. Полный код решения

```python
"""Calculate the average Normalized Discounted Cumulative Gain."""

from typing import List

import numpy as np


def avg_ndcg(
    list_relevances: List[List[float]],
    k: int,
    method: str = "standard",
) -> float:
    """Calculate average nDCG at k for multiple queries.

    Parameters
    ----------
    list_relevances : List[List[float]]
        Video relevance lists for multiple queries.
    k : int
        Number of relevance values to include for each query.
    method : str, optional
        Metric implementation method:
        "standard" uses relevance as gain;
        "industry" uses 2 ** relevance - 1 as gain.

    Returns
    -------
    float
        Average Normalized Discounted Cumulative Gain score.

    Raises
    ------
    ValueError
        If method is neither "standard" nor "industry".
    """
    if method not in ("standard", "industry"):
        raise ValueError

    scores = []

    for relevance in list_relevances:
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
            scores.append(0.0)
        else:
            scores.append(float(actual_dcg / ideal_dcg))

    if not scores:
        return 0.0

    return float(np.mean(scores))
```

---

# 3. Docstring модуля

```python
"""Calculate the average Normalized Discounted Cumulative Gain."""
```

Это строка документации всего файла.

Она кратко сообщает назначение модуля.

Она помогает:

- разработчику;
- IDE;
- документации;
- Pylint.

---

# 4. Импорт `List`

```python
from typing import List
```

`List` используется в аннотации:

```python
List[List[float]]
```

Это означает список списков вещественных чисел.

---

# 5. Что означает `List[List[float]]`

Разберём изнутри.

```python
List[float]
```

Один список релевантностей:

```python
[0.99, 0.94, 0.88]
```

Внешний:

```python
List[List[float]]
```

Список нескольких таких списков:

```python
[
    [0.99, 0.94, 0.88],
    [0.92, 0.85, 0.70],
    [0.98, 0.89, 0.75],
]
```

Каждая строка соответствует отдельному запросу.

---

# 6. Импорт NumPy

```python
import numpy as np
```

NumPy используется для:

- массивов;
- сортировки;
- позиций;
- логарифма;
- степени;
- суммы;
- среднего.

---

# 7. Сигнатура функции

```python
def avg_ndcg(
    list_relevances: List[List[float]],
    k: int,
    method: str = "standard",
) -> float:
```

Функция принимает:

1. матрицу релевантностей;
2. глубину `k`;
3. метод.

Возвращает один `float`.

---

# 8. Имя функции

```python
avg_ndcg
```

Это точное имя из задания.

Менять нельзя.

Автотест будет обращаться именно к нему.

---

# 9. Аргумент `list_relevances`

```python
list_relevances: List[List[float]]
```

Пример:

```python
[
    [0.99, 0.94, 0.88],
    [0.99, 0.92, 0.93],
]
```

Внешний список имеет два запроса.

---

# 10. Аргумент `k`

```python
k: int
```

Для каждого запроса оцениваются первые `k` позиций.

Одно и то же `k` применяется ко всем строкам.

---

# 11. Аргумент `method`

```python
method: str = "standard"
```

Разрешены:

```python
"standard"
"industry"
```

Если аргумент не передан, используется:

```python
"standard"
```

---

# 12. Проверка метода

```python
if method not in ("standard", "industry"):
    raise ValueError
```

Проверка выполняется один раз до цикла.

Это правильно, потому что метод общий для всех запросов.

---

# 13. Почему ValueError без текста

Условие требует:

```python
raise ValueError
```

Нельзя добавлять:

```python
raise ValueError("Unknown method")
```

Тест может проверять, что сообщение пустое.

---

# 14. Создание списка результатов

```python
scores = []
```

Пустой список будет хранить nDCG каждого запроса.

После трёх запросов он может выглядеть так:

```python
[0.999, 0.990, 0.999]
```

---

# 15. Цикл по запросам

```python
for relevance in list_relevances:
```

Python последовательно берёт каждую строку.

На первой итерации:

```python
relevance = list_relevances[0]
```

На второй:

```python
relevance = list_relevances[1]
```

И так далее.

---

# 16. Почему переменная называется `relevance`

Внутри цикла мы работаем не со всей матрицей, а с одним списком релевантностей для одного запроса.

Поэтому имя в единственном контексте логично.

---

# 17. Преобразование одной строки

```python
relevance_array = np.asarray(relevance, dtype=float)
```

Обычный Python-список превращается в NumPy-массив.

Пример:

```python
[1, 0.5, 0]
```

становится:

```python
array([1.0, 0.5, 0.0])
```

---

# 18. Почему преобразование находится внутри цикла

Запросы могут иметь разную длину:

```python
[
    [0.9, 0.8, 0.7],
    [0.7, 0.4],
    [1.0, 0.8, 0.5, 0.3],
]
```

Если пытаться создать одну обычную двумерную float-матрицу, возникнет проблема неровных строк.

Построчное преобразование работает всегда.

---

# 19. Фактический top-k

```python
actual_relevance = relevance_array[:k]
```

Сохраняется реальный порядок модели.

Пример:

```python
relevance_array = [0.99, 0.92, 0.93, 0.74, 0.61, 0.68]
k = 5
```

Получаем:

```python
[0.99, 0.92, 0.93, 0.74, 0.61]
```

---

# 20. Идеальный top-k

```python
ideal_relevance = np.sort(relevance_array)[::-1][:k]
```

Операции:

1. сортировать весь запрос по возрастанию;
2. развернуть по убыванию;
3. взять первые `k`.

Пример:

```python
[0.99, 0.92, 0.93, 0.74, 0.61, 0.68]
```

Идеальный top-5:

```python
[0.99, 0.93, 0.92, 0.74, 0.68]
```

---

# 21. Почему нужно сортировать весь список

В примере `0.68` находится на шестой позиции.

Но оно лучше, чем `0.61` на пятой.

В идеальной выдаче `0.68` должно попасть в top-5.

Если сначала взять `[:5]`, а потом сортировать, `0.68` потеряется.

---

# 22. Построение позиций

```python
positions = np.arange(1, actual_relevance.size + 1)
```

Если actual содержит 5 элементов:

```python
[1, 2, 3, 4, 5]
```

Если actual содержит 2 элемента:

```python
[1, 2]
```

---

# 23. Почему используется `.size`

Допустим:

```python
k = 5
```

Но запрос содержит только 2 результата.

Фактический top-k имеет длину 2.

Позиции тоже должны иметь длину 2.

Поэтому используется:

```python
actual_relevance.size
```

а не просто `k`.

---

# 24. Вычисление discounts

```python
discounts = np.log2(positions + 1)
```

Для позиций:

```python
[1, 2, 3]
```

получаем:

```python
[
    log2(2),
    log2(3),
    log2(4),
]
```

То есть примерно:

```python
[1.0, 1.58496, 2.0]
```

---

# 25. Проверка industry

```python
if method == "industry":
```

Если метод industry, relevance преобразуется в gain.

---

# 26. Actual gain для industry

```python
actual_gain = np.power(2, actual_relevance) - 1
```

Для каждого значения:

\[
2^{rel}-1
\]

---

# 27. Ideal gain для industry

```python
ideal_gain = np.power(2, ideal_relevance) - 1
```

Очень важно применять ту же формулу к идеальной выдаче.

Иначе DCG и IDCG будут на разных шкалах.

---

# 28. Standard gain

```python
else:
    actual_gain = actual_relevance
    ideal_gain = ideal_relevance
```

Для standard gain равен relevance.

---

# 29. Actual DCG

```python
actual_dcg = np.sum(actual_gain / discounts)
```

Каждый gain делится на собственный позиционный discount.

Затем вклады складываются.

---

# 30. Ideal DCG

```python
ideal_dcg = np.sum(ideal_gain / discounts)
```

Используются те же позиции и discounts, но идеальный порядок.

---

# 31. Проверка IDCG

```python
if ideal_dcg == 0:
    scores.append(0.0)
```

Если IDCG равен нулю, делить нельзя.

Для такого запроса в список результатов добавляется:

```python
0.0
```

---

# 32. Что делает `.append`

```python
scores.append(0.0)
```

добавляет новый элемент в конец списка.

Пример:

До:

```python
scores = [0.98, 0.95]
```

После:

```python
scores = [0.98, 0.95, 0.0]
```

---

# 33. Обычный случай nDCG

```python
else:
    scores.append(float(actual_dcg / ideal_dcg))
```

Сначала:

```python
actual_dcg / ideal_dcg
```

получает nDCG одного запроса.

Затем `float(...)` приводит число к стандартному типу.

После этого значение добавляется в `scores`.

---

# 34. Что происходит после цикла

После обработки всех запросов:

```python
scores
```

содержит одно число на запрос.

Пример:

```python
[0.9992, 0.9901, 0.9991]
```

---

# 35. Проверка пустого списка запросов

```python
if not scores:
    return 0.0
```

`not scores` истинно, если список пустой.

Это происходит, когда:

```python
list_relevances = []
```

---

# 36. Зачем нужна проверка пустого списка

Если выполнить:

```python
np.mean([])
```

NumPy вернёт:

```python
nan
```

и выдаст warning.

Вместо этого функция возвращает понятное число:

```python
0.0
```

---

# 37. Расчёт среднего

```python
np.mean(scores)
```

Пример:

```python
scores = [0.9, 0.6, 0.3]
```

NumPy считает:

```python
(0.9 + 0.6 + 0.3) / 3
```

Результат:

```python
0.6
```

---

# 38. Возврат float

```python
return float(np.mean(scores))
```

`np.mean` может вернуть `numpy.float64`.

`float(...)` преобразует его в обычный Python `float`.

---

# 39. Полный проход примера

Вход:

```python
list_relevances = [
    [0.99, 0.94, 0.88, 0.89, 0.72, 0.65],
    [0.99, 0.92, 0.93, 0.74, 0.61, 0.68],
    [0.99, 0.96, 0.81, 0.73, 0.76, 0.69],
]
k = 5
method = "standard"
```

---

# 40. Первая итерация

Текущий запрос:

```python
[0.99, 0.94, 0.88, 0.89, 0.72, 0.65]
```

Actual top-5:

```python
[0.99, 0.94, 0.88, 0.89, 0.72]
```

Ideal top-5:

```python
[0.99, 0.94, 0.89, 0.88, 0.72]
```

Полученный nDCG добавляется в `scores`.

---

# 41. Вторая итерация

Запрос:

```python
[0.99, 0.92, 0.93, 0.74, 0.61, 0.68]
```

Actual:

```python
[0.99, 0.92, 0.93, 0.74, 0.61]
```

Ideal:

```python
[0.99, 0.93, 0.92, 0.74, 0.68]
```

Второй nDCG добавляется в `scores`.

---

# 42. Третья итерация

Запрос:

```python
[0.99, 0.96, 0.81, 0.73, 0.76, 0.69]
```

Actual:

```python
[0.99, 0.96, 0.81, 0.73, 0.76]
```

Ideal:

```python
[0.99, 0.96, 0.81, 0.76, 0.73]
```

Третий nDCG добавляется в `scores`.

---

# 43. После трёх итераций

В `scores` находятся три значения.

Затем:

```python
np.mean(scores)
```

возвращает:

```text
0.99613...
```

---

# 44. Проверка одного запроса

```python
avg_ndcg(
    [[0.9, 0.8, 0.7]],
    3,
)
```

Внешний список содержит один запрос.

Среднее одного числа равно самому числу.

Если порядок идеальный, результат:

```python
1.0
```

---

# 45. Проверка нескольких идеальных запросов

```python
avg_ndcg(
    [
        [1.0, 0.8, 0.5],
        [0.9, 0.7, 0.2],
    ],
    3,
)
```

Оба запроса идеальны.

Их nDCG:

```text
1.0
1.0
```

Среднее:

```python
1.0
```

---

# 46. Проверка пустого внутреннего запроса

```python
avg_ndcg(
    [
        [],
        [0.9, 0.8],
    ],
    2,
)
```

Для пустого запроса:

```python
IDCG = 0
nDCG = 0
```

Для второго запроса:

```python
nDCG = 1
```

Среднее:

```python
0.5
```

---

# 47. Проверка пустого внешнего списка

```python
avg_ndcg([], 5)
```

Нет запросов.

Возвращается:

```python
0.0
```

---

# 48. Проверка `k = 0`

Для каждого запроса actual и ideal пустые.

IDCG равен 0.

Каждый запрос получает `0.0`.

Среднее равно `0.0`.

---

# 49. Проверка `k` больше длины строк

```python
avg_ndcg(
    [
        [0.9, 0.8],
        [0.7],
    ],
    10,
)
```

Каждая строка использует все доступные элементы.

Позиции строятся по фактической длине.

---

# 50. Проверка неправильного метода

```python
avg_ndcg(
    [[0.9, 0.8]],
    2,
    "wrong",
)
```

Функция сразу вызывает:

```python
raise ValueError
```

До цикла она не доходит.

---

# 51. Почему нельзя вызвать `normalized_dcg` из прошлого файла

Можно было бы написать:

```python
from gp_page_4_solution import normalized_dcg
```

Но автопроверка может загрузить только текущий файл.

Тогда импорт завершится ошибкой.

Поэтому решение самодостаточно.

---

# 52. Почему не используется nested helper

Можно было создать внутреннюю функцию для одного запроса.

Но текущая реализация показывает весь алгоритм прямо внутри цикла.

Для человека, который изучает код с нуля, так проще проследить:

- actual;
- ideal;
- gain;
- DCG;
- IDCG;
- nDCG;
- average.

---

# 53. Почему нельзя написать `np.mean(list_relevances)`

`list_relevances` содержит relevance labels, а не nDCG.

Среднее всех labels не имеет смысла как Average nDCG.

Сначала нужна полная метрика каждого запроса.

---

# 54. Почему нельзя объединить строки

Неправильно:

```python
flat = [
    value
    for relevance in list_relevances
    for value in relevance
]
```

После объединения исчезают границы запросов.

Невозможно построить отдельный ideal для каждого query.

---

# 55. Почему нельзя сначала усреднить позиции

Нельзя сначала вычислить среднюю релевантность на первой позиции, второй позиции и так далее, а затем считать nDCG.

Это даст метрику «средней искусственной выдачи», а не среднее качества реальных запросов.

---

# 56. Почему не округляется результат

Условие показывает:

```text
0.99613...
```

Многоточие означает продолжение числа.

Нужно вернуть полную точность.

Неправильно:

```python
round(result, 5)
```

---

# 57. Почему исходные списки не изменяются

Решение не использует:

```python
relevance.sort(reverse=True)
```

который меняет список на месте.

Используется:

```python
np.sort(relevance_array)
```

Он создаёт отсортированный результат отдельно.

Исходные данные пользователя остаются неизменными.

---

# 58. PEP8

В файле соблюдены:

- module docstring;
- function docstring;
- `snake_case`;
- правильные импорты;
- перенос сигнатуры;
- четыре пробела;
- понятные имена;
- отсутствие неиспользуемых импортов;
- стандартный `float`.

---

# 59. Почему решение рассчитано на полный балл

## Корректность

- каждый запрос считается отдельно;
- actual не сортируется;
- ideal строится по всему запросу;
- используется `k`;
- поддерживаются два метода;
- обрабатывается IDCG = 0;
- вычисляется обычное среднее;
- invalid method вызывает пустой ValueError;
- возвращается число.

## Качество

- точный API;
- PEP8;
- docstrings;
- type hints;
- понятная структура;
- поддержка строк разной длины;
- нет лишних зависимостей.

---

# 60. Самая короткая мысленная модель

```text
для каждого запроса:
    посчитать nDCG
собрать все nDCG
вернуть их среднее
```

Математически:

\[
Average\ nDCG@k
=
\frac{
nDCG_1+nDCG_2+\dots+nDCG_n
}{n}
\]

Бизнесовая интерпретация:

> Средняя доля от идеального качества ранжирования по множеству запросов.

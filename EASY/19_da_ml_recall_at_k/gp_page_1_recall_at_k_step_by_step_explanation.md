# Подробное объяснение решения Recall @ K

## 1. Что требуется реализовать

В файле должны существовать ровно четыре публичные функции из шаблона задания:

```python
def recall_at_k(labels: List[int], scores: List[float], k=5) -> float:
    ...


def precision_at_k(labels: List[int], scores: List[float], k=5) -> float:
    ...


def specificity_at_k(labels: List[int], scores: List[float], k=5) -> float:
    ...


def f1_at_k(labels: List[int], scores: List[float], k=5) -> float:
    ...
```

Проверяющая система будет импортировать файл и вызывать эти функции.

Если изменить имена функций или обязательные аргументы, тесты не смогут найти API и поставят 0 баллов.

---

# 2. Что такое labels

Пример:

```python
labels = [1, 0, 1, 0]
```

Каждое число описывает истинную релевантность одного объекта.

```text
1 — релевантный объект
0 — нерелевантный объект
```

У каждого элемента списка есть индекс:

```text
labels[0] = 1
labels[1] = 0
labels[2] = 1
labels[3] = 0
```

Индекс начинается с нуля.

---

# 3. Что такое scores

Пример:

```python
scores = [0.20, 0.95, 0.80, 0.10]
```

Score — это оценка модели.

Чем score больше, тем выше модель хочет поставить объект.

Самое важное правило:

```text
labels[i] и scores[i] относятся к одному объекту
```

Например:

| Индекс | Label | Score |
|---:|---:|---:|
| 0 | 1 | 0.20 |
| 1 | 0 | 0.95 |
| 2 | 1 | 0.80 |
| 3 | 0 | 0.10 |

Объект с индексом `1` имеет:

```text
label = 0
score = 0.95
```

Модель очень уверена, что объект хороший, но историческая метка говорит, что он нерелевантен. Если он попадёт в top-K, это будет False Positive.

---

# 4. Что означает k

```python
k = 2
```

Это означает, что положительным предсказанием считаются два объекта с самыми большими scores.

Для примера:

```python
scores = [0.20, 0.95, 0.80, 0.10]
```

Два самых больших значения:

```text
0.95 — индекс 1
0.80 — индекс 2
```

Следовательно:

```text
top_indices = {1, 2}
```

Объекты 1 и 2 считаются predicted positive.

Объекты 0 и 3 считаются predicted negative.

---

# 5. Почему используется вспомогательная функция

Во всех четырёх метриках сначала нужно выполнить одинаковые действия:

1. Проверить входные данные.
2. Отсортировать объекты.
3. Выбрать top-K.
4. Посчитать TP, FP, TN и FN.

Если написать этот код четыре раза, появятся проблемы:

- файл станет длиннее;
- можно случайно реализовать сортировку по-разному;
- исправление придётся делать в четырёх местах;
- возрастает риск ошибки.

Поэтому общая логика вынесена в функцию:

```python
_confusion_matrix_at_k(...)
```

Нижнее подчёркивание в начале имени означает:

> Это внутренняя вспомогательная функция модуля.

Проверяющая система может её не вызывать. Она нужна нашим четырём основным функциям.

---

# 6. Импорты

```python
from typing import List, Tuple
```

Модуль `typing` используется для аннотаций типов.

`List[int]` означает:

```text
список целых чисел
```

`List[float]` означает:

```text
список вещественных чисел
```

`Tuple[int, int, int, int]` означает:

```text
кортеж из четырёх целых чисел
```

Аннотации не выполняют вычисления. Они помогают человеку и инструментам понять, какие данные ожидает функция.

---

# 7. Заголовок вспомогательной функции

```python
def _confusion_matrix_at_k(
    labels: List[int], scores: List[float], k: int
) -> Tuple[int, int, int, int]:
```

Функция принимает:

- `labels`;
- `scores`;
- `k`.

Возвращает четыре числа:

```text
TP, FP, TN, FN
```

Порядок важен.

---

# 8. Проверка одинаковой длины

```python
if len(labels) != len(scores):
    raise ValueError("labels and scores must have the same length")
```

`len(...)` возвращает количество элементов.

Например:

```python
len([1, 0, 1])
```

Результат:

```text
3
```

Почему длины должны совпадать?

Потому что каждый label должен иметь соответствующий score.

Неправильный ввод:

```python
labels = [1, 0, 1]
scores = [0.9, 0.8]
```

У третьего label нет score. Невозможно честно понять его позицию.

`raise ValueError(...)` немедленно останавливает функцию и сообщает о некорректных данных.

---

# 9. Нормализация k

```python
top_k = min(max(k, 0), len(labels))
```

Эта строка защищает код от крайних значений.

Разберём изнутри.

## Случай 1. Нормальный k

```text
k = 5
len(labels) = 10
```

```python
max(5, 0) == 5
min(5, 10) == 5
```

Получаем:

```text
top_k = 5
```

## Случай 2. Отрицательный k

```text
k = -3
```

```python
max(-3, 0) == 0
```

Получаем:

```text
top_k = 0
```

Ни один объект не считается положительным.

## Случай 3. k больше числа объектов

```text
k = 100
len(labels) = 8
```

```python
min(100, 8) == 8
```

Получаем:

```text
top_k = 8
```

Нельзя выбрать больше объектов, чем существует.

---

# 10. Создание индексов

```python
range(len(scores))
```

Если scores содержит четыре элемента:

```python
scores = [0.20, 0.95, 0.80, 0.10]
```

то:

```python
range(len(scores))
```

представляет индексы:

```text
0, 1, 2, 3
```

Нам нужно сортировать индексы, а не сами labels.

Почему?

Потому что индекс сохраняет связь между score и label.

---

# 11. Сортировка по score

```python
ranked_indices = sorted(
    range(len(scores)),
    key=scores.__getitem__,
    reverse=True,
)
```

Разберём каждый аргумент.

## Что сортируется

```python
range(len(scores))
```

То есть индексы.

## По какому ключу

```python
key=scores.__getitem__
```

Это означает:

> Для каждого индекса возьми `scores[index]` и используй это значение для сортировки.

Можно мысленно представить более длинную запись:

```python
key=lambda index: scores[index]
```

Обе записи означают одно и то же.

## Зачем reverse=True

По умолчанию `sorted` сортирует от меньшего к большему.

Нам нужны самые большие scores в начале, поэтому используется:

```python
reverse=True
```

## Результат на примере

```python
scores = [0.20, 0.95, 0.80, 0.10]
```

Индексы по убыванию score:

```text
1, 2, 0, 3
```

Проверка:

```text
scores[1] = 0.95
scores[2] = 0.80
scores[0] = 0.20
scores[3] = 0.10
```

Следовательно:

```python
ranked_indices == [1, 2, 0, 3]
```

---

# 12. Выбор top-K индексов

```python
top_indices = set(ranked_indices[:top_k])
```

## Что означает срез

Если:

```python
ranked_indices = [1, 2, 0, 3]
top_k = 2
```

то:

```python
ranked_indices[:2]
```

даст:

```text
[1, 2]
```

## Зачем set

`set` — множество.

```python
set([1, 2])
```

даёт:

```text
{1, 2}
```

Множество позволяет быстро проверять:

```python
index in top_indices
```

То есть:

> Входит ли текущий объект в top-K?

---

# 13. Начальные значения счётчиков

```python
true_positive = 0
false_positive = 0
true_negative = 0
false_negative = 0
```

До обхода объектов мы ещё ничего не посчитали, поэтому все счётчики равны нулю.

---

# 14. Цикл по labels

```python
for index, label in enumerate(labels):
```

`enumerate` одновременно даёт:

- индекс;
- значение.

Для:

```python
labels = [1, 0, 1, 0]
```

цикл последовательно получает:

```text
index = 0, label = 1
index = 1, label = 0
index = 2, label = 1
index = 3, label = 0
```

---

# 15. Определение predicted positive

```python
predicted_positive = index in top_indices
```

Если:

```text
top_indices = {1, 2}
```

то:

```text
index 0 -> False
index 1 -> True
index 2 -> True
index 3 -> False
```

`True` означает, что объект попал в top-K.

`False` означает, что объект находится вне top-K.

---

# 16. Подсчёт True Positive

```python
if label == 1 and predicted_positive:
    true_positive += 1
```

Условия:

```text
истинный label = 1
объект попал в top-K
```

Это правильное положительное решение.

`+= 1` означает увеличить счётчик на единицу.

---

# 17. Подсчёт False Positive

```python
elif label == 0 and predicted_positive:
    false_positive += 1
```

Условия:

```text
истинный label = 0
объект попал в top-K
```

Модель заняла место в верхней выдаче нерелевантным объектом.

---

# 18. Подсчёт True Negative

```python
elif label == 0 and not predicted_positive:
    true_negative += 1
```

Условия:

```text
истинный label = 0
объект не попал в top-K
```

Нерелевантный объект правильно оставлен внизу.

`not predicted_positive` меняет:

```text
True на False
False на True
```

---

# 19. Подсчёт False Negative

```python
elif label == 1 and not predicted_positive:
    false_negative += 1
```

Условия:

```text
истинный label = 1
объект не попал в top-K
```

Модель пропустила релевантный объект.

---

# 20. Возврат четырёх чисел

```python
return true_positive, false_positive, true_negative, false_negative
```

Python автоматически создаёт кортеж.

Например:

```text
(1, 1, 1, 1)
```

---

# 21. Реализация Recall@K

```python
def recall_at_k(labels: List[int], scores: List[float], k=5) -> float:
```

Функция должна вернуть вещественное число.

## Получаем TP и FN

```python
true_positive, _, _, false_negative = _confusion_matrix_at_k(
    labels, scores, k
)
```

Вспомогательная функция возвращает четыре значения:

```text
TP, FP, TN, FN
```

Для Recall нужны только TP и FN.

Символ `_` означает:

> Это значение получено, но дальше не используется.

## Знаменатель

```python
denominator = true_positive + false_negative
```

Это все реальные положительные объекты.

## Защита от деления на ноль

```python
if denominator == 0:
    return 0.0
```

Если в labels нет ни одной единицы, знаменатель равен нулю.

Делить на ноль нельзя.

В решении выбрана политика вернуть `0.0`.

## Формула

```python
return true_positive / denominator
```

Это:

```text
TP / (TP + FN)
```

---

# 22. Реализация Precision@K

```python
true_positive, false_positive, _, _ = _confusion_matrix_at_k(
    labels, scores, k
)
```

Нужны TP и FP.

```python
denominator = true_positive + false_positive
```

Это число объектов, фактически попавших в top-K.

```python
return true_positive / denominator
```

Формула:

```text
TP / (TP + FP)
```

Если `k = 0`, ни один объект не выбран, знаменатель равен нулю и функция возвращает `0.0`.

---

# 23. Реализация Specificity@K

```python
_, false_positive, true_negative, _ = _confusion_matrix_at_k(
    labels, scores, k
)
```

Нужны TN и FP.

```python
denominator = true_negative + false_positive
```

Это все реальные отрицательные объекты.

```python
return true_negative / denominator
```

Формула:

```text
TN / (TN + FP)
```

Если в labels нет ни одного нуля, denominator равен нулю и функция возвращает `0.0`.

---

# 24. Реализация F1@K

В коде используется формула:

```text
F1 = 2 × TP / (2 × TP + FP + FN)
```

Код:

```python
true_positive, false_positive, _, false_negative = (
    _confusion_matrix_at_k(labels, scores, k)
)
```

Знаменатель:

```python
denominator = 2 * true_positive + false_positive + false_negative
```

Результат:

```python
return 2 * true_positive / denominator
```

Почему не вызываются отдельно `precision_at_k` и `recall_at_k`?

Потому что тогда пришлось бы повторно сортировать scores два раза.

Одна confusion matrix позволяет вычислить F1 напрямую.

---

# 25. Полный прогон на примере

Дано:

```python
labels = [1, 0, 1, 0]
scores = [0.20, 0.95, 0.80, 0.10]
k = 2
```

## Сортировка

```text
индекс 1 -> score 0.95 -> label 0
индекс 2 -> score 0.80 -> label 1
индекс 0 -> score 0.20 -> label 1
индекс 3 -> score 0.10 -> label 0
```

## Top-2

```text
индексы {1, 2}
labels [0, 1]
```

## Счётчики

Индекс 0:

```text
label = 1
не в top-2
FN += 1
```

Индекс 1:

```text
label = 0
в top-2
FP += 1
```

Индекс 2:

```text
label = 1
в top-2
TP += 1
```

Индекс 3:

```text
label = 0
не в top-2
TN += 1
```

Итог:

```text
TP = 1
FP = 1
TN = 1
FN = 1
```

Метрики:

```text
Recall@2 = 1 / (1 + 1) = 0.5
Precision@2 = 1 / (1 + 1) = 0.5
Specificity@2 = 1 / (1 + 1) = 0.5
F1@2 = 2 / (2 + 1 + 1) = 0.5
```

---

# 26. Ручные проверки

## Проверка 1. Идеальное ранжирование

```python
labels = [1, 1, 0, 0]
scores = [0.9, 0.8, 0.2, 0.1]
k = 2
```

Top-2 содержит обе единицы.

```text
TP = 2
FP = 0
TN = 2
FN = 0
```

Ожидается:

```text
Recall@2 = 1.0
Precision@2 = 1.0
Specificity@2 = 1.0
F1@2 = 1.0
```

## Проверка 2. Полностью неправильный top-K

```python
labels = [0, 0, 1, 1]
scores = [0.9, 0.8, 0.2, 0.1]
k = 2
```

Top-2 содержит только нули.

```text
TP = 0
FP = 2
TN = 0
FN = 2
```

Ожидается:

```text
Recall@2 = 0.0
Precision@2 = 0.0
Specificity@2 = 0.0
F1@2 = 0.0
```

## Проверка 3. k равно нулю

```python
labels = [1, 0, 1]
scores = [0.9, 0.8, 0.7]
k = 0
```

Ни один объект не выбран.

```text
TP = 0
FP = 0
TN = 1
FN = 2
```

Ожидается:

```text
Recall@0 = 0.0
Precision@0 = 0.0
Specificity@0 = 1.0
F1@0 = 0.0
```

## Проверка 4. k больше длины списка

```python
labels = [1, 0, 1]
scores = [0.9, 0.8, 0.7]
k = 100
```

Фактически выбираются все три объекта.

```text
TP = 2
FP = 1
TN = 0
FN = 0
```

Ожидается:

```text
Recall = 1.0
Precision = 2 / 3
Specificity = 0.0
F1 = 4 / 5 = 0.8
```

## Проверка 5. Нет положительных labels

```python
labels = [0, 0, 0]
scores = [0.9, 0.8, 0.7]
k = 2
```

Для Recall нет положительных объектов, поэтому denominator равен нулю.

Решение возвращает:

```text
Recall@2 = 0.0
```

## Проверка 6. Нет отрицательных labels

```python
labels = [1, 1, 1]
scores = [0.9, 0.8, 0.7]
k = 2
```

Для Specificity нет отрицательных объектов, поэтому denominator равен нулю.

Решение возвращает:

```text
Specificity@2 = 0.0
```

---

# 27. Как проверить файл локально

Можно временно создать отдельный тестовый файл или открыть Python/Jupyter и выполнить:

```python
from gp_page_1_recall_at_k_solution import (
    f1_at_k,
    precision_at_k,
    recall_at_k,
    specificity_at_k,
)

labels = [1, 0, 1, 0, 1, 0, 0, 1]
scores = [0.95, 0.85, 0.80, 0.75, 0.70, 0.60, 0.40, 0.20]
k = 5

print(recall_at_k(labels, scores, k))
print(precision_at_k(labels, scores, k))
print(specificity_at_k(labels, scores, k))
print(f1_at_k(labels, scores, k))
```

Ожидаемый вывод:

```text
0.75
0.6
0.5
0.6666666666666666
```

Последнее число длинное, потому что дробь `2/3` невозможно точно представить конечным двоичным числом.

Проверяющие тесты обычно сравнивают такие значения с допустимой погрешностью.

---

# 28. Почему решение соответствует PEP8

В решении:

- импорты находятся в начале файла;
- между функциями оставлены две пустые строки;
- имена функций и переменных записаны в `snake_case`;
- строки не перегружены;
- у функций есть docstring;
- нет неиспользуемых импортов;
- нет внешних зависимостей;
- нет кода, который запускается при импорте файла.

Это важно для 20% баллов за качество кода.

---

# 29. Сложность алгоритма

Основная операция — сортировка индексов.

Для `n` объектов:

```text
время: O(n log n)
память: O(n)
```

Для учебной задачи это правильный выбор: код короткий, понятный и надёжный.

---

# 30. Самая важная мысль урока

Все четыре метрики используют одну и ту же confusion matrix.

Разница только в том, какую ошибку мы считаем важной:

```text
Recall@K      — сколько релевантных объектов мы не потеряли
Precision@K   — насколько чистый наш top-K
Specificity@K — насколько хорошо мы оставили мусор за пределами top-K
F1@K          — насколько сбалансированы Recall и Precision
```

Код является прямым переводом этой логики в Python.

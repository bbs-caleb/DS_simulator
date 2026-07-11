# GP — страница 1: пошаговое объяснение решения APPROXIMATE KNN

# 1. Что делает весь файл

Файл решает три основные подзадачи:

```text
1. distance
   Вычислить расстояния от одной точки до всех документов.

2. create_sw_graph
   Построить граф связей между документами.

3. nsw
   Пройти по графу и найти приближённых ближайших соседей.
```

Дополнительная функция:

```text
calc_d_and_upd
```

Она вычисляет расстояние до точки только один раз и сохраняет результат.

---

# 2. Импорты

```python
from collections import OrderedDict, defaultdict
from typing import Callable, Tuple, Dict, List

import numpy as np
from tqdm.auto import tqdm
```

## OrderedDict

Это словарь, запоминающий порядок добавления элементов.

Мы будем хранить:

```text
индекс точки → расстояние до запроса
```

Пример:

```python
visited = OrderedDict()
visited[5] = 0.8
visited[2] = 0.4
visited[9] = 1.2
```

Тогда:

```python
list(visited.keys())
```

даст:

```text
[5, 2, 9]
```

а:

```python
list(visited.values())
```

даст:

```text
[0.8, 0.4, 1.2]
```

Позиции ключей и значений соответствуют друг другу.

## defaultdict

Обычный словарь требует заранее создать список:

```python
edges[0] = []
edges[0].append(5)
```

`defaultdict(list)` создаёт пустой список автоматически:

```python
edges = defaultdict(list)
edges[0].append(5)
```

## Callable

Тип для функции.

```python
dist_f: Callable = distance
```

означает, что в аргумент можно передать функцию расстояния. По умолчанию используется `distance`.

Это важно для API и тестов: код должен вызывать `dist_f`, а не всегда жёстко вызывать `distance`.

## Tuple

```python
Tuple[float, bool]
```

означает пару значений:

```text
число с плавающей точкой, логическое значение
```

## Dict[int, List[int]]

Означает:

```text
словарь, где ключ — int, значение — список int
```

Именно так представлен граф.

## NumPy

Используется для:

- массивов;
- broadcasting;
- нормы;
- сортировки индексов;
- случайного выбора;
- объединения массивов.

## tqdm

Показывает progress bar при построении графа.

---

# 3. Функция distance

```python
def distance(pointA: np.ndarray, documents: np.ndarray) -> np.ndarray:
    dist = np.linalg.norm(pointA - documents, axis=1, keepdims=True)
    return dist
```

## Входные формы

Одна точка:

```python
pointA = np.array([1.0, 2.0])
```

Форма:

```text
(2,)
```

Несколько документов:

```python
documents = np.array([
    [1.0, 2.0],
    [4.0, 6.0],
    [2.0, 2.0]
])
```

Форма:

```text
(3, 2)
```

То есть три документа, каждый содержит два числа.

---

# 4. Broadcasting в pointA - documents

NumPy мысленно повторяет `pointA` для каждой строки:

```text
[1, 2]
[1, 2]
[1, 2]
```

Затем выполняет вычитание:

```text
[1, 2] - [1, 2] = [ 0,  0]
[1, 2] - [4, 6] = [-3, -4]
[1, 2] - [2, 2] = [-1,  0]
```

Результат имеет форму `(3, 2)`.

---

# 5. np.linalg.norm

```python
np.linalg.norm(..., axis=1, keepdims=True)
```

`axis=1` означает:

> Считать норму отдельно по каждой строке.

Получаем:

```text
sqrt(0² + 0²) = 0
sqrt((-3)² + (-4)²) = 5
sqrt((-1)² + 0²) = 1
```

Результат:

```text
[[0.],
 [5.],
 [1.]]
```

---

# 6. Зачем keepdims=True

Без `keepdims=True` форма была бы:

```text
(N,)
```

С `keepdims=True`:

```text
(N, 1)
```

Условие задачи требует именно `N × 1`, поэтому этот параметр важен для скрытых тестов.

---

# 7. Функция create_sw_graph

```python
def create_sw_graph(
        data: np.ndarray,
        num_candidates_for_choice_long: int = 10,
        num_edges_long: int = 5,
        num_candidates_for_choice_short: int = 10,
        num_edges_short: int = 5,
        use_sampling: bool = False,
        sampling_share: float = 0.05,
        dist_f: Callable = distance
    ) -> Dict[int, List[int]]:
```

`data` имеет форму:

```text
(N, D)
```

Пример:

```text
N = 1000 документов
D = 128 чисел в embedding
```

```text
data.shape = (1000, 128)
```

---

# 8. Параметры коротких рёбер

```text
num_candidates_for_choice_short = 10
num_edges_short = 5
```

Алгоритм:

1. Берёт десять ближайших кандидатов.
2. Случайно выбирает из них пять.
3. Сохраняет пять коротких рёбер.

Кандидаты и рёбра — не одно и то же.

Пул кандидатов может быть больше числа реально создаваемых связей.

---

# 9. Параметры длинных рёбер

```text
num_candidates_for_choice_long = 10
num_edges_long = 5
```

Алгоритм:

1. Берёт десять самых далёких кандидатов.
2. Случайно выбирает пять.
3. Сохраняет пять длинных рёбер.

---

# 10. Создание графа

```python
edges = defaultdict(list)
num_points = data.shape[0]
```

Если:

```text
data.shape = (1000, 128)
```

то:

```text
num_points = 1000
```

Граф постепенно станет похож на:

```python
{
    0: [3, 8, 12, 51, ...],
    1: [0, 4, 17, 80, ...],
    2: [1, 9, 33, 70, ...]
}
```

---

# 11. Цикл по точкам

```python
for cur_point_idx in tqdm(range(num_points)):
```

`cur_point_idx` принимает значения:

```text
0, 1, 2, ..., N - 1
```

Для каждой точки строится отдельный список исходящих рёбер.

---

# 12. Полный режим

```python
if not use_sampling:
    all_dists = dist_f(data[cur_point_idx, :], data)
```

`data[cur_point_idx, :]` берёт одну строку и все столбцы.

Форма:

```text
(D,)
```

`data` имеет форму:

```text
(N, D)
```

Поэтому `all_dists` имеет форму:

```text
(N, 1)
```

---

# 13. Сортировка индексов

```python
argsorted = np.argsort(all_dists.reshape(1, -1))[0][1:]
```

Разбираем по частям.

## reshape(1, -1)

Было:

```text
(N, 1)
```

Стало:

```text
(1, N)
```

`-1` говорит NumPy вычислить размер автоматически.

## np.argsort

`argsort` возвращает индексы, а не отсортированные значения.

Пример:

```python
values = np.array([8.0, 2.0, 5.0])
np.argsort(values)
```

Результат:

```text
[1, 2, 0]
```

Потому что:

```text
values[1] = 2
values[2] = 5
values[0] = 8
```

## [0]

Берётся первая строка массива формы `(1, N)`.

## [1:]

Расстояние точки до самой себя равно нулю, поэтому её индекс будет первым. Срез `[1:]` удаляет саму точку.

---

# 14. Sampling-ветка

```python
sample_size = int(num_points * sampling_share)
```

Пример:

```text
num_points = 10 000
sampling_share = 0.05
sample_size = 500
```

Затем выбираются уникальные индексы:

```python
choiced = np.random.choice(
    list(range(num_points)),
    size=sample_size,
    replace=False
)
```

`replace=False` означает, что один индекс не выбирается дважды.

Расстояния считаются только до sample:

```python
part_dists = dist_f(
    data[cur_point_idx, :],
    data[choiced, :]
)
```

После сортировки позиции внутри sample переводятся обратно в глобальные индексы:

```python
argsorted = choiced[
    np.argsort(part_dists.reshape(1, -1))[0][1:]
]
```

---

# 15. Короткие кандидаты

```python
short_cands = argsorted[:num_candidates_for_choice_short]
```

Так как массив отсортирован от меньшего расстояния к большему, начало содержит ближайшие точки.

Пример:

```text
argsorted = [7, 2, 9, 4, 1, 8, ...]
num_candidates_for_choice_short = 4
```

Получаем:

```text
short_cands = [7, 2, 9, 4]
```

---

# 16. Выбор коротких рёбер

```python
short_choice = np.random.choice(
    short_cands,
    size=num_edges_short,
    replace=False
)
```

Если:

```text
short_cands = [7, 2, 9, 4]
num_edges_short = 2
```

возможный результат:

```text
[9, 2]
```

---

# 17. Далёкие кандидаты

```python
long_cands = argsorted[-num_candidates_for_choice_long:]
```

Отрицательный срез берёт конец массива.

Пример:

```text
argsorted = [7, 2, 9, 4, 1, 8, 5, 3]
num_candidates_for_choice_long = 3
```

Получаем:

```text
[8, 5, 3]
```

Затем из пула случайно выбираются длинные рёбра.

---

# 18. Объединение рёбер

```python
for point_idx in np.concatenate([short_choice, long_choice]):
    edges[cur_point_idx].append(point_idx)
```

Пример:

```text
short_choice = [2, 9]
long_choice = [20, 37]
```

После `concatenate`:

```text
[2, 9, 20, 37]
```

Все индексы добавляются в список текущей вершины.

---

# 19. Почему граф направленный

Код добавляет:

```python
edges[cur_point_idx].append(point_idx)
```

Но не добавляет автоматически:

```python
edges[point_idx].append(cur_point_idx)
```

Поэтому связь `i → j` не гарантирует `j → i`.

Это соответствует эталонной логике задания.

---

# 20. Возврат обычного словаря

```python
return dict(edges)
```

`edges` был `defaultdict`, но контракт требует словарь. Поэтому выполняется преобразование в `dict`.

---

# 21. Функция calc_d_and_upd

```python
def calc_d_and_upd(
        all_visited_points: OrderedDict,
        query_point: np.ndarray,
        all_documents: np.ndarray,
        point_idx: int,
        dist_f: Callable
    ) -> Tuple[float, bool]:
```

Название можно понять как:

```text
calculate distance and update
```

Функция возвращает:

```text
расстояние, была ли точка уже посещена
```

---

# 22. Повторно посещённая точка

```python
if point_idx in all_visited_points:
    return all_visited_points[point_idx], True
```

Если индекс уже есть в словаре:

- расстояние уже вычислено;
- берётся сохранённое значение;
- `True` означает, что точка была посещена раньше.

---

# 23. Новая точка

```python
cur_dist = dist_f(
    query_point,
    all_documents[point_idx, :].reshape(1, -1)
)[0][0]
```

`all_documents[point_idx, :]` имеет форму `(D,)`.

Функция `distance` ожидает матрицу документов `(N, D)`. Для одного документа нужна форма `(1, D)`:

```python
reshape(1, -1)
```

`distance` возвращает `(1, 1)`, поэтому `[0][0]` извлекает число.

После этого:

```python
all_visited_points[point_idx] = cur_dist
return cur_dist, False
```

`False` означает, что точка новая.

---

# 24. Функция nsw

```python
def nsw(
        query_point: np.ndarray,
        all_documents: np.ndarray,
        graph_edges: Dict[int, List[int]],
        search_k: int = 10,
        num_start_points: int = 5,
        dist_f: Callable = distance
    ) -> np.ndarray:
```

Аргументы:

- `query_point` — что ищем;
- `all_documents` — где ищем;
- `graph_edges` — по каким рёбрам ходим;
- `search_k` — сколько индексов вернуть;
- `num_start_points` — сколько независимых маршрутов начать;
- `dist_f` — функция расстояния.

---

# 25. Хранилище посещённых точек

```python
all_visited_points = OrderedDict()
num_started_points = 0
```

В словарь попадают все точки, до которых было вычислено расстояние, а не только конечные точки маршрутов.

В конце top-K выбирается среди всех посещённых вершин.

---

# 26. Внешний while

```python
while (
    num_started_points < num_start_points
    or len(all_visited_points) < search_k
):
```

Цикл продолжается, если:

1. ещё выполнено недостаточно стартов;
2. или посещено меньше точек, чем нужно вернуть.

Почему `or`, а не `and`?

Если использовать `and`, алгоритм мог бы остановиться после нужного числа стартов, даже если собрал меньше `search_k` уникальных точек.

С `or` должны выполниться оба итоговых требования:

- маршрутов не меньше `num_start_points`;
- посещённых точек не меньше `search_k`.

---

# 27. Случайный старт

```python
cur_point_idx = np.random.randint(
    0,
    all_documents.shape[0] - 1
)
```

Выбирается случайная стартовая вершина.

Эта строка повторяет эталонную реализацию курса.

Затем вызывается кэш-функция:

```python
cur_dist, verdict = calc_d_and_upd(...)
```

Если старт уже использовался:

```python
if verdict:
    continue
```

Начинается следующая итерация внешнего цикла. Такой повторный старт не считается новым маршрутом.

---

# 28. Внутренний greedy-поиск

```python
while True:
    min_dist = cur_dist
    choiced_cand = cur_point_idx
```

Пока лучшая известная точка — текущая.

`choiced_cand` — выбранный кандидат.

---

# 29. Получение соседей

```python
cands_idxs = graph_edges[cur_point_idx]
true_verdict_cands = {cur_point_idx}
```

`cands_idxs` — список исходящих соседей текущей вершины.

`true_verdict_cands` — множество точек, которые уже посещались. Текущая точка точно посещена, поэтому сразу добавляется.

---

# 30. Проверка соседей

```python
for cand_idx in cands_idxs:
    tmp_d, verdict = calc_d_and_upd(...)
```

Для каждого соседа получаем:

- `tmp_d` — расстояние до запроса;
- `verdict` — встречался ли сосед раньше.

Если сосед ближе:

```python
if tmp_d < min_dist:
    min_dist = tmp_d
    choiced_cand = cand_idx
```

Если сосед уже был посещён:

```python
if verdict:
    true_verdict_cands.add(cand_idx)
```

---

# 31. Конструкция for ... else

В Python у цикла `for` может быть `else`:

```python
for item in items:
    ...
else:
    ...
```

`else` выполняется, если цикл закончился без `break`.

Внутри текущего `for` нет `break`, поэтому после проверки всех соседей выполняется блок `else`.

---

# 32. Остановка маршрута

```python
if choiced_cand in true_verdict_cands:
    break
```

Два основных случая.

## Нет улучшения

Если ни один сосед не ближе:

```text
choiced_cand == cur_point_idx
```

Текущая точка находится во множестве посещённых, поэтому маршрут останавливается.

## Лучший сосед уже посещён

Переход к нему может создать цикл. Поэтому маршрут также останавливается.

---

# 33. Переход к новому соседу

Если найден более близкий и новый сосед:

```python
cur_dist = min_dist
cur_point_idx = choiced_cand
continue
```

Теперь выбранный сосед становится текущей точкой, и внутренний цикл повторяется.

После завершения маршрута:

```python
num_started_points += 1
```

---

# 34. Выбор итогового top-K

После всех маршрутов словарь может выглядеть так:

```python
{
    8: 1.7,
    3: 0.4,
    20: 0.9,
    11: 0.2
}
```

Получаем позиции наименьших расстояний:

```python
best_idxs = np.argsort(
    list(all_visited_points.values())
)[:search_k]
```

Значения:

```text
[1.7, 0.4, 0.9, 0.2]
```

`argsort`:

```text
[3, 1, 2, 0]
```

Это позиции в списке, а не индексы документов.

Затем:

```python
final_idx = np.array(
    list(all_visited_points.keys())
)[best_idxs]
```

Ключи:

```text
[8, 3, 20, 11]
```

После индексирования:

```text
[11, 3, 20, 8]
```

Это индексы документов в порядке увеличения расстояния.

---

# 35. Маленький пример маршрута

Документы одномерные:

```text
index 0 → [0]
index 1 → [2]
index 2 → [4]
index 3 → [7]
index 4 → [10]
```

Запрос:

```text
query = [6]
```

Расстояния:

```text
до 0: 6
до 1: 4
до 2: 2
до 3: 1
до 4: 4
```

Настоящий ближайший — `index 3`.

Пусть маршрут начинается в `index 0`.

Соседи:

```text
[1, 4]
```

Оба имеют расстояние 4, что лучше текущего 6. Пусть выбран `index 1`.

Соседи `index 1`:

```text
[2, 4]
```

`index 2` имеет расстояние 2, поэтому переходим в него.

Соседи `index 2`:

```text
[3, 0]
```

`index 3` имеет расстояние 1, поэтому переходим в него.

Если у `index 3` нет более близкого нового соседа, маршрут останавливается.

---

# 36. Почему результат приближённый

Алгоритм рассматривает только:

- случайные старты;
- посещённые вершины;
- соседей посещённых вершин.

Очень близкая точка может существовать, но не попасть ни в один исследованный маршрут.

Поэтому результат не гарантированно exact.

---

# 37. Почему несколько стартов помогают

Один старт может попасть в неправильный кластер и остановиться в локальном минимуме.

Другой старт может оказаться ближе к правильной области.

Все посещённые точки из разных маршрутов объединяются, затем из них выбирается общий top-K.

---

# 38. Ручная проверка distance

```python
import numpy as np

from gp_page_1_solution import distance


point = np.array([1.0, 2.0])
documents = np.array([
    [1.0, 2.0],
    [4.0, 6.0],
    [2.0, 2.0]
])

result = distance(point, documents)

print(result)
print(result.shape)
```

Ожидается:

```text
[[0.]
 [5.]
 [1.]]

(3, 1)
```

---

# 39. Проверка графа

Для маленького датасета нужно уменьшить параметры, иначе кандидатов может быть меньше требуемого числа рёбер.

```python
import numpy as np

from gp_page_1_solution import create_sw_graph


np.random.seed(42)

data = np.array([
    [0.0],
    [1.0],
    [2.0],
    [10.0],
    [11.0],
    [12.0]
])

graph = create_sw_graph(
    data,
    num_candidates_for_choice_long=2,
    num_edges_long=1,
    num_candidates_for_choice_short=2,
    num_edges_short=1
)

print(graph)
```

У каждой вершины будет одно короткое и одно длинное исходящее ребро.

---

# 40. Проверка nsw

```python
import numpy as np

from gp_page_1_solution import create_sw_graph, nsw


np.random.seed(42)

data = np.random.randn(100, 4)
query = np.random.randn(4)

graph = create_sw_graph(data)

result = nsw(
    query,
    data,
    graph,
    search_k=10,
    num_start_points=5
)

print(result)
print(result.shape)
```

Ожидаемая форма:

```text
(10,)
```

---

# 41. Сравнение с exact KNN

```python
from gp_page_1_solution import distance, nsw


exact = np.argsort(
    distance(query, data).reshape(-1)
)[:10]

approximate = nsw(
    query,
    data,
    graph,
    search_k=10,
    num_start_points=5
)

recall = len(
    set(exact) & set(approximate)
) / 10

print("exact:", exact)
print("approximate:", approximate)
print("Recall@10:", recall)
```

Пересечение множеств:

```python
set(exact) & set(approximate)
```

содержит индексы, найденные обоими методами.

---

# 42. Частые ошибки

## Ошибка 1. Возвращать `(N,)`

Неверно:

```python
np.linalg.norm(pointA - documents, axis=1)
```

По условию требуется `(N, 1)`.

## Ошибка 2. Использовать np.sort

`np.sort` возвращает значения расстояний. Для графа нужны индексы, поэтому используется `np.argsort`.

## Ошибка 3. Не удалить саму точку

Точка всегда имеет расстояние ноль до себя и станет собственным соседом.

## Ошибка 4. Использовать replace=True

Одно ребро может быть выбрано несколько раз.

## Ошибка 5. Игнорировать dist_f

Скрытые тесты могут передать кастомную функцию расстояния.

## Ошибка 6. Автоматически добавлять обратные рёбра

Это изменит ожидаемый граф.

## Ошибка 7. Возвращать расстояния вместо индексов

`nsw` должен вернуть индексы документов.

## Ошибка 8. Вернуть меньше search_k

Внешний цикл специально следит, чтобы посещённых точек было достаточно.

## Ошибка 9. Пересчитывать расстояния

Для этого существует `calc_d_and_upd`.

## Ошибка 10. Перепутать позиции argsort и индексы документов

В конце позиции `best_idxs` применяются к списку ключей.

---

# 43. Сложность

## distance

```text
O(ND)
```

## create_sw_graph

Расстояния:

```text
O(N²D)
```

Сортировки:

```text
примерно O(N² log N)
```

Это учебное построение, а не production-вариант.

## nsw

Если посещено `V` вершин и у каждой в среднем `E` соседей:

```text
примерно O(V × E × D)
```

Смысл ANN:

```text
V << N
```

---

# 44. Почему код минимальный

В solution нет:

- классов;
- логирования;
- сложных абстракций;
- сторонних ANN-библиотек;
- лишней production-валидации;
- конфигурационных систем.

Цель — пройти учебные тесты и максимально прямо показать алгоритм.

---

# 45. Что запомнить для интервью

1. Exact KNN сравнивает запрос со всеми точками.
2. ANN сокращает число сравнений.
3. Геометрию задаёт embedding-модель.
4. Короткие рёбра дают локальную точность.
5. Длинные рёбра дают глобальные переходы.
6. Greedy search может застрять.
7. Несколько стартов снижают риск локального минимума.
8. Расстояния полезно кэшировать.
9. Качество ANN измеряется Recall@K.
10. Решение выбирается по recall, latency, memory и cost.
11. ANN обычно является candidate generator.
12. Production HNSW значительно сложнее этого кода.

---

# 46. Весь алгоритм одной фразой

> Мы заранее строим карту связей между векторами, а во время запроса идём по этой карте в сторону более близких точек, чтобы не сравнивать запрос со всей коллекцией.

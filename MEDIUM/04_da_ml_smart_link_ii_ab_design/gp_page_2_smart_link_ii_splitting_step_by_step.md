# Smart-Link II: Splitting — пошаговое объяснение кода с нуля

# 1. Полный код

```python
"""Deterministic traffic splitting for an A/B experiment."""

from bisect import bisect_right
from hashlib import sha256
from math import isclose
from typing import List, Tuple


class Experiment:
    """Contains the logic for assigning clicks to experiment groups."""

    def __init__(
        self,
        experiment_id: int,
        groups: Tuple[str, ...] = ("A", "B"),
        group_weights: List[float] = None,
    ):
        if not groups:
            raise ValueError("At least one group must be provided.")

        self.experiment_id = experiment_id
        self.groups = tuple(groups)

        self.salt = sha256(
            f"experiment:{self.experiment_id}".encode("utf-8")
        ).hexdigest()

        if group_weights is None:
            equal_weight = 1.0 / len(self.groups)
            self.group_weights = [equal_weight] * len(self.groups)
        else:
            if len(group_weights) != len(self.groups):
                raise ValueError(
                    "The number of group weights must match the number of groups."
                )

            if any(weight < 0 for weight in group_weights):
                raise ValueError("Group weights must be non-negative.")

            if not isclose(
                sum(group_weights),
                1.0,
                rel_tol=1e-9,
                abs_tol=1e-9,
            ):
                raise ValueError("Group weights must sum to 1.")

            self.group_weights = list(group_weights)

        cumulative_weight = 0.0
        self._cumulative_weights = []

        for weight in self.group_weights:
            cumulative_weight += weight
            self._cumulative_weights.append(cumulative_weight)

        self._cumulative_weights[-1] = 1.0

    def group(self, click_id: int) -> Tuple[int, str]:
        """Assign a click to a deterministic experiment group.

        Parameters
        ----------
        click_id: int
            Identifier of the click.

        Returns
        -------
        Tuple[int, str]
            Group index and group name.
        """
        click_key = f"{self.salt}:{click_id}".encode("utf-8")
        digest = sha256(click_key).digest()

        hash_value = int.from_bytes(digest[:8], byteorder="big")
        random_value = hash_value / 2**64

        group_id = bisect_right(
            self._cumulative_weights,
            random_value,
        )

        if group_id == len(self.groups):
            group_id -= 1

        return group_id, self.groups[group_id]
```

---

# 2. Импорты

## 2.1. `bisect_right`

```python
from bisect import bisect_right
```

Модуль `bisect` умеет искать позицию числа в отсортированном списке.

Нам нужно определить, между какими накопленными границами находится хеш-число.

Пример:

```python
boundaries = [0.5, 1.0]
value = 0.73
```

`0.73` находится между `0.5` и `1.0`.

Значит, оно относится к группе с индексом `1`.

---

## 2.2. `sha256`

```python
from hashlib import sha256
```

`sha256` превращает входную строку в длинное хеш-значение.

Главные свойства:

- одинаковый вход дает одинаковый результат;
- маленькое изменение входа сильно меняет результат;
- результаты хорошо распределены;
- функция стабильна между запусками Python.

---

## 2.3. `isclose`

```python
from math import isclose
```

Нам нужно проверить:

```text
сумма весов = 1
```

Но числа с плавающей точкой хранятся приближенно.

Например:

```python
0.1 + 0.2
```

может дать:

```text
0.30000000000000004
```

Поэтому вместо строгого сравнения:

```python
sum(weights) == 1.0
```

используется:

```python
isclose(sum(weights), 1.0)
```

---

## 2.4. Типы

```python
from typing import List, Tuple
```

Они используются в аннотациях.

```python
groups: Tuple[str, ...]
```

означает кортеж строк произвольной длины.

```python
group_weights: List[float]
```

означает список чисел с плавающей точкой.

```python
Tuple[int, str]
```

означает, что метод возвращает пару:

```text
целое число + строка
```

---

# 3. Объявление класса

```python
class Experiment:
```

Класс — шаблон для создания объектов эксперимента.

Пример объекта:

```python
experiment = Experiment(experiment_id=42)
```

В объекте сохраняются:

- идентификатор эксперимента;
- названия групп;
- веса;
- соль;
- накопленные границы.

---

# 4. Конструктор `__init__`

```python
def __init__(
    self,
    experiment_id: int,
    groups: Tuple[str, ...] = ("A", "B"),
    group_weights: List[float] = None,
):
```

`__init__` вызывается при создании объекта.

Пример:

```python
Experiment(experiment_id=10)
```

Аргументы:

## `experiment_id`

Уникальный номер эксперимента.

Он влияет на соль и, следовательно, на распределение.

## `groups`

Названия групп.

По умолчанию:

```python
("A", "B")
```

## `group_weights`

Желаемые доли групп.

По умолчанию:

```python
None
```

`None` означает: самостоятельно создать равные веса.

---

# 5. Проверка наличия групп

```python
if not groups:
    raise ValueError("At least one group must be provided.")
```

Пустой список или кортеж групп не имеет смысла.

Нельзя назначить клик, если нет ни одной группы.

---

# 6. Сохранение параметров

```python
self.experiment_id = experiment_id
self.groups = tuple(groups)
```

`self` означает текущий объект.

После этого можно обращаться:

```python
experiment.experiment_id
experiment.groups
```

`tuple(groups)` гарантирует, что группы хранятся как кортеж.

---

# 7. Создание соли

```python
self.salt = sha256(
    f"experiment:{self.experiment_id}".encode("utf-8")
).hexdigest()
```

Разберем по частям.

## 7.1. Формирование строки

Для `experiment_id=42`:

```python
f"experiment:{self.experiment_id}"
```

получается:

```text
experiment:42
```

## 7.2. Преобразование в байты

```python
.encode("utf-8")
```

`sha256` работает с байтами, а не с обычной строкой.

## 7.3. Вычисление хеша

```python
sha256(...)
```

## 7.4. Преобразование в текст

```python
.hexdigest()
```

Получается строка из шестнадцатеричных символов.

Для одного `experiment_id` она всегда одинаковая.

---

# 8. Равные веса по умолчанию

```python
if group_weights is None:
    equal_weight = 1.0 / len(self.groups)
    self.group_weights = [equal_weight] * len(self.groups)
```

## Две группы

```text
1 / 2 = 0.5
```

Результат:

```python
[0.5, 0.5]
```

## Четыре группы

```text
1 / 4 = 0.25
```

Результат:

```python
[0.25, 0.25, 0.25, 0.25]
```

---

# 9. Проверка пользовательских весов

## 9.1. Число весов

```python
if len(group_weights) != len(self.groups):
```

Каждая группа должна иметь один вес.

Корректно:

```python
groups=("A", "B", "C")
group_weights=[0.8, 0.1, 0.1]
```

Некорректно:

```python
groups=("A", "B", "C")
group_weights=[0.5, 0.5]
```

---

## 9.2. Неотрицательность

```python
if any(weight < 0 for weight in group_weights):
```

`any(...)` возвращает `True`, если хотя бы один вес отрицательный.

Некорректно:

```python
[0.7, 0.4, -0.1]
```

Нулевой вес разрешен:

```python
[1.0, 0.0]
```

Это означает, что вторая группа не получает трафик.

---

## 9.3. Сумма весов

```python
if not isclose(
    sum(group_weights),
    1.0,
    rel_tol=1e-9,
    abs_tol=1e-9,
):
```

Проверяется, что сумма практически равна единице.

Корректно:

```python
[0.9, 0.05, 0.05]
```

Некорректно:

```python
[0.9, 0.05, 0.04]
```

---

## 9.4. Копирование списка

```python
self.group_weights = list(group_weights)
```

Создается собственный список внутри объекта.

Это защищает объект от части внешних изменений.

---

# 10. Накопленные веса

```python
cumulative_weight = 0.0
self._cumulative_weights = []
```

`cumulative_weight` — текущая сумма.

Подчеркивание в имени:

```python
_cumulative_weights
```

означает, что это внутренний технический атрибут класса.

---

## Цикл

```python
for weight in self.group_weights:
    cumulative_weight += weight
    self._cumulative_weights.append(cumulative_weight)
```

Для:

```python
[0.9, 0.05, 0.05]
```

шаги:

```text
начало: 0.00
+ 0.90 = 0.90
+ 0.05 = 0.95
+ 0.05 = 1.00
```

Результат:

```python
[0.90, 0.95, 1.00]
```

---

## Последняя граница

```python
self._cumulative_weights[-1] = 1.0
```

Из-за представления float последняя сумма теоретически может быть:

```text
0.9999999999999999
```

Мы принудительно ставим:

```text
1.0
```

Это делает последнюю границу надежной.

---

# 11. Метод `group`

```python
def group(self, click_id: int) -> Tuple[int, str]:
```

Метод принимает `click_id`.

Он должен вернуть:

```python
(group_id, group_name)
```

---

# 12. Построение ключа клика

```python
click_key = f"{self.salt}:{click_id}".encode("utf-8")
```

Пример внутренней строки:

```text
<salt>:12345
```

Для другого эксперимента соль изменится.

Для другого клика изменится `click_id`.

Следовательно, хеш также изменится.

---

# 13. Хеш клика

```python
digest = sha256(click_key).digest()
```

`.digest()` возвращает 32 байта.

Нам не обязательно использовать все 32 байта.

Для разбиения трафика достаточно первых восьми:

```python
digest[:8]
```

Восемь байт дают:

```text
2^64
```

возможных значений.

Это огромный диапазон.

---

# 14. Преобразование байтов в целое число

```python
hash_value = int.from_bytes(digest[:8], byteorder="big")
```

Компьютер хранит байты, но для математической нормализации нам нужно целое число.

`byteorder="big"` задает порядок чтения байтов.

Для результата задачи конкретный порядок не принципиален, если он всегда одинаков.

---

# 15. Число от 0 до 1

```python
random_value = hash_value / 2**64
```

Максимальный `hash_value` меньше `2**64`.

Поэтому:

```text
0 <= random_value < 1
```

Это число используется как точка на интервале.

---

# 16. Поиск группы

```python
group_id = bisect_right(
    self._cumulative_weights,
    random_value,
)
```

## Для 50/50

Границы:

```python
[0.5, 1.0]
```

Если:

```text
random_value = 0.2
```

группа:

```text
0 → A
```

Если:

```text
random_value = 0.8
```

группа:

```text
1 → B
```

## Для 90/5/5

Границы:

```python
[0.9, 0.95, 1.0]
```

Соответствие:

```text
0.00–0.90 → A
0.90–0.95 → B
0.95–1.00 → C
```

---

# 17. Защитная проверка индекса

```python
if group_id == len(self.groups):
    group_id -= 1
```

Теоретически нормализованное значение должно быть меньше единицы.

Последняя граница также равна единице.

Поэтому обычно эта ветка не потребуется.

Но она защищает код от крайнего граничного случая и гарантирует допустимый индекс.

---

# 18. Возвращаемое значение

```python
return group_id, self.groups[group_id]
```

Если:

```text
group_id = 1
groups = ("A", "B")
```

возвращается:

```python
(1, "B")
```

Это в точности соответствует API задания.

---

# 19. Примеры использования

## 19.1. Стандартный A/B

```python
experiment = Experiment(experiment_id=1)

print(experiment.group(100))
print(experiment.group(101))
print(experiment.group(102))
```

Назначения могут быть, например:

```text
(1, "B")
(0, "A")
(1, "B")
```

---

## 19.2. Повторяемость

```python
experiment = Experiment(experiment_id=1)

first_result = experiment.group(100)
second_result = experiment.group(100)

print(first_result == second_result)
```

Результат:

```text
True
```

---

## 19.3. Два эксперимента

```python
experiment_1 = Experiment(experiment_id=1)
experiment_2 = Experiment(experiment_id=2)

print(experiment_1.group(100))
print(experiment_2.group(100))
```

Результаты могут различаться, потому что соли разные.

---

## 19.4. Три группы

```python
experiment = Experiment(
    experiment_id=10,
    groups=("control", "model_1", "model_2"),
)
```

Веса автоматически:

```text
1/3, 1/3, 1/3
```

---

## 19.5. Неравномерный сплит

```python
experiment = Experiment(
    experiment_id=10,
    groups=("A", "B", "C"),
    group_weights=[0.90, 0.05, 0.05],
)
```

---

# 20. Сложность алгоритма

Пусть число групп равно `k`.

## Создание объекта

Построение накопленных весов:

```text
O(k)
```

## Один вызов `group`

- SHA-256 работает с короткой строкой;
- бинарный поиск `bisect_right`:

```text
O(log k)
```

В обычном A/B-тесте `k` очень мало, поэтому метод работает быстро.

---

# 21. Почему решение минимальное

Здесь нет:

- NumPy;
- pandas;
- SciPy;
- сторонних random-библиотек;
- базы данных;
- глобального состояния;
- лишних классов.

Используется только стандартная библиотека Python.

Это уменьшает число зависимостей и риск ошибок.

---

# 22. Самое главное для понимания

Запомните цепочку:

```text
experiment_id
    ↓
детерминированная соль
    ↓
salt + click_id
    ↓
SHA-256
    ↓
число от 0 до 1
    ↓
интервал весов
    ↓
group_id и group_name
```

Один и тот же вход проходит по одной и той же цепочке, поэтому результат воспроизводим.

Разные клики и разные эксперименты создают другие хеши, поэтому трафик хорошо перемешивается.

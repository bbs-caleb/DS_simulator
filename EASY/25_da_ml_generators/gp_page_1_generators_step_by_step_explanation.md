# Пошаговое объяснение решения

## 1. Полный код

```python
import random


def username_generator(n, first_names=None, last_names=None):
    """Generate user dictionaries with sequential unique IDs."""
    if first_names is None:
        first_names = ["Alex", "Maria", "John", "Anna"]

    if last_names is None:
        last_names = ["Smith", "Brown", "Wilson", "Taylor"]

    for user_id in range(1, n + 1):
        yield {
            "id": user_id,
            "first_name": random.choice(first_names),
            "last_name": random.choice(last_names),
        }


def data_generator(n):
    """Generate pairs of an index and a random integer from 0 to 100."""
    for x_value in range(n):
        yield x_value, random.randint(0, 100)
```

---

# 2. Первая строка: импорт модуля

```python
import random
```

Python поставляется с готовыми модулями. Модуль `random` содержит функции для получения псевдослучайных значений.

После импорта доступны:

```python
random.choice(...)
random.randint(...)
```

`random.choice` выбирает один элемент последовательности.

`random.randint(a, b)` выбирает целое число от `a` до `b`, включая обе границы.

---

# 3. Объявление `username_generator`

```python
def username_generator(n, first_names=None, last_names=None):
```

## `def`

`def` создаёт функцию.

## Имя функции

Имя должно точно совпадать с заданием:

```text
username_generator
```

Автотест, вероятнее всего, делает импорт примерно так:

```python
from solution import username_generator
```

Если назвать функцию иначе, тест не найдёт её.

## Параметр `n`

`n` — число пользователей.

```python
username_generator(3)
```

означает: создать генератор, который сможет выдать три записи.

## Параметр `first_names`

```python
first_names=None
```

Это необязательный параметр.

Если список не передан, внутри функции будет `None`.

Если передан:

```python
username_generator(
    3,
    ["Max", "Sophia", "Liam"],
)
```

то функция использует именно этот список.

## Параметр `last_names`

Работает аналогично.

---

# 4. Docstring

```python
"""Generate user dictionaries with sequential unique IDs."""
```

Это строка документации.

Она объясняет назначение функции и улучшает читаемость.

Посмотреть её можно через:

```python
help(username_generator)
```

Docstring не влияет на вычисление результата.

---

# 5. Список имён по умолчанию

```python
if first_names is None:
    first_names = ["Alex", "Maria", "John", "Anna"]
```

## Что делает `if`

Блок выполняется только при истинном условии.

## Что означает `is None`

Проверяется, что пользователь не передал список.

Если вызов такой:

```python
username_generator(3)
```

то `first_names` равен `None`, и создаётся внутренний список.

Если вызов такой:

```python
username_generator(3, ["Max"])
```

то условие ложно и переданный список не заменяется.

## Почему не `if not first_names`

Потому что:

```python
None
[]
```

— разные значения.

`None` означает, что аргумент не задан.

Пустой список означает, что пользователь явно передал коллекцию без элементов.

Проверка `is None` точнее соблюдает контракт API.

---

# 6. Список фамилий по умолчанию

```python
if last_names is None:
    last_names = ["Smith", "Brown", "Wilson", "Taylor"]
```

Логика полностью аналогична списку имён.

После двух проверок функция имеет:

- список имён;
- список фамилий.

---

# 7. Цикл генерации пользователей

```python
for user_id in range(1, n + 1):
```

Разберём справа налево.

## Почему `n + 1`

Правая граница `range` не включается.

```python
range(1, 4)
```

выдаёт:

```text
1, 2, 3
```

Поэтому для `n = 3` нужна правая граница `4`, то есть `n + 1`.

## Что получает `user_id`

Для `n = 3`:

```text
первая итерация: user_id = 1
вторая итерация: user_id = 2
третья итерация: user_id = 3
```

Именно это обеспечивает последовательные уникальные ID.

---

# 8. Формирование словаря

```python
{
    "id": user_id,
    "first_name": random.choice(first_names),
    "last_name": random.choice(last_names),
}
```

Словарь хранит пары `ключ: значение`.

## Ключ `id`

```python
"id": user_id
```

На первой итерации значение равно `1`.

## Ключ `first_name`

```python
"first_name": random.choice(first_names)
```

Выбирается один случайный элемент списка.

## Ключ `last_name`

```python
"last_name": random.choice(last_names)
```

Выбирается одна случайная фамилия.

Ключи должны называться строго:

```text
id
first_name
last_name
```

Переименование нарушит API задания.

---

# 9. Что делает `yield`

```python
yield {
    ...
}
```

`yield` отдаёт один словарь и приостанавливает функцию.

Функция не завершается окончательно.

Она сохраняет:

- текущее значение `user_id`;
- списки имён и фамилий;
- позицию в цикле;
- место после `yield`.

При следующем запросе функция продолжит цикл.

---

# 10. Что происходит при вызове функции

```python
generator = username_generator(3)
```

На этой строке все пользователи ещё не созданы.

Создаётся генераторный объект.

Первый пользователь появляется только здесь:

```python
first_user = next(generator)
```

Второй:

```python
second_user = next(generator)
```

Третий:

```python
third_user = next(generator)
```

Четвёртый вызов:

```python
next(generator)
```

приведёт к `StopIteration`.

Цикл `for` скрывает эту механику:

```python
for user in username_generator(3):
    print(user)
```

---

# 11. Мысленное выполнение `username_generator(2)`

Вызов:

```python
generator = username_generator(2)
```

Состояние:

```text
Объект создан. Тело функции ещё не дошло до yield.
```

Первый `next(generator)`:

1. Проверяется `first_names is None`.
2. Создаётся стандартный список имён.
3. Проверяется `last_names is None`.
4. Создаётся стандартный список фамилий.
5. `range(1, 3)` выдаёт `1`.
6. Выбирается имя.
7. Выбирается фамилия.
8. Формируется словарь с ID `1`.
9. Словарь отдаётся наружу.
10. Выполнение замораживается.

Второй `next(generator)`:

1. Выполнение продолжается после первого `yield`.
2. Цикл получает `user_id = 2`.
3. Снова выбираются имя и фамилия.
4. Формируется словарь с ID `2`.
5. Словарь отдаётся.
6. Выполнение снова приостанавливается.

Третий `next(generator)`:

1. Цикл пытается получить следующий ID.
2. Значений больше нет.
3. Функция завершается.
4. Python сообщает `StopIteration`.

---

# 12. Объявление второй функции

```python
def data_generator(n):
```

Имя должно строго совпадать с заданием.

Функция принимает только один параметр — количество точек.

---

# 13. Цикл для `x`

```python
for x_value in range(n):
```

`range(n)` начинается с нуля.

Для `n = 3`:

```text
0, 1, 2
```

Это точно соответствует условию: `x` — последовательно возрастающее целое число, начиная с `0`.

---

# 14. Случайное значение `y`

```python
random.randint(0, 100)
```

Функция может вернуть:

```text
0, 1, 2, ..., 99, 100
```

Обе границы входят в диапазон.

Это важно. Например:

```python
random.randrange(0, 100)
```

не сможет вернуть `100`.

---

# 15. Выдача кортежа

```python
yield x_value, random.randint(0, 100)
```

Python создаёт кортеж даже без явных скобок.

Это эквивалентно:

```python
yield (x_value, random.randint(0, 100))
```

Для трёх итераций возможен результат:

```text
(0, 49)
(1, 27)
(2, 88)
```

`x` предсказуем, `y` случаен.

---

# 16. Почему в отправляемом файле нет `print`

Платформа импортирует модуль и вызывает функции.

Если добавить на уровне файла:

```python
for user in username_generator(3):
    print(user)
```

этот код запустится во время импорта.

Это создаёт нежелательный вывод и может мешать тестам.

Поэтому в solution-файле находятся только:

- импорт;
- определения функций.

---

# 17. Проверка количества пользователей

```python
users = list(username_generator(5))

assert len(users) == 5
```

`list(...)` исчерпывает генератор и собирает значения в список.

В production это может расходовать память, но в маленьком тесте это нормально.

---

# 18. Проверка ID

```python
users = list(username_generator(3))
ids = [user["id"] for user in users]

assert ids == [1, 2, 3]
```

---

# 19. Проверка пользовательских списков

```python
users = list(
    username_generator(
        3,
        first_names=["OnlyName"],
        last_names=["OnlySurname"],
    )
)
```

Поскольку каждый список содержит один элемент, случайный выбор всегда вернёт его.

```python
for user in users:
    assert user["first_name"] == "OnlyName"
    assert user["last_name"] == "OnlySurname"
```

Так можно надёжно проверить использование переданных аргументов.

---

# 20. Проверка точек графика

```python
points = list(data_generator(5))

assert len(points) == 5
assert [point[0] for point in points] == [0, 1, 2, 3, 4]

for _, y_value in points:
    assert 0 <= y_value <= 100
```

---

# 21. Проверка типа генератора

```python
import types


assert isinstance(
    username_generator(1),
    types.GeneratorType,
)

assert isinstance(
    data_generator(1),
    types.GeneratorType,
)
```

Если вместо `yield` вернуть список, такой тест не пройдёт.

---

# 22. Граничные случаи

## `n = 0`

```python
list(username_generator(0))
```

Результат:

```python
[]
```

Потому что диапазон не содержит значений.

То же самое:

```python
list(data_generator(0))
```

## Отрицательное `n`

```python
list(data_generator(-3))
```

тоже даёт пустой список.

Условие не требует отдельной ошибки, поэтому дополнительная валидация не добавлена.

## Повторяющиеся имена

Допустимы:

```python
[
    {"id": 1, "first_name": "Alex", ...},
    {"id": 2, "first_name": "Alex", ...},
]
```

Уникальность требуется для ID, не для комбинации имени и фамилии.

---

# 23. Почему решение минимальное

Можно было добавить:

- аннотации типов;
- проверку типа `n`;
- ошибку для пустых списков;
- параметр `seed`;
- класс пользователя;
- логирование;
- dataclass;
- дополнительные параметры.

Но это не требуется условием.

Для учебного автогрейдера лучшая стратегия:

> Строго сохранить API, реализовать нужное поведение и не создавать лишних побочных эффектов.

---

# 24. Типичные неверные решения

## Возврат списка

```python
def data_generator(n):
    result = []

    for x_value in range(n):
        result.append(
            (x_value, random.randint(0, 100))
        )

    return result
```

Почему неверно:

- отсутствует `yield`;
- возвращается готовый список;
- функция не является генератором;
- нарушено прямое требование задания.

## ID с нуля

```python
for user_id in range(n):
```

Для `n = 3` получим:

```text
0, 1, 2
```

## Один `return` внутри цикла

```python
for user_id in range(1, n + 1):
    return {
        "id": user_id,
        ...
    }
```

Функция завершится на первом пользователе.

## Вывести словарь, но не отдать

```python
print(user)
```

Печать и возвращаемое значение — разные вещи.

---

# 25. Что проверять перед отправкой

1. Расширение файла — `.py`.
2. Есть `import random`.
3. Имя первой функции — `username_generator`.
4. Имя второй — `data_generator`.
5. Первая функция имеет нужные три параметра.
6. Вторая функция имеет один параметр.
7. В обеих функциях используется `yield`.
8. ID начинается с `1`.
9. `x` начинается с `0`.
10. `y` попадает в диапазон `[0, 100]`.
11. Ключи словаря написаны правильно.
12. В файле нет запуска примеров.
13. В файле нет лишнего вывода.
14. Файл импортируется без синтаксической ошибки.

---

# 26. Модель понимания

```text
генераторная функция
        |
        | вызов
        v
генераторный объект
        |
        | next()
        v
один элемент
        |
        | next()
        v
следующий элемент
        |
        | после исчерпания
        v
StopIteration
```

Ключевая формула:

```text
yield = отдать значение сейчас + сохранить состояние + продолжить позже
```

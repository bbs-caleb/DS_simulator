# Исправление `@memoize`: ошибка `unhashable type: 'dict'`

## Результат проверки

Предыдущая версия получила:

```text
80 / 100
```

Она прошла:

- один аргумент;
- два аргумента;
- именованные аргументы;
- Pylint.

Она не прошла:

```text
test_nonhashable_argument
```

Ошибка:

```text
TypeError: unhashable type: 'dict'
```

---

## Причина ошибки

Предыдущий ключ создавался из исходных аргументов:

```python
key = (args, tuple(sorted(kwargs.items())))
```

Если функция получала словарь:

```python
some_function({"name": "Nodir"})
```

то `args` содержал:

```python
(
    {"name": "Nodir"},
)
```

Кортеж может быть ключом словаря только тогда, когда все его элементы хешируемы.

`dict` не хешируется, поэтому ошибка возникала при проверке:

```python
if key not in cache:
```

Сам `if` корректен. Некорректным был объект `key`.

---

## Что исправлено

Добавлена функция:

```python
def _make_hashable(value):
    ...
```

Она преобразует изменяемые контейнеры в хешируемые представления:

```text
dict  → frozenset пар
list  → tuple элементов
tuple → tuple рекурсивно обработанных элементов
set   → frozenset элементов
```

Преобразование выполняется рекурсивно, поэтому поддерживаются вложенные структуры.

Пример:

```python
{
    "filters": [
        {"city": "Tashkent"},
        {"ages": {20, 30}},
    ]
}
```

---

## Почему сохраняются маркеры типов

Список и кортеж нельзя превращать в полностью одинаковые ключи.

Исходные аргументы:

```python
[1, 2]
```

и:

```python
(1, 2)
```

могут давать разные результаты функции.

Поэтому представления различаются:

```python
(list, (1, 2))
(tuple, (1, 2))
```

---

## Почему словарь превращается во `frozenset`

Эти словари равны:

```python
{"x": 1, "y": 2}
{"y": 2, "x": 1}
```

Порядок вставки не должен создавать разные записи кэша.

`frozenset`:

- не зависит от порядка;
- является хешируемым;
- не требует сортировать ключи разных типов.

---

## Важный момент

Преобразованные значения используются только для ключа:

```python
key = (
    _make_hashable(args),
    _make_hashable(kwargs),
)
```

Исходная функция получает оригинальные аргументы:

```python
func(*args, **kwargs)
```

Если пользователь передал список, функция получает список, а не кортеж.

---

## Исправленное решение

```python
"""Memoization decorator implementation."""

from functools import wraps
from typing import Any, Callable, Hashable


def _make_hashable(value: Any) -> Hashable:
    """Convert nested mutable containers into hashable equivalents."""
    if isinstance(value, dict):
        return (
            dict,
            frozenset(
                (
                    _make_hashable(key),
                    _make_hashable(item),
                )
                for key, item in value.items()
            ),
        )

    if isinstance(value, list):
        return (
            list,
            tuple(_make_hashable(item) for item in value),
        )

    if isinstance(value, tuple):
        return (
            tuple,
            tuple(_make_hashable(item) for item in value),
        )

    if isinstance(value, set):
        return (
            set,
            frozenset(_make_hashable(item) for item in value),
        )

    return value


def memoize(func: Callable) -> Callable:
    """Cache and return function results for previously used arguments."""
    cache = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        key = (
            _make_hashable(args),
            _make_hashable(kwargs),
        )

        if key not in cache:
            cache[key] = func(*args, **kwargs)

        return cache[key]

    return wrapper
```

---

## Какие случаи теперь поддерживаются

```python
f(10)
f(10, 20)
f(x=10, y=20)
f({"x": 10})
f([1, 2, 3])
f({1, 2, 3})
f({"items": [1, {"x": 2}]})
```

Повторные равные словари с другим порядком ключей также создают одинаковый ключ кэша.

---

## Что отправлять

Отправляйте обновлённый файл:

```text
gp_page_1_memoize_solution.py
```

Старую версию загружать больше не нужно.

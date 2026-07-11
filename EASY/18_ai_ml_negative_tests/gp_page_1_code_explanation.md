# Пошаговое объяснение `test_metrics.py`

## 1. Что нужно сделать

Функция `ctr` уже находится в модуле `metrics.py`. Мы не изменяем её. Мы создаём тесты, которые намеренно передают неправильные данные и проверяют ожидаемые исключения.

Проверяющая система отдельно предупреждает:

> Не изменяйте формат импорта и использования функции.

Поэтому сохраняем:

```python
import metrics
```

и каждый вызов выполняем через:

```python
metrics.ctr(...)
```

---

## 2. Готовое решение

```python
import metrics


def test_non_int_clicks():
    try:
        metrics.ctr(1.5, 2)
    except TypeError:
        pass
    else:
        raise AssertionError("Non int clicks not handled")


def test_non_int_views():
    try:
        metrics.ctr(1, 2.5)
    except TypeError:
        pass
    else:
        raise AssertionError("Non int views not handled")


def test_non_positive_clicks():
    try:
        metrics.ctr(-1, 2)
    except ValueError:
        pass
    else:
        raise AssertionError("Non positive clicks not handled")


def test_non_positive_views():
    try:
        metrics.ctr(0, -1)
    except ValueError:
        pass
    else:
        raise AssertionError("Non positive views not handled")


def test_clicks_greater_than_views():
    try:
        metrics.ctr(3, 2)
    except ValueError:
        pass
    else:
        raise AssertionError("Clicks greater than views not handled")


def test_zero_views():
    try:
        metrics.ctr(0, 0)
    except ZeroDivisionError:
        pass
    else:
        raise AssertionError("Zero views not handled")
```

---

# 3. Разбор импорта

```python
import metrics
```

Python загружает файл `metrics.py` как модуль с именем `metrics`.

Функция внутри вызывается через точку:

```python
metrics.ctr
```

Точка означает: получить объект `ctr`, принадлежащий модулю `metrics`.

Мы не пишем:

```python
from metrics import ctr
```

не потому, что это всегда неправильно, а потому, что условие требует сохранить формат.

---

# 4. Почему две пустые строки

После импорта до верхнеуровневой функции стоят две пустые строки:

```python
import metrics


def test_non_int_clicks():
```

Это рекомендация PEP8. В задании 25% баллов выделено на качество кода, поэтому оформление важно.

---

# 5. Общая конструкция каждого теста

```python
def test_name():
    try:
        function_call()
    except ExpectedError:
        pass
    else:
        raise AssertionError("...")
```

## `def`

Создаёт функцию.

## Имя `test_...`

`pytest` автоматически ищет функции, имя которых начинается с `test_`.

## `try`

Пытается выполнить вызов с неправильными данными.

## `except ExpectedError`

Перехватывает только нужный тип ошибки.

## `pass`

Ничего не делает: возникновение нужной ошибки уже означает успех теста.

## `else`

У конструкции `try` блок `else` выполняется, когда исключения не возникло.

В негативном тесте это плохо: функция приняла неправильные данные.

## `raise AssertionError`

Вручную проваливает тест и оставляет понятное сообщение.

---

# 6. `test_non_int_clicks`

```python
def test_non_int_clicks():
    try:
        metrics.ctr(1.5, 2)
    except TypeError:
        pass
    else:
        raise AssertionError("Non int clicks not handled")
```

Передаём:
- `clicks = 1.5`;
- `views = 2`.

`1.5` имеет тип `float`, а функция требует `int`.

Внутри `ctr` срабатывает:

```python
if not isinstance(clicks, int):
    raise TypeError(...)
```

Поэтому тест ждёт `TypeError`.

Если функция не выбросила ошибку, выполняется `else`, и тест падает.

---

# 7. `test_non_int_views`

```python
def test_non_int_views():
    try:
        metrics.ctr(1, 2.5)
    except TypeError:
        pass
    else:
        raise AssertionError("Non int views not handled")
```

Здесь:
- `clicks = 1` — правильный `int`;
- `views = 2.5` — неправильный `float`.

Мы оставили клики корректными, чтобы изолировать только проблему просмотров.

Ожидаем `TypeError`.

---

# 8. `test_non_positive_clicks`

```python
def test_non_positive_clicks():
    try:
        metrics.ctr(-1, 2)
    except ValueError:
        pass
    else:
        raise AssertionError("Non positive clicks not handled")
```

`-1` — это `int`, поэтому тип правильный.

Но значение отрицательное:

```python
if clicks < 0:
```

Следовательно, ожидается `ValueError`.

## Почему не передаём 0

Реальный код запрещает только:

```python
clicks < 0
```

Ноль допустим и означает: просмотры были, кликов не было.

Название теста содержит `non_positive`, но ориентироваться нужно на фактический контракт функции. Для гарантированного нарушения передаём `-1`.

---

# 9. `test_non_positive_views`

```python
def test_non_positive_views():
    try:
        metrics.ctr(0, -1)
    except ValueError:
        pass
    else:
        raise AssertionError("Non positive views not handled")
```

Здесь:
- типы правильные;
- клики допустимы;
- просмотры отрицательные.

Внутри срабатывает:

```python
if views < 0:
    raise ValueError(...)
```

Поэтому ждём `ValueError`.

---

# 10. `test_clicks_greater_than_views`

```python
def test_clicks_greater_than_views():
    try:
        metrics.ctr(3, 2)
    except ValueError:
        pass
    else:
        raise AssertionError("Clicks greater than views not handled")
```

Оба значения:
- целые;
- положительные;
- просмотры не равны нулю.

Но нарушено отношение:

```text
3 клика > 2 просмотров
```

Функция проверяет:

```python
if views < clicks:
```

Подстановка:

```python
if 2 < 3:
```

Условие истинно, выбрасывается `ValueError`.

Это проверка бизнес-инварианта между двумя аргументами.

---

# 11. `test_zero_views`

```python
def test_zero_views():
    try:
        metrics.ctr(0, 0)
    except ZeroDivisionError:
        pass
    else:
        raise AssertionError("Zero views not handled")
```

Это самый важный и потенциально ошибочный тест.

Мы хотим дойти до:

```python
if views:
    return clicks / views
else:
    raise ZeroDivisionError(...)
```

При `views = 0` условие `if views` ложно.

## Почему `(0, 0)`, а не `(1, 0)`

Если вызвать:

```python
metrics.ctr(1, 0)
```

проверки идут сверху вниз. До деления функция увидит:

```python
if views < clicks:
```

То есть:

```python
if 0 < 1:
```

и выбросит `ValueError`, потому что кликов больше просмотров.

Тест тогда не проверит `ZeroDivisionError`.

С парой `(0, 0)`:

```python
0 < 0
```

ложно. Функция проходит дальше и выбрасывает именно `ZeroDivisionError`.

---

# 12. Что будет при неправильном исключении

Допустим, тест ожидает:

```python
except TypeError:
```

но функция выбросила `ValueError`.

`except TypeError` его не перехватит. Ошибка выйдет наружу, и тест упадёт.

Это правильное поведение. Мы проверяем не просто факт падения, а точный тип.

---

# 13. Почему не используется `except Exception`

Такой код:

```python
except Exception:
    pass
```

сделал бы тест слишком слабым. Он принял бы любую ошибку, включая случайный `NameError`.

Нужно ловить:
- `TypeError` для неправильных типов;
- `ValueError` для неправильных значений;
- `ZeroDivisionError` для нулевых просмотров.

---

# 14. Почему не используется `pytest.raises`

В обычном проекте можно написать:

```python
import pytest

with pytest.raises(TypeError):
    metrics.ctr(1.5, 2)
```

Но шаблон задания уже задал стиль через `try / except / else`, а импорт и вызов обозначены как критичные.

Самое безопасное решение для автопроверки — продолжить шаблон без лишних библиотек.

---

# 15. Почему тесты ничего не возвращают

Тестовая функция успешна, если завершилась без необработанного исключения.

Она не должна писать:

```python
return True
```

Провал обозначается исключением:
- `AssertionError`;
- либо неожиданной ошибкой тестируемой функции.

---

# 16. PEP8

Решение соблюдает базовые требования:
- четыре пробела на уровень отступа;
- две пустые строки между функциями;
- понятные имена;
- нет лишних импортов;
- строки разумной длины;
- нет закомментированного мусора.

---

# 17. Соответствие каждому пункту

| Функция теста | Вход | Ожидаемая ошибка |
|---|---:|---|
| `test_non_int_clicks` | `(1.5, 2)` | `TypeError` |
| `test_non_int_views` | `(1, 2.5)` | `TypeError` |
| `test_non_positive_clicks` | `(-1, 2)` | `ValueError` |
| `test_non_positive_views` | `(0, -1)` | `ValueError` |
| `test_clicks_greater_than_views` | `(3, 2)` | `ValueError` |
| `test_zero_views` | `(0, 0)` | `ZeroDivisionError` |

---

# 18. Как проверить локально

Структура:

```text
project/
├── metrics.py
└── test_metrics.py
```

Команда:

```bash
python -m pytest -v
```

Ожидается:

```text
6 passed
```

На платформу нужно отправить только `test_metrics.py`, если интерфейс не просит иное.

---

# 19. Чек-лист перед отправкой

- Файл называется `test_metrics.py`.
- Импорт — `import metrics`.
- Вызов — `metrics.ctr(...)`.
- Все шесть функций присутствуют.
- Для отрицательных значений ожидается `ValueError`.
- Для float ожидается `TypeError`.
- Для нулевых просмотров передаётся `(0, 0)`.
- Для нулевых просмотров ожидается `ZeroDivisionError`.
- Нет `except Exception`.
- Нет незаполненных `pass` вместо тестов.

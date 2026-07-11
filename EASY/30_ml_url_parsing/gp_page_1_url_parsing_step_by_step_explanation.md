# URL PARSING — пошаговый разбор финального решения с абсолютного нуля

## 1. Финальный код целиком

```python
"""Extract reachable URLs from a text message."""

import re
from collections import Counter
from typing import Dict

import requests


URL_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.)?"
    r"((?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?)",
    flags=re.IGNORECASE,
)
TRAILING_CHARACTERS = ".,!?;:)]}'\"/"


def normalize_url(url: str) -> str:
    """Normalize the host while preserving the path character case."""
    cleaned_url = url.rstrip(TRAILING_CHARACTERS)
    host, separator, path = cleaned_url.partition("/")

    if not separator:
        return host.lower()

    return f"{host.lower()}/{path}"


def parse_urls(message: str) -> Dict[str, int]:
    """Return occurrence counts for reachable URLs in the message."""
    url_counts = Counter(
        normalize_url(url)
        for url in URL_PATTERN.findall(message)
    )
    reachable_urls = []

    for url in url_counts:
        try:
            response = requests.get(f"http://{url}", timeout=5)
            response.raise_for_status()
            reachable_urls.append(url)
        except requests.RequestException as error:
            print(error)

    return {url: url_counts[url] for url in reachable_urls}
```

Теперь разберём каждую конструкцию.

---

## 2. Строка документации модуля

```python
"""Extract reachable URLs from a text message."""
```

Это module docstring — краткое описание назначения файла.

Она сообщает:

> Этот модуль извлекает доступные URL из текстового сообщения.

Зачем нужна:

- помогает читателю понять назначение файла;
- используется инструментами документации;
- улучшает качество кода;
- обычно нравится линтерам.

---

## 3. Импорт `re`

```python
import re
```

`re` — стандартный модуль Python для регулярных выражений.

Обычный поиск умеет искать конкретную строку:

```python
"example.com" in message
```

Но нам нужно искать **любой** домен.
Поэтому требуется шаблон.

---

## 4. Импорт `Counter`

```python
from collections import Counter
```

`Counter` считает частоты элементов.

Пример:

```python
items = ["a", "b", "a", "a"]
counts = Counter(items)
```

Результат:

```python
Counter({"a": 3, "b": 1})
```

В задаче элементами являются нормализованные URL.

---

## 5. Импорт `Dict`

```python
from typing import Dict
```

`Dict` нужен для аннотации возвращаемого типа:

```python
Dict[str, int]
```

Это читается так:

- ключ словаря — `str`;
- значение — `int`.

Пример:

```python
{"example.com": 2}
```

Аннотация не выполняет проверку сама по себе, но документирует контракт.

---

## 6. Импорт `requests`

```python
import requests
```

`requests` — библиотека для HTTP-запросов.

Она позволяет написать:

```python
requests.get("http://example.com", timeout=5)
```

и попытаться получить ответ от сервера.

---

## 7. Что такое константа

```python
URL_PATTERN = re.compile(...)
TRAILING_CHARACTERS = ".,!?;:)]}'\"/"
```

Имена написаны заглавными буквами.
По соглашению Python это означает:

> Значение является константой уровня модуля и не должно изменяться во время работы.

Python технически не запрещает изменить его, но стиль сообщает намерение программиста.

---

## 8. Зачем компилировать regex заранее

```python
URL_PATTERN = re.compile(...)
```

Можно было бы использовать:

```python
re.findall(pattern, message)
```

Но отдельный скомпилированный объект удобнее:

- шаблон создаётся один раз;
- получает понятное имя;
- код функции становится короче;
- шаблон проще тестировать;
- меньше повторной работы при множестве вызовов.

---

## 9. Полный regex

```python
r"(?:https?://)?(?:www\.)?"
r"((?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?)"
```

Две соседние строковые константы Python автоматически объединяет.
То есть это одна строка.

Разберём слева направо.

---

## 10. Почему используется raw string `r"..."`

Перед строкой стоит `r`:

```python
r"\s"
```

Это raw string.
В ней обратный слеш передаётся regex как есть.

Без `r` пришлось бы чаще удваивать обратные слеши.
Для регулярных выражений raw strings — стандартная практика.

---

## 11. `(?:https?://)?`

Эта часть находит необязательный протокол.

Разбор:

### `(?: ... )`

Незахватывающая группа.
Она объединяет элементы, но не возвращается как отдельный результат.

### `http`

Буквальные символы `http`.

### `s?`

Символ `s` встречается 0 или 1 раз.

Поэтому подходят:

```text
http
https
```

### `://`

Буквальные символы протокола.

### Последний `?`

Вся группа необязательна.

Поэтому подходят и такие формы:

```text
https://example.com
http://example.com
example.com
```

---

## 12. `(?:www\.)?`

Эта группа означает необязательный префикс `www.`.

### `www`

Буквальные символы.

### `\.`

Точка в regex обычно означает любой символ.
Чтобы найти настоящую точку, её нужно экранировать:

```regex
\.
```

### Последний `?`

Вся группа необязательна.

Подходят:

```text
www.example.com
example.com
```

Префикс не входит в захваченную часть, поэтому автоматически удаляется из результата.

---

## 13. Почему основная часть заключена в обычные скобки

```python
(
    (?:[a-zA-Z0-9-]+\.)+
    [a-zA-Z]{2,}
    (?:/[^\s]*)?
)
```

Это захватывающая группа.

`findall` при наличии такой группы возвращает именно её содержимое.

Именно поэтому:

```text
https://www.example.com/path
```

даёт:

```text
example.com/path
```

а протокол и `www.` не входят в результат.

---

## 14. `(?:[a-zA-Z0-9-]+\.)+`

Эта часть описывает одну или несколько частей домена перед доменной зоной.

### `[a-zA-Z0-9-]`

Класс допустимых символов:

- маленькие латинские буквы;
- большие латинские буквы;
- цифры;
- дефис.

### `+`

Один или более символов.

### `\.`

Буквальная точка.

### Внешний `+`

Вся конструкция повторяется один или более раз.

Поэтому подходят:

```text
example.
sub.example.
en.wikipedia.
```

---

## 15. `[a-zA-Z]{2,}`

Это доменная зона.

### `[a-zA-Z]`

Только латинская буква.

### `{2,}`

Минимум два символа, верхняя граница не задана.

Примеры:

```text
com
ru
org
info
```

---

## 16. `(?:/[^\s]*)?`

Это необязательный путь.

### `/`

Путь начинается со слеша.

### `[^\s]`

Квадратные скобки задают класс символов.
`^` внутри них означает отрицание.

`\s` — пробельный символ.

Следовательно:

```regex
[^\s]
```

означает любой непробельный символ.

### `*`

Ноль или более символов.

### Последний `?`

Весь путь необязателен.

Поэтому подходят:

```text
example.com
example.com/path
example.com/questions/tagged/python
example.com/wiki/Special:Random
```

Это исправляет первую реальную ошибку: путь не теряется.

---

## 17. `flags=re.IGNORECASE`

```python
flags=re.IGNORECASE
```

Regex должен находить URL независимо от регистра:

```text
HTTPS://WWW.EXAMPLE.COM
https://www.example.com
```

Но это не означает, что потом нужно перевести весь найденный URL в нижний регистр.
Флаг влияет только на **поиск совпадения**.
Нормализация выполняется отдельно.

---

## 18. Завершающие символы

```python
TRAILING_CHARACTERS = ".,!?;:)]}'\"/"
```

URL часто расположен перед пунктуацией:

```text
Visit example.com.
Open example.com/path,
See example.com/test)
```

Regex захватывает всё до пробела, поэтому в совпадение может попасть финальная точка или скобка.

Эти символы нужно удалить с правого края.

Также удаляется одиночный завершающий `/`:

```text
example.com/
```

становится:

```text
example.com
```

---

## 19. Функция `normalize_url`

```python
def normalize_url(url: str) -> str:
```

Она получает один найденный URL и возвращает нормализованный URL.

Почему вынесена отдельно:

- одна функция — одна ответственность;
- легче читать;
- легче тестировать;
- логика нормализации не смешана с сетью;
- можно переиспользовать.

---

## 20. Docstring функции

```python
"""Normalize the host while preserving the path character case."""
```

Ключевая фраза:

> нормализовать хост, сохраняя регистр пути.

Это напрямую фиксирует скрытое требование.

---

## 21. `rstrip`

```python
cleaned_url = url.rstrip(TRAILING_CHARACTERS)
```

`rstrip(chars)` удаляет с правого края все символы, входящие в `chars`.

Примеры:

```python
"example.com.".rstrip(".")
# "example.com"
```

```python
"example.com/path,)".rstrip(".,)")
# "example.com/path"
```

Важно: он не удаляет символы в середине строки.

---

## 22. `partition("/")`

```python
host, separator, path = cleaned_url.partition("/")
```

`partition` делит строку по первому вхождению разделителя и всегда возвращает три элемента:

```text
часть до разделителя
сам разделитель
часть после разделителя
```

Пример:

```python
"example.com/wiki/Special:Random".partition("/")
```

Результат:

```python
(
    "example.com",
    "/",
    "wiki/Special:Random",
)
```

Если слеша нет:

```python
"example.com".partition("/")
```

Результат:

```python
("example.com", "", "")
```

Почему `partition` удобнее `split`:

- разделяет только по первому слешу;
- сохраняет весь остальной путь;
- всегда возвращает ровно три значения;
- не нужно отдельно проверять длину списка.

---

## 23. Проверка наличия пути

```python
if not separator:
    return host.lower()
```

Если `separator` — пустая строка, значит слеша не было.
URL состоит только из домена.

Тогда достаточно вернуть домен в нижнем регистре.

Пример:

```text
Example.COM
```

становится:

```text
example.com
```

---

## 24. Сохранение регистра пути

```python
return f"{host.lower()}/{path}"
```

Здесь:

- `host.lower()` нормализует домен;
- `/` возвращает разделитель;
- `path` добавляется без `.lower()`.

Пример:

```text
EN.WIKIPEDIA.ORG/wiki/Special:Random
```

Результат:

```text
en.wikipedia.org/wiki/Special:Random
```

Это исправляет вторую реальную ошибку.

---

## 25. Главная функция

```python
def parse_urls(message: str) -> Dict[str, int]:
```

Вход:

```python
message: str
```

Выход:

```python
Dict[str, int]
```

Пример:

```python
parse_urls("Visit example.com and example.com")
```

может вернуть:

```python
{"example.com": 2}
```

---

## 26. Поиск всех URL

```python
URL_PATTERN.findall(message)
```

`findall` возвращает список всех совпадений захватывающей группы.

Пример:

```python
[
    "example.com",
    "example.com/path",
    "google.com",
]
```

Поскольку протокол и `www.` находятся вне захватывающей группы, они уже удалены.

---

## 27. Generator expression

```python
normalize_url(url)
for url in URL_PATTERN.findall(message)
```

Это генераторное выражение.

Оно означает:

> Для каждого найденного URL вызови `normalize_url`.

Пример логики:

```text
www.Example.COM/Path.
        ↓
Example.COM/Path.
        ↓
example.com/Path
```

---

## 28. Создание `Counter`

```python
url_counts = Counter(
    normalize_url(url)
    for url in URL_PATTERN.findall(message)
)
```

Допустим, после нормализации получено:

```python
[
    "example.com",
    "example.com",
    "google.com",
]
```

`Counter` создаст:

```python
Counter({
    "example.com": 2,
    "google.com": 1,
})
```

---

## 29. Почему сеть проверяется после `Counter`

```python
for url in url_counts:
```

Итерация по `Counter` идёт по уникальным ключам.

Если `example.com` встречается 100 раз:

```python
url_counts["example.com"] == 100
```

но цикл посетит ключ только один раз.

Это основная оптимизация скорости.

---

## 30. Список доступных URL

```python
reachable_urls = []
```

Сюда добавляются только URL, запрос к которым завершился успешно.

Сначала список пустой.

---

## 31. Цикл по уникальным URL

```python
for url in url_counts:
```

Если `url_counts` равен:

```python
{
    "example.com": 5,
    "google.com": 2,
}
```

цикл выполнится два раза, а не семь.

---

## 32. `try`

```python
try:
```

Внутри находится операция, которая может завершиться исключением.

Сетевые операции ненадёжны, поэтому их нельзя считать гарантированно успешными.

---

## 33. HTTP-запрос

```python
response = requests.get(f"http://{url}", timeout=5)
```

### f-string

```python
f"http://{url}"
```

подставляет значение переменной.

Если:

```python
url = "example.com/path"
```

получится:

```text
http://example.com/path
```

### Почему добавляется протокол

Нормализованный ключ специально не содержит `http://` или `https://`.
Но для сетевого запроса библиотеке нужен абсолютный URL.

### `timeout=5`

Запрос ограничен по времени согласно условию задания.

---

## 34. `raise_for_status`

```python
response.raise_for_status()
```

HTTP-ответ может технически прийти, но иметь ошибочный статус, например 404 или 500.

`raise_for_status()` превращает такой статус в исключение `HTTPError`, которое является наследником `requests.RequestException`.

Следовательно, такой URL не попадёт в список доступных.

---

## 35. Добавление доступного URL

```python
reachable_urls.append(url)
```

Эта строка выполняется только если:

- `requests.get` не выбросил исключение;
- `raise_for_status` не выбросил исключение.

---

## 36. Обработка ошибки

```python
except requests.RequestException as error:
    print(error)
```

Перехватываются сетевые исключения библиотеки `requests`.

`as error` сохраняет объект исключения в переменную.

`print(error)` соответствует шаблону из задания.

Функция не падает и продолжает цикл.

---

## 37. Финальный dictionary comprehension

```python
return {url: url_counts[url] for url in reachable_urls}
```

Это генерация словаря.

Читается так:

> Для каждого доступного URL создай пару: URL → его исходное количество упоминаний.

Пример:

```python
url_counts = {
    "example.com": 3,
    "broken.test": 2,
}
reachable_urls = ["example.com"]
```

Результат:

```python
{"example.com": 3}
```

---

## 38. Полный ручной проход на примере

Сообщение:

```text
Visit HTTPS://WWW.Example.COM/Path, example.com/Path and broken.test.
```

### Шаг 1. Regex

```python
[
    "Example.COM/Path,",
    "example.com/Path",
    "broken.test.",
]
```

### Шаг 2. Нормализация

```python
[
    "example.com/Path",
    "example.com/Path",
    "broken.test",
]
```

### Шаг 3. Counter

```python
{
    "example.com/Path": 2,
    "broken.test": 1,
}
```

### Шаг 4. Проверка сети

Предположим:

- `example.com/Path` доступен;
- `broken.test` выбрасывает исключение.

### Шаг 5. Результат

```python
{
    "example.com/Path": 2,
}
```

---

## 39. Почему решение минимальное, но качественное

Оно использует только необходимые идеи:

- один regex;
- одна маленькая функция нормализации;
- `Counter`;
- один цикл по уникальным URL;
- стандартную обработку исключений;
- type hints;
- docstrings.

Нет лишних классов, абстракций и зависимостей.

Для учебной функции это хороший баланс:

- просто;
- читаемо;
- быстро;
- тестируемо;
- соответствует API.

---

## 40. Что нужно запомнить из задачи

1. Regex находит шаблоны, а не только конкретные строки.
2. Нормализация должна объединять эквивалентные записи.
3. Нельзя терять путь URL.
4. Нельзя бездумно применять `.lower()` ко всей строке.
5. Дорогие сетевые операции выполняются после дедупликации.
6. Сеть всегда требует timeout и обработки исключений.
7. Маленькую логику полезно выносить в отдельную функцию.
8. Скрытые тесты часто проверяют семантику данных, а не только пример из условия.

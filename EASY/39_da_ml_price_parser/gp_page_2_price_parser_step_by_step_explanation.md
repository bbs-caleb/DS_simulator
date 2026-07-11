# DA/ML: PRICE PARSER — страница 2

# Шаг 3. Пошаговое объяснение кода с нуля

## 1. Полный код

```python
"""Extract product information from an HTML product card."""

import re
from html import unescape
from typing import Pattern


def _make_tag_pattern(tag_name: str, class_name: str) -> Pattern[str]:
    """Build a pattern for an HTML tag with the required CSS class."""
    escaped_class = re.escape(class_name)
    return re.compile(
        rf'<{tag_name}\b[^>]*\bclass\s*=\s*["\'][^"\']*'
        rf'(?<![\w-]){escaped_class}(?![\w-])[^"\']*["\'][^>]*>'
        rf'(?P<content>.*?)</{tag_name}\s*>',
        flags=re.IGNORECASE | re.DOTALL,
    )


TITLE_PATTERN = _make_tag_pattern("h1", "product-title")
CATEGORY_PATTERN = _make_tag_pattern("div", "product-category")
OLD_PRICE_PATTERN = _make_tag_pattern("span", "price-old")
NEW_PRICE_PATTERN = _make_tag_pattern("span", "price-new")
HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
WHITESPACE_PATTERN = re.compile(r"\s+")


def _extract_text(html: str, pattern: Pattern[str]) -> str:
    """Extract and clean text from the first tag matched by pattern."""
    match = pattern.search(html)
    if match is None:
        return ""

    inner_html = match.group("content")
    text_without_tags = HTML_TAG_PATTERN.sub("", inner_html)
    decoded_text = unescape(text_without_tags)
    return WHITESPACE_PATTERN.sub(" ", decoded_text).strip()


def parse_product_info(html: str) -> dict:
    """Extract product title, category, old price, and current price."""
    product_info = {
        "title": _extract_text(html, TITLE_PATTERN),
        "category": _extract_text(html, CATEGORY_PATTERN),
        "old_price": _extract_text(html, OLD_PRICE_PATTERN),
        "new_price": _extract_text(html, NEW_PRICE_PATTERN),
    }
    return product_info
```

---

## 2. Docstring файла

```python
"""Extract product information from an HTML product card."""
```

Это описание всего модуля. Оно сообщает, что файл извлекает информацию о товаре из HTML-карточки.

На вычисления docstring не влияет, но:

- делает код понятнее;
- помогает документации;
- улучшает качество по Pylint;
- показывает назначение файла.

---

## 3. Импорт `re`

```python
import re
```

`re` — стандартная библиотека Python для регулярных выражений.

Она нужна для:

- компиляции шаблонов;
- поиска нужных HTML-блоков;
- удаления вложенных тегов;
- нормализации пробелов.

Устанавливать её отдельно не нужно.

---

## 4. Импорт `unescape`

```python
from html import unescape
```

HTML использует специальные записи:

```text
&amp;
&nbsp;
&lt;
&gt;
```

`unescape` превращает их в обычный текст:

```python
unescape("TV &amp; Video")
# "TV & Video"
```

```python
unescape("50&nbsp;000 ₽")
# между 50 и 000 будет неразрывный пробел
```

Дальше неразрывный пробел нормализуется обычным regex для пробелов.

---

## 5. Импорт `Pattern`

```python
from typing import Pattern
```

`Pattern[str]` — аннотация типа для скомпилированного регулярного выражения.

Она объясняет, что аргумент или результат является regex-шаблоном для строк.

Аннотация не меняет выполнение программы. Она нужна для:

- читаемости;
- IDE;
- статической проверки;
- понятного контракта функции.

---

## 6. Генератор шаблонов

```python
def _make_tag_pattern(tag_name: str, class_name: str) -> Pattern[str]:
```

Функция получает два значения.

Например:

```python
tag_name = "h1"
class_name = "product-title"
```

Она создаёт шаблон, который ищет:

```html
<h1 class="product-title">...</h1>
```

Почему это отдельная функция?

Без неё пришлось бы четыре раза вручную писать почти одинаковый длинный regex.

---

## 7. Почему имя начинается с `_`

```python
_make_tag_pattern
```

Подчёркивание означает:

> Это внутренняя вспомогательная функция модуля.

Публичная функция, которую проверяет система:

```python
parse_product_info
```

Пользователь не обязан вызывать вспомогательные функции напрямую.

---

## 8. Экранирование класса

```python
escaped_class = re.escape(class_name)
```

Некоторые символы имеют специальное значение в regex.

Например точка:

```regex
.
```

означает любой символ.

`re.escape` превращает переданную строку в безопасный фрагмент шаблона.

Это хорошая привычка, когда часть regex строится из переменной.

---

## 9. `re.compile`

```python
return re.compile(
```

`re.compile` создаёт объект шаблона.

После этого можно писать:

```python
pattern.search(html)
```

а не передавать строковый regex в `re.search` при каждом вызове.

---

## 10. Префикс `rf`

```python
rf'...'
```

Он объединяет:

- `r` — raw string;
- `f` — f-string.

### Raw string

Позволяет удобно писать:

```python
\b
\s
```

### F-string

Позволяет вставить значение:

```python
{tag_name}
```

Если `tag_name == "h1"`, в шаблон подставляется `h1`.

---

## 11. Начало тега

```regex
<{tag_name}\b
```

Для заголовка получится:

```regex
<h1\b
```

`` здесь не используется: запись `\b` в regex означает границу слова.

Она помогает не перепутать:

```html
<h1>
```

с:

```html
<h10>
```

---

## 12. `[^>]*`

```regex
[^>]*
```

Разбор:

- квадратные скобки — набор символов;
- `^` внутри скобок — отрицание;
- `>` — исключённый символ;
- `*` — ноль или больше повторений.

То есть:

> Любые символы, кроме `>`, в любом количестве.

Это позволяет пропустить дополнительные атрибуты:

```html
<h1 id="main" data-test="title" class="product-title">
```

---

## 13. Поиск атрибута `class`

```regex
\bclass\s*=\s*
```

`class` — ищется отдельное слово `class`.

`\s*` — ноль или больше пробельных символов.

Поэтому совпадут:

```html
class="product-title"
```

```html
class = "product-title"
```

```html
class=   "product-title"
```

---

## 14. Одинарные и двойные кавычки

```regex
["\']
```

Совпадает с:

```text
"
```

или:

```text
'
```

Значит, поддерживаются:

```html
class="product-title"
```

и:

```html
class='product-title'
```

---

## 15. Точное имя CSS-класса

```regex
(?<![\w-])product\-title(?![\w-])
```

Левая проверка:

```regex
(?<![\w-])
```

означает, что перед именем не должно быть буквы, цифры, `_` или `-`.

Правая проверка:

```regex
(?![\w-])
```

означает то же для символа после имени.

Так принимается:

```html
class="headline product-title active"
```

но не принимается другой класс:

```html
class="product-title-extra"
```

---

## 16. Именованная группа `content`

```regex
(?P<content>.*?)
```

Это захватывающая группа с именем:

```text
content
```

Для HTML:

```html
<h1 class="product-title"><b>Телевизор</b> Ultra HD</h1>
```

внутри группы будет:

```html
<b>Телевизор</b> Ultra HD
```

Получить группу можно так:

```python
match.group("content")
```

---

## 17. Почему используется `.*?`, а не `.*`

```regex
.*?
```

`.*` — жадный поиск. Он пытается захватить максимально возможный фрагмент.

`.*?` — ленивый поиск. Он берёт минимальный фрагмент до ближайшего подходящего закрывающего тега.

Это уменьшает риск захватить лишний HTML между несколькими элементами.

---

## 18. Закрывающий тег

```regex
</{tag_name}\s*>
```

Для `span` получится:

```regex
</span\s*>
```

Обычно совпадёт:

```html
</span>
```

Также допускается пробел:

```html
</span >
```

---

## 19. Флаги

```python
flags=re.IGNORECASE | re.DOTALL,
```

Символ `|` объединяет флаги.

### `re.IGNORECASE`

Игнорирует регистр:

```html
<h1>
<H1>
```

обрабатываются одинаково.

### `re.DOTALL`

Позволяет точке `.` совпадать с переносом строки.

Это важно для многострочного HTML.

---

## 20. Глобальные шаблоны

```python
TITLE_PATTERN = _make_tag_pattern("h1", "product-title")
CATEGORY_PATTERN = _make_tag_pattern("div", "product-category")
OLD_PRICE_PATTERN = _make_tag_pattern("span", "price-old")
NEW_PRICE_PATTERN = _make_tag_pattern("span", "price-new")
```

Каждая строка создаёт шаблон для конкретного поля.

Имена записаны в `UPPER_CASE`, потому что это глобальные константы.

---

## 21. Шаблон вложенного тега

```python
HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
```

Он находит:

```html
<b>
</b>
<strike>
</strike>
<strong>
</strong>
```

Разбор:

```regex
<
```

начало тега.

```regex
[^>]+
```

один или больше символов, кроме `>`.

```regex
>
```

конец тега.

---

## 22. Шаблон пробелов

```python
WHITESPACE_PATTERN = re.compile(r"\s+")
```

`\s` означает любой пробельный символ:

- пробел;
- перенос строки;
- табуляцию;
- неразрывный пробел после декодирования.

`+` означает один или больше повторений.

---

## 23. Функция `_extract_text`

```python
def _extract_text(html: str, pattern: Pattern[str]) -> str:
```

Она получает:

1. весь HTML;
2. шаблон поля.

Возвращает очищенный текст.

Она нужна, чтобы не повторять четыре раза одинаковые действия.

---

## 24. Поиск

```python
match = pattern.search(html)
```

`.search()` ищет совпадение в любом месте строки.

Это правильнее, чем `.match()`, потому что нужный тег обычно не находится в самом начале HTML-документа.

---

## 25. Обработка отсутствия совпадения

```python
if match is None:
    return ""
```

Если блок не найден, `.search()` возвращает `None`.

Без проверки следующая строка вызвала бы ошибку:

```text
AttributeError: 'NoneType' object has no attribute 'group'
```

По условию блоки гарантированы, но безопасный fallback не мешает API и особенно логичен для пустой старой цены.

---

## 26. Получение внутреннего HTML

```python
inner_html = match.group("content")
```

Для:

```html
<span class="price-old"><strike>55 000 ₽</strike></span>
```

получим:

```html
<strike>55 000 ₽</strike>
```

---

## 27. Удаление вложенных тегов

```python
text_without_tags = HTML_TAG_PATTERN.sub("", inner_html)
```

`.sub()` выполняет замену.

Первый аргумент:

```python
""
```

означает заменить найденные теги пустой строкой.

Было:

```html
<strike>55 000 ₽</strike>
```

Стало:

```text
55 000 ₽
```

---

## 28. Декодирование HTML-сущностей

```python
decoded_text = unescape(text_without_tags)
```

Пример:

```text
TV &amp; Video
```

становится:

```text
TV & Video
```

---

## 29. Очистка пробелов

```python
return WHITESPACE_PATTERN.sub(" ", decoded_text).strip()
```

Сначала все последовательности пробелов заменяются одним пробелом.

Затем `.strip()` удаляет пробелы по краям.

Было:

```text
"\n    Телевизор      Ultra HD   \n"
```

Стало:

```text
"Телевизор Ultra HD"
```

---

## 30. Главная функция

```python
def parse_product_info(html: str) -> dict:
```

Это точная сигнатура задания.

Её нельзя менять, потому что тесты вызывают функцию именно с одним аргументом `html`.

---

## 31. Формирование словаря

```python
product_info = {
    "title": _extract_text(html, TITLE_PATTERN),
    "category": _extract_text(html, CATEGORY_PATTERN),
    "old_price": _extract_text(html, OLD_PRICE_PATTERN),
    "new_price": _extract_text(html, NEW_PRICE_PATTERN),
}
```

Каждый ключ получает результат одной и той же очистки, но с разным шаблоном.

Это уменьшает дублирование.

---

## 32. Возврат результата

```python
return product_info
```

Функция должна вернуть словарь.

Нельзя заменить на:

```python
print(product_info)
```

Проверяющая система делает примерно так:

```python
result = parse_product_info(html)
assert result == expected
```

Если функция только печатает, `result` будет равен `None`.

---

## 33. Путь данных на примере заголовка

HTML:

```html
<h1 class="product-title"><b>Телевизор</b> Ultra HD</h1>
```

### Этап 1

`TITLE_PATTERN.search(html)` находит весь блок.

### Этап 2

`group("content")` возвращает:

```html
<b>Телевизор</b> Ultra HD
```

### Этап 3

`HTML_TAG_PATTERN.sub("", ...)` удаляет `<b>` и `</b>`.

Результат:

```text
Телевизор Ultra HD
```

### Этап 4

`unescape` декодирует сущности, если они есть.

### Этап 5

`WHITESPACE_PATTERN` нормализует пробелы.

---

## 34. Как работает пустая старая цена

HTML:

```html
<span class="price-old"></span>
```

Группа `content` содержит пустую строку:

```python
""
```

Удаление тегов, `unescape` и очистка пробелов сохраняют:

```python
""
```

Поэтому дополнительный специальный `if old_price` не требуется.

---

## 35. Почему цена не переводится в `int`

Задание требует:

```text
"50 000 ₽"
```

Если вернуть:

```python
50000
```

то тип и значение будут отличаться от ожидаемых.

Нужно решать ровно поставленный контракт, а не добавлять следующую стадию обработки.

---

## 36. Почему нет примера запуска в `solution.py`

В файл для проверяющей системы не добавляется:

```python
html = "..."
print(parse_product_info(html))
```

При импорте такой код выполнится автоматически и создаст лишний вывод.

В `solution.py` должны остаться только:

- импорты;
- глобальные шаблоны;
- вспомогательные функции;
- целевая функция.

---

## 37. Временная сложность

Пусть длина HTML равна `n`.

Функция выполняет четыре поиска по строке и очистку найденных частей.

Грубо:

```text
O(4n)
```

Константа отбрасывается:

```text
O(n)
```

Для одной карточки это нормальная сложность.

---

## 38. Почему код проходит требования PEP8

В коде:

- импорты находятся сверху;
- между функциями две пустые строки;
- константы имеют `UPPER_CASE`;
- внутренние функции начинаются с `_`;
- есть docstring;
- есть аннотации типов;
- нет неиспользуемых переменных;
- нет `print`;
- нет сторонних зависимостей;
- имена описывают смысл.

---

## 39. Что загружать

В Karpov Simulator нужно загрузить:

```text
solution.py
```

В комплект также добавлена идентичная копия:

```text
gp_page_2_price_parser_solution.py
```

Она нужна для вашего общего нейминга учебных материалов.

---

## 40. Контрольные вопросы

1. Почему `search`, а не `match`?
2. Что находится в группе `content`?
3. Что делает `re.DOTALL`?
4. Что удаляет `HTML_TAG_PATTERN`?
5. Почему пустая старая цена превращается в `""`?
6. Зачем используется `unescape`?
7. Что означает `\s+`?
8. Почему шаблоны глобальные?
9. Почему цены остаются строками?
10. Почему нужен `return`, а не `print`?

Если вы можете объяснить каждый пункт своими словами, значит вы понимаете решение, а не просто копируете код.

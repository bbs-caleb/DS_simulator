# Страница 3. JaccardEval: пошаговое объяснение с абсолютного нуля

## 1. Общая схема программы

Программа выполняет следующую цепочку:

```text
путь к data.json
        ↓
чтение JSON
        ↓
валидация документов
        ↓
список пар (text, ocr_text)
        ↓
расчёт Jaccard distance для каждой пары
        ↓
создание кортежей (score, text, ocr_text)
        ↓
стабильная сортировка по score
        ↓
возврат первых limit результатов
```

Важно разделить два уровня:

- `BaseEval` управляет всем процессом;
- `JaccardEval` знает только, как сравнить две конкретные строки.

---

# 2. Что такое класс

Класс — это описание будущих объектов.

```python
class BaseEval:
    ...
```

Можно представить класс как чертёж. Объект — экземпляр, созданный по чертежу:

```python
evaluation = BaseEval("data.json")
```

Переменная `evaluation` хранит объект класса `BaseEval`.

---

# 3. Что такое self

Методы класса получают первым параметром `self`:

```python
def load_documents(self, path):
```

`self` — текущий объект.

Когда выполняется:

```python
evaluation.load_documents("data.json")
```

Python автоматически передаёт объект `evaluation` в `self`.

Через `self` объект хранит свои данные:

```python
self.documents
```

---

# 4. Что происходит при создании JaccardEval

```python
evaluation = JaccardEval("data.json")
```

У `JaccardEval` нет собственного `__init__`, но он наследуется от `BaseEval`:

```python
class JaccardEval(BaseEval):
```

Поэтому используется:

```python
def __init__(self, documents_path: str):
    self.documents = self.load_documents(documents_path)

    if not self.documents:
        raise ValueError("The documents list is empty.")
```

Первая строка загружает документы и сохраняет их внутри объекта.

Если список пустой, выбрасывается `ValueError`.

---

# 5. Проверка существования файла

```python
if not os.path.isfile(path):
    raise FileNotFoundError(...)
```

`os.path.isfile(path)` возвращает:

- `True`, если файл существует;
- `False`, если файл не найден или путь не ведёт к обычному файлу.

Оператор `not` инвертирует значение.

Если файла нет, программа сразу сообщает об этом через `FileNotFoundError`.

---

# 6. Чтение JSON

```python
with open(path, "r", encoding="utf-8") as file:
    documents = json.load(file)
```

Разбор параметров:

- `path` — путь;
- `"r"` — режим чтения;
- `encoding="utf-8"` — кодировка, корректно поддерживающая русский текст;
- `with` — конструкция, которая автоматически закроет файл.

`json.load(file)` превращает JSON в Python-объекты.

JSON:

```json
[
  {
    "text": "hello",
    "ocr_text": "hel1o"
  }
]
```

станет:

```python
[
    {
        "text": "hello",
        "ocr_text": "hel1o"
    }
]
```

---

# 7. Обработка неправильного JSON

```python
except json.JSONDecodeError as error:
    raise ValueError(...) from error
```

Если в файле нарушен JSON-синтаксис, `json.load` выбрасывает `JSONDecodeError`.

Программа превращает его в `ValueError`, сохраняя исходную причину через `from error`.

---

# 8. Проверка, что корень JSON — список

```python
if not isinstance(documents, list):
    raise ValueError(...)
```

Подходит:

```json
[
  {"text": "a", "ocr_text": "b"},
  {"text": "c", "ocr_text": "d"}
]
```

Не подходит:

```json
{"text": "a", "ocr_text": "b"}
```

Во втором случае корень — словарь, а задача ожидает список документов.

---

# 9. Проверка каждого документа

```python
return [self.validate_document(document) for document in documents]
```

Это list comprehension.

Его длинный эквивалент:

```python
result = []

for document in documents:
    validated = self.validate_document(document)
    result.append(validated)

return result
```

Для каждого документа вызывается `validate_document`.

---

# 10. validate_document

## 10.1. Проверка словаря

```python
if not isinstance(doc, dict):
    raise ValueError(...)
```

Ожидается структура:

```python
{
    "text": "...",
    "ocr_text": "..."
}
```

## 10.2. Проверка поля text

```python
if "text" not in doc:
    raise ValueError(...)
```

`in` проверяет наличие ключа.

## 10.3. Проверка поля ocr_text

```python
if "ocr_text" not in doc:
    raise ValueError(...)
```

## 10.4. Возврат кортежа

```python
return doc["text"], doc["ocr_text"]
```

Python создаёт:

```python
(text, ocr_text)
```

Именно такие пары сохраняются в `self.documents`.

---

# 11. Что такое наследование

```python
class JaccardEval(BaseEval):
```

Это означает:

> JaccardEval является специализированным вариантом BaseEval.

Он получает методы базового класса, но может заменить отдельные методы своей реализацией.

На этой странице заменяется `_eval_func`.

---

# 12. Что означает переопределение метода

В `BaseEval` существует:

```python
def _eval_func(self, text, ocr_text):
```

В `JaccardEval` создаётся метод с тем же именем:

```python
def _eval_func(self, text, ocr_text):
```

Для объекта `JaccardEval` будет использоваться дочерняя версия.

Пример:

```python
base = BaseEval("data.json")
jaccard = JaccardEval("data.json")
```

```python
base._eval_func(...)
```

использует посимвольный алгоритм.

```python
jaccard._eval_func(...)
```

использует Jaccard distance.

---

# 13. Первая строка Jaccard-метода

```python
text_words = set(text.split(" "))
```

Разберём изнутри наружу.

## 13.1. split

```python
"apple orange".split(" ")
```

Результат:

```python
["apple", "orange"]
```

В качестве разделителя передан конкретный пробел.

## 13.2. set

```python
set(["apple", "orange"])
```

Результат:

```python
{"apple", "orange"}
```

Если слово повторяется:

```python
set(["home", "work", "home"])
```

получается:

```python
{"home", "work"}
```

Повторение удаляется.

---

# 14. Вторая строка

```python
ocr_words = set(ocr_text.split(" "))
```

То же действие выполняется для OCR-текста.

Теперь есть два множества:

```python
text_words
ocr_words
```

---

# 15. Пересечение

```python
intersection = text_words.intersection(ocr_words)
```

Пересечение содержит только общие элементы.

Пример:

```python
text_words = {"apple", "orange"}
ocr_words = {"apple", "banana"}
```

Тогда:

```python
intersection == {"apple"}
```

Количество общих слов:

```python
len(intersection) == 1
```

---

# 16. Объединение

```python
union = text_words.union(ocr_words)
```

Объединение содержит все уникальные элементы:

```python
{"apple", "orange", "banana"}
```

Количество:

```python
len(union) == 3
```

---

# 17. Расчёт сходства

```python
jaccard_similarity = len(intersection) / len(union)
```

Подстановка:

```python
1 / 3
```

Результат:

```python
0.3333333333333333
```

Это мера сходства.

---

# 18. Превращение сходства в ошибку

```python
return 1 - jaccard_similarity
```

Для примера:

```python
1 - 0.3333333333333333
```

Результат:

```python
0.6666666666666667
```

Теперь идеальное совпадение даёт `0`, а отсутствие общих слов — `1`.

Это соответствует сортировке: самые большие ошибки должны быть первыми.

---

# 19. Как работает evaluate

```python
results = [
    (self._eval_func(text, ocr_text), text, ocr_text)
    for text, ocr_text in self.documents
]
```

Для каждой пары создаётся кортеж:

```python
(score, text, ocr_text)
```

Ключевой момент:

```python
self._eval_func(...)
```

`self` является объектом `JaccardEval`, поэтому Python вызывает Jaccard-метод.

Это называется полиморфизмом.

---

# 20. Как работает сортировка

```python
results.sort(key=lambda result: result[0], reverse=True)
```

Каждый элемент:

```python
(score, text, ocr_text)
```

Индексы:

```text
result[0] → score
result[1] → text
result[2] → ocr_text
```

`lambda result: result[0]` означает:

> Для сортировки используй только score.

`reverse=True` означает сортировку по убыванию.

---

# 21. Стабильная сортировка

Пусть до сортировки:

```python
[
    (1.0, "Документ A", "..."),
    (0.5, "Документ B", "..."),
    (1.0, "Документ C", "...")
]
```

После сортировки:

```python
[
    (1.0, "Документ A", "..."),
    (1.0, "Документ C", "..."),
    (0.5, "Документ B", "...")
]
```

`A` остаётся раньше `C`, потому что Python-сортировка стабильна.

Текстовые элементы кортежа не участвуют в сортировке, потому что ключ — только `result[0]`.

---

# 22. Как работает limit

```python
if limit is None:
    return results

return results[:limit]
```

## limit=None

Возвращаются все документы.

## limit=3

```python
results[:3]
```

возвращает первые три элемента.

## limit=0

Возвращается пустой список.

---

# 23. Почему нельзя округлять внутри метода

Неправильно:

```python
return round(1 - jaccard_similarity, 2)
```

Проблемы:

1. скрытые тесты могут сравнивать точные значения;
2. разные score могут стать одинаковыми;
3. сортировка может измениться;
4. информация теряется.

Правильно:

```python
return 1 - jaccard_similarity
```

Округление только при печати:

```python
print(f"score: {score:.2f}")
```

---

# 24. Разбор home work

```python
score = evaluation._eval_func("home work", "work home")
```

После `split`:

```python
["home", "work"]
["work", "home"]
```

После `set`:

```python
{"home", "work"}
{"work", "home"}
```

Порядка у множества нет, поэтому множества равны.

```text
intersection size = 2
union size = 2
similarity = 1
score = 0
```

---

# 25. Разбор повторения слова

```python
score = evaluation._eval_func(
    "home work home",
    "work home",
)
```

После разбиения:

```python
["home", "work", "home"]
["work", "home"]
```

После `set`:

```python
{"home", "work"}
{"work", "home"}
```

Частота потеряна, поэтому score равен `0`.

---

# 26. Сложность

Пусть в текстах `n` и `m` слов.

Создание множеств в среднем занимает:

\[
O(n + m)
\]

Пересечение и объединение также близки к линейному времени.

Для одного документа итоговая сложность примерно:

\[
O(n + m)
\]

Дополнительная память нужна для двух множеств, пересечения и объединения.

---

# 27. Типичные ошибки

## Ошибка 1. Возвращать similarity

Неправильно:

```python
return len(intersection) / len(union)
```

Тогда лучшие документы получат максимальный score и окажутся наверху.

## Ошибка 2. Перепутать дробь

Неправильно:

```python
len(union) / len(intersection)
```

Результат может быть больше единицы, а при пустом пересечении будет деление на ноль.

## Ошибка 3. Не использовать set

Неправильно:

```python
text_words = text.split(" ")
```

Это список, а задача требует множества.

## Ошибка 4. Использовать split без аргумента

```python
text.split()
```

В обычной работе это может быть полезно, но условие явно говорит использовать пробел как разделитель. Для автотеста безопаснее точная реализация:

```python
text.split(" ")
```

## Ошибка 5. Не наследоваться

Неправильно:

```python
class JaccardEval:
```

Правильно:

```python
class JaccardEval(BaseEval):
```

## Ошибка 6. Удалить BaseEval

В решении должны находиться обе реализации.

## Ошибка 7. Переписать evaluate

Не требуется. Унаследованный метод уже вызывает переопределённый `_eval_func`.

## Ошибка 8. Добавить lower или очистку пунктуации

Это изменит метрику и потенциально сломает скрытые тесты.

---

# 28. Как проверить вручную

```python
evaluation = JaccardEval("data.json")
result = evaluation.evaluate(limit=3)

for score, text, ocr_text in result:
    print(f"score: {score:.2f}")
    print(f"source text: {text}")
    print(f"parsed text: {ocr_text}")
    print()
```

Ожидаемые первые score:

```text
1.00
1.00
0.93
```

---

# 29. Финальная модель понимания

`BaseEval` отвечает за общий pipeline:

```text
файл → загрузка → проверка → вычисление → сортировка → limit
```

`JaccardEval` отвечает только за формулу:

```text
строки
→ split(" ")
→ set
→ intersection
→ union
→ similarity
→ 1 - similarity
```

Именно такое разделение делает решение коротким, расширяемым и соответствующим API.

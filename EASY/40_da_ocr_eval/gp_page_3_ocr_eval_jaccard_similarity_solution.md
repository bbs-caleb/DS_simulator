# Страница 3. Решение задачи Jaccard Similarity

## 1. Что требует задание

Нужно подготовить один Python-файл, содержащий две реализации:

```python
BaseEval
JaccardEval
```

При этом `JaccardEval` должен:

1. наследоваться от `BaseEval`;
2. переопределять `_eval_func`;
3. делить оба текста на слова через пробел;
4. преобразовывать слова в множества;
5. рассчитывать коэффициент Жаккара;
6. возвращать `1 - Jaccard Similarity`.

Загрузка JSON, валидация документов, сортировка и `limit` остаются в `BaseEval`.

---

# 2. Файл для отправки

```text
gp_page_3_ocr_eval_jaccard_similarity_solution.py
```

В Karpov Simulator загружается именно этот `.py`-файл. Markdown-файлы нужны для обучения и не отправляются вместо решения.

---

# 3. Полный код

```python
"""Evaluate OCR output using direct comparison and Jaccard distance."""

import json
import os
from typing import List, Tuple


class BaseEval:
    """Evaluate differences between original texts and OCR texts."""

    def __init__(self, documents_path: str):
        """Load and store documents from a JSON file."""
        self.documents = self.load_documents(documents_path)

        if not self.documents:
            raise ValueError("The documents list is empty.")

    def load_documents(self, path: str) -> List[Tuple[str, str]]:
        """
        Load documents from a JSON file.

        Args:
            path: Path to the JSON file.

        Returns:
            A list of tuples in the form ``(text, ocr_text)``.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            ValueError: If the file contains invalid JSON or its root value
                is not a list.
        """
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File does not exist: {path}")

        try:
            with open(path, "r", encoding="utf-8") as file:
                documents = json.load(file)
        except json.JSONDecodeError as error:
            raise ValueError(
                "The file does not contain valid JSON."
            ) from error

        if not isinstance(documents, list):
            raise ValueError("The JSON file must contain a list of documents.")

        return [self.validate_document(document) for document in documents]

    def validate_document(self, doc: dict) -> Tuple[str, str]:
        """
        Validate one document and return its original and OCR texts.

        Args:
            doc: Document loaded from the JSON file.

        Returns:
            A tuple in the form ``(text, ocr_text)``.

        Raises:
            ValueError: If the document is not a dictionary or does not
                contain one of the required fields.
        """
        if not isinstance(doc, dict):
            raise ValueError("Each document must be a dictionary.")

        if "text" not in doc:
            raise ValueError("The document does not contain the 'text' field.")

        if "ocr_text" not in doc:
            raise ValueError(
                "The document does not contain the 'ocr_text' field."
            )

        return doc["text"], doc["ocr_text"]

    def _eval_func(self, text: str, ocr_text: str) -> float:
        """
        Count character differences at matching positions.

        Characters are compared pairwise. The absolute difference between
        string lengths is added to count unmatched trailing characters.

        Args:
            text: Original text.
            ocr_text: Text returned by OCR.

        Returns:
            The number of differing characters.
        """
        different_characters = sum(
            source_char != ocr_char
            for source_char, ocr_char in zip(text, ocr_text)
        )
        length_difference = abs(len(text) - len(ocr_text))

        return different_characters + length_difference

    def evaluate(self, limit: int = None) -> List[Tuple[float, str, str]]:
        """
        Evaluate all documents and sort them by score in descending order.

        Args:
            limit: Maximum number of results to return. If it is ``None``,
                all results are returned.

        Returns:
            Stable score-sorted tuples in the form
            ``(score, text, ocr_text)``.
        """
        results = [
            (self._eval_func(text, ocr_text), text, ocr_text)
            for text, ocr_text in self.documents
        ]
        results.sort(key=lambda result: result[0], reverse=True)

        if limit is None:
            return results

        return results[:limit]


class JaccardEval(BaseEval):
    """Evaluate OCR errors using word-level Jaccard distance."""

    def _eval_func(self, text: str, ocr_text: str) -> float:
        """
        Calculate one minus the Jaccard similarity of two word sets.

        Words are obtained by splitting each text using a space as the
        separator.

        Args:
            text: Original text.
            ocr_text: Text returned by OCR.

        Returns:
            Jaccard distance in the range from 0 to 1.
        """
        text_words = set(text.split(" "))
        ocr_words = set(ocr_text.split(" "))

        intersection = text_words.intersection(ocr_words)
        union = text_words.union(ocr_words)
        jaccard_similarity = len(intersection) / len(union)

        return 1 - jaccard_similarity
```

---

# 4. Почему решение соответствует каждому требованию

## 4.1. Наследование

```python
class JaccardEval(BaseEval):
```

Это точное выполнение требования «написать класс `JaccardEval`, унаследованный от `BaseEval`».

Дочерний класс получает готовые методы:

- `__init__`;
- `load_documents`;
- `validate_document`;
- `evaluate`.

## 4.2. Переопределение внутреннего метода

В `JaccardEval` объявлен метод с тем же именем:

```python
def _eval_func(self, text: str, ocr_text: str) -> float:
```

Когда у объекта `JaccardEval` вызывается унаследованный `evaluate`, внутри будет использована новая Jaccard-реализация.

## 4.3. Разбиение по пробелу

```python
text.split(" ")
ocr_text.split(" ")
```

Передан конкретный разделитель — один пробел. Это соответствует формулировке задания.

## 4.4. Множества слов

```python
text_words = set(...)
ocr_words = set(...)
```

Повторяющиеся слова удаляются, потому что множество хранит только уникальные значения.

## 4.5. Пересечение

```python
intersection = text_words.intersection(ocr_words)
```

В `intersection` остаются слова, присутствующие в обоих текстах.

## 4.6. Объединение

```python
union = text_words.union(ocr_words)
```

В `union` входят все уникальные слова двух текстов.

## 4.7. Коэффициент Жаккара

```python
jaccard_similarity = len(intersection) / len(union)
```

Это формула:

\[
J(A,B) = \frac{|A \cap B|}{|A \cup B|}
\]

## 4.8. Мера различия

```python
return 1 - jaccard_similarity
```

Чем меньше сходство, тем больше ошибка.

## 4.9. Стабильная сортировка

В базовом классе:

```python
results.sort(key=lambda result: result[0], reverse=True)
```

Сортировка выполняется только по первому элементу кортежа — `score`.

`list.sort` в Python стабилен. Если два результата имеют одинаковый `score`, их исходный порядок сохраняется.

---

# 5. Проверка на простых примерах

## 5.1. Одинаковые тексты

```python
score = evaluation._eval_func(
    "apple orange",
    "apple orange",
)
```

Множества:

```text
{apple, orange}
{apple, orange}
```

Пересечение — 2 слова, объединение — 2 слова:

\[
1 - \frac{2}{2} = 0
\]

Результат:

```python
0.0
```

## 5.2. Одно общее слово

```python
score = evaluation._eval_func(
    "apple orange",
    "apple banana",
)
```

Пересечение:

```text
{apple}
```

Объединение:

```text
{apple, orange, banana}
```

\[
1 - \frac{1}{3} \approx 0.6667
\]

## 5.3. Полностью разные слова

```python
score = evaluation._eval_func(
    "apple orange",
    "pear banana",
)
```

Пересечение пустое:

\[
1 - \frac{0}{4} = 1
\]

Результат:

```python
1.0
```

## 5.4. Переставленные слова

```python
score = evaluation._eval_func(
    "home work",
    "work home",
)
```

Оба множества равны:

```text
{home, work}
```

Поэтому:

```python
score == 0
```

Это ожидаемое свойство множеств, а не ошибка реализации.

## 5.5. Повторение слова

```python
score = evaluation._eval_func(
    "home work home",
    "work home",
)
```

После `set` повторение исчезает, поэтому score снова равен `0`.

---

# 6. Проверка на data.json

Код проверки:

```python
evaluation = JaccardEval("data.json")
result = evaluation.evaluate(limit=3)

for score, text, ocr_text in result:
    print(f"score: {score:.2f}")
    print(f"source text: {text}")
    print(f"parsed text: {ocr_text}")
    print()
```

Первые три значения:

```text
1.00
1.00
0.93
```

Порядок совпадает с условием:

1. «Сравните климатические условия пустыни и тропического леса.»
2. «Рассчитайте массу молекулы воды.»
3. «Рассчитайте среднюю скорость, если известно расстояние и время.»

---

# 7. Почему результат не округляется внутри _eval_func

Нельзя писать:

```python
return round(1 - jaccard_similarity, 2)
```

Причины:

- скрытые тесты могут ожидать точный `float`;
- округление может сделать разные значения одинаковыми;
- изменится порядок сортировки;
- будет потеряна информация.

Правильно возвращать полное значение:

```python
return 1 - jaccard_similarity
```

Округление используется только при отображении:

```python
print(f"score: {score:.2f}")
```

---

# 8. Что не нужно добавлять

Перед загрузкой не следует:

- менять имена классов;
- удалять `BaseEval`;
- менять сигнатуры методов;
- применять `.lower()`;
- удалять пунктуацию;
- использовать `.split()` без аргумента;
- заменять множества списками;
- округлять score;
- возвращать similarity вместо distance;
- переписывать `evaluate` в дочернем классе;
- подключать сторонние библиотеки.

Каждое такое изменение либо не требуется, либо меняет контракт и рискованно для скрытых тестов.

---

# 9. Почему код минимальный

В `JaccardEval` находится только новая логика:

```python
class JaccardEval(BaseEval):
    def _eval_func(...):
        ...
```

Всё остальное повторно используется из `BaseEval`.

Это уменьшает:

- дублирование;
- риск ошибок;
- количество строк;
- сложность сопровождения.

---

# 10. Итог

Для отправки используется:

```text
gp_page_3_ocr_eval_jaccard_similarity_solution.py
```

В нём присутствуют оба класса и точная реализация `1 - Jaccard Similarity` по множествам слов.

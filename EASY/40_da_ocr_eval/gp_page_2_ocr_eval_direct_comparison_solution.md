# Решение задания: класс `BaseEval`

## Что сдавать в проверяющую систему

В качестве решения требуется один Python-файл с реализацией класса `BaseEval`.

Готовый файл:

```text
gp_page_2_ocr_eval_direct_comparison_solution.py
```

В нём сохранены:

- имя класса `BaseEval`;
- сигнатуры всех требуемых методов;
- порядок элементов возвращаемых кортежей;
- стабильная сортировка только по первому элементу;
- обработка отсутствующего файла;
- обработка некорректного JSON;
- проверка структуры документов;
- проверка пустого списка документов.

---

## Полный код решения

```python
"""Evaluate OCR output using direct character-by-character comparison."""

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
            raise ValueError("The file does not contain valid JSON.") from error

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
```

---

## Почему решение соответствует условию

### Реализована загрузка JSON

Используются:

```python
with open(path, "r", encoding="utf-8") as file:
    documents = json.load(file)
```

Кодировка UTF-8 обязательна для корректной работы с русскими символами.

### Реализована валидация

Для каждого документа проверяется:

```python
isinstance(doc, dict)
```

а также наличие ключей:

```python
"text"
"ocr_text"
```

### Реализовано прямое сравнение

Совпадающие позиции сравниваются через `zip`. Разница длин добавляется отдельно.

### Реализована требуемая сортировка

```python
results.sort(key=lambda result: result[0], reverse=True)
```

Сортировка использует только первый элемент — score.

### Стабильность не нарушена

Python-сортировка стабильна. Если у двух записей одинаковый score, их исходный относительный порядок сохраняется.

### `limit` применяется после сортировки

Сначала формируется полный отсортированный результат, затем берётся срез:

```python
results[:limit]
```

Это возвращает именно документы с максимальными ошибками.

---

## Проверенный результат на предоставленном наборе данных

Первые три score:

```text
67
57
52
```

Они полностью совпадают с ожидаемым выводом задания.

---

## Почему не добавлены лишние проверки

В условии требуется проверить наличие полей, но не сказано дополнительно проверять тип значений `text` и `ocr_text`.

Добавление неоговорённых ограничений иногда ломает скрытые тесты. Поэтому решение следует контракту задания и не меняет API без необходимости.

---

## Как запустить локально

Положите рядом:

```text
gp_page_2_ocr_eval_direct_comparison_solution.py
data.json
```

Создайте временный файл проверки или выполните в Python:

```python
from gp_page_2_ocr_eval_direct_comparison_solution import BaseEval

ocr_eval = BaseEval("data.json")
result = ocr_eval.evaluate(limit=3)

for score, text, ocr_text in result:
    print(f"score: {score}")
    print(f"source text: {text}")
    print(f"parsed text: {ocr_text}")
    print()
```

---

## Что не нужно загружать в проверяющую систему

Обычно платформа ожидает только Python-файл решения. Не требуется загружать:

- `data.json`, если он уже есть у проверяющей системы;
- Markdown-файлы;
- ZIP-архив;
- отдельный тестовый скрипт.

Markdown-файлы предназначены для обучения и понимания решения.

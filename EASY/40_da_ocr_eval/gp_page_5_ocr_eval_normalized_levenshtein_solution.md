# Страница 5. Решение задачи Normalized Levenshtein Distance

## 1. Что требуется реализовать

Проверяющая система ожидает один Python-файл с двумя классами:

```python
BaseEval
NormLevEval
```

`NormLevEval` должен:

1. наследоваться от `BaseEval`;
2. принимать стоимости вставки, удаления и замены;
3. проверять, что каждая стоимость лежит в диапазоне `[0, 2]`;
4. считать взвешенное расстояние Левенштейна;
5. нормализовать расстояние;
6. учитывать максимальную длину пары строк;
7. учитывать максимальную стоимость операции;
8. возвращать score от `0` до `1`;
9. сохранять исходный API `BaseEval`.

---

## 2. Файл для отправки

```text
gp_page_5_ocr_eval_normalized_levenshtein_solution.py
```

---

## 3. Полный код

```python
"""Evaluate OCR output using normalized weighted Levenshtein distance."""

import json
import os
from typing import List, Tuple


class BaseEval:
    """Evaluate differences between original texts and OCR texts."""

    def __init__(self, documents_path: str):
        """Load documents from a JSON file."""
        self.documents = self.load_documents(documents_path)

        if not self.documents:
            raise ValueError("The documents list is empty.")

    def load_documents(self, path: str) -> List[Tuple[str, str]]:
        """
        Load and validate documents from a JSON file.

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
            message = "The file does not contain valid JSON."
            raise ValueError(message) from error

        if not isinstance(documents, list):
            message = "The JSON file must contain a list of documents."
            raise ValueError(message)

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
            message = "The document does not contain the 'text' field."
            raise ValueError(message)

        if "ocr_text" not in doc:
            message = "The document does not contain the 'ocr_text' field."
            raise ValueError(message)

        return doc["text"], doc["ocr_text"]

    def _eval_func(self, text: str, ocr_text: str) -> float:
        """
        Count character differences at matching positions.

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


class NormLevEval(BaseEval):
    """Evaluate OCR errors using normalized weighted Levenshtein distance."""

    def __init__(
        self,
        documents_path: str,
        insert_cost: float = 1,
        delete_cost: float = 1,
        substitute_cost: float = 1,
    ):
        """
        Initialize the evaluator and validate operation costs.

        Args:
            documents_path: Path to the JSON file with documents.
            insert_cost: Cost of an insertion.
            delete_cost: Cost of a deletion.
            substitute_cost: Cost of a substitution.

        Raises:
            ValueError: If any operation cost is outside the range [0, 2].
        """
        costs = (insert_cost, delete_cost, substitute_cost)

        if not all(0 <= cost <= 2 for cost in costs):
            raise ValueError("Operation costs must be in the range [0, 2].")

        self.insert_cost = insert_cost
        self.delete_cost = delete_cost
        self.substitute_cost = substitute_cost

        super().__init__(documents_path)

    def _eval_func(self, text: str, ocr_text: str) -> float:
        """
        Calculate normalized weighted Levenshtein distance.

        Args:
            text: Reference text.
            ocr_text: OCR output text.

        Returns:
            A normalized distance in the range from 0 to 1.
        """
        rows_count = len(text) + 1
        columns_count = len(ocr_text) + 1

        distances = [
            [0.0] * columns_count
            for _ in range(rows_count)
        ]

        for row in range(rows_count):
            distances[row][0] = row * self.delete_cost

        for column in range(columns_count):
            distances[0][column] = column * self.insert_cost

        for row in range(1, rows_count):
            for column in range(1, columns_count):
                insertion_cost = (
                    distances[row][column - 1]
                    + self.insert_cost
                )
                deletion_cost = (
                    distances[row - 1][column]
                    + self.delete_cost
                )

                characters_are_different = (
                    text[row - 1] != ocr_text[column - 1]
                )
                replacement_cost = (
                    distances[row - 1][column - 1]
                    + characters_are_different * self.substitute_cost
                )

                distances[row][column] = min(
                    insertion_cost,
                    deletion_cost,
                    replacement_cost,
                )

        max_text_length = max(len(text), len(ocr_text))
        max_operation_cost = max(
            self.insert_cost,
            self.delete_cost,
            self.substitute_cost,
        )
        max_possible_distance = (
            max_text_length * max_operation_cost
        )

        if max_possible_distance == 0:
            return 0.0

        return distances[-1][-1] / max_possible_distance
```

---

## 4. Почему решение соответствует каждому требованию

### Наследование

```python
class NormLevEval(BaseEval):
```

### Параметры конструктора

```python
insert_cost
delete_cost
substitute_cost
```

в точности присутствуют в сигнатуре.

### Проверка диапазона

```python
if not all(0 <= cost <= 2 for cost in costs):
    raise ValueError(...)
```

Границы `0` и `2` разрешены.

### Взвешенные базовые значения

```python
distances[row][0] = row * self.delete_cost
```

```python
distances[0][column] = column * self.insert_cost
```

### Взвешенные переходы

```python
+ self.insert_cost
+ self.delete_cost
+ self.substitute_cost
```

### Нормализация по максимальной длине

```python
max(len(text), len(ocr_text))
```

### Учёт максимальной стоимости

```python
max(
    self.insert_cost,
    self.delete_cost,
    self.substitute_cost,
)
```

### Защита от деления на ноль

```python
if max_possible_distance == 0:
    return 0.0
```

### Стабильная сортировка

Она уже реализована в `BaseEval`:

```python
results.sort(key=lambda result: result[0], reverse=True)
```

---

## 5. Формула нормализации

```python
normalized_distance = (
    weighted_distance
    / (
        max(len(text), len(ocr_text))
        * max(insert_cost, delete_cost, substitute_cost)
    )
)
```

Эта формула соответствует docstring из задания.

---

## 6. Проверка диапазона стоимостей

Корректно:

```python
NormLevEval(
    "data.json",
    insert_cost=0,
    delete_cost=2,
    substitute_cost=1.2,
)
```

Некорректно:

```python
NormLevEval("data.json", insert_cost=-0.1)
```

Некорректно:

```python
NormLevEval("data.json", delete_cost=2.1)
```

В обоих случаях должен возникнуть `ValueError`.

---

## 7. Проверка на простых строках

### Полное совпадение

```python
_eval_func("abc", "abc")
```

Взвешенное расстояние:

```text
0
```

Нормализованное расстояние:

```text
0.0
```

### Пустая строка в непустую

При стандартных весах:

```python
_eval_func("", "abc")
```

Нужно три вставки:

```text
3
```

Знаменатель:

```text
3 × 1 = 3
```

Результат:

```text
1.0
```

### Одна замена

```python
_eval_func("cat", "cut")
```

При `substitute_cost=1.2`:

```text
distance = 1.2
```

Знаменатель:

```text
3 × 1.2 = 3.6
```

Результат:

```text
1.2 / 3.6 = 0.333...
```

---

## 8. Проверка на `data.json`

При:

```python
evaluation = NormLevEval(
    "data.json",
    substitute_cost=1.2,
)
```

первые четыре score:

```text
0.1525...
0.125
0.125
0.12
```

При форматировании:

```python
print(f"score: {score:.2f}")
```

получается:

```text
0.15
0.12
0.12
0.12
```

Порядок документов совпадает с условием.

---

## 9. Почему `0.125` печатается как `0.12`

Python использует округление при форматировании числа с плавающей точкой.

```python
f"{0.125:.2f}"
```

может вывести:

```text
0.12
```

Это связано с двоичным представлением чисел и правилом округления до ближайшего
чётного в пограничных случаях.

Внутри метода округлять score нельзя. Проверяющая система должна получать
полную точность.

---

## 10. Почему нельзя делить только на длину

Неправильно:

```python
distance / max(len(text), len(ocr_text))
```

Если `substitute_cost=2`, итоговая величина может иметь другой масштаб.

Правильно учитывать максимальный вес:

```python
distance / (
    max_length * max_operation_cost
)
```

---

## 11. Почему нельзя использовать сумму стоимостей

Неправильный знаменатель:

```python
max_length * (
    insert_cost + delete_cost + substitute_cost
)
```

Одна позиция не обязана одновременно требовать все три операции.

В условии прямо указана максимальная стоимость среди операций.

---

## 12. Почему нельзя нормализовать до расчёта матрицы

Нормализация применяется к итоговому минимальному пути.

Нельзя делить каждую отдельную операцию на длину заранее без необходимости:
это усложняет код и может создать различия из-за численной арифметики.

Правильный порядок:

```text
сначала weighted Levenshtein distance
потом единая нормализация
```

---

## 13. Типичные ошибки

### Не вызвать `super().__init__`

Тогда документы не будут загружены.

### Вызвать `super().__init__` до сохранения весов

В текущей архитектуре загрузка не вызывает `_eval_func`, поэтому это не
сломает работу, но логичнее сначала валидировать и сохранить параметры.

### Первый столбец умножить на insert_cost

Неправильно. Первый столбец означает удаления.

### Первую строку умножить на delete_cost

Неправильно. Первая строка означает вставки.

### Всегда добавлять substitute_cost

При совпадающих символах стоимость замены должна быть нулевой.

### Не обработать нулевой знаменатель

Это приведёт к `ZeroDivisionError`.

### Округлить внутри `_eval_func`

Это может изменить сортировку и скрытые проверки.

### Использовать `min(len(text), len(ocr_text))`

Это нарушает условие и может дать score больше единицы.

---

## 14. Что загружать

Только Python-файл:

```text
gp_page_5_ocr_eval_normalized_levenshtein_solution.py
```

`README.md` для этой страницы не требуется.

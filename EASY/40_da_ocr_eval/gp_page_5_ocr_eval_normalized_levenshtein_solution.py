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

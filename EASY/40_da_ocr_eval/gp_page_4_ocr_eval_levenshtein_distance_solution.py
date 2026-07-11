"""Evaluate OCR output using character comparison and Levenshtein distance."""

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


class LevenshteinEval(BaseEval):
    """Evaluate OCR errors using Levenshtein distance."""

    def _eval_func(self, text: str, ocr_text: str) -> float:
        """
        Calculate the Levenshtein distance between two strings.

        Args:
            text: Original text.
            ocr_text: Text returned by OCR.

        Returns:
            The minimum number of insertions, deletions, and substitutions
            required to transform ``text`` into ``ocr_text``.
        """
        rows_count = len(text) + 1
        columns_count = len(ocr_text) + 1

        distances = [
            [0] * columns_count
            for _ in range(rows_count)
        ]

        for row in range(rows_count):
            distances[row][0] = row

        for column in range(columns_count):
            distances[0][column] = column

        for row in range(1, rows_count):
            for column in range(1, columns_count):
                insertion_cost = distances[row][column - 1] + 1
                deletion_cost = distances[row - 1][column] + 1
                replacement_cost = (
                    distances[row - 1][column - 1]
                    + (text[row - 1] != ocr_text[column - 1])
                )

                distances[row][column] = min(
                    insertion_cost,
                    deletion_cost,
                    replacement_cost,
                )

        return distances[-1][-1]

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

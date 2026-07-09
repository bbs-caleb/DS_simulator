"""Batch data loader with tokenization for sentiment analysis."""

from dataclasses import dataclass
from itertools import islice
from typing import Generator, Iterator, List, TextIO, Tuple

from transformers import PreTrainedTokenizer

LABELS = {"negative": -1, "neutral": 0, "positive": 1}


def iter_records(file: TextIO) -> Iterator[str]:
    """Yield logical csv records, merging multiline quoted fields"""
    record = ""
    for line in file:
        record += line
        if record.count('"') % 2 == 0:  # record complete when quotes balanced
            yield record.rstrip("\n")
            record = ""


@dataclass
class DataLoader:
    """Load and tokenize reviews from a csv file batch by batch."""

    path: str
    tokenizer: PreTrainedTokenizer
    batch_size: int = 512
    max_length: int = 128

    def __iter__(self) -> Generator[List[List[int]], None, None]:
        """Iterate over batches"""
        for i in range(len(self)):
            yield self.batch_tokenized(i)

    def __len__(self) -> int:
        """Number of batches"""
        with open(self.path, encoding="utf-8") as file:
            next(file)  # skip header
            rows = sum(1 for _ in iter_records(file))
        return (rows + self.batch_size - 1) // self.batch_size  # ceil division

    def tokenize(self, batch: List[str]) -> List[List[int]]:
        """Tokenize list of texts"""
        return [
            self.tokenizer.encode(
                text,
                add_special_tokens=True,
                max_length=self.max_length,
                truncation=True,
            )
            for text in batch
        ]

    def batch_loaded(self, i: int) -> Tuple[List[str], List[int]]:
        """Return loaded i-th batch of data (text, label)"""
        start = i * self.batch_size
        with open(self.path, encoding="utf-8") as file:
            next(file)  # skip header
            records = islice(iter_records(file), start, start + self.batch_size)
            rows = [record.split(",", 4) for record in records]
        texts = [row[4].replace('""', '"') for row in rows]  # review
        labels = [LABELS[row[3]] for row in rows]  # sentiment
        return texts, labels

    def batch_tokenized(self, i: int) -> Tuple[List[List[int]], List[int]]:
        """Return tokenized i-th batch of data"""
        texts, labels = self.batch_loaded(i)
        tokens = self.tokenize(texts)
        return tokens, labels

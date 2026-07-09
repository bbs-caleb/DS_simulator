"""Batch data loader with padding and BERT sentence embeddings."""

from dataclasses import dataclass, field
from itertools import islice
from typing import Generator, Iterator, List, TextIO, Tuple

import torch
from transformers import PreTrainedTokenizer

LABELS = {"negative": -1, "neutral": 0, "positive": 1}


def iter_records(file: TextIO) -> Iterator[str]:
    """Yield logical csv records, merging multiline quoted fields"""
    record = file.readline()
    while record:
        while record.count('"') % 2:  # unbalanced quotes: field spans more lines
            line = file.readline()
            if not line:
                break
            record += line
        yield record.rstrip("\n")
        record = file.readline()


def attention_mask(padded: List[List[int]]) -> List[List[int]]:
    """Return mask of ones for real tokens and zeros for padding"""
    return [[int(token != 0) for token in row] for row in padded]


def review_embedding(tokens: List[List[int]], model) -> List[List[float]]:
    """Return embedding for batch of tokenized texts"""
    mask = attention_mask(tokens)
    tokens = torch.tensor(tokens)
    mask = torch.tensor(mask)
    with torch.no_grad():
        last_hidden_states = model(tokens, attention_mask=mask)
    return last_hidden_states[0][:, 0, :].tolist()  # [CLS] embeddings


@dataclass
class DataLoader:
    """Load, tokenize and pad reviews from a csv file batch by batch."""

    path: str
    tokenizer: PreTrainedTokenizer
    batch_size: int = 512
    max_length: int = 128
    padding: str = None
    offsets: List[int] = field(default_factory=list, init=False, repr=False)

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

    def seek_records(self, file: TextIO, i: int) -> Iterator[str]:
        """Position file at batch i start, caching offsets on the way"""
        if not self.offsets:
            file.readline()  # skip header
            self.offsets.append(file.tell())
        known = min(i, len(self.offsets) - 1)  # nearest cached batch
        file.seek(self.offsets[known])
        records = iter_records(file)
        for _ in range(i - known):  # skip forward, remembering boundaries
            for _ in islice(records, self.batch_size):
                pass
            self.offsets.append(file.tell())
        return records

    def pad(self, tokens: List[List[int]]) -> List[List[int]]:
        """Pad token sequences with zeros according to padding mode"""
        if self.padding == "max_length":
            width = self.max_length
        elif self.padding == "batch":
            width = max(len(row) for row in tokens)
        else:
            return tokens
        return [row + [0] * (width - len(row)) for row in tokens]

    def tokenize(self, batch: List[str]) -> List[List[int]]:
        """Tokenize list of texts"""
        tokens = [
            self.tokenizer.encode(
                text,
                add_special_tokens=True,
                max_length=self.max_length,
                truncation=True,
            )
            for text in batch
        ]
        return self.pad(tokens)

    def batch_loaded(self, i: int) -> Tuple[List[str], List[int]]:
        """Return loaded i-th batch of data (text, label)"""
        with open(self.path, encoding="utf-8") as file:
            records = self.seek_records(file, i)
            rows = [record.split(",", 4) for record in islice(records, self.batch_size)]
            if i + 1 == len(self.offsets) and len(rows) == self.batch_size:
                self.offsets.append(file.tell())  # remember next batch start
        texts = [row[4].replace('""', '"') for row in rows]  # review
        labels = [LABELS[row[3]] for row in rows]  # sentiment
        return texts, labels

    def batch_tokenized(self, i: int) -> Tuple[List[List[int]], List[int]]:
        """Return tokenized i-th batch of data"""
        texts, labels = self.batch_loaded(i)
        tokens = self.tokenize(texts)
        return tokens, labels

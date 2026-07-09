"""Parallel text cleaning with joblib."""

import math
import multiprocessing
import re
from string import punctuation
from typing import Iterable, List

import pandas as pd
from joblib import Parallel, delayed
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

URL_PATTERN = re.compile(r"https?://[^,\s]+,?")
MENTION_PATTERN = re.compile(r"@[^,\s]+,?")
MULTISPACE_PATTERN = re.compile(r" +")
PUNCT_TRANSLATOR = str.maketrans("", "", punctuation)

_STOP_WORDS = None


def _get_stop_words() -> set:
    """Load English stop words once inside each process."""
    global _STOP_WORDS
    if _STOP_WORDS is None:
        _STOP_WORDS = set(stopwords.words("english"))
    return _STOP_WORDS


def _clean_text(text: str, lemmatizer: WordNetLemmatizer, stop_words: set) -> str:
    """Clean and lemmatize one text."""
    text = str(text)
    text = URL_PATTERN.sub("", text)
    text = MENTION_PATTERN.sub("", text)
    text = text.translate(PUNCT_TRANSLATOR)
    text = MULTISPACE_PATTERN.sub(" ", text).strip()

    words = text.split()
    lemma_words = [lemmatizer.lemmatize(word.lower()) for word in words]
    clean_words = [word for word in lemma_words if word not in stop_words]

    return " ".join(clean_words)


def _clean_text_batch(texts: Iterable[str]) -> List[str]:
    """Clean a group of texts inside one process."""
    stop_words = _get_stop_words()
    lemmatizer = WordNetLemmatizer()

    return [_clean_text(text, lemmatizer, stop_words) for text in texts]


def _resolve_n_jobs(n_jobs: int, data_size: int) -> int:
    """Convert n_jobs to a real positive number of processes."""
    if n_jobs == 0:
        raise ValueError("n_jobs must not be 0")

    if data_size == 0:
        return 1

    if n_jobs < 0:
        cpu_count = multiprocessing.cpu_count()
        n_jobs = max(cpu_count + 1 + n_jobs, 1)

    return min(n_jobs, data_size)


def _split_into_chunks(items: List[str], chunk_count: int) -> List[List[str]]:
    """Split data into several ordered chunks."""
    chunk_size = math.ceil(len(items) / chunk_count)
    return [items[index:index + chunk_size] for index in range(0, len(items), chunk_size)]


def clear_data(source_path: str, target_path: str, n_jobs: int):
    """Parallel process dataframe.

    Parameters
    ----------
    source_path : str
        Path to load dataframe from.

    target_path : str
        Path to save dataframe to.

    n_jobs : int
        Count of jobs to process. Use -1 to use all CPU cores.
    """
    data = pd.read_parquet(source_path)
    data = data.copy().dropna().reset_index(drop=True)

    texts = data["text"].tolist()
    process_count = _resolve_n_jobs(n_jobs, len(texts))
    chunks = _split_into_chunks(texts, process_count)

    if process_count == 1:
        cleaned_chunks = [_clean_text_batch(chunks[0])] if chunks else [[]]
    else:
        cleaned_chunks = Parallel(
            n_jobs=process_count,
            backend="multiprocessing",
            batch_size=1,
        )(delayed(_clean_text_batch)(chunk) for chunk in chunks)

    data["cleaned_text"] = [text for chunk in cleaned_chunks for text in chunk]
    data.to_parquet(target_path)

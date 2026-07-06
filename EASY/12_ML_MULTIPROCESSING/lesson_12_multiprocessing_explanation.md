# 12 урок. ML: MULTIPROCESSING

## 1. Контекст задачи

### Бизнесовый контекст

В NLP-задачах часто нужно обрабатывать много текстов: отзывы клиентов, обращения в поддержку, сообщения в чатах, комментарии, описания товаров.

Перед обучением модели текст обычно чистят: удаляют ссылки, упоминания, пунктуацию, разбивают текст на слова, приводят слова к нижнему регистру, лемматизируют и удаляют стоп-слова.

Если строк мало, обычный цикл работает нормально. Но если строк много, последовательная обработка становится медленной. Один процесс обрабатывает один текст, потом второй, потом третий — как одна касса в магазине.

Параллельная обработка позволяет открыть несколько «касс». Каждый процесс получает свою часть текстов и чистит их независимо.

Для бизнеса это важно, потому что быстрее готовятся данные для ML-моделей, быстрее пересчитываются NLP-признаки, быстрее запускаются эксперименты и команда меньше ждёт завершения пайплайна.

### Технический контекст

В исходном baseline-коде все тексты обрабатываются в одном цикле:

```python
for text in data["text"]:
    обработать текст
```

Это последовательная обработка.

В задании нужно реализовать ту же самую очистку, но параллельно через `joblib`:

- `Parallel` запускает несколько процессов;
- `delayed` передаёт функцию в параллельное выполнение;
- `n_jobs` задаёт количество процессов.

Главное условие: результат должен совпадать с baseline. Поэтому нельзя менять логику токенизации. В первой версии ошибка была в том, что вместо `word_tokenize()` использовался `split()`. Это быстрее, но результат может отличаться. В исправленной версии используется именно `word_tokenize()`, как в baseline.

---

## 2. Готовое решение

Файл для отправки: `lesson_12_multiprocessing_solution.py`

```python
"""Parallel text preprocessing for NLP datasets."""

import math
import multiprocessing
import re
from string import punctuation
from typing import Iterable, List

import pandas as pd
from joblib import Parallel, delayed
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

URL_PATTERN = re.compile(r"https?://[^,\s]+,?")
MENTION_PATTERN = re.compile(r"@[^,\s]+,?")
SPACE_PATTERN = re.compile(" +")
TRANSLATOR = str.maketrans("", "", punctuation)


def _clean_texts(texts: Iterable[str]) -> List[str]:
    """Clean a batch of texts using the same logic as the baseline."""
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words("english"))
    cleaned_texts = []

    for text in texts:
        text = str(text)
        text = URL_PATTERN.sub("", text)
        text = MENTION_PATTERN.sub("", text)

        transform_text = text.translate(TRANSLATOR)
        transform_text = SPACE_PATTERN.sub(" ", transform_text)

        text_tokens = word_tokenize(transform_text)
        lemma_text = [
            lemmatizer.lemmatize(word.lower())
            for word in text_tokens
        ]
        cleaned_text = " ".join(
            str(word) for word in lemma_text if word not in stop_words
        )
        cleaned_texts.append(cleaned_text)

    return cleaned_texts


def _get_batch_count(n_jobs: int, data_size: int) -> int:
    """Return a safe number of batches for parallel processing."""
    if n_jobs == 0:
        raise ValueError("n_jobs must not be 0")

    if n_jobs < 0:
        cpu_count = multiprocessing.cpu_count()
        n_jobs = max(cpu_count + 1 + n_jobs, 1)

    return min(n_jobs, data_size)


def _make_batches(items: List[str], n_batches: int) -> List[List[str]]:
    """Split a list into ordered batches."""
    batch_size = math.ceil(len(items) / n_batches)
    return [
        items[index:index + batch_size]
        for index in range(0, len(items), batch_size)
    ]


def clear_data(source_path: str, target_path: str, n_jobs: int) -> None:
    """Parallel process dataframe.

    Parameters
    ----------
    source_path : str
        Path to load dataframe from

    target_path : str
        Path to save dataframe to

    n_jobs : int
        Count of job to process
    """
    data = pd.read_parquet(source_path)
    data = data.copy().dropna().reset_index(drop=True)

    texts = data["text"].tolist()
    if not texts:
        data["cleaned_text"] = []
        data.to_parquet(target_path)
        return

    if n_jobs == 1:
        cleaned_text_list = _clean_texts(texts)
    else:
        batch_count = _get_batch_count(n_jobs, len(texts))
        batches = _make_batches(texts, batch_count)
        cleaned_batches = Parallel(
            n_jobs=n_jobs,
            backend="multiprocessing",
            batch_size=1,
        )(delayed(_clean_texts)(batch) for batch in batches)
        cleaned_text_list = [
            text for batch in cleaned_batches for text in batch
        ]

    data["cleaned_text"] = cleaned_text_list
    data.to_parquet(target_path)

```

---

## 3. Почему первая версия получила 0 баллов

Тест `xtest_baseline_equal` сравнивает результат нашей функции с результатом baseline-кода.

В baseline используется:

```python
text_tokens = word_tokenize(transform_text)
```

В первой версии был использован более простой вариант:

```python
words = text.split()
```

Это не одно и то же.

`split()` просто режет текст по пробелам.

`word_tokenize()` использует правила NLTK. Она может иначе обрабатывать сокращения, спецсимволы и некоторые текстовые случаи.

Поэтому даже если код быстрее, тест считает решение неправильным, потому что итоговый `cleaned_text` не совпадает с baseline.

---

## 4. Пошаговое объяснение кода

### Шаг 1. Импортируем библиотеки

```python
import math
import multiprocessing
import re
from string import punctuation
from typing import Iterable, List
```

- `math` нужен для округления размера батча вверх.
- `multiprocessing` нужен, чтобы узнать количество ядер процессора.
- `re` нужен для регулярных выражений.
- `punctuation` содержит стандартные знаки пунктуации.
- `Iterable` и `List` нужны для подсказок типов.

```python
import pandas as pd
from joblib import Parallel, delayed
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
```

- `pandas` читает и сохраняет parquet-файл.
- `Parallel` запускает параллельную обработку.
- `delayed` подготавливает функцию к параллельному запуску.
- `stopwords` даёт список частых английских слов.
- `WordNetLemmatizer` приводит слова к базовой форме.
- `word_tokenize` разбивает текст на токены так же, как baseline.

### Шаг 2. Заранее готовим регулярные выражения

```python
URL_PATTERN = re.compile(r"https?://[^,\s]+,?")
MENTION_PATTERN = re.compile(r"@[^,\s]+,?")
SPACE_PATTERN = re.compile(" +")
TRANSLATOR = str.maketrans("", "", punctuation)
```

В baseline регулярные выражения и таблица удаления пунктуации фактически готовятся во время обработки текстов. Здесь мы готовим их один раз заранее. Это ускоряет код, но не меняет результат.

### Шаг 3. Функция `_clean_texts`

```python
def _clean_texts(texts: Iterable[str]) -> List[str]:
```

Эта функция получает не один текст, а батч текстов.

Например, если у нас 10 000 текстов и 4 процесса, данные можно разделить примерно так:

- процесс 1: тексты 1–2500;
- процесс 2: тексты 2501–5000;
- процесс 3: тексты 5001–7500;
- процесс 4: тексты 7501–10000.

Внутри функции создаются:

```python
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))
```

`lemmatizer` нужен для лемматизации.

`stop_words` переведён в `set`, потому что проверка `word not in stop_words` в множестве работает быстрее, чем в списке. Результат при этом не меняется.

### Шаг 4. Очистка текста

Каждый текст обрабатывается так же, как в baseline:

```python
text = str(text)
text = URL_PATTERN.sub("", text)
text = MENTION_PATTERN.sub("", text)
transform_text = text.translate(TRANSLATOR)
transform_text = SPACE_PATTERN.sub(" ", transform_text)
text_tokens = word_tokenize(transform_text)
lemma_text = [lemmatizer.lemmatize(word.lower()) for word in text_tokens]
cleaned_text = " ".join(
    [str(word) for word in lemma_text if word not in stop_words]
)
```

Самая важная строка:

```python
text_tokens = word_tokenize(transform_text)
```

Она нужна, чтобы результат совпал с baseline.

### Шаг 5. Функция `_get_batch_count`

```python
def _get_batch_count(n_jobs: int, data_size: int) -> int:
```

Эта функция определяет, на сколько частей делить данные.

Если `n_jobs == 0`, это ошибка, потому что нельзя запустить ноль процессов:

```python
if n_jobs == 0:
    raise ValueError("n_jobs must not be 0")
```

Если `n_jobs < 0`, например `-1`, это значит использовать максимум доступных ядер:

```python
cpu_count = multiprocessing.cpu_count()
n_jobs = max(cpu_count + 1 + n_jobs, 1)
```

Например, если у компьютера 8 ядер и `n_jobs=-1`, получится 8 процессов.

В конце количество батчей ограничивается количеством строк:

```python
return min(n_jobs, data_size)
```

### Шаг 6. Функция `_make_batches`

```python
def _make_batches(items: List[str], n_batches: int) -> List[List[str]]:
```

Эта функция делит список текстов на части.

```python
batch_size = math.ceil(len(items) / n_batches)
```

`math.ceil` округляет вверх.

Например, `math.ceil(10 / 4) = 3`.

Дальше создаётся список батчей:

```python
return [
    items[index:index + batch_size]
    for index in range(0, len(items), batch_size)
]
```

### Шаг 7. Главная функция `clear_data`

```python
def clear_data(source_path: str, target_path: str, n_jobs: int) -> None:
```

Она принимает:

- `source_path` — путь к исходному parquet-файлу;
- `target_path` — путь, куда сохранить результат;
- `n_jobs` — сколько процессов использовать.

Сначала читаем данные:

```python
data = pd.read_parquet(source_path)
```

Потом повторяем baseline-логику:

```python
data = data.copy().dropna().reset_index(drop=True)
```

Дальше берём колонку `text` как список:

```python
texts = data["text"].tolist()
```

Если после удаления пропусков строк не осталось, сохраняем пустой результат:

```python
if not texts:
    data["cleaned_text"] = []
    data.to_parquet(target_path)
```

### Шаг 8. Если `n_jobs == 1`

```python
if n_jobs == 1:
    cleaned_text_list = _clean_texts(texts)
```

Если процесс один, параллельность не нужна. Мы просто чистим все тексты в одном процессе.

### Шаг 9. Если процессов несколько

```python
batch_count = _get_batch_count(n_jobs, len(texts))
batches = _make_batches(texts, batch_count)
```

Сначала считаем количество батчей, потом делим тексты.

Дальше запускаем `joblib`:

```python
cleaned_batches = Parallel(
    n_jobs=n_jobs,
    backend="multiprocessing",
    batch_size=1,
)(delayed(_clean_texts)(batch) for batch in batches)
```

На выходе получается список списков. Его нужно превратить в один список:

```python
cleaned_text_list = [text for batch in cleaned_batches for text in batch]
```

`Parallel` сохраняет порядок задач, поэтому порядок строк в результате не ломается.

### Шаг 10. Сохраняем результат

```python
data["cleaned_text"] = cleaned_text_list
data.to_parquet(target_path)
```

Создаём новую колонку `cleaned_text` и сохраняем parquet-файл.

---

## 5. Почему решение должно пройти `baseline_equal`

Порядок обработки повторяет baseline:

1. `pd.read_parquet(source_path)`
2. `data.copy().dropna().reset_index(drop=True)`
3. `str(text)`
4. удаление ссылок через `r"https?://[^,\s]+,?"`
5. удаление mentions через `r"@[^,\s]+,?"`
6. удаление пунктуации через `str.maketrans("", "", punctuation)`
7. замена нескольких пробелов через `re.sub(" +", " ", transform_text)`
8. `word_tokenize(transform_text)`
9. `lemmatizer.lemmatize(word.lower())`
10. удаление английских stopwords
11. сборка строки через `" ".join(...)`

Главное отличие от baseline только в том, что тексты обрабатываются батчами параллельно.

Смысл очистки не изменён.

---

## 6. Почему решение быстрее baseline

Baseline делает неэффективную вещь внутри каждой строки:

```python
stop_words = stopwords.words("english")
```

То есть список стоп-слов загружается заново для каждого текста.

В решении стоп-слова создаются один раз на батч:

```python
stop_words = set(stopwords.words("english"))
```

Также baseline обрабатывает все тексты одним процессом. Решение делит тексты на батчи и обрабатывает их параллельно:

```python
Parallel(n_jobs=n_jobs, backend="multiprocessing")
```

Поэтому на больших данных должно быть быстрее.

---

## 7. Что отправлять

В систему нужно загрузить файл:

```text
lesson_12_multiprocessing_solution.py
```

Не нужно загружать `.md`-файл, если платформа просит только Python-файл.

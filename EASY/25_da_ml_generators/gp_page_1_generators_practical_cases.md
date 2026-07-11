# Практические промышленные сценарии применения генераторов

## 1. Потоковое чтение JSONL

JSONL хранит один JSON-объект в каждой строке.

```python
import json


def read_jsonl(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        for line in file:
            yield json.loads(line)
```

Потребление:

```python
for event in read_jsonl("events.jsonl"):
    process(event)
```

Преимущества:

- файл может быть больше RAM;
- обработка начинается сразу;
- можно остановиться раньше;
- ошибка может быть привязана к конкретной строке.

---

# 2. Потоковая валидация

```python
def valid_events(events):
    for event in events:
        if "user_id" not in event:
            continue

        if "timestamp" not in event:
            continue

        yield event
```

Pipeline:

```python
events = read_jsonl("events.jsonl")
events = valid_events(events)

for event in events:
    save(event)
```

Каждый объект проходит обработку отдельно.

---

# 3. Генератор батчей

```python
def make_batches(items, batch_size):
    batch = []

    for item in items:
        batch.append(item)

        if len(batch) == batch_size:
            yield batch
            batch = []

    if batch:
        yield batch
```

Пример:

```python
for batch in make_batches(events, batch_size=1000):
    insert_batch(batch)
```

Почему batch processing часто лучше выдачи по одной записи:

- меньше SQL-запросов;
- меньше сетевых round trips;
- эффективнее bulk insert;
- удобнее retry;
- можно применять векторные операции;
- память остаётся ограниченной размером батча.

---

# 4. Пагинация API

```python
def iter_api_records(client):
    page = 1

    while True:
        response = client.get_records(page=page)
        records = response["records"]

        if not records:
            break

        for record in records:
            yield record

        page += 1
```

Потребитель не знает о страницах:

```python
for record in iter_api_records(client):
    save(record)
```

Production-добавления:

- timeout;
- retry;
- exponential backoff;
- rate limiting;
- checkpoint;
- deduplication;
- observability.

---

# 5. Keyset pagination из базы

```python
def iter_orders(repository, batch_size):
    last_id = 0

    while True:
        rows = repository.fetch_after(
            last_id=last_id,
            limit=batch_size,
        )

        if not rows:
            break

        for row in rows:
            yield row

        last_id = rows[-1]["order_id"]
```

Преимущества перед большим `OFFSET`:

- стабильнее на больших таблицах;
- можно хранить checkpoint;
- проще продолжить после сбоя;
- меньше деградация при росте номера страницы.

Требования:

- стабильный порядок;
- подходящий уникальный ключ;
- понимание поведения при новых вставках.

---

# 6. ML batch generator

```python
def training_batches(features, targets, batch_size):
    for start in range(0, len(features), batch_size):
        end = start + batch_size
        yield features[start:end], targets[start:end]
```

В реальном проекте добавятся:

- shuffle;
- epochs;
- augmentation;
- prefetch;
- multiprocessing workers;
- deterministic seed;
- обработка последнего неполного батча.

---

# 7. Генератор синтетического временного ряда

```python
import random


def synthetic_metric(number_of_points):
    for timestamp_index in range(number_of_points):
        value = random.randint(0, 100)
        yield timestamp_index, value
```

Это промышленное развитие второй функции задания.

Применения:

- тестирование dashboard;
- mock real-time source;
- проверка графика;
- нагрузочное тестирование consumer;
- тестирование мониторинга.

Синтетические данные нельзя выдавать за реальные бизнес-наблюдения.

---

# 8. Генератор тестовых пользователей

```python
import random


def synthetic_users(number_of_users, first_names, last_names):
    for user_id in range(1, number_of_users + 1):
        yield {
            "id": user_id,
            "first_name": random.choice(first_names),
            "last_name": random.choice(last_names),
        }
```

Применения:

- unit tests;
- integration tests;
- заполнение dev-среды;
- демонстрационный стенд;
- нагрузочное тестирование;
- проверка импорта и пагинации.

Ограничения:

- имена повторяются;
- распределение нереалистично;
- между признаками нет настоящих зависимостей;
- такой поток не подходит для честной оценки ML-модели.

---

# 9. Фильтр кандидатов в рекомендациях

```python
def available_candidates(candidates):
    for candidate in candidates:
        if not candidate["in_stock"]:
            continue

        if candidate["is_blocked"]:
            continue

        yield candidate
```

Можно взять первые 100:

```python
from itertools import islice


top_available = list(
    islice(available_candidates(candidates), 100)
)
```

Это корректно только тогда, когда исходный поток уже идёт в нужном порядке релевантности.

---

# 10. Antifraud replay

Исторические транзакции можно последовательно подавать в новую версию правил или модели.

Задачи:

- сравнить old/new model;
- оценить false positives;
- проверить latency;
- найти regression;
- воспроизвести инцидент;
- построить backtest.

Нужно контролировать:

- event time;
- processing time;
- порядок;
- дубли;
- late events;
- feature state на исторический момент;
- идемпотентность.

---

# 11. Потоковый экспорт CSV

```python
def csv_rows(records):
    yield "id,amount\n"

    for record in records:
        yield f'{record["id"]},{record["amount"]}\n'
```

Web framework может отправлять строки пользователю по мере генерации.

Плюсы:

- низкая память;
- ранний time-to-first-byte;
- поддержка больших экспортов.

Риски:

- ошибка может произойти после начала ответа;
- клиент может отключиться;
- соединение с БД может жить долго;
- сложнее повторить частично скачанный файл;
- нужны timeout и cancellation.

---

# 12. Потоковый агрегат

Для суммы не нужен список:

```python
total_revenue = sum(
    order["revenue"]
    for order in orders
)
```

Для среднего:

```python
total = 0
count = 0

for value in values:
    total += value
    count += 1

average = total / count if count else 0
```

Дополнительная память — `O(1)`.

---

# 13. Потоковый top-k

```python
import heapq


def top_k_by_score(items, k):
    return heapq.nlargest(
        k,
        items,
        key=lambda item: item["score"],
    )
```

`heapq.nlargest` принимает iterable. Память в типичном случае зависит от `k`, а не от полного количества входных элементов.

---

# 14. Когда generator pipeline опасен

Красивый pipeline:

```python
source = read_source()
cleaned = clean(source)
enriched = enrich(cleaned)
filtered = filter_rows(enriched)
```

может скрывать проблемы:

- источник открыт слишком долго;
- ошибка возникает только во время потребления;
- один этап становится bottleneck;
- нет checkpoint;
- повторный проход невозможен;
- не видно, где потерялись записи;
- два consumer случайно делят один генератор.

Production pipeline требует:

- input/output counters;
- latency на каждом шаге;
- error handling;
- dead-letter storage;
- checkpoints;
- schema validation;
- timeout;
- retry;
- data-quality checks.

---

# 15. Мини-проект из этого урока

## Название

**Synthetic Event Stream for Dashboard Testing**

## Бизнесовая задача

Команда делает dashboard, но реальный источник данных ещё не готов. Нужен временный поток точек для проверки:

- отображения графика;
- обновления значений;
- поведения на границах;
- нагрузки;
- остановки потока;
- обработки аномалий.

## Архитектура

```text
data_generator
    -> validation
    -> batching
    -> mock API
    -> dashboard
```

## Что можно добавить

- timestamp;
- несколько метрик;
- тренд;
- сезонность;
- пропуски;
- выбросы;
- фиксированный seed;
- сохранение в JSONL;
- unit tests;
- метрики throughput.

## Почему это похоже на реальную работу

В production регулярно создают:

- mock data;
- test fixtures;
- replay streams;
- synthetic load;
- staging pipelines;
- demo environments.

Учебное задание даёт базовый механизм для такого инструмента.

---

# 16. Главный вывод

Генератор особенно подходит, когда жизненный цикл записи выглядит так:

```text
получить -> проверить -> преобразовать -> использовать -> забыть
```

Если данные нужно:

- многократно использовать;
- сортировать целиком;
- индексировать;
- случайно выбирать;
- хранить долго;

то лучше может подойти список, массив, DataFrame, таблица или внешний storage.

Сильный инженер не использует генераторы везде. Он выбирает их тогда, когда ленивость соответствует реальному жизненному циклу данных.

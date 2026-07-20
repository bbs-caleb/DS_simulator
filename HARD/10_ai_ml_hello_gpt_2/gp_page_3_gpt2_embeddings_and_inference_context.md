# Страница 3. Как GPT-2 видит слова и как собрать inference-пайплайн

## 1. Что требуется сделать на этой странице

На прошлой странице была реализована функция генерации token IDs. Она уже умеет:

- получать текущую последовательность ID;
- вызывать модель;
- применять temperature;
- применять top-k;
- применять top-p;
- выбирать следующий token ID;
- повторять процесс авторегрессивно.

Но пользователь не работает с ID токенов. Пользователь вводит обычную строку:

```text
The best thing about AI is its ability to
```

И ожидает обычную строку на выходе.

Поэтому сейчас требуется соединить три компонента:

```text
ТЕКСТ
  ↓ encoder.encode
TOKEN IDs
  ↓ generate
НОВЫЕ TOKEN IDs
  ↓ encoder.decode
ТЕКСТ
```

В этом и состоит задача страницы.

---

# Часть I. Бизнесовый смысл

## 2. Почему этот шаг важен для продукта

Предыдущая функция `generate` была математическим ядром. Но сама по себе она неудобна для продукта:

```python
generate(
    llm=gpt2,
    input_ids=[464, 1266, 1517],
    ...
)
```

Продавец маркетплейса не знает, что означают числа `464`, `1266` и `1517`.

Он хочет передать:

```text
Wireless headphones with noise cancellation
```

И получить:

```text
Designed for comfortable everyday listening...
```

Значит, production-сервису нужны интерфейсные слои:

1. **Tokenizer / Encoder** — переводит текст в ID.
2. **Language Model** — работает с числовыми представлениями.
3. **Decoder** — переводит ID обратно в текст.

Без первого и третьего слоя модель существует только как математический объект, но не как пользовательский сервис.

---

## 3. Где используется такой pipeline

### E-commerce

Вход:

```text
Product: wireless headphones
Features: ANC, Bluetooth 5.2, 30-hour battery
```

Выход:

```text
Experience immersive sound with active noise cancellation...
```

### Fintech

Вход:

```text
Explain why this transfer is pending in simple language
```

Выход:

```text
The transfer is still being checked by the receiving bank...
```

### Support

Вход:

```text
Customer cannot reset password
```

Выход:

```text
Please check whether the reset email is in the spam folder...
```

### Two-sided marketplace

Вход:

```text
Create a concise job description for a Python data engineer
```

Выход:

```text
We are looking for a Python data engineer to build reliable pipelines...
```

### Internal Big Tech assistant

Вход:

```text
Summarize the following incident report
```

Выход:

```text
The outage was caused by an invalid configuration rollout...
```

Во всех случаях пользовательский API работает со строками, хотя модель внутри работает с ID и векторами.

---

# Часть II. Эмбеддинги токенов

## 4. Что такое token embedding

Token ID — это всего лишь номер:

```text
token "cat" → ID 9246
```

Число `9246` не является смыслом слова. Между ID 9246 и ID 9247 нет смысловой близости только потому, что числа рядом.

Поэтому внутри модели используется таблица embeddings:

\[
W_{TE} \in \mathbb{R}^{V \times D}
\]

где:

- \(V\) — размер словаря;
- \(D\) — размерность модели;
- одна строка таблицы — embedding одного token ID.

Для GPT-2 размер словаря равен 50 257 токенам.

Для GPT-2 Small:

\[
W_{TE} \in \mathbb{R}^{50257 \times 768}
\]

Если token ID равен 9246, модель берет строку:

```python
wte[9246]
```

Результат — вектор из 768 вещественных чисел.

---

## 5. Почему embedding — это «численный смысл»

В процессе обучения embedding-векторы меняются вместе с остальными весами модели.

Модель постепенно размещает токены в многомерном пространстве так, чтобы полезные закономерности можно было извлекать линейными преобразованиями и attention-механизмом.

Упрощенная интуиция:

- близкие контексты → частично похожие представления;
- разные грамматические функции → разные направления пространства;
- свойства токена могут кодироваться распределенно по множеству координат.

Не нужно представлять, что одна координата означает «животное», а другая «цвет». В современных моделях признаки обычно распределены по большому числу измерений.

---

## 6. Размеры GPT-2

Семейство GPT-2 включает четыре основные конфигурации:

| Модель | Размерность embedding | Число слоев |
|---|---:|---:|
| 124M / Small | 768 | 12 |
| 355M / Medium | 1024 | 24 |
| 774M / Large | 1280 | 36 |
| 1558M / XL | 1600 | 48 |

Увеличение модели означает:

- больше параметров;
- больше памяти;
- больше вычислений;
- обычно лучшее качество;
- выше latency;
- дороже inference.

Для бизнеса «больше» не всегда означает «лучше». Нужно учитывать:

- SLA;
- стоимость GPU;
- нагрузку;
- качество на конкретной задаче;
- возможность использовать более маленькую модель с fine-tuning.

---

# Часть III. Позиционные embeddings

## 7. Почему порядок токенов важен

Рассмотрим:

```text
The cat chased the mouse.
```

и:

```text
The mouse chased the cat.
```

Набор токенов почти одинаковый, но смысл противоположный.

Если передать модели только embeddings токенов без информации о позиции, она не сможет надежно различать порядок.

---

## 8. Как GPT-2 кодирует позиции

GPT-2 использует обучаемую таблицу positional embeddings:

\[
W_{PE} \in \mathbb{R}^{C \times D}
\]

где:

- \(C\) — максимальная длина контекста;
- \(D\) — размерность embedding.

Для GPT-2 Small:

\[
W_{PE} \in \mathbb{R}^{1024 \times 768}
\]

Для токена на позиции \(i\) входное представление формируется как:

\[
x_i = W_{TE}[token_i] + W_{PE}[i]
\]

То есть модель складывает:

- смысл токена;
- информацию о его позиции.

Оба вектора имеют одинаковую размерность, поэтому сложение возможно.

---

## 9. Почему сложение не уничтожает смысл

Модель обучается с самого начала на сумме token и positional embeddings.

Все следующие линейные слои приспосабливаются к такой форме входа.

Интуитивно модель учится извлекать разные типы информации из разных направлений embedding-пространства:

- содержание токена;
- положение;
- синтаксическую роль;
- контекст.

Сложение не означает, что информация физически смешалась необратимо. В высокоразмерном пространстве обучаемые проекции способны выделять полезные компоненты.

---

# Часть IV. Transformer-блок

## 10. Два главных преобразования

Каждый decoder-блок GPT-2 содержит два главных вычислительных этапа:

1. Masked Multi-Head Self-Attention.
2. Feed-Forward Network.

Упрощенная схема:

```text
representations
    ↓
masked self-attention
    ↓
context-enriched representations
    ↓
feed-forward network
    ↓
updated representations
```

---

## 11. Self-Attention

Self-Attention позволяет каждому токену учитывать другие доступные токены.

Для каждого токена вычисляются:

- Query;
- Key;
- Value.

Затем токен определяет, на какие предыдущие токены стоит обратить больше внимания.

Пример:

```text
The trophy did not fit in the suitcase because it was too large.
```

Чтобы понять, к чему относится `it`, модель должна использовать контекст.

Attention позволяет текущему токену собирать информацию из других токенов с разными весами.

---

## 12. Почему attention называется masked

GPT-2 генерирует слева направо.

При предсказании следующего токена модель не должна видеть будущие токены. Иначе во время обучения она подсматривала бы правильный ответ.

Используется causal mask:

```text
позиция 1 видит: 1
позиция 2 видит: 1, 2
позиция 3 видит: 1, 2, 3
позиция 4 видит: 1, 2, 3, 4
```

Будущие позиции маскируются.

---

## 13. Feed-Forward Network

После обмена контекстом каждый токен отдельно проходит через FFN.

FFN применяется независимо к каждой позиции, но с одинаковыми весами.

Для GPT-2 Small размерность обычно расширяется:

```text
768 → 3072 → 768
```

FFN можно интерпретировать как этап локальной обработки уже собранной контекстной информации.

Attention отвечает за:

> Откуда взять информацию?

FFN отвечает за:

> Как преобразовать собранную информацию?

---

# Часть V. Encoder из задания

## 14. Что делает `encoder.encode`

В предоставленном `encoder.py` метод:

```python
encoder.encode(text)
```

выполняет:

1. разбиение текста регулярным выражением;
2. преобразование UTF-8 байтов;
3. Byte Pair Encoding;
4. поиск каждого BPE-токена в словаре;
5. возврат списка token IDs.

Пример интерфейса:

```python
input_ids = encoder.encode(
    "The best thing about AI"
)
```

Результат имеет вид:

```python
[464, 1266, 1517, 546, ...]
```

Конкретные ID зависят от GPT-2 vocabulary.

---

## 15. Что делает `encoder.decode`

Метод:

```python
encoder.decode(output_ids)
```

выполняет обратное преобразование:

```text
token IDs
  ↓
BPE token strings
  ↓
byte sequence
  ↓
UTF-8 text
```

На выходе получается обычная строка.

---

# Часть VI. Загрузка модели

## 16. Что возвращает utility-функция

В шаблоне:

```python
encoder, hparams, weights = (
    load_encoder_hparams_and_weights(
        model_size,
        models_dir,
    )
)
```

Возвращаются три объекта.

### `encoder`

Токенизатор и декодер GPT-2.

### `hparams`

Гиперпараметры модели, например:

- `n_ctx`;
- `n_embd`;
- `n_layer`;
- `n_head`;
- `n_vocab`.

### `weights`

Все обученные матрицы модели:

- token embeddings;
- positional embeddings;
- attention weights;
- FFN weights;
- normalization parameters.

---

## 17. Проверка длины контекста

```python
assert len(input_ids) + n_tokens < hparams["n_ctx"]
```

Модель не может обрабатывать бесконечно длинный контекст.

Если:

```text
n_ctx = 1024
prompt = 1000 токенов
n_tokens = 40
```

то:

```text
1000 + 40 = 1040
```

Это превышает окно контекста.

Проверка останавливает выполнение до того, как модель попадет в некорректное состояние.

---

# Часть VII. Полный data flow

## 18. Этап 1 — загрузка

```python
encoder, hparams, weights = (
    load_encoder_hparams_and_weights(
        model_size,
        models_dir,
    )
)
```

Система загружает:

- vocabulary;
- BPE merges;
- hparams;
- checkpoint;
- веса.

---

## 19. Этап 2 — токенизация

```python
input_ids = encoder.encode(prompt)
```

Строка становится списком целых чисел.

---

## 20. Этап 3 — генерация

```python
output_ids = generate(
    llm=gpt2,
    input_ids=input_ids,
    n_tokens=n_tokens,
    top_k=50,
    top_p=0.8,
    temperature=0.75,
    random_state=0,
    weights=weights,
)
```

Критически важно передать:

- `llm=gpt2`;
- `input_ids=input_ids`;
- `n_tokens=n_tokens`;
- `weights=weights`.

---

## 21. Этап 4 — декодирование

```python
output = encoder.decode(output_ids)
```

Новые token IDs превращаются в строку.

---

## 22. Этап 5 — возврат

```python
return output
```

Функция `main` возвращает строку, которую можно:

- показать в CLI;
- вернуть через API;
- вывести в Streamlit;
- сохранить в БД;
- отправить продавцу.

---

# Часть VIII. Что именно проверяют тесты

## 23. Токенизация — 20%

Ожидается:

```python
input_ids = encoder.encode(prompt)
```

Типичные ошибки:

```python
input_ids = prompt
```

или:

```python
input_ids = [prompt]
```

или:

```python
input_ids = encoder(prompt)
```

---

## 24. Вызов генерации — 40%

Ожидается корректный вызов:

```python
generate(
    llm=gpt2,
    input_ids=input_ids,
    n_tokens=n_tokens,
    ...
    weights=weights,
)
```

Типичные ошибки:

- передать `prompt` вместо `input_ids`;
- передать `encoder` вместо `gpt2`;
- забыть `weights`;
- захардкодить `n_tokens=10`;
- перепутать `model_size` и `models_dir`.

---

## 25. Декодирование — 20%

Ожидается:

```python
output = encoder.decode(output_ids)
```

Типичные ошибки:

- вернуть `output_ids`;
- вызвать `encode` вместо `decode`;
- декодировать `input_ids`;
- объединить ID через `" ".join(...)`.

---

## 26. PEP8 — 20%

Проверяются:

- длина строк;
- отступы;
- имена;
- пустые строки;
- imports;
- docstrings;
- отсутствие синтаксических ошибок.

---

# Часть IX. Production-мышление

## 27. Почему в реальной системе этого недостаточно

Учебный pipeline:

```text
prompt → encode → generate → decode
```

Production pipeline чаще выглядит так:

```text
request validation
    ↓
product data retrieval
    ↓
prompt construction
    ↓
tokenization
    ↓
context length control
    ↓
model inference
    ↓
sampling
    ↓
decode
    ↓
safety filters
    ↓
fact validation
    ↓
logging
    ↓
response
```

Нужно учитывать:

- timeouts;
- retries;
- batching;
- caching;
- GPU memory;
- malformed inputs;
- toxicity;
- hallucinations;
- observability;
- versioning модели;
- rollback.

---

## 28. Что логировать

Полезные поля:

- request ID;
- model version;
- prompt template version;
- token count;
- output token count;
- temperature;
- top-k;
- top-p;
- random seed;
- latency;
- validation result;
- moderation result;
- user feedback.

Нельзя бездумно логировать чувствительные данные:

- персональные данные;
- финансовые сведения;
- секреты;
- private messages.

---

## 29. Метрики

### Технические

- p50/p95/p99 latency;
- tokens per second;
- GPU utilization;
- error rate;
- timeout rate;
- average prompt length;
- average generated length.

### Качественные

- factual accuracy;
- relevance;
- repetition;
- format compliance;
- toxicity;
- human preference.

### Бизнесовые

- acceptance rate;
- time saved;
- seller activation;
- product publication speed;
- CTR;
- conversion;
- GMV uplift;
- cost per accepted description.

---

# Часть X. Итог

На этой странице важно понять разделение ответственности:

```text
Encoder
    текст → IDs

GPT-2
    IDs → logits

Generate
    logits → новые IDs

Decoder
    IDs → текст
```

Финальное решение требует заполнить всего три места, но за ними стоит полный inference-пайплайн языковой модели.

# Страница 7. Сборка Transformer-блока и полного GPT-2

## 1. Что происходит на этой странице

На предыдущих страницах мы по отдельности реализовали основные детали GPT-2:

1. токенизацию и обратное декодирование;
2. генерацию следующего токена;
3. линейный слой;
4. GELU;
5. Feed-Forward Network;
6. Self-Attention;
7. causal mask;
8. Multi-Head Attention.

Теперь мы собираем эти детали в законченный вычислительный граф.

Один GPT-2 decoder block имеет вид:

```text
residual stream x
    ↓
LayerNorm ln_1
    ↓
Masked Multi-Head Attention
    ↓
прибавление к residual stream
    ↓
LayerNorm ln_2
    ↓
Feed-Forward Network
    ↓
прибавление к residual stream
    ↓
output следующего блока
```

Математически:

\[
x' = x + MHA(LN_1(x))
\]

\[
x_{out} = x' + FFN(LN_2(x'))
\]

Это **Pre-LayerNorm** архитектура: нормализация применяется перед MHA и FFN.

После прохождения всех одинаковых блоков GPT-2 выполняет:

```text
final LayerNorm
    ↓
умножение на транспонированную token embedding matrix
    ↓
logits по всему словарю
    ↓
берётся строка последней позиции
```

---

# Часть I. Бизнесовый контекст

## 2. Зачем собирать модель вручную

На уровне продукта мы хотим получить сервис:

```text
описание товара и характеристики
    ↓
GPT-2
    ↓
новое SEO-описание
```

Но внутри сервиса существует длинная цепочка:

```text
строка
→ tokenizer
→ token IDs
→ token embeddings + positional embeddings
→ N Transformer blocks
→ final LayerNorm
→ vocabulary logits
→ sampling
→ новые token IDs
→ decoder
→ строка
```

Текущая страница соединяет центральную часть этой цепочки: stacked Transformer blocks и выходной vocabulary projection.

Понимание этой части важно не только для обучения. Оно позволяет ML-инженеру:

- диагностировать ошибки размерностей;
- оценивать память и вычислительную стоимость;
- понимать, какие параметры находятся в checkpoint;
- применять quantization;
- строить model server;
- реализовывать KV cache;
- понимать latency генерации;
- не путать LayerNorm, residual connections и output projection;
- корректно переносить веса между PyTorch, TensorFlow и NumPy.

---

## 3. Применение в e-commerce

Для автоматической генерации описаний товара модель получает структурированную информацию:

```text
Название: беспроводные наушники
Активное шумоподавление: да
Время работы: 30 часов
Разъём: USB-C
```

Разные блоки постепенно превращают исходные представления токенов в контекстные:

- Attention связывает характеристику с её значением;
- FFN нелинейно преобразует собранную информацию;
- residual stream сохраняет исходный сигнал;
- LayerNorm стабилизирует масштаб;
- несколько блоков формируют всё более сложные абстракции.

Бизнесовые метрики такого сервиса:

- acceptance rate сгенерированного текста продавцами;
- доля карточек без ручных исправлений;
- время от загрузки товара до публикации;
- стоимость генерации одной карточки;
- CTR карточки;
- conversion rate;
- GMV uplift;
- частота фактических ошибок;
- число жалоб и возвратов из-за неверных характеристик.

---

## 4. Fintech

Та же архитектура может использоваться для:

- объяснения статуса банковской операции;
- суммаризации обращения клиента;
- создания черновика ответа поддержки;
- извлечения контекста из договора;
- генерации понятного объяснения сложного термина.

Но для финансовых систем недостаточно хорошей генерации. Нужны:

- grounding на проверенных данных;
- deterministic validation сумм и валют;
- защита персональных данных;
- audit log;
- versioning модели;
- human-in-the-loop для критических решений;
- запрет на неподтверждённые финансовые рекомендации.

Архитектура модели отвечает за представление текста, но бизнес-правила должны жить вокруг модели.

---

## 5. Two-sided marketplaces

На площадке, соединяющей заказчика и исполнителя, GPT-подобная модель может:

- улучшать описание заказа;
- нормализовать требования;
- формировать резюме переписки;
- объяснять условия сделки;
- предлагать исполнителю черновик ответа;
- переводить сообщения.

При оптимизации нельзя смотреть только на краткосрочную конверсию. Сгенерированный текст может увеличить число откликов, но одновременно создать ложные ожидания и ухудшить completion rate.

Поэтому важны совместные метрики:

```text
conversion
+ successful completion
+ dispute rate
+ refund rate
+ repeat usage
```

---

## 6. Dating

Возможные применения:

- улучшение описания профиля;
- подсказки для начала диалога;
- перевод;
- переформулирование грубого сообщения;
- суммаризация длинной переписки;
- moderation assistance.

Риски:

- impersonation;
- harassment;
- манипулятивные сообщения;
- утечки приватных данных;
- сексуальный контент;
- мошеннические сценарии.

Здесь высокое качество Transformer не отменяет необходимость safety layer.

---

## 7. iGaming и casino

GPT-подобная система может:

- объяснять правила;
- помогать поддержке;
- локализовывать интерфейс;
- создавать информационные материалы.

Однако она не должна свободно придумывать:

- условия бонуса;
- вероятность выигрыша;
- ограничения;
- регуляторные требования.

Численные и юридические условия должны поступать из источника истины и проходить validation.

---

## 8. Crypto

Применения:

- объяснение интерфейса кошелька;
- суммаризация governance proposal;
- помощь с документацией;
- анализ описания транзакции;
- support assistant.

Критические поля нельзя генерировать по памяти модели:

- адреса;
- суммы;
- chain ID;
- комиссии;
- актуальное состояние сети;
- контрактные параметры.

---

## 9. Big Tech и промышленность

Transformer-блоки используются в системах:

- поиска;
- генерации кода;
- knowledge assistants;
- анализа инцидентов;
- документации;
- customer support;
- инженерных помощников;
- мультимодальных моделях;
- анализе телеметрии.

В промышленном контексте важны:

- latency;
- availability;
- rollback;
- validation;
- observability;
- предсказуемость;
- защита коммерческой тайны;
- ограничение автономных действий модели.

---

# Часть II. Residual stream

## 10. Что такое residual connection

Обычный слой можно представить так:

\[
y = F(x)
\]

Residual-блок:

\[
y = x + F(x)
\]

Слой не обязан полностью реконструировать новое представление. Он учится вычислять поправку к уже существующему сигналу.

В GPT-2 существует главный поток hidden states, который часто называют **residual stream**.

Attention и FFN читают этот поток и возвращают обновления:

```text
residual stream
    + attention update
    + ffn update
```

---

## 11. Интуиция residual learning

Представим текстовый embedding как текущую гипотезу о смысле токена.

На первом слое она грубая.

Attention говорит:

```text
этому токену не хватает контекста от таких-то позиций
```

FFN говорит:

```text
собранные признаки нужно нелинейно преобразовать вот так
```

Вместо полного уничтожения старого смысла каждый компонент добавляет корректировку.

Это облегчает обучение глубоких сетей.

---

## 12. Градиенты и identity path

Для:

\[
y = x + F(x)
\]

производная:

\[
\frac{dy}{dx} = I + \frac{dF(x)}{dx}
\]

В градиенте присутствует identity-компонента. Это помогает сигналу проходить через глубокую сеть и уменьшает проблему деградации при увеличении числа слоёв.

Это не означает, что residual connection полностью решает все проблемы оптимизации, но он является одной из центральных причин успешного обучения очень глубоких архитектур.

---

## 13. Почему формы должны совпадать

Для сложения:

```python
x + mha_output
```

необходимо:

```text
x.shape == mha_output.shape
```

Поэтому MHA возвращает:

```text
[n_seq, n_embd]
```

FFN временно расширяет размерность:

```text
n_embd → 4*n_embd
```

но возвращает:

```text
4*n_embd → n_embd
```

И Attention, и FFN совместимы с residual stream.

---

# Часть III. Layer Normalization

## 14. Формула

Для каждого токена нормализация выполняется по последней оси, то есть по embedding dimensions.

Среднее:

\[
\mu = \frac{1}{D}\sum_{i=1}^{D}x_i
\]

Дисперсия:

\[
\sigma^2 = \frac{1}{D}\sum_{i=1}^{D}(x_i-\mu)^2
\]

Нормированное значение:

\[
\hat{x}_i = \frac{x_i-\mu}{\sqrt{\sigma^2+\epsilon}}
\]

Обучаемый scale и bias:

\[
y_i = g_i\hat{x}_i+b_i
\]

Код:

```python
mean = np.mean(x, axis=-1, keepdims=True)
variance = np.var(x, axis=-1, keepdims=True)
x = (x - mean) / np.sqrt(variance + eps)
return g * x + b
```

---

## 15. Почему нормируется последняя ось

Вход:

```text
[n_seq, n_embd]
```

Каждая строка — один токен.

LayerNorm нормирует координаты одного токена независимо от других токенов.

Это отличается от BatchNorm, которая использует статистики по batch dimension и зависит от других объектов в batch.

---

## 16. Назначение epsilon

Если variance близка к нулю, деление может стать нестабильным.

Добавляется:

```python
eps = 1e-5
```

Это предотвращает деление на ноль и улучшает численную устойчивость.

---

## 17. Gamma и beta

После стандартизации применяются обучаемые параметры:

```python
g * x + b
```

`g` часто называют gamma.

`b` — beta.

Они позволяют модели восстановить полезный масштаб и сдвиг. Нормализация не заставляет все слои навсегда оставаться строго со средним ноль и дисперсией один после affine transformation.

---

# Часть IV. Pre-LN и Post-LN

## 18. Pre-LayerNorm GPT-2

Текущий блок:

```python
x = x + mha(layer_norm(x, **ln_1), ...)
x = x + ffn(layer_norm(x, **ln_2), ...)
```

LayerNorm применяется перед sublayer.

Это Pre-LN.

---

## 19. Ошибочный порядок

Нельзя написать:

```python
x = layer_norm(x + mha(x, ...), **ln_1)
```

Это уже другая архитектура.

Даже если формы совпадают, численные результаты будут совершенно другими и загруженные GPT-2 weights перестанут соответствовать модели.

---

## 20. Почему порядок является частью checkpoint contract

Checkpoint содержит веса, обученные для конкретного вычислительного графа.

Недостаточно иметь те же матрицы. Нужно точно воспроизвести:

- порядок LayerNorm;
- residual additions;
- порядок MHA и FFN;
- GELU-вариант;
- causal mask;
- разделение на heads;
- positional embeddings;
- финальную нормализацию;
- output projection.

Одно изменение архитектуры делает веса несовместимыми по смыслу, даже если физические формы массивов подходят.

---

# Часть V. Один Transformer block

## 21. Первый sublayer

```python
x = x + mha(
    layer_norm(x, **ln_1),
    **attn,
    n_head=n_head,
)
```

Порядок:

1. сохранить исходный `x` для residual;
2. нормировать `x` через `ln_1`;
3. передать нормированный вход в MHA;
4. получить attention update;
5. прибавить update к исходному `x`.

---

## 22. Второй sublayer

```python
x = x + ffn(
    layer_norm(x, **ln_2),
    **mlp,
)
```

Важно: здесь используется уже обновлённый после Attention `x`.

Порядок:

1. взять результат первого residual;
2. нормировать через `ln_2`;
3. вычислить FFN update;
4. прибавить его к текущему residual stream.

---

## 23. Почему нельзя использовать старый x для FFN

Неправильно:

```python
original_x = x
x = x + mha(...)
x = x + ffn(layer_norm(original_x, **ln_2), ...)
```

FFN должен обрабатывать representation, уже обогащённое Attention.

---

# Часть VI. Параметры блока

## 24. Структура block

Один элемент `blocks` имеет примерно такую структуру:

```python
{
    "ln_1": {
        "g": ...,
        "b": ...,
    },
    "attn": {
        "c_attn": {
            "w": ...,
            "b": ...,
        },
        "c_proj": {
            "w": ...,
            "b": ...,
        },
    },
    "ln_2": {
        "g": ...,
        "b": ...,
    },
    "mlp": {
        "c_fc": {
            "w": ...,
            "b": ...,
        },
        "c_proj": {
            "w": ...,
            "b": ...,
        },
    },
}
```

Поэтому вызов:

```python
transformer_block(x, n_head=n_head, **block)
```

автоматически передаёт:

```text
mlp
attn
ln_1
ln_2
```

---

## 25. Распаковка `attn`

Внутри:

```python
mha(..., **attn, n_head=n_head)
```

эквивалентно:

```python
mha(
    normalized_x,
    c_attn=attn["c_attn"],
    c_proj=attn["c_proj"],
    n_head=n_head,
)
```

---

## 26. Распаковка `mlp`

```python
ffn(..., **mlp)
```

эквивалентно:

```python
ffn(
    normalized_x,
    c_fc=mlp["c_fc"],
    c_proj=mlp["c_proj"],
)
```

---

# Часть VII. Полный GPT-2 forward pass

## 27. Token embeddings

```python
wte[inputs]
```

`wte`:

```text
[n_vocab, n_embd]
```

`inputs`:

```text
[n_seq]
```

Результат:

```text
[n_seq, n_embd]
```

---

## 28. Positional embeddings

```python
wpe[range(len(inputs))]
```

`wpe`:

```text
[n_ctx, n_embd]
```

Берутся позиции:

```text
0, 1, 2, ..., n_seq-1
```

Результат:

```text
[n_seq, n_embd]
```

---

## 29. Сложение embeddings

```python
x = wte[inputs] + wpe[range(len(inputs))]
```

Форма:

```text
[n_seq, n_embd]
```

Содержательно каждый токен получает:

- информацию о token identity;
- информацию о позиции.

---

## 30. Стек блоков

```python
for block in blocks:
    x = transformer_block(
        x,
        n_head=n_head,
        **block,
    )
```

Каждый блок имеет собственные веса, но одинаковую структуру.

GPT-2 Small содержит 12 блоков.

Более крупные варианты содержат больше блоков и более широкие embeddings.

---

## 31. Final LayerNorm

После последнего блока:

```python
x = layer_norm(x, **ln_f)
```

Это отдельная финальная нормализация.

Нельзя забывать её или заменять `ln_2` последнего блока.

---

# Часть VIII. Vocabulary projection

## 32. Logits

Нужно для каждого токена получить score каждого элемента vocabulary:

```text
hidden states: [n_seq, n_embd]
output matrix: [n_embd, n_vocab]
```

Код:

```python
logits = x @ wte.T
```

`wte.T` имеет:

```text
[n_embd, n_vocab]
```

Результат:

```text
[n_seq, n_vocab]
```

---

## 33. Weight tying

GPT-2 повторно использует одну матрицу:

```text
wte
```

Для входа:

```python
wte[token_id]
```

Для выхода:

```python
x @ wte.T
```

Это называется **weight tying**.

Преимущества:

- меньше параметров;
- входное и выходное token space согласованы;
- может улучшать статистическую эффективность обучения.

---

## 34. Почему возвращается `logits[-1]`

Полный forward создаёт logits для каждой позиции:

```text
[n_seq, n_vocab]
```

Для генерации следующего токена нужен output последней позиции:

```python
return logits[-1]
```

Форма:

```text
[n_vocab]
```

Именно этот вектор затем поступает в temperature, top-k, top-p и sampling.

---

# Часть IX. Полный generation loop

## 35. Как всё соединяется

```text
input text
 ↓
encoder.encode
 ↓
input IDs
 ↓
gpt2(input IDs)
 ↓
next-token logits
 ↓
temperature + top-k + top-p
 ↓
next token ID
 ↓
добавить ID в sequence
 ↓
повторить gpt2
 ↓
encoder.decode
 ↓
output text
```

Текущая функция `gpt2` не выбирает токен. Она возвращает logits.

Sampling остаётся отдельным компонентом.

Это хорошее разделение ответственности:

- модель вычисляет scores;
- decoding strategy выбирает конкретный output.

---

# Часть X. Размерности GPT-2 Small

## 36. Вход

```text
inputs: [n_seq]
```

## 37. Embeddings

```text
wte[inputs]: [n_seq, 768]
wpe[positions]: [n_seq, 768]
x: [n_seq, 768]
```

## 38. Attention projection

```text
c_attn: 768 → 2304
```

## 39. Heads

```text
12 heads
head dimension = 64
```

## 40. MHA output

```text
[n_seq, 768]
```

## 41. FFN

```text
768 → 3072 → 768
```

## 42. Блок

```text
[n_seq, 768] → [n_seq, 768]
```

## 43. Vocabulary logits

```text
[n_seq, 768] @ [768, 50257]
=
[n_seq, 50257]
```

## 44. Next-token logits

```text
[50257]
```

---

# Часть XI. Почему однородные блоки могут решать сложные задачи

## 45. Одинаковая структура, разные параметры

Все блоки имеют одинаковый вычислительный шаблон, но разные обученные веса.

Ранние слои часто формируют более локальные признаки.

Средние могут кодировать синтаксис и отношения сущностей.

Поздние формируют признаки, непосредственно полезные для next-token prediction.

Это не жёсткое правило «слой номер N делает только X», но полезная интуиция.

---

## 46. Глубина как итеративное уточнение

Каждый блок:

1. собирает контекст;
2. преобразует признаки;
3. добавляет обновление в residual stream.

Модель многократно уточняет hidden state каждого токена.

---

# Часть XII. Production system design

## 47. Model loading

Checkpoint должен загружаться один раз при старте worker, а не на каждый запрос.

Иначе latency будет огромной.

---

## 48. Batching

Несколько запросов можно обрабатывать совместно, но длины последовательностей различаются.

Нужны:

- padding;
- attention masks;
- scheduler;
- ограничение batch latency;
- управление GPU memory.

---

## 49. KV cache

При autoregressive inference нет необходимости пересчитывать Keys и Values предыдущих токенов на каждом шаге.

KV cache хранит их для каждого слоя.

Плюс:

- быстрее generation.

Минус:

- память растёт с длиной контекста;
- снижает максимальный concurrent batch.

---

## 50. Observability

Следует измерять:

- prompt tokens;
- output tokens;
- time to first token;
- tokens per second;
- p50/p95/p99 latency;
- GPU memory;
- model loading time;
- error rate;
- timeout rate;
- output validation failures;
- safety rejection rate.

---

## 51. Версионирование

Нужно версионировать:

- model checkpoint;
- tokenizer;
- prompt template;
- decoding parameters;
- business rules;
- safety policy;
- post-processing.

Tokenizer и weights являются связанным контрактом. Нельзя заменить vocabulary и оставить старую embedding matrix.

---

## 52. Guardrails

Для SEO-сервиса полезны:

- проверка соответствия характеристикам;
- запрет выдуманных сертификатов;
- проверка запрещённых claims;
- ограничение длины;
- проверка языка;
- blacklist слов;
- human review;
- хранение feedback продавца.

---

# Часть XIII. Критические ошибки задания

## 53. Post-LN вместо Pre-LN

Неправильно:

```python
x = layer_norm(x + mha(x, ...), **ln_1)
```

---

## 54. Забыть residual после MHA

Неправильно:

```python
x = mha(layer_norm(x, **ln_1), ...)
```

Это уничтожит residual stream.

---

## 55. Забыть residual после FFN

Неправильно:

```python
x = ffn(layer_norm(x, **ln_2), ...)
```

---

## 56. Нормировать старый x перед FFN

FFN должен получать LayerNorm от representation после Attention residual.

---

## 57. Поменять ln_1 и ln_2

У них разные обученные параметры.

---

## 58. Поменять attn и mlp местами

Checkpoint обучался с конкретным порядком.

---

## 59. Забыть final LayerNorm

```python
x = layer_norm(x, **ln_f)
```

является частью GPT-2 forward pass.

---

## 60. Использовать отдельную случайную output matrix

В условии output projection:

```python
x @ wte.T
```

---

## 61. Вернуть все позиции

Задание ожидает next-token logits:

```python
return logits[-1]
```

---

## 62. Изменить API

Нельзя менять сигнатуры:

```python
transformer_block(x, mlp, attn, ln_1, ln_2, n_head)
```

```python
gpt2(inputs, wte, wpe, blocks, ln_f, n_head)
```

---

# Часть XIV. Интервью

## 63. Что такое residual stream?

Residual stream — основной hidden-state поток Transformer. Attention и FFN добавляют к нему обучаемые обновления, вместо полной замены representation.

## 64. Почему GPT-2 использует Pre-LN?

LayerNorm применяется перед MHA и FFN. Такой порядок является частью архитектуры и помогает стабильному прохождению сигнала и градиентов в глубоких сетях.

## 65. Что такое weight tying?

Одна token embedding matrix используется как lookup table на входе и в транспонированном виде как output projection на vocabulary.

## 66. Почему возвращаются logits последнего токена?

В autoregressive generation следующий токен определяется на основе hidden state последней доступной позиции.

## 67. Чем logits отличаются от probabilities?

Logits — ненормированные scores. Для probabilities применяется Softmax, возможно после temperature и filtering.

---

# Часть XV. Итоговая ментальная модель

```text
EMBEDDINGS
token meaning + position

BLOCK 1
normalize → communicate through MHA → add update
normalize → think through FFN → add update

BLOCK 2
то же самое с другими весами

...

FINAL LAYERNORM
стабилизировать representation

WTE TRANSPOSE
сравнить hidden state со всеми token embeddings

LAST POSITION
получить next-token logits
```

Ключевой код страницы:

```python
x = x + mha(
    layer_norm(x, **ln_1),
    **attn,
    n_head=n_head,
)

x = x + ffn(
    layer_norm(x, **ln_2),
    **mlp,
)
```

Это и есть один полный GPT-2 Transformer block.

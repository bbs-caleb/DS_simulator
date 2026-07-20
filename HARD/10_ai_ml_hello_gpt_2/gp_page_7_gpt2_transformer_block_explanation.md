# Страница 7. Пошаговое объяснение сборки GPT-2

## 1. Что загружать в проверяющую систему

Нужно отправить Python-файл:

```text
gp_page_7_gpt2_transformer_block_solution.py
```

В нём находится полный код из шаблона и заполнены два пропуска функции `transformer_block`.

Главное решение:

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

Дальше разберём буквально каждую часть.

---

# Часть I. Полный код

```python
"""Minimal NumPy implementation of a GPT-2 forward pass."""

import numpy as np


def gelu(x):
    """Apply the GELU activation used in GPT-2."""
    return 0.5 * x * (
        1
        + np.tanh(
            np.sqrt(2 / np.pi)
            * (x + 0.044715 * x**3)
        )
    )


def layer_norm(x, g, b, eps: float = 1e-5):
    """Normalize the last axis and apply scale and bias."""
    mean = np.mean(x, axis=-1, keepdims=True)
    variance = np.var(x, axis=-1, keepdims=True)
    x = (x - mean) / np.sqrt(variance + eps)
    return g * x + b


def ffn(x, c_fc, c_proj):
    """Apply the position-wise feed-forward network."""
    hidden = gelu(linear(x, **c_fc))
    return linear(hidden, **c_proj)


def linear(x, w, b):
    """Apply a linear transformation."""
    return x @ w + b


def softmax(x):
    """Apply a numerically stable softmax."""
    exp_x = np.exp(
        x - np.max(
            x,
            axis=-1,
            keepdims=True,
        )
    )
    return exp_x / np.sum(
        exp_x,
        axis=-1,
        keepdims=True,
    )


def attention(q, k, v, mask):
    """Apply masked scaled dot-product attention."""
    scores = q @ k.T / np.sqrt(q.shape[-1])
    return softmax(scores + mask) @ v


def mha(x, c_attn, c_proj, n_head):
    """Apply masked multi-head self-attention."""
    x = linear(x, **c_attn)
    qkv = np.split(x, 3, axis=-1)

    qkv_heads = [
        np.split(part, n_head, axis=-1)
        for part in qkv
    ]

    causal_mask = (1 - np.tri(x.shape[0])) * -1e10

    out_heads = [
        attention(q, k, v, causal_mask)
        for q, k, v in zip(*qkv_heads)
    ]

    x = np.hstack(out_heads)
    return linear(x, **c_proj)


def transformer_block(
    x,
    mlp,
    attn,
    ln_1,
    ln_2,
    n_head,
):
    """Apply one pre-layer-normalized GPT-2 decoder block."""
    x = x + mha(
        layer_norm(x, **ln_1),
        **attn,
        n_head=n_head,
    )
    x = x + ffn(
        layer_norm(x, **ln_2),
        **mlp,
    )
    return x


def gpt2(inputs, wte, wpe, blocks, ln_f, n_head):
    """Run GPT-2 and return logits for the next token."""
    x = wte[inputs] + wpe[range(len(inputs))]

    for block in blocks:
        x = transformer_block(
            x,
            n_head=n_head,
            **block,
        )

    x = layer_norm(x, **ln_f)
    logits = x @ wte.T

    return logits[-1]
```

---

# Часть II. Функция `gelu`

## 2. Заголовок

```python
def gelu(x):
```

Функция принимает число или NumPy-массив.

Операции выполняются поэлементно.

---

## 3. Формула

```python
return 0.5 * x * (
    1
    + np.tanh(
        np.sqrt(2 / np.pi)
        * (x + 0.044715 * x**3)
    )
)
```

Это tanh-аппроксимация GELU, используемая GPT-2.

GELU находится между полностью жёстким ReLU и плавным gating.

Она не меняет форму массива.

Пример:

```text
x.shape = [n_seq, 4*n_embd]
```

После GELU:

```text
[n_seq, 4*n_embd]
```

---

# Часть III. Функция `layer_norm`

## 4. Сигнатура

```python
def layer_norm(x, g, b, eps: float = 1e-5):
```

Аргументы:

- `x` — hidden states;
- `g` — gamma, обучаемый scale;
- `b` — beta, обучаемый bias;
- `eps` — небольшое число для стабильности.

---

## 5. Среднее

```python
mean = np.mean(x, axis=-1, keepdims=True)
```

Предположим:

```text
x.shape = [5, 768]
```

`axis=-1` означает вычисление среднего по 768 embedding coordinates каждого токена.

Форма `mean`:

```text
[5, 1]
```

Благодаря `keepdims=True` среднее можно вычесть из `x` через broadcasting.

---

## 6. Дисперсия

```python
variance = np.var(x, axis=-1, keepdims=True)
```

Форма:

```text
[5, 1]
```

Каждый токен получает собственную variance.

---

## 7. Стандартизация

```python
x = (x - mean) / np.sqrt(variance + eps)
```

### `x - mean`

Центрирует embedding около нуля.

### `variance + eps`

Защищает от нулевой дисперсии.

### `np.sqrt`

Превращает variance в standard deviation.

### Деление

Приводит координаты примерно к единичной дисперсии.

---

## 8. Gamma и beta

```python
return g * x + b
```

`g` и `b` имеют форму:

```text
[n_embd]
```

NumPy распространяет их по всем токенам.

Это обучаемое affine transformation после стандартизации.

---

# Часть IV. Функция `ffn`

## 9. Первый linear

```python
linear(x, **c_fc)
```

`c_fc`:

```python
{
    "w": ...,  # [n_embd, 4*n_embd]
    "b": ...,  # [4*n_embd]
}
```

Форма меняется:

```text
[n_seq, n_embd]
→
[n_seq, 4*n_embd]
```

---

## 10. GELU

```python
hidden = gelu(linear(x, **c_fc))
```

Добавляется нелинейность.

---

## 11. Projection

```python
return linear(hidden, **c_proj)
```

`c_proj` возвращает форму:

```text
[n_seq, 4*n_embd]
→
[n_seq, n_embd]
```

Это необходимо для residual addition.

---

# Часть V. `linear`, `softmax`, `attention`, `mha`

Эти функции уже были реализованы на предыдущих страницах, но остаются в полном файле, потому что `transformer_block` вызывает `mha`, а `mha` зависит от остальных функций.

## 12. Linear

```python
return x @ w + b
```

## 13. Stable Softmax

```python
exp_x = np.exp(
    x - np.max(x, axis=-1, keepdims=True)
)
```

Вычитание максимума предотвращает overflow.

## 14. Masked Attention

```python
scores = q @ k.T / np.sqrt(q.shape[-1])
return softmax(scores + mask) @ v
```

## 15. MHA

```text
QKV projection
→ split Q/K/V
→ split heads
→ causal Attention каждой головы
→ hstack
→ c_proj
```

---

# Часть VI. Главная функция `transformer_block`

## 16. Сигнатура

```python
def transformer_block(
    x,
    mlp,
    attn,
    ln_1,
    ln_2,
    n_head,
):
```

### `x`

Текущий residual stream:

```text
[n_seq, n_embd]
```

### `mlp`

Параметры FFN:

```python
{
    "c_fc": {...},
    "c_proj": {...},
}
```

### `attn`

Параметры MHA:

```python
{
    "c_attn": {...},
    "c_proj": {...},
}
```

### `ln_1`

Параметры первой LayerNorm.

### `ln_2`

Параметры второй LayerNorm.

### `n_head`

Число attention heads.

---

# Часть VII. Первый residual sublayer

## 17. Внутренняя часть

```python
layer_norm(x, **ln_1)
```

Сначала нормируется исходный residual stream.

Оператор `**ln_1` раскрывает:

```python
layer_norm(
    x,
    g=ln_1["g"],
    b=ln_1["b"],
)
```

---

## 18. Передача в MHA

```python
mha(
    layer_norm(x, **ln_1),
    **attn,
    n_head=n_head,
)
```

Распаковка `**attn`:

```python
mha(
    normalized_x,
    c_attn=attn["c_attn"],
    c_proj=attn["c_proj"],
    n_head=n_head,
)
```

MHA возвращает:

```text
[n_seq, n_embd]
```

---

## 19. Residual addition

```python
x = x + mha(...)
```

Левая часть сложения — старый residual stream.

Правая — attention update.

Формы совпадают.

После операции переменная `x` уже содержит обновлённое представление.

---

## 20. Почему не нужно сохранять отдельную копию

Python сначала полностью вычисляет правую часть:

```python
mha(layer_norm(x, ...), ...)
```

В этот момент `x` всё ещё старый.

Только после этого выполняется сложение и присваивание.

Поэтому строка:

```python
x = x + mha(...)
```

корректно реализует residual connection.

---

# Часть VIII. Второй residual sublayer

## 21. LayerNorm от обновлённого x

```python
layer_norm(x, **ln_2)
```

Здесь `x` уже содержит результат Attention residual.

Это принципиально важно.

---

## 22. FFN

```python
ffn(
    layer_norm(x, **ln_2),
    **mlp,
)
```

Распаковка:

```python
ffn(
    normalized_x,
    c_fc=mlp["c_fc"],
    c_proj=mlp["c_proj"],
)
```

---

## 23. Второй residual

```python
x = x + ffn(...)
```

FFN update прибавляется к representation после Attention.

---

## 24. Возврат

```python
return x
```

Форма:

```text
[n_seq, n_embd]
```

Она совпадает с входом, поэтому следующий block может использовать тот же API.

---

# Часть IX. Почему это Pre-LN

## 25. Фактический порядок

```text
LayerNorm
→ sublayer
→ residual addition
```

Для MHA:

```python
x + mha(layer_norm(x))
```

Для FFN:

```python
x + ffn(layer_norm(x))
```

---

## 26. Post-LN выглядел бы иначе

```python
x = layer_norm(
    x + mha(x, ...),
    **ln_1,
)
```

Это не GPT-2 block из задания.

---

# Часть X. Функция `gpt2`

## 27. Сигнатура

```python
def gpt2(inputs, wte, wpe, blocks, ln_f, n_head):
```

### `inputs`

Список token IDs.

### `wte`

Token embedding matrix.

### `wpe`

Position embedding matrix.

### `blocks`

Список словарей с параметрами Transformer blocks.

### `ln_f`

Final LayerNorm parameters.

### `n_head`

Число heads.

---

# Часть XI. Embedding lookup

## 28. Token embeddings

```python
wte[inputs]
```

Пример:

```python
inputs = [5, 18, 5]
```

NumPy выбирает строки:

```text
wte[5]
wte[18]
wte[5]
```

Форма:

```text
[3, n_embd]
```

---

## 29. Position embeddings

```python
wpe[range(len(inputs))]
```

При трёх токенах:

```python
range(3)
```

означает позиции:

```text
0, 1, 2
```

---

## 30. Сложение

```python
x = wte[inputs] + wpe[range(len(inputs))]
```

Token и positional vectors имеют одинаковую форму.

Каждая позиция получает сумму двух embeddings.

---

# Часть XII. Цикл по блокам

## 31. `for block in blocks`

```python
for block in blocks:
```

Количество итераций равно числу Transformer layers.

---

## 32. Вызов

```python
x = transformer_block(
    x,
    n_head=n_head,
    **block,
)
```

Пусть `block` содержит:

```python
{
    "mlp": mlp_params,
    "attn": attention_params,
    "ln_1": first_norm_params,
    "ln_2": second_norm_params,
}
```

После распаковки Python вызывает:

```python
transformer_block(
    x,
    mlp=mlp_params,
    attn=attention_params,
    ln_1=first_norm_params,
    ln_2=second_norm_params,
    n_head=n_head,
)
```

Это и есть «GPT-2 корректно распаковывает параметры» из условия.

---

## 33. Почему `n_head` отдельно

`n_head` является общим архитектурным hyperparameter.

Он не обязательно хранится внутри каждого `block`.

Поэтому передаётся явно:

```python
n_head=n_head
```

---

# Часть XIII. Финальная LayerNorm

## 34. Строка

```python
x = layer_norm(x, **ln_f)
```

Она выполняется один раз после всех blocks.

`ln_f` не заменяет `ln_1` и `ln_2`.

Это отдельный набор gamma и beta.

---

# Часть XIV. Vocabulary projection

## 35. Транспонирование wte

```python
wte.T
```

Исходная форма:

```text
[n_vocab, n_embd]
```

После `.T`:

```text
[n_embd, n_vocab]
```

---

## 36. Умножение

```python
logits = x @ wte.T
```

Формы:

```text
[n_seq, n_embd]
@
[n_embd, n_vocab]
=
[n_seq, n_vocab]
```

Для каждой позиции создаётся score каждого token ID.

---

## 37. Почему это не Softmax

Функция возвращает logits.

Softmax и sampling применяются в generation logic.

Это позволяет выбирать разные decoding strategies:

- greedy;
- temperature;
- top-k;
- top-p.

---

# Часть XV. Последняя позиция

## 38. `logits[-1]`

```python
return logits[-1]
```

Индекс `-1` означает последнюю строку.

Если:

```text
logits.shape = [7, 50257]
```

то:

```text
logits[-1].shape = [50257]
```

Это scores следующего токена после всей текущей последовательности.

---

# Часть XVI. Ручная проверка Transformer block

## 39. Reference calculation

Можно вычислить expected result отдельно:

```python
attention_input = layer_norm(
    x,
    **ln_1,
)

attention_update = mha(
    attention_input,
    **attn,
    n_head=n_head,
)

x_after_attention = x + attention_update

ffn_input = layer_norm(
    x_after_attention,
    **ln_2,
)

ffn_update = ffn(
    ffn_input,
    **mlp,
)

expected = x_after_attention + ffn_update
```

И сравнить:

```python
actual = transformer_block(
    x,
    mlp,
    attn,
    ln_1,
    ln_2,
    n_head,
)

assert np.allclose(actual, expected)
```

---

# Часть XVII. Проверка LayerNorm

## 40. Без gamma и beta

Если:

```python
g = np.ones(n_embd)
b = np.zeros(n_embd)
```

то после LayerNorm среднее каждой строки должно быть близко к нулю:

```python
normalized.mean(axis=-1)
```

Дисперсия должна быть близка к единице, с небольшой поправкой из-за epsilon.

---

# Часть XVIII. Проверка output shape

## 41. Маленькая модель

Пусть:

```text
n_vocab = 11
n_embd = 4
n_head = 2
```

После:

```python
logits = gpt2(...)
```

ожидаем:

```text
logits.shape == (11,)
```

Потому что функция возвращает scores по всему vocabulary для следующего токена.

---

# Часть XIX. Типичные неправильные реализации

## 42. Без residual

Неправильно:

```python
x = mha(layer_norm(x, **ln_1), ...)
x = ffn(layer_norm(x, **ln_2), ...)
```

Старый signal полностью теряется.

---

## 43. LayerNorm после sublayer

Неправильно:

```python
x = layer_norm(
    x + mha(x, ...),
    **ln_1,
)
```

---

## 44. Одновременное вычисление updates

Неправильно:

```python
attention_update = mha(layer_norm(x, **ln_1), ...)
ffn_update = ffn(layer_norm(x, **ln_2), ...)
x = x + attention_update + ffn_update
```

FFN должен увидеть уже обновлённый после MHA `x`.

---

## 45. Использовать ln_1 дважды

Неправильно:

```python
x = x + ffn(layer_norm(x, **ln_1), **mlp)
```

У FFN свой `ln_2`.

---

## 46. Пропустить final ln_f

Это изменит logits.

---

## 47. Умножить на wte вместо wte.T

Неправильно:

```python
x @ wte
```

Формы несовместимы.

---

## 48. Вернуть Softmax probabilities

Задание ожидает logits.

Не нужно:

```python
return softmax(logits[-1])
```

---

## 49. Вернуть `logits`

Это будет матрица для всех позиций.

Нужно:

```python
return logits[-1]
```

---

## 50. Создать отдельную output weight matrix

В шаблоне используется weight tying через `wte.T`.

---

# Часть XX. Как тесты могут проверять решение

## 51. Monkeypatch LayerNorm

Тест может заменить `layer_norm` на функцию, записывающую порядок вызовов.

Он увидит:

```text
ln_1 → mha → residual → ln_2 → ffn → residual
```

---

## 52. Identity sublayers

Если MHA и FFN возвращают нули:

```text
transformer_block(x) == x
```

Это проверяет residual path.

---

## 53. Constant updates

Если MHA возвращает `A`, FFN возвращает `B`, результат должен быть:

```text
x + A + B
```

Но вход FFN должен строиться от `x + A`.

---

## 54. Параметры block

Тест может передать словари с ожидаемыми ключами и проверить, что `**block`, `**attn`, `**mlp`, `**ln_1`, `**ln_2` распаковываются без ошибок.

---

## 55. Форма logits

Тест проверит:

```text
[n_vocab]
```

---

## 56. Weight tying

Тест может сравнить output с ручным:

```python
layer_norm_result @ wte.T
```

---

# Часть XXI. Сложность

## 57. Один блок

Основные расходы:

- QKV projection;
- Attention matrix;
- output projection;
- FFN expansion и contraction.

Attention имеет квадратичную зависимость от длины последовательности.

FFN обычно содержит большую долю параметров и значительное число FLOPs.

---

## 58. Стек блоков

Если блоков `L`, вычисления примерно линейно растут с `L`:

```text
cost ≈ L × cost_of_one_block
```

---

## 59. Vocabulary projection

Последнее умножение:

```text
[n_seq, n_embd] @ [n_embd, n_vocab]
```

также дорого при большом vocabulary.

Для generation можно вычислять только последнюю позицию при наличии оптимизированного inference path и KV cache.

---

# Часть XXII. Что рассказать на собеседовании

## 60. Один GPT-2 block

> GPT-2 block использует Pre-LayerNorm. Сначала нормированный residual stream проходит через masked multi-head self-attention, результат прибавляется к residual. Затем обновлённый stream снова нормируется, проходит position-wise FFN и также прибавляется residual connection.

## 61. Полный GPT-2 forward

> Token и positional embeddings складываются, проходят через стек одинаковых по архитектуре blocks с разными весами, затем через final LayerNorm. Hidden states проецируются на vocabulary с помощью транспонированной token embedding matrix. Для next-token generation берутся logits последней позиции.

## 62. Зачем residual

> Sublayers учатся вычислять обновления к текущему representation. Identity path облегчает обучение глубоких сетей и прохождение градиента.

## 63. Зачем LayerNorm

> LayerNorm стабилизирует масштаб hidden states по embedding dimension каждого токена. Gamma и beta позволяют обучаемо восстановить нужный scale и shift.

## 64. Что такое weight tying

> Одна матрица используется как token embedding lookup и как output classifier в транспонированном виде.

---

# Часть XXIII. Финальная памятка

Запомните две строки:

```python
x = x + mha(
    layer_norm(x, **ln_1),
    **attn,
    n_head=n_head,
)
```

```python
x = x + ffn(
    layer_norm(x, **ln_2),
    **mlp,
)
```

Расшифровка:

```text
1. normalize
2. transform
3. add residual
4. normalize updated stream
5. transform
6. add residual
```

После stacking:

```text
final LayerNorm
→ x @ wte.T
→ logits[-1]
```

Это завершает минимальную NumPy-реализацию GPT-2 forward pass.

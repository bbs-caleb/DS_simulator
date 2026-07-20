# Страница 6. Пошаговое объяснение Masked Multi-Head Attention

## 1. Файл для отправки

```text
gp_page_6_gpt2_masked_multi_head_attention_solution.py
```

В нём должны остаться функции с исходным API:

```python
linear(x, w, b)
softmax(x)
attention(q, k, v, mask)
causal_self_attention(x, c_attn, c_proj)
mha(x, c_attn, c_proj, n_head)
```

Нельзя переименовывать функции или менять порядок аргументов.

---

# 2. Полный код

```python
"""Masked multi-head attention components for GPT-2."""

import numpy as np


def linear(x, w, b):
    """Apply a linear transformation to the input."""
    return x @ w + b


def softmax(x):
    """Apply a numerically stable softmax over the last axis."""
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


def causal_self_attention(x, c_attn, c_proj):
    """Apply single-head causal self-attention."""
    x = linear(x, **c_attn)
    q, k, v = np.split(x, 3, axis=-1)

    causal_mask = (1 - np.tri(x.shape[0])) * -1e10

    x = attention(q, k, v, causal_mask)
    return linear(x, **c_proj)


def mha(x, c_attn, c_proj, n_head):
    """Apply masked multi-head self-attention."""
    x = linear(x, **c_attn)
    qkv = np.split(x, 3, axis=-1)

    split_qkv = [
        np.split(part, n_head, axis=-1)
        for part in qkv
    ]
    qkv_heads = list(zip(*split_qkv))

    causal_mask = (1 - np.tri(x.shape[0])) * -1e10

    out_heads = [
        attention(q, k, v, causal_mask)
        for q, k, v in qkv_heads
    ]

    x = np.hstack(out_heads)
    return linear(x, **c_proj)
```

---

# 3. Разбор `attention`

## Заголовок

```python
def attention(q, k, v, mask):
```

Входы:

```text
q: [n_q, d_k]
k: [n_k, d_k]
v: [n_k, d_v]
mask: [n_q, n_k]
```

Выход:

```text
[n_q, d_v]
```

---

## Scores

```python
scores = q @ k.T / np.sqrt(q.shape[-1])
```

### `k.T`

Если:

```text
k: [n_k, d_k]
```

то:

```text
k.T: [d_k, n_k]
```

### Матричное умножение

```text
[n_q, d_k] @ [d_k, n_k]
=
[n_q, n_k]
```

Каждый Query сравнивается с каждым Key.

### Масштаб

```python
np.sqrt(q.shape[-1])
```

`q.shape[-1]` — размер одной головы `d_k`.

В Multi-Head Attention это не вся размерность embedding, а размерность конкретной головы.

---

## Прибавление mask

```python
scores + mask
```

Разрешённая позиция:

```text
score + 0
```

Будущая позиция:

```text
score - 1e10
```

---

## Softmax и Values

```python
return softmax(scores + mask) @ v
```

После Softmax каждая строка — распределение внимания по доступным Keys.

Умножение на `v` создаёт взвешенную сумму Values.

---

# 4. Разбор causal mask

```python
causal_mask = (1 - np.tri(x.shape[0])) * -1e10
```

Пусть:

```python
x.shape[0] == 3
```

Тогда:

```python
np.tri(3)
```

равно:

```text
[
    [1, 0, 0],
    [1, 1, 0],
    [1, 1, 1],
]
```

После:

```python
1 - np.tri(3)
```

получается:

```text
[
    [0, 1, 1],
    [0, 0, 1],
    [0, 0, 0],
]
```

После умножения:

```text
[
    [0, -1e10, -1e10],
    [0,     0, -1e10],
    [0,     0,     0],
]
```

Первая позиция видит только себя.

Вторая — первую и себя.

Третья — все три позиции.

---

# 5. Разбор `causal_self_attention`

## QKV projection

```python
x = linear(x, **c_attn)
```

`c_attn` — словарь:

```python
{
    "w": weight,
    "b": bias,
}
```

Оператор `**` превращает вызов в:

```python
linear(
    x,
    w=c_attn["w"],
    b=c_attn["b"],
)
```

Форма меняется:

```text
[n_seq, n_embd]
→
[n_seq, 3*n_embd]
```

---

## QKV split

```python
q, k, v = np.split(x, 3, axis=-1)
```

Последняя ось делится на три равные части.

Получаем:

```text
q: [n_seq, n_embd]
k: [n_seq, n_embd]
v: [n_seq, n_embd]
```

---

## Masked attention

```python
x = attention(q, k, v, causal_mask)
```

Форма остаётся:

```text
[n_seq, n_embd]
```

---

## Output projection

```python
return linear(x, **c_proj)
```

Она подготавливает результат к residual connection следующего уровня.

Residual здесь не прибавляется. Он будет реализован внутри Transformer block.

---

# 6. Разбор `mha`

## Общая QKV projection

```python
x = linear(x, **c_attn)
```

GPT-2 хранит Q, K и V в одной объединённой проекции.

---

## Split QKV

```python
qkv = np.split(x, 3, axis=-1)
```

Результат:

```python
qkv[0]  # Q
qkv[1]  # K
qkv[2]  # V
```

Каждый массив:

```text
[n_seq, n_embd]
```

---

# 7. Деление Q/K/V на головы

```python
split_qkv = [
    np.split(part, n_head, axis=-1)
    for part in qkv
]
```

Рассмотрим:

```text
n_embd = 8
n_head = 2
```

Размер головы:

```text
d_head = 4
```

Каждая матрица:

```text
[n_seq, 8]
```

делится на:

```text
[
    [n_seq, 4],
    [n_seq, 4],
]
```

---

## Эквивалент через цикл

```python
split_qkv = []

for part in qkv:
    heads = np.split(
        part,
        n_head,
        axis=-1,
    )
    split_qkv.append(heads)
```

List comprehension короче, но выполняет то же самое.

---

# 8. Почему структура ещё неудобна

После split:

```text
split_qkv = [
    [q0, q1],
    [k0, k1],
    [v0, v1],
]
```

Для Attention нужна структура:

```text
[
    (q0, k0, v0),
    (q1, k1, v1),
]
```

---

# 9. `zip(*split_qkv)`

```python
qkv_heads = list(zip(*split_qkv))
```

Оператор `*` раскрывает список:

```python
zip(
    split_qkv[0],
    split_qkv[1],
    split_qkv[2],
)
```

`zip` берёт элементы с одинаковой позицией.

Итерация 1:

```text
q0, k0, v0
```

Итерация 2:

```text
q1, k1, v1
```

`zip` возвращает iterator, поэтому применяется `list`.

Итоговый тип:

```text
List[tuple]
```

Это прямо соответствует формулировке задания.

---

# 10. Causal mask в MHA

```python
causal_mask = (1 - np.tri(x.shape[0])) * -1e10
```

После QKV-проекции:

```text
x.shape[0] == n_seq
```

Маска имеет:

```text
[n_seq, n_seq]
```

Она подходит каждой голове, потому что число токенов одинаково.

---

# 11. Attention для каждой головы

```python
out_heads = [
    attention(q, k, v, causal_mask)
    for q, k, v in qkv_heads
]
```

Каждый tuple автоматически распаковывается:

```python
q, k, v
```

Выполняется отдельный Attention.

Результат одной головы:

```text
[n_seq, d_head]
```

---

# 12. Объединение

```python
x = np.hstack(out_heads)
```

При двух головах:

```text
head0: [n_seq, 4]
head1: [n_seq, 4]
```

Результат:

```text
[n_seq, 8]
```

То есть исходная hidden dimension восстановлена.

---

# 13. Output projection MHA

```python
return linear(x, **c_proj)
```

Output projection:

- смешивает признаки голов;
- сохраняет `n_embd`;
- позволяет добавить результат к residual stream.

---

# 14. Ручной пример маски

Пусть есть Values:

```text
v0 = [10]
v1 = [20]
v2 = [30]
```

Для первого токена маска разрешает только `v0`.

Даже если score для `v2` огромный, после добавления `-1e10` его вероятность становится нулевой.

Первый output:

```text
[10]
```

Для последнего токена разрешены все Values, поэтому его output может быть смесью:

```text
a0*v0 + a1*v1 + a2*v2
```

---

# 15. Проверка отсутствия утечки

Можно изменить Value будущего токена:

```python
v_changed = v.copy()
v_changed[-1] += 1_000_000
```

После этого:

- outputs ранних позиций не должны измениться;
- output последней позиции может измениться.

Это прямой тест причинности.

---

# 16. Локальная проверка формы MHA

```python
import numpy as np

rng = np.random.default_rng(42)

n_seq = 5
n_embd = 8
n_head = 2

x = rng.normal(
    size=(n_seq, n_embd)
)

c_attn = {
    "w": rng.normal(
        size=(n_embd, 3*n_embd)
    ),
    "b": rng.normal(
        size=(3*n_embd,)
    ),
}

c_proj = {
    "w": rng.normal(
        size=(n_embd, n_embd)
    ),
    "b": rng.normal(
        size=(n_embd,)
    ),
}

result = mha(
    x,
    c_attn,
    c_proj,
    n_head,
)

assert result.shape == x.shape
```

---

# 17. Типичные ошибки

## Маска после Softmax

Неправильно:

```python
softmax(scores) + mask
```

Правильно:

```python
softmax(scores + mask)
```

---

## Scale по полной размерности

Внутри головы нужно:

```python
np.sqrt(q.shape[-1])
```

Не:

```python
np.sqrt(n_embd)
```

---

## Split по axis=0

Неправильно:

```python
np.split(part, n_head, axis=0)
```

Это разделит токены.

Правильно:

```python
axis=-1
```

---

## Неправильная группировка

Нельзя соединить:

```text
q0, k1, v0
```

Каждая голова использует части с одним индексом.

---

## `np.vstack`

Неправильно:

```python
np.vstack(out_heads)
```

Получится слишком много строк.

---

## Сумма голов

Неправильно:

```python
sum(out_heads)
```

Hidden dimension не восстановится.

---

## Output projection до merge

`c_proj` применяется после `np.hstack`.

---

# 18. Соответствие баллам

## 60% — causal attention

```python
scores = q @ k.T / np.sqrt(q.shape[-1])
return softmax(scores + mask) @ v
```

и:

```python
causal_mask = (1 - np.tri(x.shape[0])) * -1e10
```

## 40% — MHA

```python
split_qkv = [
    np.split(part, n_head, axis=-1)
    for part in qkv
]
```

```python
qkv_heads = list(zip(*split_qkv))
```

```python
out_heads = [...]
```

```python
x = np.hstack(out_heads)
```

---

# 19. Вопросы на интервью

## Зачем mask добавлять до Softmax?

Softmax должен перераспределить вероятность только между разрешёнными токенами. Большой отрицательный logit превращается в практически нулевую вероятность.

## Почему heads делят embedding?

Это позволяет нескольким независимым Attention-механизмам анализировать разные подпространства признаков, сохраняя общую вычислительную размерность.

## Почему головы конкатенируются?

Каждая голова создаёт разные признаки. Конкатенация сохраняет их отдельно до обучаемого смешивания через output projection.

## Какие tensors хранит KV cache?

Keys и Values каждого прошлого токена на каждом слое и в каждой голове.

---

# 20. Финальная цепочка размерностей

Пусть:

```text
n_seq = N
n_embd = D
n_head = H
d_head = D/H
```

Тогда:

```text
x:                     [N, D]
Linear c_attn:         [N, 3D]
Q, K, V:               3 × [N, D]
Q/K/V heads:           3 × H × [N, D/H]
one head attention:    [N, D/H]
all head outputs:      H × [N, D/H]
np.hstack:             [N, D]
Linear c_proj:         [N, D]
```

Это полный Masked Multi-Head Attention GPT-2.

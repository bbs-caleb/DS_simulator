# Страница 5. Пошаговый разбор решения Self-Attention

## 1. Файл для отправки

В проверяющую систему загружается:

```text
gp_page_5_gpt2_self_attention_softmax_qkv_solution.py
```

В нём должны остаться четыре функции:

```python
linear
softmax
attention
self_attention
```

---

## 2. Полный код

```python
"""Self-attention components for GPT-2."""

import numpy as np


def linear(x, w, b):
    """Apply a linear transformation to the input."""
    return x @ w + b


def softmax(x):
    """Apply a numerically stable softmax over the last axis."""
    shifted_x = x - np.max(x, axis=-1, keepdims=True)
    exp_x = np.exp(shifted_x)
    return exp_x / np.sum(exp_x, axis=-1, keepdims=True)


def attention(q, k, v):
    """Apply scaled dot-product attention."""
    scores = q @ k.T / np.sqrt(q.shape[-1])
    return softmax(scores) @ v


def self_attention(x, c_attn, c_proj):
    """Apply GPT-2 single-head self-attention."""
    x = linear(x, **c_attn)
    q, k, v = np.split(x, 3, axis=-1)
    x = attention(q, k, v)
    return linear(x, **c_proj)
```

---

## 3. `linear`

```python
def linear(x, w, b):
    return x @ w + b
```

`@` означает матричное умножение. Если:

```text
x: [m, in]
w: [in, out]
b: [out]
```

то:

```text
x @ w + b: [m, out]
```

Bias прибавляется к каждой строке через broadcasting.

---

## 4. `softmax`

### Заголовок

```python
def softmax(x):
```

Для Attention `x` обычно имеет форму:

```text
[n_q, n_k]
```

Каждая строка — scores одного Query по всем Keys.

### Вычитание максимума

```python
shifted_x = x - np.max(x, axis=-1, keepdims=True)
```

`axis=-1` означает последнюю ось. Для матрицы максимум вычисляется отдельно в каждой строке.

`keepdims=True` сохраняет форму `[n_q, 1]`.

Пример:

```text
[1000, 999, 998]
```

после вычитания максимума:

```text
[0, -1, -2]
```

Это предотвращает переполнение `np.exp`.

### Экспонента

```python
exp_x = np.exp(shifted_x)
```

Все элементы становятся положительными.

### Нормализация

```python
return exp_x / np.sum(exp_x, axis=-1, keepdims=True)
```

Каждая строка делится на собственную сумму. Поэтому сумма строки равна 1.

### Почему результат не меняется от сдвига

\[
\frac{e^{x_i-c}}{\sum_j e^{x_j-c}}
=
\frac{e^{x_i}e^{-c}}{e^{-c}\sum_j e^{x_j}}
=
\frac{e^{x_i}}{\sum_j e^{x_j}}
\]

---

## 5. Ручной Softmax

Пусть:

```text
x = [2, 1, 0]
```

После сдвига:

```text
[0, -1, -2]
```

Экспоненты:

```text
[1.0000, 0.3679, 0.1353]
```

Сумма:

```text
1.5032
```

Вероятности:

```text
[0.6652, 0.2447, 0.0900]
```

---

## 6. `attention`

```python
def attention(q, k, v):
    scores = q @ k.T / np.sqrt(q.shape[-1])
    return softmax(scores) @ v
```

### Формы входа

```text
q: [n_q, d_k]
k: [n_k, d_k]
v: [n_k, d_v]
```

### Транспонирование Key

```python
k.T
```

Меняет:

```text
[n_k, d_k]
```

на:

```text
[d_k, n_k]
```

### Матрица scores

```python
q @ k.T
```

Формы:

```text
[n_q, d_k] @ [d_k, n_k] = [n_q, n_k]
```

Каждый Query сравнивается с каждым Key.

### Scale

```python
np.sqrt(q.shape[-1])
```

`q.shape[-1]` — это `d_k`.

Полная строка:

```python
scores = q @ k.T / np.sqrt(q.shape[-1])
```

### Attention weights

```python
softmax(scores)
```

Форма остаётся `[n_q, n_k]`. Каждая строка суммируется в 1.

### Взвешенная сумма Values

```python
softmax(scores) @ v
```

Формы:

```text
[n_q, n_k] @ [n_k, d_v] = [n_q, d_v]
```

---

## 7. Ручной пример Attention

```python
q = [[1, 0]]
k = [[1, 0], [0, 1]]
v = [[10, 0], [0, 20]]
```

Dot products:

```text
q @ k.T = [[1, 0]]
```

`d_k = 2`, значит делим на `sqrt(2)`:

```text
[[0.7071, 0]]
```

Softmax примерно:

```text
[[0.6698, 0.3302]]
```

Умножение на V:

```text
0.6698*[10, 0] + 0.3302*[0, 20]
=
[6.698, 6.604]
```

---

## 8. `self_attention`

```python
def self_attention(x, c_attn, c_proj):
    x = linear(x, **c_attn)
    q, k, v = np.split(x, 3, axis=-1)
    x = attention(q, k, v)
    return linear(x, **c_proj)
```

### Вход

```text
x: [n_seq, n_embd]
```

### QKV projection

```python
x = linear(x, **c_attn)
```

`c_attn` — словарь:

```python
{
    "w": matrix,
    "b": bias,
}
```

`**c_attn` раскрывает его в именованные аргументы.

Форма:

```text
[n_seq, n_embd] → [n_seq, 3*n_embd]
```

### Split

```python
q, k, v = np.split(x, 3, axis=-1)
```

`3` — число равных частей.

`axis=-1` — последняя ось.

Если:

```text
x.shape = [5, 12]
```

получаем:

```text
q.shape = [5, 4]
k.shape = [5, 4]
v.shape = [5, 4]
```

### Self-Attention

```python
x = attention(q, k, v)
```

Q, K и V получены из одной последовательности, поэтому механизм называется Self-Attention.

### Output projection

```python
return linear(x, **c_proj)
```

Она сохраняет форму `[n_seq, n_embd]` и является частью архитектуры GPT-2.

---

## 9. Полный shape tracing

```text
x                         [n_seq, n_embd]
c_attn.w                  [n_embd, 3*n_embd]
linear                    [n_seq, 3*n_embd]
q                         [n_seq, n_embd]
k                         [n_seq, n_embd]
v                         [n_seq, n_embd]
q @ k.T                   [n_seq, n_seq]
softmax                   [n_seq, n_seq]
softmax @ v               [n_seq, n_embd]
c_proj.w                  [n_embd, n_embd]
result                    [n_seq, n_embd]
```

---

## 10. Локальные проверки

### Softmax

```python
x = np.array([
    [1.0, 2.0, 3.0],
    [1000.0, 1001.0, 1002.0],
])

result = softmax(x)

assert result.shape == x.shape
assert np.allclose(result.sum(axis=-1), 1.0)
assert np.isfinite(result).all()
```

### Инвариантность к сдвигу

```python
assert np.allclose(
    softmax(x),
    softmax(x + 1000),
)
```

### Attention

```python
rng = np.random.default_rng(42)
q = rng.normal(size=(3, 4))
k = rng.normal(size=(5, 4))
v = rng.normal(size=(5, 6))

result = attention(q, k, v)

assert result.shape == (3, 6)
```

### Self-Attention

```python
n_seq = 4
n_embd = 3

x = rng.normal(size=(n_seq, n_embd))

c_attn = {
    "w": rng.normal(size=(n_embd, 3*n_embd)),
    "b": rng.normal(size=(3*n_embd,)),
}

c_proj = {
    "w": rng.normal(size=(n_embd, n_embd)),
    "b": rng.normal(size=(n_embd,)),
}

result = self_attention(x, c_attn, c_proj)

assert result.shape == x.shape
```

---

## 11. Ошибки, которые не пройдут тесты

### Общая сумма Softmax

```python
np.sum(exp_x)
```

Нужно:

```python
np.sum(exp_x, axis=-1, keepdims=True)
```

### Нестабильная экспонента

```python
np.exp(x)
```

без вычитания максимума может переполниться.

### Неправильный transpose

Правильно:

```python
q @ k.T
```

### Нет scale

Нельзя забывать:

```python
/ np.sqrt(q.shape[-1])
```

### Scale после Softmax

Неправильно:

```python
softmax(q @ k.T) / np.sqrt(d_k)
```

### Поэлементное умножение с V

Неправильно:

```python
weights * v
```

Правильно:

```python
weights @ v
```

### Split до linear

Q, K и V создаются из результата `c_attn`, а не из исходного `x`.

### Split по axis=0

Это разделит токены. Нужно делить последний размер.

### Нет c_proj

Возвращать только `attention(q, k, v)` недостаточно.

---

## 12. Почему здесь нет mask

Шаблон функции:

```python
attention(q, k, v)
```

не принимает mask. Поэтому на этой странице causal mask добавлять не нужно. Лишняя маска изменит ожидаемые тестовые значения.

---

## 13. Почему здесь нет heads

Это single-head Self-Attention. Не нужно самостоятельно делить embedding на головы, потому что API задачи этого не требует. Multi-Head Attention будет отдельным шагом.

---

## 14. Распределение баллов

### 20% — Softmax

Покрывается стабильной нормализацией по последней оси.

### 40% — Attention

Покрывается точной формулой:

```python
softmax(q @ k.T / np.sqrt(q.shape[-1])) @ v
```

### 20% — QKV

Покрывается:

```python
q, k, v = np.split(x, 3, axis=-1)
```

Для полного результата также важно сохранить сигнатуры, output projection и корректный PEP8-код.

---

## 15. Ответ на интервью за 30 секунд

> Из входных embeddings одной последовательности объединённым линейным слоем строятся Q, K и V. Результат размерности `3d` разделяется на три части. Матрица `QKᵀ` измеряет совместимость каждого Query с каждым Key. Scores масштабируются на `sqrt(d_k)`, нормируются Softmax по Keys и используются как веса для взвешенной суммы Values. Затем применяется output projection.

---

## 16. Финальный алгоритм

```text
1. Выполнить Linear с c_attn.
2. Разделить последний размер на Q, K и V.
3. Посчитать Q @ K.T.
4. Разделить scores на sqrt(d_k).
5. Применить стабильный Softmax по последней оси.
6. Умножить Attention weights на V.
7. Выполнить Linear с c_proj.
8. Вернуть массив исходной размерности.
```

# Страница 4. Пошаговое объяснение решения FFN

## 1. Файл для отправки

В проверяющую систему нужно загрузить:

```text
gp_page_4_gpt2_ffn_linear_gelu_solution.py
```

В нём находятся только:

- импорт NumPy;
- функция `linear`;
- функция `gelu`;
- функция `ffn`.

---

# Часть I. Полный код

```python
"""Feed-forward network components for GPT-2."""

import numpy as np


def linear(x, w, b):
    """Apply a linear transformation to the input."""
    return x @ w + b


def gelu(x):
    """Apply the Gaussian Error Linear Unit activation."""
    return 0.5 * x * (
        1.0
        + np.tanh(
            np.sqrt(2.0 / np.pi)
            * (x + 0.044715 * x**3)
        )
    )


def ffn(x, c_fc, c_proj):
    """Apply the GPT-2 feed-forward network."""
    hidden = gelu(linear(x, **c_fc))
    return linear(hidden, **c_proj)
```

---

# Часть II. Module docstring

## 2. Первая строка

```python
"""Feed-forward network components for GPT-2."""
```

Это описание Python-модуля.

Оно помогает:

- человеку понять назначение файла;
- Pylint не выдавать предупреждение о missing module docstring;
- инструментам документации.

Эта строка не влияет на математический результат.

---

# Часть III. Импорт

## 3. NumPy

```python
import numpy as np
```

NumPy нужен для:

- работы с массивами;
- `np.tanh`;
- `np.sqrt`;
- константы `np.pi`;
- матричного умножения через NumPy arrays.

Оператор `@` реализован самими массивами NumPy.

---

# Часть IV. Функция `linear`

## 4. Заголовок

```python
def linear(x, w, b):
```

Функция принимает три объекта.

### `x`

Входной массив:

```text
[m, in]
```

### `w`

Матрица весов:

```text
[in, out]
```

### `b`

Вектор bias:

```text
[out]
```

---

## 5. Docstring

```python
"""Apply a linear transformation to the input."""
```

Описывает назначение функции.

---

## 6. Возвращаемое выражение

```python
return x @ w + b
```

Оно выполняется в два этапа:

```python
x @ w
```

затем:

```python
... + b
```

---

## 7. Что делает `@`

Оператор:

```python
x @ w
```

означает матричное умножение.

Он не равен:

```python
x * w
```

Знак `*` выполняет поэлементное умножение и требует совместимые формы.

`@` вычисляет сумму произведений строк и столбцов.

---

## 8. Ручной пример

```python
x = np.array([
    [1.0, 2.0],
    [3.0, 4.0],
])

w = np.array([
    [10.0, 20.0, 30.0],
    [40.0, 50.0, 60.0],
])

b = np.array([1.0, 2.0, 3.0])
```

Формы:

```text
x: [2, 2]
w: [2, 3]
b: [3]
```

Первая строка результата матричного умножения:

```text
1*10 + 2*40 = 90
1*20 + 2*50 = 120
1*30 + 2*60 = 150
```

После bias:

```text
[91, 122, 153]
```

Вторая строка:

```text
3*10 + 4*40 = 190
3*20 + 4*50 = 260
3*30 + 4*60 = 330
```

После bias:

```text
[191, 262, 333]
```

Итог:

```python
[
    [91.0, 122.0, 153.0],
    [191.0, 262.0, 333.0],
]
```

---

## 9. Почему bias прибавляется ко всем строкам

`b.shape == (out,)`.

Результат `x @ w` имеет:

```text
[m, out]
```

NumPy использует broadcasting и повторяет bias логически для каждой из `m` строк.

---

# Часть V. Функция `gelu`

## 10. Заголовок

```python
def gelu(x):
```

Она принимает:

- число;
- вектор;
- матрицу;
- многомерный NumPy-массив.

Все операции поэлементные.

---

## 11. Формула

```python
return 0.5 * x * (
    1.0
    + np.tanh(
        np.sqrt(2.0 / np.pi)
        * (x + 0.044715 * x**3)
    )
)
```

Это tanh-аппроксимация GELU, используемая GPT-2.

---

## 12. Почему `x**3`

```python
x**3
```

возводит каждый элемент массива в третью степень.

Например:

```python
x = np.array([-2.0, 0.0, 3.0])
```

получается:

```python
[-8.0, 0.0, 27.0]
```

---

## 13. Кубическая поправка

```python
x + 0.044715 * x**3
```

Это часть приближения нормальной функции распределения через `tanh`.

Не нужно:

- округлять `0.044715`;
- заменять его на другое число;
- удалять кубическую часть.

---

## 14. Константа

```python
np.sqrt(2.0 / np.pi)
```

### `np.pi`

Число \(\pi\).

### `2.0 / np.pi`

Деление двух вещественных чисел.

### `np.sqrt(...)`

Квадратный корень.

---

## 15. Tanh

```python
np.tanh(...)
```

Применяется отдельно к каждому элементу.

Tanh возвращает значения приблизительно от -1 до 1.

---

## 16. Почему стоит `1.0 +`

После tanh:

```text
[-1, 1]
```

После прибавления единицы:

```text
[0, 2]
```

После умножения на 0.5:

```text
[0, 1]
```

Это создаёт плавный коэффициент пропускания входа.

---

## 17. Что происходит с отрицательными значениями

GELU не просто делает:

```text
negative → 0
```

Как ReLU.

Она плавно уменьшает отрицательные значения.

Некоторые значения около нуля остаются небольшими отрицательными.

---

## 18. Значение в нуле

Подставим:

```text
x = 0
```

Куб:

```text
0³ = 0
```

Tanh:

```text
tanh(0) = 0
```

Итог:

```text
0.5 * 0 * (1 + 0) = 0
```

То есть:

```python
gelu(0) == 0
```

---

## 19. Большое положительное значение

При большом положительном `x`:

```text
tanh(...) ≈ 1
```

Тогда:

```text
0.5 * x * (1 + 1)
=
x
```

---

## 20. Большое отрицательное значение

При большом отрицательном `x`:

```text
tanh(...) ≈ -1
```

Тогда:

```text
0.5 * x * (1 - 1)
≈ 0
```

---

# Часть VI. Функция `ffn`

## 21. Заголовок

```python
def ffn(x, c_fc, c_proj):
```

### `x`

Матрица embeddings:

```text
[n_seq, n_embd]
```

### `c_fc`

Словарь первого линейного слоя:

```python
{
    "w": first_weight_matrix,
    "b": first_bias,
}
```

### `c_proj`

Словарь второго линейного слоя:

```python
{
    "w": second_weight_matrix,
    "b": second_bias,
}
```

---

## 22. Первый этап

```python
linear(x, **c_fc)
```

Оператор `**` раскрывает словарь.

Это:

```python
linear(
    x,
    w=c_fc["w"],
    b=c_fc["b"],
)
```

---

## 23. Форма первого результата

Если:

```text
x: [n_seq, n_embd]
c_fc["w"]: [n_embd, 4*n_embd]
c_fc["b"]: [4*n_embd]
```

то:

```text
linear(x, **c_fc):
[n_seq, 4*n_embd]
```

---

## 24. GELU

```python
gelu(linear(x, **c_fc))
```

GELU не меняет форму.

Поэтому:

```text
[n_seq, 4*n_embd]
```

остаётся:

```text
[n_seq, 4*n_embd]
```

---

## 25. Переменная `hidden`

```python
hidden = gelu(linear(x, **c_fc))
```

Она хранит промежуточное скрытое представление.

Название `hidden` отражает hidden layer FFN.

---

## 26. Второй linear

```python
return linear(hidden, **c_proj)
```

Если:

```text
hidden: [n_seq, 4*n_embd]
c_proj["w"]: [4*n_embd, n_embd]
c_proj["b"]: [n_embd]
```

результат:

```text
[n_seq, n_embd]
```

---

# Часть VII. Почему residual connection отсутствует

## 27. Что такое residual

В полном Transformer-блоке позже будет:

```python
x = x + ffn(...)
```

Но текущая функция должна вернуть только:

```python
ffn(x)
```

Не:

```python
x + ffn(x)
```

Иначе при добавлении residual на следующем уровне вход будет прибавлен дважды.

---

# Часть VIII. Локальные проверки

## 28. Проверка linear

```python
import numpy as np

x = np.array([
    [1.0, 2.0],
    [3.0, 4.0],
])

w = np.array([
    [10.0, 20.0],
    [30.0, 40.0],
])

b = np.array([1.0, 2.0])

result = linear(x, w, b)

expected = x @ w + b

assert np.allclose(result, expected)
```

---

## 29. Проверка GELU на нуле

```python
assert np.allclose(gelu(np.array([0.0])), [0.0])
```

---

## 30. Проверка формы GELU

```python
x = np.random.randn(4, 5)

assert gelu(x).shape == x.shape
```

---

## 31. Проверка формы FFN

```python
rng = np.random.default_rng(42)

n_seq = 3
n_embd = 4
hidden_size = 4 * n_embd

x = rng.normal(size=(n_seq, n_embd))

c_fc = {
    "w": rng.normal(size=(n_embd, hidden_size)),
    "b": rng.normal(size=(hidden_size,)),
}

c_proj = {
    "w": rng.normal(size=(hidden_size, n_embd)),
    "b": rng.normal(size=(n_embd,)),
}

result = ffn(x, c_fc, c_proj)

assert result.shape == x.shape
```

---

## 32. Проверка FFN вручную

```python
expected = (
    gelu(x @ c_fc["w"] + c_fc["b"])
    @ c_proj["w"]
    + c_proj["b"]
)

assert np.allclose(result, expected)
```

---

# Часть IX. Как тесты могут выявить ошибки

## 33. Неправильный порядок умножения

Если написать:

```python
w @ x
```

формы часто окажутся несовместимы.

Даже если для квадратных матриц код запустится, численный результат будет другим.

---

## 34. Поэлементное умножение

Если написать:

```python
x * w
```

это не dense layer.

Тест `linear` сравнит результат с матричным произведением и завершится ошибкой.

---

## 35. Забытый bias

```python
return x @ w
```

неполон.

При ненулевом `b` тест сразу обнаружит различие.

---

## 36. Другая GELU

Если использовать:

```python
np.maximum(0, x)
```

это ReLU.

Если использовать точную erf-формулу, результат будет очень близким, но не идентичным tanh-аппроксимации. Строгие тесты могут не принять.

---

## 37. Неправильный FFN

Неправильно:

```python
return gelu(
    linear(
        linear(x, **c_fc),
        **c_proj,
    )
)
```

Здесь GELU применяется после projection.

Правильно:

```text
c_fc → GELU → c_proj
```

---

# Часть X. Почему решение минимальное

## 38. Не нужны циклы

Все вычисления векторизованы NumPy.

Не нужно проходить:

- по строкам;
- по нейронам;
- по embedding dimensions.

NumPy выполняет операции над целыми массивами.

---

## 39. Не нужны проверки форм

Проверки форм могут быть полезны в production, но в учебной функции:

- контракт задан условием;
- лишний код может усложнить решение;
- NumPy сам выдаст ошибку при несовместимых формах.

---

## 40. Не нужен класс

Задание требует три функции.

Создание классов:

```python
class Linear:
class GELU:
class FFN:
```

нарушит ожидаемый API.

---

# Часть XI. Баллы

## 41. GELU — 40 баллов

Обеспечивается точной формулой:

```python
0.5 * x * (
    1.0
    + np.tanh(
        np.sqrt(2.0 / np.pi)
        * (x + 0.044715 * x**3)
    )
)
```

---

## 42. Linear — 40 баллов

Обеспечивается:

```python
x @ w + b
```

---

## 43. FFN — 20 баллов

Обеспечивается:

```python
hidden = gelu(linear(x, **c_fc))
return linear(hidden, **c_proj)
```

---

# Часть XII. Ответ на интервью

## 44. Короткое объяснение кода

> `linear` выполняет affine transformation `x @ w + b`. `gelu` реализует tanh-аппроксимацию Gaussian Error Linear Unit, используемую GPT-2. `ffn` сначала расширяет hidden dimension через `c_fc`, применяет GELU, а затем возвращает исходную размерность через `c_proj`.

---

## 45. Почему FFN называется position-wise

Если `x` имеет форму:

```text
[n_seq, n_embd]
```

матричное умножение применяет один и тот же слой к каждой строке.

Каждая строка соответствует отдельной позиции токена.

FFN не смешивает строки между собой.

Смешивание токенов выполняет attention.

---

## 46. Что изучается в весах FFN

Во время обучения изменяются:

```python
c_fc["w"]
c_fc["b"]
c_proj["w"]
c_proj["b"]
```

GELU не имеет обучаемых параметров.

---

# Часть XIII. Финальная схема

```text
x: [n_seq, n_embd]
    ↓
x @ c_fc["w"] + c_fc["b"]
    ↓
[n_seq, 4*n_embd]
    ↓
GELU
    ↓
[n_seq, 4*n_embd]
    ↓
hidden @ c_proj["w"] + c_proj["b"]
    ↓
[n_seq, n_embd]
```

Это и есть Feed-Forward Network GPT-2 в текущем задании.

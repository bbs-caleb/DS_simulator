# SKU Embeddings — Matrix Normalization: пошаговое объяснение с нуля

# 1. Что дано на вход

Каждый метод получает:

```python
matrix: csr_matrix
```

Это разреженная User-Item Matrix.

Строки:

```text
пользователи
```

Столбцы:

```text
товары
```

Значения:

```text
количество покупок
```

Пример плотного представления маленькой матрицы:

```text
[
    [6, 0, 2, 2],
    [3, 20, 0, 8],
    [12, 1, 0, 6],
]
```

В реальной задаче матрица хранится в CSR, и нули физически почти не занимают память.

---

# 2. Почему сначала импортируется NumPy

```python
import numpy as np
```

NumPy используется не для создания полной матрицы.

Он используется только для небольших одномерных векторов:

- суммы строк;
- суммы столбцов;
- обратные суммы;
- document frequency;
- IDF;
- длины строк;
- delta.

Размер этих векторов:

```text
N или M
```

а не:

```text
N × M
```

---

# 3. Зачем импортировать `diags`

```python
from scipy.sparse import csr_matrix, diags
```

`diags` создаёт разреженную диагональную матрицу.

Пример:

```python
diags([0.5, 0.25, 1.0])
```

математически представляет:

```text
[
    [0.5, 0,    0],
    [0,   0.25, 0],
    [0,   0,    1.0],
]
```

Но хранит только три диагональных значения.

Диагональные матрицы удобны для масштабирования строк и столбцов.

---

# 4. Разбор `by_column`

Сигнатура:

```python
@staticmethod
def by_column(matrix: csr_matrix) -> csr_matrix:
```

`@staticmethod` означает, что метод не использует состояние объекта.

Его вызывают так:

```python
Normalization.by_column(matrix)
```

Создавать объект класса не нужно.

---

# 5. Суммы столбцов

```python
column_sums = np.asarray(matrix.sum(axis=0)).ravel()
```

Разберём по частям.

## `matrix.sum(axis=0)`

`axis=0` означает:

```text
суммировать сверху вниз
```

То есть получить сумму каждого столбца.

Для:

```text
[
    [2, 0, 1],
    [1, 3, 0],
]
```

результат:

```text
[3, 3, 1]
```

## `np.asarray(...)`

Преобразует результат SciPy в обычный NumPy-массив.

## `.ravel()`

Делает одномерный вектор:

```text
shape = (M,)
```

---

# 6. Почему создаётся `inverse_sums`

```python
inverse_sums = np.zeros_like(
    column_sums,
    dtype=float,
)
```

Нам нужно делить каждый столбец на его сумму.

Деление можно заменить умножением:

\[
x / s = x \cdot (1/s)
\]

Поэтому сначала рассчитываются:

```text
1 / column_sum
```

---

# 7. Безопасное деление

```python
np.divide(
    1.0,
    column_sums,
    out=inverse_sums,
    where=column_sums != 0,
)
```

Почему нельзя просто написать:

```python
1 / column_sums
```

Если пустой столбец имеет сумму 0, появится:

```text
division by zero
inf
```

Параметр:

```python
where=column_sums != 0
```

выполняет деление только для ненулевых сумм.

Для нулевого столбца коэффициент остаётся 0.

---

# 8. Масштабирование столбцов

```python
norm_matrix = matrix.astype(float).dot(
    diags(inverse_sums)
)
```

Умножение справа на диагональную матрицу масштабирует столбцы:

\[
X D
\]

Каждый столбец умножается на свой коэффициент.

`astype(float)` нужен, потому что нормализованные значения обычно дробные.

---

# 9. Возврат CSR

```python
return norm_matrix.tocsr()
```

Некоторые операции могут вернуть другой sparse-формат.

`.tocsr()` гарантирует тип:

```python
csr_matrix
```

---

# 10. Ручной пример `by_column`

Исходная матрица:

```text
[
    [2, 0, 1],
    [1, 3, 0],
]
```

Суммы столбцов:

```text
[3, 3, 1]
```

Обратные суммы:

```text
[1/3, 1/3, 1]
```

Результат:

```text
[
    [2/3, 0,   1],
    [1/3, 1,   0],
]
```

Каждый ненулевой столбец суммируется в 1.

---

# 11. Разбор `by_row`

Суммы строк:

```python
row_sums = np.asarray(
    matrix.sum(axis=1)
).ravel()
```

`axis=1` означает:

```text
суммировать слева направо
```

---

# 12. Обратные суммы строк

```python
inverse_sums = np.zeros_like(
    row_sums,
    dtype=float,
)
```

Затем:

```python
np.divide(
    1.0,
    row_sums,
    out=inverse_sums,
    where=row_sums != 0,
)
```

---

# 13. Масштабирование строк

```python
norm_matrix = diags(inverse_sums).dot(
    matrix.astype(float)
)
```

Диагональная матрица умножается слева:

\[
D X
\]

Это масштабирует строки.

---

# 14. Ручной пример `by_row`

Матрица:

```text
[
    [2, 0, 1],
    [1, 3, 0],
]
```

Суммы строк:

```text
[3, 4]
```

Обратные суммы:

```text
[1/3, 1/4]
```

Результат:

```text
[
    [2/3, 0,   1/3],
    [1/4, 3/4, 0],
]
```

Каждая ненулевая строка суммируется в 1.

---

# 15. Разбор `tf_idf`

Первая строка:

```python
tf_matrix = Normalization.by_row(matrix)
```

TF в этой задаче — доля товара внутри всех покупок пользователя.

То есть TF уже совпадает с нормализацией по строкам.

---

# 16. Число пользователей

```python
user_count = matrix.shape[0]
```

`shape[0]` — число строк.

В аналогии с текстами это число документов.

---

# 17. Document frequency

```python
document_frequency = np.asarray(
    (matrix > 0).sum(axis=0)
).ravel()
```

Разберём.

## `matrix > 0`

Каждое ненулевое положительное значение превращается в `True`.

Пример:

```text
[
    [2, 0, 1],
    [1, 3, 0],
]
```

становится:

```text
[
    [True,  False, True],
    [True,  True,  False],
]
```

## `.sum(axis=0)`

Считает, в скольких строках встречается каждый товар.

Результат:

```text
[2, 1, 1]
```

Это и есть document frequency.

---

# 18. Создание IDF-вектора

```python
idf = np.zeros_like(
    document_frequency,
    dtype=float,
)
```

Вектор имеет длину, равную числу товаров.

---

# 19. Защита от пустых столбцов

```python
valid_columns = document_frequency > 0
```

Пустой столбец имеет:

```text
df = 0
```

Нельзя считать:

```text
log(N / 0)
```

Поэтому IDF вычисляется только для непустых столбцов.

---

# 20. Формула IDF

```python
idf[valid_columns] = np.log(
    user_count
    / document_frequency[valid_columns]
)
```

Формула:

\[
IDF_j = \log(N/df_j)
\]

Чем меньше пользователей покупали товар, тем больше IDF.

---

# 21. Применение IDF

```python
norm_matrix = tf_matrix.dot(
    diags(idf)
)
```

Умножение справа масштабирует столбцы.

Каждый столбец TF умножается на свой IDF.

---

# 22. Маленький пример TF-IDF

Матрица:

```text
[
    [2, 0, 1],
    [1, 3, 0],
]
```

TF:

```text
[
    [2/3, 0,   1/3],
    [1/4, 3/4, 0],
]
```

Document frequency:

```text
[2, 1, 1]
```

Число пользователей:

```text
N = 2
```

IDF:

```text
[
    log(2/2),
    log(2/1),
    log(2/1),
]
```

То есть:

```text
[
    0,
    log(2),
    log(2),
]
```

Первый товар встречается у всех и получает нулевой IDF.

---

# 23. Разбор `bm_25`

Сначала проверяются крайние случаи:

```python
if matrix.shape[0] == 0 or matrix.nnz == 0:
    return csr_matrix(matrix.shape, dtype=float)
```

## `matrix.shape[0] == 0`

Нет пользователей.

## `matrix.nnz == 0`

Нет ненулевых взаимодействий.

В обоих случаях нормализовать нечего.

---

# 24. TF для BM25

```python
tf_matrix = Normalization.by_row(matrix)
```

Используется та же TF, что в TF-IDF.

---

# 25. Длины строк

```python
row_lengths = np.asarray(
    matrix.sum(axis=1)
).ravel()
```

Это исходное общее количество покупок каждого пользователя:

\[
|d_i|
\]

---

# 26. Средняя длина

```python
average_length = row_lengths.mean()
```

Это:

\[
avgdl
\]

Средняя сумма покупок пользователя.

---

# 27. Защита от нулевой средней

```python
if average_length == 0:
    return csr_matrix(matrix.shape, dtype=float)
```

Если средняя длина равна нулю, все строки пусты.

---

# 28. IDF для BM25

Document frequency и IDF считаются так же, как в TF-IDF:

```python
document_frequency = np.asarray(
    (matrix > 0).sum(axis=0)
).ravel()
```

```python
idf[valid_columns] = np.log(
    matrix.shape[0]
    / document_frequency[valid_columns]
)
```

---

# 29. Что такое `delta`

```python
delta = k1 * (
    (1.0 - b)
    + b * row_lengths / average_length
)
```

Это строковая часть знаменателя:

\[
\Delta_i =
k_1
\left(
1-b+b\frac{|d_i|}{avgdl}
\right)
\]

Для каждой строки свой коэффициент.

---

# 30. Почему нельзя написать `tf_matrix + delta`

`delta` — вектор строк.

Если прибавить его к sparse-матрице, нули могут стать ненулевыми.

Матрица перестанет быть разреженной.

Поэтому формулу переписывают.

---

# 31. Обратный `delta`

```python
inverse_delta = np.zeros_like(
    delta,
    dtype=float,
)
```

Затем безопасное деление:

```python
np.divide(
    1.0,
    delta,
    out=inverse_delta,
    where=delta != 0,
)
```

---

# 32. Вычисление `TF / delta`

```python
saturated_tf = (
    diags(inverse_delta)
    .dot(tf_matrix)
    .tocsr()
)
```

Диагональная матрица масштабирует строки:

\[
TF_{ij}/\Delta_i
\]

---

# 33. Первая степень `-1`

```python
saturated_tf = saturated_tf.power(-1)
```

Для каждого хранящегося значения:

\[
(TF/\Delta)^{-1}
=
\Delta/TF
\]

Нули не хранятся, поэтому операция работает только с ненулевыми парами.

---

# 34. Прибавление единицы

```python
saturated_tf.data += 1.0
```

Прибавляется единица только к хранящимся значениям.

Получаем:

\[
1+\Delta/TF
\]

Структура матрицы не меняется.

---

# 35. Вторая степень `-1`

```python
saturated_tf = saturated_tf.power(-1)
```

Получаем:

\[
\frac{1}{1+\Delta/TF}
=
\frac{TF}{TF+\Delta}
\]

---

# 36. Умножение на `k1 + 1`

```python
saturated_tf.data *= k1 + 1.0
```

Получаем:

\[
\frac{TF(k_1+1)}{TF+\Delta}
\]

---

# 37. Умножение на IDF

```python
norm_matrix = saturated_tf.dot(
    diags(idf)
)
```

Каждый товарный столбец умножается на свой IDF.

Итог:

\[
BM25_{ij}
=
IDF_j
\cdot
\frac{TF_{ij}(k_1+1)}
{TF_{ij}+\Delta_i}
\]

---

# 38. Отдельная обработка `k1 == 0`

```python
if k1 == 0:
    saturated_tf = tf_matrix.copy()
    saturated_tf.data.fill(1.0)
```

При `k1 = 0`:

\[
\frac{TF(0+1)}{TF+0}=1
\]

для каждой ненулевой пары.

После этого остаётся умножение на IDF.

---

# 39. Почему исходная матрица не меняется

Ни один метод не делает:

```python
matrix.data = ...
```

Все изменения происходят в новых объектах.

Поэтому можно безопасно вызвать:

```python
row_matrix = Normalization.by_row(matrix)
tfidf_matrix = Normalization.tf_idf(matrix)
bm25_matrix = Normalization.bm_25(matrix)
```

на одном исходном объекте.

---

# 40. Проверка типа

После каждого метода:

```python
isinstance(result, csr_matrix)
```

должно быть:

```text
True
```

---

# 41. Проверка формы

Для входа:

```text
shape = (N, M)
```

выход должен иметь:

```text
shape = (N, M)
```

Нормализация не добавляет и не удаляет пользователей или товары.

---

# 42. Что будет с нулевой строкой

Нулевая строка:

```text
[0, 0, 0]
```

остаётся:

```text
[0, 0, 0]
```

Новые взаимодействия не создаются.

---

# 43. Что будет с нулевым столбцом

Нулевой столбец остаётся нулевым.

IDF для него не вычисляется, потому что:

```text
df = 0
```

---

# 44. Главные ошибки новичка

## Ошибка 1

```python
matrix.toarray()
```

На больших данных может закончиться память.

## Ошибка 2

```python
matrix / matrix.sum(axis=1)
```

Broadcasting может работать не так, как ожидается, и вернуть неудобный формат.

## Ошибка 3

Не защищаться от нулевых сумм.

## Ошибка 4

Считать IDF по сумме количества:

```python
matrix.sum(axis=0)
```

IDF требует число пользователей с товаром, а не общее количество товара.

Правильно:

```python
(matrix > 0).sum(axis=0)
```

## Ошибка 5

Использовать логарифм без деления:

```python
np.log(document_frequency)
```

## Ошибка 6

Прибавлять dense-вектор к sparse-матрице в BM25.

## Ошибка 7

Забывать `.tocsr()`.

## Ошибка 8

Изменять имена `k1` и `b`.

Автотест может проверять точный API.

---

# 45. Итоговый порядок вычислений

## By column

```text
column sums
-> inverse sums
-> right diagonal multiplication
```

## By row

```text
row sums
-> inverse sums
-> left diagonal multiplication
```

## TF-IDF

```text
row normalization
-> document frequency
-> IDF
-> column scaling
```

## BM25

```text
row normalization
-> row lengths
-> average length
-> document frequency
-> IDF
-> delta
-> reciprocal transformation
-> column scaling
```

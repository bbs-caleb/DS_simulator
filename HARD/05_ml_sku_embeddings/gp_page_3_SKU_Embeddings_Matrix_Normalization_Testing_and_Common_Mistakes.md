# SKU Embeddings — тестирование и частые ошибки Matrix Normalization

# 1. Что должна проверить локальная проверка

Для каждого метода нужно проверить:

- тип результата;
- форму результата;
- значения;
- отсутствие изменения входной матрицы;
- отсутствие NaN и inf;
- поведение на пустых строках;
- поведение на пустых столбцах;
- поведение на полностью пустой матрице.

---

# 2. Базовая тестовая матрица

```python
import numpy as np
from scipy.sparse import csr_matrix

matrix = csr_matrix(
    np.array(
        [
            [2, 0, 1],
            [0, 3, 0],
            [1, 1, 0],
            [0, 0, 0],
        ],
        dtype=float,
    )
)
```

Здесь:

- 4 пользователя;
- 3 товара;
- последняя строка пустая.

---

# 3. Тест `by_column`

Суммы столбцов:

```text
column 0: 2 + 0 + 1 + 0 = 3
column 1: 0 + 3 + 1 + 0 = 4
column 2: 1 + 0 + 0 + 0 = 1
```

Ожидаем:

```python
expected = np.array(
    [
        [2 / 3, 0, 1],
        [0, 3 / 4, 0],
        [1 / 3, 1 / 4, 0],
        [0, 0, 0],
    ]
)
```

Проверка:

```python
result = Normalization.by_column(matrix)

assert isinstance(result, csr_matrix)
assert result.shape == matrix.shape

np.testing.assert_allclose(
    result.toarray(),
    expected,
)
```

---

# 4. Тест `by_row`

Суммы строк:

```text
row 0: 3
row 1: 3
row 2: 2
row 3: 0
```

Ожидаем:

```python
expected = np.array(
    [
        [2 / 3, 0, 1 / 3],
        [0, 1, 0],
        [1 / 2, 1 / 2, 0],
        [0, 0, 0],
    ]
)
```

Проверка:

```python
result = Normalization.by_row(matrix)

assert isinstance(result, csr_matrix)
assert result.shape == matrix.shape

np.testing.assert_allclose(
    result.toarray(),
    expected,
)
```

---

# 5. Проверка сумм после row normalization

```python
row_sums = np.asarray(
    result.sum(axis=1)
).ravel()
```

Ожидаем:

```text
[1, 1, 1, 0]
```

Проверка:

```python
np.testing.assert_allclose(
    row_sums,
    np.array([1, 1, 1, 0]),
)
```

---

# 6. Проверка сумм после column normalization

```python
column_sums = np.asarray(
    result.sum(axis=0)
).ravel()
```

Для непустых столбцов ожидаем 1.

---

# 7. Ручной тест TF-IDF

Число пользователей:

```text
N = 4
```

Document frequency:

```text
item 0 встречается у 2 пользователей
item 1 встречается у 2 пользователей
item 2 встречается у 1 пользователя
```

IDF:

```text
[
    log(4 / 2),
    log(4 / 2),
    log(4 / 1),
]
```

TF:

```text
[
    [2/3, 0,   1/3],
    [0,   1,   0],
    [1/2, 1/2, 0],
    [0,   0,   0],
]
```

Ожидаемый TF-IDF:

```python
idf = np.log(
    np.array([4 / 2, 4 / 2, 4 / 1])
)

expected = np.array(
    [
        [2 / 3, 0, 1 / 3],
        [0, 1, 0],
        [1 / 2, 1 / 2, 0],
        [0, 0, 0],
    ]
) * idf
```

---

# 8. Ручной тест BM25

Плотная формула допустима только для маленького теста.

```python
dense = matrix.toarray()
row_lengths = dense.sum(axis=1)
average_length = row_lengths.mean()

tf = np.divide(
    dense,
    row_lengths[:, None],
    out=np.zeros_like(dense),
    where=row_lengths[:, None] != 0,
)

document_frequency = (dense > 0).sum(axis=0)
idf = np.zeros(dense.shape[1], dtype=float)

valid = document_frequency > 0
idf[valid] = np.log(
    dense.shape[0]
    / document_frequency[valid]
)

k1 = 2.0
b = 0.75

expected = np.zeros_like(dense)

for row in range(dense.shape[0]):
    delta = k1 * (
        (1 - b)
        + b * row_lengths[row] / average_length
    )

    for column in range(dense.shape[1]):
        if dense[row, column] != 0:
            expected[row, column] = (
                idf[column]
                * tf[row, column]
                * (k1 + 1)
                / (tf[row, column] + delta)
            )
```

Проверка:

```python
result = Normalization.bm_25(
    matrix,
    k1=k1,
    b=b,
)

np.testing.assert_allclose(
    result.toarray(),
    expected,
)
```

---

# 9. Проверка входной матрицы

До вызова:

```python
original = matrix.copy()
```

После всех методов:

```python
np.testing.assert_array_equal(
    matrix.toarray(),
    original.toarray(),
)
```

Исходная матрица не должна измениться.

---

# 10. Проверка полностью пустой матрицы

```python
empty = csr_matrix((4, 5), dtype=float)

result = Normalization.bm_25(empty)

assert isinstance(result, csr_matrix)
assert result.shape == (4, 5)
assert result.nnz == 0
```

---

# 11. Проверка матрицы без строк

```python
empty_rows = csr_matrix((0, 5), dtype=float)

result = Normalization.bm_25(empty_rows)

assert result.shape == (0, 5)
assert result.nnz == 0
```

---

# 12. Проверка пустого столбца

```python
matrix = csr_matrix(
    [
        [1, 0, 0],
        [0, 2, 0],
    ],
    dtype=float,
)
```

Третий столбец пустой.

После любой нормализации он должен остаться пустым.

Проверка:

```python
result = Normalization.tf_idf(matrix)

assert result[:, 2].nnz == 0
```

---

# 13. Проверка `k1 = 0`

Для каждой ненулевой пары насыщенная TF-часть равна 1.

Ожидаемый результат:

```text
IDF товара на всех существующих взаимодействиях
```

Проверка:

```python
result = Normalization.bm_25(
    matrix,
    k1=0.0,
    b=0.75,
)
```

---

# 14. Проверка разных `b`

## `b = 0`

Длина строки не влияет.

## `b = 1`

Используется полная длиновая коррекция.

Сравните результаты и убедитесь, что они отличаются на строках разной длины.

---

# 15. Проверка отсутствия NaN и inf

```python
for method in (
    Normalization.by_column,
    Normalization.by_row,
    Normalization.tf_idf,
    Normalization.bm_25,
):
    result = method(matrix)

    assert not np.isnan(result.data).any()
    assert not np.isinf(result.data).any()
```

---

# 16. Частая ошибка: dense conversion

Неправильно:

```python
dense = matrix.toarray()
```

внутри production-метода.

На маленьком тесте это работает.

На реальной матрице может вызвать OOM.

---

# 17. Частая ошибка: неправильный IDF

Неправильно:

```python
document_frequency = matrix.sum(axis=0)
```

Это сумма количества.

Правильно:

```python
document_frequency = (
    matrix > 0
).sum(axis=0)
```

Это число пользователей с товаром.

---

# 18. Частая ошибка: перепутать оси

```python
axis=0
```

суммирует столбцы.

```python
axis=1
```

суммирует строки.

Если перепутать, broadcasting может дать ошибку или неверный результат.

---

# 19. Частая ошибка: вернуть COO

`multiply` или некоторые другие операции могут вернуть COO.

Автотест требует `csr_matrix`.

Правильно:

```python
return norm_matrix.tocsr()
```

---

# 20. Частая ошибка: изменить API

Нельзя менять:

```python
def bm_25(
    matrix: csr_matrix,
    k1: float = 2.0,
    b: float = 0.75,
)
```

Например, нельзя переименовать:

```text
k1 -> k
b  -> beta
```

если автотест вызывает параметры по имени.

---

# 21. Частая ошибка: обычные методы вместо static

Неправильно:

```python
def by_row(self, matrix):
```

Задание требует:

```python
@staticmethod
def by_row(matrix):
```

---

# 22. Частая ошибка: прямое прибавление `delta`

Неправильно:

```python
denominator = tf_matrix + delta
```

Это может разрушить разреженность.

Правильно использовать reciprocal transformation.

---

# 23. Частая ошибка: прибавить 1 ко всей матрице

Неправильно:

```python
sparse_matrix + 1
```

Это логически превращает нулевые ячейки в единицы.

Правильно:

```python
sparse_matrix.data += 1
```

---

# 24. Частая ошибка: integer division

Если входная матрица целочисленная, нормализованные значения должны быть float.

Поэтому используется:

```python
matrix.astype(float)
```

---

# 25. Чек-лист перед загрузкой

- файл называется `solution.py`;
- класс называется `Normalization`;
- четыре метода имеют `@staticmethod`;
- точные имена методов сохранены;
- `k1` и `b` сохранены;
- нет `toarray` в решении;
- нет dense-матрицы размера N × M;
- возвращается `csr_matrix`;
- shape сохраняется;
- нулевые строки обработаны;
- нулевые столбцы обработаны;
- IDF использует document frequency;
- BM25 использует TF;
- BM25 использует row length и average length;
- BM25 не разрушает sparsity;
- код проходит PEP8.

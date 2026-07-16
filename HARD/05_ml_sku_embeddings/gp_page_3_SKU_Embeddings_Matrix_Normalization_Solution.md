# SKU Embeddings — готовое решение Matrix Normalization

## 1. Какой файл загружать

Проверяющая система требует один файл:

```text
solution.py
```

Именно этот файл находится в корне итогового архива.

---

# 2. Финальный код

```python
import numpy as np
from scipy.sparse import csr_matrix, diags


class Normalization:
    """Normalize a sparse User-Item matrix."""

    @staticmethod
    def by_column(matrix: csr_matrix) -> csr_matrix:
        """Normalize each matrix column by its sum.

        Args:
            matrix: User-Item matrix of size (N, M).

        Returns:
            Normalized CSR matrix of size (N, M).
        """
        column_sums = np.asarray(matrix.sum(axis=0)).ravel()
        inverse_sums = np.zeros_like(column_sums, dtype=float)

        np.divide(
            1.0,
            column_sums,
            out=inverse_sums,
            where=column_sums != 0,
        )

        norm_matrix = matrix.astype(float).dot(diags(inverse_sums))
        return norm_matrix.tocsr()

    @staticmethod
    def by_row(matrix: csr_matrix) -> csr_matrix:
        """Normalize each matrix row by its sum.

        Args:
            matrix: User-Item matrix of size (N, M).

        Returns:
            Normalized CSR matrix of size (N, M).
        """
        row_sums = np.asarray(matrix.sum(axis=1)).ravel()
        inverse_sums = np.zeros_like(row_sums, dtype=float)

        np.divide(
            1.0,
            row_sums,
            out=inverse_sums,
            where=row_sums != 0,
        )

        norm_matrix = diags(inverse_sums).dot(matrix.astype(float))
        return norm_matrix.tocsr()

    @staticmethod
    def tf_idf(matrix: csr_matrix) -> csr_matrix:
        """Normalize a User-Item matrix using TF-IDF.

        Users are treated as documents and items as terms.

        Args:
            matrix: User-Item matrix of size (N, M).

        Returns:
            TF-IDF-normalized CSR matrix of size (N, M).
        """
        tf_matrix = Normalization.by_row(matrix)

        user_count = matrix.shape[0]
        document_frequency = np.asarray(
            (matrix > 0).sum(axis=0)
        ).ravel()

        idf = np.zeros_like(document_frequency, dtype=float)
        valid_columns = document_frequency > 0
        idf[valid_columns] = np.log(
            user_count / document_frequency[valid_columns]
        )

        norm_matrix = tf_matrix.dot(diags(idf))
        return norm_matrix.tocsr()

    @staticmethod
    def bm_25(
        matrix: csr_matrix,
        k1: float = 2.0,
        b: float = 0.75,
    ) -> csr_matrix:
        """Normalize a User-Item matrix using BM25 weights.

        Users are treated as documents and items as terms.

        Args:
            matrix: User-Item matrix of size (N, M).
            k1: Term-frequency saturation coefficient.
            b: Row-length normalization coefficient.

        Returns:
            BM25-normalized CSR matrix of size (N, M).
        """
        if matrix.shape[0] == 0 or matrix.nnz == 0:
            return csr_matrix(matrix.shape, dtype=float)

        tf_matrix = Normalization.by_row(matrix)
        row_lengths = np.asarray(matrix.sum(axis=1)).ravel()
        average_length = row_lengths.mean()

        if average_length == 0:
            return csr_matrix(matrix.shape, dtype=float)

        document_frequency = np.asarray(
            (matrix > 0).sum(axis=0)
        ).ravel()

        idf = np.zeros_like(document_frequency, dtype=float)
        valid_columns = document_frequency > 0
        idf[valid_columns] = np.log(
            matrix.shape[0] / document_frequency[valid_columns]
        )

        if k1 == 0:
            saturated_tf = tf_matrix.copy()
            saturated_tf.data.fill(1.0)
        else:
            delta = k1 * (
                (1.0 - b)
                + b * row_lengths / average_length
            )
            inverse_delta = np.zeros_like(delta, dtype=float)

            np.divide(
                1.0,
                delta,
                out=inverse_delta,
                where=delta != 0,
            )

            saturated_tf = (
                diags(inverse_delta)
                .dot(tf_matrix)
                .tocsr()
            )
            saturated_tf = saturated_tf.power(-1)
            saturated_tf.data += 1.0
            saturated_tf = saturated_tf.power(-1)
            saturated_tf.data *= k1 + 1.0

        norm_matrix = saturated_tf.dot(diags(idf))
        return norm_matrix.tocsr()
```

---

# 3. Почему решение соответствует API

Сохранены точные требования:

- класс называется `Normalization`;
- все методы являются `@staticmethod`;
- метод называется `by_column`;
- метод называется `by_row`;
- метод называется `tf_idf`;
- метод называется `bm_25`;
- параметры `bm_25` называются `matrix`, `k1`, `b`;
- значения по умолчанию равны `2.0` и `0.75`;
- каждый метод принимает `csr_matrix`;
- каждый метод возвращает `csr_matrix`;
- форма матрицы не меняется.

---

# 4. Решение `by_column`

Алгоритм:

1. посчитать сумму каждого столбца;
2. получить обратные суммы;
3. создать диагональную матрицу коэффициентов;
4. умножить исходную матрицу справа.

Математически:

\[
X_{norm} = X D_{col}^{-1}
\]

Где диагональ содержит:

\[
1 / column\_sum_j
\]

---

# 5. Решение `by_row`

Алгоритм:

1. посчитать сумму каждой строки;
2. получить обратные суммы;
3. создать диагональную матрицу коэффициентов;
4. умножить исходную матрицу слева.

Математически:

\[
X_{norm} = D_{row}^{-1} X
\]

---

# 6. Решение `tf_idf`

## TF

Используется готовая нормализация по строкам:

```python
tf_matrix = Normalization.by_row(matrix)
```

## Document frequency

```python
(matrix > 0).sum(axis=0)
```

считает, у скольких пользователей товар встречается хотя бы один раз.

## IDF

```python
np.log(user_count / document_frequency)
```

## Итог

Каждый столбец TF-матрицы умножается на свой IDF.

---

# 7. Решение `bm_25`

Сначала вычисляются:

- TF;
- длина каждой строки;
- средняя длина;
- document frequency;
- IDF;
- коэффициент `delta` для каждой строки.

Исходная часть формулы:

\[
\frac{TF(k_1+1)}{TF+\Delta}
\]

переписывается:

\[
(k_1+1)
\left(
(TF/\Delta)^{-1}+1
\right)^{-1}
\]

Это позволяет:

- не прибавлять вектор ко всей sparse-матрице;
- не создавать новые ненулевые элементы;
- работать только с `data`;
- сохранить память.

---

# 8. Обработка нулевых строк и столбцов

В коде используется:

```python
np.divide(
    1.0,
    sums,
    out=inverse_sums,
    where=sums != 0,
)
```

Если сумма равна нулю, обратное значение остаётся нулём.

Это предотвращает:

- деление на ноль;
- `inf`;
- `nan`.

Пустые строки и столбцы остаются пустыми.

---

# 9. Почему входная матрица не изменяется

Во всех методах создаются новые объекты:

- `astype(float)`;
- `dot`;
- `multiply`;
- `power`;
- `copy`.

Исходная матрица не модифицируется.

Это важно, потому что один и тот же объект может использоваться для нескольких экспериментов.

---

# 10. Почему результат приводится к CSR

Некоторые операции SciPy могут вернуть другой sparse-формат.

Поэтому в конце используется:

```python
.tocsr()
```

Так соблюдается контракт задания:

```text
вход  — csr_matrix
выход — csr_matrix
```

---

# 11. Почему код memory-safe

Код не создаёт плотную матрицу размера:

```text
N × M
```

Создаются только векторы:

```text
длина N
длина M
```

и sparse-диагональные матрицы.

Сложность по памяти определяется в основном числом ненулевых элементов:

```text
O(nnz + N + M)
```

---

# 12. Что не нужно добавлять

Не нужно:

- использовать `toarray`;
- создавать `np.zeros((N, M))`;
- использовать sklearn;
- менять имена методов;
- делать методы обычными вместо static;
- возвращать NumPy-массив;
- прибавлять dense-вектор к sparse-матрице;
- добавлять лишние параметры.

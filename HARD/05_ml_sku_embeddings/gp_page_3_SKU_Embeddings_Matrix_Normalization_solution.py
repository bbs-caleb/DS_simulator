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

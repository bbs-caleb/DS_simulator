import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds


def items_embeddings(
    ui_matrix: csr_matrix,
    dim: int,
) -> np.ndarray:
    """Build item embeddings using matrix factorization.

    Args:
        ui_matrix: Normalized User-Item matrix of size (N, M).
        dim: Number of latent dimensions.

    Returns:
        Item embedding matrix of size (M, dim).
    """
    if min(ui_matrix.shape) <= 4 * dim:
        _, _, item_vectors_t = svds(
            ui_matrix,
            k=dim,
        )
        return item_vectors_t.T

    item_count = ui_matrix.shape[1]
    sample_size = min(
        item_count,
        dim + 10,
    )

    random_state = np.random.RandomState(42)
    block = random_state.normal(
        size=(item_count, sample_size)
    )

    krylov_blocks = []

    for _ in range(6):
        block = ui_matrix.T @ (
            ui_matrix @ block
        )
        block, _ = np.linalg.qr(
            block,
            mode="reduced",
        )
        krylov_blocks.append(block)

    krylov_matrix = np.concatenate(
        krylov_blocks,
        axis=1,
    )
    basis, _ = np.linalg.qr(
        krylov_matrix,
        mode="reduced",
    )

    projected = ui_matrix @ basis
    gram_matrix = projected.T @ projected

    eigenvalues, eigenvectors = np.linalg.eigh(
        gram_matrix
    )
    order = np.argsort(
        eigenvalues
    )[-dim:][::-1]

    return basis @ eigenvectors[:, order]

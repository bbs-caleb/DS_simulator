from typing import Dict

import pandas as pd
from scipy.sparse import csr_matrix


class UserItemMatrix:
    """Create a sparse user-item matrix from aggregated sales data."""

    def __init__(self, sales_data: pd.DataFrame):
        """Initialize mappings, counters, and the CSR matrix.

        Args:
            sales_data: Aggregated sales data with columns
                user_id, item_id, qty, and price.
        """
        self._sales_data = sales_data.copy()

        user_ids = sorted(self._sales_data["user_id"].unique())
        item_ids = sorted(self._sales_data["item_id"].unique())

        self._user_count = len(user_ids)
        self._item_count = len(item_ids)

        self._user_map = {
            int(user_id): index
            for index, user_id in enumerate(user_ids)
        }
        self._item_map = {
            int(item_id): index
            for index, item_id in enumerate(item_ids)
        }

        row_ind = (
            self._sales_data["user_id"]
            .map(self._user_map)
            .to_numpy(dtype=int)
        )
        col_ind = (
            self._sales_data["item_id"]
            .map(self._item_map)
            .to_numpy(dtype=int)
        )
        values = pd.to_numeric(
            self._sales_data["qty"]
        ).to_numpy()

        self._matrix = csr_matrix(
            (values, (row_ind, col_ind)),
            shape=(self._user_count, self._item_count),
        )

    @property
    def user_count(self) -> int:
        """Return the number of unique users."""
        return self._user_count

    @property
    def item_count(self) -> int:
        """Return the number of unique items."""
        return self._item_count

    @property
    def user_map(self) -> Dict[int, int]:
        """Return a mapping from user IDs to matrix row indexes."""
        return self._user_map

    @property
    def item_map(self) -> Dict[int, int]:
        """Return a mapping from item IDs to matrix column indexes."""
        return self._item_map

    @property
    def csr_matrix(self) -> csr_matrix:
        """Return the user-item matrix in CSR format."""
        return self._matrix

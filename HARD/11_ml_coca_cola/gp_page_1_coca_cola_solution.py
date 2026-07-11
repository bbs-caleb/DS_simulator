# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-locals
from __future__ import annotations

from fractions import Fraction
from math import gcd

import numpy as np
import pandas as pd
from scipy.optimize import Bounds, LinearConstraint, milp
from sklearn.base import TransformerMixin


class CocaCola(TransformerMixin):
    """Postprocess prices using horizontal and vertical price rules."""

    @staticmethod
    def _line_mask(values: pd.Series) -> pd.Series:
        """Return a mask for non-empty line identifiers."""
        return values.notna() & values.ne("")

    @staticmethod
    def _to_fraction(value: float) -> Fraction:
        """Convert a decimal volume to an exact rational number."""
        return Fraction(str(value))

    @classmethod
    def _unit_price_coefficients(
        cls,
        left_netto: float,
        right_netto: float,
    ) -> tuple[int, int]:
        """Return integer coefficients for a unit-price comparison."""
        left = cls._to_fraction(left_netto)
        right = cls._to_fraction(right_netto)

        left_coefficient = left.denominator * right.numerator
        right_coefficient = right.denominator * left.numerator

        divisor = gcd(left_coefficient, right_coefficient)

        return (
            left_coefficient // divisor,
            right_coefficient // divisor,
        )

    @staticmethod
    def _append_constraint(
        rows: list[np.ndarray],
        lower_bounds: list[float],
        upper_bounds: list[float],
        variable_count: int,
        coefficients: dict[int, float],
        lower_bound: float = -np.inf,
        upper_bound: float = np.inf,
    ) -> None:
        """Append one sparse-style row to a linear constraint system."""
        row = np.zeros(variable_count)

        for position, coefficient in coefficients.items():
            row[position] = coefficient

        rows.append(row)
        lower_bounds.append(lower_bound)
        upper_bounds.append(upper_bound)

    @classmethod
    def _append_absolute_deviation_constraints(
        cls,
        prices: np.ndarray,
        variable_count: int,
        rows: list[np.ndarray],
        lower_bounds: list[float],
        upper_bounds: list[float],
    ) -> None:
        """Add constraints for absolute price deviations."""
        size = len(prices)

        for position, original_price in enumerate(prices):
            cls._append_constraint(
                rows,
                lower_bounds,
                upper_bounds,
                variable_count,
                {
                    position: 1,
                    size + position: -1,
                },
                upper_bound=int(original_price),
            )

            cls._append_constraint(
                rows,
                lower_bounds,
                upper_bounds,
                variable_count,
                {
                    position: -1,
                    size + position: -1,
                },
                upper_bound=-int(original_price),
            )

    @classmethod
    def _append_hline_constraints(
        cls,
        frame: pd.DataFrame,
        variable_count: int,
        rows: list[np.ndarray],
        lower_bounds: list[float],
        upper_bounds: list[float],
    ) -> None:
        """Require equal prices inside every horizontal line."""
        mask = cls._line_mask(frame["hline"])

        for _, group in frame.loc[mask].groupby(
            "hline",
            sort=False,
        ):
            positions = group.index.to_list()

            if len(positions) < 2:
                continue

            first_position = positions[0]

            for position in positions[1:]:
                cls._append_constraint(
                    rows,
                    lower_bounds,
                    upper_bounds,
                    variable_count,
                    {
                        first_position: 1,
                        position: -1,
                    },
                    lower_bound=0,
                    upper_bound=0,
                )

    @classmethod
    def _append_vline_constraints(
        cls,
        frame: pd.DataFrame,
        variable_count: int,
        rows: list[np.ndarray],
        lower_bounds: list[float],
        upper_bounds: list[float],
    ) -> None:
        """Require increasing total prices and decreasing unit prices."""
        mask = cls._line_mask(frame["vline"])

        for _, group in frame.loc[mask].groupby(
            "vline",
            sort=False,
        ):
            nettos = sorted(group["netto"].unique())

            for left_netto, right_netto in zip(
                nettos,
                nettos[1:],
            ):
                left_positions = group.index[
                    group["netto"].eq(left_netto)
                ].to_list()
                right_positions = group.index[
                    group["netto"].eq(right_netto)
                ].to_list()

                left_coefficient, right_coefficient = (
                    cls._unit_price_coefficients(
                        left_netto,
                        right_netto,
                    )
                )

                for left_position in left_positions:
                    for right_position in right_positions:
                        cls._append_constraint(
                            rows,
                            lower_bounds,
                            upper_bounds,
                            variable_count,
                            {
                                left_position: -1,
                                right_position: 1,
                            },
                            lower_bound=1,
                        )

                        cls._append_constraint(
                            rows,
                            lower_bounds,
                            upper_bounds,
                            variable_count,
                            {
                                left_position: left_coefficient,
                                right_position: -right_coefficient,
                            },
                            lower_bound=1,
                        )

    @classmethod
    def _build_business_constraints(
        cls,
        frame: pd.DataFrame,
        variable_count: int,
        use_vlines: bool,
        use_hlines: bool,
    ) -> tuple[list[np.ndarray], list[float], list[float]]:
        """Build absolute-deviation and business-rule constraints."""
        rows: list[np.ndarray] = []
        lower_bounds: list[float] = []
        upper_bounds: list[float] = []

        prices = frame["price"].to_numpy(dtype=np.int64)

        cls._append_absolute_deviation_constraints(
            prices,
            variable_count,
            rows,
            lower_bounds,
            upper_bounds,
        )

        if use_hlines:
            cls._append_hline_constraints(
                frame,
                variable_count,
                rows,
                lower_bounds,
                upper_bounds,
            )

        if use_vlines:
            cls._append_vline_constraints(
                frame,
                variable_count,
                rows,
                lower_bounds,
                upper_bounds,
            )

        return rows, lower_bounds, upper_bounds

    @staticmethod
    def _make_linear_constraint(
        rows: list[np.ndarray],
        lower_bounds: list[float],
        upper_bounds: list[float],
    ) -> LinearConstraint:
        """Convert stored rows to a scipy LinearConstraint."""
        return LinearConstraint(
            np.vstack(rows),
            np.asarray(lower_bounds),
            np.asarray(upper_bounds),
        )

    @classmethod
    def _solve_component(
        cls,
        component: pd.DataFrame,
        use_vlines: bool,
        use_hlines: bool,
    ) -> np.ndarray:
        """Solve one connected component with lexicographic objectives."""
        frame = component.reset_index(drop=True)
        prices = frame["price"].to_numpy(dtype=np.int64)
        size = len(frame)

        first_variable_count = 2 * size

        rows, lower_bounds, upper_bounds = (
            cls._build_business_constraints(
                frame,
                first_variable_count,
                use_vlines,
                use_hlines,
            )
        )

        first_objective = np.concatenate(
            (
                np.zeros(size),
                np.ones(size),
            )
        )

        first_bounds = Bounds(
            np.concatenate(
                (
                    np.ones(size),
                    np.zeros(size),
                )
            ),
            np.full(first_variable_count, np.inf),
        )

        first_result = milp(
            c=first_objective,
            integrality=np.ones(first_variable_count),
            bounds=first_bounds,
            constraints=cls._make_linear_constraint(
                rows,
                lower_bounds,
                upper_bounds,
            ),
            options={"disp": False},
        )

        if not first_result.success:
            return prices.copy()

        minimum_l1_error = int(round(first_result.fun))

        if minimum_l1_error == 0:
            return prices.copy()

        second_variable_count = 3 * size

        rows, lower_bounds, upper_bounds = (
            cls._build_business_constraints(
                frame,
                second_variable_count,
                use_vlines,
                use_hlines,
            )
        )

        cls._append_constraint(
            rows,
            lower_bounds,
            upper_bounds,
            second_variable_count,
            {
                size + position: 1
                for position in range(size)
            },
            lower_bound=minimum_l1_error,
            upper_bound=minimum_l1_error,
        )

        for position in range(size):
            cls._append_constraint(
                rows,
                lower_bounds,
                upper_bounds,
                second_variable_count,
                {
                    size + position: 1,
                    2 * size + position: -minimum_l1_error,
                },
                upper_bound=0,
            )

        second_objective = np.concatenate(
            (
                np.zeros(2 * size),
                np.ones(size),
            )
        )

        second_bounds = Bounds(
            np.concatenate(
                (
                    np.ones(size),
                    np.zeros(size),
                    np.zeros(size),
                )
            ),
            np.concatenate(
                (
                    np.full(2 * size, np.inf),
                    np.ones(size),
                )
            ),
        )

        second_result = milp(
            c=second_objective,
            integrality=np.ones(second_variable_count),
            bounds=second_bounds,
            constraints=cls._make_linear_constraint(
                rows,
                lower_bounds,
                upper_bounds,
            ),
            options={"disp": False},
        )

        if not second_result.success:
            return np.rint(
                first_result.x[:size]
            ).astype(np.int64)

        return np.rint(
            second_result.x[:size]
        ).astype(np.int64)

    @staticmethod
    def _find_components(
        frame: pd.DataFrame,
        use_vlines: bool,
        use_hlines: bool,
    ) -> list[list[int]]:
        """Find connected row components created by price-line links."""
        size = len(frame)
        parents = list(range(size))

        def find(position: int) -> int:
            while parents[position] != position:
                parents[position] = parents[parents[position]]
                position = parents[position]

            return position

        def union(left_position: int, right_position: int) -> None:
            left_root = find(left_position)
            right_root = find(right_position)

            if left_root != right_root:
                parents[right_root] = left_root

        line_columns = []

        if use_vlines:
            line_columns.append("vline")

        if use_hlines:
            line_columns.append("hline")

        for column in line_columns:
            mask = CocaCola._line_mask(frame[column])

            for _, group in frame.loc[mask].groupby(
                column,
                sort=False,
            ):
                positions = group.index.to_list()

                if len(positions) < 2:
                    continue

                first_position = positions[0]

                for position in positions[1:]:
                    union(first_position, position)

        components: dict[int, list[int]] = {}

        for position in range(size):
            root = find(position)
            components.setdefault(root, []).append(position)

        return list(components.values())

    @classmethod
    def _optimize_frame(
        cls,
        df: pd.DataFrame,
        use_vlines: bool,
        use_hlines: bool,
    ) -> pd.DataFrame:
        """Optimize all independent connected components."""
        result = df.copy()
        frame = df.reset_index(drop=True)

        components = cls._find_components(
            frame,
            use_vlines,
            use_hlines,
        )

        for positions in components:
            if len(positions) < 2:
                continue

            component = frame.loc[positions].copy()
            component.index = range(len(component))

            corrected_prices = cls._solve_component(
                component,
                use_vlines,
                use_hlines,
            )

            price_column = result.columns.get_loc("price")

            result.iloc[
                positions,
                price_column,
            ] = corrected_prices

        result["price"] = result["price"].astype(int)

        return result

    @staticmethod
    def fix_vlines(df: pd.DataFrame) -> pd.DataFrame:
        """Correct all vertical price lines."""
        return CocaCola._optimize_frame(
            df,
            use_vlines=True,
            use_hlines=False,
        )

    @staticmethod
    def fix_hlines(df: pd.DataFrame) -> pd.DataFrame:
        """Correct all horizontal price lines."""
        return CocaCola._optimize_frame(
            df,
            use_vlines=False,
            use_hlines=True,
        )

    def fit(
        self,
        df: pd.DataFrame,
        y: pd.Series = None,
    ) -> CocaCola:
        """Return the stateless fitted transformer."""
        return self

    def transform(
        self,
        df: pd.DataFrame,
        y: pd.Series = None,
    ) -> pd.DataFrame:
        """Apply vertical correction first and horizontal correction second."""
        df = self.fix_vlines(df)
        df = self.fix_hlines(df)

        return df

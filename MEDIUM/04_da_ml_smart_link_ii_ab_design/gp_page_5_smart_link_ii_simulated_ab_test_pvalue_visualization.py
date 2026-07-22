"""Compare p-value distributions in simulated A/A and A/B tests."""

import matplotlib.pyplot as plt
import numpy as np

from gp_page_5_smart_link_ii_simulated_ab_test_solution import (
    cpc_sample,
    t_test,
)


def simulate_p_values(
    n_simulations: int,
    n_samples: int,
    conversion_rate: float,
    mde: float,
    reward_avg: float,
    reward_std: float,
    alpha: float = 0.05,
) -> tuple[np.ndarray, np.ndarray]:
    """Return p-values from simulated A/A and A/B experiments."""
    aa_p_values = np.zeros(n_simulations)
    ab_p_values = np.zeros(n_simulations)
    test_conversion_rate = conversion_rate * (1.0 + mde)

    for simulation_index in range(n_simulations):
        aa_cpc_a = cpc_sample(
            n_samples,
            conversion_rate,
            reward_avg,
            reward_std,
        )
        aa_cpc_b = cpc_sample(
            n_samples,
            conversion_rate,
            reward_avg,
            reward_std,
        )

        _, aa_p_value = t_test(
            aa_cpc_a,
            aa_cpc_b,
            alpha,
        )
        aa_p_values[simulation_index] = aa_p_value

        ab_cpc_a = cpc_sample(
            n_samples,
            conversion_rate,
            reward_avg,
            reward_std,
        )
        ab_cpc_b = cpc_sample(
            n_samples,
            test_conversion_rate,
            reward_avg,
            reward_std,
        )

        _, ab_p_value = t_test(
            ab_cpc_a,
            ab_cpc_b,
            alpha,
        )
        ab_p_values[simulation_index] = ab_p_value

    return aa_p_values, ab_p_values


def plot_p_value_comparison(
    aa_p_values: np.ndarray,
    ab_p_values: np.ndarray,
    output_path: str = (
        "gp_page_5_smart_link_ii_simulated_ab_test_"
        "pvalue_comparison.png"
    ),
) -> None:
    """Plot and save A/A and A/B p-value distributions."""
    figure, axis = plt.subplots(figsize=(10, 6))

    axis.hist(
        aa_p_values,
        bins=20,
        density=True,
        alpha=0.6,
        label="A/A p-values",
    )
    axis.hist(
        ab_p_values,
        bins=20,
        density=True,
        alpha=0.6,
        label="A/B p-values",
    )
    axis.axvline(
        x=0.05,
        linestyle="--",
        label="alpha = 0.05",
    )

    axis.set_title("P-value distributions: A/A versus A/B")
    axis.set_xlabel("p-value")
    axis.set_ylabel("Density")
    axis.set_xlim(0.0, 1.0)
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_path, dpi=150)
    plt.close(figure)


if __name__ == "__main__":
    np.random.seed(42)

    aa_values, ab_values = simulate_p_values(
        n_simulations=5_000,
        n_samples=2_000,
        conversion_rate=0.10,
        mde=0.20,
        reward_avg=10.0,
        reward_std=2.0,
        alpha=0.05,
    )

    print(
        "A/A type I error rate:",
        np.mean(aa_values < 0.05),
    )
    print(
        "A/B power:",
        np.mean(ab_values < 0.05),
    )
    print(
        "A/B type II error rate:",
        np.mean(ab_values >= 0.05),
    )

    plot_p_value_comparison(
        aa_values,
        ab_values,
    )

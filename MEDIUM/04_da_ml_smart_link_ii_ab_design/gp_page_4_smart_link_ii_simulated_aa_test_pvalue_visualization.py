"""Visualize p-values produced by simulated A/A experiments."""

import matplotlib.pyplot as plt
import numpy as np

from gp_page_4_smart_link_ii_simulated_aa_test_solution import (
    cpc_sample,
    t_test,
)


def simulate_p_values(
    n_simulations: int,
    n_samples: int,
    conversion_rate: float,
    reward_avg: float,
    reward_std: float,
    alpha: float = 0.05,
) -> np.ndarray:
    """Run A/A simulations and return all generated p-values."""
    p_values = np.zeros(n_simulations)

    for simulation_index in range(n_simulations):
        cpc_a = cpc_sample(
            n_samples,
            conversion_rate,
            reward_avg,
            reward_std,
        )
        cpc_b = cpc_sample(
            n_samples,
            conversion_rate,
            reward_avg,
            reward_std,
        )

        _, p_value = t_test(cpc_a, cpc_b, alpha)
        p_values[simulation_index] = p_value

    return p_values


def plot_p_values(
    p_values: np.ndarray,
    output_path: str = (
        "gp_page_4_smart_link_ii_simulated_aa_test_"
        "pvalue_distribution.png"
    ),
) -> None:
    """Plot and save the p-value distribution."""
    figure, axis = plt.subplots(figsize=(10, 6))

    axis.hist(
        p_values,
        bins=20,
        density=True,
        edgecolor="black",
    )
    axis.axhline(
        y=1.0,
        linestyle="--",
        label="Uniform(0, 1) density",
    )
    axis.axvline(
        x=0.05,
        linestyle=":",
        label="alpha = 0.05",
    )

    axis.set_title("P-value distribution in a simulated A/A test")
    axis.set_xlabel("p-value")
    axis.set_ylabel("Density")
    axis.set_xlim(0.0, 1.0)
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_path, dpi=150)
    plt.close(figure)


if __name__ == "__main__":
    np.random.seed(42)

    simulated_p_values = simulate_p_values(
        n_simulations=10_000,
        n_samples=1_000,
        conversion_rate=0.10,
        reward_avg=10.0,
        reward_std=2.0,
        alpha=0.05,
    )

    print(
        "Estimated type I error rate:",
        np.mean(simulated_p_values < 0.05),
    )

    plot_p_values(simulated_p_values)

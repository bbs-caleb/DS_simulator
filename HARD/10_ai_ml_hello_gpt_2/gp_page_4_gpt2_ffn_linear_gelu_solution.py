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

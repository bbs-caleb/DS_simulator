"""Self-attention components for GPT-2."""

import numpy as np


def linear(x, w, b):
    """Apply a linear transformation to the input."""
    return x @ w + b


def softmax(x):
    """Apply a numerically stable softmax over the last axis."""
    shifted_x = x - np.max(x, axis=-1, keepdims=True)
    exp_x = np.exp(shifted_x)
    return exp_x / np.sum(exp_x, axis=-1, keepdims=True)


def attention(q, k, v):
    """Apply scaled dot-product attention."""
    scores = q @ k.T / np.sqrt(q.shape[-1])
    return softmax(scores) @ v


def self_attention(x, c_attn, c_proj):
    """Apply GPT-2 single-head self-attention."""
    x = linear(x, **c_attn)
    q, k, v = np.split(x, 3, axis=-1)
    x = attention(q, k, v)
    return linear(x, **c_proj)

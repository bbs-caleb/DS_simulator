"""Masked multi-head attention components for GPT-2."""

import numpy as np


def linear(x, w, b):
    """Apply a linear transformation to the input."""
    return x @ w + b


def softmax(x):
    """Apply a numerically stable softmax over the last axis."""
    exp_x = np.exp(
        x - np.max(
            x,
            axis=-1,
            keepdims=True,
        )
    )
    return exp_x / np.sum(
        exp_x,
        axis=-1,
        keepdims=True,
    )


def attention(q, k, v, mask):
    """Apply masked scaled dot-product attention."""
    scores = q @ k.T / np.sqrt(q.shape[-1])
    return softmax(scores + mask) @ v


def causal_self_attention(x, c_attn, c_proj):
    """Apply single-head causal self-attention."""
    x = linear(x, **c_attn)
    q, k, v = np.split(x, 3, axis=-1)

    causal_mask = (1 - np.tri(x.shape[0])) * -1e10

    x = attention(q, k, v, causal_mask)
    return linear(x, **c_proj)


def mha(x, c_attn, c_proj, n_head):
    """Apply masked multi-head self-attention."""
    x = linear(x, **c_attn)
    qkv = np.split(x, 3, axis=-1)

    split_qkv = [
        np.split(part, n_head, axis=-1)
        for part in qkv
    ]
    qkv_heads = list(zip(*split_qkv))

    causal_mask = (1 - np.tri(x.shape[0])) * -1e10

    out_heads = [
        attention(q, k, v, causal_mask)
        for q, k, v in qkv_heads
    ]

    x = np.hstack(out_heads)
    return linear(x, **c_proj)

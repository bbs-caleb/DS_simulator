"""Minimal NumPy implementation of a GPT-2 forward pass."""

import numpy as np


def gelu(x):
    """Apply the GELU activation used in GPT-2."""
    return 0.5 * x * (
        1
        + np.tanh(
            np.sqrt(2 / np.pi)
            * (x + 0.044715 * x**3)
        )
    )


def layer_norm(x, g, b, eps: float = 1e-5):
    """Normalize the last axis and apply scale and bias."""
    mean = np.mean(x, axis=-1, keepdims=True)
    variance = np.var(x, axis=-1, keepdims=True)
    x = (x - mean) / np.sqrt(variance + eps)
    return g * x + b


def ffn(x, c_fc, c_proj):
    """Apply the position-wise feed-forward network."""
    hidden = gelu(linear(x, **c_fc))
    return linear(hidden, **c_proj)


def linear(x, w, b):
    """Apply a linear transformation."""
    return x @ w + b


def softmax(x):
    """Apply a numerically stable softmax."""
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


def mha(x, c_attn, c_proj, n_head):
    """Apply masked multi-head self-attention."""
    x = linear(x, **c_attn)
    qkv = np.split(x, 3, axis=-1)

    qkv_heads = [
        np.split(part, n_head, axis=-1)
        for part in qkv
    ]

    causal_mask = (1 - np.tri(x.shape[0])) * -1e10

    out_heads = [
        attention(q, k, v, causal_mask)
        for q, k, v in zip(*qkv_heads)
    ]

    x = np.hstack(out_heads)
    return linear(x, **c_proj)


def transformer_block(
    x,
    mlp,
    attn,
    ln_1,
    ln_2,
    n_head,
):
    """Apply one pre-layer-normalized GPT-2 decoder block."""
    x = x + mha(
        layer_norm(x, **ln_1),
        **attn,
        n_head=n_head,
    )
    x = x + ffn(
        layer_norm(x, **ln_2),
        **mlp,
    )
    return x


def gpt2(inputs, wte, wpe, blocks, ln_f, n_head):
    """Run GPT-2 and return logits for the next token."""
    x = wte[inputs] + wpe[range(len(inputs))]

    for block in blocks:
        x = transformer_block(
            x,
            n_head=n_head,
            **block,
        )

    x = layer_norm(x, **ln_f)
    logits = x @ wte.T

    return logits[-1]

from typing import Callable
from typing import List

import numpy as np


def generate(
    llm: Callable[[List[int]], List[float]],
    prompt: List[str],
    n_tokens: int,
    vocab: List[str],
    top_k: int = 50,
    top_p: float = 0.75,
    temperature: float = 1.1,
    random_state: int = 0,
) -> List[str]:
    """Generate a sequence of tokens from a prompt using a language model."""
    np.random.seed(random_state)

    input_ids = [vocab.index(token) for token in prompt]
    generated_tokens = []

    for _ in range(n_tokens):
        logits = np.asarray(llm(input_ids), dtype=float)
        logits = logits / temperature

        shifted_logits = logits - np.max(logits)
        probabilities = np.exp(shifted_logits)
        probabilities /= probabilities.sum()

        indices = np.argsort(probabilities)[-top_k:]
        probabilities = probabilities[indices]
        probabilities /= probabilities.sum()

        order = np.argsort(probabilities)[::-1]
        indices = indices[order]
        probabilities = probabilities[order]

        cumulative_probabilities = np.cumsum(probabilities)
        threshold = np.min(
            cumulative_probabilities[
                cumulative_probabilities >= top_p
            ]
        )
        mask = cumulative_probabilities <= threshold

        probabilities = probabilities[mask]
        probabilities /= probabilities.sum()
        indices = indices[mask]

        next_token_id = int(
            np.random.choice(indices, p=probabilities)
        )

        generated_tokens.append(vocab[next_token_id])
        input_ids.append(next_token_id)

    return generated_tokens

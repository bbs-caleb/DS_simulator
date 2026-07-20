from typing import Callable
from typing import List

import numpy as np
from gpt2 import gpt2
from util import load_encoder_hparams_and_weights


def generate(
    llm: Callable[[List[int]], List[float]],
    input_ids: List[int],
    n_tokens: int,
    top_k: int = 1,
    top_p: float = 0.75,
    temperature: float = 1.0,
    weights: dict = None,
    random_state: int = 0,
) -> List[int]:
    """Generate a sequence of tokens from a prompt using a language model."""
    np.random.seed(random_state)
    output_ids = []

    for _ in range(n_tokens):
        logits = llm(input_ids + output_ids, **weights)
        logits = np.array(logits)
        logits = logits / temperature
        probabilities = np.exp(logits)
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

        next_id = int(
            np.random.choice(
                indices,
                p=probabilities,
            )
        )
        output_ids.append(next_id)

    return output_ids


def main(
    prompt: str,
    n_tokens: int = 40,
    model_size: str = "124M",
    models_dir: str = "models",
):
    """Generate a text continuation with GPT-2."""
    encoder, hparams, weights = load_encoder_hparams_and_weights(
        model_size,
        models_dir,
    )

    input_ids = encoder.encode(prompt)
    assert len(input_ids) + n_tokens < hparams["n_ctx"]

    output_ids = generate(
        llm=gpt2,
        input_ids=input_ids,
        n_tokens=n_tokens,
        top_k=50,
        top_p=0.8,
        temperature=0.75,
        random_state=0,
        weights=weights,
    )

    output = encoder.decode(output_ids)

    return output


if __name__ == "__main__":
    import fire

    fire.Fire(main)

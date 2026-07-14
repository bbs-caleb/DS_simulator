"""LLM assistant for working with a Replicate-hosted multimodal model."""

import json
import os
import time
from typing import Any, Dict

import replicate
from dotenv import load_dotenv


class LLMAssistant:
    """Interact with a multimodal LLM through the Replicate API."""

    def __init__(
        self,
        system_prompt: str,
        model_id: str,
        temperature: float = 0.01,
        max_tokens: int = 1024,
    ):
        """
        Initialize the assistant.

        Raises:
            ValueError: If REPLICATE_API_TOKEN is missing or empty.
        """
        load_dotenv()

        self.token = os.getenv("REPLICATE_API_TOKEN")

        if not self.token:
            raise ValueError(
                "Environment variable REPLICATE_API_TOKEN is missing or empty."
            )

        self.system_prompt = system_prompt
        self.model_id = model_id
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = replicate.Client(api_token=self.token)

    def _generate_input(self, image_Base64: str) -> Dict[str, Any]:
        """Build the input payload expected by the LLaVA model."""
        return {
            "top_p": 1,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "image": f"data:image/jpeg;base64,{image_Base64}",
            "prompt": self.system_prompt,
        }

    def _parse_response(self, output: str) -> Dict[str, Any]:
        """Parse a JSON model response into the service response format."""
        try:
            result = json.loads(output)
        except (json.JSONDecodeError, TypeError) as error:
            return {
                "status": "error",
                "result": {},
                "error": str(error),
            }

        if not isinstance(result, dict):
            return {
                "status": "error",
                "result": {},
                "error": "The model response must be a JSON object.",
            }

        return {
            "status": "success",
            "result": result,
            "error": "",
        }

    def generate_response(
        self,
        image_Base64: str,
        timeout: int = 10,
    ) -> Dict[str, Any]:
        """Generate and parse a response for a Base64-encoded image."""
        if timeout < 1:
            raise ValueError("Timeout must be at least 1 second.")

        prediction = self.client.predictions.create(
            version=self.model_id,
            input=self._generate_input(image_Base64),
        )

        started_at = time.time()
        terminal_statuses = {"succeeded", "failed", "canceled"}

        while prediction.status not in terminal_statuses:
            if time.time() - started_at >= timeout:
                if hasattr(prediction, "cancel"):
                    prediction.cancel()

                return {
                    "status": "error",
                    "result": {},
                    "error": (
                        f"Prediction timeout exceeded after {timeout} seconds."
                    ),
                }

            time.sleep(0.1)
            reloaded_prediction = prediction.reload()

            if reloaded_prediction is not None:
                prediction = reloaded_prediction

        if prediction.status != "succeeded":
            error = getattr(prediction, "error", None)
            error_message = error or (
                f"Prediction finished with status '{prediction.status}'."
            )

            return {
                "status": "error",
                "result": {},
                "error": str(error_message),
            }

        output = prediction.output

        if isinstance(output, str):
            raw_output = output
        elif output is None:
            raw_output = ""
        else:
            raw_output = "".join(str(part) for part in output)

        return self._parse_response(raw_output)

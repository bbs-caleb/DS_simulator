"""FastAPI service for validating an image and calling an LLM assistant."""

import base64
import binascii
from typing import Any

from fastapi import FastAPI, HTTPException, Request


class LLMAssistant:
    """
    Stub class to simulate the behavior of a real LLM assistant.
    """

    def generate_response(self, image_data: str, timeout: int = 10) -> Any:
        """
        Simulate generation of nutritional information from image data.
        """
        _ = image_data, timeout

        return {
            "status": "success",
            "result": {
                "calories": 100,
                "proteins": 10,
                "fats": 20,
                "carbohydrates": 30,
            },
            "error": "",
        }


# Initialize FastAPI app.
app = FastAPI()

# Create one assistant instance that is used by the endpoint.
assistant = LLMAssistant()


@app.post("/generate_response")
async def generate_response(request: Request) -> Any:
    """
    Generate nutritional information for a Base64-encoded image.

    The request body must contain the ``image_base64`` field.

    Raises:
        HTTPException:
            - 400 if the Base64 image string is invalid.
            - 504 if the assistant raises TimeoutError.
            - 500 if any other unexpected error occurs.
    """
    try:
        request_data = await request.json()

        if not isinstance(request_data, dict):
            raise HTTPException(
                status_code=400,
                detail="Invalid request body",
            )

        image_base64 = request_data.get("image_base64")

        if not isinstance(image_base64, str) or not image_base64:
            raise HTTPException(
                status_code=400,
                detail="Invalid Base64 image data",
            )

        try:
            base64.b64decode(image_base64, validate=True)
        except (binascii.Error, ValueError) as error:
            raise HTTPException(
                status_code=400,
                detail="Invalid Base64 image data",
            ) from error

        return assistant.generate_response(image_base64, timeout=10)

    except HTTPException:
        raise
    except TimeoutError as error:
        raise HTTPException(
            status_code=504,
            detail="The LLM assistant request timed out",
        ) from error
    except Exception as error:  # pylint: disable=broad-exception-caught
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred",
        ) from error

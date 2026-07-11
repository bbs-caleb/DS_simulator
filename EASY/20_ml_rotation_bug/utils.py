import cv2
import numpy as np


def rotated_image(image: np.ndarray, angle: int = 45) -> np.ndarray:
    """Rotate image by angle degrees."""
    height, width = image.shape[:2]
    center = (width / 2, height / 2)
    transform = cv2.getRotationMatrix2D(center, angle, 1)
    result = cv2.warpAffine(image, transform, (width, height))
    return result

import numpy as np

import utils


def test_rotated_image():
    image = np.zeros((100, 200, 3), dtype=np.uint8)

    result = utils.rotated_image(image, angle=0)

    assert result.shape == image.shape

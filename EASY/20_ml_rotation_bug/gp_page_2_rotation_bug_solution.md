# ML: ROTATION BUG — исправление бага

## Что требуется на этой странице

На предыдущей странице мы написали тест, который обнаруживает ошибку в функции поворота изображения.

Теперь нужно исправить функцию `rotated_image`, сохранив исходный API:

```python
def rotated_image(image: np.ndarray, angle: int = 45) -> np.ndarray:
```

Нельзя:

- менять имя функции;
- менять порядок аргументов;
- удалять значение `angle=45`;
- возвращать объект другого типа;
- переименовывать обязательный файл `utils.py`.

## Готовое решение

```python
import cv2
import numpy as np


def rotated_image(image: np.ndarray, angle: int = 45) -> np.ndarray:
    """Rotate image by angle degrees."""
    height, width = image.shape[:2]
    center = (width / 2, height / 2)
    transform = cv2.getRotationMatrix2D(center, angle, 1)
    result = cv2.warpAffine(image, transform, (width, height))
    return result
```

## Какой файл загружать

В проверяющую систему нужно загрузить:

```text
utils.py
```

## Что было исправлено

В исходной реализации было:

```python
width, height, channels = image.shape
```

Но NumPy возвращает форму изображения в порядке:

```text
height, width, channels
```

Теперь используется:

```python
height, width = image.shape[:2]
```

После этого центр передаётся в OpenCV в формате:

```text
(x, y) = (width / 2, height / 2)
```

А размер выходного изображения передаётся в формате:

```text
(width, height)
```

Таким образом:

- NumPy читается в порядке `(height, width)`;
- OpenCV получает координаты в порядке `(width, height)`;
- форма результата сохраняется;
- тест с прямоугольным изображением проходит.

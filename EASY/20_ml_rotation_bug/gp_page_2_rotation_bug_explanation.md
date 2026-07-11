# ML: ROTATION BUG — подробное объяснение исправления

# 1. Исходная функция

Нам была дана функция:

```python
import cv2
import numpy as np


def rotated_image(image: np.ndarray, angle: int = 45) -> np.ndarray:
    """Rotate image by angle degrees."""
    width, height, channels = image.shape
    transform = cv2.getRotationMatrix2D((height / 2, width / 2), angle, 1)
    result = cv2.warpAffine(image, transform, (width, height))
    return result
```

На первый взгляд функция выглядит логично:

1. получает размер изображения;
2. рассчитывает центр;
3. создаёт матрицу поворота;
4. применяет поворот;
5. возвращает результат.

Но ошибка находится в порядке размеров.

---

# 2. Как NumPy хранит изображение

Цветное изображение обычно является трёхмерным массивом:

```text
(height, width, channels)
```

Например:

```python
image.shape == (100, 200, 3)
```

Это означает:

- высота — 100 пикселей;
- ширина — 200 пикселей;
- каналов — 3.

Очень важно:

```text
первое число — height
второе число — width
третье число — channels
```

Поэтому строка:

```python
width, height, channels = image.shape
```

неправильная.

При форме:

```text
(100, 200, 3)
```

Python присваивал:

```text
width = 100
height = 200
channels = 3
```

Хотя должно быть:

```text
height = 100
width = 200
channels = 3
```

---

# 3. Почему используется `image.shape[:2]`

В исправленной функции написано:

```python
height, width = image.shape[:2]
```

Разберём выражение по частям.

## `image.shape`

Для цветного изображения:

```python
image.shape
```

может вернуть:

```text
(100, 200, 3)
```

## `[:2]`

Срез:

```python
image.shape[:2]
```

берёт только первые два значения:

```text
(100, 200)
```

То есть:

```text
(height, width)
```

## Присваивание

```python
height, width = image.shape[:2]
```

получаем:

```text
height = 100
width = 200
```

Теперь переменные соответствуют реальному смыслу значений.

---

# 4. Почему мы не сохраняем `channels`

В старой функции было:

```python
width, height, channels = image.shape
```

Но переменная `channels` нигде дальше не использовалась.

Нам нужны только:

- высота;
- ширина.

Поэтому достаточно:

```python
height, width = image.shape[:2]
```

Это делает код:

- короче;
- понятнее;
- чище;
- устойчивее.

Кроме того, такой вариант работает не только с цветным, но и с двумерным изображением в градациях серого:

```text
(height, width)
```

---

# 5. Расчёт центра изображения

Исправленный код:

```python
center = (width / 2, height / 2)
```

OpenCV задаёт точку в формате:

```text
(x, y)
```

Где:

- `x` — координата по горизонтали;
- `y` — координата по вертикали.

Горизонтальное направление связано с шириной:

```text
x = width
```

Вертикальное направление связано с высотой:

```text
y = height
```

Поэтому центр:

```text
(width / 2, height / 2)
```

Для изображения:

```text
height = 100
width = 200
```

центр равен:

```text
(200 / 2, 100 / 2)
```

то есть:

```text
(100, 50)
```

---

# 6. Создание матрицы поворота

Код:

```python
transform = cv2.getRotationMatrix2D(center, angle, 1)
```

Функция получает три аргумента.

## Первый аргумент — `center`

```python
center
```

Точка, вокруг которой вращается изображение.

## Второй аргумент — `angle`

```python
angle
```

Угол поворота в градусах.

По умолчанию:

```python
angle = 45
```

## Третий аргумент — `1`

```python
1
```

Это коэффициент масштаба.

Значение:

```text
1
```

означает:

```text
не увеличивать и не уменьшать изображение
```

Например:

- `0.5` — уменьшить в два раза;
- `2` — увеличить в два раза;
- `1` — оставить исходный масштаб.

Результатом является матрица аффинного преобразования.

---

# 7. Применение преобразования

Код:

```python
result = cv2.warpAffine(image, transform, (width, height))
```

`cv2.warpAffine` получает:

1. исходное изображение;
2. матрицу преобразования;
3. размер выходного изображения.

## Главная особенность OpenCV

Размер передаётся в порядке:

```text
(width, height)
```

Это отличается от `image.shape`, где порядок:

```text
(height, width)
```

Именно на этом различии была построена ошибка.

Исправленный код передаёт:

```python
(width, height)
```

где переменные уже содержат правильные значения.

Для нашего примера:

```text
width = 200
height = 100
```

OpenCV получает:

```text
(200, 100)
```

Результирующий NumPy-массив будет иметь форму:

```text
(100, 200, 3)
```

То есть исходная форма сохраняется.

---

# 8. Полный путь размеров

Пусть вход:

```python
image.shape == (100, 200, 3)
```

## Шаг 1

```python
height, width = image.shape[:2]
```

Результат:

```text
height = 100
width = 200
```

## Шаг 2

```python
center = (width / 2, height / 2)
```

Результат:

```text
center = (100, 50)
```

## Шаг 3

```python
cv2.warpAffine(image, transform, (width, height))
```

OpenCV получает:

```text
output width = 200
output height = 100
```

## Шаг 4

NumPy показывает выход:

```text
(height, width, channels)
```

Результат:

```text
(100, 200, 3)
```

Входная и выходная формы совпали.

---

# 9. Почему предыдущий тест теперь проходит

Тест:

```python
import numpy as np

import utils


def test_rotated_image():
    image = np.zeros((100, 200, 3), dtype=np.uint8)

    result = utils.rotated_image(image, angle=0)

    assert result.shape == image.shape
```

## Входная форма

```text
image.shape = (100, 200, 3)
```

## После исправления

```text
result.shape = (100, 200, 3)
```

## Проверка

```python
assert (100, 200, 3) == (100, 200, 3)
```

Условие истинно.

Тест проходит.

---

# 10. Почему мы не меняем размер canvas

При повороте на угол вроде `45°` углы исходного изображения могут обрезаться.

Можно было бы расширить canvas, чтобы вместить всё повёрнутое изображение.

Но это уже другая задача и другое поведение функции.

Текущий контракт предполагает:

```text
размер результата равен исходному размеру
```

Поэтому мы не добавляем:

- расчёт нового bounding box;
- дополнительный padding;
- перенос центра;
- изменение размера результата.

Для учебной задачи нужно исправить именно перепутанные размеры и не менять API.

---

# 11. Почему решение минимальное

Готовая функция:

```python
def rotated_image(image: np.ndarray, angle: int = 45) -> np.ndarray:
    """Rotate image by angle degrees."""
    height, width = image.shape[:2]
    center = (width / 2, height / 2)
    transform = cv2.getRotationMatrix2D(center, angle, 1)
    result = cv2.warpAffine(image, transform, (width, height))
    return result
```

В ней нет:

- ненужных проверок;
- исключений, которых не требует API;
- визуализации;
- чтения файлов;
- дополнительных зависимостей;
- изменения сигнатуры;
- сложной геометрии.

Каждая строка выполняет одну понятную задачу.

---

# 12. Соответствие PEP8

## Импорты

```python
import cv2
import numpy as np
```

Каждый импорт находится на отдельной строке.

## Пустые строки

Перед функцией верхнего уровня оставлены две пустые строки.

## Имена

```python
height
width
center
transform
result
```

Имена описывают содержимое переменных.

## Длина строк

Строки имеют нормальную длину.

## Docstring

```python
"""Rotate image by angle degrees."""
```

Функция содержит краткое описание.

---

# 13. Почему нельзя менять API

Проверяющая система будет импортировать функцию примерно так:

```python
from utils import rotated_image
```

И вызывать:

```python
rotated_image(image)
```

или:

```python
rotated_image(image, angle=90)
```

Поэтому сигнатура должна остаться:

```python
def rotated_image(image: np.ndarray, angle: int = 45) -> np.ndarray:
```

Если изменить имя функции или аргументы, скрытые тесты не смогут её вызвать.

Даже правильная математическая реализация тогда получит 0 баллов за несоответствие API.

---

# 14. Какие варианты исправления возможны

Можно было написать:

```python
height, width, channels = image.shape
```

Это исправляет порядок для цветных изображений.

Но `channels` не используется, и такой вариант не работает для двумерного grayscale-массива.

Лучший минимальный вариант:

```python
height, width = image.shape[:2]
```

Он:

- решает текущий баг;
- не создаёт неиспользуемую переменную;
- подходит и для цветных, и для grayscale-изображений;
- остаётся простым.

---

# 15. Финальный файл для загрузки

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

Загружать нужно файл:

```text
utils.py
```

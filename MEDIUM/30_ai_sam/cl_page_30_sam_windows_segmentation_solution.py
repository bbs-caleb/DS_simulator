"""Урок 30. AI: SAM — сегментация всех окон на фото с камеры дрона.

Пайплайн (Grounded-SAM):
    текст "window." --> Grounding DINO --> bounding boxes окон
    bounding boxes  --> SAM            --> бинарные маски окон
    все маски       --> объединение    --> одна маска mask.jpg

Запуск в Google Colab:
    !pip install -q -U transformers
    положить фото дрона рядом со скриптом под именем, указанным в IMAGE_PATH
    %run cl_page_30_sam_windows_segmentation_solution.py

Результат: файл mask.jpg — чёрный фон, белые области = окна.
"""

import numpy as np
import torch
from PIL import Image
from transformers import AutoModelForZeroShotObjectDetection
from transformers import AutoProcessor
from transformers import SamModel
from transformers import SamProcessor

# ----------------------------------------------------------------------------
# НАСТРОЙКИ. Меняются только эти строки.
# ----------------------------------------------------------------------------

IMAGE_PATH = "drone_photo.png"      # исходное фото с камеры дрона
OUTPUT_MASK_PATH = "mask.jpg"       # файл-ответ, который сдаём в тренажёр
OUTPUT_PREVIEW_PATH = "preview.jpg"  # картинка для глазами-проверки, НЕ сдаём

TEXT_PROMPT = "window."             # текстовый промпт, точка в конце обязательна
BOX_THRESHOLD = 0.30                # порог уверенности детектора по боксу
TEXT_THRESHOLD = 0.25               # порог соответствия бокса словам промпта

GDINO_MODEL_ID = "IDEA-Research/grounding-dino-base"
SAM_MODEL_ID = "facebook/sam-vit-huge"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# ----------------------------------------------------------------------------
# ШАГ 1. Загрузка изображения
# ----------------------------------------------------------------------------

def load_image(path):
    """Читает картинку с диска и приводит её к трёхканальному RGB."""
    image = Image.open(path).convert("RGB")
    print(f"Изображение загружено: размер {image.size[0]}x{image.size[1]} пикселей")
    return image


# ----------------------------------------------------------------------------
# ШАГ 2. Grounding DINO: текст -> bounding boxes
# ----------------------------------------------------------------------------

def detect_boxes(image, prompt, box_threshold, text_threshold):
    """Находит на картинке все объекты, описанные текстом prompt.

    Возвращает массив формы (N, 4) в формате xyxy:
    [x_левый_верхний, y_левый_верхний, x_правый_нижний, y_правый_нижний].
    """
    processor = AutoProcessor.from_pretrained(GDINO_MODEL_ID)
    model = AutoModelForZeroShotObjectDetection.from_pretrained(GDINO_MODEL_ID)
    model = model.to(DEVICE).eval()

    inputs = processor(images=image, text=prompt, return_tensors="pt").to(DEVICE)

    with torch.no_grad():
        outputs = model(**inputs)

    # Пороги передаём позиционно: имя третьего аргумента менялось между
    # версиями transformers (box_threshold -> threshold), позиция — нет.
    results = processor.post_process_grounded_object_detection(
        outputs,
        inputs.input_ids,
        box_threshold,
        text_threshold,
        target_sizes=[(image.size[1], image.size[0])],
    )

    boxes = results[0]["boxes"].detach().cpu().numpy()
    scores = results[0]["scores"].detach().cpu().numpy()
    print(f"Grounding DINO нашёл объектов: {len(boxes)}")
    if len(boxes) > 0:
        print(f"Уверенность: min={scores.min():.3f}, max={scores.max():.3f}")
    return boxes


# ----------------------------------------------------------------------------
# ШАГ 3. SAM: bounding boxes -> бинарные маски
# ----------------------------------------------------------------------------

def segment_boxes(image, boxes):
    """Превращает каждый bounding box в точную бинарную маску объекта.

    Возвращает массив формы (N, H, W) из значений True/False.
    """
    processor = SamProcessor.from_pretrained(SAM_MODEL_ID)
    model = SamModel.from_pretrained(SAM_MODEL_ID).to(DEVICE).eval()

    # SAM ждёт вложенный список: [ [box1, box2, ...] ] — внешний уровень
    # это батч картинок, у нас в батче одна картинка.
    input_boxes = [[[float(v) for v in box] for box in boxes]]

    inputs = processor(image, input_boxes=input_boxes, return_tensors="pt").to(DEVICE)

    with torch.no_grad():
        outputs = model(**inputs, multimask_output=False)

    masks = processor.image_processor.post_process_masks(
        outputs.pred_masks.detach().cpu(),
        inputs["original_sizes"].cpu(),
        inputs["reshaped_input_sizes"].cpu(),
    )[0]

    masks = masks.squeeze(1).numpy().astype(bool)
    print(f"SAM построил масок: {masks.shape[0]}, размер маски: {masks.shape[1]}x{masks.shape[2]}")
    return masks


# ----------------------------------------------------------------------------
# ШАГ 4. Объединение масок и сохранение ответа
# ----------------------------------------------------------------------------

def merge_masks(masks):
    """Склеивает N масок в одну: пиксель белый, если он попал хотя бы в одну маску."""
    merged = np.any(masks, axis=0)
    share = merged.mean() * 100
    print(f"Итоговая маска: белых пикселей {share:.2f}% от площади кадра")
    return merged


def save_mask(mask, path):
    """Сохраняет булеву маску как чёрно-белую картинку (0 — фон, 255 — объект)."""
    mask_uint8 = mask.astype(np.uint8) * 255
    mask_pil = Image.fromarray(mask_uint8)
    mask_pil.save(path)
    print(f"Маска сохранена: {path}")


def save_preview(image, mask, path):
    """Служебная картинка: исходное фото с подсвеченными окнами. В тренажёр НЕ сдаётся."""
    base = np.array(image).astype(np.float32)
    overlay = base.copy()
    overlay[mask] = 0.45 * overlay[mask] + 0.55 * np.array([255.0, 40.0, 40.0])
    Image.fromarray(overlay.astype(np.uint8)).save(path)
    print(f"Превью для самопроверки сохранено: {path}")


# ----------------------------------------------------------------------------
# ГЛАВНАЯ ФУНКЦИЯ
# ----------------------------------------------------------------------------

def main():
    """Полный проход: картинка -> боксы -> маски -> mask.jpg."""
    print(f"Устройство: {DEVICE}")

    image = load_image(IMAGE_PATH)

    boxes = detect_boxes(image, TEXT_PROMPT, BOX_THRESHOLD, TEXT_THRESHOLD)
    if len(boxes) == 0:
        raise ValueError(
            "Детектор не нашёл ни одного окна. Понизьте BOX_THRESHOLD "
            "(например до 0.20) или проверьте путь к картинке."
        )

    masks = segment_boxes(image, boxes)
    mask = merge_masks(masks)

    save_mask(mask, OUTPUT_MASK_PATH)
    save_preview(image, mask, OUTPUT_PREVIEW_PATH)


if __name__ == "__main__":
    main()

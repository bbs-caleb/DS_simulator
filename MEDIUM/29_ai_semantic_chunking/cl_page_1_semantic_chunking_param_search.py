"""Вспомогательный скрипт для подбора параметров (часть 2 задания).

ЭТОТ ФАЙЛ НЕ НУЖНО ЗАГРУЖАТЬ В ГРЕЙДЕР.
Скопируйте его содержимое в ячейку Colab-ноутбука и запустите.

Что он делает
-------------
1. Считает, сколько предложений и сколько расстояний даёт ваш текст.
2. Показывает таблицу "threshold -> сколько чанков получится".
   (Число чанков зависит ТОЛЬКО от threshold, буферы на него не влияют!)
3. Перебирает все комбинации buffer_back / buffer_forward / threshold
   и печатает те, что дают нужное вам число чанков, вместе с началом
   каждого чанка — чтобы вы сравнили с картинкой из задания.
"""

from itertools import product

from sentence_transformers import SentenceTransformer

# --- сюда подставьте класс из вашего решения ------------------------------
# from cl_page_1_semantic_chunking import SemanticSplitter
# В Colab класс уже определён в ячейке выше, импорт не нужен.

MODEL = SentenceTransformer("TaylorAI/bge-micro-v2")

# Сколько чанков должно получиться (посчитайте по картинке из задания:
# сколько цветных полос — столько чанков).
TARGET_CHUNKS = 6

# Диапазоны перебора
BUFFER_BACK_GRID = [0, 1, 2, 3]
BUFFER_FORWARD_GRID = [0, 1, 2, 3]
THRESHOLD_GRID = list(range(50, 100))


def report_structure(text):
    """Напечатать базовую структуру текста и формулу для threshold."""
    probe = SemanticSplitter(MODEL)  # noqa: F821
    sentences = probe._split_text(text)  # pylint: disable=protected-access
    n_sent = len(sentences)
    n_dist = n_sent - 1
    print(f"Предложений в тексте:      {n_sent}")
    print(f"Расстояний (n_sent - 1):   {n_dist}")
    print()
    print("Формула-подсказка:")
    print("  число чанков ~= round(n_dist * (1 - threshold/100)) + 1")
    print("  => threshold ~= 100 * (1 - (чанков - 1) / n_dist)")
    approx = 100 * (1 - (TARGET_CHUNKS - 1) / n_dist)
    print(f"  для {TARGET_CHUNKS} чанков threshold ~= {approx:.1f}")
    print()
    return sentences


def threshold_table(text):
    """Показать, сколько чанков даёт каждый threshold."""
    print("threshold -> количество чанков")
    seen = {}
    for thr in THRESHOLD_GRID:
        splitter = SemanticSplitter(  # noqa: F821
            MODEL, buffer_back=1, buffer_forward=1, threshold=thr
        )
        count = len(splitter.split(text))
        seen.setdefault(count, []).append(thr)
    for count in sorted(seen):
        thresholds = seen[count]
        print(f"  {count:>3} чанков : threshold {thresholds[0]}..{thresholds[-1]}")
    print()


def grid_search(text):
    """Перебрать все комбинации и показать подходящие."""
    print(f"=== Комбинации, дающие ровно {TARGET_CHUNKS} чанков ===\n")
    found = 0
    for back, forward, thr in product(
        BUFFER_BACK_GRID, BUFFER_FORWARD_GRID, THRESHOLD_GRID
    ):
        splitter = SemanticSplitter(  # noqa: F821
            MODEL, buffer_back=back, buffer_forward=forward, threshold=thr
        )
        chunks = splitter.split(text)
        if len(chunks) != TARGET_CHUNKS:
            continue
        found += 1
        print(f"back={back}  forward={forward}  threshold={thr}")
        for i, chunk in enumerate(chunks):
            print(f"    chunk {i + 1}: {chunk[:70]}...")
        print()
    if not found:
        print("Ничего не найдено — расширьте сетки или проверьте TARGET_CHUNKS.")


if __name__ == "__main__":
    # В Colab переменная `essay` уже определена в ячейке "Текст для работы".
    report_structure(essay)  # noqa: F821
    threshold_table(essay)  # noqa: F821
    grid_search(essay)  # noqa: F821

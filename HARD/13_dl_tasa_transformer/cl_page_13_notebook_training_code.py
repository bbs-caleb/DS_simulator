"""Заполненные train_model и evaluate_model для ноутбука урока 13.

В грейдер НЕ сдаётся - это код для запуска обучения в Google Colab.
Вставьте функции в соответствующие ячейки ноутбука.

Внимание: в первой ячейке ноутбука не хватает импорта DataLoader.
Замените строку `from torch.utils.data import Dataset` на:
    from torch.utils.data import Dataset, DataLoader
"""

import torch
from torch import nn


def train_model(model, train_dataloader, device, vocab_size,
                epochs=20, learning_rate=0.0001):
    """Обучение модели: предсказываем следующий товар в сессии."""
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    # pylint: disable=too-many-locals
    # Сигнатура задана шаблоном ноутбука - менять нельзя
    criterion = nn.CrossEntropyLoss(ignore_index=0)  # паддинг не штрафуем
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    for epoch in range(epochs):
        model.train()
        total_loss = 0

        for src_items, src_times, _ in train_dataloader:
            src_items = src_items.to(device)
            src_times = src_times.to(device)

            optimizer.zero_grad()

            # Автоэнкодерная постановка: цель = та же последовательность
            logits = model(src_items, src_times, src_items, src_times)

            # Сдвиг на один шаг: по позиции i предсказываем товар i+1
            predictions = logits[:, :-1, :].reshape(-1, vocab_size)
            targets = src_items[:, 1:].reshape(-1)

            loss = criterion(predictions, targets)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(f'Epoch {epoch + 1}/{epochs}, '
              f'Loss: {total_loss / len(train_dataloader)}')


def evaluate_model(model, dataloader, device, vocab_size):
    """Оценка точности предсказания следующего товара."""
    model.eval()
    correct_predictions = 0
    total_predictions = 0

    with torch.no_grad():
        for src_items, src_times, _ in dataloader:
            src_items = src_items.to(device)
            src_times = src_times.to(device)

            logits = model(src_items, src_times, src_items, src_times)

            predictions = logits[:, :-1, :].reshape(-1, vocab_size)
            targets = src_items[:, 1:].reshape(-1)

            predicted_items = predictions.argmax(dim=1)

            mask = targets != 0  # паддинг не считаем
            correct_predictions += (
                (predicted_items == targets) & mask
            ).sum().item()
            total_predictions += mask.sum().item()

    accuracy = correct_predictions / total_predictions
    print(f'Test Accuracy: {accuracy * 100:.2f}%')
    return accuracy

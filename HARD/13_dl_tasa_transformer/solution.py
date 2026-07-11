"""TASA Transformer: BERT-энкодер и трансформер-декодер для предсказания
следующего элемента в последовательности действий пользователя."""

from torch import nn
from transformers import BertModel


class TASA_Transformer(nn.Module):  # pylint: disable=invalid-name
    """
    Класс модели, использующей BERT-энкодер и трансформер-декодер
    для предсказания следующего элемента в последовательности.
    """

    def __init__(self, vocab_size, hidden_dim, nhead, num_layers):
        """
        Инициализация модели.

        Параметры:
        - vocab_size: Размер словаря.
        - hidden_dim: Размерность скрытого слоя.
        - nhead: Количество голов в механизме внимания.
        - num_layers: Количество слоев в декодере трансформера.
        """
        super().__init__()

        # 1. Предобученный BERT кодирует входные последовательности
        self.bert_encoder = BertModel.from_pretrained("bert-base-uncased")

        # 2. Слой декодера и стек из num_layers таких слоев
        decoder_layer = nn.TransformerDecoderLayer(
            d_model=hidden_dim, nhead=nhead, batch_first=True
        )
        self.transformer_decoder = nn.TransformerDecoder(
            decoder_layer, num_layers=num_layers
        )

        # 3. Полносвязный слой: скрытое состояние -> логиты по словарю
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, src_items, src_times, tgt_items, tgt_times):
        """
        Прямой проход модели.

        Параметры:
        - src_items: Входная последовательность элементов.
        - src_times: Временные метки для входной последовательности.
        - tgt_items: Целевая последовательность элементов.
        - tgt_times: Временные метки для целевой последовательности.

        Возвращает:
        - logits: Прогнозы следующего элемента в последовательности.
        """
        # pylint: disable=unused-argument

        # 1. Кодируем входную последовательность BERT-энкодером
        src_mask = (src_items > 0).long()  # 1 - реальный товар, 0 - паддинг
        src_encoded = self.bert_encoder(
            input_ids=src_items, attention_mask=src_mask
        ).last_hidden_state

        # 2. Кодируем целевую последовательность BERT-энкодером
        tgt_mask = (tgt_items > 0).long()
        tgt_encoded = self.bert_encoder(
            input_ids=tgt_items, attention_mask=tgt_mask
        ).last_hidden_state

        # 3. Декодер сопоставляет целевую последовательность с контекстом src
        decoded_output = self.transformer_decoder(tgt_encoded, src_encoded)

        # 4. Полносвязный слой переводит скрытые состояния в логиты
        logits = self.fc(decoded_output)
        return logits

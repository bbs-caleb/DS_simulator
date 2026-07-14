# Пошаговый разбор точного API класса

## 1. Путь к датасету

```python
self.dataset_path = dataset_path
```

Путь сохраняется в объекте, потому что `_load_data()` вызывается без аргументов:

```python
self._load_data()
```

## 2. Словарь данных

```python
self.data = self._load_data()
```

Формат:

```python
{
    "cornstarch": {
        "calories": 381.0,
        "fats": 0.1,
        "proteins": 0.26,
        "carbohydrates": 91.27,
    }
}
```

## 3. Список ингредиентов

```python
self._ingredients = list(self.data.keys())
```

Это список названий в том же порядке, в котором затем создаются embeddings.

## 4. Encoder

```python
self.encoder = SentenceTransformer(model_name)
```

Тест может проверять именно поле `encoder`, а не `model`.

## 5. Embeddings

```python
self._embeddings = self.encoder.encode(
    self._ingredients,
    convert_to_tensor=True,
)
```

Ключевая деталь: атрибут называется `_embeddings` с начальным подчёркиванием.

## 6. Semantic search

```python
cosine_scores = util.pytorch_cos_sim(
    ingredient_embedding,
    self._embeddings,
)
```

Запрос сравнивается со всей матрицей embeddings.

## 7. Порог semantic search

```python
threshold=0.6
```

Если максимальная близость ниже порога, метод возвращает `None`.

## 8. Default search type

```python
search_type="fuzzy"
```

Это значение по умолчанию из API шаблона.

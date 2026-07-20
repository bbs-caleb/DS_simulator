# Страница 3. Пошаговое объяснение решения `main.py`

## 1. Какие строки были пропущены в шаблоне

В исходном шаблоне были четыре пропуска:

```python
input_ids = _
```

```python
output_ids = generate(
    llm=_,
    input_ids=_,
    n_tokens=_,
    ...
    weights=_,
)
```

```python
output = _
```

Правильные значения:

```python
input_ids = encoder.encode(prompt)
```

```python
output_ids = generate(
    llm=gpt2,
    input_ids=input_ids,
    n_tokens=n_tokens,
    top_k=50,
    top_p=0.8,
    temperature=0.75,
    random_state=0,
    weights=weights,
)
```

```python
output = encoder.decode(output_ids)
```

---

# Часть I. Импорты

## 2. `Callable`

```python
from typing import Callable
```

`Callable` описывает объект, который можно вызвать как функцию.

В сигнатуре:

```python
llm: Callable[[List[int]], List[float]]
```

это означает:

- `llm` принимает `List[int]`;
- возвращает `List[float]`.

На практике `gpt2` принимает token IDs и веса модели, а возвращает logits.

---

## 3. `List`

```python
from typing import List
```

Используется для type hints:

```python
input_ids: List[int]
```

То есть `input_ids` — список целых чисел.

---

## 4. NumPy

```python
import numpy as np
```

Используется внутри `generate` для:

- seed;
- массивов;
- exponent;
- sorting;
- cumulative sum;
- sampling.

---

## 5. Импорт модели

```python
from gpt2 import gpt2
```

Теперь имя `gpt2` ссылается на функцию модели.

В предоставленной заглушке функция возвращает случайные logits. В полном варианте она должна реализовывать forward pass GPT-2.

---

## 6. Импорт loader

```python
from util import load_encoder_hparams_and_weights
```

Эта функция загружает:

- encoder;
- hparams;
- weights.

---

# Часть II. Функция `generate`

## 7. Почему ее не нужно писать заново

Задание прямо говорит, что генерация была реализована на предыдущем шаге.

В текущем файле функция уже присутствует. Основная задача — правильно вызвать ее из `main`.

Нельзя:

- удалить функцию;
- изменить ее сигнатуру;
- передавать ей строки вместо ID;
- забыть веса.

---

## 8. Что возвращает `generate`

Тип:

```python
List[int]
```

Пример:

```python
[383, 318, 257, 922, 13]
```

Это новые token IDs.

Это еще не финальная строка.

---

# Часть III. Функция `main`

## 9. Сигнатура

```python
def main(
    prompt: str,
    n_tokens: int = 40,
    model_size: str = "124M",
    models_dir: str = "models",
):
```

### `prompt`

Обычная строка пользователя.

### `n_tokens`

Сколько новых токенов сгенерировать.

Это не количество слов. Один токен может быть:

- словом;
- частью слова;
- пробелом вместе со словом;
- знаком пунктуации;
- последовательностью байтов.

### `model_size`

Размер GPT-2:

```text
124M
355M
774M
1558M
```

### `models_dir`

Каталог, где находятся файлы модели.

---

# Часть IV. Загрузка

## 10. Строка загрузки

```python
encoder, hparams, weights = (
    load_encoder_hparams_and_weights(
        model_size,
        models_dir,
    )
)
```

Python вызывает loader и распаковывает tuple из трех элементов.

Эквивалентно:

```python
result = load_encoder_hparams_and_weights(
    model_size,
    models_dir,
)

encoder = result[0]
hparams = result[1]
weights = result[2]
```

---

## 11. Что такое `encoder`

Это объект класса `Encoder`.

У него есть методы:

```python
encoder.encode(text)
encoder.decode(tokens)
```

---

## 12. Что такое `hparams`

Обычный словарь Python.

Примерно:

```python
{
    "n_vocab": 50257,
    "n_ctx": 1024,
    "n_embd": 768,
    "n_head": 12,
    "n_layer": 12,
}
```

---

## 13. Что такое `weights`

Вложенная структура NumPy-массивов.

Пример верхнего уровня:

```python
{
    "wte": ...,
    "wpe": ...,
    "blocks": [...],
    "ln_f": ...,
}
```

`wte` — token embedding matrix.

`wpe` — positional embedding matrix.

---

# Часть V. Токенизация

## 14. Правильная строка

```python
input_ids = encoder.encode(prompt)
```

Разберем справа налево.

### `prompt`

Строка:

```text
The best thing about AI is its ability to
```

### `encoder.encode(prompt)`

Encoder:

- разбивает строку;
- применяет byte encoding;
- применяет BPE;
- ищет ID токенов;
- возвращает список чисел.

### `input_ids =`

Сохраняет этот список в переменную.

---

## 15. Почему нельзя использовать `vocab.index`

В предыдущей учебной функции vocab был передан явно:

```python
vocab: List[str]
```

Здесь настоящая GPT-2 использует:

- JSON encoder;
- BPE merges;
- byte-level preprocessing.

Поэтому ручной `vocab.index` недостаточен.

Нужно использовать официальный объект encoder.

---

## 16. Пример типов

До токенизации:

```python
type(prompt)
# str
```

После токенизации:

```python
type(input_ids)
# list

type(input_ids[0])
# int
```

---

# Часть VI. Проверка контекста

## 17. Строка assert

```python
assert len(input_ids) + n_tokens < hparams["n_ctx"]
```

### `len(input_ids)`

Количество prompt-токенов.

### `n_tokens`

Количество будущих токенов.

### `hparams["n_ctx"]`

Максимальная длина контекста.

---

## 18. Почему учитывается будущая генерация

Допустим:

```text
prompt = 1000 токенов
n_tokens = 30
n_ctx = 1024
```

Prompt сам помещается:

```text
1000 < 1024
```

Но вместе с генерацией:

```text
1000 + 30 = 1030
```

Контекст переполняется.

Поэтому проверяется сумма.

---

# Часть VII. Вызов генерации

## 19. Полный вызов

```python
output_ids = generate(
    llm=gpt2,
    input_ids=input_ids,
    n_tokens=n_tokens,
    top_k=50,
    top_p=0.8,
    temperature=0.75,
    random_state=0,
    weights=weights,
)
```

---

## 20. `llm=gpt2`

Передаем саму функцию, а не результат ее вызова.

Правильно:

```python
llm=gpt2
```

Неправильно:

```python
llm=gpt2()
```

Почему?

`generate` сама должна вызывать модель на каждой итерации:

```python
logits = llm(...)
```

---

## 21. `input_ids=input_ids`

Левая часть:

```python
input_ids=
```

это имя параметра `generate`.

Правая часть:

```python
input_ids
```

это локальная переменная, полученная после tokenization.

Имена совпадают, но это разные роли.

---

## 22. `n_tokens=n_tokens`

Функция `main` получает число от пользователя и передает его генератору.

Нельзя написать:

```python
n_tokens=40
```

потому что тогда CLI-аргумент пользователя будет проигнорирован.

---

## 23. Sampling-параметры

```python
top_k=50
top_p=0.8
temperature=0.75
```

Они заданы условием шаблона.

Их не нужно менять.

---

## 24. `random_state=0`

Фиксирует генерацию для воспроизводимости.

При mock-модели и фиксированном seed результат повторяется.

---

## 25. `weights=weights`

Это критический параметр.

Внутри генерации:

```python
logits = llm(
    input_ids + output_ids,
    **weights,
)
```

`**weights` раскрывает словарь в именованные аргументы.

Mock-функция:

```python
def gpt2(inputs, **weights):
```

принимает их и использует:

```python
weights["wte"].shape[0]
```

чтобы определить размер vocabulary.

Без `weights=weights` mock-функция упадет:

```text
KeyError: 'wte'
```

---

# Часть VIII. Что происходит внутри цикла

## 26. Первый шаг

Допустим:

```python
input_ids = [464, 1266, 1517]
output_ids = []
```

Модель получает:

```python
input_ids + output_ids
```

то есть:

```python
[464, 1266, 1517]
```

Выбирается первый новый ID, например:

```python
287
```

Теперь:

```python
output_ids = [287]
```

---

## 27. Второй шаг

Модель получает:

```python
[464, 1266, 1517] + [287]
```

то есть:

```python
[464, 1266, 1517, 287]
```

Выбирается следующий ID.

Это авторегрессия.

---

# Часть IX. Декодирование

## 28. Правильная строка

```python
output = encoder.decode(output_ids)
```

### `output_ids`

Список новых token IDs.

### `encoder.decode`

Преобразует IDs обратно в UTF-8 строку.

### `output`

Готовая строка.

---

## 29. Почему декодируются только `output_ids`

Задача ожидает именно сгенерированное продолжение.

Если декодировать:

```python
input_ids + output_ids
```

результат включит исходный prompt.

Шаблон говорит:

> преобразование сгенерированных токенов обратно в строку.

Поэтому используется:

```python
encoder.decode(output_ids)
```

---

# Часть X. Возврат

## 30. `return output`

```python
return output
```

Функция должна вернуть строку, а не печатать ее.

Почему возврат лучше:

- тест может сравнить результат;
- CLI-библиотека сама выведет значение;
- функцию можно вызвать из другого Python-кода;
- результат можно передать в API.

---

# Часть XI. CLI

## 31. Блок запуска

```python
if __name__ == "__main__":
    import fire

    fire.Fire(main)
```

Когда файл запускается:

```bash
python main.py --prompt "Hello"
```

`__name__` равен `"__main__"`.

Fire преобразует CLI-аргументы в аргументы функции `main`.

---

## 32. Команда запуска

```bash
python main.py \
    --prompt "The best thing about AI is its ability to" \
    --n_tokens 10 \
    --model_size "124M" \
    --models_dir "models"
```

Fire вызовет примерно:

```python
main(
    prompt="The best thing about AI is its ability to",
    n_tokens=10,
    model_size="124M",
    models_dir="models",
)
```

---

# Часть XII. Что будет происходить при первом запуске

## 33. Проверка checkpoint

Utility вызывает:

```python
tf.train.latest_checkpoint(model_dir)
```

Если checkpoint отсутствует, начнется скачивание файлов модели.

Для GPT-2 это могут быть крупные файлы.

---

## 34. Загружаемые файлы

Среди них:

```text
checkpoint
encoder.json
hparams.json
model.ckpt.data-00000-of-00001
model.ckpt.index
model.ckpt.meta
vocab.bpe
```

### `encoder.json`

Сопоставление BPE tokens → IDs.

### `vocab.bpe`

Правила BPE merge.

### `hparams.json`

Архитектурные параметры.

### checkpoint-файлы

Обученные веса.

---

# Часть XIII. Проверки перед отправкой

## 35. Проверка синтаксиса

```bash
python -m py_compile \
    gp_page_3_gpt2_tokenization_generation_decoding_solution.py
```

Если команда ничего не вывела, синтаксис корректен.

---

## 36. Проверка Pylint

```bash
pylint \
    gp_page_3_gpt2_tokenization_generation_decoding_solution.py
```

Учтите, что локально Pylint может жаловаться на отсутствующие TensorFlow или Fire, если зависимости не установлены. В проверяющей системе зависимости могут быть предоставлены отдельно.

---

## 37. Что загружать

Нужно загрузить Python-файл:

```text
gp_page_3_gpt2_tokenization_generation_decoding_solution.py
```

Внутри уже содержится полный `main.py`.

---

# Часть XIV. Типичные ошибки

## 38. Ошибка: оставить `_`

```python
input_ids = _
```

`_` здесь не специальный placeholder Python. Если переменная `_` не определена, возникнет:

```text
NameError
```

---

## 39. Ошибка: передать prompt в generate

Неправильно:

```python
input_ids=prompt
```

`prompt` — строка.

`generate` ожидает:

```python
List[int]
```

---

## 40. Ошибка: вызвать encoder.decode до генерации

Нельзя декодировать prompt IDs и передавать строку модели.

Модель работает с числами.

---

## 41. Ошибка: забыть weights

Неправильно:

```python
output_ids = generate(
    llm=gpt2,
    input_ids=input_ids,
    n_tokens=n_tokens,
)
```

В этой версии `gpt2` ожидает weights через `**weights`.

---

## 42. Ошибка: передать hparams вместо weights

Неправильно:

```python
weights=hparams
```

`hparams` содержит числа конфигурации.

`weights` содержит обученные матрицы.

---

## 43. Ошибка: вернуть IDs

Неправильно:

```python
return output_ids
```

Задание ожидает строку.

---

## 44. Ошибка: декодировать input

Неправильно:

```python
output = encoder.decode(input_ids)
```

Это вернет исходный prompt, а не генерацию.

---

## 45. Ошибка: вызвать `gpt2` заранее

Неправильно:

```python
llm=gpt2(input_ids, **weights)
```

Так в `llm` попадет массив logits, а не callable-функция.

Правильно:

```python
llm=gpt2
```

---

# Часть XV. Связь с system design

## 46. API-контракт

Пример endpoint:

```http
POST /v1/generate
```

Request:

```json
{
  "prompt": "Product: wireless headphones...",
  "max_new_tokens": 80,
  "temperature": 0.75,
  "top_k": 50,
  "top_p": 0.8
}
```

Response:

```json
{
  "text": "Experience immersive audio...",
  "model_version": "gpt2-124m",
  "prompt_tokens": 24,
  "generated_tokens": 80
}
```

---

## 47. Компоненты сервиса

```text
Load Balancer
    ↓
Generation API
    ↓
Tokenizer
    ↓
Model Server
    ↓
Sampler
    ↓
Decoder
    ↓
Validation
    ↓
Response
```

---

## 48. Почему encoder должен соответствовать модели

Нельзя использовать случайный tokenizer с GPT-2 weights.

Token ID 100 в одном vocabulary может означать один token, а в другом — совершенно другой.

Если encoder и модель не совпадают:

- embeddings будут выбраны не для тех токенов;
- output IDs будут декодированы неправильно;
- текст станет бессмысленным.

Tokenizer является частью контракта модели.

---

# Часть XVI. Ответы на интервью

## 49. Как текст попадает в GPT

> Сначала tokenizer выполняет byte-level BPE и преобразует строку в token IDs. По каждому ID выбирается строка из token embedding matrix. К ней добавляется positional embedding соответствующей позиции. Полученные векторы проходят через последовательность causal Transformer decoder blocks.

---

## 50. Как GPT возвращает текст

> Последний hidden state преобразуется в logits по vocabulary. Из распределения выбирается следующий token ID. Он добавляется в контекст, и цикл повторяется. После генерации encoder/decoder mapping превращает IDs обратно в строку.

---

## 51. Token embedding против positional embedding

> Token embedding кодирует содержание токена. Positional embedding кодирует его положение в последовательности. В GPT-2 оба являются обучаемыми векторами одинаковой размерности и складываются перед первым Transformer-блоком.

---

## 52. Почему нужен causal mask

> Чтобы токен на позиции i не мог использовать информацию из будущих позиций. Это делает обучение совместимым с авторегрессивной генерацией слева направо.

---

# Часть XVII. Итоговый ответ задачи

Три обязательных блока:

```python
input_ids = encoder.encode(prompt)
```

```python
output_ids = generate(
    llm=gpt2,
    input_ids=input_ids,
    n_tokens=n_tokens,
    top_k=50,
    top_p=0.8,
    temperature=0.75,
    random_state=0,
    weights=weights,
)
```

```python
output = encoder.decode(output_ids)
```

Вся страница сводится к правильному соединению:

```text
USER TEXT
    ↓
ENCODER
    ↓
MODEL + GENERATION
    ↓
DECODER
    ↓
USER TEXT
```

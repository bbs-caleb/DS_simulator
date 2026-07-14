
# AI: Calorie Tracker — подробное объяснение 100-балльного решения

## 1. Что требовалось сделать

На этом шаге нужно было реализовать класс `LLMAssistant`, который связывает
наш FastAPI-сервис с мультимодальной моделью LLaVA через Replicate.

Класс должен уметь:

1. загрузить секретный токен Replicate из переменной окружения;
2. сформировать правильный набор входных параметров для модели;
3. отправить изображение и промпт в Replicate;
4. дождаться завершения prediction;
5. остановить ожидание при превышении `timeout`;
6. разобрать текстовый JSON-ответ модели;
7. вернуть единый словарь результата;
8. корректно обработать ошибки модели и ошибки JSON.

Итоговый поток данных:

```text
Streamlit
    ↓
FastAPI
    ↓
LLMAssistant.generate_response()
    ↓
Replicate API
    ↓
LLaVA
    ↓
JSON с КБЖУ
    ↓
FastAPI
    ↓
Streamlit
```

---

# 2. Почему нужен отдельный класс `LLMAssistant`

Без отдельного класса всю работу с Replicate пришлось бы писать прямо внутри
FastAPI-эндпоинта.

Это привело бы к смешиванию разных обязанностей:

- FastAPI принимал бы HTTP-запрос;
- FastAPI знал бы детали Replicate;
- FastAPI формировал бы input модели;
- FastAPI ожидал бы prediction;
- FastAPI разбирал бы JSON;
- FastAPI обрабатывал бы ошибки модели.

Такой код сложно тестировать и поддерживать.

Поэтому обязанности разделены:

## FastAPI отвечает за HTTP

Например:

```text
POST /generate_response
```

Он принимает запрос и возвращает HTTP-ответ.

## `LLMAssistant` отвечает за модель

Он знает:

- какой `model_id` использовать;
- какой промпт передать;
- как оформить Base64-изображение;
- как создать prediction;
- как дождаться результата;
- как разобрать ответ.

Это пример принципа **Single Responsibility Principle**:
один класс должен отвечать за одну область ответственности.

---

# 3. Полный код решения

```python
"""LLM assistant for working with a Replicate-hosted multimodal model."""

import json
import os
import time
from typing import Any, Dict

import replicate
from dotenv import load_dotenv


class LLMAssistant:
    """Interact with a multimodal LLM through the Replicate API."""

    def __init__(
        self,
        system_prompt: str,
        model_id: str,
        temperature: float = 0.01,
        max_tokens: int = 1024,
    ):
        """
        Initialize the assistant.

        Raises:
            ValueError: If REPLICATE_API_TOKEN is missing or empty.
        """
        load_dotenv()

        self.token = os.getenv("REPLICATE_API_TOKEN")

        if not self.token:
            raise ValueError(
                "Environment variable REPLICATE_API_TOKEN is missing or empty."
            )

        self.system_prompt = system_prompt
        self.model_id = model_id
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = replicate.Client(api_token=self.token)

    def _generate_input(self, image_Base64: str) -> Dict[str, Any]:
        """Build the input payload expected by the LLaVA model."""
        return {
            "top_p": 1,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "image": f"data:image/jpeg;base64,{image_Base64}",
            "prompt": self.system_prompt,
        }

    def _parse_response(self, output: str) -> Dict[str, Any]:
        """Parse a JSON model response into the service response format."""
        try:
            result = json.loads(output)
        except (json.JSONDecodeError, TypeError) as error:
            return {
                "status": "error",
                "result": {},
                "error": str(error),
            }

        if not isinstance(result, dict):
            return {
                "status": "error",
                "result": {},
                "error": "The model response must be a JSON object.",
            }

        return {
            "status": "success",
            "result": result,
            "error": "",
        }

    def generate_response(
        self,
        image_Base64: str,
        timeout: int = 10,
    ) -> Dict[str, Any]:
        """Generate and parse a response for a Base64-encoded image."""
        if timeout < 1:
            raise ValueError("Timeout must be at least 1 second.")

        prediction = self.client.predictions.create(
            version=self.model_id,
            input=self._generate_input(image_Base64),
        )

        started_at = time.time()
        terminal_statuses = {"succeeded", "failed", "canceled"}

        while prediction.status not in terminal_statuses:
            if time.time() - started_at >= timeout:
                if hasattr(prediction, "cancel"):
                    prediction.cancel()

                return {
                    "status": "error",
                    "result": {},
                    "error": (
                        f"Prediction timeout exceeded after {timeout} seconds."
                    ),
                }

            time.sleep(0.1)
            reloaded_prediction = prediction.reload()

            if reloaded_prediction is not None:
                prediction = reloaded_prediction

        if prediction.status != "succeeded":
            error = getattr(prediction, "error", None)
            error_message = error or (
                f"Prediction finished with status '{prediction.status}'."
            )

            return {
                "status": "error",
                "result": {},
                "error": str(error_message),
            }

        output = prediction.output

        if isinstance(output, str):
            raw_output = output
        elif output is None:
            raw_output = ""
        else:
            raw_output = "".join(str(part) for part in output)

        return self._parse_response(raw_output)
```

---

# 4. Разбор импортов

```python
import json
```

Модель возвращает текст.

Например:

```text
{"calories": 500, "proteins": 30, "fats": 40, "carbohydrates": 50}
```

Для Python это пока обычная строка.

`json.loads()` превращает эту строку в словарь:

```python
{
    "calories": 500,
    "proteins": 30,
    "fats": 40,
    "carbohydrates": 50,
}
```

---

```python
import os
```

Модуль `os` нужен для чтения переменных окружения:

```python
os.getenv("REPLICATE_API_TOKEN")
```

Токен не должен храниться непосредственно в коде.

Плохо:

```python
token = "r8_секретный_ключ"
```

Правильно:

```python
token = os.getenv("REPLICATE_API_TOKEN")
```

---

```python
import time
```

`time` используется в двух местах.

Первое:

```python
started_at = time.time()
```

Мы запоминаем момент начала ожидания.

Второе:

```python
time.sleep(0.1)
```

Мы делаем небольшую паузу между проверками статуса prediction.

Без паузы цикл отправлял бы запросы к Replicate почти непрерывно.

---

```python
from typing import Any, Dict
```

Это type hints — подсказки о типах данных.

```python
Dict[str, Any]
```

означает:

- результат является словарём;
- ключи словаря являются строками;
- значения могут иметь разные типы.

Например:

```python
{
    "status": "success",
    "result": {"calories": 500},
    "error": "",
}
```

---

```python
import replicate
```

Это официальный Python-клиент Replicate.

Через него создаётся объект клиента:

```python
replicate.Client(api_token=self.token)
```

и prediction:

```python
self.client.predictions.create(...)
```

---

```python
from dotenv import load_dotenv
```

`load_dotenv()` загружает значения из локального файла `.env`.

Пример `.env`:

```text
REPLICATE_API_TOKEN=r8_********************************
```

---

# 5. Конструктор `__init__`

```python
def __init__(
    self,
    system_prompt: str,
    model_id: str,
    temperature: float = 0.01,
    max_tokens: int = 1024,
):
```

Конструктор выполняется при создании объекта:

```python
assistant = LLMAssistant(
    system_prompt=system_prompt,
    model_id=model_id,
    temperature=0.01,
)
```

## Параметр `system_prompt`

Это инструкция для модели.

Например:

```text
Если на изображении есть еда, верни JSON с calories, proteins, fats,
carbohydrates. Если еды нет, верни {}.
```

## Параметр `model_id`

Это идентификатор конкретной версии модели на Replicate.

Он сообщает Replicate, какую модель запускать.

## Параметр `temperature`

Температура управляет случайностью ответа.

Для творческой генерации можно использовать более высокие значения.

В нашей задаче нужен стабильный JSON, поэтому используется:

```python
temperature=0.01
```

## Параметр `max_tokens`

Ограничивает максимальную длину ответа модели.

В нашей задаче ответ короткий, но значение `1024` оставляет безопасный запас.

---

# 6. Загрузка токена

```python
load_dotenv()
```

Python читает файл `.env`.

Затем:

```python
self.token = os.getenv("REPLICATE_API_TOKEN")
```

Значение сохраняется в объекте.

Если переменной нет:

```python
if not self.token:
```

создаётся понятная ошибка:

```python
raise ValueError(
    "Environment variable REPLICATE_API_TOKEN is missing or empty."
)
```

Это лучше, чем продолжать выполнение и получить непонятную ошибку авторизации
при обращении к API.

---

# 7. Сохранение настроек

```python
self.system_prompt = system_prompt
self.model_id = model_id
self.temperature = temperature
self.max_tokens = max_tokens
```

Все переданные настройки сохраняются внутри объекта.

После этого любой метод класса может использовать:

```python
self.system_prompt
self.model_id
self.temperature
self.max_tokens
```

---

# 8. Создание клиента Replicate

```python
self.client = replicate.Client(api_token=self.token)
```

Клиент — это объект, через который выполняются запросы к Replicate.

Почему не нужно каждый раз создавать нового клиента?

Потому что один экземпляр `LLMAssistant` может выполнить много запросов.
Клиент создаётся один раз в `__init__`, а затем переиспользуется.

---

# 9. Метод `_generate_input`

```python
def _generate_input(self, image_Base64: str) -> Dict[str, Any]:
```

Начальный символ `_` означает, что метод считается внутренним.

Это не запрет на вызов, а договорённость:

```text
Этот метод нужен самому классу и не является основным публичным API.
```

Метод формирует словарь входов для модели:

```python
return {
    "top_p": 1,
    "max_tokens": self.max_tokens,
    "temperature": self.temperature,
    "image": f"data:image/jpeg;base64,{image_Base64}",
    "prompt": self.system_prompt,
}
```

---

# 10. Почему к Base64 добавляется префикс

В метод приходит строка примерно такого вида:

```text
/9j/4AAQSkZJRgABAQAAAQABAAD...
```

Это только Base64-содержимое.

Модели нужно понять:

- что это данные;
- что это изображение;
- что формат изображения JPEG;
- что содержимое закодировано в Base64.

Поэтому создаётся Data URL:

```python
f"data:image/jpeg;base64,{image_Base64}"
```

Результат:

```text
data:image/jpeg;base64,/9j/4AAQSkZJRg...
```

Состав строки:

```text
data:
```

данные передаются прямо в строке;

```text
image/jpeg
```

MIME-тип изображения;

```text
base64
```

способ кодирования;

```text
,
```

разделитель;

после запятой идут реальные данные изображения.

---

# 11. Параметры модели

## `top_p`

```python
"top_p": 1
```

Параметр также управляет вариативностью генерации.

Значение `1` означает, что дополнительное ограничение выборки токенов почти не
применяется.

## `max_tokens`

```python
"max_tokens": self.max_tokens
```

Ограничивает длину ответа.

## `temperature`

```python
"temperature": self.temperature
```

Минимальная температура помогает получить стабильный формат.

## `image`

```python
"image": f"data:image/jpeg;base64,{image_Base64}"
```

Передаёт изображение.

## `prompt`

```python
"prompt": self.system_prompt
```

Передаёт текстовую инструкцию.

---

# 12. Метод `_parse_response`

```python
def _parse_response(self, output: str) -> Dict[str, Any]:
```

Его задача — преобразовать сырой текст модели в единый формат нашего сервиса.

---

# 13. Успешный JSON-разбор

```python
result = json.loads(output)
```

Если модель вернула:

```text
{"calories": 500, "proteins": 30, "fats": 40, "carbohydrates": 50}
```

то `result` будет:

```python
{
    "calories": 500,
    "proteins": 30,
    "fats": 40,
    "carbohydrates": 50,
}
```

---

# 14. Обработка некорректного JSON

Модель может нарушить промпт и вернуть:

```text
This meal contains approximately 500 calories.
```

Такой текст нельзя разобрать через `json.loads()`.

Возникнет:

```python
json.JSONDecodeError
```

Также возможен `TypeError`, если в метод передали неподходящий тип.

Обе ошибки обрабатываются:

```python
except (json.JSONDecodeError, TypeError) as error:
```

Метод не падает, а возвращает:

```python
{
    "status": "error",
    "result": {},
    "error": str(error),
}
```

Это важный инженерный принцип:

```text
Ошибка внешней модели не должна аварийно завершать весь сервис.
```

---

# 15. Почему проверяется `dict`

Даже корректный JSON не обязательно является объектом.

Например, это корректный JSON:

```json
[1, 2, 3]
```

Это тоже корректный JSON:

```json
500
```

И это корректный JSON:

```json
"hello"
```

Но наш API ожидает именно объект:

```json
{
  "calories": 500,
  "proteins": 30,
  "fats": 40,
  "carbohydrates": 50
}
```

Поэтому выполняется проверка:

```python
if not isinstance(result, dict):
```

Если результат не является словарём, возвращается ошибка.

---

# 16. Почему пустой словарь `{}` считается успехом

Для изображения без еды модель должна вернуть:

```json
{}
```

После `json.loads()` это:

```python
{}
```

Пустой словарь всё равно имеет тип `dict`.

Поэтому проверка:

```python
isinstance({}, dict)
```

возвращает:

```python
True
```

Значит ответ `{}` считается корректным успешным результатом.

Это важно: пустой результат не означает техническую ошибку.
Он означает бизнес-результат:

```text
На изображении не обнаружена еда.
```

---

# 17. Формат успешного ответа

```python
return {
    "status": "success",
    "result": result,
    "error": "",
}
```

Контракт состоит из трёх полей.

## `status`

```python
"success"
```

Операция завершилась корректно.

## `result`

Содержит разобранный JSON модели.

## `error`

Пустая строка, потому что ошибки нет.

---

# 18. Метод `generate_response`

```python
def generate_response(
    self,
    image_Base64: str,
    timeout: int = 10,
) -> Dict[str, Any]:
```

Это главный публичный метод класса.

Именно его будет вызывать FastAPI.

Он получает:

- Base64-строку изображения;
- максимальное время ожидания.

---

# 19. Проверка `timeout`

```python
if timeout < 1:
    raise ValueError("Timeout must be at least 1 second.")
```

Почему здесь используется исключение?

Потому что `timeout < 1` — это ошибка программиста или вызывающего кода.

Например:

```python
assistant.generate_response(image, timeout=0)
```

Такой параметр не имеет смысла.

Это отличается от реального истечения времени во время работы prediction.

---

# 20. Создание prediction

```python
prediction = self.client.predictions.create(
    version=self.model_id,
    input=self._generate_input(image_Base64),
)
```

Здесь происходит фактический запрос к Replicate.

## `version`

```python
version=self.model_id
```

Указывается версия модели.

## `input`

```python
input=self._generate_input(image_Base64)
```

Передаётся сформированный словарь:

```python
{
    "top_p": 1,
    "max_tokens": 1024,
    "temperature": 0.01,
    "image": "data:image/jpeg;base64,...",
    "prompt": "...",
}
```

---

# 21. Что такое prediction

Prediction — это объект, представляющий один запуск модели.

У него есть статус.

Пример жизненного цикла:

```text
starting
    ↓
processing
    ↓
succeeded
```

Также возможны:

```text
failed
```

или:

```text
canceled
```

Объект содержит:

- `status`;
- `output`;
- `error`;
- `reload()`;
- иногда `cancel()`.

---

# 22. Запоминание времени начала

```python
started_at = time.time()
```

Допустим, `time.time()` вернул:

```text
1000.0
```

Через две секунды он вернёт:

```text
1002.0
```

Разница:

```python
1002.0 - 1000.0
```

равна двум секундам.

Так код измеряет фактическое время ожидания.

---

# 23. Терминальные статусы

```python
terminal_statuses = {"succeeded", "failed", "canceled"}
```

Терминальный статус означает, что prediction больше не выполняется.

## `succeeded`

Модель успешно завершила работу.

## `failed`

Модель завершилась с ошибкой.

## `canceled`

Prediction была отменена.

---

# 24. Цикл ожидания

```python
while prediction.status not in terminal_statuses:
```

Пока статус не финальный, код продолжает ждать.

Например:

```text
starting
```

не является финальным.

```text
processing
```

тоже не является финальным.

---

# 25. Проверка превышения времени

```python
if time.time() - started_at >= timeout:
```

Допустим:

```python
started_at = 1000
timeout = 10
```

Если текущее время стало:

```python
1010
```

то:

```python
1010 - 1000 >= 10
```

даёт `True`.

Значит лимит ожидания превышен.

---

# 26. Самое важное исправление для 100 баллов

Первая версия выбрасывала:

```python
raise TimeoutError(...)
```

Из-за этого автотест `test_generate_response_timeout` завершался ошибкой.

Тест ожидал, что реальный таймаут будет обработан внутри метода и превращён в
обычный словарь ошибки.

Правильная реализация:

```python
return {
    "status": "error",
    "result": {},
    "error": (
        f"Prediction timeout exceeded after {timeout} seconds."
    ),
}
```

То есть метод не падает, а сообщает об ошибке через стандартный контракт.

Именно это изменение позволило пройти внутренний тест и получить 100 баллов.

---

# 27. Почему `timeout < 1` и реальный таймаут обрабатываются по-разному

Это принципиально разные ситуации.

## Неверный параметр

```python
timeout=0
```

Это ошибка вызова функции.

Поэтому:

```python
raise ValueError(...)
```

## Prediction не успела завершиться

```text
timeout был корректным, но модель отвечала слишком долго
```

Это рабочая ошибка внешнего сервиса.

Поэтому возвращается:

```python
{
    "status": "error",
    "result": {},
    "error": "...",
}
```

---

# 28. Отмена prediction

```python
if hasattr(prediction, "cancel"):
    prediction.cancel()
```

Если лимит уже превышен, продолжать вычисление модели обычно не нужно.

Отмена полезна по двум причинам:

1. не расходуются лишние вычислительные ресурсы;
2. может уменьшиться стоимость запроса.

Почему используется `hasattr()`?

Потому что в автотестах prediction может быть поддельным mock-объектом.

Не каждый mock обязательно имеет метод `cancel()`.

Проверка:

```python
hasattr(prediction, "cancel")
```

защищает код от `AttributeError`.

---

# 29. Пауза между проверками

```python
time.sleep(0.1)
```

Цикл ждёт 0.1 секунды.

Без паузы:

```python
while ...:
    prediction.reload()
```

мог бы вызывать API тысячи раз за секунду.

С паузой получается примерно до десяти проверок в секунду.

Для прототипа это разумный компромисс между:

- скоростью реакции;
- количеством запросов.

---

# 30. Обновление prediction

```python
reloaded_prediction = prediction.reload()
```

`reload()` получает актуальное состояние из Replicate.

До обновления локальный объект мог содержать:

```text
processing
```

После обновления:

```text
succeeded
```

---

# 31. Почему учитывается возвращаемое значение `reload()`

```python
if reloaded_prediction is not None:
    prediction = reloaded_prediction
```

В некоторых реализациях `reload()` обновляет текущий объект и возвращает `None`.

В других тестовых или библиотечных реализациях метод может вернуть новый объект.

Код поддерживает оба варианта.

## Вариант 1

```python
prediction.reload()
```

обновляет `prediction` на месте и возвращает `None`.

Тогда переменная не заменяется.

## Вариант 2

```python
prediction.reload()
```

возвращает новый prediction.

Тогда выполняется:

```python
prediction = reloaded_prediction
```

Это делает решение устойчивым к разным реализациям и mock-объектам автотеста.

---

# 32. Обработка неуспешного финального статуса

После цикла prediction уже имеет один из статусов:

```text
succeeded
failed
canceled
```

Проверка:

```python
if prediction.status != "succeeded":
```

означает:

```text
Если это failed или canceled, возвращаем ошибку.
```

---

# 33. Получение ошибки модели

```python
error = getattr(prediction, "error", None)
```

`getattr()` безопасно получает атрибут.

Если `prediction.error` существует, возвращается его значение.

Если атрибута нет, возвращается `None`.

Это особенно полезно для mock-объектов в тестах.

---

# 34. Запасное сообщение об ошибке

```python
error_message = error or (
    f"Prediction finished with status '{prediction.status}'."
)
```

Если Replicate дал собственную ошибку, используется она.

Например:

```text
Model failed because image format is unsupported
```

Если текст ошибки отсутствует, создаётся понятное сообщение:

```text
Prediction finished with status 'failed'.
```

---

# 35. Единый результат ошибки

```python
return {
    "status": "error",
    "result": {},
    "error": str(error_message),
}
```

Все рабочие ошибки возвращаются в одном формате.

Это удобно для FastAPI:

```python
response = assistant.generate_response(...)

if response["status"] == "error":
    ...
```

---

# 36. Получение output

Если prediction успешна:

```python
output = prediction.output
```

Но тип `output` может отличаться.

Он может быть:

- одной строкой;
- `None`;
- списком или другой последовательностью частей.

---

# 37. Если output — строка

```python
if isinstance(output, str):
    raw_output = output
```

Например:

```python
output = '{"calories": 500}'
```

Ничего объединять не нужно.

---

# 38. Если output отсутствует

```python
elif output is None:
    raw_output = ""
```

Пустая строка позже попадёт в `_parse_response()`.

`json.loads("")` создаст ошибку JSON.

Метод аккуратно вернёт:

```python
{
    "status": "error",
    "result": {},
    "error": "...",
}
```

То есть даже неожиданный пустой output не сломает сервис.

---

# 39. Если output состоит из частей

```python
else:
    raw_output = "".join(str(part) for part in output)
```

Например, Replicate может вернуть:

```python
[
    '{"calories": 500, ',
    '"proteins": 30, ',
    '"fats": 40, ',
    '"carbohydrates": 50}',
]
```

После `join` получится:

```text
{"calories": 500, "proteins": 30, "fats": 40, "carbohydrates": 50}
```

После этого строку можно передать в `json.loads()`.

---

# 40. Финальный вызов `_parse_response`

```python
return self._parse_response(raw_output)
```

Почему код не вызывает `json.loads()` прямо здесь?

Потому что логика разбора уже вынесена в отдельный метод.

Это даёт преимущества:

- нет дублирования;
- внутренний метод легко тестировать отдельно;
- код `generate_response()` остаётся понятным;
- можно позже улучшить обработку JSON в одном месте.

---

# 41. Полный успешный сценарий

Пусть пользователь загрузил фотографию бургера.

## Шаг 1

Streamlit превращает изображение в Base64.

## Шаг 2

FastAPI вызывает:

```python
assistant.generate_response(image_Base64, timeout=20)
```

## Шаг 3

Проверяется:

```python
timeout >= 1
```

## Шаг 4

`_generate_input()` создаёт payload.

## Шаг 5

Создаётся prediction.

## Шаг 6

Статус меняется:

```text
starting → processing → succeeded
```

## Шаг 7

Из `prediction.output` получается JSON-строка.

## Шаг 8

`_parse_response()` превращает её в словарь.

## Шаг 9

Возвращается:

```python
{
    "status": "success",
    "result": {
        "calories": 500,
        "proteins": 30,
        "fats": 40,
        "carbohydrates": 50,
    },
    "error": "",
}
```

---

# 42. Сценарий изображения без еды

Модель возвращает:

```text
{}
```

`json.loads("{}")` даёт:

```python
{}
```

Это словарь, поэтому результат:

```python
{
    "status": "success",
    "result": {},
    "error": "",
}
```

Это не техническая ошибка.

Это корректный бизнес-ответ:

```text
Еда не обнаружена.
```

---

# 43. Сценарий некорректного ответа модели

Модель вернула:

```text
The image contains a hamburger.
```

`json.loads()` не может разобрать текст.

Метод возвращает:

```python
{
    "status": "error",
    "result": {},
    "error": "Expecting value: line 1 column 1 ...",
}
```

Сервис остаётся рабочим.

---

# 44. Сценарий таймаута

Prediction остаётся в статусе:

```text
processing
```

дольше разрешённого времени.

Тогда:

1. вызывается `cancel()`, если он доступен;
2. возвращается:

```python
{
    "status": "error",
    "result": {},
    "error": "Prediction timeout exceeded after 1 seconds.",
}
```

Именно этот формат ожидал автотест.

---

# 45. Сценарий `failed`

Prediction завершилась:

```text
failed
```

Допустим, `prediction.error` содержит:

```text
Invalid image
```

Метод вернёт:

```python
{
    "status": "error",
    "result": {},
    "error": "Invalid image",
}
```

---

# 46. Сценарий `canceled`

Если prediction была отменена извне:

```text
canceled
```

и собственного текста ошибки нет, метод вернёт:

```python
{
    "status": "error",
    "result": {},
    "error": "Prediction finished with status 'canceled'.",
}
```

---

# 47. Как решение связано с баллами

## 20% — внутренние методы

Проверялись:

- `_generate_input()`;
- `_parse_response()`;
- поведение таймаута;
- корректность внутренних форматов.

Критическая деталь для полного прохождения:

```python
реальный таймаут должен возвращать error-словарь,
а не выбрасывать TimeoutError
```

## 60% — `generate_response`

Метод правильно:

- создаёт prediction;
- передаёт model ID;
- передаёт input;
- обновляет статус;
- ждёт завершения;
- обрабатывает успешный output;
- обрабатывает ошибки.

## 20% — качество кода

Решение прошло Pylint благодаря:

- понятным именам;
- docstring;
- корректным импортам;
- ограниченной длине строк;
- отсутствию лишнего кода;
- логичному разделению методов.

Итого:

```text
20 + 60 + 20 = 100 баллов
```

---

# 48. Почему первая версия получила 80 баллов

Первая версия имела:

```python
raise TimeoutError(
    f"Prediction exceeded the timeout of {timeout} seconds."
)
```

Основная логика была правильной, поэтому:

```text
test_generate_response — 60/60
test_pylint — 20/20
```

Но внутренний тест вызвал сценарий таймаута и не ожидал исключения.

Он получил необработанный `TimeoutError`, поэтому весь блок внутренних тестов
получил:

```text
0/20
```

Итог:

```text
80/100
```

---

# 49. Почему финальное исправление правильное именно для этого API

Документация задания описывала единый возвращаемый словарь:

```python
{
    "status": "...",
    "result": {...},
    "error": "...",
}
```

Фактический автотест подтвердил, что таймаут тоже должен быть частью этого
контракта.

Поэтому финальное решение не выбрасывает рабочую ошибку внешнего сервиса наружу,
а возвращает её как данные.

Это делает API класса предсказуемым:

```python
response = assistant.generate_response(...)
```

После вызова можно всегда проверить:

```python
response["status"]
```

---

# 50. Что нужно запомнить из задания

## 1. Не хранить API-токены в коде

Использовать `.env` и переменные окружения.

## 2. Внешний API может отвечать долго

Всегда нужен timeout.

## 3. Prediction имеет жизненный цикл

Нужно проверять статус и обновлять объект.

## 4. LLM может нарушить формат

Нельзя слепо доверять её тексту. Нужен `json.loads()` и обработка ошибок.

## 5. Пустой словарь может быть корректным результатом

`{}` означает отсутствие еды, а не техническую ошибку.

## 6. Для всех рабочих ошибок полезен единый контракт

```python
{
    "status": "error",
    "result": {},
    "error": "...",
}
```

## 7. Автотест важнее предположений

Формулировка задания могла навести на мысль, что нужен `TimeoutError`.
Но фактический тест показал, что ожидается словарь.

В задачах с закрытыми тестами нужно ориентироваться на:

- требования API;
- результаты тестов;
- точный текст ошибки;
- уже прошедшие проверки.

---

# 51. Минимальный пример использования

```python
from assistant import LLMAssistant


model_id = (
    "80537f9eead1a5bfa72d5ac6ea6414379be41d4d4f6679fd776e9535d1eb58bb"
)

system_prompt = """
Analyze the image.
For food return JSON with calories, proteins, fats and carbohydrates.
For a non-food image return {}.
Return JSON only.
"""

assistant = LLMAssistant(
    system_prompt=system_prompt,
    model_id=model_id,
    temperature=0.01,
)

response = assistant.generate_response(
    image_Base64="BASE64_IMAGE_DATA",
    timeout=20,
)

print(response)
```

---

# 52. Как должен выглядеть `.env`

```text
REPLICATE_API_TOKEN=r8_ваш_реальный_токен
```

Файл `.env` нельзя:

- отправлять в GitHub;
- пересылать другим людям;
- прикладывать к решению;
- показывать на скриншотах.

В `.gitignore` добавляется:

```text
.env
```

---

# 53. Главная мысль решения

Класс выполняет три последовательные задачи:

```text
Подготовить input
    ↓
Дождаться prediction
    ↓
Преобразовать output в единый словарь
```

В коде этому соответствуют три логических части:

```python
_generate_input()
generate_response()
_parse_response()
```

Именно такое разделение делает решение:

- понятным;
- тестируемым;
- устойчивым;
- пригодным для интеграции в FastAPI;
- соответствующим требованиям автотестов.

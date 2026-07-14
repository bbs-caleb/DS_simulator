# AI: Calorie Tracker — пошаговое объяснение с нуля

## 1. Что такое эндпоинт

Эндпоинт — это адрес внутри API, который выполняет конкретную операцию.

В нашем коде:

```python
@app.post("/generate_response")
```

означает:

- адрес: `/generate_response`;
- разрешённый HTTP-метод: `POST`;
- обработчик: функция `generate_response`.

Полный локальный адрес после запуска:

```text
http://127.0.0.1:8000/generate_response
```

## 2. Почему функция объявлена через `async`

```python
async def generate_response(request: Request) -> Any:
```

`async` позволяет FastAPI эффективно ожидать сетевые операции и чтение запроса,
не блокируя весь сервер.

Для получения JSON используется `await`:

```python
request_data = await request.json()
```

Слово `await` означает: дождаться завершения асинхронной операции и получить
результат.

## 3. Что хранится в `request_data`

Фронтенд отправляет:

```json
{
  "image_base64": "..."
}
```

После выполнения:

```python
request_data = await request.json()
```

в Python получается словарь:

```python
{
    "image_base64": "..."
}
```

## 4. Проверка типа тела запроса

```python
if not isinstance(request_data, dict):
```

Здесь проверяется, является ли тело запроса словарём.

Это защищает код от ситуации, когда клиент отправил, например:

```json
["a", "b", "c"]
```

В таком объекте нельзя нормально искать поле `image_base64`.

## 5. Получение Base64-строки

```python
image_base64 = request_data.get("image_base64")
```

Метод `.get()` безопасно ищет ключ.

Если ключа нет, Python вернёт `None`, а не завершит программу с `KeyError`.

## 6. Проверка, что значение является непустой строкой

```python
if not isinstance(image_base64, str) or not image_base64:
```

Условие состоит из двух частей.

Первая часть:

```python
not isinstance(image_base64, str)
```

проверяет, что значение имеет тип `str`.

Вторая часть:

```python
not image_base64
```

проверяет, что строка не пустая.

Если проверка не пройдена, создаётся HTTP-ошибка:

```python
raise HTTPException(
    status_code=400,
    detail="Invalid Base64 image data",
)
```

`400` означает, что проблема находится в данных, присланных клиентом.

## 7. Строгая проверка Base64

```python
base64.b64decode(image_base64, validate=True)
```

Эта строка пытается декодировать Base64.

Например:

```text
aGVsbG8=
```

является Base64-представлением слова `hello`.

Параметр:

```python
validate=True
```

запрещает посторонние символы.

Если строка испорчена, Python создаёт исключение `binascii.Error` или
`ValueError`.

## 8. Преобразование ошибки декодирования в HTTP 400

```python
except (binascii.Error, ValueError) as error:
    raise HTTPException(
        status_code=400,
        detail="Invalid Base64 image data",
    ) from error
```

Конструкция:

```python
from error
```

сохраняет исходную причину исключения. Это полезно для диагностики и логирования.

## 9. Вызов ассистента

```python
return assistant.generate_response(image_base64, timeout=10)
```

В функцию передаются:

- проверенная Base64-строка;
- максимальное время ожидания — 10 секунд.

Сейчас ассистент является заглушкой и возвращает фиксированный словарь.
На следующем этапе этот класс можно заменить интеграцией с настоящей LLM.

## 10. Обработка HTTPException

```python
except HTTPException:
    raise
```

Это один из самых важных блоков.

Ранее код специально создавал `HTTPException` со статусом `400`. Её необходимо
вернуть FastAPI без изменений.

Если этот блок убрать, общий `except Exception` может перехватить созданную
HTTP-ошибку и заменить правильный код `400` на неправильный код `500`.

## 11. Обработка таймаута

```python
except TimeoutError as error:
    raise HTTPException(
        status_code=504,
        detail="The LLM assistant request timed out",
    ) from error
```

`TimeoutError` означает, что внешний сервис не успел ответить вовремя.

Код `504 Gateway Timeout` сообщает клиенту, что сервер ожидал ответ от другого
сервиса, но не получил его в установленное время.

## 12. Обработка остальных ошибок

```python
except Exception as error:
    raise HTTPException(
        status_code=500,
        detail="An unexpected error occurred",
    ) from error
```

Этот блок является последней защитой.

Он перехватывает ошибки, которые не были предусмотрены отдельно, и возвращает
код `500 Internal Server Error`.

Пользователь не получает внутренний текст исключения. Это безопаснее, потому что
внутренние детали программы не раскрываются наружу.

## 13. Как запустить сервис

Поместите `solution.py` в каталог проекта и выполните:

```bash
uvicorn solution:app --reload
```

Здесь:

- `solution` — имя файла без `.py`;
- `app` — объект `FastAPI`;
- `--reload` — автоматический перезапуск после изменения кода.

## 14. Как открыть документацию FastAPI

После запуска откройте:

```text
http://127.0.0.1:8000/docs
```

FastAPI автоматически создаст интерактивную документацию Swagger UI.

## 15. Минимальная ручная проверка

```python
import base64

import requests


url = "http://127.0.0.1:8000/generate_response"

image_base64 = base64.b64encode(b"test image").decode("utf-8")

response = requests.post(
    url,
    json={"image_base64": image_base64},
    timeout=10,
)

print(response.status_code)
print(response.json())
```

Ожидаемый HTTP-код:

```text
200
```

## 16. Проверка некорректной строки

```python
response = requests.post(
    url,
    json={"image_base64": "%%%not-base64%%%"},
    timeout=10,
)

print(response.status_code)
print(response.json())
```

Ожидаемый HTTP-код:

```text
400
```

## 17. Что загружать в проверяющую систему

Загружайте только:

```text
solution.py
```

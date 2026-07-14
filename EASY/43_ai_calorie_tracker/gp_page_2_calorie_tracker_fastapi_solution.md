# AI: Calorie Tracker — готовое решение

## Файл для загрузки

В проверяющую систему необходимо загрузить:

```text
solution.py
```

## Реализованная функция

```python
@app.post("/generate_response")
async def generate_response(request: Request) -> Any:
    try:
        request_data = await request.json()

        if not isinstance(request_data, dict):
            raise HTTPException(
                status_code=400,
                detail="Invalid request body",
            )

        image_base64 = request_data.get("image_base64")

        if not isinstance(image_base64, str) or not image_base64:
            raise HTTPException(
                status_code=400,
                detail="Invalid Base64 image data",
            )

        try:
            base64.b64decode(image_base64, validate=True)
        except (binascii.Error, ValueError) as error:
            raise HTTPException(
                status_code=400,
                detail="Invalid Base64 image data",
            ) from error

        return assistant.generate_response(image_base64, timeout=10)

    except HTTPException:
        raise
    except TimeoutError as error:
        raise HTTPException(
            status_code=504,
            detail="The LLM assistant request timed out",
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred",
        ) from error
```

## Почему это решение покрывает все критерии

### 1. Корректная Base64-строка — 200

Строка проходит проверку, после чего вызывается ассистент:

```python
return assistant.generate_response(image_base64, timeout=10)
```

FastAPI автоматически возвращает статус `200 OK`.

### 2. Некорректная Base64-строка — 400

Декодирование выполняется в строгом режиме:

```python
base64.b64decode(image_base64, validate=True)
```

Ошибка преобразуется в:

```python
HTTPException(status_code=400, ...)
```

### 3. TimeoutError — 504

```python
except TimeoutError as error:
    raise HTTPException(status_code=504, ...) from error
```

### 4. Непредвиденная ошибка — 500

```python
except Exception as error:
    raise HTTPException(status_code=500, ...) from error
```

### 5. HTTPException не превращается в 500

Это критически важно:

```python
except HTTPException:
    raise
```

Без этого блока созданная нами ошибка `400` могла бы попасть в общий обработчик
и ошибочно превратиться в `500`.

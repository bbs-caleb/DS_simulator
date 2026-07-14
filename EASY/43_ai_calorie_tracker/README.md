# AI: Calorie Tracker — FastAPI

## Главный файл для отправки

```text
solution.py
```

## Запуск

```bash
uvicorn solution:app --reload
```

## Эндпоинт

```text
POST http://127.0.0.1:8000/generate_response
```

## Тело запроса

```json
{
  "image_base64": "aGVsbG8="
}
```

## Коды ответа

- `200` — запрос успешно обработан;
- `400` — некорректная Base64-строка;
- `504` — таймаут ассистента;
- `500` — непредвиденная ошибка.

## Дополнительные материалы

- `gp_page_1_calorie_tracker_fastapi_context.md` — бизнесовый и технический контекст;
- `gp_page_2_calorie_tracker_fastapi_solution.md` — объяснение готового решения;
- `gp_page_3_calorie_tracker_fastapi_step_by_step_explanation.md` — подробный разбор с нуля.

# ML: RECSYS LIVE-STREAMING PLATFORM — страница 5

## Состав комплекта

1. `gp_page_5_recsys_live_streaming_platform_context.md` — подробный бизнесовый и технический контекст.
2. `gp_page_5_recsys_live_streaming_platform_solution.py` — готовое минимальное решение.
3. `gp_page_5_recsys_live_streaming_platform_code_explanation.md` — построчное объяснение с нуля.
4. `gp_page_5_recsys_live_streaming_platform_interview_system_design.md` — продуктовый и system design разбор.

## Что отправлять

В проверяющую систему отправляется:

`gp_page_5_recsys_live_streaming_platform_solution.py`

В шаблоне запуска используется модуль `solution`:

```python
uvicorn.run("solution:app", host="localhost")
```

Поэтому для локального запуска сохраните копию Python-файла под именем `solution.py`. Сам код менять не требуется.

## Главная логика

Для заданного времени `time`:

1. Оставляем только активные просмотры:

```text
time_start <= time <= time_end
```

2. Считаем количество активных зрителей каждого стримера.
3. Сортируем стримеров по убыванию числа зрителей.
4. Возвращаем список через FastAPI.

Пример ответа:

```json
{
  "user_id": 42,
  "time": 6147,
  "popular_streamers": ["alice", "bob"]
}
```

`user_id` пока не меняет выдачу: это global popularity baseline. Он нужен для стабильного API-контракта и последующего перехода к персонализации.

## Порядок изучения

1. Context.
2. Готовый Python-код.
3. Пошаговое объяснение.
4. Interview/system design.
5. Локальный запуск и проверка через `/docs`.

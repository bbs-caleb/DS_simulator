# Page 3. Greedy Sampler: решение и построчное объяснение

## 1. Готовый файл

Решение находится в:

```text
gp_page_3_greedy_sampler_app.py
```

Файл реализует:

```text
GET /sample/
PUT /feedback/
GET /offer_ids/{offer_id}/stats/
```

`README.md` не добавляется, потому что это не первая страница темы.

---

# 2. Полный код

```python
"""FastAPI service with a greedy offer sampler."""

import numpy as np
import uvicorn
from fastapi import FastAPI

app = FastAPI()

OFFER_CLICKS = {}
CLICK_TO_OFFER = {}
OFFER_REWARDS = {}
OFFER_CONVERSIONS = {}

RANDOM_CLICKS = 100


def get_rpc(offer_id: int) -> float:
    """Return revenue per click for an offer."""
    clicks = OFFER_CLICKS.get(offer_id, 0)
    if clicks == 0:
        return 0.0
    return OFFER_REWARDS.get(offer_id, 0.0) / clicks


@app.get("/sample/")
def sample(click_id: int, offer_ids: str) -> dict:
    """Choose an offer randomly during initialization, then greedily."""
    offers_ids = [int(offer) for offer in offer_ids.split(",")]

    total_clicks = sum(OFFER_CLICKS.values())

    if total_clicks < RANDOM_CLICKS:
        offer_id = int(np.random.choice(offers_ids))
        sampler = "random"
    else:
        offer_id = max(offers_ids, key=get_rpc)
        sampler = "greedy"

    OFFER_CLICKS[offer_id] = OFFER_CLICKS.get(offer_id, 0) + 1
    CLICK_TO_OFFER[click_id] = offer_id

    response = {
        "click_id": click_id,
        "offer_id": offer_id,
        "sampler": sampler,
    }
    return response


@app.put("/feedback/")
def feedback(click_id: int, reward: float) -> dict:
    """Save feedback for a particular click."""
    offer_id = CLICK_TO_OFFER[click_id]
    reward = float(reward)
    is_conversion = reward > 0

    OFFER_REWARDS[offer_id] = OFFER_REWARDS.get(offer_id, 0.0) + reward

    if is_conversion:
        OFFER_CONVERSIONS[offer_id] = (
            OFFER_CONVERSIONS.get(offer_id, 0) + 1
        )

    response = {
        "click_id": click_id,
        "offer_id": offer_id,
        "is_conversion": is_conversion,
        "reward": reward,
    }
    return response


@app.get("/offer_ids/{offer_id}/stats/")
def stats(offer_id: int) -> dict:
    """Return statistics for an offer."""
    clicks = OFFER_CLICKS.get(offer_id, 0)
    conversions = OFFER_CONVERSIONS.get(offer_id, 0)
    reward = OFFER_REWARDS.get(offer_id, 0.0)

    if clicks == 0:
        cr = 0.0
        rpc = 0.0
    else:
        cr = conversions / clicks
        rpc = reward / clicks

    response = {
        "offer_id": offer_id,
        "clicks": clicks,
        "conversions": conversions,
        "reward": reward,
        "cr": cr,
        "rpc": rpc,
    }
    return response


def main() -> None:
    """Run the application."""
    uvicorn.run(app, host="localhost")


if __name__ == "__main__":
    main()
```

---

# 3. Импорты

## NumPy

```python
import numpy as np
```

NumPy нужен для случайного выбора на первых 100 запросах:

```python
np.random.choice(offers_ids)
```

## Uvicorn

```python
import uvicorn
```

Uvicorn запускает сервер, который слушает HTTP-запросы и передаёт их FastAPI.

## FastAPI

```python
from fastapi import FastAPI
```

Импортируется класс веб-приложения.

---

# 4. Создание FastAPI-приложения

```python
app = FastAPI()
```

Справа создаётся объект FastAPI. Слева он сохраняется в переменную `app`.

Декораторы `@app.get` и `@app.put` будут регистрировать в этом объекте endpoints.

---

# 5. Глобальные словари

## Количество кликов

```python
OFFER_CLICKS = {}
```

Ключ — `offer_id`, значение — количество рекомендаций.

## Связь клика с оффером

```python
CLICK_TO_OFFER = {}
```

Ключ — `click_id`, значение — выбранный `offer_id`.

## Сумма наград

```python
OFFER_REWARDS = {}
```

Ключ — `offer_id`, значение — накопленный reward.

## Количество конверсий

```python
OFFER_CONVERSIONS = {}
```

Ключ — `offer_id`, значение — число положительных feedback.

Глобальные словари видны всем функциям в одном процессе, поэтому `/sample`, `/feedback` и `/stats` работают с общим состоянием.

---

# 6. Константа RANDOM_CLICKS

```python
RANDOM_CLICKS = 100
```

Это количество первых рекомендаций, выполняемых случайно.

Заглавные буквы показывают, что переменная используется как константа.

---

# 7. Функция `get_rpc`

```python
def get_rpc(offer_id: int) -> float:
```

Функция получает ID оффера и возвращает его RPC.

## Получение clicks

```python
clicks = OFFER_CLICKS.get(offer_id, 0)
```

Метод `.get()` принимает:

```text
ключ, значение_по_умолчанию
```

Если оффера нет в словаре, возвращается `0`.

## Защита от деления на ноль

```python
if clicks == 0:
    return 0.0
```

RPC нельзя считать как `reward / 0`, поэтому неизвестный оффер получает оценку `0.0`.

## Формула RPC

```python
return OFFER_REWARDS.get(offer_id, 0.0) / clicks
```

Например:

```text
reward = 20
clicks = 10
RPC = 20 / 10 = 2.0
```

---

# 8. Endpoint `/sample/`

```python
@app.get("/sample/")
```

Декоратор означает:

> при GET-запросе на `/sample/` вызвать функцию ниже.

Функция:

```python
def sample(click_id: int, offer_ids: str) -> dict:
```

принимает:

- `click_id` как `int`;
- `offer_ids` как строку;
- возвращает словарь.

Пример URL:

```text
/sample/?click_id=101&offer_ids=10,20,30
```

---

# 9. Преобразование строки кандидатов

```python
offers_ids = [int(offer) for offer in offer_ids.split(",")]
```

Пусть пришло:

```python
offer_ids = "10,20,30"
```

Сначала:

```python
offer_ids.split(",")
```

даёт:

```python
["10", "20", "30"]
```

Затем `int()` превращает строки в числа:

```python
[10, 20, 30]
```

Исходный порядок сохраняется.

---

# 10. Подсчёт общего числа рекомендаций

```python
total_clicks = sum(OFFER_CLICKS.values())
```

Пусть словарь выглядит так:

```python
{
    10: 40,
    20: 35,
    30: 25,
}
```

Тогда:

```text
40 + 35 + 25 = 100
```

Это количество уже обработанных `/sample` запросов.

Почему не используется `len(CLICK_TO_OFFER)`:

- `len` считает уникальные ключи;
- повторный `click_id` перезапишет старую запись;
- сумма счётчиков отражает фактическое число рекомендаций.

---

# 11. Первые 100 случайных запросов

```python
if total_clicks < RANDOM_CLICKS:
```

Перед первым запросом:

```text
total_clicks = 0
```

Перед сотым:

```text
total_clicks = 99
```

В обоих случаях условие истинно.

Перед 101-м:

```text
total_clicks = 100
```

Условие ложно, поэтому включается greedy.

## Случайный выбор

```python
offer_id = int(np.random.choice(offers_ids))
```

NumPy выбирает один элемент из списка кандидатов.

`int()` нужен, чтобы получить обычный Python `int`, который корректно сериализуется в JSON.

## Поле sampler

```python
sampler = "random"
```

API сообщает, что использовалась случайная стратегия.

---

# 12. Greedy-выбор

```python
else:
    offer_id = max(offers_ids, key=get_rpc)
    sampler = "greedy"
```

Пусть:

```python
offers_ids = [10, 20, 30]
```

И значения RPC:

```text
RPC(10) = 1.2
RPC(20) = 0.8
RPC(30) = 2.0
```

`max` вызывает `get_rpc` для каждого ID и возвращает `30`.

## Если RPC равны

Пусть:

```python
offers_ids = [45, 67]
```

RPC обоих равен нулю. При равных ключах `max` возвращает первый элемент — `45`.

Это соответствует требованию задачи.

---

# 13. Обновление счётчика кликов

```python
OFFER_CLICKS[offer_id] = OFFER_CLICKS.get(offer_id, 0) + 1
```

Если оффер показан впервые:

```text
0 + 1 = 1
```

Если ранее было 7 рекомендаций:

```text
7 + 1 = 8
```

Счётчик обновляется в `/sample`, а не в `/feedback`, потому что клик уже состоялся, даже если feedback придёт позже или не придёт вообще.

---

# 14. Сохранение связи клика

```python
CLICK_TO_OFFER[click_id] = offer_id
```

Например:

```python
CLICK_TO_OFFER[101] = 30
```

Позднее feedback с `click_id=101` обновит статистику оффера 30.

---

# 15. Ответ `/sample/`

```python
response = {
    "click_id": click_id,
    "offer_id": offer_id,
    "sampler": sampler,
}
```

Пример:

```json
{
  "click_id": 101,
  "offer_id": 30,
  "sampler": "random"
}
```

`return response` отдаёт словарь FastAPI, который преобразует его в JSON.

---

# 16. Endpoint `/feedback/`

```python
@app.put("/feedback/")
```

Функция принимает:

```python
def feedback(click_id: int, reward: float) -> dict:
```

Оффер не передаётся, потому что сервис должен восстановить его самостоятельно.

---

# 17. Поиск оффера по click ID

```python
offer_id = CLICK_TO_OFFER[click_id]
```

Если:

```python
CLICK_TO_OFFER = {
    101: 30,
}
```

то feedback для клика 101 обновит оффер 30.

Благодаря словарю порядок прихода feedback не имеет значения.

---

# 18. Приведение reward к float

```python
reward = float(reward)
```

Примеры:

```python
float(0)    # 0.0
float(5)    # 5.0
float(4.2)  # 4.2
```

Это даёт стабильный тип в ответе и статистике.

---

# 19. Определение конверсии

```python
is_conversion = reward > 0
```

```python
0.0 > 0   # False
4.2 > 0   # True
```

FastAPI преобразует Python `bool` в JSON `true` или `false`.

---

# 20. Накопление reward

```python
OFFER_REWARDS[offer_id] = OFFER_REWARDS.get(offer_id, 0.0) + reward
```

Пусть накоплено `10.0`, а новый reward равен `4.2`.

После обновления:

```text
14.2
```

Reward именно суммируется, а не заменяется последним значением.

---

# 21. Накопление conversions

```python
if is_conversion:
```

Счётчик увеличивается только при положительном reward.

```python
OFFER_CONVERSIONS[offer_id] = (
    OFFER_CONVERSIONS.get(offer_id, 0) + 1
)
```

При `reward=0` этот блок не выполняется.

---

# 22. Ответ `/feedback/`

```python
response = {
    "click_id": click_id,
    "offer_id": offer_id,
    "is_conversion": is_conversion,
    "reward": reward,
}
```

Пример конверсии:

```json
{
  "click_id": 101,
  "offer_id": 30,
  "is_conversion": true,
  "reward": 4.2
}
```

Пример без конверсии:

```json
{
  "click_id": 102,
  "offer_id": 10,
  "is_conversion": false,
  "reward": 0.0
}
```

---

# 23. Endpoint `/stats/`

```python
@app.get("/offer_ids/{offer_id}/stats/")
```

`{offer_id}` — path-параметр.

URL:

```text
/offer_ids/30/stats/
```

передаст функции `offer_id=30`.

---

# 24. Получение статистики

```python
clicks = OFFER_CLICKS.get(offer_id, 0)
conversions = OFFER_CONVERSIONS.get(offer_id, 0)
reward = OFFER_REWARDS.get(offer_id, 0.0)
```

Для неизвестного оффера все значения будут нулевыми.

---

# 25. CR и RPC

```python
if clicks == 0:
    cr = 0.0
    rpc = 0.0
```

Это защита от деления на ноль.

Иначе:

```python
cr = conversions / clicks
rpc = reward / clicks
```

Пример:

```text
clicks = 10
conversions = 2
reward = 15.0

CR = 2 / 10 = 0.2
RPC = 15 / 10 = 1.5
```

Не путайте RPC со средней наградой на конверсию. Для RPC знаменатель — clicks.

---

# 26. Ответ `/stats/`

```python
response = {
    "offer_id": offer_id,
    "clicks": clicks,
    "conversions": conversions,
    "reward": reward,
    "cr": cr,
    "rpc": rpc,
}
```

Все ключи совпадают с условием.

---

# 27. Запуск приложения

```python
def main() -> None:
    """Run the application."""
    uvicorn.run(app, host="localhost")
```

В Uvicorn передаётся сам объект `app`, поэтому прямой запуск не зависит от имени Python-файла.

```python
if __name__ == "__main__":
    main()
```

Сервер запускается только при прямом выполнении:

```bash
python gp_page_3_greedy_sampler_app.py
```

Swagger UI:

```text
http://localhost:8000/docs
```

---

# 28. Как сбрасывать статистику

Состояние хранится в памяти процесса. Для чистого запуска:

1. остановите сервер через `Ctrl+C`;
2. снова запустите файл.

Все четыре словаря создадутся пустыми.

---

# 29. Ручная проверка

## Неизвестный оффер

Сразу после запуска:

```text
GET /offer_ids/999/stats/
```

Ожидается:

```json
{
  "offer_id": 999,
  "clicks": 0,
  "conversions": 0,
  "reward": 0.0,
  "cr": 0.0,
  "rpc": 0.0
}
```

## Первый sample

```text
GET /sample/?click_id=1&offer_ids=10,20
```

В ответе обязательно:

```json
{
  "click_id": 1,
  "offer_id": 10 или 20,
  "sampler": "random"
}
```

## Feedback с конверсией

Предположим, был выбран оффер 20:

```text
PUT /feedback/?click_id=1&reward=5
```

Ожидается:

```json
{
  "click_id": 1,
  "offer_id": 20,
  "is_conversion": true,
  "reward": 5.0
}
```

## Stats после feedback

```text
GET /offer_ids/20/stats/
```

Ожидается:

```json
{
  "offer_id": 20,
  "clicks": 1,
  "conversions": 1,
  "reward": 5.0,
  "cr": 1.0,
  "rpc": 5.0
}
```

---

# 30. Проверка перехода random -> greedy

После чистого запуска первые 100 вызовов `/sample` должны возвращать:

```text
"sampler": "random"
```

101-й вызов должен вернуть:

```text
"sampler": "greedy"
```

При этом greedy обязан выбирать только из кандидатов текущего запроса.

---

# 31. Почему решение соответствует распределению баллов

## `/feedback/` — 10%

Реализованы:

- получение click ID;
- восстановление offer ID;
- определение conversion;
- сумма reward;
- количество conversions;
- правильный JSON-ответ.

## `/stats/` — 40%

Реализованы:

- clicks;
- conversions;
- reward;
- CR;
- RPC;
- нулевая статистика неизвестного оффера;
- защита от деления на ноль.

## `/sample/` — 40%

Реализованы:

- parsing кандидатов;
- 100 случайных рекомендаций;
- greedy после инициализации;
- максимизация RPC;
- выбор только среди кандидатов;
- первый кандидат при равных нулевых RPC;
- сохранение click-to-offer;
- поле `sampler`.

## Качество — 10%

В коде есть:

- module docstring;
- docstrings функций;
- понятные имена;
- константа вместо магического числа;
- небольшая функция `get_rpc`;
- форматирование, совместимое с PEP 8;
- минимальная архитектура без лишних сущностей.

---

# 32. Частые неправильные решения

## Обновлять clicks в feedback

Неверно, потому что feedback может запаздывать или не прийти. Click считается в момент `/sample`.

## Передавать offer ID в feedback

Неверно: по условию он не передаётся. Нужно использовать `CLICK_TO_OFFER`.

## Считать conversion для `reward=0`

Неверно. В задаче conversion — только `reward > 0`.

## Делить reward на conversions

Это не RPC. Правильно:

```text
RPC = reward / clicks
```

## Выбирать лучший оффер из всех известных

Неверно. Выбор делается только среди `offer_ids` текущего запроса.

## Сортировать кандидатов

Неверно, потому что при отсутствии статистики требуется первый входной кандидат, а не минимальный ID.

## Не обрабатывать неизвестный оффер в stats

Прямое обращение к словарю вызовет `KeyError`. Нужно использовать `.get(..., 0)`.

---

# 33. Итоговый алгоритм словами

1. `/sample` получает click ID и строку кандидатов.
2. Строка преобразуется в список целых ID.
3. Считается общее число прошлых рекомендаций.
4. Первые 100 раз выбирается случайный кандидат.
5. После этого выбирается кандидат с максимальным RPC.
6. Рекомендация записывается в `OFFER_CLICKS`.
7. Связь клика и оффера записывается в `CLICK_TO_OFFER`.
8. `/feedback` по click ID находит оффер.
9. Reward добавляется к сумме оффера.
10. При reward больше нуля увеличивается conversion.
11. `/stats` возвращает накопленные показатели.
12. Для неизвестного оффера возвращаются нули.

Это полное минимальное решение Greedy Sampler.

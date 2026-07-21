# Page 4. Финальное исправленное решение ε-Greedy Sampler

## 1. Файл для отправки

Отправляйте:

```text
gp_page_4_epsilon_greedy_sampler_app.py
```

---

## 2. Три критические части

### Сброс между тестовыми startup

```python
@app.on_event("startup")
def reset_statistics() -> None:
    """Reset all in-memory statistics before every application startup."""
    OFFER_CLICKS.clear()
    CLICK_TO_OFFER.clear()
    OFFER_REWARDS.clear()
    OFFER_CONVERSIONS.clear()
```

### Подсчёт clicks в `/sample`

```python
OFFER_CLICKS[offer_id] = OFFER_CLICKS.get(offer_id, 0) + 1
```

### Feedback не увеличивает clicks

В feedback обновляются только:

```python
OFFER_REWARDS
OFFER_CONVERSIONS
```

---

# 3. Почему нельзя считать clicks в feedback

По определению задания:

```text
clicks = количество показов / рекомендаций оффера
```

Показ происходит в момент `/sample`.

Feedback может:

- прийти позже;
- не прийти вообще;
- прийти в другом порядке.

Если считать только feedback, статистика занижает число показов и тест после одного sample получает ноль вместо единицы.

---

# 4. Почему нельзя убрать startup reset

Тесты могут использовать несколько lifecycle одного импортированного модуля.

Без очистки предыдущие вызовы `/sample` загрязняют следующий тест.

Поэтому первый тестовый сценарий видел четыре старых клика offer 42.

---

# 5. Расчёт greedy RPC

```python
def get_rpc(offer_id: int) -> float:
    clicks = OFFER_CLICKS.get(offer_id, 0)
    if clicks == 0:
        return 0.0
    return OFFER_REWARDS.get(offer_id, 0.0) / clicks
```

Используется то же количество clicks, которое показывает `/stats`.

Нельзя использовать отдельный `feedback_count`: тогда greedy и stats начинают считать разные метрики.

---

# 6. ε-greedy

```python
if np.random.random() < EPSILON:
```

при:

```python
EPSILON = 0.1
```

означает:

```text
10% random
90% greedy
```

Random:

```python
offer_id = int(np.random.choice(offers_ids))
sampler = "random"
```

Greedy:

```python
offer_id = max(offers_ids, key=get_rpc)
sampler = "greedy"
```

Обе ветки выбирают только среди кандидатов текущего запроса.

---

# 7. Что происходит при равных RPC

Для:

```python
offers_ids = [45, 67]
```

и:

```text
RPC(45) = 0
RPC(67) = 0
```

выражение:

```python
max(offers_ids, key=get_rpc)
```

возвращает первый элемент:

```text
45
```

Это соответствует условию.

---

# 8. Полный жизненный цикл одного клика

## Sample

```text
click_id=100
offer_ids=10,20
```

Допустим, выбран offer 20.

Состояние:

```python
OFFER_CLICKS[20] = 1
CLICK_TO_OFFER[100] = 20
```

Stats сразу после sample:

```json
{
  "offer_id": 20,
  "clicks": 1,
  "conversions": 0,
  "reward": 0.0,
  "cr": 0.0,
  "rpc": 0.0
}
```

## Feedback без конверсии

```text
click_id=100
reward=0
```

Clicks остаётся 1.

```json
{
  "offer_id": 20,
  "clicks": 1,
  "conversions": 0,
  "reward": 0.0,
  "cr": 0.0,
  "rpc": 0.0
}
```

## Feedback с конверсией

Для другого клика того же оффера приходит reward 6.

Если всего было два sample:

```text
clicks = 2
conversions = 1
reward = 6
CR = 1 / 2 = 0.5
RPC = 6 / 2 = 3
```

---

# 9. Локальные проверки финального файла

Проверены два конкретных падения LMS.

## После reset неизвестная статистика

```python
stats(42)
```

даёт:

```python
{
    "offer_id": 42,
    "clicks": 0,
    "conversions": 0,
    "reward": 0.0,
    "cr": 0.0,
    "rpc": 0.0,
}
```

## После одного sample

```python
sample(1, "1009")
stats(1009)
```

даёт:

```python
{
    "offer_id": 1009,
    "clicks": 1,
    "conversions": 0,
    "reward": 0.0,
    "cr": 0.0,
    "rpc": 0.0,
}
```

## После feedback

```python
feedback(1, 5)
```

даёт:

```python
{
    "click_id": 1,
    "offer_id": 1009,
    "is_conversion": True,
    "reward": 5.0,
}
```

Stats:

```python
{
    "offer_id": 1009,
    "clicks": 1,
    "conversions": 1,
    "reward": 5.0,
    "cr": 1.0,
    "rpc": 5.0,
}
```

---

# 10. Что изменилось относительно предыдущего файла

Было:

```text
startup reset = есть
clicks в sample = нет
clicks в feedback = да
```

Стало:

```text
startup reset = есть
clicks в sample = да
clicks в feedback = нет
```

Именно эта комбинация соответствует обоим сообщениям LMS.

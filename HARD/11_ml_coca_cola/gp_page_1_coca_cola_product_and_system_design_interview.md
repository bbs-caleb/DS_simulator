# gp_page_1 — ML: COCA-COLA — продуктовый и system design разбор

## 1. Как объяснить задачу на интервью

Эта задача показывает, что ML-модель — это только часть системы.

Хороший ответ:

> У нас есть модель dynamic pricing. Она выдаёт raw recommended prices. Но перед публикацией мы должны применить business constraints: большая упаковка должна быть дороже, но выгоднее за единицу объёма, а товары одного формата должны иметь одинаковую цену. Поэтому нужен postprocessing / constraint layer.

---

## 2. Какие вопросы задать интервьюеру

Перед кодом нужно уточнить:

1. Цена всегда integer?
2. Growth price строгий?
3. Unit price decrease строгий?
4. Что важнее: L1 или количество изменений?
5. Как решать ничьи?
6. Может ли товар входить и в hline, и в vline?
7. Есть ли max price change?
8. Есть ли minimum margin?
9. Нужно ли сохранять price endings?
10. Сколько товаров в одной линейке?
11. Batch или online?
12. Какой SLA?

---

## 3. Формализация vertical line

Пусть:

```text
n_i — объём
p_i — цена
```

Если:

```text
n_i < n_{i+1}
```

то:

```text
p_i < p_{i+1}
```

и:

```text
p_i / n_i > p_{i+1} / n_{i+1}
```

Для integer price:

```text
p_{i+1} - p_i >= 1
```

Для unit price после перевода в коэффициенты:

```text
A * p_i - B * p_{i+1} >= 1
```

---

## 4. Формализация horizontal line

Для товаров одной `hline`:

```text
p_1 = p_2 = ... = p_k
```

Если цель — минимизировать L1, оптимальная общая цена лежит в медиане.

---

## 5. Целевая функция

Главная цель:

```text
min sum(abs(new_price - old_price))
```

Вторая цель:

```text
min count(new_price != old_price)
```

Вторая цель применяется только среди решений с минимальным L1.

---

## 6. Почему не встроить всё в модель

Можно пытаться обучить модель с ограничениями:

- monotonic constraints;
- custom loss;
- calibration;
- structured prediction.

Но отдельный postprocessing всё равно полезен:

- hard guarantees;
- проще аудит;
- бизнес-правила меняются быстрее модели;
- можно тестировать отдельно;
- юридические правила нельзя нарушать;
- можно объяснить каждое изменение.

---

## 7. Production architecture

```text
Product catalog
      ↓
Feature pipeline
      ↓
ML pricing model
      ↓
Raw price recommendations
      ↓
Constraint engine
      ↓
Independent validator
      ↓
Approval / publication
      ↓
Monitoring
```

### Product catalog

Хранит:

- item;
- brand;
- category;
- netto;
- unit;
- hline;
- vline;
- active flag.

### ML model

Возвращает:

- raw price;
- expected demand;
- expected revenue;
- expected margin;
- confidence;
- model version.

### Constraint engine

Применяет:

- Coca-Cola rule;
- horizontal equality;
- margin floor;
- max price change;
- legal constraints;
- supplier constraints;
- price endings.

### Validator

Независимо проверяет итоговые цены.

### Monitoring

Следит за:

- количеством нарушений до и после;
- долей изменённых SKU;
- L1 adjustment;
- revenue;
- margin;
- complaints;
- manual overrides.

---

## 8. Что логировать

Для каждого товара полезно хранить:

```text
item_id
old_price
model_price
final_price
changed_flag
hline
vline
rules_triggered
model_version
catalog_version
timestamp
```

Это нужно для:

- объяснений бизнесу;
- аудита;
- rollback;
- поиска багов;
- мониторинга модели.

---

## 9. Failure modes

### Ошибка каталога

Например, 0.5 л записали как 5 л.

Защита:

- data validation;
- диапазоны допустимых объёмов;
- anomaly detection;
- ручная проверка новых связей.

### Смешение единиц

В одну линейку попали литры и граммы.

Защита:

- unit должен быть частью ключа;
- проверка единиц перед оптимизацией.

### Массовая коррекция

Constraint layer меняет 60% цен.

Это может означать, что модель деградировала.

Защита:

- alert;
- guardrail;
- canary;
- rollback;
- сравнение с предыдущей моделью.

### Solver timeout

Защита:

- timeout;
- fallback;
- last good prices;
- ручная модерация.

---

## 10. A/B-тест

Нельзя случайно разнести связанные SKU по разным группам.

Если один товар линейки в control, а другой в treatment, покупатель увидит смешанную полку.

Лучше рандомизировать на уровне:

- магазина;
- региона;
- категории;
- целой группы связанных товаров.

Метрики:

- revenue;
- margin;
- units;
- conversion;
- complaints;
- manual overrides;
- cannibalization;
- product mix.

---

## 11. Применение в retail

В retail это нужно для:

- price ladder;
- управления маржой;
- снижения ручной работы;
- контроля каннибализации;
- понятной полки;
- автоматической публикации цен.

---

## 12. Применение в marketplace

Примеры:

- пакет 1 / 3 / 10 товаров;
- тариф продавца Basic / Pro / Enterprise;
- пакеты продвижения;
- комиссии по объёму;
- цена за лид.

Важно учитывать обе стороны рынка:

- покупатель;
- продавец;
- liquidity;
- retention;
- supply-demand balance.

---

## 13. Применение в финтехе

Примеры:

- пакеты переводов;
- API limits;
- эквайринг;
- страховые пакеты;
- комиссии по обороту.

Дополнительные ограничения:

- регуляторика;
- fair pricing;
- риск;
- прозрачность;
- KYC / AML.

---

## 14. iGaming / crypto / dating

Похожие pricing tiers бывают в:

- виртуальной валюте;
- бустах;
- премиум-подписках;
- лимитах;
- комиссиях.

Важно не забывать:

- responsible gaming;
- возрастные ограничения;
- AML/KYC;
- прозрачность цены;
- локальные законы.

---

## 15. Big Tech мышление

В Google, Meta, Anthropic, SpaceX, BP и других компаниях похожее мышление применяется в:

- cloud billing;
- API pricing;
- enterprise contracts;
- logistics;
- supply chain;
- advertising;
- compute packages;
- support tiers.

Главная идея:

> ML output должен пройти слой ограничений перед реальным действием.

---

## 16. Сильный ответ на интервью

Можно ответить так:

> Я бы не публиковал raw ML prices напрямую. Я бы построил constraint layer. Для vertical line задал бы hard constraints: total price растёт, unit price падает. Для horizontal line — equality constraint. Цель — минимальное L1-отклонение от ML-рекомендаций, а при равенстве — минимальное число изменённых SKU. После оптимизации я бы запускал независимый validator и мониторил changed_sku_share, adjustment size, revenue, margin и manual_override_rate.

---

## 17. Главный вывод

Зрелый DS/MLE строит не только модель.

Он строит систему:

```text
model → constraints → validation → monitoring → business decision
```

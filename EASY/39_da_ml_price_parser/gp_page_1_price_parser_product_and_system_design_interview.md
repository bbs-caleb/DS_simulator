# PRICE PARSER

# Продуктовое и System Design интервью

## 1. Что проверяет интервьюер

Задача «спроектировать систему мониторинга цен» проверяет не знание одной библиотеки. Интервьюер оценивает, умеете ли вы:

- понять бизнес-цель;
- уточнить требования;
- оценить масштаб;
- спроектировать поток данных;
- выбрать компромиссы;
- обеспечить качество;
- обработать сбои;
- связать архитектуру с деньгами.

Слабый ответ:

> Напишем BeautifulSoup, найдём CSS-класс и запишем цену в PostgreSQL.

Сильный ответ начинается с вопроса:

> Для какого решения будут использоваться данные: отчёт, рекомендации человеку или автоматический repricing?

---

# 2. Универсальная структура ответа

1. Бизнес-цель.
2. Пользователи.
3. Functional requirements.
4. Non-functional requirements.
5. Масштаб.
6. Модель данных.
7. High-level architecture.
8. Глубокий разбор компонентов.
9. Data Quality.
10. Failure modes.
11. Security и legal.
12. Метрики.
13. Эксперимент и rollout.
14. Компромиссы.

---

# 3. Бизнес-цель

Уточняющие вопросы:

- данные используются только в BI?
- менеджер принимает решение вручную?
- цена меняется автоматически?
- какие категории критичны?
- какова стоимость ошибочного снижения?
- насколько быстро нужно реагировать?

Сильная формулировка:

> Если система аналитическая, допустима часовая задержка и ручная проверка. Если данные напрямую запускают repricing, нужны строгая валидация, audit trail, минимальная маржа, лимиты изменения и kill switch.

---

# 4. Пользователи системы

## Category Manager

Нужны:

- конкурентные цены;
- история;
- промо;
- наличие;
- объяснение аномалий.

## Pricing Engine

Нужны:

- единая валюта;
- confidence;
- freshness;
- сопоставленный SKU;
- структурированный price type.

## Data Scientist

Нужны:

- длинная история;
- raw data;
- parser version;
- статусы ошибок;
- признаки промо;
- отсутствие leakage.

## Finance и Commercial

Нужны:

- влияние на gross profit;
- margin guardrails;
- оценка потерь;
- контроль отклонений.

---

# 5. Functional requirements

1. Получать страницы.
2. Извлекать название, цену, валюту, наличие, продавца и доставку.
3. Различать regular, sale, loyalty и installment price.
4. Нормализовать валюту и единицы.
5. Матчить внешний товар с внутренним SKU.
6. Хранить историю.
7. Обнаруживать изменения.
8. Валидировать.
9. Отправлять алерты.
10. Отдавать данные через API, DWH или stream.
11. Поддерживать ручную проверку.
12. Вести audit log.

---

# 6. Non-functional requirements

- latency;
- throughput;
- availability;
- durability;
- scalability;
- observability;
- maintainability;
- cost;
- security.

Пример SLO:

```text
99% KVI не старше 30 минут
95% обычных SKU не старше 6 часов
parse success ключевых источников ≥ 98%
API availability ≥ 99.9%
```

---

# 7. Оценка масштаба

Предположим:

```text
5 млн внутренних SKU
20 конкурентов
30% имеют матч у конкретного конкурента
4 проверки в сутки
```

```text
5 000 000 × 20 × 0.3 × 4 = 120 000 000 проверок/сутки
```

После оценки нужно предложить приоритизацию:

- KVI — часто;
- high-revenue SKU — чаще;
- long tail — реже;
- адаптивная частота по волатильности;
- отдельная политика для out-of-stock.

На интервью важен порядок величины, а не идеальная арифметика.

---

# 8. High-level architecture

```text
Catalog + Product Matches
          ↓
       Scheduler
          ↓
       Task Queue
          ↓
HTTP Fetchers / Browser Workers
          ↓
    Raw HTML Storage
          ↓
      Parser Service
          ↓
     Validation Layer
       ↙          ↘
Price History    Quarantine
       ↓
 Matching Service
       ↓
  Pricing Engine
       ↓
 BI / Alerts / API
```

---

# 9. Scheduler

Определяет частоту и приоритет.

Возможная логика:

```text
priority = revenue_weight
         × strategic_weight
         × volatility_weight
         × freshness_need
```

Не все SKU нужно проверять одинаково часто.

---

# 10. Queue

Очередь обеспечивает:

- backpressure;
- retry;
- масштабирование;
- приоритеты;
- разделение producer/consumer;
- replay.

Система должна быть идемпотентной: повторная задача не создаёт неконтролируемые дубли.

Пример ключа:

```text
competitor_id + url + scheduled_time_bucket
```

---

# 11. Fetcher

## Static HTTP Fetcher

Плюсы:

- дешёвый;
- быстрый;
- масштабируемый.

## Browser Worker

Нужен для JavaScript и сложных пользовательских сценариев.

Минусы:

- дороже;
- медленнее;
- требует больше ресурсов.

Сильный компромисс:

> Сначала использовать разрешённый API, фид, JSON endpoint или статический HTML. Browser automation — дорогой fallback.

---

# 12. Raw Storage

Зачем хранить HTML:

- расследование;
- аудит;
- повторный parsing;
- regression tests;
- сравнение версий.

Компромисс стоимости:

- полный HTML для ошибок;
- выборка успешных;
- compression;
- ограниченный retention;
- object storage.

---

# 13. Parser Service

Контракт:

```text
parse(source, html, context) -> ParsedProduct
```

`context` может включать:

- URL;
- регион;
- язык;
- ожидаемую валюту;
- категорию;
- внутренний товар.

Архитектура адаптеров:

```text
CompetitorAParser
CompetitorBParser
CompetitorCParser
```

Общие библиотеки:

- currency normalization;
- locale handling;
- unit normalization;
- error codes;
- confidence.

---

# 14. Validation Layer

## Синтаксические проверки

- преобразование в число;
- валюта распознана;
- обязательные поля заполнены.

## Семантические

- sale ≤ regular;
- monthly payment не full price;
- unit price согласуется с упаковкой.

## Исторические

- сравнение с предыдущим наблюдением;
- отклонение от медианы;
- category-specific threshold.

## Кросс-источниковые

- сравнение с рынком;
- проверка относительно категории;
- поиск экстремальных выбросов.

---

# 15. Quarantine

Подозрительная запись:

```text
status = needs_review
reason = 90_percent_price_drop
```

Для автоматического repricing лучше потерять часть coverage, чем применить опасную ложную цену.

---

# 16. Модель данных

```sql
price_observation (
    observation_id,
    internal_product_id,
    external_product_id,
    competitor_id,
    seller_id,
    region_id,
    url,
    observed_at,
    fetched_at,
    parsed_at,
    current_price,
    regular_price,
    loyalty_price,
    currency,
    availability,
    delivery_price,
    promotion_text,
    parser_version,
    parse_status,
    confidence,
    raw_reference
)
```

Почему несколько timestamps:

- `observed_at` — когда цена была представлена источником;
- `fetched_at` — когда получили страницу;
- `parsed_at` — когда обработали.

---

# 17. Serving Layer

Для онлайн-чтения:

```text
GET /v1/prices/current?product_id=123&competitor_id=abc&region_id=tashkent
```

Для аналитики:

- DWH;
- columnar storage;
- materialized view;
- batch export.

Для событий:

- stream `price_changed`.

---

# 18. Freshness и TTL

Если свежая цена недоступна:

1. использовать последнюю валидную;
2. пометить stale;
3. запретить автоматический repricing после TTL;
4. использовать агрегат рынка;
5. отправить на ручную проверку.

Сильная формулировка:

> Историческая цена может оставаться в аналитике, но после TTL не должна автоматически менять нашу цену.

---

# 19. Отказоустойчивость

- retry с exponential backoff;
- timeout;
- dead-letter queue;
- circuit breaker;
- rate limiting;
- autoscaling;
- replay;
- fallback parser;
- previous valid value;
- kill switch.

Чаще достаточно at-least-once доставки и идемпотентной записи. Потеря наблюдения обычно хуже безопасного дубля.

---

# 20. Batch или Streaming

## Batch

Подходит для:

- ежедневной аналитики;
- long tail;
- стабильных категорий;
- ограниченного бюджета.

## Near Real-Time

Подходит для:

- электроники;
- авиабилетов;
- Buy Box;
- flash sale;
- автоматического repricing.

Часто лучший вариант — гибрид.

---

# 21. Где нужен ML

- product matching;
- classification price type;
- извлечение из неоднородного текста;
- anomaly detection;
- priority scheduling;
- confidence estimation;
- price optimization.

Сильная позиция:

> Для стабильного DOM правила дешевле и интерпретируемее. ML нужен, когда источников много, структура неоднородна, а правила перестают масштабироваться.

---

# 22. Метрики

## Leading

- coverage;
- freshness;
- parse success;
- correctness;
- match precision;
- latency;
- доля валидных цен.

## Business

- gross profit;
- revenue;
- conversion;
- price index;
- margin rate;
- market share;
- inventory turnover.

## Guardrails

- цены ниже себестоимости;
- аномальные изменения;
- ручные откаты;
- OOS;
- complaints;
- regulatory incidents.

Возможная North Star:

```text
доля ценовых решений, принятых на основе свежих и валидных конкурентных данных
```

или конечная:

```text
incremental gross profit от pricing-системы
```

---

# 23. A/B-тест

Возможная схема:

- treatment SKU используют новую систему;
- control остаётся на старом процессе;
- стратификация по категории и выручке;
- учёт промо и сезонности;
- guardrails по margin и OOS.

Метрики:

- gross profit;
- conversion;
- units;
- revenue;
- margin rate;
- OOS;
- cancellations.

Нужно учитывать interference: изменение цены одного SKU влияет на товары-заменители. Иногда лучше рандомизировать по категории, региону или кластеру.

---

# 24. Legal и этика

Нужно упомянуть:

- применимое законодательство;
- условия использования источника;
- разрешённые API и фиды;
- rate limits;
- data privacy;
- legal review;
- риск антиконкурентного поведения.

Мониторинг рынка и автоматическое ценообразование должны проходить юридическую проверку, особенно если система может непреднамеренно координировать цены.

---

# 25. MVP

Хороший MVP:

- 1–2 ключевых конкурента;
- одна категория;
- небольшой набор KVI;
- ежедневное обновление;
- rule-based parser;
- ручная проверка;
- dashboard;
- без автоматического repricing.

Цель MVP — доказать correctness, coverage и бизнес-полезность.

---

# 26. Rollout

1. Shadow mode.
2. Read-only dashboard.
3. Рекомендации менеджеру.
4. Автоматизация малой доли SKU.
5. Лимиты изменения.
6. Расширение категорий.
7. Полная автоматизация с guardrails.

Shadow mode означает, что система считает решения, но не применяет их. Это позволяет сравнить рекомендации с действиями людей и измерить потенциальные ошибки.

---

# 27. Product Sense вопросы

1. Что считается конкурентом?
2. Какая цена сопоставима?
3. Учитываем ли доставку?
4. Что делать с loyalty price?
5. Что делать с отсутствующим товаром?
6. Какова допустимая задержка?
7. Сколько стоит ошибка?
8. Какие SKU стратегические?
9. Нужна ли автоматизация?
10. Какие пределы изменения?
11. Кто подтверждает аномалии?
12. Какие регионы?
13. Как оцениваем matching?
14. Нужна ли история?
15. Как выглядит rollback?
16. Какие legal constraints?
17. Как измеряется business impact?

---

# 28. Частые вопросы интервьюера

## Что делать, если изменился HTML?

- monitoring success rate;
- contract tests;
- raw HTML;
- fallback;
- versioning;
- alert;
- rollback;
- quarantine.

## Как выбрать частоту?

Учитывать:

- выручку;
- волатильность;
- KVI;
- стоимость запроса;
- SLA;
- риск stale data.

## Как найти неверную цену?

- диапазоны;
- история;
- другие конкуренты;
- category rules;
- confidence;
- ручная выборка;
- anomaly model.

## Что важнее: precision или recall?

Для автоматического repricing обычно precision. Ложная цена опаснее пропущенной.

## Как масштабировать?

- queue;
- stateless workers;
- autoscaling;
- sharding по источнику;
- adaptive scheduling;
- раздельные browser и HTTP pools.

---

# 29. Failure Mode Analysis

| Сбой | Последствие | Защита |
|---|---|---|
| Выбрана старая цена | Неверное сравнение | Семантика и тесты |
| Взята рассрочка | Сильное занижение | Price type classifier |
| Потеряна валюта | Ошибка в разы | Явная currency |
| Сломался HTML | Падение coverage | Alert и fallback |
| Ошибка матчинга | Другой SKU | Confidence и review |
| Stale data | Позднее решение | TTL |
| Дубли | Искажённая аналитика | Idempotency |
| Массовый repricing bug | Финансовый ущерб | Limits и kill switch |
| Не учтена доставка | Нечестное сравнение | Total landed price |

---

# 30. Пример сильного ответа

> Сначала уточню, используется ли система для аналитики или автоматического repricing. Во втором случае precision, freshness и защита бизнеса важнее максимального coverage.
>
> Каталог и таблица матчей передают задания scheduler. Scheduler учитывает выручку, KVI и волатильность и отправляет задачи в очередь. Статические страницы обрабатываются HTTP workers, динамические — отдельным browser pool. Raw HTML хранится в object storage с ограниченным retention.
>
> Source-specific parser извлекает current, regular, loyalty price, currency, seller, availability и delivery. Общий слой нормализует локаль и единицы. Validation проверяет диапазоны, историю и тип цены. Подозрительные записи идут в quarantine.
>
> Pricing engine получает только свежие значения с высоким confidence. Он применяет минимальную маржу, максимальный шаг изменения, TTL и kill switch. Основные технические метрики — coverage, correctness, freshness и latency. Бизнесовые — gross profit, conversion, price index и доля ошибочных repricing-решений.
>
> Запускал бы через shadow mode, затем рекомендации человеку и только после подтверждения качества — ограниченный автоматический rollout.

---

# 31. Как показать senior-мышление

Senior обсуждает не только happy path:

- regional price;
- seller;
- loyalty eligibility;
- delivery;
- timezone;
- versioning;
- data lineage;
- audit;
- manual override;
- ownership;
- on-call;
- rollback;
- cost;
- legal review;
- experiment design.

---

# 32. Финальная шпаргалка

Отвечайте через четыре слоя.

## Бизнес

```text
Какое решение улучшаем и сколько стоит ошибка?
```

## Данные

```text
Какую цену, для какого товара, региона, продавца и момента получили?
```

## Система

```text
Как собираем, валидируем, храним и доставляем?
```

## Контроль

```text
Как узнаём об ошибке и предотвращаем ущерб?
```

Такой ответ показывает, что вы понимаете не только функцию, но и промышленную систему.

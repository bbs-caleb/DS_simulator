# Smart-Link I: продуктовый и system design разбор для интервью

## Как рассуждать о системе ε-greedy на продуктовом, аналитическом и ML System Design интервью

---

# 1. Что проверяет интервьюер

Когда кандидату дают задачу вида:

> Спроектируйте Smart-Link, который автоматически направляет трафик на лучшие офферы.

интервьюер обычно проверяет не только знание формулы ε-greedy.

Он хочет понять, умеет ли кандидат:

- уточнить бизнес-цель;
- определить пользователей и участников;
- выбрать правильную единицу принятия решения;
- сформулировать reward;
- увидеть delayed feedback;
- заметить контрфактуальную проблему;
- продумать online serving;
- спроектировать события и хранилища;
- предложить эксперимент;
- определить guardrails;
- предусмотреть сбои и fallback;
- объяснить компромиссы простым языком.

Сильный кандидат сначала проектирует **продуктовое решение**, затем **данные**, затем **алгоритм**, и только потом говорит про инфраструктуру.

---

# 2. Структура сильного ответа

Удобный порядок:

```text
1. Уточнить цель и участников.
2. Определить решение и момент принятия решения.
3. Определить кандидатов и ограничения.
4. Определить reward и задержку.
5. Выбрать baseline.
6. Выбрать bandit-политику.
7. Спроектировать события и данные.
8. Спроектировать online architecture.
9. Продумать эксперимент.
10. Добавить мониторинг, safety и fallback.
11. Обсудить масштабирование и дальнейшие улучшения.
```

Не начинайте ответ с фразы «я возьму FastAPI, Kafka и Redis». Это преждевременно. Сначала нужно понять, что именно оптимизируется.

---

# 3. Уточняющие вопросы бизнесу

## 3.1. Кто основной клиент продукта?

Возможные ответы:

- арбитражник хочет максимизировать свой доход;
- рекламодатель хочет максимизировать качественные actions;
- сеть хочет максимизировать маржу;
- продукт должен балансировать все стороны.

Это критично. Один и тот же алгоритм с разным reward будет принимать разные решения.

## 3.2. Что является единицей решения?

Обычно один входящий клик.

Но возможны варианты:

- сессия;
- пользователь;
- рекламная кампания;
- пачка трафика;
- дневная квота.

Нужно уточнить, можно ли одному пользователю показывать разные офферы при повторных визитах.

## 3.3. Какие офферы являются кандидатами?

Нужно выяснить:

- все активные офферы или только выбранная группа;
- разрешённые страны;
- publisher restrictions;
- device restrictions;
- бюджет;
- возрастные ограничения;
- compliance;
- frequency caps;
- приоритетные договорённости.

## 3.4. Как определяется успех?

Варианты:

- созданный action;
- подтверждённый action;
- выплата;
- revenue;
- profit;
- LTV;
- advertiser ROI.

## 3.5. Когда приходит reward?

- мгновенно;
- через часы;
- через дни;
- после ручной проверки;
- после окончания return window.

## 3.6. Какой объём трафика?

Это влияет на:

- скорость обучения;
- допустимый epsilon;
- требования к latency;
- архитектуру хранения;
- статистическую мощность эксперимента.

## 3.7. Какова цена плохого решения?

- потеря одного клика;
- нарушение закона;
- перерасход бюджета;
- потеря рекламодателя;
- финансовый fraud;
- ущерб пользователю.

От этого зависит допустимый уровень exploration.

---

# 4. Продуктовая постановка

## 4.1. Пользовательская проблема

Начинающему publisher сложно вручную определить, какой оффер лучше подходит его трафику.

Smart-Link снижает барьер входа:

- не нужно выбирать один оффер;
- система автоматически распределяет трафик;
- статистика обновляется в реальном времени;
- новые офферы получают тестовый трафик;
- слабые офферы постепенно получают меньше кликов.

## 4.2. Ценностное предложение

Для publisher:

- выше EPC;
- меньше ручной работы;
- быстрее обнаруживаются хорошие офферы;
- проще запускать кампанию.

Для advertiser:

- больше релевантного трафика;
- выше качество actions;
- лучше используется бюджет.

Для сети:

- растёт объём транзакций;
- увеличивается retention партнёров;
- растёт маржа;
- появляется технологический moat.

## 4.3. North-star metric

Пример:

```text
Confirmed publisher earnings per eligible click
```

Почему не просто CR:

- payouts различаются;
- часть конверсий отклоняется;
- высокий CR не гарантирует высокий доход.

Другой вариант для сети:

```text
Confirmed contribution margin per eligible click
```

Но его использование должно соответствовать обещанию продукта.

---

# 5. Метрики

## 5.1. Primary metric

Один основной результат эксперимента:

- confirmed revenue per click;
- confirmed profit per click;
- publisher EPC;
- approved actions per 1 000 clicks.

## 5.2. Secondary metrics

- raw conversion rate;
- approval rate;
- average payout;
- advertiser ROI;
- budget utilization;
- time to first conversion;
- publisher retention;
- доля трафика на новых офферах.

## 5.3. Guardrails

- fraud rate;
- rejected action rate;
- complaint rate;
- latency p95/p99;
- redirect failure rate;
- budget overspend;
- traffic concentration;
- доля офферов с нарушением гео;
- revenue decline для ключевых партнёров;
- churn.

## 5.4. Diagnostic metrics

- exploration rate;
- доля exploitation;
- action probability distribution;
- количество доступных кандидатов;
- доля fallback;
- lag до reward;
- доля незрелых кликов;
- state update delay;
- event duplication rate.

---

# 6. Определение bandit-задачи

## Arms

Офферы, прошедшие eligibility filter.

## Decision

Выбор одного оффера для одного клика.

## Reward

Например:

```text
confirmed_payout - expected_fraud_loss
```

или базовый бинарный reward для MVP.

## Horizon

Необходимо уточнить, за какой период максимизируется результат:

- один день;
- жизнь кампании;
- долгосрочная ценность publisher;
- lifetime offer.

## Constraints

- budget caps;
- geo restrictions;
- compliance;
- publisher rules;
- traffic source rules;
- frequency caps;
- SLA.

---

# 7. Baselines

Перед ε-greedy необходимо назвать baselines.

## Baseline 1. Random

Равномерное распределение трафика.

Плюсы: собирает unbiased данные.

Минусы: теряет много денег.

## Baseline 2. Static best by historical EPC

Выбрать оффер с максимальным историческим EPC.

Плюсы: просто.

Минусы: не адаптируется и страдает от selection bias.

## Baseline 3. Round-robin

По очереди показывать офферы.

Плюсы: равномерное покрытие.

Минусы: не максимизирует текущую награду.

## Baseline 4. Greedy

Всегда выбирать текущего лидера.

Плюсы: высокая краткосрочная эксплуатация.

Минусы: lock-in.

## Candidate. ε-greedy

Простой баланс exploration/exploitation.

---

# 8. Логика ε-greedy в продукте

Пусть для каждого Smart-Link и оффера хранится оценка `Q`.

На входе:

- smart_link_id;
- click context;
- список eligible offers.

Алгоритм:

```text
1. Отфильтровать недоступные офферы.
2. Получить оценки кандидатов.
3. С вероятностью epsilon перейти в exploration.
4. Иначе выбрать лидера.
5. При ties выбрать случайно среди лидеров.
6. Посчитать точную вероятность выбранного действия.
7. Записать immutable decision event.
8. Выполнить redirect.
9. После reward обновить состояние.
```

---

# 9. Требования к latency и доступности

Redirect находится в критическом пользовательском пути.

Каждые дополнительные миллисекунды могут снижать конверсию.

Пример нефункциональных требований:

- p50 < 20 ms;
- p95 < 50 ms;
- p99 < 100 ms;
- availability 99.99%;
- zero invalid redirects;
- graceful degradation.

Конкретные числа на интервью нужно обозначить как предварительные и согласовать с бизнесом.

---

# 10. Высокоуровневая архитектура

```text
Пользовательский клик
        |
        v
Edge / Redirect Gateway
        |
        v
Eligibility Service -------- Offer Config DB
        |
        v
Decision Service ----------- Fast State Store
        |                         |
        |                         v
        |                    Policy State
        v
Decision Event Log --------> Kafka / Event Bus
        |
        v
HTTP 302 Redirect на рекламодателя

Позже:
Advertiser Postback / Conversion API
        |
        v
Conversion Ingestion
        |
        v
Attribution + Validation + Fraud
        |
        v
Reward Event
        |
        v
Policy Updater ---------> State Store
        |
        v
Analytics Warehouse / Monitoring
```

---

# 11. Компоненты

## 11.1. Redirect Gateway

Функции:

- принимает клик;
- создаёт request_id/click_id;
- собирает базовый контекст;
- вызывает decision service;
- выполняет HTTP redirect;
- использует fallback при сбое.

## 11.2. Offer Configuration Store

Хранит:

- offer_id;
- status;
- payout;
- geo;
- allowed traffic sources;
- device rules;
- budget;
- start/end time;
- advertiser;
- category;
- compliance flags.

Конфигурация меняется реже, чем приходят клики, поэтому её можно кэшировать.

## 11.3. Eligibility Service

Возвращает только допустимые офферы.

Должен быть детерминированным и аудируемым.

Пример результата:

```json
{
  "eligible_offer_ids": [101, 104, 109],
  "excluded": {
    "102": "budget_exhausted",
    "103": "geo_not_allowed"
  }
}
```

## 11.4. Decision Service

Функции:

- получает кандидатов;
- читает policy state;
- выполняет ε-greedy;
- считает action probability;
- возвращает решение и версию политики.

## 11.5. State Store

Ключ может выглядеть так:

```text
smart_link_id + segment_id + offer_id
```

Храним:

- count;
- reward_sum;
- estimate;
- last_update_at;
- version.

Для высокой нагрузки подходит Redis или другой low-latency KV store.

## 11.6. Event Bus

Нужен, чтобы отделить быстрый redirect от тяжёлой обработки.

События:

- click_received;
- decision_made;
- redirect_completed;
- conversion_created;
- conversion_approved;
- conversion_rejected;
- reward_finalized;
- policy_updated.

## 11.7. Attribution Service

Связывает conversion с click_id.

Проверяет:

- окно атрибуции;
- дубликаты;
- статус;
- advertiser postback signature;
- cross-device правила.

## 11.8. Fraud Service

Может выдавать:

- fraud score;
- block/allow;
- delayed review;
- final label.

## 11.9. Policy Updater

Обновляет статистику асинхронно после финального reward.

Не должен повторно учитывать одно событие.

## 11.10. Analytics Warehouse

Используется для:

- отчётности;
- A/B-анализа;
- drift detection;
- расследований;
- обучения более сложных моделей.

---

# 12. API дизайн

## 12.1. Decision endpoint

```http
POST /v1/decision
```

Пример запроса:

```json
{
  "smart_link_id": 42,
  "publisher_id": 7,
  "campaign_id": 99,
  "context": {
    "country": "AM",
    "device_type": "mobile",
    "os": "android",
    "traffic_source": "social"
  }
}
```

Пример ответа:

```json
{
  "request_id": "b7d9...",
  "offer_id": 104,
  "redirect_url": "https://advertiser.example/...",
  "decision_type": "exploration",
  "action_probability": 0.033333,
  "policy_version": "epsilon_greedy_v3",
  "epsilon": 0.1
}
```

## 12.2. Reward endpoint

```http
POST /v1/rewards
```

```json
{
  "event_id": "conv-123",
  "request_id": "b7d9...",
  "reward_type": "approved_conversion",
  "reward_value": 8.0,
  "occurred_at": "2026-07-19T10:30:00Z"
}
```

Требования:

- идемпотентность;
- аутентификация;
- валидация подписи;
- обработка out-of-order событий;
- повторная доставка.

---

# 13. Схема данных

## 13.1. Decision events

```text
decision_id
click_id
request_timestamp
smart_link_id
publisher_id
campaign_id
context_json
eligible_offer_ids
selected_offer_id
decision_type
epsilon
action_probability
policy_version
estimated_values
latency_ms
fallback_reason
```

## 13.2. Conversion events

```text
event_id
click_id
offer_id
advertiser_id
conversion_type
status
raw_value
currency
occurred_at
received_at
fraud_score
```

## 13.3. Final rewards

```text
reward_event_id
decision_id
final_reward
reward_definition_version
finalized_at
source_event_ids
```

## 13.4. Policy state

```text
smart_link_id
segment_id
offer_id
selection_count
reward_count
reward_sum
estimated_value
last_updated_at
state_version
```

---

# 14. Delayed reward design

## 14.1. Почему это сложно

Клик может быть сегодня, подтверждение — через неделю.

Если сравнивать вчерашние клики с полностью созревшей прошлой неделей, свежая когорта будет выглядеть хуже.

## 14.2. Решение

Разделить:

- provisional events;
- finalized rewards.

Policy updater может:

- обновлять только финальные rewards;
- либо использовать промежуточные оценки и корректировать их позже.

## 14.3. Mature cohort analysis

Для аналитики сравнивать когорты, у которых прошло одинаковое время с момента клика.

Например, считать 7-day confirmed reward только для кликов старше 7 дней.

---

# 15. Конкурентные обновления

При высокой нагрузке два reward события могут одновременно обновить один и тот же счётчик.

Проблема lost update:

```text
оба процесса прочитали count = 100
первый записал 101
второй тоже записал 101
ожидалось 102
```

Решения:

- atomic increment;
- compare-and-swap;
- optimistic locking;
- stream partitioning by key;
- single writer per partition.

---

# 16. Exactly-once и идемпотентность

На практике event bus чаще даёт at-least-once delivery.

Поэтому consumer обязан быть идемпотентным.

Подход:

```text
1. Проверить event_id.
2. Если уже обработан — вернуть успех без повторного обновления.
3. Иначе атомарно записать processed event и обновить state.
```

---

# 17. Fallback policy

Система должна работать при:

- недоступности state store;
- timeout decision service;
- пустом наборе кандидатов;
- повреждённой конфигурации;
- неизвестном smart_link_id.

Варианты fallback:

1. статический безопасный оффер;
2. последний известный лучший оффер из локального кэша;
3. round-robin по доступным офферам;
4. рекламная заглушка;
5. возврат publisher-defined destination.

Fallback должен быть:

- быстрым;
- безопасным;
- наблюдаемым;
- ограниченным по времени;
- не нарушать eligibility.

---

# 18. Кэширование

Можно кэшировать:

- offer configuration;
- eligible candidates для стабильных сегментов;
- policy state;
- fallback selection.

Нужно продумать:

- TTL;
- invalidation;
- stale data;
- budget updates;
- emergency stop.

Budget и legal flags могут требовать почти мгновенной инвалидизации.

---

# 19. Масштабирование

## 19.1. Горизонтальное масштабирование

Decision service должен быть stateless, а состояние храниться во внешнем store.

## 19.2. Шардирование

Ключ шардирования:

- smart_link_id;
- publisher_id;
- offer_id;
- region.

Нужно избегать hot keys для очень крупных Smart-Link.

## 19.3. Региональное размещение

Redirect лучше обслуживать близко к пользователю.

Но состояние между регионами может расходиться.

Варианты:

- regional policies;
- eventual consistency;
- периодическая синхронизация;
- централизованный updater;
- глобальный read-replica setup.

---

# 20. Экспериментальный дизайн

## 20.1. Контроль

Текущая логика выбора оффера.

## 20.2. Treatment

ε-greedy policy.

## 20.3. Единица рандомизации

Варианты:

- click;
- user;
- publisher;
- campaign;
- smart_link.

Click-level randomization даёт высокую мощность, но может вызывать contamination.

Publisher-level randomization чище для бизнес-эффекта, но требует больше времени и участников.

## 20.4. Interference

Один оффер имеет общий бюджет. Treatment может быстро его исчерпать и повлиять на control.

Это нарушение SUTVA.

Возможные решения:

- раздельные бюджеты;
- кластерная рандомизация;
- switchback design;
- анализ на уровне рынка/времени;
- ограничение treatment traffic.

## 20.5. Метрика

Нельзя сравнивать незрелые conversions.

Нужно заранее определить:

- attribution window;
- maturity window;
- status accepted as success;
- currency conversion;
- outlier treatment.

## 20.6. Длительность

Определяется:

- MDE;
- baseline rate;
- variance;
- volume;
- delayed feedback;
- сезонностью.

## 20.7. Ramp-up

Пример:

```text
1% → 5% → 10% → 25% → 50%
```

На каждом шаге проверяются guardrails.

---

# 21. Shadow mode

До реального переключения можно запускать новую policy в тени.

Система:

- не меняет redirect;
- вычисляет, какой оффер выбрала бы новая политика;
- пишет решение в лог;
- проверяет latency, стабильность и candidate coverage.

Ограничение: reward альтернативного оффера неизвестен. Shadow mode не доказывает бизнес-эффект, но хорошо проверяет инфраструктуру.

---

# 22. Мониторинг

## 22.1. Технический

- QPS;
- latency p50/p95/p99;
- error rate;
- timeout rate;
- cache hit rate;
- state store latency;
- Kafka lag;
- duplicate event rate;
- fallback rate.

## 22.2. Data quality

- missing click_id;
- unknown offer_id;
- пустой candidate set;
- reward без decision;
- decision без redirect;
- out-of-order events;
- currency mismatch;
- отрицательные payouts;
- abnormal approval lag.

## 22.3. Policy

- actual exploration share;
- action distribution;
- top-offer concentration;
- estimate drift;
- reward drift;
- difference by geo/publisher/device;
- new-offer coverage.

## 22.4. Business

- EPC;
- approved conversion rate;
- margin per click;
- advertiser rejection;
- publisher complaints;
- budget pacing;
- partner churn.

---

# 23. Алерты

Примеры:

- fallback > 1% за 5 минут;
- p99 latency > 100 ms;
- пустой candidate set вырос в 3 раза;
- один offer получает > 90% трафика неожиданно;
- approved reward снизился на 30%;
- fraud rate вырос выше порога;
- budget overspend > 0;
- policy state не обновлялся 15 минут;
- action probability отсутствует в логах.

---

# 24. Versioning

Нужно версионировать:

- policy code;
- epsilon;
- reward definition;
- eligibility rules;
- feature schema;
- attribution logic;
- state snapshot;
- experiment assignment.

Иначе невозможно воспроизвести решение прошлого месяца.

---

# 25. Privacy, legal и ethics

Контекст может содержать чувствительные признаки.

Нужно:

- собирать минимум данных;
- ограничивать retention;
- шифровать данные;
- разделять PII и decision logs;
- обеспечивать access control;
- соблюдать consent;
- не использовать запрещённые признаки;
- проводить fairness review для регулируемых продуктов.

В fintech, betting, health и employment цена ошибки особенно высока.

---

# 26. Как обсуждать ε

Сильный ответ:

> Я не буду выбирать epsilon произвольно. Сначала оценю объём трафика, стоимость exploration, число офферов, скорость drift и задержку reward. Для MVP задам небольшой ограниченный epsilon и проведу simulation plus controlled ramp-up. В нестационарной среде сохраню минимальный exploration floor или использую adaptive policy.

Слабый ответ:

> Обычно epsilon равен 0.1, поэтому поставлю 0.1.

---

# 27. Как обсуждать reward

Сильный ответ:

> Сначала уточню, кто является клиентом Smart-Link. Если обещание publisher — максимизировать доход, primary reward должен отражать подтверждённую publisher value per click. При этом fraud, rejection, latency и budget overspend станут guardrails. Для раннего MVP можно начать с binary approved action, но это только proxy.

---

# 28. Как обсуждать cold start

Нужно упомянуть:

- minimum traffic quota;
- priors по категории;
- optimistic initialization;
- exploration caps;
- защита от плохих новых офферов;
- отдельный onboarding period;
- использование contextual model.

---

# 29. Как обсуждать нестационарность

Нужно сказать, что обычное sample average по всей истории плохо адаптируется.

Варианты:

- constant step size;
- sliding window;
- decay;
- change point detection;
- minimum epsilon;
- reinitialization после крупных изменений оффера.

---

# 30. Как обсуждать offline evaluation

Нужно прямо произнести:

> У нас есть только reward выбранного действия, поэтому обычная offline-валидация biased. Я буду логировать propensity каждого решения и использовать рандомизированный holdout или off-policy estimators, а финальный эффект подтвержу online experiment.

Это один из самых сильных сигналов зрелости кандидата.

---

# 31. Типичные follow-up вопросы

## Почему не supervised learning?

Потому что для каждого клика наблюдается reward только одного выбранного оффера. Нет полного target по всем альтернативам, а политика сама влияет на собираемые данные.

## Почему не всегда лучший исторический оффер?

История biased текущей политикой, среда меняется, новые офферы не имеют данных, а агрегированно лучший оффер может быть плохим для отдельных сегментов.

## Что произойдёт при epsilon = 0?

Полностью greedy policy. Нет систематического exploration, высокий риск lock-in.

## Что произойдёт при epsilon = 1?

Полностью случайная политика. Хорошо исследует, но почти не использует знания.

## Как считать probability выбранного действия?

Зависит от точной реализации exploration и ties. Вероятность нужно вычислять из реальной policy, а не записывать приблизительно.

## Как работать с новым оффером?

Дать controlled exploration, использовать prior или optimistic initialization, ограничить максимальный трафик до получения минимальной статистики.

## Как не исчерпать бюджет?

Eligibility проверяет остаток, pacing регулирует скорость расходования, state обновляется с низкой задержкой, при достижении лимита оффер немедленно исключается.

## Что делать при недоступности Redis?

Использовать локальный кэш последнего состояния или безопасный статический fallback, логировать деградацию и не нарушать eligibility.

## Как бороться с повторным reward event?

Idempotency key и таблица обработанных event_id, атомарное обновление.

## Как учитывать отмены?

Финализировать reward после approval window или отправлять корректирующее отрицательное событие с сохранением полной истории.

---

# 32. Пример ответа кандидата за 5 минут

> Я начну с уточнения бизнес-цели. Smart-Link может оптимизировать publisher EPC, доход сети или подтверждённые actions рекламодателя, и это разные reward. Предположу, что основная цель — confirmed publisher earnings per eligible click, а fraud rate, rejection rate, overspend и redirect latency — guardrails.
>
> Единица решения — входящий клик. Перед ML-выбором eligibility service отфильтрует офферы по гео, устройству, publisher restrictions, статусу и бюджету. Среди оставшихся кандидатов MVP использует epsilon-greedy: с вероятностью 1-epsilon выбирает максимальную оценку expected reward, с epsilon — исследует. Ties разрешаем случайно. При каждом решении обязательно логируем candidate set, selected offer, epsilon, action probability и policy version.
>
> Решение обслуживается low-latency stateless API. Конфигурация офферов хранится в основной БД и кэшируется, состояние policy — во внешнем KV store. Decision event отправляется в event log до redirect или надёжно буферизуется. Конверсии приходят позже через postback, проходят attribution, validation и fraud, после чего финальный reward асинхронно обновляет state. Обновления идемпотентны по event_id.
>
> До запуска сделаем simulator, random/greedy baselines и shadow mode. Затем запустим постепенный A/B ramp-up, учитывая maturity conversion cohorts и общий бюджет офферов. Мониторим EPC, confirmed reward, fraud, rejection, latency, fallback, traffic concentration и overspend. При сбое используем безопасный fallback из допустимых офферов.
>
> После MVP можно добавить forgetting для drift и contextual bandit по гео, устройству, publisher и времени, но только после проверки качества событий и атрибуции.

---

# 33. Пример ответа кандидата за 30–40 минут

## Шаг 1. Scope

- Smart-Link маршрутизирует только клики внутри одной заранее выбранной группы офферов.
- MVP работает в одной географии.
- Reward — confirmed payout.
- Conversion window — 7 дней.
- Traffic — условно 10 000 RPS.
- p99 redirect latency — менее 100 ms.

## Шаг 2. Functional requirements

- создать Smart-Link;
- настроить набор офферов;
- принять клик;
- выбрать eligible offer;
- перенаправить пользователя;
- принять conversion postback;
- обновить policy;
- показать отчётность;
- отключить оффер экстренно.

## Шаг 3. Non-functional requirements

- высокая доступность;
- низкая latency;
- идемпотентность;
- auditability;
- масштабирование;
- eventual consistency допустима для аналитики, но budget stop должен быть быстрым.

## Шаг 4. Data model

Обсудить decision, conversion, reward и policy state таблицы.

## Шаг 5. API

Обсудить `/decision`, `/rewards`, configuration endpoints и emergency stop.

## Шаг 6. Online path

Описать gateway → eligibility → decision → event → redirect.

## Шаг 7. Async path

Описать conversion → attribution → fraud → reward → updater.

## Шаг 8. Algorithm

Объяснить epsilon, ties, action probability, initialization и update rule.

## Шаг 9. Failure handling

Timeouts, cache, stale state, duplicate events, empty candidates, fallback.

## Шаг 10. Experiment

Control, treatment, unit, budget interference, mature cohorts, ramp-up.

## Шаг 11. Future

Contextual bandits, adaptive exploration, Bayesian methods, constrained optimization.

---

# 34. Ошибки кандидата

## Ошибка 1. Начать с нейросети

Проблема задачи не в недостатке сложности модели, а в online decision и partial feedback.

## Ошибка 2. Не спросить про reward

Тогда вся архитектура оптимизирует непонятную цель.

## Ошибка 3. Не упомянуть delayed conversion

Для CPA это фундаментальная особенность.

## Ошибка 4. Не логировать propensity

Будущую политику трудно оценивать.

## Ошибка 5. Игнорировать budget и eligibility

Сервис может отправить пользователя на недоступный или запрещённый оффер.

## Ошибка 6. Хранить state внутри одного FastAPI процесса

Не работает при масштабировании и рестартах.

## Ошибка 7. Не иметь fallback

Redirect path не может зависеть от стопроцентной доступности ML-компонента.

## Ошибка 8. Сравнивать свежие и зрелые конверсии

Получается неверный вывод.

## Ошибка 9. Считать A/B независимым при общем бюджете

Treatment влияет на control через shared inventory.

## Ошибка 10. Оптимизировать только краткосрочный payout

Можно ухудшить качество, fraud, retention и отношения с рекламодателями.

---

# 35. Оценка сложности

На интервью полезно разделить этапы.

## MVP

- один reward;
- простой epsilon-greedy;
- небольшой набор офферов;
- один регион;
- Redis state;
- асинхронный updater;
- базовый dashboard;
- ручной epsilon.

## Production v2

- delayed reward model;
- non-stationary updates;
- budget pacing;
- contextual segmentation;
- automatic rollback;
- off-policy evaluation;
- multi-region;
- fraud-aware reward.

## Production v3

- contextual bandit;
- constrained optimization;
- multi-objective policy;
- adaptive exploration;
- causal long-term value;
- advertiser/publisher equilibrium.

---

# 36. Продуктовые кейсы для тренировки

## Кейс 1. Fintech leads

Банк платит:

- 1 доллар за заявку;
- ещё 10 долларов за одобрение;
- ещё 30 долларов за выданный кредит.

Вопросы:

- какой reward выбрать;
- когда обновлять policy;
- как учесть риск;
- как не оптимизировать fake leads.

## Кейс 2. Marketplace sellers

Платформа выбирает продавца для карточки товара.

Вопросы:

- максимизировать GMV или margin;
- как учесть SLA продавца;
- как не убить новых продавцов;
- как учитывать stock.

## Кейс 3. Dating notifications

Выбрать тип push-уведомления.

Вопросы:

- reward: open, message или healthy conversation;
- как учесть fatigue;
- какие safety guardrails;
- как не стимулировать harassment.

## Кейс 4. AI model routing

Выбрать модель для запроса.

Вопросы:

- reward: качество минус стоимость и latency;
- как оценивать качество;
- как исследовать дорогие модели;
- как ограничить unsafe outputs.

## Кейс 5. iGaming bonus

Выбрать бонус.

Вопросы:

- responsible gaming;
- regulatory constraints;
- self-exclusion;
- недопустимость reward, максимизирующего вред.

---

# 37. Чек-лист перед завершением ответа

Проверьте, что вы обсудили:

- [ ] пользователя и бизнес-цель;
- [ ] единицу решения;
- [ ] arms;
- [ ] eligibility;
- [ ] reward;
- [ ] delayed feedback;
- [ ] epsilon и ties;
- [ ] exact action probability;
- [ ] logging;
- [ ] online architecture;
- [ ] idempotency;
- [ ] fallback;
- [ ] experiment;
- [ ] guardrails;
- [ ] drift;
- [ ] cold start;
- [ ] privacy и compliance;
- [ ] следующий шаг к contextual bandit.

---

# 38. Финальная формула сильного мышления

```text
Не «какую модель выбрать?»,
а:

какое решение принимается
→ для кого
→ в какой момент
→ среди каких допустимых действий
→ с какой наградой
→ через какое время приходит обратная связь
→ как решение влияет на будущие данные
→ как доказать инкрементальный эффект
→ как ограничить риск
→ как обеспечить работу при сбое.
```

Именно такой порядок превращает знание ε-greedy из учебной формулы в уровень продуктового аналитика, ML-инженера или ML System Design кандидата.

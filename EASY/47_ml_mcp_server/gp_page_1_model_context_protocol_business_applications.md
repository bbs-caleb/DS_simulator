# MCP: бизнес-применение по индустриям
## Как мыслить не инструментом, а бизнес-результатом

---

# 1. Начинать нужно не с MCP

Плохой вопрос:

```text
Где бы нам внедрить MCP?
```

Хороший вопрос:

```text
Какой пользовательский процесс сейчас медленный,
дорогой, фрагментированный или ошибочный?
```

Затем:

```text
Может ли AI помочь?
Нужен ли доступ к нескольким системам?
Нужен ли стандартный интеграционный слой?
```

MCP — средство, а не цель.

---

# 2. Универсальная бизнес-форма

```text
Пользователь:
Job to be done:
Текущий процесс:
Боль:
Данные:
Действия:
Цена ошибки:
Подтверждение:
Бизнес-метрика:
Техническая метрика:
Почему MCP:
```

Пример:

```text
Пользователь: demand planner
Job: расследовать недопрогноз
Процесс: вручную открыть 5 отчётов
Боль: 40 минут на SKU-store кейс
Данные: forecast, sales, OOS, promo, delivery
Действия: прочитать данные, сформировать RCA
Цена ошибки: OOS или overstock
Подтверждение: изменение прогноза только человеком
Метрики: WAPE, OOS, time-to-decision
Почему MCP: единый reuse-доступ к нескольким системам
```

---

# 3. Финтех и банки

## 3.1. Copilot кредитного аналитика

Данные:

- анкета;
- bureau;
- transactions;
- KYC;
- anti-fraud;
- risk models.

Tools:

- `get_customer_application`;
- `get_credit_bureau_summary`;
- `get_income_consistency`;
- `get_fraud_signals`;
- `get_model_score_explanation`;
- `create_manual_review_case`.

Resources:

- кредитная политика;
- model card;
- определения features;
- regulatory guidance.

Метрики:

- turnaround time;
- manual review rate;
- cost per application;
- approval rate при фиксированном default rate;
- analyst productivity.

LLM должна собирать факты и объяснять, но финальное регулируемое решение остаётся в deterministic risk engine/policy.

## 3.2. Anti-fraud

Agent получает device graph, IP, merchant history, velocity features и payment data.

Read tools можно автоматизировать. Заморозка операции, блокировка аккаунта и финансовая mutation требуют policy и approval.

Метрики:

- mean time to investigate;
- fraud loss;
- false positive rate;
- recovered amount;
- cases per analyst.

## 3.3. Banking support

Запрос:

```text
Почему перевод не прошёл?
```

Agent:

1. находит transfer;
2. проверяет status;
3. получает decline code;
4. читает справочник;
5. объясняет;
6. создаёт case.

Нужно маскировать реквизиты, проверять ownership и не раскрывать внутренние anti-fraud rules.

---

# 4. Marketplace

## 4.1. Seller copilot

Tools:

- sales;
- stock;
- buy-box;
- competitor price;
- listing rejection;
- ads;
- draft price change.

Метрики:

- seller activation;
- GMV;
- ad adoption;
- time to first sale;
- support contacts;
- listing quality.

Оптимизация только GMV или только цены опасна. Нужно учитывать margin, stock, elasticity, fairness и seller economics.

## 4.2. Buyer support

- найти заказ;
- объяснить задержку;
- открыть возврат;
- проверить refund;
- предложить альтернативу.

Возврат требует ownership, eligibility, amount, idempotency и confirmation.

## 4.3. Trust & Safety

Agent собирает evidence о counterfeit, duplicate sellers и policy violations. Блокировка seller должна учитывать false positives и appeals.

Метрики:

- harmful listing exposure;
- investigation time;
- appeal overturn rate;
- false suspension;
- protected GMV.

---

# 5. E-commerce и retail

## 5.1. Demand forecasting copilot

Tools:

- `get_forecast`;
- `get_sales`;
- `get_promo_calendar`;
- `get_oos`;
- `get_inventory`;
- `get_delivery_schedule`;
- `calculate_wape`;
- `explain_deviation`.

Agent должен различать:

- падение спроса;
- censored demand из-за OOS;
- promo;
- price change;
- cannibalization;
- distribution;
- delivery issue;
- data quality.

Метрики:

- WAPE;
- bias;
- OOS;
- overstock;
- inventory turnover;
- planner time saved;
- accepted recommendation rate.

Write flow:

```text
agent предлагает correction
→ planner видит before/after
→ подтверждает
→ система записывает
```

## 5.2. Replenishment assistant

Учитывает:

- on-hand;
- on-order;
- lead time;
- safety stock;
- MOQ;
- pack size;
- shelf life;
- capacity.

Если забыть pack size или shelf life, система создаст overstock/waste.

## 5.3. Category manager copilot

Объединяет DWH, ERP, promo, competitor prices, inventory и supplier data для weekly review, promo analysis, assortment и margin bridge.

---

# 6. Two-sided marketplaces

Примеры: ride-hailing, delivery, freelance, travel.

Запрос:

```text
Почему вырос ETA в зоне?
```

Agent собирает:

- demand;
- active drivers/couriers;
- weather;
- incidents;
- incentive;
- cancellation.

Метрики:

- ETA;
- fulfillment;
- cancellation;
- utilization;
- conversion;
- contribution margin.

Нельзя оптимизировать одну сторону:

```text
слишком низкая цена → riders довольны → drivers уходят → ETA растёт
```

MCP даёт данные и действия, но marketplace equilibrium остаётся продуктовой задачей.

---

# 7. iGaming и casino

Требуются responsible gaming и compliance.

## Support

- withdrawal status;
- KYC;
- wagering requirements;
- ticket;
- responsible gaming limits.

Нельзя обходить self-exclusion, подталкивать уязвимого пользователя или скрывать риски.

## Responsible gaming

Agent обнаруживает risk signals, предлагает безопасные лимиты и инициирует manual review.

Метрики:

- time to intervention;
- self-exclusion compliance;
- regulatory incidents;
- harmful behavior exposure.

## Fraud/bonus abuse

MCP соединяет device graph, payment, account history, promo engine, KYC и geolocation risk. Agent собирает evidence, но не должен произвольно конфисковывать средства.

---

# 8. Crypto

## Portfolio assistant

Read tools:

- balances;
- transactions;
- market prices;
- exposure;
- scenario simulation.

Write tools:

- sign transaction;
- withdraw;
- swap;
- bridge.

Безопасная архитектура:

```text
Agent формирует unsigned transaction
→ показывает chain, asset, amount, fee, address
→ пользователь подтверждает кошельком
→ private key не проходит через LLM
```

Seed phrase и private key никогда не передаются в prompt или elicitation form.

## Compliance

- blockchain tracing;
- sanctions screening;
- source-of-funds summary;
- case management.

---

# 9. Dating

## Safety copilot

- report history;
- duplicate accounts;
- device risk;
- moderation signals;
- safety case.

Риски:

- sensitive data;
- stalking;
- wrongful ban;
- раскрытие reporter identity;
- discrimination.

Нужны minimization, strict roles, redaction, audit и appeal.

## User assistant

Может помочь с profile, settings и safety report. Не должен массово отправлять сообщения, имитировать человека или раскрывать hidden location.

---

# 10. Anthropic и AI-platform company

Внутренние MCP-сервисы могут подключать:

- knowledge;
- code;
- incidents;
- eval dashboards;
- experiments;
- customer support;
- billing.

Ценность:

- integration создаётся один раз;
- несколько AI surfaces переиспользуют её;
- governance централизуется.

Метрики:

- integration lead time;
- reuse rate;
- tool success;
- developer adoption;
- incident rate;
- cost per task.

---

# 11. Google / Meta / Big Tech

## Engineering productivity

Tools:

- code search;
- build status;
- test failure;
- deploy history;
- incident;
- owner;
- feature flag.

Метрики:

- time to diagnosis;
- MTTR;
- review cycle;
- developer throughput.

## Ads

Read: campaign metrics, policy, budget, creatives, experiments.

Write: pause, budget change, publish creative.

Нужны spend limits, approval, policy validation, rollback и audit.

---

# 12. SpaceX / aerospace

Read-only use cases:

- engineering knowledge;
- telemetry summarization;
- anomaly investigation;
- maintenance records;
- simulation results.

Для safety-critical систем:

```text
LLM предлагает гипотезу
→ deterministic verification/simulation
→ engineer review
→ certified control system executes
```

Никакого прямого бесконтрольного управления.

---

# 13. BP / energy / industrial

Use cases:

- maintenance copilot;
- inspection reports;
- sensor anomaly;
- work order;
- spare parts;
- safety procedures;
- emissions reporting.

Всегда показывать source, version, timestamp, units и required approval.

Метрики:

- downtime;
- MTTR;
- maintenance turnaround;
- false alarms;
- safety compliance.

---

# 14. Классификация tools по риску

## Low-risk read

Публичная документация, calculator, агрегированные метрики.

## Sensitive read

PII, finance, source code, messages.

## Reversible write

Draft, tag, create non-final task.

## Consequential write

Send, publish, change price, cancel order, block account.

## Critical

Transfer funds, delete production, industrial control, reveal keys.

Чем выше риск, тем сильнее policy, confirmation, authorization и audit.

---

# 15. Метрики MCP-продукта

## Adoption

- WAU;
- eligible-user penetration;
- retention;
- repeat use.

## Task success

- end-to-end completion;
- correct tool selection;
- successful execution;
- user-confirmed success.

## Quality

- factual accuracy;
- groundedness;
- policy compliance;
- correction rate;
- escalation rate.

## Efficiency

- time saved;
- clicks saved;
- cases per employee;
- cost per task;
- latency.

## Business outcome

- revenue/conversion;
- OOS;
- default/fraud loss;
- MTTR;
- support cost.

## Safety

- unauthorized actions;
- data incidents;
- confirmation bypass;
- audit completeness.

---

# 16. ROI

```text
Annual benefit =
time saved × labor cost
+ revenue uplift
+ avoided loss
+ reduced support cost
```

```text
Annual cost =
development
+ infrastructure
+ LLM usage
+ maintenance
+ security
+ incidents
```

```text
ROI = (benefit - cost) / cost
```

Нужно учитывать цену ошибок. Экономия времени может быть уничтожена редкими дорогими ошибками.

---

# 17. Build vs Buy

## Build

Плюсы: control, custom security, domain logic, data residency.

Минусы: cost, maintenance, on-call, protocol updates.

## Third-party

Плюсы: быстро, готовая integration.

Минусы: trust, vendor risk, data exposure, SLA.

## Hybrid

Third-party для low-risk, internal servers для core data/actions, gateway и allowlist.

---

# 18. Anti-patterns

- Technology-first без JTBD.
- Demo success считают production success.
- Измеряют tool calls, а не outcome.
- Автоматизируют плохой процесс.
- Нет owner, SLA и deprecation plan.
- Сразу дают write access.
- Не считают cost и false actions.

---

# 19. Как выбрать первый use case

Оценить по 1–5:

| Критерий | Вопрос |
|---|---|
| Частота | Как часто задача возникает? |
| Боль | Сколько времени/денег теряется? |
| Интеграционность | Сколько систем нужно? |
| Проверяемость | Есть ли ground truth? |
| Риск | Насколько опасна ошибка? |
| Данные | Доступны и качественны? |
| Adoption | Пользователь готов менять workflow? |

Лучший MVP:

- частый;
- болезненный;
- read-heavy;
- проверяемый;
- низко/среднерисковый;
- с понятной метрикой.

---

# 20. Итоговое мышление

Не продавайте MCP. Продавайте:

- анализ за 2 минуты вместо 40;
- support case без переключения между 6 системами;
- incident RCA с источниками;
- снижение ручной работы planner;
- безопасный reuse-доступ AI к корпоративным capabilities.

MCP — архитектурная причина, почему такой продукт можно масштабировать.

# Smart-Link II: практический чек-лист дизайна A/B-эксперимента

Этот файл можно использовать как шаблон перед запуском реального или учебного теста.

---

# 1. Паспорт эксперимента

## Название

```text
Название:
```

## Владельцы

```text
Product owner:
Analyst:
Data scientist:
Engineer:
```

## Решение, которое будет принято

```text
Если тест успешен, мы:
Если тест неуспешен, мы:
Если результат неоднозначен, мы:
```

---

# 2. Бизнес-проблема

```text
Какая проблема существует сейчас?

Как она влияет на пользователя?

Как она влияет на выручку, прибыль, риск или стоимость?

Почему ее нужно решать сейчас?

Какова цена бездействия?
```

---

# 3. Гипотеза

Шаблон:

```text
Если мы [изменение]
для [population],
то [primary metric]
изменится минимум на [MDE],
потому что [механизм],
при этом [guardrails] не ухудшатся сильнее [граница].
```

Заполненная гипотеза:

```text

```

Проверки:

- [ ] Указано конкретное изменение.
- [ ] Указана аудитория.
- [ ] Указан механизм эффекта.
- [ ] Есть одна primary metric.
- [ ] Указан минимально полезный эффект.
- [ ] Есть защитные ограничения.

---

# 4. Population

## Eligible

```text
Кто участвует:
```

## Excluded

```text
Кто исключается:
```

## Eligibility timing

```text
Eligibility вычисляется до или после assignment?
```

В обычном дизайне eligibility должна вычисляться **до assignment**.

Проверки:

- [ ] Правила одинаковы для A и B.
- [ ] Treatment не влияет на попадание в выборку.
- [ ] Боты и внутренний трафик определяются единообразно.
- [ ] Неeligible трафик логируется отдельно.

---

# 5. Randomization

```text
Randomization unit:
Почему выбран этот уровень:
Stable identifier:
Split:
Hash/salt:
Повторное назначение возможно:
```

Проверки:

- [ ] Один объект не меняет вариант.
- [ ] В ключ включен `experiment_id`.
- [ ] Assignment не зависит от будущего результата.
- [ ] Группа доступна во всех downstream-событиях.
- [ ] Есть expected traffic ratio.
- [ ] Уровень анализа учитывает кластеризацию.

---

# 6. Варианты

## A — Control

```text
Текущая версия:
Model/config version:
Fallback:
```

## B — Treatment

```text
Новая версия:
Model/config version:
Параметры:
Fallback:
```

## Единственное различие

```text
Кроме тестируемого изменения, A и B должны быть максимально одинаковыми.
```

Проверки:

- [ ] Одинаковая атрибуция.
- [ ] Одинаковая обработка ботов.
- [ ] Одинаковые валютные курсы.
- [ ] Одинаковое конверсионное окно.
- [ ] Изменения конфигурации версионируются.

---

# 7. Метрики

## Primary metric

```text
Название:
Бизнес-смысл:
Формула:
Числитель:
Знаменатель:
Уровень агрегации:
Окно:
Источник:
```

## Secondary metrics

```text
1.
2.
3.
```

## Guardrails

```text
1.
2.
3.
```

## Diagnostic metrics

```text
1.
2.
3.
```

Проверки:

- [ ] Primary metric выбрана до запуска.
- [ ] Она отражает ценность, а не только proxy.
- [ ] Формула не допускает двусмысленности.
- [ ] Окно одинаково для A и B.
- [ ] Для guardrails заданы границы.
- [ ] Ratio-метрика определена однозначно.

---

# 8. Статистический дизайн

```text
Baseline:
MDE absolute:
MDE relative:
Alpha:
Power:
One-sided / two-sided:
Allocation:
Required sample per group:
Expected daily traffic:
Minimum calendar duration:
Maturation window:
Statistical test:
Confidence interval method:
```

Проверки:

- [ ] MDE имеет бизнес-смысл.
- [ ] Размер выборки посчитан заранее.
- [ ] Тест покрывает полный бизнес-цикл.
- [ ] Учтено окно задержанной конверсии.
- [ ] Метод анализа выбран до запуска.
- [ ] Правило остановки выбрано до запуска.
- [ ] Для кластеров учтен design effect.
- [ ] Для тяжелого хвоста предусмотрена robust-проверка.

---

# 9. Smart-Link и адаптивный алгоритм

```text
Learning online:
Initial state:
Epsilon:
Update frequency:
Feedback event:
Conversion delay:
Uses A data:
Shared budgets:
Shared inventory:
Warm-up:
Cold-start rule:
```

Проверки:

- [ ] Параметры B зафиксированы или версионируются.
- [ ] Известно, какие данные обучают B.
- [ ] Учитывается exploration cost.
- [ ] Проверено влияние budget caps.
- [ ] Проверено interference между A и B.
- [ ] Warm-up определен до просмотра результатов.
- [ ] Логируется exploration/exploitation.

---

# 10. События и данные

Обязательные поля:

- [ ] `event_id`
- [ ] `event_type`
- [ ] `event_timestamp`
- [ ] `processing_timestamp`
- [ ] `experiment_id`
- [ ] `variant`
- [ ] `assignment_id`
- [ ] `unit_id`
- [ ] `session_id`
- [ ] `request_id`
- [ ] `model_version`
- [ ] `eligibility`
- [ ] `exposure`
- [ ] `outcome`
- [ ] `revenue`
- [ ] `currency`
- [ ] `offer_id`
- [ ] `publisher/source`

Проверки:

- [ ] Есть дедупликация.
- [ ] Assignment логируется до результата.
- [ ] A и B используют одинаковую атрибуцию.
- [ ] Late events обрабатываются одинаково.
- [ ] Нет many-to-many задвоения.
- [ ] Processing time не перепутан с event time.
- [ ] Денежные значения приведены к единой валюте.
- [ ] Refund и rejection учитываются одинаково.

---

# 11. Перед запуском

- [ ] Проведены unit-тесты.
- [ ] Проведены интеграционные тесты.
- [ ] Проверен A/A.
- [ ] Проверено распределение bucket.
- [ ] Проверен expected split.
- [ ] Проверен fallback.
- [ ] Проверен feature freshness.
- [ ] Проверен rollback.
- [ ] Определены emergency stop rules.
- [ ] Зафиксирован analysis plan.
- [ ] Проверено пересечение с другими экспериментами.
- [ ] Зафиксированы owner и каналы уведомлений.

---

# 12. Мониторинг

Ежедневно:

- [ ] Traffic volume.
- [ ] SRM.
- [ ] Assignment stability.
- [ ] Exposure rate.
- [ ] Missing events.
- [ ] Duplicate events.
- [ ] Error rate.
- [ ] Latency.
- [ ] Guardrails.
- [ ] Offer distribution.
- [ ] Budget/cap status.
- [ ] Model version.
- [ ] Data delay.
- [ ] Fraud anomaly.

Важно:

```text
Мониторинг безопасности допустим.
Остановка по первому обычному p-value без sequential design недопустима.
```

---

# 13. Emergency stop

```text
Критический guardrail:
Порог:
Кто принимает решение:
Как выполняется rollback:
Что происходит с данными после остановки:
```

Примеры причин:

- критическое падение revenue;
- резкий рост fraud;
- массовые ошибки;
- нарушение compliance;
- недоступность сервиса;
- опасная latency;
- некорректный assignment.

---

# 14. Финальный анализ

## Data quality

- [ ] Размеры групп.
- [ ] SRM.
- [ ] Дозрели outcomes.
- [ ] Нет критических потерь.
- [ ] Версии корректны.
- [ ] Eligibility одинаков.
- [ ] Assignment стабилен.
- [ ] Нет необъясненного contamination.

## Primary result

```text
A:
B:
Absolute effect:
Relative effect:
Confidence interval:
P-value:
Sample size A:
Sample size B:
```

## Guardrails

```text
Метрика:
Эффект:
Допустимая граница:
Решение:
```

## Robustness

- [ ] По дням.
- [ ] По крупным сегментам.
- [ ] Без одной аномальной даты.
- [ ] Без одного доминирующего партнера.
- [ ] С учетом кластеризации.
- [ ] С заранее допустимой обработкой выбросов.
- [ ] Проверен тяжелый хвост.
- [ ] Проверена задержка конверсий.

---

# 15. Decision memo

```text
Рекомендация:
Основной эффект:
Доверительный интервал:
Бизнес-ценность:
Guardrails:
Ограничения:
Риски:
Следующее действие:
```

Возможные решения:

```text
1. Full rollout.
2. Gradual rollout.
3. Rollout на отдельный сегмент.
4. Не раскатывать.
5. Исправить данные и перезапустить.
6. Провести подтверждающий тест.
7. Изменить алгоритм.
```

---

# 16. Самопроверка

Перед тем как назвать тест успешным, ответьте:

1. Что именно было рандомизировано?
2. Один объект мог попасть в обе группы?
3. Был ли SRM?
4. Primary metric выбрана заранее?
5. MDE определена через бизнес-ценность?
6. Размер выборки рассчитан заранее?
7. Был ли peeking?
8. Дозрели ли конверсии?
9. Есть ли общий inventory?
10. Не повлиял ли B на A?
11. Не ухудшились ли guardrails?
12. Эффект практически значим?
13. Доверительный интервал достаточно узкий?
14. Решение устойчиво к разумным проверкам?
15. Можно ли воспроизвести анализ?
16. Известно ли, какая версия алгоритма работала?
17. Не было ли фильтрации после treatment?
18. Учтены ли дубли и late events?
19. Согласован ли rollout с владельцами рисков?
20. Сохранены ли выводы и новые гипотезы?

---

# 17. Заполненный мини-пример Smart-Link

```text
Название:
Smart-Link ε-greedy vs random routing

Бизнес-проблема:
Случайный роутинг отправляет часть трафика на офферы с низкой ожидаемой ценностью.

Гипотеза:
ε-greedy увеличит confirmed revenue per eligible user минимум на 3%,
не ухудшив latency p95 более чем на 20 мс и complaint rate более чем на 0.1 п.п.

Population:
Новые eligible пользователи в поддерживаемых странах.

Randomization unit:
stable_user_id

Split:
50/50

Primary:
confirmed revenue per eligible user, окно 7 дней

Secondary:
conversion rate, payout per conversion, exploration share

Guardrails:
latency, error rate, fraud, complaints, rejection, concentration

Alpha:
0.05

Power:
0.80

MDE:
+3% relative

Minimum duration:
2 полные недели + 7 дней maturation

Decision:
Rollout при практически полезном положительном эффекте,
валидном сплите и отсутствии нарушений guardrails.
```

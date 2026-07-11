# QUANTILE T-TEST — продуктовое и system design интервью

## 1. Что проверяет интервьюер

Задача про ETA позволяет проверить не только статистику.

Интервьюер хочет увидеть, умеете ли вы:

- понять бизнесовую боль;
- определить цену ошибки;
- выбрать правильный estimand;
- разделить primary и guardrail metrics;
- спроектировать эксперимент;
- проверить его целостность;
- связать offline ML с online impact;
- спроектировать production-сервис;
- сформулировать решение для бизнеса.

---

# 2. Как начать сильный ответ

Хорошая формулировка:

> Сначала уточню определение ETA-ошибки и цену ошибки в каждом направлении. Если недопрогноз дороже перепрогноза, средняя абсолютная ошибка не полностью отражает цель. Primary metric должна описывать правый хвост, например p95 положительной signed error или долю заказов с опозданием относительно обещания больше 15 минут. Среднюю signed error я оставлю guardrail-метрикой и проверю независимым двухвыборочным t-тестом.

Это сразу показывает:

- бизнесовое мышление;
- понимание асимметрии;
- понимание хвоста;
- правильную роль t-теста.

---

# 3. Уточняющие вопросы бизнесу

## Про ошибку

1. Как именно вычисляется ошибка?
2. Какой знак означает недопрогноз?
3. Используем минуты или относительную ошибку?
4. Что дороже: недопрогноз или перепрогноз?
5. Есть ли SLA-порог?

## Про продукт

1. ETA показывается до заказа или после?
2. Может ли ETA изменить сам состав заказов?
3. Как измеряются отмены?
4. Компенсации автоматические или ручные?
5. Какие пользователи наиболее чувствительны к опозданию?

## Про эксперимент

1. Единица рандомизации — пользователь, заказ, ресторан или зона?
2. Плановый сплит 50/50 или staged rollout?
3. Сколько длится эксперимент?
4. Какие сезоны и пики должны попасть в период?
5. Есть ли сетевые эффекты?

## Про систему

1. Какова SLA latency модели?
2. Что происходит при timeout?
3. Есть ли fallback?
4. Логируется ли model version?
5. Доступен ли фактический arrival time для всех заказов?

---

# 4. Дерево метрик

## Business outcome

- completed orders;
- retention;
- contribution margin;
- customer lifetime value.

## Primary metric

Одна заранее выбранная хвостовая метрика:

- p95 underprediction;
- p99 underprediction;
- late-by-15 rate;
- Expected Shortfall worst 5%.

## Secondary metrics

- MAE;
- median error;
- p90;
- calibration;
- segment metrics.

## Product guardrails

- conversion;
- cancellation;
- support contacts;
- compensation cost;
- repeat order rate;
- среднее показанное ETA.

## Technical guardrails

- p95/p99 latency;
- timeout rate;
- availability;
- fallback rate;
- feature freshness.

## Marketplace guardrails

- courier/drone utilisation;
- restaurant load;
- supply acceptance;
- delivery cost.

---

# 5. Почему t-тест здесь не primary test

T-test отвечает на вопрос о средних.

Но бизнес-гипотеза:

> новая модель лучше ведёт себя в худших случаях.

Это вопрос о хвосте.

Поэтому:

- t-test средней — guardrail;
- bootstrap/permutation/quantile regression — возможные методы для хвостовой гипотезы.

Сильная формулировка:

> Я не буду использовать t-тест среднего как доказательство улучшения p95. Это разные estimands.

---

# 6. H0 и H1 для guardrail

```text
H0: mu_A = mu_B
H1: mu_A != mu_B
```

Решение:

```text
p < alpha -> отвергаем H0
p >= alpha -> не отвергаем H0
```

Но guardrail часто лучше формулировать как non-inferiority или equivalence.

Например, бизнес допускает сдвиг средней ошибки не более чем на 0.5 минуты.

Тогда вопрос не просто «есть ли отличие», а:

> находится ли эффект внутри допустимого интервала?

Для этого можно использовать confidence interval или TOST.

Это сильное замечание на интервью.

---

# 7. Почему отсутствие значимости не доказывает равенство

Допустим:

```text
p = 0.30
```

Нельзя сказать:

> модели имеют одинаковые средние.

Можно сказать:

> данных недостаточно, чтобы отвергнуть равенство средних при выбранном alpha.

Возможные причины:

- эффекта нет;
- мало данных;
- высокий шум;
- низкая мощность;
- плохой дизайн.

---

# 8. MDE и power

До запуска нужно определить минимально значимый эффект.

Пример:

> уменьшение late-by-15 rate менее чем на 0.5 процентного пункта не окупает внедрение.

Или:

> сдвиг средней signed error больше 0.5 минуты считается неприемлемым guardrail-нарушением.

MDE нужен для:

- sample size;
- длительности;
- интерпретации;
- decision rule.

---

# 9. Unit of randomization

Если пользователь делает много заказов, рандомизация по заказу может создавать непоследовательный опыт.

Пользователь сегодня видит старую модель, завтра новую.

Часто лучше рандомизировать по user_id.

Но тогда заказы одного пользователя зависимы.

Анализ должен учитывать кластер:

- user-level aggregation;
- cluster bootstrap;
- cluster-robust inference;
- mixed model.

Фраза для интервью:

> Единица анализа должна соответствовать единице рандомизации или стандартные ошибки должны учитывать кластеризацию.

---

# 10. Sample Ratio Mismatch

До анализа метрик:

1. Проверяю число пользователей по группам.
2. Сравниваю с плановым split.
3. Проверяю assignment logging.
4. Проверяю missing outcomes.
5. Проверяю cross-over.
6. Проверяю fallback по группам.

Если план 50/50, а факт 70/30, p-value основной метрики пока нельзя интерпретировать как обычно без расследования.

---

# 11. Selection bias из-за ETA

ETA показывается до заказа.

Новая модель меняет решение пользователя оформить заказ. Следовательно, набор доставленных заказов в A и B может различаться.

Если анализировать только completed orders:

- в B могут исчезнуть сложные длинные заказы;
- хвост ошибок искусственно улучшится;
- причинный эффект модели смешается с изменением состава заказов.

Нужно определить estimand:

- эффект на всех eligible sessions;
- эффект на созданных заказах;
- эффект на доставленных заказах;
- policy effect, включающий изменение конверсии.

Для бизнеса часто важен полный policy effect.

---

# 12. Cancellations и missing outcomes

Для отменённого заказа фактическое время доставки отсутствует.

Нельзя просто удалить такие строки, если отмена зависит от ETA.

Варианты:

- отдельная cancellation metric;
- composite outcome;
- intention-to-treat analysis;
- sensitivity analysis;
- survival/time-to-event подход.

---

# 13. Interference

В delivery marketplace группы могут влиять друг на друга.

Пример:

- новая ETA меняет спрос на рестораны;
- нагрузка перераспределяется;
- фактическое время доставки меняется и для контроля.

Это interference.

Возможные дизайны:

- geo-cluster randomization;
- switchback по времени;
- zone-level experiment;
- анализ spillover.

---

# 14. Как сравнивать p95

## Bootstrap difference

Estimand:

```text
Delta = p95_B - p95_A
```

Алгоритм:

1. Сэмплировать экспериментальные единицы A с возвращением.
2. Сэмплировать B.
3. Посчитать p95 A и B.
4. Посчитать Delta.
5. Повторить, например, тысячи раз.
6. Построить confidence interval.

Если отрицательный интервал целиком ниже нуля и меньшая ошибка лучше, это поддерживает улучшение.

## Почему cluster bootstrap

Если рандомизация по пользователю, нужно пересэмплировать пользователей вместе со всеми их заказами.

---

# 15. Альтернатива: доля тяжёлых опозданий

Определяем:

```text
late = error > 15 minutes
```

Метрика:

```text
late_rate = mean(late)
```

Плюсы:

- легко объяснить;
- связано с SLA;
- проще power calculation;
- устойчивее p99.

Минусы:

- порог дискретизирует информацию;
- ошибка 16 и 60 минут становятся одинаковыми единицами late.

Можно использовать late rate вместе с Expected Shortfall.

---

# 16. Multiple testing

Плохой процесс:

1. Посмотреть p50.
2. Посмотреть p75.
3. Посмотреть p90.
4. Посмотреть p95.
5. Посмотреть p99.
6. Выбрать единственный значимый результат.

Это p-hacking.

Правильно:

- выбрать primary quantile заранее;
- ограничить число ключевых гипотез;
- использовать correction или hierarchical testing;
- остальные срезы считать диагностическими.

---

# 17. Сегменты

Критичные срезы:

- город;
- расстояние;
- день недели;
- час;
- погода;
- ресторан;
- размер заказа;
- загрузка;
- тип дрона;
- новый/старый пользователь;
- baseline ETA bucket;
- platform/version.

Сегментный анализ нужен для риска, но не должен превращаться в поиск случайной значимости.

---

# 18. Decision table

## Хвост улучшился, guardrails стабильны

Постепенный rollout.

## Хвост улучшился, conversion упала

Не раскатывать как есть. Проверить calibration trade-off.

## Хвост незначим, интервал широкий

Inconclusive. Нужны данные или более мощная метрика.

## Offline лучше, online хуже

Приоритет causal online evidence. Исследовать mismatch.

## Общий эффект хороший, критический сегмент хуже

Ограничить rollout, исправить сегмент или ввести routing.

---

# 19. ETA system design — входы

Возможные признаки:

- координаты пользователя;
- координаты ресторана;
- дистанция;
- время приготовления;
- ресторанная очередь;
- текущая позиция дрона;
- наличие свободных дронов;
- ветер;
- осадки;
- температура;
- ограничения маршрута;
- время суток;
- день недели;
- историческая скорость;
- размер заказа;
- тип упаковки.

---

# 20. Offline и online features

## Offline

- исторические агрегаты ресторана;
- среднее время маршрута;
- сезонность;
- reliability ресторана;
- статистики зоны.

## Online

- текущая очередь;
- current weather;
- availability;
- real-time traffic/air constraints;
- live drone state.

Ключевые проблемы:

- freshness;
- training-serving skew;
- missing values;
- late events;
- feature versioning.

---

# 21. Serving architecture

Типичный поток:

1. Клиент запрашивает список ресторанов.
2. Backend формирует candidate orders.
3. ETA service получает контекст.
4. Online feature store отдаёт свежие признаки.
5. Model server делает inference.
6. Calibration layer применяет корректировки.
7. Business rules ограничивают невозможные значения.
8. API возвращает ETA.
9. Prediction event логируется.
10. Позже outcome join связывает прогноз с фактом.

---

# 22. Что логировать

Обязательно:

- request_id;
- user_id;
- order_id;
- experiment_id;
- variant;
- model_version;
- feature_version;
- prediction;
- timestamp;
- inference latency;
- fallback flag;
- actual arrival;
- cancellation;
- restaurant and geo context.

Без model version и assignment анализ может быть недостоверным.

---

# 23. Fallback

Если модель недоступна:

- предыдущая стабильная модель;
- rule-based estimate;
- cached route estimate;
- conservative operational estimate.

Нужно мониторить:

- fallback rate;
- fallback quality;
- fallback by variant;
- причины timeout.

Если B чаще падает и использует fallback, эксперимент фактически тестирует смесь политик.

---

# 24. Latency budget

Модель работает в пользовательском запросе.

Нужно обсуждать:

- p50 latency;
- p95;
- p99;
- timeout;
- end-to-end budget;
- caching;
- batching;
- degradation strategy.

Средняя latency тоже может скрывать хвост, поэтому system design повторяет статистическую идею урока.

---

# 25. Monitoring

## Data

- missing rate;
- schema changes;
- drift;
- freshness;
- duplicates;
- invalid ranges.

## Model

- MAE;
- bias;
- p95/p99 error;
- late rate;
- calibration;
- segment performance.

## Service

- latency percentiles;
- availability;
- error rate;
- timeout;
- CPU/GPU;
- fallback.

## Business

- conversion;
- cancellations;
- support contacts;
- compensation cost;
- retention;
- GMV;
- margin.

---

# 26. Rollout

Безопасный процесс:

1. Offline validation.
2. Shadow mode.
3. Canary.
4. 1% traffic.
5. 5%.
6. 25%.
7. 50%.
8. 100%.

На каждом этапе:

- automated guardrails;
- rollback;
- segment monitoring;
- version tracking;
- incident ownership.

---

# 27. Типичные слабые ответы

## «Использую t-тест, потому что две группы»

Не определена гипотеза.

## «Использую Mann–Whitney, потому что данные ненормальные»

Не определён estimand.

## «p больше 0.05, модели одинаковые»

Неверная интерпретация.

## «p95 улучшился, раскатываем»

Нет guardrails и effect size.

## «Сплит 50/50 на неделю»

Нет power, seasonality и unit of randomization.

---

# 28. Сильный полный ответ

> Сначала определю ошибку как `actual - predicted`, чтобы положительный хвост означал недопрогноз. Поскольку бизнес хочет сократить тяжёлые нарушения обещания, primary metric выберу до эксперимента: например, p95 положительной ошибки или долю заказов с опозданием больше 15 минут. Для p95 оценю разницу квантилей и доверительный интервал cluster bootstrap на уровне единицы рандомизации. Среднюю signed error оставлю guardrail, чтобы модель не уменьшила хвост простым добавлением консервативного буфера ко всем ETA. Для средней двух независимых групп использую t-test согласно постановке. До анализа проверю SRM, cross-over, logging completeness, missing outcomes и соответствие unit of analysis unit of randomization. Дополнительно проверю conversion, cancellation, compensation cost, p95 latency, availability и fallback. Решение приму по заранее заданному MDE и confidence interval, после чего выполню staged rollout с rollback.

---

# 29. Короткий шаблон

1. Определить знак ошибки.
2. Оценить цену каждого направления.
3. Зафиксировать хвостовую primary metric.
4. Среднее оставить guardrail.
5. Проверить SRM.
6. Проверить unit of randomization.
7. Для средней использовать independent t-test.
8. Для квантиля использовать подход, соответствующий квантилю.
9. Смотреть effect size и interval.
10. Проверить продуктовые и технические guardrails.
11. Принять решение по заранее заданному правилу.
12. Сделать staged rollout и monitoring.

---

# 30. Главная формула мышления

```text
бизнес-риск
→ estimand
→ metric
→ experiment design
→ statistical inference
→ decision
→ rollout
→ monitoring
```

Именно эта цепочка отличает практического DS/MLE от человека, который просто знает название статистической функции.

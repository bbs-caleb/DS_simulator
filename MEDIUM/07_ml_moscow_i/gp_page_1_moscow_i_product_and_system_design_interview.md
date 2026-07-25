# MOSCOW I: продуктовое и ML System Design интервью

# 1. Что интервьюер хочет услышать

В задаче про антиспам слабый ответ звучит так:

> Я бы попробовал CatBoost, а потом BERT.

Такой ответ показывает знание названий алгоритмов, но почти ничего не говорит о продуктовом мышлении.

Сильный ответ должен показать, что кандидат умеет:

- понять бизнес-цель;
- определить стоимость ошибок;
- выбрать primary metric и guardrails;
- сформулировать acceptance criteria;
- построить дешёвый план экспериментов;
- учитывать данные и инфраструктуру;
- спроектировать безопасный rollout;
- мониторить модель после запуска;
- объяснить, что не входит в текущий scope.

---

# 2. Начинаем не с модели, а с бизнес-цели

Начать стоит так:

> Цель системы — уменьшить количество спама и нагрузку на модераторов, не нанося заметного вреда обычным участникам чата.

Эта формулировка сразу показывает, что вы понимаете баланс пользы и риска.

Далее перечислите заинтересованные стороны:

- участники чата;
- модераторы;
- служба поддержки;
- владелец сообщества;
- ML-команда;
- злоумышленники.

У каждой стороны свои интересы.

Пользователю важно не получить несправедливый бан.

Модератору важно уменьшить ручную работу.

Владельцу сообщества важно сохранить качество общения.

Спамер будет пытаться обходить систему.

---

# 3. Уточняющие вопросы на интервью

Перед проектированием сильный кандидат задаёт вопросы.

## 3.1. Что считается спамом

Нужно определить policy taxonomy:

- реклама;
- мошенничество;
- массовые сообщения;
- вредоносные ссылки;
- повторяющиеся сообщения;
- приглашения в сторонние каналы;
- продажа услуг;
- off-topic.

Без чёткой policy разные модераторы будут размечать одинаковые сообщения по-разному.

## 3.2. Какое действие принимает система

Модель может:

- только поставить score;
- отправить сообщение на review;
- скрыть сообщение;
- удалить сообщение;
- замьютить пользователя;
- временно заблокировать;
- забанить навсегда.

Стоимость False Positive сильно зависит от действия.

Ошибочная подсказка модератору и ошибочный permanent ban — совершенно разные риски.

## 3.3. Какое SLA

- решение до публикации;
- меньше 100 мс;
- меньше 1 секунды;
- можно обработать через минуту;
- допустим batch.

Это определяет ограничения на модель и архитектуру.

## 3.4. Какой объём трафика

Нужно знать:

- сообщений в день;
- пиковый QPS;
- число чатов;
- среднюю длину сообщения;
- долю спама;
- долю сообщений со ссылкой.

## 3.5. Есть ли ручная модерация

- сколько модераторов;
- какой SLA review;
- сколько сообщений они могут обработать;
- работают ли круглосуточно;
- можно ли использовать human-in-the-loop.

## 3.6. Есть ли апелляция

- можно ли восстановить сообщение;
- можно ли разбанить пользователя;
- как быстро рассматривается жалоба;
- попадает ли решение апелляции обратно в labels.

## 3.7. Какие инфраструктурные ограничения

- CPU only или есть GPU;
- ограничение по RAM;
- latency;
- стоимость inference;
- privacy;
- срок хранения сообщений;
- требования explainability.

---

# 4. Метрики

## 4.1. Primary metric

В задаче задана метрика:

\[
Recall @ Specificity > 99.5\%
\]

Она означает:

> среди threshold, при которых мы правильно оставляем более 99.5% нормальных сообщений, выбираем тот, который даёт максимально возможный Recall.

Это разумно, потому что:

- Recall отвечает за найденный спам;
- Specificity ограничивает вред обычным пользователям.

## 4.2. Guardrail metrics

Кроме основной offline-метрики нужны:

- число ошибочных удалений;
- appeal rate;
- доля восстановленных сообщений;
- moderator override rate;
- жалобы пользователей;
- latency p95/p99;
- доля сообщений на manual review;
- cost per 1000 messages;
- spam exposure time;
- retention участников;
- активность в чате.

## 4.3. Сегментные метрики

Общая метрика может скрывать провал в одном сегменте.

Нужно считать качество по:

- языку;
- длине сообщения;
- типу ссылки;
- возрасту аккаунта;
- времени суток;
- типу чата;
- типу спама;
- новым и старым пользователям;
- временным периодам.

---

# 5. Почему нужно переводить проценты в абсолютные числа

Допустим:

- 1 000 000 нормальных сообщений в месяц;
- Specificity = 99.6%;
- FPR = 0.4%.

Тогда:

\[
1{,}000{,}000 \times 0.004 = 4{,}000
\]

Даже 99.6% могут означать четыре тысячи ошибочных срабатываний в месяц.

Поэтому интервьюер ожидает вопросы:

- каков base rate;
- какой реальный трафик;
- сколько ошибок допустимо;
- какова стоимость одной ошибки;
- есть ли ручное восстановление.

---

# 6. Data design

## 6.1. Возможные источники данных

- текст сообщения;
- ссылки и домены;
- возраст аккаунта;
- история сообщений;
- частота отправки;
- время с последней смены имени;
- время с последней смены аватарки;
- жалобы;
- решения модераторов;
- membership patterns;
- device/IP signals, если политика это разрешает;
- graph features;
- поведение в нескольких чатах.

## 6.2. Labels

Источники labels:

- решение модератора;
- жалоба пользователя;
- подтверждённый бан;
- ручная разметка;
- confirmed scam campaign.

Основные риски labels:

- inconsistent policy;
- noisy labels;
- delayed labels;
- selection bias;
- moderator bias;
- feedback loop.

## 6.3. Feedback loop

Если модель сама определяет, что показывать модераторам, новые labels будут собираться только по подозрительным сообщениям.

Тогда система перестаёт видеть ошибки на сообщениях, которым дала низкий score.

Нужна случайная контрольная выборка обычного трафика для проверки False Negative.

## 6.4. Train/validation/test split

Для спама случайный split может быть опасен.

Один и тот же spam campaign может попасть и в train, и в test.

Модель запомнит шаблон и покажет завышенное качество.

Лучше использовать:

- temporal split;
- group split по campaign;
- отдельный out-of-time test;
- deduplication похожих сообщений.

---

# 7. Baseline

На интервью всегда полезно начать с baseline.

Варианты:

1. rules;
2. logistic regression;
3. gradient boosting;
4. text model.

Baseline нужен, чтобы понять:

- насколько сложная модель вообще необходима;
- сколько ценности даёт каждый следующий шаг;
- какова цена сложности;
- что делать при падении основной модели.

В нашей задаче baseline уже есть. Это хороший знак: команда не начинала с самого дорогого решения.

---

# 8. Error analysis как часть system design

Предложите создать taxonomy ошибок.

Пример:

| Категория ошибки | Количество | Доля | Возможное исправление |
|---|---:|---:|---|
| Obfuscated links | 120 | 20% | URL normalization |
| Новые рекламные шаблоны | 90 | 15% | новые labels |
| Семантический scam без ключевых слов | 80 | 13% | BERT |
| Нестабильный threshold | 70 | 12% | calibration |
| Ошибка разметки | 60 | 10% | relabeling |
| Metadata interaction | 50 | 8% | boosting |

Для каждой категории оценивают:

- impact;
- confidence;
- effort;
- risk.

Так error analysis превращается из «посмотреть ошибки» в управляемый план работ.

---

# 9. План экспериментов

## 9.1. Experiment 1: gradient boosting

Гипотеза:

> Нелинейные взаимодействия существующих признаков повысят Recall при сохранении Specificity > 99.5%.

Нужно зафиксировать:

- один и тот же split;
- один evaluation pipeline;
- одинаковый threshold-selection protocol;
- latency;
- model size;
- confidence intervals.

## 9.2. Experiment 2: feature improvements

Возможные признаки:

- URL normalization;
- domain reputation;
- message frequency;
- число повторов;
- character entropy;
- доля цифр;
- доля заглавных букв;
- необычное смешение алфавитов;
- скорость отправки сообщений;
- признаки нового аккаунта.

## 9.3. Experiment 3: calibration

Проверить:

- reliability curve;
- Platt scaling;
- isotonic regression;
- stability threshold по времени;
- разные thresholds для разных действий.

## 9.4. Experiment 4: BERT

Только если анализ показывает семантическую проблему.

Начать можно с дешёвого prototype:

- small multilingual model;
- frozen embeddings + linear classifier;
- distilled model;
- offline benchmark;
- ограниченный hyperparameter search.

---

# 10. Архитектура высокого уровня

```text
Telegram Event
      |
      v
Message Ingestion
      |
      +----------------------+
      |                      |
      v                      v
Text Preprocessing      Metadata Fetch
      |                      |
      +----------+-----------+
                 |
                 v
          Feature Builder
                 |
                 v
          Model Inference
                 |
                 v
          Threshold Policy
        /        |          \
       /         |           \
      v          v            v
 Allow       Manual Review   Block
      \          |            /
       \         |           /
        +--------+----------+
                 |
                 v
          Logging + Feedback
                 |
                 v
        Monitoring / Retraining
```

---

# 11. Компоненты архитектуры

## 11.1. Message ingestion

Получает событие из Telegram.

Нужно обеспечить:

- idempotency;
- дедупликацию;
- retry;
- правильный порядок событий;
- trace id.

## 11.2. Feature builder

Строит признаки одинаково в train и inference.

Критический риск — training-serving skew.

Например, в train URL нормализуется одним способом, а в production другим. Тогда offline-качество не воспроизводится.

## 11.3. Model service

Требования:

- низкая latency;
- versioning;
- health check;
- timeout;
- logging model version;
- graceful degradation.

## 11.4. Policy layer

Модель должна выдавать score, а не самостоятельно определять окончательное действие.

Policy layer связывает score и действие.

Пример:

```text
score < 0.50
    → allow

0.50 <= score < 0.95
    → manual review

score >= 0.95
    → hide message

score >= 0.995 AND malicious domain
    → temporary block
```

Преимущества:

- разные действия для разных уровней риска;
- проще контролировать False Positive;
- можно постепенно расширять automation;
- проще rollback;
- policy можно менять без переобучения модели.

## 11.5. Decision log

Для каждого решения сохраняются:

- message id;
- timestamp;
- model version;
- feature version;
- score;
- threshold;
- action;
- причина;
- решение модератора;
- результат апелляции.

Без этого невозможно расследовать ошибки.

---

# 12. Safe rollout

## 12.1. Offline stage

- freeze test set;
- проверить метрики;
- сделать segment analysis;
- проверить adversarial cases;
- измерить latency;
- проверить model size;
- провести load test.

## 12.2. Shadow mode

Модель работает на live traffic, но не влияет на пользователя.

Собираем:

- predictions;
- latency;
- drift;
- agreement with moderators;
- реальный base rate;
- score distribution.

## 12.3. Human-in-the-loop

Модель формирует очередь для модераторов.

Плюсы:

- снижает риск;
- собирает labels;
- помогает calibrate threshold;
- показывает реальную нагрузку.

## 12.4. Canary

Запуск на малой доле:

- 1%;
- 5%;
- 10%.

Ограничения:

- один чат;
- только high-confidence spam;
- только временное скрытие;
- быстрый rollback;
- отдельный dashboard.

## 12.5. Full rollout

Только после выполнения:

- quality criterion;
- latency requirement;
- support readiness;
- monitoring;
- rollback;
- policy approval.

---

# 13. Monitoring

## 13.1. Technical monitoring

- error rate;
- timeout;
- latency p50/p95/p99;
- CPU;
- RAM;
- throughput;
- queue lag;
- availability.

## 13.2. Data monitoring

- missing features;
- schema changes;
- text length distribution;
- language distribution;
- URL rate;
- account-age distribution;
- feature drift.

## 13.3. Model monitoring

- score distribution;
- positive rate;
- specificity estimate;
- recall estimate с delayed labels;
- calibration;
- segment performance;
- moderator override.

## 13.4. Business monitoring

- spam reports;
- user complaints;
- appeal rate;
- moderator workload;
- chat retention;
- message activity;
- время жизни спам-сообщения.

---

# 14. Retraining strategy

Спамеры адаптируются, поэтому модель нельзя считать статичной.

Нужно определить:

- retraining frequency;
- trigger-based retraining;
- label delay;
- hard negative mining;
- active learning;
- versioning;
- champion/challenger.

Пример:

- данные обновляются ежедневно;
- обычное переобучение раз в месяц;
- emergency retraining при новом campaign;
- champion/challenger comparison;
- rollback на предыдущую модель.

---

# 15. Fallback

Что происходит, если модель недоступна?

Варианты:

- rule-based baseline;
- allow all;
- manual queue;
- block only known malicious domains.

Для антиспама разумный fallback часто такой:

- разрешить сообщение;
- применить только high-precision rules;
- отправить подозрительное на review.

Полностью блокировать все сообщения при падении модели нельзя.

---

# 16. Как использовать MoSCoW на интервью

## Must Have

- чёткая spam policy;
- корректные labels;
- правильный split;
- основная метрика;
- guardrails;
- error analysis;
- безопасное действие;
- rollback;
- минимальный monitoring.

## Should Have

- gradient boosting;
- feature improvements;
- calibration;
- human-in-the-loop;
- canary;
- data quality checks.

## Could Have

- BERT;
- multimodal model;
- advanced ensemble;
- active learning;
- сложный explainability dashboard.

## Won't Have

- global rollout до выполнения критерия;
- permanent ban без апелляции;
- тяжёлая модель без доказанной необходимости;
- функции вне текущего use case.

---

# 17. Готовая структура устного ответа

## Шаг 1. Бизнес-цель

> Мы хотим уменьшить spam exposure и workload модераторов, сохранив крайне низкий уровень ошибочных блокировок обычных пользователей.

## Шаг 2. Стоимость ошибок

> Для автоматического удаления False Positive особенно дорог, поэтому Specificity является жёстким ограничением.

## Шаг 3. Метрики

> Primary metric — Recall при Specificity выше 99.5%. Дополнительно смотрим appeal rate, moderator override, latency и spam reports.

## Шаг 4. Evaluation

> Используем temporal split и out-of-time test, чтобы не переоценить качество на повторяющихся campaigns.

## Шаг 5. Error analysis

> Перед сменой модели разбираем False Negative и False Positive по типам спама, языкам, ссылкам, metadata и времени.

## Шаг 6. Дешёвая гипотеза

> Если проблема в нелинейных взаимодействиях табличных признаков, пробуем gradient boosting. Если проблема в семантике, тогда BERT.

## Шаг 7. Safe rollout

> Сначала shadow mode, затем human review или canary, потом full rollout при выполнении acceptance criteria.

## Шаг 8. Monitoring

> Отслеживаем drift, score distribution, appeals, delayed recall и новые spam campaigns.

---

# 18. Пример полного сильного ответа

> Я бы не начинал с BERT. Сначала зафиксировал бы продуктовую цель: уменьшить спам и нагрузку на модераторов, не блокируя обычных пользователей. У нас уже есть жёсткий guardrail Specificity > 99.5%, потому что False Positive означает удаление нормального сообщения. Текущая логистическая регрессия проходит guardrail, но не достигает Recall 90%.
>
> Первый обязательный шаг — error analysis. Нужно понять, какие False Negative дают недостающие 1.3 процентного пункта: новые spam campaigns, ошибки labels, нелинейные взаимодействия metadata или семантика текста. После этого я бы сделал самый дешёвый эксперимент. На уже существующих табличных признаках это gradient boosting. Он может поймать взаимодействия без перестройки всего pipeline.
>
> BERT я оставил бы как следующий вариант, если анализ покажет, что основные ошибки связаны с контекстом и перефразированием. Он не гарантирует улучшение и увеличивает latency, стоимость и сложность эксплуатации.
>
> Текущую модель я бы не запускал сразу как автоматический бан, потому что она не выполнила acceptance criterion. Однако можно запустить её в shadow mode или как помощника модератора, собрать live feedback и оценить качество на реальном трафике. После достижения целевой метрики я бы сделал canary rollout с мониторингом False Positive, appeal rate, latency и возможностью быстрого rollback.

---

# 19. Перенос мышления на другие индустрии

## Финтех

Сначала стоимость fraud loss и customer friction, затем модель.

## Marketplace

Сначала баланс buyer/seller, policy и апелляции, затем автоматизация.

## E-commerce

Сначала online KPI и guardrails, затем сложный recommender.

## Dating

Сначала safety, fairness и appeal process, затем масштабирование ban automation.

## Crypto

Сначала irreversibility, compliance и human review, затем aggressive blocking.

## Space и промышленность

Сначала fail-safe, verification и fallback, затем advanced model.

---

# 20. Главный interview takeaway

Сильный ML-кандидат не продаёт конкретный алгоритм.

Он строит цепочку:

```text
Бизнес-цель
→ стоимость ошибок
→ метрики
→ данные
→ error analysis
→ дешёвая гипотеза
→ experiment
→ safe rollout
→ monitoring
→ retraining
```

Именно поэтому в этой задаче правильный MoSCoW выглядит так:

```text
Must Have   — анализ ошибок
Should Have — градиентный бустинг
Could Have  — BERT
Won't Have  — безусловный запуск текущей модели
```

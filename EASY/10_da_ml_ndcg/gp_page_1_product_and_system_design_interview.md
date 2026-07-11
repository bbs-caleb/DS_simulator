# gp_page_1 — Продуктовое, ML и System Design интервью по задаче nDCG

# 1. Как не надо отвечать на интервью

Слабый ответ:

> Возьмём embeddings, посчитаем cosine similarity, отсортируем и будем смотреть nDCG.

Почему он слабый:

- не определён пользователь;
- не определена бизнес-цель;
- не определён объект ранжирования;
- не объяснено, откуда labels;
- не выбран `k`;
- не обсуждаются bias и cold start;
- нет online validation;
- нет архитектуры;
- нет latency и scale;
- нет мониторинга;
- нет рисков.

Сильный специалист начинает не с модели, а с постановки задачи.

---

# 2. Каркас сильного ответа

Универсальная структура:

1. Уточнить продукт и пользователя.
2. Определить бизнес-цель.
3. Определить unit of ranking.
4. Определить candidate set.
5. Сформулировать target или relevance.
6. Выбрать offline-метрики.
7. Описать данные.
8. Спроектировать baseline.
9. Спроектировать production-архитектуру.
10. Продумать online-эксперимент.
11. Назвать guardrails.
12. Описать мониторинг.
13. Обсудить риски и trade-offs.

---

# 3. Пример сильного начала ответа

> Сначала уточню, кто пользователь и что означает успешная сессия. В нашем случае студент задаёт вопрос в Telegram, а система должна вернуть несколько видео. Бизнес-цель — сократить время до полезного ответа, повысить долю решённых вопросов и снизить нагрузку на преподавателей. Unit of ranking — пара «вопрос–видео». Поскольку пользователь прежде всего видит верх выдачи и полезных видео может быть несколько, основной offline-метрикой можно взять nDCG@k, но значение k должно соответствовать интерфейсу, например k=3.

Такой ответ сразу показывает, что кандидат понимает и продукт, и ML.

---

# 4. Уточняющие вопросы интервьюеру

## О пользователе

- Кто задаёт вопрос?
- Новичок или эксперт?
- Один язык или несколько?
- Есть ли история пользователя?
- Нужен один ответ или подборка?
- Есть ли разные сегменты пользователей?

## Об интерфейсе

- Сколько видео показывается сразу?
- Есть ли пагинация?
- Можно ли раскрыть ещё результаты?
- Показываются ли title, thumbnail и snippet?
- Есть ли кнопка «не помогло»?
- Может ли пользователь задать уточнение?

## О контенте

- Сколько видео в каталоге?
- Как часто добавляются новые?
- Есть ли транскрипты?
- Есть ли теги, курсы, темы, авторы?
- Есть ли дубликаты или почти одинаковые ролики?
- Есть ли контент на разных языках?

## О качестве

- Что считается успехом?
- Клик?
- Просмотр хотя бы N секунд?
- Досмотр?
- Отсутствие повторного вопроса?
- Положительная оценка?
- Решение вопроса без преподавателя?

## Об ограничениях

- Какой latency SLA?
- Какой QPS?
- Есть ли GPU?
- Можно ли использовать LLM?
- Есть ли privacy constraints?
- Можно ли хранить текст вопросов?
- Есть ли лимит стоимости inference?

---

# 5. Формулировка бизнес-цели

Для CyberTolya:

> Максимизировать долю вопросов, для которых студент быстро находит полезное видео, при ограничениях на latency, качество, безопасность и нагрузку на поддержку.

Возможные KPI:

- successful answer rate;
- time to useful click;
- CTR@1 и CTR@3;
- completion rate;
- repeat-question rate;
- escalation rate;
- feedback score;
- teacher workload;
- retention.

Важно разделять:

- **business KPI** — реальный результат для продукта;
- **online product metric** — наблюдаемое поведение;
- **offline ML metric** — proxy для быстрой разработки.

nDCG относится к offline ML metrics.

---

# 6. Почему nDCG подходит

Сильная формулировка:

> nDCG подходит, потому что у одного вопроса может быть несколько релевантных видео, релевантность градуирована, а верхние позиции важнее нижних. Нормализация позволяет сравнивать запросы с разным количеством и уровнем релевантных кандидатов.

Но затем нужно добавить:

> Я не стал бы использовать nDCG как единственную метрику. Для retrieval я бы смотрел Recall@k, для запросов с одним точным ответом — MRR или Success@1, а для production — successful answer rate, latency, coverage и guardrails.

Это показывает зрелость.

---

# 7. Как выбрать k

`k` должен вытекать из продукта.

Примеры:

- бот отправляет 3 ссылки → `nDCG@3`;
- search page показывает 10 результатов → `nDCG@10`;
- recommender carousel показывает 20 карточек → `nDCG@20`;
- ranker получает 100 кандидатов → `Recall@100` для retrieval.

Полезно смотреть несколько точек:

- `nDCG@1`;
- `nDCG@3`;
- `nDCG@5`;
- `nDCG@10`.

Тогда видно, где именно происходит улучшение.

Пример интерпретации:

- `nDCG@10` вырос, а `nDCG@1` не изменился — модель лучше сортирует середину выдачи, но не улучшает первый результат;
- `nDCG@1` вырос, а `nDCG@10` упал — первый результат стал лучше, но общая выдача хуже;
- оба выросли — сильное улучшение;
- Recall@100 низкий — ranker не сможет исправить retrieval.

---

# 8. Как получить labels

## 8.1. Экспертная разметка

Эксперт оценивает пару вопрос–видео:

- 0 — не связано;
- 1 — слабая связь;
- 2 — частично отвечает;
- 3 — полностью отвечает.

Нужно подготовить:

- инструкцию;
- примеры на границах классов;
- overlap между разметчиками;
- gold questions;
- adjudication;
- inter-annotator agreement;
- versioning разметки.

Ключевой вопрос:

> Оцениваем тематическую похожесть или способность реально решить вопрос пользователя?

Это не одно и то же.

Видео может быть тематически близким, но слишком сложным, устаревшим или не отвечать на конкретный вопрос.

## 8.2. Поведенческие labels

Сигналы:

- impression;
- click;
- watch time;
- completion;
- like;
- dislike;
- «помогло»;
- повторный вопрос;
- переход к другому видео;
- эскалация преподавателю.

Можно создать proxy relevance, например:

- 0 — показ без клика;
- 1 — клик и быстрый возврат;
- 2 — просмотр больше минуты;
- 3 — досмотр и «помогло».

Но такая шкала требует проверки.

## 8.3. Hybrid-подход

Практичный вариант:

- экспертная разметка для стабильного evaluation set;
- поведение для масштабного обучения;
- A/B-тест для финальной проверки.

---

# 9. Position bias

Пользователь чаще кликает верхнюю позицию просто потому, что она верхняя.

Если принять сырые клики за relevance:

1. старая модель ставит объект первым;
2. он получает больше кликов;
3. новая модель считает его лучшим;
4. объект навсегда закрепляется наверху.

Это feedback loop.

Методы коррекции:

- controlled randomization;
- swap experiments;
- propensity score weighting;
- inverse propensity weighting;
- click models;
- interleaving;
- exploration policies;
- counterfactual learning to rank.

На интервью достаточно сказать:

> Я не буду считать сырые клики unbiased labels. Нужны impression logs и коррекция position bias либо экспертный evaluation set.

---

# 10. Candidate generation

Нельзя всегда дорого сравнивать вопрос со всеми документами.

## BM25

Ищет совпадения слов в title, description и transcript.

Плюсы:

- простой;
- быстрый;
- сильный baseline;
- интерпретируемый;
- хорошо работает для имён, терминов и exact match.

Минусы:

- плохо понимает перефразировки;
- не знает семантические связи;
- чувствителен к лексике.

## Dense retrieval

Вопрос и документ кодируются в embeddings.

Плюсы:

- понимает семантику;
- работает с синонимами;
- лучше для перефразировок.

Минусы:

- дороже;
- сложнее обновление;
- возможны semantic false positives;
- нужен vector index.

## Hybrid retrieval

Объединяет BM25 и dense retrieval.

Часто это сильный production-подход:

- BM25 ловит точные совпадения;
- embeddings ловят смысл;
- fusion объединяет результаты.

Методы fusion:

- weighted score;
- Reciprocal Rank Fusion;
- union + ranker;
- learned fusion.

---

# 11. Ranking

После retrieval получаем, например, top-100 кандидатов.

Ranker использует более богатые признаки:

- BM25 score;
- cosine similarity;
- title exact match;
- transcript match;
- topic/category;
- language;
- freshness;
- popularity;
- watch completion;
- content quality;
- user history;
- query intent;
- duration;
- duplicate similarity;
- author affinity.

Возможные модели:

- ручная линейная формула;
- logistic regression;
- LambdaMART;
- CatBoost ranking;
- LightGBM ranker;
- neural bi-encoder;
- cross-encoder;
- LLM reranker.

---

# 12. Baseline

Хороший baseline:

1. очистить текст;
2. индексировать title + description + transcript;
3. использовать BM25;
4. отсортировать по BM25 score;
5. оценить Recall@100 и nDCG@3.

Почему baseline обязателен:

- быстро строится;
- дешёвый;
- прозрачен;
- создаёт нижнюю планку;
- помогает доказать ценность сложной модели.

Слабый кандидат сразу предлагает LLM.

Сильный кандидат сначала спрашивает:

> Насколько далеко простой baseline находится от требуемого качества?

---

# 13. Улучшенный pipeline

Возможная последовательность:

1. Query preprocessing.
2. Language detection.
3. Spell correction.
4. Intent classification.
5. Hybrid retrieval.
6. Candidate merge.
7. Feature enrichment.
8. Lightweight ranker.
9. Cross-encoder reranking top-N.
10. Deduplication.
11. Diversity.
12. Business rules.
13. Safety filtering.
14. Top-k response.
15. Logging and feedback.

---

# 14. Высокоуровневая system design схема

```text
Telegram User
      |
      v
Bot API / Gateway
      |
      v
Query Processing Service
      |
      +--> Language Detection
      +--> Spell Correction
      +--> Intent Classification
      |
      v
Candidate Retrieval
      |
      +--> BM25 Index
      +--> Vector Index
      |
      v
Candidate Merger
      |
      v
Ranking Service
      |
      +--> Lightweight Ranker
      +--> Optional Cross-Encoder
      |
      v
Business Rules / Dedup / Safety
      |
      v
Top-k Videos
      |
      v
Response Generator
      |
      v
Telegram User
```

Offline-контур:

```text
Impression and Interaction Logs
              |
              v
         Data Warehouse
              |
              +--> Labeling
              +--> Feature Pipelines
              +--> Training
              +--> Offline Evaluation
              |
              v
         Model Registry
              |
              v
          Deployment
```

---

# 15. Компоненты production-системы

## API Gateway

- authentication;
- rate limiting;
- tracing;
- retries;
- routing;
- abuse protection.

## Query Processor

- normalization;
- language detection;
- typo correction;
- transliteration;
- entity extraction;
- intent detection.

## Search Index

- inverted index;
- vector index;
- metadata filters;
- versioning;
- update/delete support.

## Ranking Service

- online inference;
- model versioning;
- batching;
- timeout;
- fallback;
- observability.

## Feature Store

Online features:

- popularity;
- freshness;
- user preferences;
- quality score.

Offline features:

- historical aggregates;
- training features;
- long-window statistics.

Главный риск — training-serving skew.

## Model Registry

Хранит:

- model version;
- code version;
- dataset version;
- metrics;
- parameters;
- lineage;
- approval status.

## Monitoring

- latency;
- errors;
- empty results;
- score drift;
- query drift;
- online KPI;
- safety incidents.

---

# 16. Latency budget

Допустим, SLA — 300 ms.

| Этап | Бюджет |
|---|---:|
| Gateway и network | 30 ms |
| Query processing | 20 ms |
| Retrieval | 50 ms |
| Feature lookup | 30 ms |
| Ranking | 80 ms |
| Rules и serialization | 20 ms |
| Резерв | 70 ms |

Нужен fallback:

- cross-encoder timeout → lightweight ranker;
- vector index unavailable → BM25;
- feature store unavailable → default features;
- ranker unavailable → retrieval score;
- полный сбой → популярные видео по теме или human support.

На интервью это показывает production-мышление.

---

# 17. Scale

Нужно уточнить:

- DAU и MAU;
- QPS average и peak;
- размер каталога;
- длину транскриптов;
- частоту обновления;
- число языков;
- latency SLA;
- доступную инфраструктуру;
- budget на inference.

Для маленького каталога можно сравнивать запрос со всеми видео.

Для миллионов документов нужны:

- inverted index;
- ANN;
- sharding;
- replication;
- caching;
- precomputed embeddings;
- incremental indexing.

---

# 18. Обновление индекса

При добавлении видео:

1. получить metadata;
2. извлечь transcript;
3. очистить текст;
4. определить язык;
5. построить embedding;
6. записать в vector index;
7. записать в BM25 index;
8. рассчитать quality features;
9. провести проверки;
10. активировать документ.

Нужно поддерживать:

- update;
- delete;
- re-embedding;
- rollback;
- version migration;
- backfill.

---

# 19. Минимальная схема данных

## `queries`

- query_id;
- user_id;
- query_text;
- timestamp;
- language;
- session_id.

## `documents`

- video_id;
- title;
- description;
- transcript;
- duration;
- course;
- topic;
- created_at;
- quality_score.

## `impressions`

- query_id;
- video_id;
- position;
- model_version;
- retrieval_source;
- retrieval_score;
- ranker_score;
- shown_at.

## `interactions`

- query_id;
- video_id;
- click;
- watch_time;
- completion;
- like;
- feedback;
- repeat_query;
- escalation.

## `labels`

- query_id;
- video_id;
- relevance;
- annotator_id;
- label_version;
- created_at.

Критически важно логировать impressions. Без них отсутствие клика невозможно корректно интерпретировать.

---

# 20. Train/validation/test split

Для живого продукта лучше time-based split:

- train — старый период;
- validation — более свежий;
- test — самый свежий.

Почему:

- production предсказывает будущее;
- random split часто переоценивает качество;
- похожие запросы могут утечь между частями;
- новые документы и темы создают реальную сложность.

Дополнительные меры:

- group by user;
- group by normalized query;
- deduplication;
- separate new-document evaluation;
- separate tail-query evaluation;
- leakage audit.

---

# 21. Offline evaluation protocol

1. Зафиксировать evaluation set.
2. Зафиксировать candidate pool.
3. Зафиксировать labels и guideline.
4. Зафиксировать формулу nDCG.
5. Зафиксировать gain.
6. Зафиксировать `k`.
7. Зафиксировать правило для `IDCG=0`.
8. Сравнить с baseline.
9. Построить confidence interval.
10. Проверить сегменты.
11. Провести error analysis.
12. Измерить latency и cost.

Без этого сравнение моделей может быть невоспроизводимым.

---

# 22. Error analysis

Разбить ошибки по типам:

- typo;
- короткий запрос;
- длинный вопрос;
- ambiguous intent;
- mixed language;
- transliteration;
- новый термин;
- имя спикера;
- код в запросе;
- редкая тема;
- несколько интентов;
- отсутствующий контент;
- дубликаты;
- популярное, но нерелевантное видео;
- устаревшее видео;
- неверная разметка.

Для каждого типа:

1. доля трафика;
2. текущая метрика;
3. примеры;
4. предполагаемая причина;
5. стоимость исправления;
6. ожидаемый бизнес-эффект.

Это полезнее, чем просто ещё раз обучить модель.

---

# 23. Online experiment

## Гипотеза

> Hybrid retrieval и reranker повышают successful answer rate относительно BM25 baseline.

## Primary metric

- successful answer rate.

## Secondary metrics

- CTR@1;
- CTR@3;
- watch time;
- completion;
- repeat-query rate;
- feedback score;
- escalation rate.

## Guardrails

- p95 latency;
- error rate;
- complaint rate;
- zero-result rate;
- unsafe result rate;
- cost per request.

## Randomization unit

Обычно user_id, чтобы один человек не видел разные алгоритмы внутри одной сессии.

## Продолжительность

Должна покрывать недельную сезонность и нужный sample size.

---

# 24. Почему нельзя тестировать только CTR

CTR может вырасти из-за:

- clickbait title;
- misleading thumbnail;
- любопытства;
- случайного клика;
- ухудшения качества после перехода.

Поэтому нужны downstream-метрики:

- watch time;
- completion;
- satisfaction;
- repeat query;
- successful resolution.

Продуктовая логика:

> Клик — не конечная ценность. Это лишь промежуточное действие.

---

# 25. Guardrails

Даже если nDCG вырос, нельзя допускать:

- резкий рост latency;
- падение coverage;
- перекос к популярному контенту;
- исчезновение новых видео;
- ухудшение по языкам;
- unsafe content;
- unfair exposure;
- рост complaints;
- рост стоимости inference.

---

# 26. Cold start

## Новый документ

Нет кликов и истории.

Решения:

- content features;
- transcript embedding;
- editorial quality;
- exploration quota;
- category priors;
- creator priors;
- controlled boost.

## Новый пользователь

Нет истории.

Решения:

- query-only ranking;
- context;
- popularity within topic;
- onboarding preferences;
- session features.

## Новый запрос

Решения:

- semantic retrieval;
- spell correction;
- query expansion;
- LLM rewrite;
- fallback to broader topic;
- human support.

---

# 27. Diversity и дубликаты

Top-3 не должны быть тремя почти одинаковыми видео.

Подходы:

- Maximal Marginal Relevance;
- duplicate detection;
- topic coverage;
- speaker diversity;
- duration diversity;
- post-ranking constraints.

Trade-off:

- чистая relevance может немного снизиться;
- пользовательская полезность может вырасти.

Значит, diversity нужно проверять онлайн, а не считать автоматически полезной.

---

# 28. Fairness

В marketplace, HR, dating, рекламе и creator economy ranking распределяет возможности.

Нужно измерять:

- exposure by group;
- seller/creator exposure;
- equal opportunity;
- disparate impact;
- geographic fairness;
- language fairness;
- new-item exposure.

nDCG со стороны пользователя не гарантирует fairness со стороны поставщика.

Это особенно важно для two-sided marketplace.

---

# 29. Multi-objective ranking

Production-цель часто выглядит так:

\[
Score =
 w_1 \cdot Relevance +
 w_2 \cdot Quality +
 w_3 \cdot BusinessValue -
 w_4 \cdot Risk
\]

Но линейная формула не всегда достаточна.

Возможные подходы:

- constrained optimization;
- Pareto frontier;
- multi-task learning;
- post-ranking rules;
- policy optimization;
- calibration;
- separate safety model.

Главный принцип:

> Нельзя незаметно подменить пользовательскую релевантность бизнес-выгодой платформы.

---

# 30. Индустриальные кейсы

## 30.1. E-commerce

Задача: ранжировать товары по запросу.

Сигналы:

- text match;
- purchase probability;
- availability;
- delivery;
- price;
- rating;
- return rate;
- margin.

Offline:

- nDCG@10;
- Recall@100;
- coverage.

Online:

- conversion;
- GMV;
- margin;
- add-to-cart;
- returns;
- latency.

Риски:

- unavailable items;
- popular-item dominance;
- sponsored bias;
- seller fairness.

## 30.2. Финтех

Задача: ранжировать продукты банка.

Нельзя максимизировать только CTR.

Учитываются:

- eligibility;
- affordability;
- credit risk;
- expected value;
- suitability;
- regulation;
- fairness;
- explainability.

nDCG может использовать utility-label, но запуск требует compliance review.

## 30.3. Two-sided marketplace

Задача: ранжировать водителей для заказа, заказы для водителей, продавцов или исполнителей.

Конфликтующие цели:

- клиенту нужна скорость;
- исполнителю — доход;
- платформе — ликвидность;
- рынку — fairness;
- регулятору — соблюдение правил.

Одной nDCG недостаточно. Нужно учитывать matching и equilibrium effects.

## 30.4. Dating

Задача: ранжировать профили.

Полезность должна быть взаимной:

\[
P(meaningful\ match) =
P(A\ likes\ B) \cdot
P(B\ likes\ A) \cdot
P(conversation)
\]

Дополнительно:

- safety;
- harassment risk;
- fatigue;
- diversity;
- fairness.

nDCG по односторонним лайкам может оптимизировать неправильную цель.

## 30.5. iGaming / casino

Возможны ranking игр, турниров и бонусов.

Но обязательны:

- responsible gaming;
- self-exclusion;
- age controls;
- risk indicators;
- лимиты;
- regulatory constraints.

Engagement не должен быть единственной целью.

## 30.6. Crypto

Можно ранжировать новости, risk alerts, токены, транзакции.

Риски:

- manipulation;
- non-stationarity;
- survivorship bias;
- extreme volatility;
- regulatory exposure.

## 30.7. LLM и RAG

Задача: ранжировать chunks перед генерацией.

Offline:

- Recall@k;
- nDCG@k;
- answer correctness;
- faithfulness.

Pipeline:

1. query encoding;
2. retrieval;
3. reranking;
4. select top-k;
5. generation;
6. citations.

Высокий retrieval nDCG не гарантирует хороший ответ, если generator игнорирует контекст.

---

# 31. Что спросит интервьюер

## Почему nDCG, а не Precision@k?

> У нас градуированная релевантность и важен порядок внутри top-k. Precision@k обычно бинарна и не различает, стоит лучший объект первым или последним в окне.

## Почему не MRR?

> MRR фокусируется на первом релевантном результате. У нас несколько полезных видео с разным уровнем полезности, поэтому nDCG информативнее.

## Как выбрать labels?

> Для evaluation set я предпочту экспертную разметку с чёткой шкалой. Для обучения можно использовать поведение, но с коррекцией position bias.

## Почему offline nDCG может не коррелировать с бизнесом?

> Labels могут быть несовершенным proxy, а реальное поведение зависит от интерфейса, latency, trust, diversity, freshness и downstream-качества.

## Что делать при IDCG=0?

> Заранее определить контракт. В отчётности можно исключать такие запросы или отдельно считать zero-relevance coverage. В учебной функции нужно строго следовать условию.

## Что улучшать сначала — retrieval или ranker?

> Сначала проверю candidate Recall. Если релевантный документ не попадает в кандидаты, ranker его не спасёт. Если Recall высокий, а nDCG низкий, проблема в сортировке.

---

# 32. Диагностическая матрица

| Candidate Recall | nDCG | Интерпретация |
|---|---|---|
| низкий | низкий | retrieval не находит нужное |
| высокий | низкий | ranker плохо сортирует |
| высокий | высокий | pipeline хорош офлайн |
| низкий | высокий | возможно, метрика считается на смещённом candidate set |

---

# 33. Качество против latency

Cross-encoder может повысить nDCG, но быть дорогим.

Способы компромисса:

- rerank только top-20;
- distillation;
- quantization;
- batching;
- caching;
- smaller model;
- dynamic routing;
- early exit;
- hardware acceleration.

Пример:

- простой запрос → BM25 + lightweight ranker;
- сложный запрос → neural reranker;
- критический timeout → fallback.

---

# 34. Fallback strategy

Уровни fallback:

1. cross-encoder;
2. lightweight ranker;
3. hybrid retrieval score;
4. BM25 only;
5. popular videos by topic;
6. human support.

Нужно логировать:

- какой путь использован;
- почему сработал fallback;
- какая latency;
- какое качество после fallback.

---

# 35. Caching

Можно кешировать:

- частые запросы;
- query embeddings;
- retrieval results;
- document embeddings;
- online features;
- final top-k.

Риски:

- stale results;
- personalization mismatch;
- privacy;
- invalidation complexity;
- разные model versions.

---

# 36. Security и privacy

Нужно учитывать:

- персональные данные в вопросах;
- access control;
- encryption;
- log redaction;
- retention policy;
- prompt injection;
- malicious document content;
- model extraction;
- abuse;
- rate limits;
- secret management.

Если используется внешний LLM, отдельно обсуждаются:

- передача данных третьей стороне;
- data residency;
- contractual restrictions;
- latency;
- cost;
- fallback.

---

# 37. Мониторинг

## Data drift

- длина запроса;
- язык;
- topic distribution;
- typo rate;
- embedding distribution;
- share of unseen queries.

## Prediction drift

- score distribution;
- top-document concentration;
- rank changes;
- confidence;
- entropy выдачи.

## Outcome drift

- CTR;
- completion;
- feedback;
- successful answer rate;
- nDCG на свежих labels.

## System metrics

- p50/p95/p99 latency;
- QPS;
- error rate;
- timeout rate;
- cache hit rate;
- CPU/GPU utilization;
- cost per request.

---

# 38. Как рассказать про nDCG за 60 секунд

> nDCG — метрика качества ранжирования. Она учитывает не только релевантность результатов, но и их позиции: полезные элементы вверху дают больший вклад. Сначала считается DCG — дисконтированная сумма релевантностей. Затем считается IDCG для идеального порядка тех же объектов. Отношение DCG к IDCG даёт nDCG, обычно от 0 до 1. Метрика подходит, когда есть несколько релевантных объектов с разными уровнями полезности. Значение обязательно указывать вместе с глубиной, например nDCG@3. В production я бы использовал её как offline proxy и подтвердил улучшение через A/B-тест.

---

# 39. Как рассказать про систему за 3 минуты

> Пользователь задаёт вопрос, система возвращает top-3 видео. Я бы начал с бизнес-KPI: доля успешно решённых вопросов, время до полезного клика и снижение повторных обращений. В retrieval построил бы BM25 baseline по заголовкам, описаниям и транскриптам, затем hybrid retrieval с embeddings. Основная метрика retrieval — Recall@100, потому что ranker не сможет поднять документ, которого нет среди кандидатов. Для финального порядка использовал бы nDCG@3, поскольку relevance градуирована и верхние позиции важнее. Labels для test set получил бы от экспертов, а для обучения использовал бы клики, watch time и feedback с коррекцией position bias. В production сделал бы двухэтапную архитектуру: retrieval, затем lightweight ranker или cross-encoder, после чего deduplication и safety. Добавил бы fallback, мониторинг latency, zero-result rate и query drift. После offline-проверки запустил бы A/B-тест с primary metric successful answer rate и guardrails по latency, жалобам и повторным вопросам.

---

# 40. Checklist ответа на system design

Перед завершением проверьте, что упомянуты:

- пользователь;
- business objective;
- success event;
- unit of ranking;
- top-k;
- retrieval;
- ranking;
- labels;
- nDCG;
- Recall@k;
- baseline;
- data split;
- position bias;
- latency;
- scale;
- fallback;
- A/B test;
- guardrails;
- monitoring;
- fairness;
- safety;
- cold start;
- error analysis.

---

# 41. Главный вывод для интервью

Слабый кандидат говорит:

> Я знаю формулу nDCG.

Сильный кандидат показывает:

> Я понимаю, зачем бизнесу ранжирование, как получить корректные labels, как выбрать метрику, как построить retrieval и ranking pipeline, как проверить причинный эффект и какие риски остаются за пределами одной offline-метрики.

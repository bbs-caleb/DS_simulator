# GP — страница 2: HNSW на продуктовом и System Design интервью

# 1. Что от вас хотят услышать

Когда интервьюер спрашивает про HNSW, он редко ждёт пересказ статьи.

Он проверяет, умеете ли вы связать:

```text
бизнесовую проблему
→ embeddings
→ ANN retrieval
→ индекс
→ latency/quality trade-off
→ production architecture
→ эксперимент
```

Сильный кандидат не начинает с:

> Возьмём HNSW, потому что он state of the art.

Он сначала выясняет требования.

---

# 2. Первые вопросы интервьюеру

## О продукте

1. Что ищет пользователь?
2. Что является документом?
3. Что означает релевантность?
4. Это search, recommendations, RAG, matching или fraud retrieval?
5. Как измеряется бизнесовый успех?

## О масштабе

1. Сколько vectors?
2. Какая dimension?
3. Какой QPS?
4. Какой peak QPS?
5. Какой `K`?
6. Какой latency SLA?
7. Как быстро растёт база?

## Об обновлениях

1. Как часто добавляются объекты?
2. Нужно ли удаление?
3. Как быстро новое содержимое должно стать доступным?
4. Как часто меняется embedding model?

## О качестве

1. Какой Recall@K нужен?
2. Нужна ли exactness?
3. Какая цена false negative?
4. Есть ли reranker?
5. Есть ли жёсткие filters?

---

# 3. Пример требований

Допустим:

```text
100 млн документов
embedding dimension = 768
5 000 средних QPS
15 000 peak QPS
retrieval p95 < 30 ms
вернуть 500 кандидатов
index freshness < 10 минут
Recall@500 >= 0.96
```

После этого можно обосновать ANN.

> Exact scan по всей коллекции, вероятно, не уложится в latency и cost budget. Я построю benchmark, но в качестве основного кандидата рассмотрю HNSW или другой ANN-индекс.

---

# 4. High-level архитектура

```text
Client
  ↓
API Gateway
  ↓
Query Processing
  ↓
Embedding Service
  ↓
Vector Retrieval / HNSW
  ↓
Metadata Filters
  ↓
Reranker
  ↓
Business Rules / Diversity / Safety
  ↓
Response
```

Offline:

```text
Raw Documents
  ↓
Validation and Cleaning
  ↓
Embedding Batch/Stream
  ↓
Index Builder
  ↓
Offline Quality Tests
  ↓
Versioned Artifact
  ↓
Canary Deployment
```

---

# 5. Почему HNSW не должен быть финальным ranker

HNSW знает в основном embedding distance.

Он обычно не знает:

- цену;
- маржу;
- наличие;
- freshness;
- user fatigue;
- policy;
- fairness;
- сложные cross features;
- context sequence.

Поэтому роль:

```text
HNSW = high-recall candidate generator
```

А reranker оптимизирует финальную полезность.

---

# 6. Объяснение HNSW за 30 секунд

> HNSW — графовый ANN-индекс. Все vectors образуют плотный нижний proximity graph, а случайные подмножества точек образуют более разреженные верхние уровни. Поиск начинается сверху, жадно приближается к query и спускается вниз. На нижнем уровне исследуется более широкий набор кандидатов. `M` контролирует связность и память, `efConstruction` — качество построения, `efSearch` — recall-latency trade-off online.

---

# 7. Объяснение HNSW за 3 минуты

> Exact search сравнивает query со всеми N vectors и становится дорогим на большом масштабе. HNSW строит многоуровневый proximity graph. Каждая точка присутствует на layer 0, а часть точек случайно попадает на верхние уровни с экспоненциально уменьшающейся вероятностью. Верхние sparse layers позволяют быстро перемещаться между крупными областями пространства. На каждом уровне выполняется greedy search, после чего найденная вершина становится entry point для слоя ниже. На layer 0 поиск расширяется до `efSearch` кандидатов и возвращает top-K. При вставке `efConstruction` определяет ширину поиска соседей, `M` — число связей. Эвристика отбора соседей сохраняет не просто ближайшие точки, а разнообразные направления, что улучшает навигацию. Мы оцениваем Recall@K против exact ground truth вместе с p95/p99 latency, QPS, memory и build time.

---

# 8. Как объяснить M

> `M` задаёт базовую связность графа. Высокое значение обычно улучшает число альтернативных маршрутов и recall, но увеличивает память, build time и число distance computations. Низкое экономит память, но может ухудшить connectivity. Я подбирал бы его benchmark’ом, а не по универсальному default.

---

# 9. Как объяснить efConstruction

> `efConstruction` — ширина candidate search во время вставки. Чем он выше, тем больше потенциальных соседей рассматривается и тем качественнее может получиться граф, но тем дольше строится индекс. Это в основном offline trade-off.

---

# 10. Как объяснить efSearch

> `efSearch` — ширина поиска при online query. Большое значение обычно повышает Recall@K, потому что алгоритм исследует больше вершин, но увеличивает latency. Это основной runtime knob, который можно тюнить под SLA.

---

# 11. Offline benchmark

Нужно подготовить:

- репрезентативный document corpus;
- query sample;
- exact top-K ground truth;
- несколько сегментов;
- load-test environment.

Для каждой конфигурации:

```text
M
× efConstruction
× efSearch
```

измерить:

- Recall@K;
- QPS;
- p50/p95/p99;
- memory;
- build time;
- index size;
- update latency;
- filtered-search quality.

---

# 12. Почему p99 важнее среднего

Среднее время может быть 10 ms, но часть пользователей получать 500 ms.

Причины tail latency:

- неудачная область графа;
- фильтры;
- cache misses;
- noisy neighbor;
- GC;
- uneven shards;
- network fan-out;
- cold index pages.

Поэтому SLA обычно смотрит на percentile.

---

# 13. Sharding

Если индекс не помещается на одну машину, его делят.

## Random sharding

Query идёт во все shards.

Каждый shard возвращает локальный top-K.

Coordinator объединяет результаты.

Плюсы:

- простое равномерное распределение.

Минусы:

- fan-out;
- network cost;
- tail latency определяется медленным shard.

## Semantic sharding

Данные делятся по clusters.

Query router выбирает shards.

Плюсы:

- меньше fan-out.

Минусы:

- routing error снижает recall;
- imbalance;
- сложные updates.

## Business sharding

Разделение по:

- tenant;
- region;
- language;
- content type.

Полезно, если запросы естественно ограничены бизнесовым сегментом.

---

# 14. Replication

Нужна для:

- availability;
- QPS scaling;
- failover;
- rolling updates.

Проблемы:

- разные версии индекса;
- replication lag;
- удвоение/утроение memory cost;
- согласованность deletes;
- согласованность metadata.

Логируйте `index_version` для каждого ответа.

---

# 15. Updates

Стратегии:

## Full rebuild

Подходит для относительно статичных данных.

Плюсы:

- чистая структура;
- простое versioning.

Минусы:

- дорогой build;
- freshness delay.

## Incremental inserts

Плюсы:

- новые документы быстро доступны.

Минусы:

- сложнее consistency;
- возможна деградация структуры.

## Main + delta index

```text
main immutable index
+ small fresh delta index
```

Query ищет в обоих, потом объединяет результаты.

Периодически delta сливается в новый main.

---

# 16. Deletes

Physical delete из графа может быть сложным.

Варианты:

- tombstone;
- deny-list;
- metadata active flag;
- periodic rebuild.

Нужно исключать deleted content из ответа немедленно, даже если physical cleanup выполняется позже.

Особенно важно для:

- privacy deletion;
- blocked profiles;
- withdrawn products;
- revoked documents;
- access control.

---

# 17. Filters

Спросите:

- сколько фильтров;
- selectivity;
- известны ли они заранее;
- применяются ли permissions;
- можно ли разделить индекс.

Подходы:

1. Pre-filter candidate universe.
2. Integrated filtered traversal.
3. Post-filter с over-fetch.
4. Separate indices by major segment.
5. Adaptive `efSearch` при высокой selectivity.

Критическая метрика:

```text
сколько валидных кандидатов осталось после фильтра
```

---

# 18. Access control в RAG

Никогда нельзя сначала передать запрещённый chunk в LLM, а потом скрыть цитату.

Permission filtering должен происходить до попадания текста в model context.

Требования:

- tenant isolation;
- document ACL;
- user/group permissions;
- revocation propagation;
- audit logs.

ANN quality вторична по отношению к security.

---

# 19. Index versioning

Хранить:

```text
index_version
embedding_model_version
metric
normalization_version
build_dataset_snapshot
M
efConstruction
software_version
build timestamp
```

Online log:

```text
query model version
index version
efSearch
filters
returned IDs
latency
```

Без этого RCA почти невозможен.

---

# 20. Rollout

Безопасный процесс:

1. Offline validation.
2. Replay historical queries.
3. Load test.
4. Shadow traffic.
5. Compare overlap and latency.
6. Canary 1%.
7. Gradual ramp.
8. Full rollout.
9. Keep previous version for rollback.

---

# 21. Monitoring

## Infrastructure

- CPU;
- memory;
- page faults;
- disk;
- network;
- queue;
- QPS;
- errors;
- timeouts.

## Search

- p50/p95/p99;
- visited nodes;
- distance computations;
- candidate count;
- post-filter count;
- zero-result rate.

## Quality

- sampled Recall@K;
- overlap with previous version;
- clicked-result rank;
- segment metrics;
- drift.

## Index

- version;
- age;
- vector count;
- tombstone count;
- shard imbalance;
- replica lag.

---

# 22. Fallback

При сбое можно использовать:

- lexical search;
- popularity;
- cached results;
- smaller backup index;
- category defaults;
- exact search на маленьком filtered subset.

Нельзя бездумно переключаться на full exact scan большой базы — это может вызвать cascading failure.

---

# 23. Capacity planning

Оценить:

```text
vector memory
+ graph memory
+ metadata
+ runtime overhead
+ replication factor
+ headroom
```

Затем:

```text
required nodes = total memory / safe memory per node
```

Но также учитываются:

- QPS capacity;
- peak load;
- rebuild overlap;
- rolling deployment;
- failure of one node/AZ.

---

# 24. A/B test

Пример гипотезы:

> Увеличение `efSearch` повысит retrieval recall и улучшит conversion, а рост p95 останется в SLA.

Primary metric:

- conversion;
- successful search;
- answer success;
- match success.

Guardrails:

- p95/p99;
- timeout;
- infrastructure cost;
- diversity;
- complaint rate;
- safety;
- zero results.

---

# 25. Когда не нужен A/B

A/B может быть не нужен для чисто инфраструктурного изменения, если доказано:

- результаты бит-в-бит идентичны;
- latency только улучшается;
- нет изменения availability или ordering.

Но ANN-параметры обычно меняют результаты, поэтому online validation полезна.

---

# 26. Частый вопрос: HNSW или IVF

Хороший ответ:

> Я не выбирал бы абстрактно. HNSW часто даёт сильный recall-latency trade-off, но требует памяти. IVF/PQ может лучше подходить при большом масштабе и memory constraints. Я сравню их на своей размерности, распределении, filters, update pattern и hardware.

---

# 27. Частый вопрос: HNSW или vector database

Это разные уровни.

HNSW — алгоритм индекса.

Vector database — система, которая может предоставлять:

- storage;
- metadata;
- distributed execution;
- replication;
- filters;
- APIs;
- backups;
- observability;
- auth.

Vector database может внутри использовать HNSW.

---

# 28. Частый вопрос: почему не FAISS сразу

> FAISS — библиотека алгоритмов и высокопроизводительных индексов. Но production-система всё равно требует persistence, service layer, versioning, updates, filters, security, sharding, monitoring и deployment. Выбор библиотеки не заменяет system design.

---

# 29. Частый вопрос: можно ли менять efSearch на каждый запрос

Во многих реализациях — да или концептуально возможно.

Это позволяет adaptive search:

- VIP/high-value query → выше efSearch;
- строгий latency mode → ниже;
- сложный filter → выше;
- fallback retry → выше.

Но нужно контролировать:

- fairness;
- capacity;
- tail latency;
- предсказуемость SLA.

---

# 30. Частый вопрос: как понять, что проблема в embedding, а не HNSW

Диагностика:

1. Сравнить ANN с exact search на тех же embeddings.
2. Если ANN Recall высокий, но результаты нерелевантны — проблема до/после ANN.
3. Проверить human relevance exact neighbors.
4. Проверить model versions и normalization.
5. Проверить reranker и filters.

Разделение:

```text
ANN quality = насколько хорошо приближаем exact neighbors
Semantic quality = насколько exact neighbors полезны пользователю
```

---

# 31. Частый вопрос: как измерить ANN без exact поиска на миллиарде vectors

Exact ground truth можно строить:

- на sampled corpus;
- на sampled queries;
- batch GPU brute force;
- offline распределённо;
- для ограниченного benchmark snapshot.

Необязательно делать exact для каждого production query.

---

# 32. Частый вопрос: что произойдёт при увеличении dimension

Обычно:

- distance computation дороже;
- vector memory растёт;
- cache locality ухудшается;
- геометрия может стать сложнее;
- для высокого recall могут понадобиться большие `M`/`ef`.

Но результат зависит от intrinsic dimension и данных, поэтому нужен benchmark.

---

# 33. Частый вопрос: как уменьшить память

Варианты:

- float16/bfloat16 при допустимом качестве;
- scalar quantization;
- product quantization;
- dimension reduction;
- меньший `M`;
- disk-based ANN;
- tiered storage;
- sharding;
- хранение original vectors отдельно;
- rerank top-N exact vectors из другого store.

Каждый вариант требует проверки качества.

---

# 34. Частый вопрос: как бороться с local minima

- hierarchy;
- больший `efSearch`;
- больший/лучше подобранный `M`;
- качественный `efConstruction`;
- diversity heuristic;
- несколько entry candidates;
- rebuild деградировавшего индекса;
- улучшение embeddings.

---

# 35. Кейс: semantic product search

## Требование

Пользователь вводит свободный текст.

## Архитектура

```text
query
→ text encoder
→ HNSW top-1000
→ inventory/region filters
→ cross-encoder reranker
→ business rules
→ top-50
```

## Метрики

Retrieval:

- Recall@1000;
- latency;
- survivor count.

Product:

- CTR;
- add-to-cart;
- conversion;
- zero result;
- revenue quality.

## Риски

- out-of-stock;
- multilingual queries;
- stale embeddings;
- seller spam;
- category imbalance.

---

# 36. Кейс: RAG assistant

## Архитектура

```text
question
→ query rewrite
→ embedding
→ HNSW retrieval with ACL
→ hybrid lexical merge
→ reranker
→ context selection
→ LLM
```

## Метрики

- evidence Recall@K;
- groundedness;
- answer correctness;
- permission violations = 0;
- p95.

## Риски

- wrong chunking;
- stale docs;
- missing metadata;
- ACL leakage;
- incompatible embedding versions.

---

# 37. Кейс: fraud case retrieval

## Архитектура

```text
transaction/session features
→ embedding
→ similar historical cases
→ neighbour-derived features
→ risk model
→ policy engine
```

## Метрики

- fraud recall;
- false positive rate;
- loss prevented;
- approval rate;
- decision latency.

## Риски

- leakage;
- delayed labels;
- adversarial adaptation;
- stale index;
- explainability.

---

# 38. Ошибки кандидата

## Ошибка 1

> HNSW всегда O(log N).

Лучше:

> Иерархия даёт ожидаемо хорошее/логарифмически масштабируемое поведение, но проверяем эмпирически.

## Ошибка 2

> Повысим M до максимума.

Проблема: память и latency.

## Ошибка 3

> Recall@K вырос — релизим.

Проблема: нет product metrics и SLA.

## Ошибка 4

> HNSW вернёт финальную выдачу.

Проблема: нет reranker/filters.

## Ошибка 5

> Обновим query encoder без rebuild.

Проблема: несовместимые vector spaces.

## Ошибка 6

> Post-filter всегда достаточно.

Проблема: может остаться мало результатов.

---

# 39. Сильная структура ответа на 15 минут

1. Уточнить product goal.
2. Уточнить N, D, QPS, K, SLA, freshness.
3. Назвать exact baseline.
4. Обосновать ANN.
5. Объяснить HNSW.
6. Нарисовать online pipeline.
7. Нарисовать offline build.
8. Обсудить M/efConstruction/efSearch.
9. Обсудить filters и reranking.
10. Обсудить updates/deletes/versioning.
11. Обсудить sharding/replication.
12. Назвать Recall, latency, memory, build metrics.
13. Обсудить rollout, A/B и rollback.
14. Назвать риски.

---

# 40. Готовый финальный ответ

> Я начну с требований: размер коллекции, dimension, QPS, K, latency, freshness, filters и цена ошибки. Exact search будет baseline и источником ground truth. Если он не укладывается в SLA/cost, HNSW станет одним из кандидатов. HNSW хранит многоуровневый proximity graph: sparse upper layers обеспечивают крупные переходы, layer 0 — локальное уточнение. `M` управляет связностью и памятью, `efConstruction` — качеством и стоимостью построения, `efSearch` — online recall-latency trade-off. Индекс будет candidate generator, после него применятся обязательные filters и reranker. Embedding model и index версионируются совместно. Offline я сравню Recall@K, p95/p99, QPS, memory и build time, включая сегменты и filtered queries. Затем проведу shadow/canary и A/B test по продуктовой метрике с latency, safety и cost guardrails. Для production также нужны updates, deletes, replication, sharding, monitoring, fallback и rollback.

---

# 41. Чек-лист самопроверки

Перед интервью вы должны без подсказки объяснить:

- exact vs ANN;
- NSW vs HNSW;
- hierarchy;
- greedy search;
- local minimum;
- entry point;
- `M`;
- `efConstruction`;
- `efSearch`;
- neighbor diversity;
- Recall@K;
- p95/p99;
- filters;
- reranker;
- updates/deletes;
- model/index versioning;
- sharding;
- replication;
- fallback;
- A/B test.

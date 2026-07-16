# SKU Embeddings: продуктовое и System Design интервью

# 1. Что интервьюер на самом деле проверяет

Когда вас спрашивают про эмбеддинги товаров, интервьюер редко проверяет только знание формулы cosine similarity.

Обычно проверяются сразу несколько уровней мышления:

1. Понимаете ли вы бизнес-задачу.
2. Умеете ли вы уточнять смысл слова «похожий».
3. Умеете ли вы связать данные, target и loss.
4. Понимаете ли вы разницу между offline и online.
5. Можете ли вы спроектировать масштабируемую систему.
6. Знаете ли вы, как решать cold start.
7. Понимаете ли вы bias в логах.
8. Умеете ли вы выбрать метрики.
9. Умеете ли вы оценить риски запуска.
10. Можете ли вы объяснить компромиссы.

---

# 2. С чего начинать ответ

Не начинайте с архитектуры нейросети.

Начните с уточняющих вопросов.

## Правильные вопросы

- Что означает «похожий товар»?
- Нужны заменители или комплементы?
- Где будет использоваться результат?
- Какое действие пользователя является целевым?
- Какой размер каталога?
- Сколько запросов в секунду?
- Какая допустимая задержка?
- Есть ли текст и изображения?
- Есть ли история просмотров и покупок?
- Как часто появляются новые SKU?
- Нужно ли персонализировать результат?
- Какая бизнес-метрика главная?
- Есть ли ограничения по наличию, цене, региону?
- Нужно ли объяснять рекомендацию?
- Требуется ли real-time обновление?

---

# 3. Продуктовая декомпозиция

## 3.1. Пример задачи

«Постройте систему похожих товаров для маркетплейса».

Это слишком широкая постановка.

Нужно разложить на сценарии.

### Сценарий A: Similar items на карточке товара

Пользователь смотрит товар и видит альтернативы.

Цель:

- увеличить вероятность покупки;
- помочь сравнить;
- снизить уход.

### Сценарий B: Замена отсутствующего товара

Цель:

- сохранить заказ;
- снизить отмену;
- уменьшить потерю выручки.

### Сценарий C: С этим товаром покупают

Цель:

- увеличить средний чек;
- сделать покупку удобнее.

### Сценарий D: Поиск дубликатов

Цель:

- очистить каталог;
- объединить карточки;
- уменьшить фрагментацию отзывов.

### Сценарий E: Прогноз нового SKU

Цель:

- найти аналоги;
- перенести форму спроса;
- уменьшить ошибку cold start forecast.

Каждый сценарий требует разной ground truth.

---

# 4. Как сформулировать цель модели

## 4.1. Для substitutes

Positive pair:

- пользователь выбрал B, когда A отсутствовал;
- A и B взаимозаменяемы по экспертной разметке;
- переходы между A и B после сравнения;
- товар B куплен после просмотра A.

Но нужно исключить:

- комплементы;
- случайные совместные покупки;
- разные размеры;
- несовместимые модели;
- товары с другой целевой аудиторией.

## 4.2. Для complements

Positive pair:

- товары куплены в одной корзине;
- используются вместе;
- один товар добавляется после другого;
- один аксессуар совместим с основным товаром.

Нужно учитывать:

- размер корзины;
- сезонность;
- промо;
- позицию;
- рекомендательную экспозицию.

## 4.3. Для co-view

Positive pair:

- товары просмотрены в одной сессии;
- пользователь сравнивал их;
- между просмотрами небольшой интервал.

Минус:

Co-view может означать:

- похожесть;
- сравнение;
- случайную навигацию;
- влияние старой выдачи.

---

# 5. Данные

## 5.1. Основные таблицы

### `items`

```text
item_id
title
description
brand
category_id
price
seller_id
attributes
created_at
status
```

### `events`

```text
user_id
session_id
item_id
event_type
timestamp
position
request_id
device
region
```

### `orders`

```text
order_id
user_id
item_id
quantity
price
timestamp
returned
```

### `inventory`

```text
item_id
warehouse_id
available_qty
updated_at
```

### `catalog_relations`

```text
item_id
related_item_id
relation_type
source
confidence
```

## 5.2. Сессии

Сессия может завершаться после 30 минут бездействия.

Но это не универсальное правило.

Для grocery:

- пользователь может собирать корзину долго.

Для video:

- 30 минут может быть слишком много.

Для B2B:

- сессия может длиться часами.

Параметр нужно валидировать по поведению.

---

# 6. Подготовка обучающих примеров

## 6.1. Положительные пары

Пример для последовательности:

```text
A -> B -> C -> D
```

При окне 2:

```text
(A, B)
(A, C)
(B, A)
(B, C)
(B, D)
...
```

Можно задавать вес по расстоянию:

```text
weight = 1 / time_gap
```

или:

```text
weight = exp(-lambda * time_gap)
```

## 6.2. Negative sampling

### Uniform negatives

Случайный товар из каталога.

Плюс: просто.

Минус: слишком легко.

### Popularity-weighted negatives

Чаще выбираются популярные товары.

Плюс: реалистичнее.

Минус: может усилить popularity bias.

### In-batch negatives

Другие positive items в batch используются как negatives.

Плюс:

- дешево;
- эффективно.

Минус:

- возможны false negatives.

### Hard negatives

Похожие, но неправильные товары.

Плюс:

- сильный обучающий сигнал.

Минус:

- сложнее добывать;
- риск ложных отрицательных примеров.

---

# 7. Архитектура модели

## 7.1. Базовый вариант: item2vec

Аналог word2vec.

- товар = слово;
- сессия = предложение;
- соседний товар = контекст.

Плюсы:

- простота;
- быстрое обучение;
- хороший baseline.

Минусы:

- слабый cold start;
- не использует контент;
- ограниченная персонализация.

## 7.2. Two-tower

### Query tower

Вход:

- пользователь;
- текущий товар;
- история;
- контекст.

Выход:

```text
query_embedding
```

### Candidate tower

Вход:

- item_id;
- title;
- category;
- image;
- price.

Выход:

```text
item_embedding
```

Score:

\[
score(q, i) = q^T i
\]

или cosine.

Плюсы:

- item embeddings можно вычислить заранее;
- масштабируется;
- подходит для ANN.

Минусы:

- interaction между query и item ограничен dot product;
- сложные pairwise признаки идут в ranker.

## 7.3. Мультимодальный item encoder

Можно объединить:

- ID embedding;
- text embedding;
- image embedding;
- category embedding;
- numeric features.

Пример:

```text
item_vector =
MLP(
    concat(
        id_embedding,
        text_embedding,
        image_embedding,
        category_embedding,
        price_features
    )
)
```

---

# 8. Loss functions

## 8.1. Contrastive loss

Положительные пары должны быть близко.

Отрицательные — дальше margin.

Интуиция:

```text
positive -> pull together
negative -> push apart
```

## 8.2. Triplet loss

Есть:

- anchor;
- positive;
- negative.

Цель:

\[
d(anchor, positive) + margin < d(anchor, negative)
\]

Пример:

```text
anchor   = iPhone 15 case
positive = compatible case
negative = iPhone 14 case
```

## 8.3. Softmax / sampled softmax

Модель должна дать высокий score правильному товару среди множества кандидатов.

Для большого каталога полный softmax дорогой, поэтому используют sampling.

## 8.4. InfoNCE

Для batch из пар `(query, positive_item)` другие items становятся negatives.

Цель повышает score правильной пары относительно других.

---

# 9. Выбор similarity

## Dot product

Плюсы:

- очень быстрый;
- естественно работает в two-tower;
- поддерживается ANN.

Минус:

- зависит от нормы.

## Cosine similarity

Плюсы:

- сравнивает направление;
- устойчивее к масштабу.

Минус:

- теряется информация нормы.

## Euclidean distance

Плюсы:

- понятная геометрия;
- подходит для metric learning.

Минус:

- чувствительно к масштабу.

Хороший ответ на интервью:

> Я выберу similarity не отдельно, а вместе с loss, нормализацией и типом ANN-индекса, чтобы train-time score совпадал с serving-time score.

---

# 10. Offline-пайплайн

## Шаг 1. Сбор логов

Источники:

- views;
- clicks;
- cart;
- purchases;
- substitutions;
- returns;
- catalog.

## Шаг 2. Очистка

Удалить:

- ботов;
- тестовый трафик;
- дубликаты;
- аномальные сессии;
- неактивные SKU.

## Шаг 3. Построение пар

Создать:

- positives;
- negatives;
- weights.

## Шаг 4. Time split

Train:

```text
до даты T1
```

Validation:

```text
T1 - T2
```

Test:

```text
T2 - T3
```

Нельзя делать случайный split, если система работает во времени.

## Шаг 5. Обучение

Сохраняются:

- model version;
- data version;
- feature schema;
- metrics;
- config.

## Шаг 6. Экспорт item embeddings

Получаем:

```text
item_id -> vector
```

## Шаг 7. Построение ANN index

Например:

- HNSW;
- IVF;
- PQ.

## Шаг 8. Публикация

Новая версия индекса проходит:

- quality checks;
- smoke tests;
- canary;
- rollback readiness.

---

# 11. Online serving

## 11.1. Запрос

Пример:

```text
GET /similar-items?item_id=123
```

## 11.2. Получение query embedding

Варианты:

- заранее сохраненный embedding item_id;
- онлайн item encoder;
- embedding пользователя;
- комбинация user + item + context.

## 11.3. ANN retrieval

Возвращаем top-200 кандидатов.

## 11.4. Filtering

Убираем:

- исходный товар;
- out-of-stock;
- запрещенные категории;
- несовместимые варианты;
- недоступные в регионе;
- дубликаты.

## 11.5. Ranking

Учитываем:

- similarity;
- price gap;
- margin;
- availability;
- rating;
- delivery time;
- personalization.

## 11.6. Response

Возвращаем top-20.

---

# 12. Latency budget

Пример бюджета 100 мс:

```text
API gateway          5 ms
feature lookup      10 ms
query encoder       15 ms
ANN retrieval       20 ms
filters             10 ms
ranker              20 ms
network + reserve   20 ms
```

Нужно обсуждать p95 и p99, а не только среднее.

---

# 13. Масштабирование

## Каталог 1 млн SKU

При 128 float32:

```text
1_000_000 * 128 * 4
≈ 512 MB
```

Это только raw embeddings.

Плюс ANN graph, metadata, replicas.

## Каталог 100 млн SKU

Raw embeddings:

```text
100_000_000 * 128 * 4
≈ 51.2 GB
```

Понадобятся:

- sharding;
- quantization;
- compression;
- distributed ANN;
- replicas;
- tiered storage.

---

# 14. Обновление индекса

## Batch update

Например, раз в сутки.

Плюсы:

- проще;
- воспроизводимо.

Минусы:

- новые товары долго отсутствуют.

## Incremental update

Добавление новых SKU в течение дня.

Плюсы:

- свежесть.

Минусы:

- сложнее versioning;
- индекс может деградировать;
- не все ANN структуры одинаково удобны для delete/update.

## Стратегия

- полный rebuild ночью;
- incremental inserts днем;
- periodic compaction;
- atomic version switch.

---

# 15. Версионирование

Нужно хранить:

```text
model_version
embedding_version
index_version
catalog_snapshot
feature_schema_version
training_data_range
distance_metric
normalization_flag
```

Критическая ошибка:

- embeddings версии A;
- ANN index версии B;
- ranker ожидает признаки версии C.

---

# 16. Cold start

## Новый SKU с контентом

Используем:

- title;
- description;
- category;
- brand;
- image;
- attributes.

Item encoder может сразу построить embedding.

## Новый SKU без контента

Fallback:

- category centroid;
- brand centroid;
- seller prior;
- popular items;
- manual rules.

## Новый пользователь

- session-based query;
- popularity by region;
- context;
- onboarding signals.

---

# 17. Offline evaluation

## 17.1. Recall@K

Из всех релевантных товаров сколько попало в top-K.

Полезно для retrieval.

## 17.2. Precision@K

Какая доля top-K релевантна.

## 17.3. NDCG@K

Учитывает позицию и graded relevance.

## 17.4. MRR

Смотрит на позицию первого релевантного результата.

## 17.5. Coverage

Какую долю каталога система вообще умеет рекомендовать.

## 17.6. Diversity

Насколько результаты не дублируют друг друга.

## 17.7. Head/Mid/Tail slices

Обязательно оценивать отдельно:

- популярные товары;
- средние;
- редкие;
- новые.

---

# 18. Online A/B-test

## Гипотеза

Новая embedding retrieval система увеличит conversion rate карточки товара без ухудшения latency и complaint rate.

## Primary metric

Например:

- purchase conversion from similar-items block.

## Secondary metrics

- CTR;
- add-to-cart;
- revenue per session;
- margin;
- average order value.

## Guardrails

- p95 latency;
- error rate;
- out-of-stock rate;
- return rate;
- complaint rate;
- diversity;
- seller concentration.

## Рандомизация

Обычно по user_id или cookie.

Нельзя рандомизировать по request, если пользователь должен видеть стабильный опыт.

---

# 19. Почему нельзя оптимизировать только CTR

Клик может быть вызван:

- любопытством;
- плохой подписью;
- misleading thumbnail;
- слишком низкой ценой;
- отсутствием релевантности.

CTR может вырасти, а покупки упасть.

Поэтому нужно смотреть воронку:

```text
impression
-> click
-> add to cart
-> purchase
-> non-return
-> retention
```

---

# 20. Мониторинг

## Data monitoring

- число событий;
- доля missing;
- число активных SKU;
- новые категории;
- event schema;
- bot traffic.

## Embedding monitoring

- norm distribution;
- mean cosine;
- neighbor stability;
- collapse;
- hubness;
- drift;
- NaN/Inf.

## Retrieval monitoring

- recall proxy;
- latency;
- empty results;
- filter drop rate;
- index freshness.

## Business monitoring

- CTR;
- conversion;
- revenue;
- substitution success;
- complaints.

---

# 21. Инциденты

## Сценарий 1. ANN сервис недоступен

Fallback:

- cache;
- category popular;
- precomputed similar items;
- previous index;
- business rules.

## Сценарий 2. Новый индекс плохого качества

Нужен:

- canary;
- automatic rollback;
- shadow traffic;
- version switch.

## Сценарий 3. Embedding содержит NaN

Validation до публикации:

```text
no NaN
no Inf
norm > epsilon
expected dimension
item coverage threshold
```

---

# 22. Trade-offs

## Качество vs latency

Больше candidates:

- лучше recall;
- выше latency.

## Размерность vs память

Большая dimension:

- больше емкость;
- больше память;
- медленнее retrieval.

## Freshness vs стабильность

Частые обновления:

- свежие сигналы;
- выше операционный риск.

## Персонализация vs explainability

Глубокая модель:

- выше качество;
- сложнее объяснить.

## Popularity vs discovery

Популярные товары:

- безопасная конверсия;
- слабая новизна и long tail.

---

# 23. Типичный вопрос: «Почему не использовать категорию и цену?»

Хороший ответ:

Категория и цена — сильный baseline, но они не отражают:

- скрытые отношения;
- совместные покупки;
- поведение;
- стиль;
- совместимость;
- аудиторию;
- контекст.

При этом я бы обязательно сравнил embeddings с простым baseline. Сложная модель должна доказать пользу.

---

# 24. Типичный вопрос: «Как понять, что embedding хороший?»

Ответ должен быть многоуровневым.

### Геометрия

- соседи выглядят разумно;
- нет collapse;
- нет чрезмерных hubs.

### Offline

- Recall@K;
- NDCG@K;
- coverage;
- diversity.

### Slice analysis

- новые товары;
- tail;
- категории;
- регионы;
- цена.

### Online

- conversion;
- revenue;
- satisfaction;
- latency.

---

# 25. Типичный вопрос: «Как решать ложные отрицательные примеры?»

Варианты:

- исключать товары той же покупки;
- использовать soft labels;
- curated hard negatives;
- debiased contrastive loss;
- downweight uncertain negatives;
- использовать exposure logs;
- учитывать impression data;
- multi-positive training.

---

# 26. Типичный вопрос: «Что делать с изменением цены?»

Цена может быть:

- входным признаком;
- фильтром;
- reranking-признаком.

Но если embedding должен быть стабильным, динамическую цену лучше не смешивать слишком сильно с семантической частью.

Возможная схема:

```text
semantic embedding -> retrieval
current price       -> ranking/filtering
```

---

# 27. Типичный вопрос: «Нужно ли хранить embeddings в feature store?»

Возможные варианты:

- object storage для batch;
- vector database для ANN;
- key-value store для lookup;
- feature store для consistency;
- cache для hot items.

Ответ зависит от:

- latency;
- update frequency;
- volume;
- online/offline consistency.

---

# 28. Полный пример ответа на system design интервью

> Сначала я уточню, что означает похожесть. Предположим, нам нужны заменители на карточке товара и при out-of-stock. Тогда ground truth нужно строить не просто по совместным корзинам, потому что это скорее complements. Я использую переходы между товарами, substitution logs, сравнения в одной сессии, экспертные пары и совместимость по атрибутам.
>
> В качестве baseline построю правила по категории, бренду, цене и ключевым атрибутам. Затем обучу item encoder. Для cold start он будет мультимодальным: ID embedding, текст, категория, бренд и изображение. Обучение — contrastive или InfoNCE с hard negatives внутри той же категории.
>
> Item embeddings будут рассчитываться offline и сохраняться с версией. Перед публикацией я нормализую их, если serving использует cosine similarity. Далее строится ANN index, например HNSW. Важно, чтобы train-time score и serving metric совпадали.
>
> Online сервис принимает item_id, получает embedding, извлекает top-200 соседей, затем фильтрует недоступные, несовместимые и запрещенные товары. Ranker учитывает similarity, разницу цены, наличие, рейтинг, доставку и бизнес-правила.
>
> Для новых товаров embedding строится из контента сразу после ingestion, а при отсутствии данных используется category centroid. Полный индекс перестраивается ежедневно, новые SKU добавляются incrementally. Версии model, embedding и index переключаются атомарно.
>
> Offline я измеряю Recall@K, NDCG@K, coverage, diversity и качество отдельно на head, mid, tail и new SKU. Online провожу A/B-тест по пользователям. Primary metric — успешная покупка замены или conversion блока. Guardrails — latency p95/p99, complaint rate, out-of-stock recommendations, returns и seller concentration.
>
> Для надежности есть fallback на precomputed category-based alternatives, canary release, shadow evaluation и быстрый rollback.

---

# 29. Вопросы, которые могут задать дополнительно

1. Почему cosine, а не dot product?
2. Что произойдет при нормализации?
3. Как выбирать embedding dimension?
4. Как строить hard negatives?
5. Что делать с false negatives?
6. Как учитывать популярность?
7. Как убрать position bias?
8. Как оценивать новые SKU?
9. Как обрабатывать удаление товара?
10. Как часто переобучать?
11. Как обеспечить consistency между моделью и индексом?
12. Как мониторить collapse?
13. Что делать при ANN outage?
14. Как выбирать HNSW параметры?
15. Как объяснить результат бизнесу?
16. Как отличить substitutes от complements?
17. Как проверить каннибализацию?
18. Как учитывать наличие?
19. Как избежать утечки будущего?
20. Как провести A/B-тест?

---

# 30. Чек-лист сильного ответа

Сильный ответ включает:

- бизнес-сценарий;
- определение relation;
- источники данных;
- positive и negative pairs;
- baseline;
- model architecture;
- loss;
- similarity;
- cold start;
- offline evaluation;
- ANN retrieval;
- filtering;
- ranking;
- latency;
- versioning;
- update strategy;
- monitoring;
- A/B-test;
- fallback;
- риски.

Если в ответе есть только «обучим word2vec и посчитаем cosine similarity», это слишком поверхностно.

---

# 31. Финальное мышление

Главный принцип:

> Embedding — это не картинка и не набор случайных чисел. Это контракт между данными, функцией потерь, геометрией пространства и бизнес-решением.

Чтобы система была полезной, должны быть согласованы:

```text
business objective
    -> labels
    -> training pairs
    -> loss
    -> similarity
    -> ANN index
    -> ranking
    -> online metric
```

Если хотя бы одно звено не соответствует остальным, можно получить красивое пространство, которое не приносит бизнесу пользы.

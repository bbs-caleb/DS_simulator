# ML: ROTATION BUG — продуктовое и ML System Design интервью

## 1. Зачем нужен этот документ

На собеседовании слабый ответ звучит так:

> Добавим случайные повороты в обучающую выборку.

Сильный ответ показывает понимание всей системы:

- какая бизнесовая проблема решается;
- кто атакующий;
- как устроены данные;
- где проходит preprocessing;
- как проверить, что баг находится не в модели;
- какие метрики важны;
- сколько решение стоит;
- как его безопасно запустить;
- как мониторить новые обходы.

Эту структуру можно использовать для marketplace, FinTech, dating, iGaming, crypto, social media, industrial CV и других продуктов.

---

# Часть I. Как начать ответ

## 2. Переформулировать задачу

Хороший старт:

> Мы строим сервис модерации изображений. Пользователи нашли transformation-based обход: после поворота содержание для человека остаётся тем же, но решение модели меняется. Нужно повысить устойчивость системы, не увеличив ложные блокировки, latency и стоимость выше допустимых границ.

Здесь сразу есть:

- продукт;
- пользовательское поведение;
- техническая причина;
- бизнесовые ограничения.

## 3. Уточняющие вопросы

### О бизнесе

- Что считается нарушением?
- Решение автоматически блокирует или только ранжирует очередь?
- Какова цена false positive?
- Какова цена false negative?
- Есть ли апелляции?
- Есть ли ручная модерация?

### О данных

- Какие форматы изображений приходят?
- Есть ли EXIF orientation?
- Как распределены portrait, landscape и square?
- Какие углы встречаются естественно?
- Какие преобразования используют атакующие?
- Как получены метки?

### О системе

- Какой QPS?
- Какой p95/p99 latency?
- CPU или GPU?
- Обработка синхронная или асинхронная?
- Сколько изображений приходится на одну сущность?
- Каковы лимиты памяти и размера файла?

### О качестве

- Какова текущая метрика на clean set?
- Какова деградация после поворота?
- Какой допустимый FPR?
- Есть ли отдельные high-risk сегменты?
- Нужна ли калибровка вероятностей?

---

# Часть II. Product sense

## 4. Сформулировать цель через бизнес

Слабая цель:

```text
увеличить accuracy
```

Сильная цель:

```text
снизить долю успешных обходов через поворот на 50%
при false positive rate ≤ 0.5%,
p95 latency ≤ 300 ms
и росте стоимости инференса ≤ 10%
```

## 5. Участники системы

### Нарушитель

Хочет обойти модерацию с минимальным изменением изображения.

### Честный пользователь

Хочет быстро опубликовать контент без ложной блокировки.

### Модератор

Хочет видеть качественно отсортированную очередь.

### Trust & Safety

Хочет снижать риск и обеспечивать выполнение правил.

### Product manager

Смотрит на конверсию, retention, cost и complaints.

### Legal/Compliance

Смотрит на аудит, объяснимость и требования регулятора.

## 6. Cost matrix

| Реальность | Решение | Результат |
|---|---|---|
| Нарушение | Заблокировано | True Positive |
| Нарушение | Разрешено | False Negative |
| Нормальный контент | Разрешён | True Negative |
| Нормальный контент | Заблокирован | False Positive |

Цена ошибок зависит от индустрии:

- FinTech: false negative может означать fraud;
- marketplace: пропущенный контрафакт;
- dating: риск безопасности;
- creator platform: false positive может вызвать отток автора;
- iGaming: регуляторный риск.

---

# Часть III. Данные

## 7. Наборы для оценки устойчивости

### 7.1. Clean validation set

Обычные изображения без искусственных преобразований.

### 7.2. Organic rotation set

Реальные изображения, которые пользователи загрузили повёрнутыми.

### 7.3. Synthetic robustness set

Контролируемые углы, например:

```text
0°, ±2°, ±5°, ±10°, ±15°, 90°, 180°, 270°
```

Диапазон должен соответствовать продукту.

### 7.4. Attack set

Реальные обходы:

- rotate;
- mirror;
- crop;
- border;
- resize;
- compression;
- screenshot;
- text overlay;
- комбинации преобразований.

## 8. Split без leakage

Нельзя класть исходное изображение в train, а его повёрнутую копию в validation.

Все варианты одного оригинала должны иметь общий:

```text
group_id = original_image_id
```

и попадать в один split.

Для anti-fraud могут понадобиться дополнительные группировки:

- account_id;
- seller_id;
- device_id;
- household_id;
- time.

## 9. Time-based split

Атаки меняются, поэтому полезно:

```text
train: январь–апрель
validation: май
test: июнь
```

Так оценка лучше имитирует production.

## 10. Разметка

Нужно обсудить:

- кто размечает;
- сколько разметчиков на объект;
- как решаются спорные случаи;
- есть ли gold set;
- измеряется ли agreement;
- используются ли результаты апелляций.

---

# Часть IV. Диагностика

## 11. Сначала измерить деградацию

Построить таблицу:

| Угол | Recall |
|---:|---:|
| 0° | 0.93 |
| 2° | 0.91 |
| 5° | 0.84 |
| 10° | 0.70 |
| 15° | 0.52 |
| 90° | 0.31 |

Это даёт transformation curve.

## 12. Проверить preprocessing до модели

Проблема может быть не в нейросети.

Типичные причины:

- перепутаны width и height;
- неверно обработан EXIF;
- crop удаляет объект;
- resize искажает aspect ratio;
- RGB/BGR mismatch;
- неправильный dtype;
- диапазон `0–255` вместо `0–1`;
- train-serving skew;
- разные interpolation modes.

Задача `ROTATION BUG` показывает именно это: маленький bug в preprocessing может выглядеть как «слабая модель».

## 13. Unit-контракты

Проверить:

```text
output shape
output dtype
channel count
value range
angle=0 сохраняет форму
batch сохраняет порядок
```

---

# Часть V. Варианты решения

## 14. Data augmentation

Baseline:

- случайный угол в реалистичном диапазоне;
- сохранение aspect ratio;
- подходящий border mode;
- возможно, комбинация с crop/resize.

Плюсы:

- просто;
- дёшево;
- часто эффективно;
- не усложняет serving.

Минусы:

- может ухудшить clean quality;
- может создать нереалистичные примеры;
- не гарантирует устойчивость ко всем обходам.

## 15. Canonicalization

До модели привести изображение к стандартной ориентации:

- EXIF correction;
- orientation classifier;
- deskew;
- document alignment;
- text orientation detection.

Особенно полезно для OCR и KYC.

## 16. Test-time augmentation

Во время инференса применить несколько ориентаций:

```text
0°, 90°, 180°, 270°
```

и агрегировать score:

```text
mean / max / calibrated rule
```

Плюсы:

- легко проверить;
- не требует немедленного переобучения.

Минусы:

- увеличивает latency;
- увеличивает стоимость;
- меняет калибровку;
- `max` может повысить false positives.

## 17. Rotation-aware архитектуры

Более сложные варианты:

- group-equivariant CNN;
- spatial transformer;
- orientation-aware embeddings;
- contrastive learning;
- consistency regularization.

Пример функции потерь:

```text
L = L_classification + λ · distance(f(x), f(T(x)))
```

## 18. Cascade

```text
cheap model
   ↓ uncertain/high-risk
robust expensive model
   ↓
manual review
```

Так можно балансировать качество и стоимость.

---

# Часть VI. Offline evaluation

## 19. Метрики по сегментам

Нельзя смотреть только общую метрику.

Сегменты:

- clean;
- rotated;
- portrait;
- landscape;
- square;
- low resolution;
- compressed;
- screenshot;
- new users;
- high-risk users;
- категории контента.

## 20. Robustness gap

```text
robustness_gap = metric_clean - metric_transformed
```

Чем меньше разрыв, тем лучше устойчивость.

## 21. Consistency

```text
consistency = P(decision(x) == decision(T(x)))
```

Но одной consistency мало: модель может стабильно ошибаться.

Нужны:

- correctness;
- consistency.

## 22. Threshold selection

После изменения модели распределение score может поменяться.

Сравнивать лучше так:

```text
Recall при фиксированном FPR
```

а не просто на старом пороге.

## 23. Calibration

Она важна, если score используется для:

- risk routing;
- трёхуровневого решения;
- ранжирования очереди;
- динамических порогов.

---

# Часть VII. Online rollout

## 24. Shadow mode

Новая модель считает score, но не влияет на решение.

## 25. Human review comparison

Расхождения между старой и новой системой проверяют модераторы.

## 26. Canary

Запуск на малой доле трафика:

```text
1% → 5% → 20% → 50% → 100%
```

## 27. Online-метрики

- escape rate;
- appeal rate;
- upheld appeal rate;
- manual review rate;
- latency;
- cost per image;
- upload completion;
- retention;
- support tickets;
- repeated attack rate.

## 28. Delayed labels

Истина может появиться позже:

- после жалобы;
- после ручной проверки;
- после апелляции;
- после расследования.

Нужен pipeline delayed feedback.

---

# Часть VIII. Архитектура

## 29. Высокоуровневая схема

```text
Client
  ↓
Upload API
  ↓
Object Storage
  ↓
Image Validation
  ↓
EXIF Normalization
  ↓
Resize / Color Conversion
  ↓
Moderation Model
  ↓
Policy Engine
  ├─ allow
  ├─ block
  └─ manual review
  ↓
Audit Log
```

## 30. Почему policy engine отделён от модели

Модель выдаёт score. Бизнесовая политика принимает решение.

Это позволяет менять:

- thresholds;
- правила по сегментам;
- fallback;
- лимиты ручной модерации;

без переобучения модели.

## 31. Что логировать

- image hash;
- preprocessing version;
- model version;
- score;
- threshold;
- final decision;
- reason code;
- latency;
- error status.

Без versioning инцидент невозможно воспроизвести.

---

# Часть IX. Reliability

## 32. Fail-open, fail-closed, fail-to-review

### Fail-open

При сбое разрешить контент.

### Fail-closed

При сбое блокировать.

### Fail-to-review

При сбое отправить человеку.

Выбор зависит от цены риска.

## 33. Idempotency

Повторная обработка одного изображения не должна создавать конфликтующие решения.

Полезный ключ:

```text
image_id + preprocessing_version + model_version
```

## 34. Caching

Можно использовать:

- cryptographic hash для точных повторов;
- perceptual hash для похожих изображений.

Но perceptual hash тоже нужно проверять на повороты.

---

# Часть X. Monitoring

## 35. Технические метрики

- QPS;
- error rate;
- p50/p95/p99 latency;
- queue depth;
- CPU/GPU;
- memory;
- decode failures;
- unexpected shapes.

## 36. Data monitoring

- aspect ratio;
- resolution;
- EXIF orientation;
- file format;
- brightness;
- compression;
- rotated-looking share.

## 37. Model monitoring

- score distribution;
- prediction rate;
- uncertainty;
- drift;
- delayed precision/recall;
- robustness gap;
- segment performance.

## 38. Abuse monitoring

- резкий рост углов `3–7°`;
- повторные изображения с разными преобразованиями;
- кластеры аккаунтов;
- близкие embeddings;
- новые комбинации атак.

---

# Часть XI. Частые вопросы интервьюера

## 39. Почему не повернуть всё в четыре стороны?

> Это возможный baseline, но четыре инференса почти пропорционально увеличивают latency и стоимость. Сначала я проверю EXIF normalization, preprocessing bugs и обучающую аугментацию. TTA можно оставить для high-risk или uncertain трафика.

## 40. Почему не использовать только случайные повороты?

> Аугментация помогает, но не гарантирует coverage реальных атак. Нужен отдельный attack set, метрики по углам и проверка сохранения метки. Также важно исключить train-serving skew.

## 41. Что важнее: recall или precision?

> Зависит от решения. Для автоматической блокировки обычно нужен высокий precision. Для ранжирования ручной очереди можно сильнее оптимизировать recall при ограничении нагрузки на модераторов.

## 42. Как понять, что проблема не в модели?

> Начну с unit- и integration-тестов preprocessing: shape, dtype, channels, EXIF, resize и identity-преобразования. Затем сравню tensors до модели и построю controlled robustness set.

## 43. Как избежать leakage?

> Все варианты одного оригинала должны быть в одном split. Для антифрода дополнительно группирую по account/device и использую time-based holdout.

## 44. Как запускать новую версию?

> Shadow mode, ручная проверка расхождений, canary, постепенный rollout. Guardrails: appeals, false blocks, manual load, latency и cost.

---

# Часть XII. Короткий ответ на 5–7 минут

## 45. Шаблон

1. **Problem:** поворот позволяет обходить модерацию.
2. **Objective:** снизить escape rate при ограничении FPR, latency и cost.
3. **Diagnose:** проверить preprocessing, EXIF, shape и train-serving consistency.
4. **Data:** clean, organic, synthetic и real attack sets.
5. **Split:** группировать по original image и времени.
6. **Baseline:** исправить pipeline и добавить realistic rotation augmentation.
7. **Advanced:** canonicalization, TTA, consistency learning, cascade.
8. **Evaluation:** recall at fixed FPR, robustness gap, segment metrics.
9. **Deployment:** shadow → canary → gradual rollout.
10. **Monitoring:** data drift, attack patterns, appeals, latency, manual load.

---

# Часть XIII. Как связать учебный тест с большой системой

## 46. Главный инженерный вывод

Система может содержать:

- миллионы параметров;
- GPU;
- Kafka;
- object storage;
- сложный monitoring;
- ручную модерацию.

Но одна строка:

```python
width, height, channels = image.shape
```

может передавать модели некорректное изображение.

Сильная формулировка на интервью:

> Я не стал бы начинать с усложнения модели, пока не зафиксировал контракты preprocessing. Для rotation utility я добавлю unit-тест на прямоугольном изображении при угле 0°, который проверяет сохранение shape. Это дешёвая защита от regression и train-serving bugs.

## 47. Пример финального ответа

> Я сначала разделю проблему на preprocessing bug и model robustness. Проверю NumPy shape `(height, width, channels)`, требования OpenCV к `dsize=(width, height)`, EXIF orientation и соответствие train/serving pipeline. Зафиксирую контракт unit-тестом на прямоугольном изображении и угле 0°, потому что он изолирует ошибку размеров. Затем соберу clean, organic и attack sets, причём все трансформации одного оригинала будут находиться в одном split. Базовым решением будет корректный preprocessing и реалистичная rotation augmentation. Оценивать буду recall атак при фиксированном FPR, robustness gap, latency и стоимость. Новую версию запущу сначала в shadow mode, затем canary, контролируя appeals, manual review rate и escape rate. Для high-risk случаев при необходимости добавлю TTA или robust cascade.

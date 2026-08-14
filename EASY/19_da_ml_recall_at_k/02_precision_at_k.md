# Precision@K — объяснение с нуля

## 1. Главная идея

Recall спрашивает:

> Сколько из всего релевантного мы нашли?

Precision задаёт другой вопрос:

> Из того, что мы показали в Top-K, сколько действительно релевантно?

Для поисковой выдачи это очень естественно. Пользователь видит ограниченное число результатов: 5, 10, 20 карточек. Если большая часть Top-K нерелевантна, выдача ощущается плохой.

---

## 2. Базовые данные

```python
labels = [1, 0, 1, 0, 1]
scores = [0.90, 0.80, 0.20, 0.70, 0.60]
k = 3
```

Смысл:

```text
label = 1 -> релевантно / исторически был клик
label = 0 -> нерелевантно
score -> оценка релевантности новой модели
```

Сортируем по score:

| rank | label | score |
|---:|---:|---:|
| 1 | 1 | 0.90 |
| 2 | 0 | 0.80 |
| 3 | 0 | 0.70 |
| 4 | 1 | 0.60 |
| 5 | 1 | 0.20 |

Top-3:

```text
[1, 0, 0]
```

Один relevant из трёх.

\[
Precision@3 = 1/3
\]

---

## 3. Обычный Precision

В бинарной классификации:

\[
Precision = TP/(TP+FP)
\]

Где:

- `TP` — predicted positive, который действительно positive;
- `FP` — predicted positive, который на самом деле negative.

Precision отвечает:

> Когда модель что-то выбирает как positive, насколько часто она права?

---

## 4. Precision@K

В ranking-задаче удобно объявить:

```text
Top-K -> predicted positive
всё ниже Top-K -> predicted negative
```

Тогда:

\[
Precision@K = TP@K/(TP@K+FP@K)
\]

Если Top-K содержит ровно K объектов:

\[
Precision@K =
\frac{relevant\ в\ Top-K}{K}
\]

---

## 5. Интуиция

Самая короткая формулировка:

> **Precision@K = чистота Top-K.**

Пример:

```text
K = 20
в Top-20 relevant = 12
```

\[
Precision@20 = 12/20 = 0.6
\]

То есть 60% показанных результатов релевантны.

---

## 6. Ручной пример

```python
labels = [1, 1, 0, 0, 1, 0]
scores = [0.95, 0.80, 0.99, 0.10, 0.75, 0.60]
k = 4
```

После сортировки:

```text
0.99 -> 0
0.95 -> 1
0.80 -> 1
0.75 -> 1
0.60 -> 0
0.10 -> 0
```

Top-4:

```text
[0, 1, 1, 1]
```

Три relevant из четырёх:

\[
Precision@4 = 3/4 = 0.75
\]

---

## 7. Precision vs Recall на одном примере

Пусть:

```text
Всего relevant = 20
K = 5
В Top-5 relevant = 4
```

Precision:

\[
4/5 = 0.8
\]

Recall:

\[
4/20 = 0.2
\]

Интерпретация:

```text
Top-5 очень чистый: 80% результатов хорошие.
Но мы нашли лишь 20% всего релевантного.
```

Это не противоречие: знаменатели у метрик разные.

---

## 8. Как реализовать

```python
from typing import List


def precision_at_k(labels: List[int], scores: List[float], k=5) -> float:
    ranked_indices = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True,
    )

    top_k_indices = ranked_indices[:k]

    if not top_k_indices:
        return 0.0

    true_positives = sum(labels[i] for i in top_k_indices)

    return true_positives / len(top_k_indices)
```

---

## 9. Почему `len(top_k_indices)`, а не всегда `k`

Если:

```text
n = 3
k = 5
```

фактически доступно только 3 результата.

В одной распространённой конвенции:

```text
Precision = relevant / фактический размер top
```

то есть знаменатель 3.

Но в некоторых benchmark-протоколах Precision@K строго делят на K, даже если список короче K.

Поэтому в реальном проекте нужно знать контракт метрики. В учебной задаче обычно входные данные подобраны так, чтобы неоднозначность не мешала, либо тесты явно фиксируют ожидаемое поведение.

---

## 10. Вариант через zip

```python
def precision_at_k(labels, scores, k=5):
    ranked = sorted(
        zip(scores, labels),
        key=lambda pair: pair[0],
        reverse=True,
    )

    top_k = ranked[:k]

    if not top_k:
        return 0.0

    relevant = sum(label for _, label in top_k)

    return relevant / len(top_k)
```

---

## 11. Почему Precision@K не обязан уменьшаться с K

Частая ошибка:

> Чем больше K, тем Precision всегда меньше.

Нет.

Пример:

```text
Top-2: R, N
Precision@2 = 1/2 = 0.5
```

Если третий объект relevant:

```text
Top-3: R, N, R
Precision@3 = 2/3 ≈ 0.667
```

Precision вырос.

Он может:

- расти;
- падать;
- оставаться тем же.

В отличие от Recall@K, у Precision@K нет обязательной монотонности.

---

## 12. Precision@K = 1

Это означает:

> Все результаты в Top-K релевантны.

Но это **не означает**, что найдены все relevant.

Например:

```text
Всего relevant = 100
K = 5
Top-5 содержит 5 relevant
```

Precision@5:

```text
1.0
```

Recall@5:

```text
0.05
```

То есть выдача идеальна по чистоте, но охват всего 5%.

---

## 13. Precision@K = 0

Это означает:

```text
в Top-K нет ни одного actual positive
```

То есть `TP=0`.

Если K > 0:

\[
Precision@K = 0
\]

---

## 14. Что если positive вообще нет

Например:

```python
labels = [0, 0, 0, 0]
```

Если K > 0, любой Top-K содержит только negatives:

```text
TP = 0
FP = K
```

Precision = 0.

В отличие от Recall, здесь denominator обычно не нулевой, пока выбран хотя бы один объект.

---

## 15. Что если K=0

Top-0 пустой:

```text
TP = 0
FP = 0
```

Формально denominator равен нулю.

Нужна договорённость:

- вернуть 0.0;
- запретить K <= 0;
- вернуть NaN.

Для production лучше определить контракт явно.

---

## 16. Почему threshold 0.5 здесь не нужен

В классификации можно делать:

```python
pred = score >= 0.5
```

Но `Precision@K` задаёт predicted positives иначе:

```text
берём ровно K самых больших scores
```

Именно это соответствует выдаче ограниченного размера.

---

## 17. Ограничение Precision@K

Precision@K не учитывает порядок внутри Top-K.

Два ranking-а:

```text
A: R R R N N
B: N N R R R
```

При `K=5`:

```text
Precision@5(A) = 3/5
Precision@5(B) = 3/5
```

Но для пользователя A обычно лучше, потому что relevant результаты стоят выше.

Если позиция важна, используют:

- NDCG@K;
- MRR;
- MAP.

---

## 18. Precision@K и исторические клики

В условии Greenterest positive можно задавать через исторические реакции, например клики.

Важно понимать:

> offline Precision@K по историческим кликам — не то же самое, что будущий CTR новой модели.

Исторические клики зависели от того, что показывала старая система и на каких позициях. Для учебной задачи этот bias игнорируется и `labels` принимаются как ground truth.

---

## 19. Типичные ошибки

### Ошибка 1 — делить на все positives

```python
tp / sum(labels)
```

Это Recall.

### Ошибка 2 — взять `labels[:k]`

Нужно сначала отсортировать объекты по scores.

### Ошибка 3 — сортировать scores и labels отдельно

Так теряется связь между предсказанием и истинным label.

### Ошибка 4 — сортировать по возрастанию

Если больший score означает большую релевантность, нужен descending order.

### Ошибка 5 — использовать threshold

`@K` — это Top-K, не threshold classification.

---

## 20. Мини-тесты

```python
assert precision_at_k(
    labels=[1, 0, 1],
    scores=[0.9, 0.8, 0.7],
    k=2,
) == 0.5
```

Top-2 labels:

```text
[1, 0]
```

Один relevant из двух.

Ещё:

```python
assert precision_at_k(
    labels=[1, 1, 0],
    scores=[0.9, 0.8, 0.1],
    k=2,
) == 1.0
```

---

## 21. Связь с confusion matrix

```text
                      ACTUAL
                 positive  negative

TOP-K               TP       FP
OUTSIDE TOP-K       FN       TN
```

Precision смотрит на строку Top-K:

\[
Precision = TP/(TP+FP)
\]

То есть:

> Из всего, что модель выбрала, какая доля правильная?

---

## 22. Когда Precision особенно важен

Precision важен, когда False Positive портят опыт или дороги.

Примеры:

- конечная поисковая выдача;
- первые рекомендации;
- результаты, которые требуют ручной проверки;
- alerting-системы;
- moderation queue с ограниченной пропускной способностью.

Если человек способен посмотреть только 20 результатов, хочется, чтобы эти 20 были максимально качественными.

---

## 23. Вопросы на собеседовании

### 1. Что такое Precision@K?

Доля relevant объектов среди первых K результатов ranking-а.

### 2. Формула?

\[
Precision@K = TP/(TP+FP)
\]

При полном Top-K:

\[
Precision@K = relevant@K/K
\]

### 3. Может Precision@K увеличиваться при росте K?

Да. Например, если следующий добавленный объект relevant.

### 4. Обязан ли Precision@K быть монотонным?

Нет.

### 5. Может Precision=1 при маленьком Recall?

Да. Если Top-K полностью relevant, но relevant объектов в системе намного больше K.

### 6. Что использовать, если position внутри Top-K важна?

NDCG, MRR, MAP и другие position-aware ranking metrics.

### 7. В чём разница Precision и Specificity?

Precision нормируется на predicted positives:

```text
TP + FP
```

Specificity нормируется на actual negatives:

```text
TN + FP
```

---

## 24. Похожие интервью-задачи

### Задача A

```text
labels = [0, 1, 1, 0]
scores = [0.9, 0.8, 0.7, 0.6]
K = 3
```

Top-3 labels:

```text
[0, 1, 1]
```

\[
Precision@3 = 2/3
\]

### Задача B

Есть 100 relevant документов. Top-10 содержит 9 relevant.

\[
Precision@10 = 9/10 = 0.9
\]

\[
Recall@10 = 9/100 = 0.09
\]

### Задача C

Модель A:

```text
Precision@5 = 1.0
Precision@20 = 0.30
```

Интерпретация:

первые 5 результатов идеальны по бинарной релевантности, но при расширении выдачи до 20 добавляется много нерелевантных объектов.

---

## 25. Мини-шпаргалка

```text
Precision = "насколько чисто то, что выбрали"

Precision@K =
positive в Top-K
-----------------
размер Top-K
```

И:

```text
Precision = TP / (TP + FP)
```

---

## 26. Связь с заданием курса

Общий алгоритм:

```text
1. Сохранить пары label-score.
2. Отсортировать по score по убыванию.
3. Взять первые K.
4. Посчитать relevant внутри Top-K.
5. Разделить на размер выбранного Top-K согласно контракту задачи.
```

Перед автопроверкой:

- имя функции `precision_at_k`;
- сигнатура совпадает;
- ranking строится по scores;
- используется descending order;
- score и label не рассинхронизированы;
- возвращается float;
- обработан пустой Top-K.

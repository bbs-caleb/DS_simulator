# Recall@K — с абсолютного нуля

> Если слова `label`, `score`, `Top-K`, `TP`, `FN` ещё не стали понятными, сначала прочитай `00_START_HERE.md`.

---

# 1. До формулы: какую проблему решает Recall

Представь, что в истории есть **10 действительно подходящих картинок** для запроса пользователя.

Новая модель поставила в Top-20 только 6 из этих 10.

Вопрос Recall:

> Из всех хороших картинок сколько мы сумели найти наверху?

Ответ:

```text
нашли 6 из 10
```

То есть:

```text
Recall@20 = 0.6 = 60%
```

Вот и вся главная идея Recall.

---

# 2. Что значит слово Recall

Не пытайся переводить буквально. Удобнее ассоциация:

```text
Recall = охват хороших объектов
```

Он спрашивает:

> **Сколько всего хорошего мы не потеряли?**

---

# 3. Что такое positive именно здесь

В нашей задаче:

```text
label = 1 -> positive -> релевантная картинка
label = 0 -> negative -> нерелевантная картинка
```

Recall смотрит именно на positive-класс.

---

# 4. TP и FN для Recall

Из всех хороших картинок возможны два исхода.

## Хорошая попала в Top-K

Это:

```text
TP = True Positive
```

## Хорошая НЕ попала в Top-K

Это:

```text
FN = False Negative
```

Поэтому все хорошие картинки:

```text
TP + FN
```

А найденные хорошие:

```text
TP
```

Отсюда формула возникает естественно:

```text
Recall = найденные хорошие / все хорошие
```

или:

```text
Recall = TP / (TP + FN)
```

---

# 5. Первый ручной пример

Есть 5 картинок:

```python
labels = [1, 0, 1, 0, 1]
scores = [0.90, 0.80, 0.20, 0.70, 0.60]
k = 3
```

Пары:

```text
A: good, score 0.90
B: bad,  score 0.80
C: good, score 0.20
D: bad,  score 0.70
E: good, score 0.60
```

Сортируем по score:

```text
1. A good 0.90
2. B bad  0.80
3. D bad  0.70
4. E good 0.60
5. C good 0.20
```

Top-3:

```text
A good -> TP
B bad  -> не влияет на denominator Recall
D bad  -> не влияет на denominator Recall
```

За Top-3 остались хорошие:

```text
E good -> FN
C good -> FN
```

Итого:

```text
TP = 1
FN = 2
```

Recall:

```text
1 / (1 + 2) = 1/3 = 0.333...
```

То есть модель нашла только треть всех реально хороших картинок.

---

# 6. Почему плохие картинки почти не интересуют Recall

Заметь: Recall не использует `TN` и `FP` напрямую.

Его вопрос только:

> Что произошло со всеми реальными positives?

Каждый positive либо:

```text
нашли -> TP
потеряли -> FN
```

Поэтому denominator — `TP + FN`.

---

# 7. Recall@K

Обычный Recall в классификации использует predicted positive по некоторому правилу, например threshold.

В нашей ranking-задаче правило другое:

```text
Top-K = predicted positive
```

Поэтому:

```text
Recall@K = число positive внутри Top-K / число positive вообще
```

---

# 8. Хороший пример

```python
labels = [1, 0, 1, 0, 1]
scores = [0.99, 0.10, 0.95, 0.20, 0.90]
k = 3
```

После сортировки Top-3:

```text
1 -> good
2 -> good
3 -> good
```

Всего good = 3.

Нашли = 3.

```text
Recall@3 = 3/3 = 1.0
```

То есть не потеряли ни одной релевантной картинки.

---

# 9. Почему Recall=1 не означает идеальную систему

Представь:

```text
2 хороших картинки
998 плохих
K = 1000
```

Мы показываем вообще всё.

Обе хорошие точно внутри выдачи:

```text
Recall = 2/2 = 1
```

Но пользователю приходится смотреть 998 плохих результатов.

Вот почему кроме Recall нужен Precision.

---

# 10. Recall vs Precision простейшим языком

Пусть:

```text
всего good = 10
Top-5 содержит 4 good
```

Recall:

```text
4 / 10 = 0.4
```

Вопрос:

> Из всех хороших нашли сколько?

Precision:

```text
4 / 5 = 0.8
```

Вопрос:

> Из выбранных пяти сколько хорошие?

Один и тот же Top-5 может иметь:

```text
Recall = 40%
Precision = 80%
```

Это нормально.

---

# 11. Что происходит с Recall при увеличении K

Представь ranking:

```text
1 good
2 bad
3 good
4 bad
5 good
```

Recall@1 учитывает первый объект.

Recall@2 включает всё из Top-1 плюс ещё объект.

Recall@3 включает всё из Top-2 плюс ещё объект.

Когда K увеличивается, уже найденные хорошие объекты не исчезают.

Поэтому:

```text
Recall@1 <= Recall@2 <= Recall@3 <= ...
```

Recall@K не может уменьшаться при росте K для фиксированного ranking-а.

---

# 12. Почему это важно для поиска

Часто поиск двухэтапный:

```text
1. Retriever выбирает, например, 1000 кандидатов
2. Reranker красиво переставляет эти 1000
```

Если правильная картинка не попала в 1000 кандидатов, второй этап её уже не спасёт.

Поэтому на candidate generation высокий Recall очень важен.

---

# 13. Как написать функцию

```python
from typing import List


def recall_at_k(labels: List[int], scores: List[float], k=5) -> float:
    ranked_indices = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True,
    )

    top_k_indices = ranked_indices[:k]

    tp = sum(labels[i] for i in top_k_indices)
    all_positives = sum(labels)

    if all_positives == 0:
        return 0.0

    return tp / all_positives
```

---

# 14. Разбор кода по строкам

```python
range(len(scores))
```

создаёт индексы объектов:

```text
0, 1, 2, 3, ...
```

```python
key=lambda i: scores[i]
```

говорит сортировать индексы по score соответствующего объекта.

```python
reverse=True
```

нужен, потому что больший score должен идти первым.

```python
top_k_indices = ranked_indices[:k]
```

берём первые K.

```python
tp = sum(labels[i] for i in top_k_indices)
```

Поскольку labels только 0/1, сумма равна количеству positives в Top-K.

```python
all_positives = sum(labels)
```

Количество всех good объектов.

И затем:

```python
tp / all_positives
```

то есть:

```text
найденные хорошие / все хорошие
```

---

# 15. Частые ошибки

## Ошибка: `labels[:k]`

Нельзя брать первые K исходного списка. Сначала нужно построить ranking по scores.

## Ошибка: отдельно сортировать labels

Так ломается связь между картинкой, её score и label.

## Ошибка: делить на K

```python
tp / k
```

это идея Precision, не Recall.

## Ошибка: использовать `score > 0.5`

Здесь задача про Top-K, а не про threshold.

---

# 16. Edge cases

## Нет ни одного positive

```python
labels = [0, 0, 0]
```

Тогда denominator Recall = 0.

Математически Recall не определён. Учебная функция часто возвращает `0.0`, но в реальных системах могут возвращать NaN или пропускать такой query при усреднении.

## K больше числа объектов

Python `[:k]` просто вернёт все доступные объекты.

## K = 0

Top-0 пуст. При наличии positives Recall будет 0.

---

# 17. Вопросы на собеседовании

## Что такое Recall@K?

Доля всех релевантных объектов, которые попали в Top-K.

## Что в denominator?

Все actual positives: `TP + FN`.

## Может ли Recall@K уменьшиться при росте K?

Нет, при фиксированном ranking-е.

## Может Recall=1 и Precision быть очень плохим?

Да. Например, если K огромный и мы показали почти всё.

## Почему Recall важен на candidate generation?

Потому что потерянный на первом этапе relevant объект уже невозможно вернуть reranker-ом.

## Что делать с query без positives?

Сказать, что формула имеет нулевой denominator, и уточнить принятую конвенцию.

---

# 18. Тренировка

```text
labels = [1, 0, 1, 1, 0]
scores = [0.3, 0.9, 0.8, 0.1, 0.7]
K = 3
```

Ranking:

```text
0.9 -> bad
0.8 -> good
0.7 -> bad
0.3 -> good
0.1 -> good
```

Top-3 содержит 1 good.

Всего good = 3.

```text
Recall@3 = 1/3
```

---

# 19. Запоминалка

```text
RECALL = ИЗ ВСЕГО ХОРОШЕГО СКОЛЬКО НАШЛИ

Recall@K =
positive в Top-K
-----------------
positive вообще
```

или:

```text
TP / (TP + FN)
```

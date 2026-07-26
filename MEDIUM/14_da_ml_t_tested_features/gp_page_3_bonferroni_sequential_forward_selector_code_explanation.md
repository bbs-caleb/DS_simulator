# Page 3 — Bonferroni SequentialForwardSelector: объяснение кода

## 1. Главное изменение относительно page_2

На `page_2` было:

```python
if p_value < self.alpha:
    ...
```

На `page_3` порог зависит от числа кандидатов:

```python
if self.bonferroni:
    corrected_alpha = (
        self.alpha / len(excluded_features)
    )
else:
    corrected_alpha = self.alpha
```

После этого:

```python
if p_value < corrected_alpha:
    ...
```

---

# 2. Новый аргумент конструктора

```python
bonferroni: bool = True
```

`bool` означает логический тип:

```python
True
False
```

По умолчанию поправка включена.

---

# 3. Новый атрибут объекта

```python
self.bonferroni = bonferroni
```

Без этой строки API-тест может написать:

```text
SequentialForwardSelector should have
attribute bonferroni
```

Локальный аргумент `bonferroni` существует только во время вызова `__init__`.

`self.bonferroni` сохраняется внутри объекта.

---

# 4. Начало fit

```python
self.n_features_ = X.shape[1]
```

Сохраняется исходное число признаков.

---

```python
included_features = []
excluded_features = list(
    range(self.n_features_)
)
```

Например, для пяти колонок:

```python
included_features = []
excluded_features = [0, 1, 2, 3, 4]
```

---

# 5. Начальный baseline

```python
current_scores = cross_val_score(
    DummyRegressor(),
    X,
    y,
    scoring="r2",
    cv=self.cv,
    n_jobs=-1,
)
```

Почему нужен массив, а не одно среднее?

Потому что далее применяется парный t-тест.

При `RepeatedKFold(3 × 10)`:

```python
len(current_scores) == 30
```

---

# 6. Число возможных итераций

```python
features_to_select = min(
    self.max_features,
    self.n_features_,
)
```

Если в датасете 6 колонок, нельзя выбрать 10 разных колонок.

---

# 7. Внешний цикл

```python
for step in range(features_to_select):
```

На каждой итерации добавляется максимум один признак.

Но цикл может закончиться раньше:

```python
break
```

---

# 8. Список допустимых кандидатов

```python
significant_candidates = []
```

Сюда попадут кандидаты, прошедшие текущий статистический порог.

---

# 9. Расчёт порога Бонферрони

```python
if self.bonferroni:
    corrected_alpha = (
        self.alpha / len(excluded_features)
    )
else:
    corrected_alpha = self.alpha
```

Рассмотрим оба режима.

## Режим `True`

Пусть:

```text
alpha = 0.05
excluded features = 50
```

Тогда:

```text
corrected alpha = 0.001
```

## Режим `False`

Порог остаётся:

```text
0.05
```

---

# 10. Почему расчёт находится внутри внешнего цикла

После выбора признака выполняется:

```python
excluded_features.remove(best_feature)
```

Количество оставшихся кандидатов меняется.

Следовательно, на следующем шаге должен измениться и denominator:

```python
len(excluded_features)
```

Если вычислить threshold только один раз перед циклом, реализация будет неправильной.

---

# 11. Внутренний цикл

```python
for candidate in excluded_features:
```

Проверяется каждый ещё не выбранный признак.

---

# 12. Временный набор

```python
subset = included_features + [candidate]
```

Пусть:

```python
included_features = [17, 20]
candidate = 44
```

Получаем:

```python
subset = [17, 20, 44]
```

---

# 13. Оценки кандидата

```python
candidate_scores = cross_val_score(
    self.model,
    X[:, subset],
    y,
    scoring="r2",
    cv=self.cv,
    n_jobs=-1,
)
```

`X[:, subset]` означает:

```text
все строки
только колонки subset
```

---

# 14. Парный t-тест

```python
_, p_value = ttest_rel(
    candidate_scores,
    current_scores,
    alternative="greater",
)
```

Проверяется:

```text
candidate scores > current scores
```

Почему paired:

```text
оба массива получены на одинаковых CV splits
```

---

# 15. Решение по скорректированному порогу

```python
if p_value < corrected_alpha:
```

Пример:

```text
p-value = 0.004
ordinary alpha = 0.05
Bonferroni alpha = 0.001
```

Без Bonferroni кандидат прошёл бы.

С Bonferroni он не проходит.

Именно так отфильтровываются случайные слабые эффекты.

---

# 16. Что сохраняется

```python
significant_candidates.append(
    (candidate, candidate_scores)
)
```

Хранятся:

- индекс;
- весь массив CV scores.

Массив нужен для:

- выбора максимального среднего;
- обновления current baseline.

---

# 17. Отсутствие значимых кандидатов

```python
if not significant_candidates:
    break
```

Это нормальное завершение SFS.

Оно означает:

```text
ни один оставшийся feature не выдержал
текущий скорректированный threshold
```

---

# 18. Лучший среди прошедших

```python
best_feature, best_scores = max(
    significant_candidates,
    key=lambda result: result[1].mean(),
)
```

Bonferroni не меняет правило выбора победителя.

Она лишь фильтрует кандидатов.

Среди прошедших всё равно выбирается максимальный mean `R²`.

---

# 19. Обновление решения

```python
included_features.append(best_feature)
```

Добавляем победителя.

```python
excluded_features.remove(best_feature)
```

Уменьшаем число кандидатов.

```python
current_scores = best_scores
```

Следующая итерация сравнивается с новой моделью.

---

# 20. Почему нельзя добавлять всех значимых сразу

После добавления одного признака ценность остальных меняется.

Пример:

- feature A и feature B несут одинаковый сигнал;
- оба значимы относительно текущей модели;
- после добавления A feature B становится избыточным.

Поэтому SFS добавляет ровно одного победителя и пересчитывает остальные варианты заново.

---

# 21. Итоговая сортировка

```python
self.selected_features_ = sorted(
    included_features
)
```

SFS может выбирать в порядке:

```python
[20, 46, 17, 44, 26]
```

Но итоговый атрибут:

```python
[17, 20, 26, 44, 46]
```

---

# 22. transform

```python
assert self.selected_features_ is not None, (
    "Fit the model first"
)
```

До fit результат неизвестен.

После fit:

```python
return X[:, self.selected_features_]
```

---

# 23. n_selected_features_

```python
@property
def n_selected_features_(self) -> int:
```

Обращение:

```python
selector.n_selected_features_
```

Возвращает:

```python
len(self.selected_features_)
```

---

# 24. Полный поток одного шага

Пусть:

```text
alpha = 0.05
bonferroni = True
осталось 25 кандидатов
```

Тогда:

```text
corrected_alpha = 0.05 / 25 = 0.002
```

Получены кандидаты:

| Feature | Mean R² | p-value | Прошёл |
|---:|---:|---:|:---:|
| 7 | 0.710 | 0.0005 | Да |
| 12 | 0.716 | 0.0015 | Да |
| 18 | 0.720 | 0.0030 | Нет |
| 21 | 0.705 | 0.3000 | Нет |

Feature `18` имеет самое высокое среднее, но не проходит Bonferroni threshold.

Среди допустимых выигрывает feature `12`.

---

# 25. Псевдокод

```text
current_scores = dummy CV scores

для каждого шага:

    m = количество оставшихся признаков

    threshold =
        alpha / m, если bonferroni
        alpha, иначе

    significant = []

    для каждого кандидата:
        scores = CV(current + candidate)
        p = paired one-sided t-test

        если p < threshold:
            significant.append(candidate)

    если significant пуст:
        stop

    взять максимальный mean score
    обновить selected
    обновить current_scores
```

---

# 26. Самые частые ошибки

## Делить на исходное число признаков

Неправильно:

```python
self.alpha / self.n_features_
```

Так threshold не меняется.

## Делить на max_features

Неправильно:

```python
self.alpha / self.max_features
```

`max_features` не является числом одновременно тестируемых гипотез.

## Делить внутри внутреннего цикла после изменения excluded

Внутри одной итерации размер семейства должен быть фиксирован.

## Применять Bonferroni даже при False

Нужно сохранить возможность обычного t-tested режима.

## Вычислять corrected_alpha один раз до всех итераций

Количество гипотез уменьшается, поэтому threshold обязан пересчитываться.

---

# 27. Главное выражение страницы

```python
corrected_alpha = (
    self.alpha / len(excluded_features)
    if self.bonferroni
    else self.alpha
)
```

И затем:

```python
if p_value < corrected_alpha:
```

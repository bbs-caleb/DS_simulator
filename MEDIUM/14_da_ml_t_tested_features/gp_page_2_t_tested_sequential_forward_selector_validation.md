# Page 2 — T-Tested SequentialForwardSelector: валидация и ошибки

## 1. Ошибка текущей попытки

Результат:

```text
0 / 100
```

Все тесты остановились на API:

```text
AssertionError:
SequentialForwardSelector should have attribute alpha
```

Это не означает, что нужно просто добавить строку:

```python
self.alpha = 0.05
```

Правильная реализация должна:

1. принимать `alpha` как аргумент;
2. сохранять `self.alpha`;
3. использовать его как threshold;
4. считать парный t-test;
5. сравнивать candidate scores с current scores;
6. останавливать selection при отсутствии значимых кандидатов.

---

## 2. Проверка конструктора

```python
selector = SequentialForwardSelector(
    model,
    cv,
    max_features=10,
    verbose=0,
    alpha=0.05,
)
```

Проверяем:

```python
assert selector.model is model
assert selector.cv is cv
assert selector.max_features == 10
assert selector.verbose == 0
assert selector.alpha == 0.05
```

---

## 3. Проверка начального состояния

```python
assert selector.n_features_ is None
assert selector.selected_features_ is None
```

Это соответствует состоянию «fit ещё не запускался».

---

## 4. Проверка после fit

```python
selector.fit(X, y)
```

Должно выполняться:

```python
assert selector.n_features_ == X.shape[1]
assert isinstance(
    selector.selected_features_,
    list,
)
```

---

## 5. Проверка свойства

```python
assert selector.n_selected_features_ == len(
    selector.selected_features_
)
```

---

## 6. Проверка transform

```python
X_selected = selector.transform(X)

np.testing.assert_array_equal(
    X_selected,
    X[:, selector.selected_features_],
)
```

---

## 7. Проверка уникальности

```python
assert len(selector.selected_features_) == len(
    set(selector.selected_features_)
)
```

Выбранный feature удаляется из excluded, поэтому повторов быть не должно.

---

## 8. Проверка сортировки

```python
assert selector.selected_features_ == sorted(
    selector.selected_features_
)
```

---

## 9. Проверка верхнего лимита

```python
assert selector.n_selected_features_ <= (
    selector.max_features
)
```

---

## 10. Проверка упавшего ранее random_state

Для:

```text
random_state = 69
n_samples = 10 000
n_features = 50
n_informative = 5
max_features = 10
RepeatedKFold = 3 × 10
alpha = 0.05
```

Локальная T-tested реализация выбрала:

```python
[17, 20, 26, 44, 46]
```

То есть пять информативных признаков без трёх дополнительных шумовых колонок, которые выбирала простая логика сравнения средних.

---

## 11. Почему результат page_1 и page_2 отличается

Базовый SFS ранее мог получить:

```python
[8, 9, 10, 17, 20, 26, 44, 46]
```

Page_2 требует более строгого решения.

Шумовые признаки `8`, `9`, `10` могли незначительно поднять среднее, но не прошли статистическую проверку против текущего набора.

---

## 12. Граничный случай: ни один первый признак незначим

Тогда:

```python
significant_candidates == []
```

Алгоритм завершится.

После fit:

```python
selected_features_ == []
```

`transform(X)` вернёт матрицу:

```text
n_samples × 0 columns
```

---

## 13. Граничный случай: max_features больше n_features

Используется:

```python
min(self.max_features, self.n_features_)
```

Поэтому лишних итераций не будет.

---

## 14. Граничный случай: max_features = 0

Цикл не запускается.

После fit:

```python
selected_features_ == []
```

---

## 15. Граничный случай: p-value равен alpha

Условие:

```python
p_value < self.alpha
```

Если:

```text
p-value == alpha
```

кандидат не проходит.

Это стандартное строгое правило задания.

---

## 16. Граничный случай: равные CV scores

Если:

```python
candidate_scores == current_scores
```

разности равны нулю.

SciPy может вернуть `nan` из-за нулевой дисперсии разностей.

Условие:

```python
nan < alpha
```

даёт `False`.

Кандидат не будет добавлен.

---

## 17. Типичные ошибки

### Ошибка 1. Только добавить attribute alpha

Неправильно:

```python
self.alpha = alpha
```

и оставить старую проверку средних.

API может пройти, но функциональный тест упадёт.

---

### Ошибка 2. Использовать `ttest_ind`

`ttest_ind` предназначен для независимых выборок.

CV scores здесь связаны одинаковыми фолдами.

Нужен:

```python
ttest_rel
```

---

### Ошибка 3. Перепутать аргументы

Неправильно:

```python
ttest_rel(
    current_scores,
    candidate_scores,
    alternative="greater",
)
```

Это проверяет, что current больше candidate.

Правильно:

```python
ttest_rel(
    candidate_scores,
    current_scores,
    alternative="greater",
)
```

---

### Ошибка 4. Использовать two-sided

Неправильно:

```python
ttest_rel(
    candidate_scores,
    current_scores,
)
```

По умолчанию тест двусторонний.

Задание ищет именно улучшение:

```python
alternative="greater"
```

---

### Ошибка 5. Сравнивать каждый шаг с DummyRegressor

DummyRegressor нужен только для начального baseline.

После выбора feature:

```python
current_scores = best_scores
```

---

### Ошибка 6. Выбрать минимальный p-value вместо максимального score

SFS выбирает лучшую модель среди статистически допустимых кандидатов.

Кандидат с самым маленьким p-value не обязан иметь максимальный mean `R²`.

---

### Ошибка 7. Добавить всех значимых кандидатов сразу

За одну итерацию SFS добавляет один признак.

После этого все оставшиеся кандидаты должны быть переоценены уже относительно нового набора.

---

### Ошибка 8. Использовать полный baseline LinearRegression

Нельзя сравнивать первый признак с моделью на всех 50 колонках.

Начальный baseline:

```python
DummyRegressor()
```

---

### Ошибка 9. Не сортировать результат

Grader может ожидать:

```python
[17, 20, 26, 44, 46]
```

а не порядок выбора:

```python
[20, 46, 17, 44, 26]
```

---

### Ошибка 10. Добавить Bonferroni без требования текущей страницы

Bonferroni меняет threshold:

```python
alpha / number_of_tests
```

и может изменить ожидаемые признаки.

На текущем page_2 grader сообщил об `alpha`. В файл не добавляется неуказанная коррекция множественных сравнений.

---

## 18. Локальный API smoke test

```python
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import RepeatedKFold

model = LinearRegression()
cv = RepeatedKFold(
    n_splits=3,
    n_repeats=10,
    random_state=69,
)

selector = SequentialForwardSelector(
    model,
    cv,
    max_features=10,
    verbose=0,
    alpha=0.05,
)

assert selector.alpha == 0.05
assert selector.n_features_ is None
assert selector.selected_features_ is None
```

---

## 19. Финальный чек-лист

Перед загрузкой проверь:

```text
[ ] имя класса точное
[ ] есть alpha в __init__
[ ] есть self.alpha
[ ] есть DummyRegressor
[ ] есть ttest_rel
[ ] candidate_scores идут первым аргументом
[ ] alternative="greater"
[ ] используется p_value < self.alpha
[ ] best выбирается по mean R²
[ ] current_scores обновляется
[ ] result сортируется
[ ] transform использует selected_features_
[ ] n_selected_features_ является property
```

---

## 20. Файл для отправки

```text
gp_page_2_sequential_forward_selector_solution.py
```

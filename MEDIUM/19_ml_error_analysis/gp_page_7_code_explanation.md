# gp_page_7 — Подробное объяснение кода Adversarial Validation

## 1. Структура файла

Файл:

```text
gp_page_7_adversarial_validation.py
```

содержит:

```python
adversarial_validation
```

и одну внутреннюю функцию:

```python
_absolute_residuals
```

---

# 2. Импорты

```python
from typing import Optional
```

`Optional[str]` означает:

```text
параметр может быть строкой или None
```

---

```python
import numpy as np
```

NumPy используется для:

- модуля;
- округления вниз;
- работы с массивами важностей.

---

```python
import pandas as pd
```

Pandas используется для:

- DataFrame;
- Series;
- индексов;
- формирования искусственного таргета;
- хранения feature importance.

---

```python
import residuals
```

Это обязательный импорт из условия.

Мы переиспользуем функции первого шага, а не копируем их формулы.

---

```python
from sklearn.base import ClassifierMixin
```

`ClassifierMixin` используется как аннотация типа классификатора.

Функция ожидает объект, который поддерживает:

```python
fit(...)
predict_proba(...)
```

---

```python
from sklearn.metrics import roc_auc_score
```

Эта функция рассчитывает ROC-AUC вспомогательной модели.

---

# 3. Внутренняя функция `_absolute_residuals`

```python
def _absolute_residuals(
    y_test,
    y_pred,
    func,
):
```

Она:

1. Выбирает нужную функцию остатков.
2. Вызывает её.
3. Берёт модуль.
4. Возвращает pandas Series с правильным индексом.

---

## 3.1 Выбор имени функции

```python
function_name = "residuals" if func is None else func
```

Если пользователь передал:

```python
func=None
```

используется обычная функция:

```python
residuals.residuals
```

---

## 3.2 `getattr`

```python
residual_function = getattr(
    residuals,
    function_name,
)
```

Если:

```python
function_name = "ape"
```

то это эквивалентно:

```python
residual_function = residuals.ape
```

---

## 3.3 Вызов функции

```python
values = residual_function(
    y_test,
    y_pred,
)
```

На этом шаге вычисляются остатки или псевдоостатки.

---

## 3.4 Модуль и индекс

```python
return pd.Series(
    np.abs(values),
    index=y_test.index,
    dtype=float,
)
```

Почему нужен модуль:

```text
+20 и -20 — одинаковая сила ошибки
```

Почему сохраняется индекс:

Нужно точно связать ошибку с соответствующей строкой `X_test`.

Индекс может быть нестандартным:

```text
101, 205, 900
```

---

# 4. Начало `adversarial_validation`

```python
resid = _absolute_residuals(
    y_test=y_test,
    y_pred=y_pred,
    func=func,
)
```

На выходе:

```text
индекс → абсолютная ошибка
```

Например:

```text
101     2.0
205    15.0
309     1.0
410    20.0
```

---

# 5. Сколько объектов считать worst cases

```python
top_k = int(np.floor(len(X_test) * quantile))
```

Разберём по шагам.

Допустим:

```text
len(X_test) = 1000
quantile = 0.12
```

Умножение:

```text
1000 × 0.12 = 120
```

`np.floor` округляет вниз:

```text
120
```

Если получилось:

```text
12.8
```

то:

```text
floor(12.8) = 12
```

После `int` получаем обычное целое число Python.

---

# 6. Поиск крупнейших ошибок

```python
worst_indices = resid.nlargest(top_k).index
```

`nlargest(top_k)`:

1. Сортирует значения по убыванию.
2. Берёт первые `top_k`.
3. Сохраняет индексы исходных объектов.

Пример:

```text
410    20
205    15
101     2
309     1
```

При:

```python
top_k = 2
```

получим индексы:

```text
[410, 205]
```

---

# 7. Создание искусственного таргета

```python
is_error = pd.Series(
    0,
    index=X_test.index,
    dtype=int,
)
```

Создаётся Series из нулей.

Каждый объект сначала считается обычным:

```text
is_error = 0
```

---

## 7.1 Worst cases получают класс 1

```python
is_error.loc[worst_indices] = 1
```

Теперь:

```text
класс 0 → обычный объект
класс 1 → worst case
```

Почему используется `.loc`:

`worst_indices` — это метки индекса, а не позиции.

Например:

```text
101, 205, 410
```

`.loc` выбирает строки именно по таким меткам.

---

# 8. Обучение вспомогательной модели

```python
classifier.fit(X_test, is_error)
```

Классификатор пытается найти закономерность:

```text
признаки объекта → вероятность крупной ошибки
```

Основная модель уже не переобучается.

Мы обучаем отдельный диагностический классификатор.

---

# 9. Получение вероятностей

```python
error_probability = classifier.predict_proba(X_test)[:, 1]
```

`predict_proba` возвращает матрицу:

```text
[
    [P(class=0), P(class=1)],
    [P(class=0), P(class=1)],
    ...
]
```

Срез:

```python
[:, 1]
```

берёт вероятность класса 1:

```text
вероятность того, что объект является worst case
```

---

# 10. ROC-AUC

```python
roc_auc = roc_auc_score(
    is_error,
    error_probability,
)
```

ROC-AUC измеряет качество ранжирования.

Высокое значение означает:

```text
вспомогательная модель обычно ставит worst cases выше обычных объектов
```

По условию задания метрика рассчитывается на полной выборке.

Важно понимать:

Это training ROC-AUC, поэтому в реальной системе он может быть завышен.

---

# 11. Feature importance для деревьев

```python
if hasattr(
    classifier,
    "feature_importances_",
):
```

Деревья и ансамбли деревьев часто имеют атрибут:

```python
feature_importances_
```

Например:

- RandomForestClassifier;
- GradientBoostingClassifier;
- CatBoostClassifier;
- некоторые реализации boosting.

---

## 11.1 Формирование Series

```python
feature_importances = pd.Series(
    np.abs(classifier.feature_importances_),
    index=X_test.columns,
)
```

Индексом становятся названия признаков.

Пример:

```text
promo_flag        0.40
oos_share         0.25
price_change      0.20
store_format      0.15
```

---

# 12. Feature importance для линейных моделей

```python
elif hasattr(classifier, "coef_"):
```

Логистическая регрессия имеет коэффициенты:

```python
classifier.coef_
```

Для бинарной классификации форма обычно:

```text
(1, number_of_features)
```

Поэтому берётся первая строка:

```python
classifier.coef_[0]
```

---

## 12.1 Почему берётся модуль

```python
np.abs(classifier.coef_[0])
```

Знак показывает направление:

- положительный коэффициент повышает вероятность worst case;
- отрицательный снижает.

Но в поле feature importance нам нужна сила признака.

Поэтому используется модуль.

---

# 13. Если важности нет

```python
else:
    feature_importances = None
```

Не каждый классификатор имеет простой встроенный способ получить важность.

Например, некоторые модели могут не иметь:

- `feature_importances_`;
- `coef_`.

В таком случае возвращается `None`.

В production можно использовать:

- permutation importance;
- SHAP;
- drop-column importance.

Но они не требуются в этом задании.

---

# 14. Формирование результата

```python
result = {
    "ROC-AUC": roc_auc,
    "feature_importances": feature_importances,
}
```

Возвращается словарь с точно заданными ключами.

---

# 15. Почему решение соответствует условию

Учтены требования:

- используется `import residuals`;
- функции выбираются через `getattr`;
- `func=None` означает обычные остатки;
- ошибки берутся по модулю;
- top-k определяется как `floor(n × quantile)`;
- именно крупнейшие ошибки получают класс 1;
- классификатор обучается на `X_test`;
- ROC-AUC считается на полной выборке;
- используются вероятности класса 1;
- поддерживаются `feature_importances_`;
- поддерживается `coef_`;
- коэффициенты берутся по модулю;
- результат имеет требуемые ключи;
- код соответствует PEP8.

---

# 16. Ограничение учебного решения

Вспомогательная модель обучается и оценивается на одних данных.

Из-за этого ROC-AUC может быть оптимистичным.

Более надёжный production-вариант:

```text
1. Разделить данные на folds.
2. Получить out-of-fold вероятности.
3. Посчитать ROC-AUC на OOF predictions.
4. Проверить устойчивость feature importance.
```

Но это изменило бы логику задания, поэтому в сдаваемом коде используется именно требуемая полная выборка.

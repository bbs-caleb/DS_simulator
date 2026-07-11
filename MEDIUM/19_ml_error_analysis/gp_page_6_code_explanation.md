# gp_page_6 — Подробное объяснение кода Best/Worst-Case Analysis

## 1. Структура файла

Файл:

```text
gp_page_6_best_worst_cases.py
```

содержит:

```python
best_cases
worst_cases
```

Также используются две внутренние вспомогательные функции:

```python
_absolute_residuals
_select_cases
```

Подчёркивание в начале имени означает:

> Функция предназначена для внутреннего использования внутри модуля.

---

# 2. Импорты

```python
from typing import Optional
```

`Optional` означает, что параметр может содержать значение определённого типа или `None`.

Например:

```python
mask: Optional[pd.Series] = None
```

означает:

```text
mask — либо pandas Series, либо None
```

---

```python
import numpy as np
```

NumPy нужен для:

```python
np.abs(...)
```

то есть взятия модуля ошибок.

---

```python
import pandas as pd
```

Pandas нужен для:

- `DataFrame`;
- `Series`;
- индексов;
- фильтрации;
- `nsmallest`;
- `nlargest`;
- `.loc`.

---

```python
import residuals
```

Это принципиально важный импорт.

Мы не копируем формулы остатков, а используем функции из первого задания.

---

# 3. Функция `_absolute_residuals`

```python
def _absolute_residuals(
    y_test: pd.Series,
    y_pred: pd.Series,
    func: Optional[str],
) -> pd.Series:
```

Она решает две задачи:

1. Выбирает нужную функцию остатков.
2. Возвращает абсолютные остатки как pandas Series.

---

## 3.1 Определяем имя функции

```python
function_name = "residuals" if func is None else func
```

Это тернарное выражение.

Обычная запись выглядела бы так:

```python
if func is None:
    function_name = "residuals"
else:
    function_name = func
```

Если пользователь не указал функцию:

```python
func=None
```

будут считаться обычные остатки:

```text
y_true - y_pred
```

---

## 3.2 Получаем функцию по строковому имени

```python
residual_function = getattr(
    residuals,
    function_name,
)
```

Пример:

```python
function_name = "ape"
```

Тогда:

```python
getattr(residuals, "ape")
```

возвращает саму функцию:

```python
residuals.ape
```

Мы пока её не вызываем. Мы сохраняем ссылку на неё в переменную:

```python
residual_function
```

---

## 3.3 Вызываем выбранную функцию

```python
values = residual_function(
    y_test,
    y_pred,
)
```

В зависимости от `func` это может быть эквивалентно:

```python
residuals.residuals(y_test, y_pred)
```

или:

```python
residuals.squared_errors(y_test, y_pred)
```

или:

```python
residuals.logloss(y_test, y_pred)
```

или:

```python
residuals.ape(y_test, y_pred)
```

или:

```python
residuals.quantile_loss(y_test, y_pred)
```

Для `quantile_loss` используется значение `q` по умолчанию из реализации первого задания.

---

## 3.4 Берём абсолютные значения

```python
np.abs(values)
```

Это обязательное требование задания.

Даже если исходная функция возвращает signed residual:

```text
-15
```

в результате должно находиться:

```text
15
```

---

## 3.5 Создаём pandas Series

```python
return pd.Series(
    np.abs(values),
    index=y_test.index,
    dtype=float,
)
```

Почему нельзя оставить просто NumPy-массив?

Потому что нам важно сохранить соответствие:

```text
ошибка ↔ исходная строка
```

Индекс `y_test.index` позволяет затем выбрать соответствующие строки из:

- `X_test`;
- `y_test`;
- `y_pred`.

Пример:

```text
index: 101, 205, 900
```

Индекс не обязан быть:

```text
0, 1, 2
```

Поэтому нельзя полагаться только на обычные позиции.

---

# 4. Функция `_select_cases`

```python
def _select_cases(
    X_test,
    y_test,
    y_pred,
    top_k,
    mask,
    func,
    largest,
):
```

Она содержит общую логику для best и worst cases.

Различие только одно:

```text
best  → минимальные ошибки
worst → максимальные ошибки
```

Параметр:

```python
largest
```

управляет этим выбором.

---

# 5. Применение маски

```python
if mask is not None:
    X_test = X_test.loc[mask]
    y_test = y_test.loc[mask]
    y_pred = y_pred.loc[mask]
```

Если маска не передана, анализируется весь датасет.

Если маска передана, остаются только строки, где маска равна `True`.

---

## 5.1 Пример маски

```python
mask = X_test["is_promo"] == 1
```

Исходные данные:

| index | is_promo |
|---:|---:|
| 10 | 0 |
| 20 | 1 |
| 30 | 0 |
| 40 | 1 |

Маска:

```text
10    False
20     True
30    False
40     True
```

После:

```python
X_test.loc[mask]
```

останутся строки:

```text
20 и 40
```

---

## 5.2 Почему маска применяется до top-k

Допустим, нас интересуют худшие ошибки новых товаров.

Неправильно:

```text
1. Найти 10 худших товаров среди всех.
2. Из них оставить новые.
```

Может остаться только один новый товар.

Правильно:

```text
1. Оставить все новые товары.
2. Среди них найти 10 худших.
```

Именно так реализован corner-case analysis.

---

# 6. Рассчитываем остатки

```python
resid = _absolute_residuals(
    y_test,
    y_pred,
    func,
)
```

На выходе получаем Series:

```text
index
10     2.0
20    15.0
30     1.0
40     8.0
```

---

# 7. Выбор лучших или худших случаев

```python
if largest:
    selected_index = resid.nlargest(top_k).index
else:
    selected_index = resid.nsmallest(top_k).index
```

## Для worst cases

```python
resid.nlargest(top_k)
```

берёт самые большие ошибки.

## Для best cases

```python
resid.nsmallest(top_k)
```

берёт самые маленькие ошибки.

---

## 7.1 Почему используем индексы

Предположим:

```text
resid:
30     1
10     2
40     8
20    15
```

Для двух лучших случаев:

```text
selected_index = [30, 10]
```

После этого теми же индексами выбираются строки во всех объектах.

Так гарантируется, что:

- признаки;
- правильный ответ;
- прогноз;
- остаток

относятся к одной и той же исходной строке.

---

# 8. Формирование результата

```python
result = {
    "X_test": X_test.loc[selected_index],
    "y_test": y_test.loc[selected_index],
    "y_pred": y_pred.loc[selected_index],
    "resid": resid.loc[selected_index],
}
```

Функция возвращает словарь с четырьмя ключами.

---

## 8.1 `"X_test"`

Признаки выбранных объектов.

Тип:

```text
pandas DataFrame
```

---

## 8.2 `"y_test"`

Истинные значения выбранных объектов.

Тип:

```text
pandas Series
```

---

## 8.3 `"y_pred"`

Предсказания модели для выбранных объектов.

Тип:

```text
pandas Series
```

---

## 8.4 `"resid"`

Абсолютные значения ошибок.

Тип:

```text
pandas Series
```

Остатки уже:

- взяты по модулю;
- отсортированы;
- ограничены `top_k`.

---

# 9. Функция `best_cases`

```python
def best_cases(...):
    return _select_cases(
        ...
        largest=False,
    )
```

Параметр:

```python
largest=False
```

означает:

```text
выбираем самые маленькие остатки
```

---

# 10. Функция `worst_cases`

```python
def worst_cases(...):
    return _select_cases(
        ...
        largest=True,
    )
```

Параметр:

```python
largest=True
```

означает:

```text
выбираем самые большие остатки
```

---

# 11. Пример использования: обычные остатки

```python
result = worst_cases(
    X_test=X_test,
    y_test=y_test,
    y_pred=y_pred,
    top_k=10,
)
```

Так как:

```python
func=None
```

используется:

```python
residuals.residuals
```

---

# 12. Пример использования: squared errors

```python
result = worst_cases(
    X_test,
    y_test,
    y_pred,
    top_k=10,
    func="squared_errors",
)
```

---

# 13. Пример corner-case analysis

```python
promo_mask = X_test["is_promo"] == 1

result = worst_cases(
    X_test,
    y_test,
    y_pred,
    top_k=20,
    mask=promo_mask,
    func="ape",
)
```

Функция вернёт 20 промо-объектов с наибольшим абсолютным APE.

---

# 14. Почему решение соответствует требованиям

Учтены все условия:

- переиспользуется модуль `residuals`;
- функция выбирается динамически через `getattr`;
- поддерживается `func=None`;
- поддерживаются все имена функций из задания;
- маска применяется до выбора top-k;
- сортировка выполняется по абсолютной ошибке;
- в результате `resid` содержит абсолютные значения;
- best cases отсортированы по возрастанию;
- worst cases отсортированы по убыванию;
- индексы данных остаются синхронизированными;
- код не дублируется;
- соблюдается PEP8.

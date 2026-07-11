# gp_page_4 — Подробное объяснение решения

## 1. Готовое решение

Файл:

```text
gp_page_4_diagnostic_plots.py
```

содержит три функции:

```python
xy_fitted_residuals
xy_normal_qq
xy_scale_location
```

---

# 2. Импорты

```python
from typing import Tuple
```

`Tuple` используется для описания возвращаемого значения.

Каждая функция возвращает два массива:

```python
return x, y
```

Поэтому тип записан так:

```python
Tuple[np.ndarray, np.ndarray]
```

---

```python
import numpy as np
```

NumPy используется для:

- создания массивов;
- вычитания;
- среднего;
- стандартного отклонения;
- сортировки;
- модуля;
- квадратного корня;
- построения сетки квантилей.

---

```python
from scipy import stats
```

`scipy.stats` используется для функции:

```python
stats.norm.ppf
```

Она переводит уровни вероятности в квантили стандартного нормального распределения.

---

# 3. Функция `xy_fitted_residuals`

```python
def xy_fitted_residuals(
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
```

Функция принимает:

- `y_true` — реальные значения;
- `y_pred` — прогнозы модели.

---

## 3.1 Преобразование входов

```python
y_true = np.asarray(y_true, dtype=float)
y_pred = np.asarray(y_pred, dtype=float)
```

Это позволяет передавать не только NumPy-массивы, но и обычные списки Python.

Например:

```python
[10, 20, 30]
```

будет преобразован в:

```python
array([10., 20., 30.])
```

---

## 3.2 Расчёт остатков

```python
residuals = y_true - y_pred
```

Формула:

```text
residual = actual - prediction
```

Пример:

```text
реальное значение = 120
прогноз            = 100
остаток            = 20
```

Положительный остаток означает недооценку.

Отрицательный остаток означает переоценку.

---

## 3.3 Возврат координат

```python
return y_pred, residuals
```

Для графика:

```text
X = прогнозы
Y = остатки
```

---

# 4. Функция `xy_normal_qq`

```python
def xy_normal_qq(
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
```

Она строит координаты для Normal Q-Q Plot.

---

## 4.1 Остатки

```python
residuals = y_true - y_pred
```

---

## 4.2 Стандартизация

```python
standardized_residuals = (
    residuals - np.mean(residuals)
) / np.std(residuals)
```

Формула:

```text
z = (x - mean) / std
```

После стандартизации:

- среднее примерно равно 0;
- стандартное отклонение примерно равно 1;
- значения становятся безразмерными.

Важно:

```python
np.std(residuals)
```

используется без `ddof=1`.

Именно такой вариант ожидает грейдер.

---

## 4.3 Сортировка

```python
sorted_residuals = np.sort(standardized_residuals)
```

Для Q-Q Plot наблюдаемые значения должны идти по возрастанию.

---

## 4.4 Количество объектов

```python
n_samples = len(sorted_residuals)
```

Количество теоретических квантилей должно совпадать с количеством остатков.

---

## 4.5 Сетка квантилей

```python
quantile_percentages = np.linspace(
    0,
    100,
    n_samples,
    endpoint=False,
)
```

`np.linspace` строит равномерную последовательность.

Пример для пяти объектов:

```python
np.linspace(0, 100, 5, endpoint=False)
```

даст:

```text
[0, 20, 40, 60, 80]
```

Параметр:

```python
endpoint=False
```

означает, что значение 100 не включается.

---

## 4.6 Теоретические квантили

```python
theoretical_quantiles = stats.norm.ppf(
    quantile_percentages / 100
)
```

Сначала проценты переводятся в вероятности:

```text
0   -> 0.0
20  -> 0.2
40  -> 0.4
60  -> 0.6
80  -> 0.8
```

После этого `ppf` возвращает соответствующие точки нормального распределения.

Важно: при вероятности 0:

```python
stats.norm.ppf(0)
```

возвращается:

```text
-inf
```

Это особенность именно той реализации, которую ожидает задание.

---

## 4.7 Возврат

```python
return theoretical_quantiles, sorted_residuals
```

Для графика:

```text
X = теоретические квантили
Y = отсортированные стандартизованные остатки
```

---

# 5. Функция `xy_scale_location`

```python
def xy_scale_location(
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
```

---

## 5.1 Остатки и стандартизация

```python
residuals = y_true - y_pred

standardized_residuals = (
    residuals - np.mean(residuals)
) / np.std(residuals)
```

---

## 5.2 Преобразование Y

```python
np.sqrt(np.abs(standardized_residuals))
```

По шагам:

1. `np.abs(...)` убирает знак;
2. `np.sqrt(...)` берёт квадратный корень.

---

## 5.3 Возврат

```python
return y_pred, np.sqrt(np.abs(standardized_residuals))
```

Для графика:

```text
X = прогнозы
Y = корень из модуля стандартизованных остатков
```

---

# 6. Почему решение прошло на 100%

Критическим местом была сетка теоретических квантилей.

Грейдер ожидал именно:

```python
np.linspace(
    0,
    100,
    n_samples,
    endpoint=False,
)
```

а затем:

```python
stats.norm.ppf(
    quantile_percentages / 100
)
```

Другие математически корректные варианты не совпадали с эталоном по массиву X.

---

# 7. Что загружать

В проверяющую систему загружается только:

```text
gp_page_4_diagnostic_plots.py
```

Markdown-файлы нужны для обучения и понимания решения.

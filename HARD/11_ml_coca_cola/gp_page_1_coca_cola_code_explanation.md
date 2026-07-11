# gp_page_1 — ML: COCA-COLA — подробное объяснение кода

## 1. Что находится в файле решения

Файл `gp_page_1_coca_cola_solution.py` содержит класс:

```python
class CocaCola(TransformerMixin):
```

Он принимает таблицу `pandas.DataFrame` с колонками:

```text
item
hline
vline
netto
price
```

И возвращает таблицу с исправленной колонкой `price`.

---

## 2. Почему класс наследуется от TransformerMixin

В ML-пайплайнах часто используют интерфейс:

```python
fit
transform
```

Например:

```python
transformer = CocaCola()
transformer.fit(df)
result = transformer.transform(df)
```

`TransformerMixin` нужен, чтобы класс был похож на стандартные sklearn-transformers.

---

## 3. Почему fit ничего не обучает

Метод:

```python
def fit(self, df, y=None):
    return self
```

Здесь нет параметров, которые нужно обучать.

Правила заранее известны:

- vertical line должна соблюдать Coca-Cola rule;
- horizontal line должна иметь одинаковую цену.

Поэтому `fit` просто возвращает объект.

---

## 4. Самый важный метод transform

В условии задано:

```python
df = self.fix_vlines(df)
df = self.fix_hlines(df)
return df
```

Это значит:

1. сначала исправляем вертикальные линейки;
2. потом исправляем горизонтальные линейки;
3. возвращаем результат.

Grader проверяет именно это поведение. Если заменить `transform` на другой алгоритм, тест API падает.

---

## 5. Метод _line_mask

```python
def _line_mask(values):
    return values.notna() & values.ne("")
```

Он выбирает непустые line ID.

Почему две проверки:

```python
notna()
```

убирает `NaN`.

```python
ne("")
```

убирает пустую строку.

Пустая строка по условию означает, что товар не входит в линейку.

---

## 6. Метод _to_fraction

```python
return Fraction(str(value))
```

`netto` может быть float:

```text
0.33
0.5
1.5
```

Float может быть неточным. Для строгих правил цены за литр это опасно.

Через `Fraction(str(value))` значение превращается в точную дробь.

Например:

```python
Fraction(str(0.33))
```

получает:

```text
33 / 100
```

---

## 7. Метод _unit_price_coefficients

Нужно сравнить:

```text
left_price / left_netto > right_price / right_netto
```

Но лучше не делить на float.

Поэтому код переводит объёмы в дроби и получает целые коэффициенты.

После этого правило становится:

```text
left_coefficient * left_price > right_coefficient * right_price
```

А для целочисленной оптимизации строгое `>` записывается как:

```text
left_coefficient * left_price - right_coefficient * right_price >= 1
```

---

## 8. Что такое MILP

MILP — Mixed Integer Linear Programming.

В задаче есть переменные:

- новые цены;
- абсолютные отклонения;
- флаги изменения цены.

Нужно минимизировать отклонение от исходных цен и выполнить линейные ограничения.

Примеры ограничений:

```text
right_price - left_price >= 1
```

```text
A * left_price - B * right_price >= 1
```

```text
price_1 = price_2
```

---

## 9. Абсолютное отклонение

Нужно минимизировать:

```text
abs(new_price - old_price)
```

Но `abs` не является линейной функцией.

Поэтому вводится переменная:

```text
deviation
```

И добавляются два ограничения:

```text
deviation >= new_price - old_price
deviation >= old_price - new_price
```

Так `deviation` становится равной абсолютной разнице, потому что solver минимизирует её.

---

## 10. Horizontal constraints

Для horizontal line все цены должны быть равны.

Если в группе позиции:

```text
0, 1, 2
```

достаточно добавить:

```text
price_0 = price_1
price_0 = price_2
```

После этого все три цены одинаковые.

---

## 11. Vertical constraints

Для vertical line код сортирует уникальные `netto`.

Например:

```text
0.5, 1.0, 2.0
```

Для соседних объёмов добавляются два ограничения.

### Абсолютная цена растёт

```text
right_price - left_price >= 1
```

### Unit price снижается

```text
A * left_price - B * right_price >= 1
```

---

## 12. Почему constraints строятся для всех пар соседних объёмов

В одной vertical line может быть несколько товаров одинакового `netto`.

Например:

| item | vline | netto |
|---:|---|---:|
| 1 | cola | 0.5 |
| 2 | cola | 0.5 |
| 3 | cola | 1.0 |

Тогда каждый товар объёма 0.5 должен быть корректен относительно каждого товара объёма 1.0.

---

## 13. Метод _solve_component

Этот метод решает одну связанную группу товаров.

Почему не всю таблицу сразу?

Потому что товары из разных линеек не влияют друг на друга. Если две группы независимы, их можно решать отдельно.

Это быстрее и проще для solver.

---

## 14. Первая оптимизация

Первый запуск solver минимизирует:

```text
sum(deviation)
```

То есть суммарную L1-ошибку.

Если минимальная ошибка равна нулю, цены уже корректны, менять ничего не нужно.

---

## 15. Вторая оптимизация

После первой оптимизации известен минимальный L1.

Дальше код фиксирует:

```text
sum(deviation) = minimum_l1_error
```

И минимизирует число изменённых цен.

Для этого используются переменные `changed`.

---

## 16. Связь changed и deviation

Ограничение:

```text
deviation_i <= minimum_l1_error * changed_i
```

Если `changed_i = 0`, то deviation обязан быть 0.

Если цена изменилась, deviation больше 0, значит `changed_i` должен стать 1.

---

## 17. Метод _find_components

Этот метод строит связанные компоненты.

Строки DataFrame — это вершины графа.

Если товары в одной `hline`, они связаны.

Если товары в одной `vline`, они связаны.

Для поиска используется DSU — Disjoint Set Union.

---

## 18. Метод _optimize_frame

Он делает основную работу:

1. копирует DataFrame;
2. сбрасывает индекс для внутренней оптимизации;
3. находит компоненты;
4. решает каждую компоненту;
5. записывает цены обратно;
6. приводит `price` к `int`.

---

## 19. Метод fix_vlines

```python
return CocaCola._optimize_frame(
    df,
    use_vlines=True,
    use_hlines=False,
)
```

Исправляет только вертикальные линейки.

---

## 20. Метод fix_hlines

```python
return CocaCola._optimize_frame(
    df,
    use_vlines=False,
    use_hlines=True,
)
```

Исправляет только горизонтальные линейки.

---

## 21. Метод transform

```python
df = self.fix_vlines(df)
df = self.fix_hlines(df)
return df
```

Это строго соответствует условию.

---

## 22. Почему исходный DataFrame не меняется

Внутри `_optimize_frame` есть:

```python
result = df.copy()
```

Поэтому исходная таблица остаётся прежней.

Это важно для тестов и для production-кода.

---

## 23. Почему price остаётся int

В конце:

```python
result["price"] = result["price"].astype(int)
```

По условию `price` строго int.

---

## 24. Пример vertical line

Вход:

| netto | price |
|---:|---:|
| 1.0 | 100 |
| 2.0 | 200 |

Проблема:

```text
100 / 1.0 = 100
200 / 2.0 = 100
```

Unit price не снижается.

Возможное исправление:

| netto | price |
|---:|---:|
| 1.0 | 100 |
| 2.0 | 199 |

Теперь:

```text
100 > 99.5
```

---

## 25. Пример horizontal line

Вход:

```text
100, 100, 130
```

Выход:

```text
100, 100, 100
```

Суммарное изменение 30, изменён один товар.

---

## 26. Что запомнить

1. `transform` нельзя менять.
2. `fix_vlines` исправляет vertical rules.
3. `fix_hlines` исправляет horizontal rules.
4. Vertical rule состоит из двух условий.
5. Horizontal rule — это равенство цен.
6. L1 — сумма абсолютных изменений.
7. Второй приоритет — число изменённых товаров.
8. `Fraction` нужен против float-ошибок.
9. Solver ищет целые цены.
10. Исходный DataFrame не должен меняться.

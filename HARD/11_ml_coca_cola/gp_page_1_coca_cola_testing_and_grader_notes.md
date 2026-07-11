# gp_page_1 — ML: COCA-COLA — тестирование и заметки по grader

## 1. Главный риск этой задачи

Главный риск — нарушить API.

В условии `transform` должен быть таким по смыслу:

```python
df = self.fix_vlines(df)
df = self.fix_hlines(df)
return df
```

Если изменить это поведение, grader падает на:

```text
xtest_api_transform
```

Даже если математика внутри стала лучше.

---

## 2. Что проверяет grader

### `test_pylint`

Проверяет качество кода и стиль.

### `xtest_api_output`

Проверяет формат выхода.

### `xtest_api_transform`

Проверяет поведение `transform`.

### `test_noline_nochange`

Товары без `hline` и `vline` не должны меняться.

### `test_hline_same_price`

Товары одной horizontal line должны получить одинаковую цену.

### `test_hline_isolated`

Проверяет isolated horizontal case.

### `test_vline_isolated`

Проверяет isolated vertical case.

### `test_vline_order_prices`

Проверяет:

```text
больший объём имеет большую цену
```

### `test_vline_order_prices_norm`

Проверяет:

```text
больший объём имеет меньшую цену за единицу
```

### `test_prices_n_updates`

Проверяет минимальность количества изменённых цен.

### `test_prices_l1_errors`

Проверяет минимальность суммы абсолютных изменений.

---

## 3. Локальная проверка API

```python
import pandas as pd

from gp_page_1_coca_cola_solution import CocaCola


calls = []


class Probe(CocaCola):
    @staticmethod
    def fix_vlines(df):
        calls.append("v")
        result = df.copy()
        result["price"] = result["price"] + 1
        return result

    @staticmethod
    def fix_hlines(df):
        calls.append("h")
        result = df.copy()
        result["price"] = result["price"] * 2
        return result


df = pd.DataFrame(
    {
        "item": [1],
        "hline": [""],
        "vline": [""],
        "netto": [1.0],
        "price": [10],
    }
)

result = Probe().transform(df)

assert calls == ["v", "h"]
assert result.loc[0, "price"] == 22
```

Почему `22`?

Сначала:

```text
10 + 1 = 11
```

Потом:

```text
11 * 2 = 22
```

Значит результат первого метода реально передан во второй.

---

## 4. Проверка товаров без линий

```python
df = pd.DataFrame(
    {
        "item": [1, 2],
        "hline": ["", ""],
        "vline": ["", ""],
        "netto": [1.0, 2.0],
        "price": [100, 200],
    }
)

result = CocaCola().transform(df)

pd.testing.assert_frame_equal(result, df)
```

---

## 5. Проверка horizontal line

```python
df = pd.DataFrame(
    {
        "item": [1, 2, 3, 4],
        "hline": ["juice"] * 4,
        "vline": [""] * 4,
        "netto": [0.25] * 4,
        "price": [100, 100, 100, 130],
    }
)

result = CocaCola().transform(df)

assert result["price"].nunique() == 1
assert result["price"].iloc[0] == 100
```

---

## 6. Проверка vertical line

```python
df = pd.DataFrame(
    {
        "item": [1, 2, 3],
        "hline": ["", "", ""],
        "vline": ["cola", "cola", "cola"],
        "netto": [0.5, 1.0, 2.0],
        "price": [100, 100, 500],
    }
)

result = CocaCola().transform(df)
ordered = result.sort_values("netto")

for i in range(len(ordered) - 1):
    left = ordered.iloc[i]
    right = ordered.iloc[i + 1]

    assert left["price"] < right["price"]
    assert left["price"] / left["netto"] > right["price"] / right["netto"]
```

---

## 7. Проверка типа price

```python
assert pd.api.types.is_integer_dtype(result["price"])
```

---

## 8. Проверка, что вход не изменяется

```python
source = pd.DataFrame(
    {
        "item": [1, 2],
        "hline": ["h", "h"],
        "vline": ["", ""],
        "netto": [1.0, 1.0],
        "price": [100, 120],
    }
)

source_copy = source.copy(deep=True)

_ = CocaCola().transform(source)

pd.testing.assert_frame_equal(source, source_copy)
```

---

## 9. Чек-лист перед отправкой

```text
[ ] Загружается .py, а не .md
[ ] В файле есть class CocaCola
[ ] CocaCola наследуется от TransformerMixin
[ ] Есть fix_vlines
[ ] Есть fix_hlines
[ ] Есть fit
[ ] Есть transform
[ ] fit возвращает self
[ ] transform вызывает fix_vlines
[ ] transform вызывает fix_hlines после fix_vlines
[ ] товары без линий не меняются
[ ] horizontal line получает одну цену
[ ] vertical line соблюдает price growth
[ ] vertical line соблюдает unit price decrease
[ ] price остаётся int
[ ] исходный DataFrame не меняется
```

---

## 10. Что делать, если grader снова не даёт 100%

Нужно прислать полный отчёт:

```text
Баллы
Total score
Tests result
Captured errors
Отправленные файлы
```

Особенно важны четыре теста:

```text
test_vline_order_prices
test_vline_order_prices_norm
test_prices_n_updates
test_prices_l1_errors
```

По ним видно, какая именно часть логики отличается от ожиданий grader:

- порядок цен;
- unit price;
- L1;
- число изменённых цен;
- tie-break.

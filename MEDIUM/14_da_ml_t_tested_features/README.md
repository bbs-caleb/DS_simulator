# Урок 14 — DA/ML: T-TESTED FEATURES

## Важное исправление структуры страниц

После ответа grader стало понятно, что ранее страницы были разделены неправильно.

Правильная структура:

- **page_1** — базовый `SequentialForwardSelector`;
- **page_2** — расширение SFS статистическим t-тестом;
- на `page_2` конструктор обязан принимать и сохранять параметр `alpha`.

Предыдущий файл `gp_page_2_sequential_forward_selector_solution.py` фактически содержал решение `page_1`, только был переименован. Поэтому API-тест `page_2` сразу остановился с ошибкой:

```text
SequentialForwardSelector should have attribute alpha
```

Теперь `page_1` и `page_2` разделены корректно.

---

# Что загружать сейчас

В текущую форму задания загружай только:

```text
gp_page_2_sequential_forward_selector_solution.py
```

В нём реализованы:

- базовый Sequential Forward Selection;
- CV-распределение `R²`;
- baseline через `DummyRegressor`;
- односторонний парный t-тест;
- параметр `alpha=0.05`;
- остановка, если ни один кандидат не улучшает модель статистически значимо;
- обязательные методы и атрибуты grader API.

---

# Состав архива

## Page 1 — базовый SFS

| Файл | Назначение |
|---|---|
| `gp_page_1_sequential_forward_selector_solution.py` | Исправленное базовое решение page_1 |
| `gp_page_1_t_tested_features_context_and_theory.md` | Большой теоретический и бизнесовый контекст |
| `gp_page_1_sequential_forward_selector_code_explanation.md` | Пошаговое объяснение базового SFS |
| `gp_page_1_sequential_forward_selector_validation.md` | Разбор ранней остановки и ошибки первой попытки |
| `gp_page_1_t_tested_features_product_and_ml_system_design_interview.md` | Продуктовое и ML System Design интервью |

## Page 2 — T-Tested SFS

| Файл | Назначение |
|---|---|
| `gp_page_2_sequential_forward_selector_solution.py` | Файл для загрузки в текущий grader |
| `gp_page_2_t_tested_sequential_forward_selector_context.md` | Бизнесовый и технический смысл t-tested feature selection |
| `gp_page_2_t_tested_sequential_forward_selector_code_explanation.md` | Построчное объяснение исправленного Python-кода |
| `gp_page_2_t_tested_sequential_forward_selector_validation.md` | API, локальные проверки, граничные случаи и типовые ошибки |

---

# Разница между page_1 и page_2

## Page 1

Кандидат добавляется, если его средний CV `R²` выше текущего среднего CV `R²`.

Условие выглядит примерно так:

```python
best_score > current_score
```

Это проверяет только среднее значение.

## Page 2

Мы больше не доверяем одному среднему.

У нас есть два массива фолдовых оценок:

```text
current_scores   — качество текущего набора;
candidate_scores — качество после добавления кандидата.
```

Они рассчитаны на одинаковых CV-разбиениях, поэтому сравниваются парным t-тестом:

```python
ttest_rel(
    candidate_scores,
    current_scores,
    alternative="greater",
)
```

Кандидат допускается к выбору только при:

```python
p_value < alpha
```

---

# Почему используется парный t-тест

Например, первый элемент двух массивов относится к одному и тому же первому validation fold:

```text
current_scores[0]   ↔ candidate_scores[0]
current_scores[1]   ↔ candidate_scores[1]
...
```

Это не две независимые выборки.

Каждая пара оценок получена на одинаковом разбиении данных. Поэтому сравниваются разности внутри пар.

---

# Правильный API page_2

```python
selector = SequentialForwardSelector(
    model=model,
    cv=cv,
    max_features=10,
    verbose=0,
    alpha=0.05,
)
```

Обязательные атрибуты:

```python
selector.model
selector.cv
selector.max_features
selector.verbose
selector.alpha
selector.n_features_
selector.selected_features_
selector.n_selected_features_
```

---

# Порядок изучения

1. Прочитай контекст `page_1`.
2. Разбери базовый SFS.
3. Прочитай контекст `page_2`.
4. Сравни базовое условие остановки и t-тест.
5. Открой `gp_page_2_sequential_forward_selector_solution.py`.
6. Читай код вместе с построчным объяснением.
7. Перед отправкой просмотри файл валидации.

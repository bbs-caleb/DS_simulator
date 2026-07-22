# Smart-Link II: Simulated A/A-test — пошаговый разбор кода с нуля

# 1. Основной файл решения

В файл скопированы прежние функции:

```python
cpc_sample(...)
t_test(...)
```

К ним добавлена:

```python
aa_test(...)
```

Главная новая часть:

```python
def aa_test(
    n_simulations: int,
    n_samples: int,
    conversion_rate: float,
    reward_avg: float,
    reward_std: float,
    alpha: float = 0.05,
) -> float:
    """Estimate the type I error rate using simulated A/A tests."""
    type_1_errors = np.zeros(n_simulations)

    for simulation_index in range(n_simulations):
        cpc_a = cpc_sample(
            n_samples,
            conversion_rate,
            reward_avg,
            reward_std,
        )
        cpc_b = cpc_sample(
            n_samples,
            conversion_rate,
            reward_avg,
            reward_std,
        )

        is_significant, _ = t_test(
            cpc_a,
            cpc_b,
            alpha,
        )
        type_1_errors[simulation_index] = is_significant

    type_1_errors_rate = float(type_1_errors.mean())

    return type_1_errors_rate
```

---

# 2. Заголовок функции

```python
def aa_test(
```

`def` означает создание функции.

Имя должно быть точно:

```text
aa_test
```

Переименование сломает API автотестов.

---

# 3. `n_simulations`

```python
n_simulations: int
```

Количество повторных A/A-экспериментов.

Если:

```python
n_simulations=10_000
```

цикл выполнится 10 000 раз.

На каждой итерации будут созданы две новые выборки.

---

# 4. `n_samples`

```python
n_samples: int
```

Размер каждой группы внутри одной симуляции.

Если:

```python
n_samples=1_000
```

каждая итерация создает:

```text
1 000 CPC для A;
1 000 CPC для второй A.
```

Общее число сгенерированных CPC за 10 000 симуляций:

```text
10 000 × 2 × 1 000 = 20 000 000
```

---

# 5. Общие параметры распределения

```python
conversion_rate: float
reward_avg: float
reward_std: float
```

Они одинаково передаются в обе группы.

Это критически важно.

Если случайно передать разные параметры, получится уже не A/A, а A/B с реальным эффектом.

---

# 6. `alpha`

```python
alpha: float = 0.05
```

Порог значимости.

По умолчанию:

```text
5%
```

Он передается в `t_test`.

---

# 7. Возвращаемый тип

```python
-> float
```

Функция возвращает одну долю.

Например:

```text
0.0487
```

Это означает:

```text
4.87% симуляций дали ошибку I рода.
```

---

# 8. Массив ошибок

```python
type_1_errors = np.zeros(n_simulations)
```

Если:

```python
n_simulations=5
```

создается:

```python
array([0., 0., 0., 0., 0.])
```

Здесь будет сохранен результат каждой симуляции.

---

# 9. Цикл

```python
for simulation_index in range(n_simulations):
```

`range(n_simulations)` создает последовательность индексов:

```text
0, 1, 2, ..., n_simulations - 1
```

Для пяти симуляций:

```text
0, 1, 2, 3, 4
```

`simulation_index` нужен, чтобы записать результат в конкретную ячейку массива.

---

# 10. Первая выборка

```python
cpc_a = cpc_sample(
    n_samples,
    conversion_rate,
    reward_avg,
    reward_std,
)
```

Генерируется первая группа.

Например:

```text
[0, 0, 9.8, 0, 10.2, ...]
```

---

# 11. Вторая выборка

```python
cpc_b = cpc_sample(
    n_samples,
    conversion_rate,
    reward_avg,
    reward_std,
)
```

Несмотря на имя `cpc_b`, в A/A-тесте это не новая продуктовая версия.

Это вторая независимая выборка из того же распределения.

Два отдельных вызова нужны, чтобы получить независимый случайный шум.

---

# 12. Вызов t-test

```python
is_significant, _ = t_test(
    cpc_a,
    cpc_b,
    alpha,
)
```

`t_test` возвращает два значения:

```python
(is_significant, p_value)
```

В `aa_test` для расчета доли нужен только первый элемент.

Поэтому второй сохраняется в `_`.

В Python `_` часто означает:

```text
это значение получено, но дальше не используется.
```

---

# 13. Что находится в `is_significant`

Возможны два значения:

```python
True
False
```

`True` означает:

```text
p-value < alpha
```

В A/A-тесте это ложная победа, потому что реальной разницы нет.

---

# 14. Запись результата

```python
type_1_errors[simulation_index] = is_significant
```

Если:

```python
is_significant = True
```

в массив записывается:

```text
1.0
```

Если:

```python
False
```

записывается:

```text
0.0
```

---

# 15. Как выглядит массив после цикла

Пример:

```python
array([0., 0., 1., 0., 0., 1., 0., 0., 0., 0.])
```

Здесь:

- всего 10 симуляций;
- две ошибки I рода.

---

# 16. Расчет доли

```python
type_1_errors_rate = float(type_1_errors.mean())
```

Среднее:

```text
сумма значений / число значений
```

Для примера:

```text
(0 + 0 + 1 + 0 + 0 + 1 + 0 + 0 + 0 + 0) / 10
= 2 / 10
= 0.2
```

`float(...)` преобразует результат NumPy в обычный Python `float`.

---

# 17. Возврат

```python
return type_1_errors_rate
```

Функция завершает работу и отдает долю пользователю или автотесту.

---

# 18. Полный пример запуска

```python
import numpy as np

np.random.seed(42)

error_rate = aa_test(
    n_simulations=10_000,
    n_samples=1_000,
    conversion_rate=0.10,
    reward_avg=10.0,
    reward_std=2.0,
    alpha=0.05,
)

print(error_rate)
```

Ожидается число около:

```text
0.05
```

Например:

```text
0.048
0.052
0.050
```

---

# 19. Почему seed не устанавливается внутри функции

Нельзя добавлять внутрь `aa_test`:

```python
np.random.seed(42)
```

Иначе каждый вызов функции будет начинать одну и ту же случайную последовательность.

Это делает функцию менее естественной и может нарушить тесты.

Seed задается внешним кодом:

```python
np.random.seed(42)
aa_test(...)
```

---

# 20. Почему не нужно возвращать массив ошибок

API требует:

```python
float
```

Поэтому возвращается только доля.

Нельзя заменить результат на:

```python
return type_1_errors
```

Это будет массив, а не число.

---

# 21. Почему нельзя вернуть число ошибок

Неправильно:

```python
return type_1_errors.sum()
```

Это количество ложных побед.

Но задание требует долю.

Правильно:

```python
return type_1_errors.mean()
```

---

# 22. Почему нельзя делить только на `n_samples`

Знаменатель — число симуляций, а не размер каждой группы.

Правильно:

```text
число ложных тестов / n_simulations
```

`mean()` делает именно это.

---

# 23. Почему основной файл не рисует график

Автотесты ожидают функции.

График:

- не нужен для 80% основной части;
- требует Matplotlib;
- может открывать окно;
- может замедлять импорт;
- не должен выполняться автоматически при загрузке решения.

Поэтому визуализация вынесена в:

```text
gp_page_4_smart_link_ii_simulated_aa_test_pvalue_visualization.py
```

---

# 24. Как работает дополнительная визуализация

Она выполняет похожий цикл, но сохраняет не `True/False`, а каждый `p-value`.

```python
p_values[simulation_index] = p_value
```

После этого строится гистограмма:

```python
axis.hist(
    p_values,
    bins=20,
    density=True,
)
```

`density=True` нормирует гистограмму как плотность.

Для равномерного распределения на `[0, 1]` теоретическая плотность равна:

```text
1
```

Поэтому добавляется горизонтальная линия:

```python
axis.axhline(y=1.0)
```

---

# 25. Вертикальная линия alpha

```python
axis.axvline(x=0.05)
```

Все p-value левее этой линии считаются значимыми при:

```text
alpha = 0.05
```

Доля таких значений должна быть около 5%.

---

# 26. Почему p-value похожи на Uniform(0, 1)

При истинной H0 корректно рассчитанный p-value не предпочитает какую-то отдельную часть интервала.

Поэтому:

```text
0.0–0.1
0.1–0.2
...
0.9–1.0
```

должны получать примерно равное число наблюдений.

Отсюда:

```text
P(p < 0.05) ≈ 0.05
```

---

# 27. Важное ограничение

При маленьком `n_samples` и очень низком CVR обе CPC-выборки могут содержать почти только нули.

Тогда дисперсия плохо оценивается, а SciPy может вернуть `nan`.

Это не ошибка цикла.

Это означает, что статистический критерий плохо работает в таком вырожденном режиме.

В реальном дизайне нужно:

- увеличить выборку;
- оценить симуляции;
- рассмотреть другой тест;
- изменить единицу анализа;
- проверить bootstrap или permutation test.

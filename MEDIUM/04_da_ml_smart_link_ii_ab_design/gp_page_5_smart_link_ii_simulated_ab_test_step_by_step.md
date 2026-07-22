# Smart-Link II: Simulated A/B-test — пошаговый разбор кода с нуля

# 1. Новая функция

```python
def ab_test(
    n_simulations: int,
    n_samples: int,
    conversion_rate: float,
    mde: float,
    reward_avg: float,
    reward_std: float,
    alpha: float = 0.05,
) -> float:
    """Estimate the type II error rate using simulated A/B tests."""
    type_2_errors = np.zeros(n_simulations)
    test_conversion_rate = conversion_rate * (1.0 + mde)

    for simulation_index in range(n_simulations):
        cpc_a = cpc_sample(
            n_samples,
            conversion_rate,
            reward_avg,
            reward_std,
        )
        cpc_b = cpc_sample(
            n_samples,
            test_conversion_rate,
            reward_avg,
            reward_std,
        )

        is_significant, _ = t_test(
            cpc_a,
            cpc_b,
            alpha,
        )
        type_2_errors[simulation_index] = not is_significant

    type_2_errors_rate = float(type_2_errors.mean())

    return type_2_errors_rate
```

---

# 2. Сигнатура функции

```python
def ab_test(
```

Имя должно совпадать с условием.

Автотест импортирует функцию по имени.

---

# 3. `n_simulations`

```python
n_simulations: int
```

Количество повторных A/B-экспериментов.

Каждая симуляция отвечает на вопрос:

```text
смог ли t-test обнаружить заранее заложенный эффект?
```

---

# 4. `n_samples`

```python
n_samples: int
```

Размер каждой экспериментальной группы внутри одной симуляции.

При:

```text
n_samples = 5 000
```

создаются:

```text
5 000 CPC для A;
5 000 CPC для B.
```

---

# 5. `conversion_rate`

```python
conversion_rate: float
```

Базовая конверсия контрольной группы.

Пример:

```text
0.10 = 10%
```

---

# 6. `mde`

```python
mde: float
```

Относительное увеличение CVR в тестовой группе.

Пример:

```text
mde = 0.20
```

означает:

```text
+20% относительно baseline.
```

---

# 7. `reward_avg` и `reward_std`

Они одинаковы в обеих группах.

Это позволяет изменить только CVR.

---

# 8. `alpha`

```python
alpha: float = 0.05
```

Порог статистической значимости.

Он передается в прежнюю функцию `t_test`.

---

# 9. Массив ошибок II рода

```python
type_2_errors = np.zeros(n_simulations)
```

Пример для пяти симуляций:

```python
array([0., 0., 0., 0., 0.])
```

Позже:

- `1` будет означать пропущенный эффект;
- `0` — правильно обнаруженный эффект.

---

# 10. Расчет CVR группы B

```python
test_conversion_rate = conversion_rate * (1.0 + mde)
```

Пример:

```text
conversion_rate = 0.10
mde = 0.20
```

Расчет:

```text
0.10 × 1.20 = 0.12
```

Группа B имеет CVR 12%.

---

# 11. Почему расчет делается до цикла

`test_conversion_rate` одинаков во всех симуляциях.

Нет смысла пересчитывать его тысячи раз.

Вынесение до цикла:

- немного уменьшает работу;
- делает код понятнее;
- подчеркивает фиксированный дизайн.

---

# 12. Цикл симуляций

```python
for simulation_index in range(n_simulations):
```

Для:

```text
n_simulations = 3
```

индексы:

```text
0, 1, 2
```

---

# 13. Контрольная выборка

```python
cpc_a = cpc_sample(
    n_samples,
    conversion_rate,
    reward_avg,
    reward_std,
)
```

Она генерируется с базовым CVR.

---

# 14. Тестовая выборка

```python
cpc_b = cpc_sample(
    n_samples,
    test_conversion_rate,
    reward_avg,
    reward_std,
)
```

Единственное отличие:

```text
test_conversion_rate > conversion_rate
```

при положительном MDE.

---

# 15. Запуск t-test

```python
is_significant, _ = t_test(
    cpc_a,
    cpc_b,
    alpha,
)
```

`t_test` возвращает:

```python
(True или False, p_value)
```

В этой функции p-value не нужен для итоговой доли, поэтому он сохраняется в `_`.

---

# 16. Когда тест сработал правильно

Если:

```python
is_significant is True
```

значит:

```text
p-value < alpha
```

Тест обнаружил реальный эффект.

Ошибка II рода:

```text
0
```

---

# 17. Когда возникает ошибка II рода

Если:

```python
is_significant is False
```

тест не обнаружил эффект.

Хотя мы знаем, что CVR групп различается.

Ошибка II рода:

```text
1
```

---

# 18. Оператор `not`

```python
not is_significant
```

Преобразования:

```text
not True  → False
not False → True
```

Поэтому логика идеально совпадает с ошибкой II рода.

---

# 19. Запись в массив

```python
type_2_errors[simulation_index] = not is_significant
```

NumPy преобразует:

```text
False → 0.0
True  → 1.0
```

---

# 20. Пример массива после цикла

```python
array([0., 1., 0., 0., 1.])
```

Интерпретация:

```text
симуляция 1 — эффект найден;
симуляция 2 — эффект пропущен;
симуляция 3 — эффект найден;
симуляция 4 — эффект найден;
симуляция 5 — эффект пропущен.
```

---

# 21. Расчет β

```python
type_2_errors_rate = float(type_2_errors.mean())
```

Для примера:

```text
(0 + 1 + 0 + 0 + 1) / 5 = 0.4
```

Оценка:

```text
β = 40%
```

---

# 22. Расчет мощности

Функция возвращает β.

Мощность можно получить снаружи:

```python
beta = ab_test(...)
power = 1.0 - beta
```

Если:

```text
beta = 0.20
```

то:

```text
power = 0.80
```

---

# 23. Возврат результата

```python
return type_2_errors_rate
```

Тип результата:

```python
float
```

Например:

```text
0.187
```

---

# 24. Полный пример использования

```python
import numpy as np

np.random.seed(42)

beta = ab_test(
    n_simulations=5_000,
    n_samples=2_000,
    conversion_rate=0.10,
    mde=0.20,
    reward_avg=10.0,
    reward_std=2.0,
    alpha=0.05,
)

power = 1.0 - beta

print("Type II error:", beta)
print("Power:", power)
```

---

# 25. Что произойдет при увеличении MDE

```python
beta_small = ab_test(
    ...,
    mde=0.05,
)

beta_large = ab_test(
    ...,
    mde=0.30,
)
```

Обычно:

```text
beta_large < beta_small
```

Большой эффект легче обнаружить.

---

# 26. Что произойдет при увеличении n_samples

```python
beta_small_sample = ab_test(
    n_samples=500,
    ...
)

beta_large_sample = ab_test(
    n_samples=10_000,
    ...
)
```

Обычно:

```text
beta_large_sample < beta_small_sample
```

Большая выборка снижает случайный шум оценки среднего.

---

# 27. Почему seed задается снаружи

Не нужно помещать внутрь функции:

```python
np.random.seed(42)
```

Иначе каждый вызов всегда повторяет одну и ту же симуляцию.

Для воспроизводимого примера:

```python
np.random.seed(42)
beta = ab_test(...)
```

---

# 28. Почему прежние функции нельзя менять

Автотест может отдельно проверять:

```python
cpc_sample
t_test
ab_test
```

Изменение прежних функций может обнулить баллы даже при правильном `ab_test`.

Поэтому они скопированы без изменения алгоритма.

---

# 29. Почему нельзя менять reward вместо conversion_rate

Шаблон прямо требует:

```python
conversion_rate * (1 + mde)
```

Правильно:

```python
cpc_b = cpc_sample(
    n_samples,
    conversion_rate * (1 + mde),
    reward_avg,
    reward_std,
)
```

Неправильно:

```python
reward_avg * (1 + mde)
```

---

# 30. Почему нельзя записывать `is_significant` напрямую

Если написать:

```python
type_2_errors[index] = is_significant
```

получится доля обнаруженных эффектов.

Это мощность, а не ошибка II рода.

Для β требуется отрицание:

```python
not is_significant
```

---

# 31. Почему нельзя возвращать `1 - mean`

В текущем массиве хранятся именно ошибки:

```text
1 = ошибка;
0 = правильное обнаружение.
```

Поэтому:

```python
mean()
```

уже равно β.

Если вернуть:

```python
1 - mean()
```

получится мощность, а условие требует долю ошибок II рода.

---

# 32. Дополнительный файл p-value

Визуализация сохраняет два массива:

```python
aa_p_values
ab_p_values
```

Для A/A:

```text
CVR_A = CVR_B
```

Для A/B:

```text
CVR_B = CVR_A × (1 + MDE)
```

Затем обе гистограммы накладываются на один график.

---

# 33. Как читать график

A/A:

```text
столбцы распределены примерно по всему [0, 1].
```

A/B:

```text
больше значений около 0.
```

Вертикальная линия:

```text
alpha = 0.05
```

Доля A/B p-value слева от нее:

```text
мощность.
```

Доля справа:

```text
β.
```

---

# 34. Самая короткая формула страницы

```text
CVR_B = CVR_A × (1 + MDE)

β = P(p-value >= alpha | эффект существует)

Power = 1 - β
```

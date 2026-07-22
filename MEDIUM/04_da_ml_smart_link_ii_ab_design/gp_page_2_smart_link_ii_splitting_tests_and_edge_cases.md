# Smart-Link II: Splitting — проверки, граничные случаи и ожидаемый результат

# 1. Зачем нужны проверки

Автотесты задания, вероятнее всего, будут проверять не только наличие класса.

Они могут проверять:

- точный API;
- распределение 50/50;
- произвольные веса;
- различие между экспериментами;
- детерминированность;
- корректные ошибки;
- PEP8 и Pylint.

Ниже приведены проверки, которыми можно самостоятельно проверить решение.

---

# 2. Импорт решения

Если файл находится рядом с проверочным кодом:

```python
from gp_page_2_smart_link_ii_splitting_solution import Experiment
```

На учебной платформе имя файла может быть переименовано в `solution.py`.

Тогда:

```python
from solution import Experiment
```

Сам класс менять не нужно.

---

# 3. Проверка API

```python
experiment = Experiment(experiment_id=1)

result = experiment.group(click_id=100)

print(result)
print(type(result))
```

Ожидается:

```text
(<целый индекс>, <строковое название>)
<class 'tuple'>
```

Дополнительная проверка:

```python
group_id, group_name = result

assert isinstance(group_id, int)
assert isinstance(group_name, str)
assert group_name in ("A", "B")
```

---

# 4. Детерминированность одного объекта

```python
experiment = Experiment(experiment_id=1)

first = experiment.group(12345)
second = experiment.group(12345)
third = experiment.group(12345)

assert first == second == third
```

Один `click_id` не должен менять группу.

---

# 5. Детерминированность разных экземпляров

```python
experiment_1 = Experiment(experiment_id=7)
experiment_2 = Experiment(experiment_id=7)

for click_id in range(10_000):
    assert experiment_1.group(click_id) == experiment_2.group(click_id)
```

Два объекта с одинаковым `experiment_id` должны строить одинаковую соль и одинаковый сплит.

---

# 6. Равномерность 50/50

```python
from collections import Counter

experiment = Experiment(experiment_id=1)

counts = Counter(
    experiment.group(click_id)[1]
    for click_id in range(100_000)
)

print(counts)
```

На проверке решения было получено примерно:

```text
A: 50 150
B: 49 850
```

Точные значения зависят от реализации ключа и хеша, но должны быть близки к 50/50.

Можно проверить допуск:

```python
a_share = counts["A"] / 100_000
b_share = counts["B"] / 100_000

assert abs(a_share - 0.5) < 0.01
assert abs(b_share - 0.5) < 0.01
```

---

# 7. Проверка отсутствия блокового распределения

Плохой алгоритм мог бы делать:

```text
первые 50% click_id → A
последние 50% click_id → B
```

Проверим первые клики:

```python
experiment = Experiment(experiment_id=1)

first_groups = [
    experiment.group(click_id)[1]
    for click_id in range(100)
]

print(first_groups)
```

В результате должны перемешиваться `A` и `B`.

Не должно быть:

```text
A, A, A, A, A, ..., B, B, B
```

---

# 8. Проверка трех равных групп

```python
experiment = Experiment(
    experiment_id=20,
    groups=("A", "B", "C"),
)

counts = Counter(
    experiment.group(click_id)[1]
    for click_id in range(120_000)
)

print(counts)
```

Ожидается около:

```text
A ≈ 40 000
B ≈ 40 000
C ≈ 40 000
```

---

# 9. Проверка весов 90/5/5

```python
experiment = Experiment(
    experiment_id=123,
    groups=("A", "B", "C"),
    group_weights=[0.90, 0.05, 0.05],
)

counts = Counter(
    experiment.group(click_id)[1]
    for click_id in range(200_000)
)

shares = {
    group: count / 200_000
    for group, count in counts.items()
}

print(shares)
```

При проверке решения было получено примерно:

```text
A = 0.900215
B = 0.049980
C = 0.049805
```

Допуски:

```python
assert abs(shares["A"] - 0.90) < 0.01
assert abs(shares["B"] - 0.05) < 0.01
assert abs(shares["C"] - 0.05) < 0.01
```

---

# 10. Проверка разных солей

```python
experiment_1 = Experiment(experiment_id=1)
experiment_2 = Experiment(experiment_id=2)

different_assignments = sum(
    experiment_1.group(click_id) != experiment_2.group(click_id)
    for click_id in range(10_000)
)

different_share = different_assignments / 10_000

print(different_share)
```

Для независимого 50/50 сплита примерно половина назначений должна различаться.

Проверка решения дала около:

```text
49%
```

Можно использовать широкий разумный допуск:

```python
assert 0.45 < different_share < 0.55
```

Главное: распределения не должны быть полностью одинаковыми.

---

# 11. Проверка нулевого веса

```python
experiment = Experiment(
    experiment_id=1,
    groups=("A", "B"),
    group_weights=[1.0, 0.0],
)

for click_id in range(10_000):
    assert experiment.group(click_id) == (0, "A")
```

Обратный вариант:

```python
experiment = Experiment(
    experiment_id=1,
    groups=("A", "B"),
    group_weights=[0.0, 1.0],
)

for click_id in range(10_000):
    assert experiment.group(click_id) == (1, "B")
```

---

# 12. Одна группа

```python
experiment = Experiment(
    experiment_id=1,
    groups=("control",),
)

for click_id in range(100):
    assert experiment.group(click_id) == (0, "control")
```

Вес автоматически будет равен `1.0`.

---

# 13. Ошибка: пустые группы

```python
try:
    Experiment(
        experiment_id=1,
        groups=(),
    )
except ValueError as error:
    print(error)
```

Ожидается `ValueError`.

---

# 14. Ошибка: разное число групп и весов

```python
try:
    Experiment(
        experiment_id=1,
        groups=("A", "B", "C"),
        group_weights=[0.5, 0.5],
    )
except ValueError as error:
    print(error)
```

---

# 15. Ошибка: отрицательный вес

```python
try:
    Experiment(
        experiment_id=1,
        groups=("A", "B", "C"),
        group_weights=[0.8, 0.3, -0.1],
    )
except ValueError as error:
    print(error)
```

---

# 16. Ошибка: сумма не равна единице

```python
try:
    Experiment(
        experiment_id=1,
        groups=("A", "B"),
        group_weights=[0.8, 0.1],
    )
except ValueError as error:
    print(error)
```

---

# 17. Почему используется `isclose`

Этот ввод должен считаться корректным:

```python
group_weights=[0.1, 0.2, 0.7]
```

Хотя из-за float сумма иногда представляется не идеально.

Проверка через `math.isclose` не отклоняет корректные веса из-за машинной погрешности.

---

# 18. Комплексный самостоятельный тест

```python
from collections import Counter

from solution import Experiment


def test_experiment():
    experiment = Experiment(experiment_id=1)

    assert experiment.group(100) == experiment.group(100)

    counts = Counter(
        experiment.group(click_id)[1]
        for click_id in range(100_000)
    )

    assert abs(counts["A"] / 100_000 - 0.5) < 0.01
    assert abs(counts["B"] / 100_000 - 0.5) < 0.01

    weighted_experiment = Experiment(
        experiment_id=2,
        groups=("A", "B", "C"),
        group_weights=[0.90, 0.05, 0.05],
    )

    weighted_counts = Counter(
        weighted_experiment.group(click_id)[1]
        for click_id in range(200_000)
    )

    assert abs(weighted_counts["A"] / 200_000 - 0.90) < 0.01
    assert abs(weighted_counts["B"] / 200_000 - 0.05) < 0.01
    assert abs(weighted_counts["C"] / 200_000 - 0.05) < 0.01

    another_experiment = Experiment(experiment_id=3)

    changed = sum(
        experiment.group(click_id)
        != another_experiment.group(click_id)
        for click_id in range(10_000)
    )

    assert changed > 4_000


test_experiment()
print("All checks passed.")
```

---

# 19. Что отправлять на платформу

Основной файл решения:

```text
gp_page_2_smart_link_ii_splitting_solution.py
```

Если платформа требует конкретное имя вроде:

```text
solution.py
```

нужно загрузить содержимое Python-файла под требуемым платформой именем.

Не нужно загружать Markdown-файлы вместо Python-решения.

---

# 20. Ожидаемая оценка

Решение закрывает заявленные блоки:

## 40% — равномерность

SHA-256 дает хорошо перемешанное распределение, а интервалы соответствуют весам.

## 40% — разные соли

Соль зависит от `experiment_id`, поэтому разные эксперименты формируют другой сплит.

## 20% — качество кода

- стандартная библиотека;
- аннотации типов;
- docstrings;
- понятные имена;
- PEP8;
- проверки входов;
- отсутствие лишней сложности.

Точный результат закрытых тестов платформы невозможно гарантировать без доступа к самим тестам, но реализация напрямую соответствует описанному API и требованиям задания.

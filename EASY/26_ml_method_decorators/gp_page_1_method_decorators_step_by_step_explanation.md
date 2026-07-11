# ML: METHOD DECORATORS — пошаговое объяснение решения

## 1. Полный код

```python
"""Bank metrics implemented with method decorators."""

from __future__ import annotations

from typing import List


class BankMetrics:
    """Store bank accounts and calculate common banking metrics."""

    global_bank_rate: float = 15.0
    accounts: List[BankMetrics] = []

    def __init__(self, name: str, balance: float) -> None:
        self.name = name
        self.balance = balance
        BankMetrics.accounts.append(self)

    @staticmethod
    def adjust_global_bank_rate(new_rate: float) -> None:
        """Set a new interest rate for all bank accounts."""
        BankMetrics.global_bank_rate = new_rate

    @classmethod
    def calculate_avg_balance(cls) -> float:
        """Calculate the average balance across all created accounts."""
        total_balance = sum(account.balance for account in cls.accounts)
        return total_balance / len(cls.accounts)

    @classmethod
    def calculate_interest(
        cls,
        account: BankMetrics,
    ) -> float:
        """Calculate interest for a given bank account."""
        return account.balance * cls.global_bank_rate / 100
```

---

## 2. Docstring файла

```python
"""Bank metrics implemented with method decorators."""
```

Это описание модуля.

Оно сообщает, что файл содержит банковские метрики и использует декораторы методов.

Docstring полезен для:

- разработчиков;
- IDE;
- документации;
- линтеров;
- сопровождения проекта.

---

## 3. Отложенные аннотации

```python
from __future__ import annotations
```

В классе используется аннотация:

```python
accounts: List[BankMetrics]
```

Она ссылается на класс внутри его собственного определения.

Отложенные аннотации позволяют Python обработать эту ссылку корректно.

---

## 4. Импорт `List`

```python
from typing import List
```

`List` нужен для описания типа списка:

```python
List[BankMetrics]
```

Это означает:

> список объектов `BankMetrics`.

---

## 5. Объявление класса

```python
class BankMetrics:
```

С этой строки начинается класс.

Имя класса написано в `PascalCase`, что соответствует PEP8.

---

## 6. Docstring класса

```python
"""Store bank accounts and calculate common banking metrics."""
```

Описание говорит, что класс:

- хранит банковские счета;
- рассчитывает общие метрики.

---

## 7. Глобальная ставка

```python
global_bank_rate: float = 15.0
```

Разбор:

- `global_bank_rate` — имя атрибута;
- `float` — ожидаемый тип;
- `15.0` — начальное значение.

Атрибут принадлежит классу:

```text
BankMetrics.global_bank_rate = 15.0
```

---

## 8. Общий список счетов

```python
accounts: List[BankMetrics] = []
```

Изначально:

```text
BankMetrics.accounts = []
```

Список пуст.

Каждый новый объект добавляется в этот список.

---

## 9. Конструктор

```python
def __init__(self, name: str, balance: float) -> None:
```

`__init__` вызывается при создании объекта.

Пример:

```python
account1 = BankMetrics("Tom", 15000)
```

Python автоматически передаёт:

```text
self    → новый объект
name    → "Tom"
balance → 15000
```

---

## 10. Сохранение имени

```python
self.name = name
```

Слева:

```python
self.name
```

атрибут конкретного объекта.

Справа:

```python
name
```

значение аргумента.

Результат:

```text
account1.name = "Tom"
```

---

## 11. Сохранение баланса

```python
self.balance = balance
```

Результат:

```text
account1.balance = 15000
```

Баланс относится только к этому счёту.

---

## 12. Добавление объекта в реестр

```python
BankMetrics.accounts.append(self)
```

Разбор:

1. Берётся класс `BankMetrics`.
2. Берётся его список `accounts`.
3. Вызывается `append`.
4. В список добавляется текущий объект `self`.

После создания Tom:

```text
accounts = [Tom]
```

После Jerry:

```text
accounts = [Tom, Jerry]
```

После Spike:

```text
accounts = [Tom, Jerry, Spike]
```

---

## 13. Декоратор `@staticmethod`

```python
@staticmethod
```

Он сообщает Python, что следующий метод не должен получать автоматически:

- `self`;
- `cls`.

---

## 14. Метод изменения ставки

```python
def adjust_global_bank_rate(new_rate: float) -> None:
```

Метод принимает только:

```text
new_rate
```

Вызов:

```python
BankMetrics.adjust_global_bank_rate(16.0)
```

передаёт:

```text
new_rate = 16.0
```

---

## 15. Изменение ставки

```python
BankMetrics.global_bank_rate = new_rate
```

До вызова:

```text
15.0
```

После вызова:

```text
16.0
```

Метод не возвращает значение, поэтому указан тип:

```python
-> None
```

---

## 16. Декоратор `@classmethod`

```python
@classmethod
```

Python автоматически передаёт класс как первый аргумент.

По соглашению он называется:

```python
cls
```

---

## 17. Метод среднего баланса

```python
def calculate_avg_balance(cls) -> float:
```

При вызове:

```python
BankMetrics.calculate_avg_balance()
```

получаем:

```text
cls → BankMetrics
```

---

## 18. Генератор балансов

```python
account.balance for account in cls.accounts
```

Это означает:

> пройти по каждому счёту в общем списке и взять его баланс.

Для трёх объектов значения будут:

```text
15000
20000
10000
```

---

## 19. Сумма балансов

```python
total_balance = sum(
    account.balance
    for account in cls.accounts
)
```

`sum` складывает:

```text
15000 + 20000 + 10000 = 45000
```

После выполнения:

```text
total_balance = 45000
```

---

## 20. Количество счетов

```python
len(cls.accounts)
```

В списке три объекта:

```text
len(cls.accounts) = 3
```

---

## 21. Среднее значение

```python
return total_balance / len(cls.accounts)
```

Подстановка:

```text
45000 / 3 = 15000.0
```

Метод возвращает число.

---

## 22. Метод расчёта процентов

```python
@classmethod
def calculate_interest(
    cls,
    account: BankMetrics,
) -> float:
```

Метод получает:

- `cls` автоматически;
- `account` явно.

Вызов:

```python
BankMetrics.calculate_interest(account1)
```

даёт:

```text
cls     → BankMetrics
account → account1
```

---

## 23. Формула процентов

```python
return account.balance * cls.global_bank_rate / 100
```

Для Tom после изменения ставки:

```text
account.balance      = 15000
cls.global_bank_rate = 16.0
```

Расчёт:

```text
15000 × 16.0 = 240000.0
240000.0 / 100 = 2400.0
```

---

## 24. Почему используется `cls.global_bank_rate`

Метод является методом класса.

Через `cls` он получает доступ к текущему классу.

Это также помогает при наследовании: если метод вызвать через подкласс, `cls` будет указывать на подкласс.

---

## 25. Защитный блок запуска

```python
if __name__ == "__main__":
```

Если файл запускается напрямую, код внутри выполняется.

Если файл импортируется автотестом, код внутри не выполняется.

Это предотвращает создание тестовых счетов во время импорта.

---

## 26. Создание первого счёта

```python
account1 = BankMetrics("Tom", 15000)
```

Шаги:

1. Создаётся объект.
2. Вызывается `__init__`.
3. Сохраняется имя.
4. Сохраняется баланс.
5. Объект добавляется в `accounts`.
6. Ссылка записывается в `account1`.

---

## 27. Создание других счетов

```python
BankMetrics("Jerry", 20000)
BankMetrics("Spike", 10000)
```

Переменные для этих объектов не обязательны, потому что общий список класса уже сохраняет ссылки на них.

---

## 28. Проверка среднего

```python
assert BankMetrics.calculate_avg_balance() == 15000
```

`assert` проверяет условие.

Если оно ложно, возникает:

```text
AssertionError
```

---

## 29. Проверка изменения ставки

```python
BankMetrics.adjust_global_bank_rate(16.0)
assert BankMetrics.global_bank_rate == 16.0
```

Первая строка меняет ставку.

Вторая проверяет результат.

---

## 30. Проверка процентов

```python
assert BankMetrics.calculate_interest(account1) == 2400.0
```

Метод должен вернуть:

```text
2400.0
```


---

## 31. Полная трассировка состояния

### После импорта

```text
global_bank_rate = 15.0
accounts = []
```

### После Tom

```text
accounts = [Tom(15000)]
```

### После Jerry

```text
accounts = [Tom(15000), Jerry(20000)]
```

### После Spike

```text
accounts = [
    Tom(15000),
    Jerry(20000),
    Spike(10000),
]
```

### После расчёта среднего

```text
average = 15000.0
```

Состояние класса не меняется.

### После изменения ставки

```text
global_bank_rate = 16.0
```

### После расчёта процентов

```text
Tom interest = 2400.0
```

Баланс Tom не меняется. Метод только возвращает рассчитанное значение.

---

## 32. Как Python видит разные методы

Обычный метод:

```python
def method(self):
    ...
```

При вызове через объект Python автоматически передаёт объект.

Статический метод:

```python
@staticmethod
def method(value):
    ...
```

Python ничего не добавляет к аргументам.

Метод класса:

```python
@classmethod
def method(cls):
    ...
```

Python автоматически передаёт класс.

---

## 33. Как автотест может проверять декораторы

Автотест может обратиться напрямую к словарю класса:

```python
BankMetrics.__dict__["adjust_global_bank_rate"]
```

и проверить:

```python
isinstance(..., staticmethod)
```

Для метода класса:

```python
isinstance(..., classmethod)
```

Именно поэтому одинаковый математический результат не заменяет правильную структуру метода.

---

## 34. Почему нельзя переименовывать методы

Проверяющая система ожидает точные имена:

```text
adjust_global_bank_rate
calculate_avg_balance
calculate_interest
```

Если назвать метод иначе, тест не сможет его найти.

Неправильно:

```python
change_rate(...)
```

если тест ожидает:

```python
adjust_global_bank_rate(...)
```

---

## 35. Почему нельзя менять сигнатуру

Ожидаемые вызовы:

```python
BankMetrics.adjust_global_bank_rate(16.0)
BankMetrics.calculate_avg_balance()
BankMetrics.calculate_interest(account1)
```

Если добавить обязательные аргументы, вызов теста сломается.

Например, нельзя требовать:

```python
calculate_interest(account, rate)
```

потому что ставка должна браться из класса.

---

## 36. Почему нет лишней валидации

Задача не требует:

- запрещать отрицательный баланс;
- запрещать отрицательную ставку;
- обрабатывать пустой список;
- хранить валюту;
- округлять деньги;
- использовать базу данных.

Дополнительные правила должны появляться только из требований.

В реальной системе валидация нужна, но в учебной задаче важно не изменять контракт.

---

## 37. Почему нет обработки пустого списка

Если вызвать:

```python
BankMetrics.calculate_avg_balance()
```

до создания счетов, произойдёт деление на ноль.

Условие гарантирует создание счетов до расчёта.

Если бы бизнес попросил определить поведение без счетов, возможны варианты:

- вернуть `0.0`;
- вернуть `None`;
- выбросить предметное исключение.

Но выбирать вариант без требования нельзя.

---

## 38. Почему в учебном коде используется `float`

Шаблон ожидает:

```python
global_bank_rate: float
balance: float
```

Поэтому решение сохраняет эти типы.

В финансовом production-коде часто применяют:

```python
Decimal
```

из-за требований точности.

---

## 39. PEP8

В решении соблюдены:

- `PascalCase` для класса;
- `snake_case` для методов;
- аннотации типов;
- docstrings;
- пустые строки;
- читаемая длина строк;
- отсутствие лишних импортов;
- понятные имена.

---

## 40. Возможные ошибки

### Ошибка: метод имеет неверный тип

Проверьте декоратор:

```text
adjust_global_bank_rate → staticmethod
calculate_avg_balance   → classmethod
calculate_interest      → classmethod
```

### Ошибка: `cls` не передан

Убедитесь, что перед методом стоит `@classmethod`.

### Ошибка: число не имеет `balance`

В список добавили баланс вместо объекта.

Нужно:

```python
BankMetrics.accounts.append(self)
```

### Ошибка: результат равен 45000

Вернули сумму вместо среднего.

### Ошибка: результат равен 240000

Забыли деление на 100.

### Ошибка: тесты видят лишние счета

Пример создания объектов находится вне блока:

```python
if __name__ == "__main__":
```

### Ошибка: ставка не изменилась

Проверьте присваивание:

```python
BankMetrics.global_bank_rate = new_rate
```

---

## 41. Локальная проверка

Выполните:

```bash
python gp_page_1_method_decorators_solution.py
```

Правильный результат:

- нет вывода;
- нет traceback;
- нет `AssertionError`;
- код завершается успешно.

Отсутствие вывода нормально, потому что в файле нет `print`.

---

## 42. Дополнительная ручная проверка

Можно открыть Python и выполнить:

```python
from gp_page_1_method_decorators_solution import BankMetrics

BankMetrics.accounts = []
BankMetrics.global_bank_rate = 15.0

tom = BankMetrics("Tom", 15000)
jerry = BankMetrics("Jerry", 20000)
spike = BankMetrics("Spike", 10000)

print(BankMetrics.calculate_avg_balance())
# 15000.0

BankMetrics.adjust_global_bank_rate(16.0)

print(BankMetrics.global_bank_rate)
# 16.0

print(BankMetrics.calculate_interest(tom))
# 2400.0
```

---

## 43. Как объяснить решение преподавателю

Можно сказать:

> `name` и `balance` являются атрибутами каждого объекта. `global_bank_rate` и `accounts` являются общими атрибутами класса. Статический метод меняет ставку через имя класса. Метод класса `calculate_avg_balance` использует общий список, а метод класса `calculate_interest` использует общую ставку и переданный счёт.

---

## 44. Как объяснить решение одной фразой

> Конструктор сохраняет индивидуальные данные счёта, статический метод меняет общую ставку, первый метод класса считает среднее по общему реестру, а второй метод класса применяет общую ставку к переданному счёту.

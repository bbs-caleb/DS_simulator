# Этап 2. Готовое решение

## Файл для сдачи: `valid_emails.py`

```python
import re
from typing import List


VALID_EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$"
)


def valid_emails(strings: List[str]) -> List[str]:
    """Take list of potential emails and return only valid ones."""
    return [email for email in strings if VALID_EMAIL_REGEX.fullmatch(email)]
```

---

## Что именно ускорили

### Было

```python
return bool(re.fullmatch(valid_email_regex, email))
```

### Стало

```python
VALID_EMAIL_REGEX.fullmatch(email)
```

Мы больше не используем `re.fullmatch()` с обычной строкой-паттерном внутри проверки каждого email.

Теперь регулярное выражение заранее подготовлено через `re.compile()`.

---

## Почему `bool()` можно не писать

Метод:

```python
VALID_EMAIL_REGEX.fullmatch(email)
```

возвращает:

1. объект `Match`, если email подошёл под регулярное выражение;
2. `None`, если email не подошёл.

В условии `if` это работает так:

```python
if VALID_EMAIL_REGEX.fullmatch(email):
    ...
```

`Match` считается как `True`, а `None` считается как `False`.

Поэтому здесь не нужен отдельный `bool()`.

---

## Почему list comprehension здесь уместен

Было:

```python
emails = []
for email in strings:
    if is_valid_email(email):
        emails.append(email)

return emails
```

Стало:

```python
return [email for email in strings if VALID_EMAIL_REGEX.fullmatch(email)]
```

Это делает то же самое:

1. проходит по каждому email из списка `strings`;
2. проверяет email регулярным выражением;
3. оставляет только валидные email;
4. возвращает новый список.

Код стал короче и быстрее, но логика осталась такой же.

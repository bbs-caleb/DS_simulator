# Урок 25 — DA/ML: GENERATORS

Этот комплект относится к **первой странице** урока: здесь одновременно есть вводная теория и практическое задание.

## Состав комплекта

| Файл | Для чего нужен |
|---|---|
| `gp_page_1_generators_solution.py` | Готовый Python-файл для отправки в проверяющую систему |
| `gp_page_1_generators_context.md` | Подробный бизнесовый и технический разбор темы |
| `gp_page_1_generators_step_by_step_explanation.md` | Объяснение решения буквально по строкам |
| `gp_page_1_generators_interview_guide.md` | Подготовка к продуктовому и system design интервью |
| `gp_page_1_generators_practical_cases.md` | Промышленные сценарии из DS, ML и Data Engineering |
| `README.md` | Навигация и инструкция по использованию комплекта |

## Что отправлять на платформу

Загрузите только файл:

```text
gp_page_1_generators_solution.py
```

В нём находятся ровно две функции, которые требует задание:

```python
username_generator(n, first_names=None, last_names=None)
data_generator(n)
```

## Что гарантирует решение

- обе функции используют `yield`;
- обе функции возвращают генераторные объекты;
- `username_generator` создаёт ровно `n` словарей;
- ID идут от `1` до `n`;
- пользовательские списки имён и фамилий поддерживаются;
- при `None` используются внутренние списки по умолчанию;
- `data_generator` создаёт `x` от `0` до `n - 1`;
- `y` — целое случайное число от `0` до `100` включительно;
- нет `print`, демонстрационного запуска и других побочных эффектов при импорте;
- код оформлен в соответствии с базовыми требованиями PEP8.

## Быстрая локальная проверка

```python
from gp_page_1_generators_solution import data_generator
from gp_page_1_generators_solution import username_generator


print(list(username_generator(3)))
print(list(data_generator(3)))
```

Проверка типа:

```python
import types


assert isinstance(username_generator(1), types.GeneratorType)
assert isinstance(data_generator(1), types.GeneratorType)
```

## Главная идея урока

Обычная функция с `return` вычисляет результат и завершает работу.

Функция с `yield`:

1. создаёт генераторный объект;
2. вычисляет следующий элемент только по запросу;
3. отдаёт этот элемент;
4. приостанавливает выполнение;
5. сохраняет локальные переменные и текущую позицию;
6. продолжает работу при следующем `next()`.

Такой подход особенно полезен, когда данные слишком велики для загрузки в память или поступают как поток.

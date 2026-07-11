# ML: YAML CONFIG — полный комплект страницы 1

## Статус

Комплект пересобран после обратной связи автотеста. В первоначальном варианте единственной ошибкой был регистр логических значений в `yaml_to_env`:

```text
нужно: True / False
было:  true / false
```

В итоговом решении используется:

```python
env_value = str(value)
```

`env_to_yaml` уже получила 40/40, Pylint — 20/20, API и импорт прошли.

---

## Все файлы

| Файл | Назначение |
|---|---|
| `README.md` | Навигация и инструкция по отправке |
| `gp_page_1_yaml_config_context.md` | Большой бизнесовый и технический контекст |
| `gp_page_1_yaml_config_solution.py` | Минимальный файл-решение |
| `gp_page_1_yaml_config_step_by_step_explanation.md` | Пошаговое объяснение каждой части кода с нуля |
| `gp_page_1_yaml_config_testing_guide.md` | Тесты и подробный разбор ошибки 60/100 |
| `gp_page_1_yaml_config_interview_guide.md` | Product и System Design interview guide |

---

## Что загружать в Karpov Simulator

Только:

```text
gp_page_1_yaml_config_solution.py
```

Не загружайте Markdown-файлы вместе с решением.

---

## Обязательный API

```python
import yaml


def yaml_to_env(config_file: str) -> str:
    ...


def env_to_yaml(env_list: str) -> str:
    ...
```

Нельзя менять:

- имена функций;
- число обязательных аргументов;
- возвращаемый тип;
- формат: функция принимает текст, а не путь к файлу.

---

## Быстрый пример

Входной YAML:

```yaml
preprocess_params:
  sr: 24000
  use_gpu: false
model_params:
  use_spectral_norm: true
```

`yaml_to_env` возвращает:

```text
preprocess_params.sr=24000
preprocess_params.use_gpu=False
model_params.use_spectral_norm=True
```

Обратите внимание: в ENV тест ожидает `True` и `False` с заглавной буквы.

`env_to_yaml` восстановит структуру:

```yaml
preprocess_params:
  sr: 24000
  use_gpu: false
model_params:
  use_spectral_norm: true
```

---

## Критические edge cases

### Неизвестная глубина

Используется рекурсивный обход словарей.

### Типы

`yaml.safe_load` восстанавливает `int`, `float`, `bool`, строки и `null`.

### Пустая строка

```text
pretrained_model=
```

должна стать пустой строкой, а не `None`.

### `=` внутри значения

Используется `partition("=")`, который разделяет только по первому знаку.

---

## Порядок изучения

1. `gp_page_1_yaml_config_context.md`
2. `gp_page_1_yaml_config_solution.py`
3. `gp_page_1_yaml_config_step_by_step_explanation.md`
4. `gp_page_1_yaml_config_testing_guide.md`
5. `gp_page_1_yaml_config_interview_guide.md`

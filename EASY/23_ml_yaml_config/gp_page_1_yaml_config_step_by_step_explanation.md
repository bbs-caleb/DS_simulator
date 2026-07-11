# ML: YAML CONFIG — подробное объяснение решения

## 1. Обязательный API

Проверяющая система ожидает две функции:

```python
def yaml_to_env(config_file: str) -> str:
    ...


def env_to_yaml(env_list: str) -> str:
    ...
```

Имена, число аргументов и тип возвращаемого результата менять нельзя.

Важно: `config_file` — это текст YAML, а не путь к файлу.

---

# 2. Импорт

```python
import yaml
```

PyYAML даёт два главных инструмента:

```python
yaml.safe_load(text)
yaml.safe_dump(data)
```

`safe_load` превращает YAML-текст в Python-объекты.

`safe_dump` превращает Python-объекты обратно в YAML-текст.

---

# 3. Функция `yaml_to_env`

```python
def yaml_to_env(config_file: str) -> str:
```

Она получает:

```yaml
model_params:
  dim_in: 64
```

и возвращает:

```text
model_params.dim_in=64
```

## 3.1. Чтение YAML

```python
config = yaml.safe_load(config_file)
```

До вызова:

```python
config_file = "model_params:\n  dim_in: 64\n"
```

После вызова:

```python
config = {
    "model_params": {
        "dim_in": 64,
    }
}
```

## 3.2. Список строк результата

```python
env_lines = []
```

В него будут добавляться строки:

```python
[
    "model_params.dim_in=64",
    "model_params.style_dim=64",
]
```

## 3.3. Рекурсивная функция

```python
def flatten(data: dict, parent_key: str = "") -> None:
```

`data` — словарь текущего уровня.

`parent_key` — накопленный путь.

Примеры пути:

```text
""
preprocess_params
preprocess_params.spect_params
loss_params.g_loss
```

Функция не возвращает отдельное значение. Она добавляет строки в `env_lines`.

## 3.4. Перебор словаря

```python
for key, value in data.items():
```

Для:

```python
{
    "sr": 24000,
    "spect_params": {
        "n_fft": 2048,
    },
}
```

сначала будет:

```python
key = "sr"
value = 24000
```

затем:

```python
key = "spect_params"
value = {"n_fft": 2048}
```

## 3.5. Полный путь

```python
full_key = (
    f"{parent_key}.{key}"
    if parent_key
    else str(key)
)
```

Если путь уже есть:

```python
parent_key = "preprocess_params"
key = "sr"
```

получим:

```text
preprocess_params.sr
```

Если путь пустой:

```python
parent_key = ""
key = "device"
```

получим:

```text
device
```

Без условия верхнеуровневый ключ выглядел бы неправильно:

```text
.device
```

## 3.6. Рекурсивный случай

```python
if isinstance(value, dict):
    flatten(value, full_key)
```

Если `value` является словарём, лист ещё не найден. Функция вызывает себя на вложенном словаре.

Пример:

```python
flatten(
    {"n_fft": 2048},
    "preprocess_params.spect_params",
)
```

## 3.7. Базовый случай

```python
else:
```

Сюда попадаем, когда значение не словарь:

```python
value = 2048
```

Это лист дерева. Нужно сформировать переменную окружения.

## 3.8. `None`

```python
if value is None:
    env_value = "null"
```

YAML-представление отсутствующего значения:

```text
null
```

## 3.9. `bool` и остальные значения

```python
else:
    env_value = str(value)
```

Для целых чисел, `float`, строк и логических значений используется обычный `str`.

Особенно важно для автотеста этой задачи:

```python
str(True)   # "True"
str(False)  # "False"
```

Платформа ожидает именно:

```text
True
False
```

Нельзя использовать:

```python
str(value).lower()
```

потому что тогда получится `true`/`false`, а тест сравнивает текст и считает это ошибкой.

## 3.10. Примеры преобразования через `str`

Примеры:

```python
str(150)       # "150"
str(0.0001)    # "0.0001"
str("cuda")    # "cuda"
str("")        # ""
```

## 3.11. Добавление результата

```python
env_lines.append(f"{full_key}={env_value}")
```

Пример:

```text
preprocess_params.sr=24000
```

## 3.12. Запуск обхода

```python
if isinstance(config, dict):
    flatten(config)
```

Для корректного конфига верхний уровень является словарём.

## 3.13. Сборка строки

```python
return "\n".join(env_lines)
```

Список:

```python
[
    "device=cuda",
    "epochs=150",
    "fp16_run=True",
]
```

становится:

```text
device=cuda
epochs=150
fp16_run=True
```

---

# 4. Функция `env_to_yaml`

```python
def env_to_yaml(env_list: str) -> str:
```

Она получает:

```text
model_params.dim_in=64
model_params.style_dim=64
```

и возвращает YAML.

## 4.1. Корневой словарь

```python
config = {}
```

В него постепенно будет собираться дерево.

## 4.2. Разделение по строкам

```python
for raw_line in env_list.splitlines():
```

Текст:

```text
a=1
b=2
```

становится:

```python
["a=1", "b=2"]
```

## 4.3. Удаление внешних пробелов

```python
line = raw_line.strip()
```

```text
"  epochs=150  "
```

становится:

```text
"epochs=150"
```

## 4.4. Пропуск пустых строк

```python
if not line:
    continue
```

Функция спокойно обработает:

```text
device=cuda

epochs=150
```

## 4.5. Деление по первому `=`

```python
key, separator, raw_value = line.partition("=")
```

Для:

```text
token=abc=def
```

получим:

```python
key = "token"
separator = "="
raw_value = "abc=def"
```

Это лучше, чем неограниченный `split("=")`, потому что значение может содержать `=`.

## 4.6. Проверка формата

```python
if not separator:
    raise ValueError(
        "Each environment variable must contain '='."
    )
```

Строка:

```text
epochs150
```

не является корректной записью `ключ=значение`.

## 4.7. Разделение пути

```python
path = key.strip().split(".")
```

Ключ:

```text
loss_params.g_loss.lambda_sty
```

становится:

```python
[
    "loss_params",
    "g_loss",
    "lambda_sty",
]
```

Все элементы, кроме последнего, должны стать словарями. Последний получает значение.

## 4.8. Пустая строка

```python
value_text = raw_value.strip()

if value_text == "":
    value = ""
else:
    value = yaml.safe_load(value_text)
```

Это критично.

```python
yaml.safe_load("")
```

возвращает `None`, но исходное:

```yaml
pretrained_model: ""
```

должно остаться пустой строкой.

## 4.9. Восстановление типов

```python
value = yaml.safe_load(value_text)
```

Примеры:

```python
yaml.safe_load("150")
# 150, тип int

yaml.safe_load("0.001")
# 0.001, тип float

yaml.safe_load("True")
# True, тип bool

yaml.safe_load("cuda")
# "cuda", тип str
```

## 4.10. Указатель на текущий уровень

```python
current_level = config
```

Сначала мы на корне дерева.

## 4.11. Построение вложенных словарей

```python
for path_part in path[:-1]:
    current_level = current_level.setdefault(path_part, {})
```

Для:

```python
path = ["loss_params", "g_loss", "lambda_sty"]
```

`path[:-1]` равно:

```python
["loss_params", "g_loss"]
```

Сначала создаётся:

```python
{"loss_params": {}}
```

Затем:

```python
{
    "loss_params": {
        "g_loss": {}
    }
}
```

`setdefault`:

- возвращает существующее значение ключа;
- либо создаёт значение `{}` и возвращает его.

## 4.12. Запись листа

```python
current_level[path[-1]] = value
```

`path[-1]` — последний элемент:

```text
lambda_sty
```

После записи:

```python
{
    "loss_params": {
        "g_loss": {
            "lambda_sty": 1.0,
        }
    }
}
```

## 4.13. Сериализация в YAML

```python
return yaml.safe_dump(
    config,
    sort_keys=False,
    allow_unicode=True,
)
```

Результат — строка YAML.

---

# 5. Полная трассировка

Вход:

```text
a.b.c=10
a.b.flag=True
```

Начало:

```python
config = {}
```

После первой строки:

```python
{
    "a": {
        "b": {
            "c": 10,
        }
    }
}
```

После второй:

```python
{
    "a": {
        "b": {
            "c": 10,
            "flag": True,
        }
    }
}
```

YAML:

```yaml
a:
  b:
    c: 10
    flag: true
```

---

# 6. Проверка на полном `config.yml`

```python
from pathlib import Path

import yaml

from gp_page_1_yaml_config_solution import env_to_yaml
from gp_page_1_yaml_config_solution import yaml_to_env


original_text = Path("config.yml").read_text(encoding="utf-8")
env_text = yaml_to_env(original_text)
restored_text = env_to_yaml(env_text)

original_config = yaml.safe_load(original_text)
restored_config = yaml.safe_load(restored_text)

assert original_config == restored_config
```

Сравнивать исходный и восстановленный текст напрямую нельзя. YAML может быть одинаковым по смыслу, но отличаться форматированием.

---

# 7. Минимальные тесты

## Один уровень

```python
source = """
epochs: 150
device: cuda
"""

result = yaml_to_env(source)

assert set(result.splitlines()) == {
    "epochs=150",
    "device=cuda",
}
```

## Глубокая вложенность

```python
source = """
a:
  b:
    c:
      d: 42
"""

assert yaml_to_env(source) == "a.b.c.d=42"
```

## Типы

```python
source = """
epochs=150
lr=0.001
enabled=True
device=cuda
"""

result = yaml.safe_load(env_to_yaml(source))

assert result["epochs"] == 150
assert isinstance(result["epochs"], int)

assert result["lr"] == 0.001
assert isinstance(result["lr"], float)

assert result["enabled"] is True
assert result["device"] == "cuda"
```

## Пустая строка

```python
result = yaml.safe_load(env_to_yaml("pretrained_model="))

assert result["pretrained_model"] == ""
```

## Значение с `=`

```python
result = yaml.safe_load(env_to_yaml("token=abc=def"))

assert result["token"] == "abc=def"
```

## Round-trip

```python
source = """
service:
  timeout: 50
  enabled: true
  model_path: ""
"""

restored = env_to_yaml(yaml_to_env(source))

assert yaml.safe_load(restored) == yaml.safe_load(source)
```

---

# 9. Сложность

Пусть:

- `N` — число узлов YAML-дерева;
- `L` — число строк ENV;
- `D` — средняя глубина пути.

Для `yaml_to_env` каждый узел посещается один раз:

```text
O(N)
```

Для `env_to_yaml` каждая строка проходит по частям пути:

```text
O(L × D)
```

Память итоговой структуры:

```text
O(N)
```

Стек рекурсии зависит от максимальной глубины дерева.

---

# 9. Частые ошибки

## Ошибка 1. Жёстко обработать только два уровня

```python
for key, value in config.items():
    for child_key, child_value in value.items():
        ...
```

Такой код сломается на третьем уровне.

## Ошибка 2. Потерять полный путь

Получить только:

```text
n_fft=2048
```

вместо:

```text
preprocess_params.spect_params.n_fft=2048
```

Тогда структуру восстановить невозможно.

## Ошибка 3. Не восстановить типы

```yaml
epochs: "150"
```

не равно:

```yaml
epochs: 150
```

## Ошибка 4. Не обработать пустую строку

```text
pretrained_model=
```

ошибочно станет:

```yaml
pretrained_model: null
```

## Ошибка 5. Разделять по каждому `=`

```text
token=abc=def
```

нужно разделить только по первому знаку.

## Ошибка 6. Сравнивать YAML как строки

Порядок ключей и кавычки могут отличаться при одинаковом смысле.

## Ошибка 7. Изменить API

Проверяющая система не найдёт нужную функцию и поставит 0.

---

# 10. Что нужно запомнить

1. YAML после `safe_load` обычно становится словарём.
2. Вложенный словарь — дерево.
3. Рекурсия подходит для неизвестной глубины.
4. Базовый случай — значение не словарь.
5. Рекурсивный случай — значение словарь.
6. Путь накапливается через точку.
7. `setdefault` помогает строить вложенные словари.
8. `safe_load` восстанавливает базовые типы.
9. Пустая строка и `None` — разные значения.
10. Точный API так же важен, как алгоритм.

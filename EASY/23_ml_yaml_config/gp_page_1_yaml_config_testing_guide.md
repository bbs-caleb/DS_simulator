# ML: YAML CONFIG — тестирование и разбор ошибки 60/100

## 1. Результаты первой отправки

```text
✓ xtest_import
✓ xtest_api
✗ test_yaml_to_env       0/40
✓ test_env_to_yaml      40/40
✓ test_pylint           20/20
```

Это означает:

- модуль импортируется;
- имена и сигнатуры функций правильные;
- `env_to_yaml` уже полностью правильна;
- качество кода уже соответствует PEP8/Pylint;
- ошибка находится только в текстовом результате `yaml_to_env`.

Главное правило отладки:

> Не переписывать части, которые уже прошли тесты.

---

# 2. Сравнение Expected и Got

Ожидалось:

```text
preprocess_params.use_gpu=False
preprocess_params.spect_params.use_window_function=True
model_params.use_spectral_norm=True
```

Получено:

```text
preprocess_params.use_gpu=false
preprocess_params.spect_params.use_window_function=true
model_params.use_spectral_norm=true
```

Совпали:

- все ключи;
- порядок;
- вложенные пути;
- строки;
- `int`;
- `float`;
- количество переменных.

Единственное отличие — регистр `bool`.

---

# 3. Неправильный код

```python
elif isinstance(value, bool):
    env_value = str(value).lower()
```

Результат:

```python
str(True).lower()   # "true"
str(False).lower()  # "false"
```

---

# 4. Правильный код

```python
if value is None:
    env_value = "null"
else:
    env_value = str(value)
```

Результат:

```python
str(True)   # "True"
str(False)  # "False"
```

---

# 5. Почему обратное преобразование не ломается

```python
yaml.safe_load("True")
```

возвращает:

```python
True
```

А:

```python
yaml.safe_load("False")
```

возвращает:

```python
False
```

Поэтому `env_to_yaml`, которая уже получила 40/40, менять не нужно.

---

# 6. Точный тест из сообщения платформы

```python
source = """
F0_path: Utils/JDC/bst.t7
ASR_config: Utils/ASR/config.yml
ASR_path: Utils/ASR/epoch_00100.pth
preprocess_params:
  sr: 24000
  use_gpu: false
  mode: testing
  options:
    option1: 123
    option2: abc
  spect_params:
    n_fft: 2048
    win_length: 1200
    hop_length: 300
    use_window_function: true
model_params:
  dim_in: 64
  style_dim: 64
  latent_dim: 16
  num_domains: 20
  max_conv_dim: 512
  n_repeat: 4
  dropout: 0.1
  use_spectral_norm: true
  optimizer:
    learning_rate: 0.001
    momentum: 0.9
    weight_decay: 0.0001
"""
```

```python
expected = {
    "F0_path=Utils/JDC/bst.t7",
    "ASR_config=Utils/ASR/config.yml",
    "ASR_path=Utils/ASR/epoch_00100.pth",
    "preprocess_params.sr=24000",
    "preprocess_params.use_gpu=False",
    "preprocess_params.mode=testing",
    "preprocess_params.options.option1=123",
    "preprocess_params.options.option2=abc",
    "preprocess_params.spect_params.n_fft=2048",
    "preprocess_params.spect_params.win_length=1200",
    "preprocess_params.spect_params.hop_length=300",
    "preprocess_params.spect_params.use_window_function=True",
    "model_params.dim_in=64",
    "model_params.style_dim=64",
    "model_params.latent_dim=16",
    "model_params.num_domains=20",
    "model_params.max_conv_dim=512",
    "model_params.n_repeat=4",
    "model_params.dropout=0.1",
    "model_params.use_spectral_norm=True",
    "model_params.optimizer.learning_rate=0.001",
    "model_params.optimizer.momentum=0.9",
    "model_params.optimizer.weight_decay=0.0001",
}

actual = set(yaml_to_env(source).splitlines())

assert actual == expected
```

Порядок строк по условию не важен, поэтому сравниваем множества.

---

# 7. Round-trip тест

Round trip означает полный цикл:

```text
YAML → ENV → YAML
```

```python
import yaml

original = yaml.safe_load(source)
env_text = yaml_to_env(source)
restored = yaml.safe_load(env_to_yaml(env_text))

assert restored == original
```

Сравнивать YAML-тексты напрямую нельзя, потому что могут различаться:

- порядок ключей;
- кавычки;
- отступы;
- `true` и `True`;
- пустые строки в конце.

Сравниваем разобранные Python-структуры.

---

# 8. Пустая строка

```python
source = 'pretrained_model: ""\n'

assert yaml_to_env(source) == "pretrained_model="

restored = yaml.safe_load(
    env_to_yaml("pretrained_model=")
)

assert restored["pretrained_model"] == ""
assert restored["pretrained_model"] is not None
```

Почему нужна отдельная проверка:

```python
yaml.safe_load("") is None
```

---

# 9. Проверка типов

```python
env_text = """
integer_value=123
float_value=0.25
true_value=True
false_value=False
string_value=testing
null_value=null
"""

result = yaml.safe_load(env_to_yaml(env_text))

assert result["integer_value"] == 123
assert isinstance(result["integer_value"], int)

assert result["float_value"] == 0.25
assert isinstance(result["float_value"], float)

assert result["true_value"] is True
assert result["false_value"] is False
assert result["string_value"] == "testing"
assert result["null_value"] is None
```

---

# 10. Глубокая вложенность

```python
source = """
a:
  b:
    c:
      d:
        e:
          value: 10
"""

assert yaml_to_env(source) == "a.b.c.d.e.value=10"
```

---

# 11. Значение со знаком `=`

```python
result = yaml.safe_load(
    env_to_yaml("token=abc=def")
)

assert result["token"] == "abc=def"
```

Это работает благодаря:

```python
line.partition("=")
```

---

# 12. Некорректная строка

```python
try:
    env_to_yaml("invalid_line")
except ValueError:
    pass
else:
    raise AssertionError("ValueError was not raised")
```

---

# 13. Ожидаемая структура баллов после исправления

```text
yaml_to_env  40/40
env_to_yaml  40/40
pylint       20/20
Total       100/100
```

Фактический итог окончательно подтверждается новой отправкой, но исправление точно устраняет единственное расхождение, показанное автотестом.

---

# 14. Универсальный алгоритм отладки автотестов

1. Посмотреть, какие тесты уже прошли.
2. Зафиксировать работающие части.
3. Сравнить `Expected` и `Got` символ за символом.
4. Найти минимальное отличие.
5. Связать отличие с конкретной строкой кода.
6. Сделать минимальный патч.
7. Повторить точный тест локально.
8. Запустить регрессионные тесты для уже работающих функций.

Это тот же подход, который используется при исправлении production-багов.

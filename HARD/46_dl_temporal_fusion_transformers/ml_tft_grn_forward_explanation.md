# Урок 46 DL: TFT — Шаг 2. Пошаговое объяснение кода GRN

Объясняю всё с нуля.

## 1. Импорты

```python
import torch
from torch import nn
```

`torch` — сам PyTorch. `nn` — модуль с готовыми слоями (`Linear`, `ELU`, `Dropout`, `LayerNorm`). `from torch import nn` — каноничный для pylint стиль записи.

## 2. Класс GatedLinearUnit (GLU)

Этот класс уже реализован в шаблоне — разберём, чтобы понимать, что вызываем.

```python
def __init__(self, input_size, output_size):
    super().__init__()
    self.linear = nn.Linear(input_size, output_size)
    self.sigmoid = nn.Linear(input_size, output_size)
```

`nn.Linear(in, out)` — обычный полносвязный слой, то есть операция `y = x·W + b`. Внутри GLU их два: один даст «информацию», второй — «кран». Имя `self.sigmoid` немного сбивает с толку — это не функция сигмоиды, а линейный слой, к выходу которого сигмоиду применят в forward.

```python
def forward(self, x):
    return self.linear(x) * torch.sigmoid(self.sigmoid(x))
```

Формула `GLU(x) = (W_l·x + b_l) * σ(W_s·x + b_s)`:
- `self.linear(x)` — линейная (информационная) ветка;
- `torch.sigmoid(self.sigmoid(x))` — тот же вход, прогнанный через второй линейный слой и сжатый сигмоидой в `(0, 1)`;
- `*` — поэлементное умножение: «кран» решает, какую долю информации пропустить.

## 3. Класс GatedResidualNetwork — конструктор

```python
self.hidden_size = hidden_size
```

Запоминаем целевую размерность — она понадобится в forward, чтобы решить, нужна ли проекция.

```python
self.elu_dense = nn.Sequential(
    nn.Linear(input_size, hidden_size),
    nn.ELU()
)
```

`nn.Sequential` — контейнер, который прогоняет вход через слои по очереди. Здесь: сначала линейный слой `input_size → hidden_size`, потом активация **ELU** (Exponential Linear Unit — как ReLU, но для отрицательных значений даёт плавную кривую, а не строгий ноль). Это реализация `η_2 = ELU(W_2·a + b_2)` из формулы (контекст `c` в шаблоне не используется, поэтому член `W_3·c` опущен).

```python
self.linear_dense = nn.Linear(hidden_size, hidden_size)
self.dropout = nn.Dropout(dropout_rate)
self.glu = GatedLinearUnit(hidden_size, hidden_size)
self.layer_norm = nn.LayerNorm(hidden_size)
self.project = nn.Linear(input_size, hidden_size)
```

- `linear_dense` — второй линейный слой, это `η_1 = W_1·η_2 + b_1`;
- `dropout` — регуляризация: во время обучения случайно «гасит» долю нейронов (`dropout_rate`), чтобы сеть не заучивала данные;
- `glu` — наш фильтр из пункта 2;
- `layer_norm` — **LayerNorm**, нормализует активации (приводит к среднему 0 и дисперсии 1 по признакам), стабилизирует обучение;
- `project` — проекция входа `input_size → hidden_size` для skip-connection, когда размерности не совпадают.

## 4. Метод forward — то, что нужно было дописать

### Развилка residual (уже в шаблоне)

```python
if x.shape[-1] != self.hidden_size:
    residual = self.project(x)
else:
    residual = x
```

`x.shape[-1]` — размер последнего измерения входа (число признаков). Skip-connection — это «прибавить вход к выходу». Но прибавить можно только тензоры одинаковой формы. Поэтому: если вход уже размера `hidden_size` — берём его как есть; если нет — прогоняем через `self.project`, чтобы привести к `hidden_size`. `residual` — это та самая «прямая дорога» для градиента.

### Основной путь (наш код)

```python
x = self.elu_dense(x)              # eta_2 = ELU(W_2 * a + b_2)
x = self.linear_dense(x)           # eta_1 = W_1 * eta_2 + b_1
x = self.dropout(x)                # регуляризация после линейного слоя
x = self.glu(x)                    # GLU-фильтрация
x = self.layer_norm(x + residual)  # residual + LayerNorm
```

Читается сверху вниз ровно как формула GRN:

1. `self.elu_dense(x)` — нелинейное преобразование входа через линейный слой + ELU. Получаем `η_2`.
2. `self.linear_dense(x)` — второй линейный слой. Получаем `η_1`. Обратите внимание: мы переиспользуем имя `x`, просто «протаскивая» тензор через слои — это распространённый и чистый стиль.
3. `self.dropout(x)` — по тексту урока dropout идёт после линейного слоя. При обучении гасит часть значений, при инференсе (`model.eval()`) не делает ничего.
4. `self.glu(x)` — фильтр решает, какую часть преобразования пропустить. Если преобразование бесполезно, GLU может «прижать» его сигмоидой к нулю.
5. `self.layer_norm(x + residual)` — самый важный момент: сначала складываем результат основного пути с прямой дорогой `residual` (это и есть skip-connection, `a + GLU(η_1)` в формуле), затем нормализуем LayerNorm'ом. Именно сложение с `residual` даёт градиенту прямой путь и позволяет сети «пропустить» преобразование, если оно не нужно.

```python
return x
```

Возвращаем тензор формы `(..., hidden_size)`.

### Почему порядок именно такой

Формула `GRN(a) = LayerNorm(a + GLU(η_1))`, разворачиваясь изнутри наружу, даёт последовательность: сначала посчитать `η_2` (ELU-слой), потом `η_1` (линейный слой), применить dropout и GLU, и только в самом конце прибавить исходный вход `a` (= `residual`) и нормализовать. Любая перестановка сломает соответствие формуле — например, если применить LayerNorm до сложения с residual, это будет уже другая архитектура.

## 5. Функция test и точка входа

```python
def test() -> None:
    torch.manual_seed(42)
    ...
```

Smoke-тест проверяет обе ветки развилки:
- **Case 1** — вход уже размера `hidden_size`, проекция не нужна, идём по `residual = x`;
- **Case 2** — вход размера 10 ≠ 16, срабатывает `self.project`.

В обоих случаях `assert` проверяет, что выход имеет форму `(batch_size, hidden_size)` — контракт соблюдён.

```python
if __name__ == "__main__":
    test()
```

Тест запускается только при прямом запуске файла, но не при импорте класса грейдером.

## 6. Итог

Код собирает GRN строго по формуле из урока: ELU-слой → линейный слой → Dropout → GLU → сложение с residual → LayerNorm. Smoke-тест на обеих ветках проходит, pylint 10.00/10.

# GP Page 6 — подробное объяснение кода Implicit ALS

## 1. Какие файлы участвуют

### `gp_page_6_implicit_als_recommender_system_solution.py`

Это код, который должен оказаться внутри submission под именем:

```text
solution.py
```

Он содержит:

- обработку данных;
- построение sparse matrix;
- обучение ALS;
- сохранение и загрузку модели;
- генерацию рекомендаций;
- FastAPI endpoint.

### `gp_page_6_implicit_als_recommender_system_train_and_build.py`

Автоматически:

1. читает CSV;
2. обучает модель;
3. создаёт `model.pkl`;
4. копирует код в `solution.py`;
5. создаёт итоговый `solution.zip`.

---

# 2. Импорты

```python
import os
import pickle
import sys
from typing import List, Tuple
```

- `os` — переменные окружения и пути;
- `pickle` — сохранение обученной модели;
- `sys.path[0]` — директория запуска;
- `List` и `Tuple` — типы возвращаемых значений.

```python
import implicit
import numpy as np
import pandas as pd
```

- `implicit` — ALS;
- `numpy` — числовые массивы и тип `float64`;
- `pandas` — CSV и преобразования таблицы.

```python
from scipy import sparse
```

Нужен CSR-формат sparse matrix.

---

# 3. Pydantic-модель

```python
class User(BaseModel):
    user_id: int
    personal: List[str]
```

JSON имеет форму:

```json
{
  "user_id": 42,
  "personal": [
    "streamer_a",
    "streamer_b"
  ]
}
```

---

# 4. Чтение CSV без заголовков

```python
data = pd.read_csv(
    path_from,
    names=column_names,
    header=None,
)
```

`header=None` критичен.

Иначе первая строка данных может быть принята за названия столбцов — именно такая проблема уже возникала на popularity-based странице.

---

# 5. Длительность просмотра

```python
data["total_time_stream"] = (
    data["time_end"] - data["time_start"]
).clip(lower=0)
```

Пример:

```text
time_start = 1256
time_end = 1512
```

Тогда:

```text
total_time_stream = 256
```

`clip(lower=0)` не позволяет ошибочной отрицательной длительности стать отрицательным confidence.

---

# 6. Категориальные коды

```python
data["uid"] = data["uid"].astype("category")
data["streamer_name"] = data["streamer_name"].astype("category")
```

Затем:

```python
data["user_id"] = data["uid"].cat.codes
data["streamer_id"] = data["streamer_name"].cat.codes
```

Исходный id сохраняется в `uid`.

Внутренний компактный id хранится в `user_id`.

---

# 7. Почему взаимодействия агрегируются

Один пользователь может иметь несколько сессий с одним стримером.

Например:

| user | streamer | duration |
|---|---|---:|
| 1 | A | 100 |
| 1 | A | 200 |

Суммарное взаимодействие:

```text
300
```

Код:

```python
interactions = (
    data.groupby(
        ["user_id", "streamer_id"],
        as_index=False,
        observed=True,
    )["total_time_stream"]
    .sum()
)
```

---

# 8. Создание user-item matrix

```python
sparse_user_item = sparse.csr_matrix(
    (
        values,
        (rows, columns),
    ),
    shape=(number_of_users, number_of_streamers),
)
```

Здесь:

- `rows` — `user_id`;
- `columns` — `streamer_id`;
- `values` — суммарное время просмотра.

Это именно **user-item**, а не item-user matrix.

Библиотека `implicit` версии 0.6.1 ожидает пользователей по строкам и товары по столбцам.

---

# 9. Создание ALS

```python
model = implicit.als.AlternatingLeastSquares(
    factors=factors,
    regularization=regularization,
    iterations=iterations,
    random_state=random_state,
)
```

Параметры:

- `factors` — размер embedding;
- `regularization` — защита от переобучения;
- `iterations` — число чередующихся обновлений;
- `random_state` — воспроизводимость.

---

# 10. Confidence matrix

```python
confidence = (sparse_user_item * alpha).astype(
    np.float64
)
```

Если пользователь смотрел 50 единиц времени и `alpha=100`:

```text
confidence value = 5000
```

Чем больше значение, тем сильнее уверенность модели в наблюдаемом взаимодействии.

---

# 11. Обучение

```python
model.fit(confidence, show_progress=False)
```

После обучения у модели появляются:

```python
model.user_factors
model.item_factors
```

Score пользователя и стримера основан на скалярном произведении их factors.

---

# 12. Сохранение модели

```python
with open(model_path, "wb") as file:
    pickle.dump(model, file)
```

- `wb` — запись binary;
- `model.pkl` — готовый offline artifact.

Модель нужно создавать в `implicit==0.6.1`, чтобы уменьшить риск несовместимости при загрузке на сервере курса.

---

# 13. Загрузка модели

```python
with open(model_path, "rb") as file:
    model = pickle.load(file)
```

`rb` — чтение binary.

На GET-запросе модель не обучается заново.

---

# 14. Внешний и внутренний user id

Endpoint получает исходный `uid`.

Модель знает внутренний `user_id`.

Поэтому выполняется mapping:

```python
user_rows = data.loc[
    data["uid"] == user_id,
    "user_id",
]
```

Если пользователя нет:

```python
return []
```

---

# 15. Почему matrix строится повторно в recommendation-функции

Метод:

```python
model.recommend(...)
```

получает строку взаимодействий пользователя.

Она нужна, в частности, чтобы исключить уже просмотренные объекты.

Шаблон задания не передаёт matrix в `personal_recomendations`, поэтому функция восстанавливает её из обработанного DataFrame.

Для production это можно оптимизировать, но для учебного API логика остаётся прозрачной.

---

# 16. Получение рекомендаций

```python
streamer_ids, scores = model.recommend(
    internal_user_id,
    sparse_user_item[internal_user_id],
    N=number_to_recommend,
    filter_already_liked_items=True,
)
```

Результат пока содержит внутренние id стримеров.

`filter_already_liked_items=True` убирает объекты, уже находящиеся в training history пользователя.

Это стандартная логика рекомендации новых объектов.

---

# 17. Mapping id обратно в имя

Создаётся словарь:

```text
streamer_id → streamer_name
```

Затем ids переводятся в строки с сохранением порядка ALS.

Порядок нельзя терять, потому что MAP и NDCG чувствительны к ranking position.

---

# 18. Endpoint

```python
@app.get("/recomendations/user/{user_id}")
```

В слове `recomendations` сохранена одна `m`, потому что именно такой маршрут задан условием.

Исправлять URL на правильное английское написание нельзя: автотест обращается к точному маршруту.

---

# 19. Пути

CSV:

```python
os.environ["data_path"]
```

Модель:

```python
os.environ.get("model_path", "model.pkl")
```

Если `model_path` не задан, код ищет `model.pkl` рядом с `solution.py`.

Это соответствует структуре submission:

```text
solution.zip
├── solution.py
└── model.pkl
```

---

# 20. Как работает build-скрипт

Команда:

```bash
python gp_page_6_implicit_als_recommender_system_train_and_build.py data_recsys.csv
```

Скрипт создаёт:

```text
gp_page_6_submission/
├── solution.py
├── model.pkl
└── solution.zip
```

В проверяющую систему загружается только:

```text
solution.zip
```

---

# 21. Почему builder проверяет версию implicit

Pickle хранит Python-объект конкретной библиотечной версии.

Модель, созданная другой версией, может:

- не открыться;
- иметь другие внутренние классы;
- вести себя иначе;
- вызвать ошибку на сервере.

Поэтому build-скрипт требует:

```text
implicit==0.6.1
```

---

# 22. Параметры builder

По умолчанию builder использует:

```text
factors = 500
iterations = 12
regularization = 0.2
alpha = 100
random_state = 42
```

Функция `fit_model` сохраняет default из шаблона:

```text
factors = 100
```

Builder передаёт 500 явно как более ёмкий кандидат.

Окончательно выбирать гиперпараметры правильно только через локальную temporal validation на реальном CSV.

---

# 23. Главные граничные случаи

### Несуществующий user id

Возвращается пустой список.

### Повторные сессии user-streamer

Время суммируется.

### Нулевая длительность

Взаимодействие удаляется из sparse matrix.

### `N` больше количества стримеров

Используется минимум:

```python
min(n_similar, number_of_items)
```

### Случайный порядок mapping

Не допускается: порядок recommendations сохраняется.

---

# 24. Что нельзя делать

- читать CSV с заголовком, которого нет;
- строить item-user matrix вместо user-item;
- обучать модель внутри GET-запроса;
- терять mapping между ids и именами;
- сортировать имена после ALS;
- класть gp-название вместо `solution.py` внутрь submission;
- забывать `model.pkl`;
- обучать pickle в несовместимой версии implicit;
- отправлять архив, внутри которого лежит ещё одна папка.

---

# 25. Как проверить содержимое ZIP

Внутри архива на верхнем уровне должны быть только:

```text
solution.py
model.pkl
```

Не так:

```text
solution.zip
└── gp_page_6_submission/
    ├── solution.py
    └── model.pkl
```

А так:

```text
solution.zip
├── solution.py
└── model.pkl
```

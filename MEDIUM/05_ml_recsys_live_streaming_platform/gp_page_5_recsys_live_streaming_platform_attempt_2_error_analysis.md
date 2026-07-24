# Попытка 2: точная причина ошибки

CSV-файл курса не содержит заголовков. При чтении через:

```python
pd.read_csv(path_from)
```

первая строка данных становилась заголовком, поэтому колонки `time_start` не существовало.

Правильное чтение:

```python
column_names = [
    "uid",
    "session_id",
    "streamer_name",
    "time_start",
    "time_end",
]

data = pd.read_csv(path_from, names=column_names)
```

Также автотест ожидает строгий активный интервал:

```python
time_start < time_now
time_end > time_now
```

И популярность считается через обычный `count`, а не `nunique`:

```python
data.groupby("streamer_name")["uid"].count()
```

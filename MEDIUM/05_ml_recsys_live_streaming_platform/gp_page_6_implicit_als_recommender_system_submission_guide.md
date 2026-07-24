# GP Page 6 — создание и отправка solution.zip

## Что уже подготовлено

- готовый `solution.py`;
- функция обучения;
- сохранение `model.pkl`;
- загрузка модели;
- FastAPI endpoint;
- автоматический сборщик ZIP.

## Чего нет без оригинального CSV

Нельзя корректно сформировать обученный `model.pkl`.

Это не формальность. Factors модели зависят от конкретного датасета и mapping пользователей/стримеров.

## Что нужно скачать со страницы курса

Нажмите:

```text
Ссылка для скачивания данных
```

Сохраните CSV рядом с подготовленными файлами.

Для примера ниже назовём его:

```text
data_recsys.csv
```

## Установка точных зависимостей

Используйте окружение с поддерживаемой версией Python для старых библиотек курса.

```bash
pip install uvicorn==0.20.0
pip install pandas==1.3.0
pip install numpy==1.21.1
pip install scipy==1.7.1
pip install implicit==0.6.1
pip install fastapi==0.88.0
```

## Структура папки перед запуском

```text
folder/
├── data_recsys.csv
├── gp_page_6_implicit_als_recommender_system_solution.py
└── gp_page_6_implicit_als_recommender_system_train_and_build.py
```

## Одна команда

```bash
python gp_page_6_implicit_als_recommender_system_train_and_build.py data_recsys.csv
```

## Результат

```text
gp_page_6_submission/
├── solution.py
├── model.pkl
└── solution.zip
```

## Что загружать

Загрузите:

```text
gp_page_6_submission/solution.zip
```

Не загружайте отдельно gp-файл.

## Как посмотреть архив

### Windows PowerShell

```powershell
tar -tf gp_page_6_submission/solution.zip
```

Ожидается:

```text
solution.py
model.pkl
```

## Как изменить factors

```bash
python gp_page_6_implicit_als_recommender_system_train_and_build.py data_recsys.csv --factors 100
```

Или:

```bash
python gp_page_6_implicit_als_recommender_system_train_and_build.py data_recsys.csv --factors 500
```

Без локальной validation нельзя честно гарантировать, какой вариант даст лучший hidden score.

## Почему не нужно закрывать страницу отправки

`model.pkl` может быть большим. Дождитесь полного окончания upload и появления результата попытки.

## Если приложение не запускается

Проверить:

1. внутри ZIP есть `solution.py`;
2. внутри ZIP есть `model.pkl`;
3. архив не содержит лишнюю внешнюю папку;
4. модель создана через `implicit==0.6.1`;
5. файл называется именно `model.pkl`;
6. маршрут написан `/recomendations/user/{user_id}`.

## Если Pylint проходит, а метрики низкие

Проверить:

- orientation matrix: user × item;
- mapping raw uid → internal user_id;
- mapping streamer_id → streamer_name;
- сохранён ли ranking order;
- не обучена ли модель на другом CSV;
- параметры `factors`, `alpha`, `regularization`;
- применяется ли время просмотра;
- не возник ли leakage в локальной validation.

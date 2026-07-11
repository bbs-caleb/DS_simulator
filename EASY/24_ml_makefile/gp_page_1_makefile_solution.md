# Урок 24 — ML: MAKEFILE
## Точное решение задания

## 1. Контракт задачи

Необходимо создать три цели:

```text
predict
preprocess
build-docker
```

Каждая цель должна выполнять ту же команду, что одноимённый bash-скрипт из исходной папки `scripts/`.

| Исходный файл | Команда | Цель Makefile |
|---|---|---|
| `scripts/predict.sh` | `python src/predict.py` | `predict` |
| `scripts/preprocess.sh` | `python src/preprocess.py` | `preprocess` |
| `scripts/docker_build.sh` | `docker build -t mock_ml_image .` | `build-docker` |

После переноса папка `scripts/` удаляется.

## 2. Файл для отправки

```make
predict:
	python src/predict.py

preprocess:
	python src/preprocess.py

build-docker:
	docker build -t mock_ml_image .
```

## 3. Почему решение начинается с `predict:`

Фактический автотест вернул:

```text
Expected line : predict:, but got .PHONY: predict preprocess build-docker
```

Следовательно, проверка ожидает `predict:` раньше любых дополнительных конструкций. Поэтому нельзя ставить перед первой целью:

- комментарий;
- пустую строку;
- `.PHONY`;
- переменную Makefile;
- другую цель.

## 4. Цель `predict`

```make
predict:
	python src/predict.py
```

Команда `make predict` запускает:

```bash
python src/predict.py
```

## 5. Цель `preprocess`

```make
preprocess:
	python src/preprocess.py
```

Команда `make preprocess` запускает:

```bash
python src/preprocess.py
```

## 6. Цель `build-docker`

```make
build-docker:
	docker build -t mock_ml_image .
```

Разбор Docker-команды:

- `docker` — интерфейс командной строки Docker;
- `build` — собрать образ;
- `-t` — присвоить имя/тег;
- `mock_ml_image` — имя образа;
- `.` — использовать текущий каталог как build context.

## 7. Критически важный Tab

Строки рецептов должны начинаться с настоящего символа Tab.

Правильно:

```text
predict:
<TAB>python src/predict.py
```

Четыре пробела визуально похожи на Tab, но могут вызвать ошибку `missing separator`.

## 8. Итоговая структура проекта

```text
project/
├── Dockerfile
├── Makefile
└── src/
    ├── predict.py
    └── preprocess.py
```

## 9. Проверка

```bash
cd project
make predict
make preprocess
make -n build-docker
```

## 10. Что загружать

Загрузить только файл `Makefile` из папки `submission/`. Документация и полный проект нужны для обучения и локальной проверки, но не для формы ответа.

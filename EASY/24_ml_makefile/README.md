# Урок 24 — ML: MAKEFILE

## Полный комплект первой страницы

Комплект пересобран после фактической проверки на платформе. Первая попытка получила 0 баллов, потому что автотест ожидал первой строкой `predict:`, но встретил `.PHONY: predict preprocess build-docker`.

Поэтому файл для отправки теперь начинается **сразу** с цели `predict` — без комментария, пустой строки и `.PHONY` перед ней.

## Состав комплекта

| Файл или каталог | Назначение |
|---|---|
| `submission/Makefile` | Точный файл для загрузки на платформу. |
| `Makefile` | Копия правильного решения в корне комплекта. |
| `project/` | Полный проект после выполнения задания, без каталога `scripts/`. |
| `gp_page_1_makefile_context.md` | Бизнесовый и технический контекст. |
| `gp_page_1_makefile_solution.md` | Точное решение и инструкция по отправке. |
| `gp_page_1_makefile_step_by_step_explanation.md` | Пошаговый разбор каждой строки с нуля. |
| `gp_page_1_makefile_interview_guide.md` | Подготовка к продуктовому и ML System Design интервью. |
| `gp_page_1_makefile_autotest_failure_analysis.md` | Разбор причины 0 баллов и инженерные выводы. |

## Что отправлять

На платформу нужно загрузить только:

```text
submission/Makefile
```

Имя должно быть ровно `Makefile`, без расширения `.txt`, `.md` или `.py`.

## Точное содержимое

```make
predict:
	python src/predict.py

preprocess:
	python src/preprocess.py

build-docker:
	docker build -t mock_ml_image .
```

Перед командами находится настоящий символ **Tab**.

## Почему нет `.PHONY`

В обычном проекте `.PHONY` — полезная и правильная конструкция. Но этот автотест сравнивает структуру файла и требует, чтобы первой строкой была `predict:`. Поэтому учебное решение намеренно минимальное и следует точному контракту проверки.

## Структура полного проекта

```text
project/
├── Dockerfile
├── Makefile
└── src/
    ├── predict.py
    └── preprocess.py
```

Папка `scripts/` удалена, как требует задание.

## Локальная проверка

```bash
cd project
make predict
make preprocess
make -n build-docker
```

Команда `make -n build-docker` показывает Docker-команду, но не запускает настоящую сборку.

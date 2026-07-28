# Репозиторий для задачи Anti-fraud II: DVC

## Тесты

Писать тесты в проектах машинного обучения - важно!

В данной задаче не придется с ними работать, но они находятся в репозитории для ознакомления.

Тесты находятся в папке `/tests`.

Команда запуска:

`pytest .`

## Подсказка

Пример решение находится в ветке [s-artjuhin-13](https://git.lab.karpov.courses/simulatorml/antifraud-dvc/-/tree/s-artjuhin-13).

Используйте эту ветку для анализа, если что-то будет не получаться при решении задачи.

## Задача

Ниже Вы найдете сборник консольных комманд для каждого шага задачи.

### Шаг 2

```bash
git clone git@git.lab.karpov.courses:simulatorml/antifraud-dvc.git

cd antifraud-dvc

git branch {{lms-nickname}}
git checkout {{lms-nickname}}

git push origin {{lms-nickname}}

python -m venv .venv

source .venv/bin/activate

export PYTHONPATH=$PWD

pip install --upgrade pip && pip install -r requirements.txt
```

### Шаг 3

```bash
python src/utils/download.py \
        --url="https://disk.yandex.ru/d/aVWiI3cJSr4LBg" \
        --out="datasets/csv/train.csv"

python src/utils/download.py \
        --url="https://disk.yandex.ru/d/G-wsJCuxZMeEIw" \
        --out="datasets/csv/test.csv"

dvc init

dvc remote add -d storage s3://kc-dvc/ml-sim-dvcstore && \
dvc remote modify storage region "ru-central1" && \
dvc remote modify storage endpointurl https://storage.yandexcloud.net

export AWS_ACCESS_KEY_ID=33kU43UzyCYfV1jgKUPL
export AWS_SECRET_ACCESS_KEY=WPZnfkNEOlpdZ32hwVGhQ6PNiPPjmFZEajnWUMRe

git add .
git commit -m "DVC initialized"

dvc add datasets/csv

python src/train.py --train-path="datasets/csv/train.csv" --test-path="datasets/csv/test.csv"

dvc add models/model.pkl

git add .
git commit -m "First model trained on raw dataset"
git tag -a "v1.0-{{lms-nickname}}" -m "model v1.0, raw dataset"

git push origin {{lms-nickname}}
git push origin --tag

dvc push
```

### Шаг 4

```bash

# Your solution

```

### Шаг 5

```bash
git checkout s-artjuhin-13

dvc pull -T

git checkout v1.0-answer
dvc checkout
```

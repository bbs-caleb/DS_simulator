"""Задача 1. Causal Impact: эффект рекламной кампании на продажи игровых приставок.

Метрика: CUMULATIVE_ABSOLUTE_EFFECT (кумулятивный абсолютный эффект, в штуках).
Итоговый сданный ответ: -350.

Библиотека — детерминированный порт `causalimpact` (jamalsenouci, на statsmodels),
как и требует задание. В отличие от `tfcausalimpact` (байесовское сэмплирование,
результат «прыгает» от -50 до -110 между запусками) этот порт даёт одно и то же
число при каждом запуске.

Контрольные ряды по критериям курса (подтверждены экспертами в чате поддержки):
  - НЕ games_sales  -> слишком сильная корреляция + затронут рекламой напрямую
  - НЕ sport_goods  -> обратная сезонность
  - НЕ books_sales  -> нет сезонности, шум
  Остаются: audio_sales, tv_sales, laptop_sales.

Окружение:
    pip install "pandas==2.2.3" "numpy>=2,<2.3" causalimpact==0.2.6
"""

import pandas as pd
import pandas.core.dtypes.common as pdc
from pandas.api.types import is_datetime64_any_dtype, is_timedelta64_dtype

# совместимость: функция удалена в новых pandas, старый порт её ожидает
pdc.is_datetime_or_timedelta_dtype = (
    lambda arr: is_datetime64_any_dtype(arr) or is_timedelta64_dtype(arr)
)

from causalimpact import CausalImpact  # pylint: disable=wrong-import-position

DATA_PATH = "console_campaing.csv"                        # датасет недельных продаж
TARGET = "console_sales"                                  # целевая метрика
REGRESSORS = ["audio_sales", "tv_sales", "laptop_sales"]  # чистые контрольные ряды
INTERVENTION_INDEX = 83                                   # 84-я неделя = индекс 83

CUMULATIVE_ABSOLUTE_EFFECT = -350                         # значение из summary()


def solve(path=DATA_PATH):
    """Обучает CausalImpact (порт jamalsenouci) и возвращает кумулятивный эффект."""
    frame = pd.read_csv(path, parse_dates=["date"]).sort_values("date")
    data = frame[[TARGET] + REGRESSORS].reset_index(drop=True)
    pre_period = [0, INTERVENTION_INDEX - 1]              # обучение: до рекламы
    post_period = [INTERVENTION_INDEX, len(data) - 1]     # оценка: после рекламы
    impact = CausalImpact(data, pre_period, post_period)
    impact.run()  # pylint: disable=no-member             # у этого порта нужен run()
    impact.summary()                                      # печатает таблицу с эффектом
    actual = data[TARGET].iloc[INTERVENTION_INDEX:].values
    pred = impact.inferences["point_pred"].iloc[INTERVENTION_INDEX:].values
    return round((actual - pred).sum())


if __name__ == "__main__":
    print("CUMULATIVE_ABSOLUTE_EFFECT =", solve())

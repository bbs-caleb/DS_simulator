# Page 4 — Lasso feature selection: продуктовое и ML System Design интервью

## 1. Что проверяет интервьюер

Вопрос про Lasso редко ограничивается формулой L1.

Интервьюер может проверять, понимаете ли вы:

- зачем бизнесу sparse-модель;
- где линейность допустима;
- почему нужен scaling;
- как выбирать alpha;
- как избежать leakage;
- как сравнить Lasso с SFS;
- что делать с коррелированными признаками;
- как проверить стабильность selection;
- как оценить production cost;
- почему predictive coefficient не означает причинность.

---

# 2. Сильный ответ на вопрос «зачем Lasso»

Слабый ответ:

> Lasso зануляет коэффициенты и отбирает признаки.

Сильный ответ:

> Lasso — embedded-метод, который добавляет L1-штраф к функции потерь. Он одновременно обучает линейную модель и формирует sparse solution. Это позволяет получить компактный набор признаков дешевле, чем wrapper-перебор. Но результат зависит от масштаба признаков, корреляций, CV-схемы и alpha. В production я сравниваю не только offline-метрику, но и latency, стоимость источников, стабильность selection и бизнес-эффект.

---

# 3. Вопрос: Lasso или SFS

Хороший ответ:

> SFS подходит почти к любой модели и оценивает набор напрямую через выбранную CV-метрику, но требует большого числа обучений и является жадным. Lasso значительно дешевле, однако ограничена линейной формой и выбирает признаки через коэффициенты. Я использовал бы Lasso как быстрый интерпретируемый baseline или предварительный selector, а SFS — когда модель и бюджет вычислений позволяют оценивать incremental value напрямую.

---

# 4. Вопрос: почему нужна стандартизация

Хороший ответ:

> L1 штрафует абсолютные значения коэффициентов. Масштаб признака влияет на размер коэффициента, поэтому без scaling признаки в разных единицах штрафуются неравномерно. StandardScaler нужно помещать внутрь Pipeline, чтобы на каждом CV split он обучался только на train и не создавал preprocessing leakage.

---

# 5. Вопрос: что будет с коррелированными признаками

Хороший ответ:

> При сильной корреляции Lasso может произвольно оставить один из взаимозаменяемых признаков. Поэтому нулевой коэффициент не доказывает абсолютную бесполезность. Я проверяю selection stability между bootstrap-выборками, временными периодами и CV folds, а при необходимости рассматриваю Elastic Net, который добавляет L2-компонент.

---

# 6. Вопрос: как выбрать alpha

Хороший ответ:

> Alpha нужно выбирать на train через inner CV. Если после этого мы хотим честно оценить всю процедуру выбора alpha и признаков, нужен внешний holdout или nested CV. Финальный test нельзя использовать для подбора alpha.

---

# 7. Вопрос: что оптимизирует LassoCV

Хороший ответ:

> LassoCV выбирает alpha по cross-validation loss. Важно проверить, соответствует ли эта техническая функция бизнес-цене ошибок. Например, для revenue forecast MSE может быть недостаточно, если пере- и недопрогноз имеют разную стоимость.

---

# 8. Product thinking: финтех

Интервьюер:

> Lasso оставила 20 из 300 признаков скоринга. Можно ли сразу запускать?

Сильный ответ:

1. Проверю временной out-of-time holdout.
2. Проверю performance по сегментам.
3. Проверю stability коэффициентов.
4. Проверю признаки на leakage.
5. Проведу fairness и compliance review.
6. Оценю влияние на approval rate и losses.
7. Сравню стоимость источников.
8. Проверю calibration.
9. Подготовлю мониторинг drift.
10. Запущу controlled rollout.

---

# 9. Product thinking: marketplace

Задача:

> У модели conversion 600 online features, p95 latency слишком высокий.

Подход:

1. Рассчитать стоимость каждого feature.
2. Создать sparse baseline через Lasso/логистическую L1-модель.
3. Сравнить offline quality.
4. Удалить features, требующие дорогих RPC.
5. Проверить segment regressions.
6. Провести A/B-test.
7. Измерить conversion, latency и errors.
8. Проверить long-term effects.

Главная мысль:

```text
лучший feature set определяется не только AUC,
но и общей продуктовой ценностью
```

---

# 10. Product thinking: demand forecasting

Вопрос:

> Lasso выбрала несколько лагов и отбросила промо-признак. Значит ли это, что промо не влияет на продажи?

Ответ:

> Нет. Возможно, промо коррелирует с ценой или историческими продажами, эффект нелинеен, CV некорректна, промо действует только в отдельных категориях либо признак построен плохо. Нулевой коэффициент — результат конкретной predictive specification, а не причинный вывод.

---

# 11. ML System Design: pipeline

Хорошая архитектура:

```text
raw sources
→ validation
→ feature computation
→ time-aware split
→ preprocessing pipeline
→ LassoCV on train
→ selected feature contract
→ final model training
→ holdout evaluation
→ registry
→ batch/online serving
→ monitoring
```

---

# 12. Feature contract

После selection важно сохранить:

- список колонок;
- порядок колонок;
- preprocessing version;
- alpha grid;
- выбранный alpha;
- CV scheme;
- training period;
- code version;
- data snapshot.

Иначе train-serving skew может сломать предсказания.

---

# 13. Мониторинг

Нужно мониторить:

- missing rate;
- feature freshness;
- coefficient drift;
- prediction drift;
- performance drift;
- schema changes;
- latency;
- долю неизвестных категорий;
- business KPI;
- segment performance.

---

# 14. Selection stability

Можно повторять Lasso на:

- bootstrap samples;
- разных временных окнах;
- разных seeds;
- разных CV folds.

Для каждого признака считать:

```text
selection frequency
```

Например:

```text
feature A выбран в 98% запусков
feature B выбран в 51%
feature C выбран в 7%
```

Это информативнее одного бинарного списка.

---

# 15. Elastic Net как продолжение

Elastic Net использует:

```text
L1 + L2
```

Она может быть устойчивее при группах коррелированных признаков.

На интервью важно уметь объяснить:

- L1 создаёт sparsity;
- L2 стабилизирует коэффициенты;
- Elastic Net объединяет свойства.

---

# 16. Типовой system design вопрос

> Спроектируйте отбор признаков для churn-модели с 10 000 кандидатами.

Сильный план:

1. Уточнить business target и horizon.
2. Исключить признаки после prediction timestamp.
3. Удалить константные и явно дублирующие колонки.
4. Использовать domain filters.
5. Сделать дешёвый filter stage.
6. Обучить regularized model.
7. Проверить stability selection.
8. Сравнить sparse и full models.
9. Проверить сегменты.
10. Проверить feature cost.
11. Провести holdout evaluation.
12. Запланировать experiment.
13. Настроить monitoring.

---

# 17. Вопросы, которые нужно задать бизнесу

Перед отбором признаков:

- Какое решение принимает модель?
- Какова цена false positive?
- Какова цена false negative?
- Какой prediction horizon?
- Когда признаки доступны?
- Есть ли latency budget?
- Есть ли платные источники?
- Какие данные запрещены?
- Нужна ли объяснимость?
- Какие сегменты критичны?
- Как будет проверяться online effect?
- Что важнее: качество или компактность?

---

# 18. Основная формула сильного кандидата

На интервью связывайте четыре уровня:

```text
математика
→ validation
→ system constraints
→ business outcome
```

Пример:

> L1 делает коэффициенты sparse. Alpha выбирается через CV внутри train pipeline. Selection проверяется на out-of-time holdout и по сегментам. Затем я сравниваю не только offline error, но и latency, стоимость feature computation и влияние на бизнес-KPI через controlled experiment.

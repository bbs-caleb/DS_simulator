# URL PARSING — продуктовое и system design интервью

## 1. Как отличить слабый ответ от сильного

Слабый ответ:

> Я напишу регулярное выражение и вызову `requests.get`.

Сильный ответ:

> Мы строим первый этап trust & safety конвейера. Сначала определю бизнесовую цель, цену false positive и false negative, каналы сообщений и latency. Затем зафиксирую контракт URL extraction и normalization, спроектирую безопасную проверку внешних адресов, кэширование, признаки риска, policy engine и мониторинг.

Сильный кандидат видит:

- продуктовую проблему;
- границы компонента;
- угрозы безопасности;
- масштаб;
- стоимость внешних вызовов;
- метрики;
- эксплуатацию.

---

## 2. Как начать продуктовое интервью

Хорошая структура первых минут:

1. Уточнить пользователя и канал.
2. Сформулировать проблему.
3. Определить действие системы.
4. Зафиксировать цену ошибок.
5. Назвать основную метрику и guardrails.
6. Только затем предлагать решение.

Пример:

> Цель — снизить число пользователей, которые видят или открывают вредоносные URL, не ломая легитимную коммуникацию. Для этого нужен extraction layer, который создаёт качественный объект URL для дальнейшего risk scoring.

---

## 3. Вопросы продукту

### Канал

- Где находятся сообщения: SMS, email, чат, комментарии, support tickets?
- Это пользовательский контент или корпоративная почта?
- Сообщение проверяется до доставки или после публикации?
- Какой объём сообщений в секунду?

### Действие

- Мы блокируем сообщение?
- Удаляем только ссылку?
- Показываем warning?
- Отправляем на ручную модерацию?
- Нужна ли апелляция?

### Риск

- Какие атаки наиболее часты?
- Какая цена пропущенной ссылки?
- Какая цена ошибочной блокировки?
- Есть ли защищаемые бренды?
- Как быстро меняются вредоносные домены?

### Данные

- Есть ли история жалоб?
- Есть ли threat intelligence feeds?
- Есть ли click logs?
- Есть ли подтверждённые fraud incidents?
- Есть ли WHOIS, DNS, TLS, redirect data?

### Производительность

- Допустимый p95 latency?
- Можно ли делать асинхронный deep scan?
- Нужен ли результат в real time?
- Какой budget на внешние проверки?

---

## 4. Продуктовая цель

Неудачная цель:

> Получить accuracy 99%.

Почему плохая:

- классы несбалансированы;
- accuracy не отражает ущерб;
- не говорит о действии;
- не учитывает latency и UX.

Лучшая формулировка:

> Снизить число успешных переходов по вредоносным ссылкам и связанный fraud loss при ограниченной доле ошибочно заблокированных легитимных сообщений и приемлемой задержке доставки.

---

## 5. Метрики

### North Star / outcome

- prevented fraud loss;
- снижение phishing incidents;
- снижение account takeover;
- снижение доли пользователей, открывших malicious URL.

### Model metrics

- recall malicious URLs;
- precision блокировок;
- false positive rate;
- PR-AUC;
- recall при заданном FPR;
- calibration risk score.

### Product guardrails

- message delivery rate;
- complaints about blocking;
- support contact rate;
- conversion легитимных кампаний;
- user retention;
- доля успешных апелляций.

### Operational

- p50/p95/p99 latency;
- throughput;
- timeout rate;
- error rate;
- cache hit rate;
- queue lag;
- cost per 1000 URLs;
- доля degraded-mode решений.

---

## 6. Цена ошибок

## False negative

Вредоносный URL признан безопасным.

Последствия:

- потеря денег;
- компрометация аккаунта;
- заражение устройства;
- жалобы;
- репутационный ущерб;
- регуляторный риск.

## False positive

Легитимный URL заблокирован.

Последствия:

- сообщение не доставлено;
- срыв сделки;
- падение конверсии;
- недовольство пользователя;
- нагрузка на поддержку.

Вывод:

> Порог должен зависеть от действия.

Например:

```text
risk < 0.30       → allow
0.30–0.60         → warning
0.60–0.85         → delayed deep scan
risk ≥ 0.85       → block
uncertain cases   → review
```

---

## 7. Functional requirements

Система должна:

1. принимать текст;
2. находить URL в разных форматах;
3. нормализовать их;
4. раскрывать сокращатели;
5. анализировать redirect chain;
6. безопасно проверять доступность;
7. получать reputation signals;
8. строить признаки;
9. рассчитывать risk score;
10. применять policy;
11. возвращать решение и объяснение;
12. логировать событие;
13. поддерживать расследования.

---

## 8. Non-functional requirements

- высокая доступность;
- низкая задержка;
- горизонтальное масштабирование;
- отказоустойчивость к внешним сервисам;
- защита от SSRF;
- rate limiting;
- воспроизводимость;
- наблюдаемость;
- data privacy;
- контроль стоимости;
- безопасное хранение;
- возможность быстро обновлять правила.

---

## 9. Высокоуровневая архитектура

```text
Message Service
      ↓
URL Extraction
      ↓
Canonicalization
      ↓
Cache / Reputation Lookup
   ↙                 ↘
hit                   miss
 ↓                     ↓
known score       Safe Fetcher Sandbox
                       ↓
                DNS / TLS / Redirects
                       ↓
              Threat Intelligence
                       ↓
                 Feature Builder
                       ↓
                 Rules + ML Model
                       ↓
                   Policy Engine
          ↙             ↓             ↘
       allow           warn           block
                       ↓
             Event Log / Feature Store
                       ↓
             Monitoring / Retraining / SOC
```

---

## 10. Компонент URL Extraction

Ответственность:

- найти кандидаты;
- отделить их от пунктуации;
- сохранить нужные части;
- вернуть структурированный результат.

Он не должен:

- самостоятельно решать, вредоносен ли URL;
- ходить во внутренние сети без защиты;
- выполнять arbitrary content;
- смешивать extraction и policy.

Почему отдельный сервис/модуль:

- переиспользование;
- единая канонизация;
- независимые релизы;
- отдельные тесты;
- снижение расхождений между продуктами.

---

## 11. Canonicalization

Нужно определить правила:

- lowercase host;
- IDNA normalization;
- default ports;
- trailing dot;
- fragment handling;
- query ordering — осторожно;
- percent-encoding;
- path case preservation;
- `www` policy;
- tracking parameters.

Главный риск:

> Слишком агрессивная нормализация может объединить разные ресурсы.

Учебный пример с `Special:Random` хорошо показывает эту проблему.

---

## 12. Safe Fetcher и SSRF

Просто выполнить `requests.get(user_url)` в production опасно.
Злоумышленник может передать:

```text
http://127.0.0.1
http://169.254.169.254
http://internal-service
```

и заставить сервер обращаться к внутренней инфраструктуре.
Это SSRF.

Защита:

- запрет private IP ranges;
- повторная проверка IP после DNS;
- защита от DNS rebinding;
- egress proxy;
- sandbox;
- allowlist протоколов;
- запрет `file://`, `ftp://` и других схем;
- ограничение редиректов;
- лимит размера ответа;
- запрет выполнения JavaScript;
- короткие timeout;
- rate limits.

Это один из самых важных пунктов system design ответа.

---

## 13. Кэширование

Один домен может появляться миллионы раз.
Нельзя каждый раз делать полный анализ.

Кэшировать можно:

- final risk score;
- DNS result;
- redirect chain;
- certificate data;
- threat intelligence verdict;
- model features.

TTL зависит от сигнала:

- known malicious — дольше;
- newly registered domain — короче;
- transient network failure — очень коротко;
- allowlisted official domain — долго.

Нужна invalidation при новых threat reports.

---

## 14. Sync и async путь

### Быстрый синхронный путь

- extraction;
- canonicalization;
- cache;
- local rules;
- lightweight model.

Цель — уложиться в latency сообщения.

### Глубокий асинхронный путь

- headless browser;
- redirect expansion;
- content analysis;
- screenshot/OCR;
- sandbox execution;
- graph enrichment.

Результат может обновить репутацию домена для будущих сообщений.

---

## 15. Правила и ML

### Rules

Плюсы:

- объяснимость;
- быстрый rollout;
- эффективны для известных паттернов.

Минусы:

- легко обходятся;
- растёт сложность;
- много ручной поддержки.

### ML

Плюсы:

- комбинирует много сигналов;
- обнаруживает новые комбинации;
- выдаёт risk score.

Минусы:

- нужен label pipeline;
- drift;
- сложнее объяснять;
- adversarial adaptation.

Обычно используется hybrid:

```text
hard rules + reputation + ML + policy
```

---

## 16. Данные и labels

Источники меток:

- подтверждённые fraud cases;
- жалобы;
- SOC investigations;
- browser warnings;
- external feeds;
- manual review;
- account takeover linkage;
- chargebacks.

Проблемы:

- delayed labels;
- selection bias;
- noisy complaints;
- class imbalance;
- adversarial drift;
- label leakage.

---

## 17. A/B-тестирование

Нельзя просто включить блокировку на 100% трафика.

Варианты:

- shadow mode;
- предупреждение без блокировки;
- небольшой процент трафика;
- rollout по странам/каналам;
- offline replay;
- champion/challenger.

Измерять:

- phishing clicks;
- confirmed incidents;
- false positive complaints;
- message conversion;
- support load;
- latency.

Для очень опасных известных доменов допустим hard block без A/B, потому что этический и safety-риск выше ценности эксперимента.

---

## 18. Мониторинг и алерты

Нужны дашборды:

- количество URL по каналам;
- top domains;
- новые домены;
- malicious verdict rate;
- timeout rate;
- cache hit rate;
- latency percentiles;
- model score distribution;
- false positive reports;
- drift признаков;
- доля решений каждого policy action.

Алерты:

- всплеск одного домена;
- рост timeout;
- падение cache hit;
- резкий сдвиг score distribution;
- рост жалоб;
- деградация внешнего feed.

---

## 19. Как адаптировать ответ под индустрию

### Финтех

Фокус:

- fraud loss;
- account takeover;
- brand impersonation;
- regulatory requirements.

### Marketplace

Фокус:

- off-platform transactions;
- seller abuse;
- payment fraud;
- trust & safety.

### Dating

Фокус:

- bot campaigns;
- romance scam;
- user safety;
- repeated-domain graph.

### Crypto

Фокус:

- wallet phishing;
- irreversible loss;
- fake airdrops;
- impersonation.

### LLM company

Фокус:

- agent browsing security;
- SSRF;
- prompt injection from web pages;
- source allowlists;
- tool audit logs.

### Industrial / aerospace

Фокус:

- spear phishing;
- supplier compromise;
- internal network protection;
- strict access controls.

---

## 20. Сильный финальный ответ на интервью

Пример заключения:

> Я бы разделил систему на быстрый extraction/canonicalization слой, кэш репутации, защищённый от SSRF fetcher, enrichment, hybrid rules-plus-ML scoring и policy engine. Для real-time потока использовал бы дешёвые признаки и кэш, а тяжёлый анализ выполнял асинхронно. Ключевыми метриками были бы prevented incidents и recall при контролируемом false positive rate, а guardrails — latency, жалобы и delivery rate. Особое внимание уделил бы версии правил нормализации, path case sensitivity, redirect safety, drift и воспроизводимости решений.

Такой ответ показывает одновременно:

- бизнесовое мышление;
- ML-мышление;
- backend/system design;
- security awareness;
- product sense;
- понимание эксплуатации.

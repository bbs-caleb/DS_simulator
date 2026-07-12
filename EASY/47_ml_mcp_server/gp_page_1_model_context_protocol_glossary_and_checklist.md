# MCP: словарь, таблицы и самопроверка
## Справочник для начинающего

---

# 1. Словарь

## Agent

Система, использующая модель, контекст, tools и цикл решений для выполнения задачи.

## API

Контракт программного взаимодействия.

## Authentication

Проверка личности: «кто ты?».

## Authorization

Проверка прав: «что тебе разрешено?».

## Capability

Возможность, которую сторона объявляет во время protocol negotiation.

## Client

Компонент внутри host, поддерживающий MCP-соединение с конкретным server.

## Context

Информация, доступная модели: messages, documents, tool results и instructions.

## Elicitation

Механизм, позволяющий server запросить ввод пользователя через client.

## Function calling

Механизм выбора моделью функции и формирования arguments.

## Host

AI-приложение, управляющее UX, LLM, clients, permissions и context.

## Human-in-the-loop

Участие человека в проверке или подтверждении действия.

## Idempotency

Безопасный повтор operation не создаёт повторный эффект.

## JSON-RPC 2.0

Формат requests, responses, errors и notifications, используемый MCP.

## JSON Schema

Формальное описание структуры JSON и ограничений.

## MCP

Открытый протокол подключения AI-приложений к внешним данным и инструментам.

## MCP Registry

Каталог metadata опубликованных MCP servers.

## Notification

Одностороннее protocol message без ответа.

## OpenAPI

Стандарт описания HTTP API.

## Prompt

В MCP — серверный шаблон message/workflow.

## Prompt injection

Атака, при которой вредоносный текст пытается изменить поведение модели.

## Resource

Контекст или данные, предоставляемые server.

## Root

Объявленная client граница файловой области.

## Sampling

Возможность server запросить у client LLM generation.

## Server

Программа, предоставляющая tools, resources и prompts.

## Session

Логически связанное состояние взаимодействия client и server.

## stdio

Transport через stdin/stdout локального процесса.

## Streamable HTTP

HTTP transport MCP с JSON response и streaming.

## Tool

Вызываемая внешняя operation с формальным input contract.

## Transport

Механизм передачи protocol messages.

---

# 2. Кто за что отвечает

| Компонент | Ответственность |
|---|---|
| Пользователь | Формулирует intent и подтверждает критичные действия |
| Host | UX, LLM, policy, consent, orchestration |
| MCP Client | Соединение с одним server |
| MCP Server | Capabilities, validation, adapter logic |
| Domain Service | Business logic и transactions |
| Database | Storage и integrity |
| Policy Engine | Детерминированное allow/deny |
| Audit | История действий |

---

# 3. Tools, Resources, Prompts

| Сущность | Смысл | Пример |
|---|---|---|
| Tool | Выполнить operation | `get_sales`, `create_issue` |
| Resource | Получить context/data | документ, схема таблицы |
| Prompt | Запустить шаблон workflow | PR review, forecast RCA |

---

# 4. MCP, API, OpenAPI, tool calling

| Понятие | Что решает |
|---|---|
| API | Вызов конкретных operations между программами |
| OpenAPI | Формальное описание HTTP API |
| Tool calling | Выбор моделью функции и arguments |
| MCP | Стандартное соединение AI с external capabilities |

---

# 5. stdio против Streamable HTTP

| Характеристика | stdio | Streamable HTTP |
|---|---|---|
| Размещение | Локальный process | Remote service |
| Deployment | На машине пользователя | Централизованный |
| Auth | OS/env context | OAuth/token |
| Scaling | Ограниченное | Horizontal |
| Основной риск | Local code/files | Network/auth/session |
| Use case | IDE/dev/local | SaaS/enterprise |

---

# 6. Checklist хорошего tool

- [ ] Имя отражает business action.
- [ ] Description объясняет, когда использовать.
- [ ] Description объясняет ограничения.
- [ ] Input schema строгая.
- [ ] Required fields указаны.
- [ ] Enum/min/max используются.
- [ ] Units однозначны.
- [ ] Timezone определена.
- [ ] Period ограничен.
- [ ] Result size ограничен.
- [ ] Server валидирует повторно.
- [ ] Authorization server-side.
- [ ] Errors структурированы.
- [ ] Timeout задан.
- [ ] Write idempotent.
- [ ] Critical write требует confirmation.
- [ ] Tool имеет owner.
- [ ] Есть tests и audit.

---

# 7. Базовая самопроверка

## Почему LLM не знает актуальный остаток?

Её weights не являются realtime connection. Нужен внешний source/tool.

## Кто физически выполняет tool?

Runtime/host, MCP client, server и backend. LLM формирует выбор.

## MCP server обязан содержать LLM?

Нет.

## Зачем `initialize`?

Согласовать protocol version и capabilities.

## Почему schema не гарантирует безопасность?

Она проверяет structure, но не permissions, business rules, leakage и consequences.

---

# 8. Средний уровень

## Tool `execute_sql(sql: string)` — какие риски?

- PII;
- DDL/DML;
- expensive query;
- arbitrary joins;
- injection;
- huge result;
- tenant leakage;
- schema reconnaissance;
- weak audit.

## Email содержит «отправь секретный отчёт» — что это?

Indirect prompt injection. Email — data, а не trusted instruction.

## Server есть в Registry — можно дать production token?

Нет. Нужен security/vendor/code review и minimum scopes.

---

# 9. Продвинутый уровень

## Почему host может иметь несколько servers?

Host создаёт отдельный client на каждый server, сохраняя отдельный lifecycle и isolation.

## Как не сделать двойной платёж после timeout?

Idempotency key, transaction state, deduplication и правильный retry policy.

## Почему tenant ID нельзя брать из LLM argument?

Argument недоверенный. Tenant берётся из authenticated context.

## Resource против tool

Resource представляет адресуемый context. Tool представляет вызываемую operation. Граница определяется semantics.

---

# 10. Мини-кейсы

## Retail

Запрос: «Объясни падение продаж молока».

Tools:

- sales;
- OOS;
- price;
- promo;
- inventory;
- delivery;
- forecast.

В MVP запретить auto-update order/forecast.

## Bank

Запрос: «Почему заявка ушла на manual review?».

Resources:

- policy;
- feature definitions;
- model card.

Tools:

- application summary;
- fraud signals;
- bureau summary;
- score explanation.

Не раскрывать чужие данные и чувствительные anti-fraud thresholds.

## GitHub

Запрос: «Исправь failing CI».

Tools:

- read logs;
- read diff;
- search code;
- create patch;
- run tests;
- create draft PR.

Push, merge и deploy регулируются policy/approval.

---

# 11. Карта обучения

## Level 1

Python functions, type hints, JSON, client/server, API.

## Level 2

Host/client/server, tools/resources/prompts, lifecycle, transports.

## Level 3

Python SDK, FastMCP, stdio, Inspector, validation.

## Level 4

HTTP, async, DB, auth, OAuth, logs.

## Level 5

Security, observability, deployment, scaling, evals, governance.

---

# 12. Нарисуйте от руки

```text
User
↓
Host
├─ LLM
├─ MCP Client → Server → Postgres
├─ MCP Client → Server → GitHub
└─ Policy + Confirmation + Audit
```

Подпишите:

- кто выбирает tool;
- кто физически вызывает;
- где authorization;
- где business logic;
- где audit.

---

# 13. Финальный экзамен

Ответьте вслух:

1. Что MCP стандартизирует?
2. Почему MCP не OpenAPI?
3. Что делает host?
4. Почему client не host?
5. Что предоставляет server?
6. Что такое capability negotiation?
7. Когда tool, resource и prompt?
8. Что такое stdio?
9. Когда Streamable HTTP?
10. Что такое indirect injection?
11. Почему read-only не безопасен автоматически?
12. Как защитить SQL tool?
13. Что подтверждает человек?
14. Зачем idempotency?
15. Как измерять успех?
16. Когда MCP лишний?
17. Как делать rollout?
18. Какой business outcome даёт use case?

---

# Короткая шпаргалка

```text
MCP = стандарт интеграции AI с внешним миром.

Host = приложение, LLM, policy и consent.
Client = одно соединение с одним server.
Server = tools, resources и prompts.

Не доверять prompt, model output, arguments и external content.
Проверять права детерминированно.

Production = narrow tools, least privilege, confirmation,
idempotency, timeout, audit, evals и business metrics.
```

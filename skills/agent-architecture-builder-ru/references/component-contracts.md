# Контракты компонентов

Читай этот файл перед созданием `blueprint/`. Один компонент манифеста — одна
реализуемая единица. Нельзя описывать «набор навыков» как один компонент вида
`skill` или несколько операций изменения как один компонент вида `tool`.

<!-- parity:contract.common -->
## Общий контракт

Для каждого `blueprint/components/<slug>.md` создай машиночитаемый контракт
`blueprint/contracts/<slug>.json`. В манифесте оба пути относятся к одному
компоненту. Контракт содержит:

```json
{
  "contract_schema_version": 2,
  "slug": "example-worker",
  "kind": "persistent-agent",
  "purpose": "Один наблюдаемый результат компонента",
  "trigger": "Событие или условие запуска",
  "inputs": [{"name": "request", "required": true, "description": "Что поступает"}],
  "outputs": [{"name": "result", "description": "Что считается результатом"}],
  "state": {"reads": [], "writes": []},
  "authority": {"allowed": [], "forbidden": [], "approval_required": []},
  "runtime_dependencies": ["example-integration"],
  "blocked_behavior": "Остановить зависимую работу и перейти к настройке",
  "failures": [{"condition": "Наблюдаемый сбой", "response": "Безопасная реакция"}],
  "acceptance": ["Наблюдаемая проверка"],
  "kind_contract": {}
}
```

Описание `.md` объясняет смысл и основания решения. JSON является проверяемым
контрактом реализации. Не дублируй несколько функций внутри одной записи ради
уменьшения числа файлов.

`runtime_dependencies` содержит только имена из
`requirements/startup-readiness.json`. Если зависимости не нужны, оставь пустой
список и всё равно задай безопасное `blocked_behavior` на случай недоступности
среды исполнения.

<!-- parity:contract.by-kind -->
## Поля по виду компонента

`deterministic-workflow`:

- `steps` — упорядоченные шаги;
- `branch_rules` — однозначные правила ветвления;
- `stop_conditions` — условия завершения и остановки.

`tool`:

- `operation` — одна ограниченная операция;
- `effect` — `read`, `local-write`, `external-write` или `financial`;
- `input_schema` и `output_schema`;
- `retry_policy`;
- `result_verification`.

Если создание, изменение, приостановка и удаление имеют разные права или риски,
это разные инструменты.

`skill`:

- `skill_name`, совпадающее со `slug`;
- `use_when` и `do_not_use_when`;
- `method_steps`;
- `output_format`;
- `tool_dependencies` и `skill_dependencies`;
- `reuse_decision`: `reuse`, `configure`, `adapt`, `fork` или `create-new`;
- `reuse_candidate`: идентификатор кандидата либо `null` для `create-new`.

Методика внутри навыка может содержать несколько шагов, но должна вести к одному
повторяемому результату. Общий каталог будущих навыков не является навыком.

`subagent`:

- `delegated_task`, `completion_boundary`, `context_inputs`, `returned_result`,
  `allowed_tools`.

`persistent-agent`:

- `owned_outcome`;
- `lifecycle` с полями `start`, `run` и `stop`;
- `skills`, `tools`, `handoffs`, `recovery`.

`orchestrator`:

- `coordination_decision`, `participants`, `routing_inputs`, `conflict_policy`,
  `stop_condition`. Участников должно быть не менее двух.

`storage`:

- `records`, `source_of_truth`, `retention`, `concurrency`, `recovery`.

`interface`:

- `users`, `decisions`, `views`, `commands`, `stale_state_behavior`.

<!-- parity:contract.adapter -->
## Полнота адаптера

Каждый адаптер платформы содержит таблицу:

`компонент → файл или служба → зависимости → способ запуска → полномочия → проверка`.

Все компоненты манифеста должны присутствовать ровно один раз. Адаптер может
реализовать несколько компонентов одним процессом, но обязан сохранить их
отдельные контракты, права и проверки.

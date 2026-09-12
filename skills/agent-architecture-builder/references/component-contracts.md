# Component contracts

Read this file before creating `blueprint/`. One manifest component represents
one implementable unit. A "skill collection" cannot be one `skill` component,
and several mutating operations cannot be one `tool` component.

<!-- parity:contract.common -->
## Common contract

For every `blueprint/components/<slug>.md`, create a machine-readable
`blueprint/contracts/<slug>.json`. Both paths identify the same manifest
component. The contract contains:

```json
{
  "contract_schema_version": 2,
  "slug": "example-worker",
  "kind": "persistent-agent",
  "purpose": "One observable component outcome",
  "trigger": "Starting event or condition",
  "inputs": [{"name": "request", "required": true, "description": "What arrives"}],
  "outputs": [{"name": "result", "description": "What counts as the result"}],
  "state": {"reads": [], "writes": []},
  "authority": {"allowed": [], "forbidden": [], "approval_required": []},
  "runtime_dependencies": ["example-integration"],
  "blocked_behavior": "Stop dependent work and enter setup mode",
  "failures": [{"condition": "Observable failure", "response": "Safe response"}],
  "acceptance": ["Observable check"],
  "kind_contract": {}
}
```

The Markdown specification explains meaning and decision evidence. JSON is the
testable implementation contract. Do not hide several functions in one entry
to reduce the number of files.

`runtime_dependencies` contains only slugs from
`requirements/startup-readiness.json`. When no dependencies are needed, keep an
empty list and still define safe `blocked_behavior` for execution-environment
failure.

<!-- parity:contract.by-kind -->
## Fields by component kind

`deterministic-workflow`:

- `steps`: ordered steps;
- `branch_rules`: deterministic branching rules;
- `stop_conditions`: completion and stopping conditions.

`tool`:

- `operation`: one bounded operation;
- `effect`: `read`, `local-write`, `external-write`, or `financial`;
- `input_schema` and `output_schema`;
- `retry_policy`;
- `result_verification`.

When create, update, pause, and delete have different permissions or risks,
they are separate tools.

`skill`:

- `skill_name`, equal to the component `slug`;
- `use_when` and `do_not_use_when`;
- `method_steps`;
- `output_format`;
- `tool_dependencies` and `skill_dependencies`;
- `reuse_decision`: `reuse`, `configure`, `adapt`, `fork`, or `create-new`;
- `reuse_candidate`: candidate identifier, or `null` for `create-new`.

A skill method can have several steps, but it must lead to one repeatable
outcome. A catalog of future skills is not itself a skill.

`subagent`:

- `delegated_task`, `completion_boundary`, `context_inputs`, `returned_result`,
  and `allowed_tools`.

`persistent-agent`:

- `owned_outcome`;
- `lifecycle` with `start`, `run`, and `stop`;
- `skills`, `tools`, `handoffs`, and `recovery`.

`orchestrator`:

- `coordination_decision`, `participants`, `routing_inputs`, `conflict_policy`,
  and `stop_condition`. At least two participants are required.

`storage`:

- `records`, `source_of_truth`, `retention`, `concurrency`, and `recovery`.

`interface`:

- `users`, `decisions`, `views`, `commands`, and `stale_state_behavior`.

<!-- parity:contract.adapter -->
## Adapter completeness

Every platform adapter contains a mapping table:

`component → file or service → dependencies → activation → authority → test`.

Every manifest component must appear exactly once. An adapter may implement
several components in one process, but their contracts, permissions, and tests
must remain distinct.

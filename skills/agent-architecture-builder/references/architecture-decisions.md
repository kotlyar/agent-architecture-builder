# Architecture decision rules

Apply these rules only after discovery gates `D1–D4` pass. One business area may
contain deterministic processes, tools, and skills while still belonging to one
persistent agent.

## 1. Define functions before roles

Create a card for every function. Each `yes`, `no`, or `unknown` must be backed by
a user requirement, document, system observation, or explicit assumption.

| Field | Required question |
|---|---|
| Function ID | What stable name identifies this unit of work? |
| Outcome | What observable result does it produce? |
| Recipient | Who or what uses the result? |
| Inputs | What information is required? |
| Completion rule | What artifact or change counts as done? |
| Trigger | Who, when, or what event starts the work? |
| Method variability | Is the sequence fixed, or does it require judgment? |
| Persistent state | What must survive between runs? |
| State owner | Who owns the backlog, decision history, and current state? |
| Decision authority | What may this component decide alone? |
| Account | Whose identity and accounts are used? |
| External effects | What can it read, modify, publish, send, or purchase? |
| Lifecycle | How is it started, paused, retried, recovered, and completed? |
| Cadence and deadline | Does it have its own schedule, queue, or service level? |
| Dependencies | Whose input does it need, and who receives its output? |
| Shared resources | Does it share a budget, quota, or people? |
| Failure boundary | Can it be stopped and recovered independently? |

If outcome, persistent state, state owner, or decision authority is unknown, do
not create a new persistent agent or orchestrator. Record the gap and use a simpler
temporary form.

## 2. Classify the execution form

Test options from simplest to most complex. They may be combined: a skill can
call a tool inside a deterministic workflow.

### 2.1 Deterministic process

Use it only when all are true:

- steps and transitions are known before execution;
- the next step is selected by rules over structured data;
- result acceptance is objectively testable;
- a language model does not make an open-ended business decision.

A language-model call inside one step does not turn the whole process into an
agent when branching, retries, and transitions are controlled by the runtime.

### 2.2 Tool

Use a `tool` only when all are true:

- it is one bounded operation on a system or dataset;
- input and output requirements are stable;
- it owns no business goal, backlog, or persistent state;
- the caller decides why and when to invoke it.

Separate read, write, and destructive operations when they require different
credentials, approvals, idempotency, or recovery. Risk requires a safety policy,
but does not turn a tool into an agent.

### 2.3 Skill

Use a `skill` only when all are true:

- it is a repeatable reasoning or artifact-production method;
- trigger, inputs, and completed output are defined;
- the calling workflow or agent retains the goal and final decision;
- it has no own account, independent backlog, or state between calls;
- control returns to the caller after the result.

Different methods, API schemas, platform terminology, or platform rules justify
separate skills. They do not by themselves justify separate persistent agents.

### 2.4 Temporary subagent

Use a `subagent` only when all are true:

- the task has bounded inputs, output, and a completion condition;
- the parent owns the overall goal, external authority, and integration;
- the subagent needs no persistent memory, queue, or enduring identity;
- isolated context, parallel execution, or permission isolation provides a
  concrete benefit for this task.

If the last condition fails, use a skill or deterministic step. If the component
develops its own state and lifecycle, test the persistent-agent criteria.

## 3. When to create a persistent agent

A persistent agent is not a job title. It is a durable owner of an outcome, state, and
execution boundary.

### 3.1 All three persistent-agent conditions are mandatory

- `P1 Outcome ownership`: an enduring responsibility, measurable result, or
  class of decisions exists.
- `P2 State ownership`: it owns a backlog, decision history, working state, or
  memory across independent runs.
- `P3 Independent lifecycle`: it can be started, paused, completed, retried, or
  recovered independently; trigger and terminal states are defined.

### 3.2 At least one isolation condition is mandatory

- `I1 Account`: separate credentials, organization, tenant, or account scope.
- `I2 Authority`: materially different tools, write permissions, approvals, or
  spending limits.
- `I3 Data`: separate privacy, memory, or retention requirements.
- `I4 Operations`: its own cadence, service level, queue, recovery, or failure
  boundary.
- `I5 Context`: a sufficiently independent domain where isolation measurably
  improves quality, cost, or safety.
- `I6 Persistent parallel load`: a durable independent queue, not a one-off
  opportunity to delegate.

Formal rule:

```text
persistent_agent = P1 AND P2 AND P3 AND (I1 OR I2 OR I3 OR I4 OR I5 OR I6)
```

`unknown` counts as `no` for persistent-agent creation. If accounts or data require
isolation but `P1–P3` fail, create a separate service, tool, or execution policy,
not an artificial language-model agent.

The following are insufficient on their own: a job title, platform, API, system
prompt, large instruction set, different model, one-time parallel task, or human
organization chart.

## 4. When an orchestrator is justified

First justify at least two persistent agents. Then require all four conditions:

- `O1 Multiple agents`: at least two persistent agents pass `P1–P3` and isolation.
- `O2 Shared outcome`: the agents contribute to one composite user or business
  outcome.
- `O3 Integration duty`: someone must allocate shared resources, manage
  dependencies, resolve conflicts, or assemble one decision.
- `O4 Semantic coordination`: allocation or conflict resolution requires
  contextual judgment and cannot be reduced to stable structured-data rules.

```text
model_orchestrator = O1 AND O2 AND O3 AND O4
deterministic_router = O1 AND O2 AND O3 AND NOT O4
no_orchestrator = NOT O1 OR NOT O2 OR NOT O3
```

The orchestrator owns only the shared plan, handoffs, resource conflicts, and
integrated decision. Domain backlogs and evidence remain with their agents.

Do not create an orchestrator when the user routes independent agents, they
share no outcome, or integration is a simple fixed sequence.

## 5. Use two passes

Pass A assigns each function one or more execution forms:

`deterministic process | tool | skill | subagent`.

Pass B groups functions that share outcome, state owner, account, and lifecycle.
Test each group against the persistent-agent formula, then test the whole system against
the orchestrator formula.

Do not decide whether a named profession or department is a skill or an agent.
First separate its observable functions, state ownership, decisions, external
effects, and lifecycle.

## 6. Required decision table

| ID | Function or group | P1 | P2 | P3 | I1–I6 | O1–O4 | Decision | Evidence | Rejected | Review trigger |
|---|---|---:|---:|---:|---|---|---|---|---|---|

Allowed values: `yes`, `no`, `unknown`, `not applicable`.

For every skill, subagent, persistent agent, router, and orchestrator, write one testable
sentence: “Selected X because …; rejected Y because …”.

## 7. Split and merge triggers

Promote a skill to a persistent agent only when new evidence makes `P1–P3` and an
isolation condition pass—for example: a separately owned backlog, separate
account or authority, independent schedule or recovery, durable parallel queue,
or measured degradation caused by shared context.

Merge a persistent agent back when it loses its own outcome, state, or lifecycle, or when
coordination cost exceeds the value of isolation.

## 8. Domain-neutral calibration examples

| Function | Decision | Reason |
|---|---|---|
| Read one record from an external system | Tool | One bounded operation with no goal or backlog. |
| Apply a repeatable review method and return a report | Skill | The caller owns the goal and state. |
| Explore several sources once in an isolated context | Subagent | Bounded output; the parent integrates it. |
| Own a durable queue and outcome across independent runs | Persistent agent only if `P1–P3` and isolation pass | The boundary comes from ownership and lifecycle. |
| Send work by a stable `type` field | Deterministic router | The rule is known before execution. |
| Resolve changing priorities between two justified agents | Orchestrator only if `O1–O4` pass | Coordination requires contextual trade-offs. |

These examples test the rules without assigning any profession, industry, or
vendor to a particular architecture.

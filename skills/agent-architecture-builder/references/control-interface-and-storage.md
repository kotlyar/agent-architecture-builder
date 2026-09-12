# Control interface and storage decisions

Decide these after the work, authority, and persistent-state requirements are
known. Interface and database choices are independent: a browser panel may use
files, and a conversation-based system may use PostgreSQL.

## 1. Control interface

Evaluate the actual operators, frequency, visibility needs, approvals, and
operating environment.

### Conversation

<!-- parity:control.interface.conversation -->

Prefer conversation when these conditions hold together:

- one or a few users assign work irregularly;
- natural-language clarification is valuable;
- status can be summarized rather than continuously displayed;
- artifacts can live in project files;
- risky actions can be approved in the same live conversation.

Do not use conversation history as the authoritative business database.

### Command line

<!-- parity:control.interface.command-line -->

Prefer the command line when these conditions hold together:

- the primary operator is technical;
- tasks are scriptable and local;
- reproducibility and logs matter more than visual overview;
- no nontechnical multi-user workflow is required.

### Browser control panel

<!-- parity:control.interface.browser -->

Prefer a web interface when at least one of these is confirmed:

- nontechnical users must operate the system without learning commands;
- multiple users need a shared queue and current state;
- users must compare many tasks, runs, costs, or results at once;
- approvals require structured forms and visible exact parameters;
- a durable audit history, filters, or role-based views are needed;
- the interface is itself part of the required product.

A browser panel is not justified solely by having multiple agents.

Minimum panel views, only when relevant:

1. work queue and status;
2. task details, inputs, evidence, and artifacts;
3. approval request with exact target, account, action, content, and budget;
4. execution and error history;
5. agent health and current responsibility;
6. settings that expose authority limits without revealing secrets.

### API and notifications

<!-- parity:control.interface.api -->
<!-- parity:control.interface.notifications -->

Prefer an API when another system is the main caller. Prefer notifications when
routine work can run elsewhere and the user only needs meaningful changes,
failures, completion, or approval requests.

### Combination

<!-- parity:control.interface.combination -->

Use several interfaces only when each has a distinct job. Example: an API creates
tasks, a browser panel handles approvals, and notifications surface failures.
Name the authoritative source of status so the views cannot silently diverge.

## 2. Storage

First list each durable object: goals, tasks, decisions, evidence, artifacts,
approvals, external-action records, schedules, and agent-owned state. For
each object define owner, readers, writers, retention, sensitivity, and source of
truth.

### Files only

<!-- parity:control.storage.files -->

Prefer Markdown, JSON, or YAML files when these conditions hold together:

- one process usually writes at a time;
- the dataset is small and human review matters;
- version control and portable artifacts are valuable;
- queries are simple;
- transaction guarantees are unnecessary.

Use explicit directories, schemas, stable identifiers, dates, and append-only
history where overwriting would destroy evidence.

### SQLite

<!-- parity:control.storage.sqlite -->

Prefer SQLite when these conditions hold together:

- the system runs on one host;
- structured queries, filters, or an event log are useful;
- write concurrency is limited;
- zero-service deployment matters;
- the database file can be backed up safely.

Do not put secrets into the database merely for convenience. Define migrations,
backup, and recovery before calling it production-ready.

### PostgreSQL

<!-- parity:control.storage.postgresql -->

Prefer PostgreSQL when at least one of these requirements is confirmed:

- multiple processes or users write concurrently;
- transactions and stronger consistency matter;
- the service runs across hosts or containers;
- row-level permissions, robust migrations, or operational monitoring are
  required;
- expected volume or query complexity exceeds a local embedded store.

The operational cost is justified only by confirmed requirements.

### Vector search

<!-- parity:control.storage.vector-search -->

Do not add a vector database by default. Use ordinary files or database fields
when exact identifiers and structured filters solve retrieval. Add embeddings
only after a realistic retrieval test shows a semantic-search need. Record the
embedding model, source chunks, deletion behavior, and reproducibility limits.

### No separate database

<!-- parity:control.storage.no-new-database -->

Choose no new database when authoritative state already exists in external
systems and the agent only needs temporary working data. Store only pointers,
evidence snapshots, and decisions needed for auditability.

## 3. Required properties of persistent state

<!-- parity:control.persistent-state -->

Regardless of storage technology, define:

- owner, readers, and writers for every durable object;
- one authoritative source for each value;
- record schema and version;
- creation, update, deletion, retention, and sensitivity rules;
- stable links between task, run, approval, and external action;
- concurrency, backup, recovery, and access requirements.

A database does not repair ambiguous state ownership. Two components must not
write the same record without an explicit coordination rule.

## 4. Authority and external-action records

<!-- parity:control.external-action-record -->

For each externally mutating operation store:

- request identifier and timestamp;
- initiating user or component;
- exact target and account;
- proposed action and parameters;
- approval identity, scope, and time;
- idempotency key where supported;
- observed result or `result_unknown`;
- verification attempt and recovery decision.

Never retry an action with an unknown result until state has been checked or the
user has explicitly decided how to proceed.

<!-- parity:control.unknown-result -->

## 5. Required decision record

<!-- parity:control.decision-record -->

Document:

| Decision | Choice | Confirmed requirement | Rejected alternative | Cost or risk | Review trigger |
|---|---|---|---|---|---|
| Control interface |  |  |  |  |  |
| System-of-record storage |  |  |  |  |  |
| Artifact storage |  |  |  |  |  |
| Secrets storage |  |  |  |  |  |
| Audit history |  |  |  |  |  |

If the evidence is insufficient, select the simplest reversible option and label
it provisional.

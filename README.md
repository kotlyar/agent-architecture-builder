# Agent Architecture Builder

![A vintage cartoon workshop where an architect organizes processes, tools, skills, helpers, agents, and a coordinator](assets/agent-architecture-builder-hero.png)

[![skills.sh](https://skills.sh/b/kotlyar/agent-architecture-builder/agent-architecture-builder)](https://skills.sh/kotlyar/agent-architecture-builder/agent-architecture-builder)
[![Validate skills](https://github.com/kotlyar/agent-architecture-builder/actions/workflows/validate.yml/badge.svg)](https://github.com/kotlyar/agent-architecture-builder/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Русская версия](README.ru.md)

A universal Agent Skill that interviews a person in plain language and designs
the smallest justified autonomous-agent or multi-agent system.

It determines what belongs in persistent instructions, a deterministic workflow,
a tool, a skill, a temporary subagent, a persistent agent, or an orchestrator.
It also determines whether the system needs durable memory, a database, a
browser control panel, approvals, schedules, and external integrations.

The method is independent of profession, industry, and agent platform. Hermes,
Codex, Claude Code, and other environments are implementation adapters, not
inputs to the architecture decision.

## What the skill does

| Stage | What happens | Result |
|---|---|---|
| Discovery | A plain-language interview covers the outcome, real work, autonomy, and control | Verified requirements and unknowns |
| Decomposition | Work is divided into functions | Input, result, state, authority, and risk for every function |
| Architecture | Each function is tested as a workflow, tool, skill, subagent, or persistent agent | The smallest justified system and an orchestrator decision |
| Reuse | Existing skills are discovered and evaluated | Reuse, configure, adapt, fork, or create-new decision |
| Adaptation | Neutral components are mapped to each selected environment | Exact files, services, activation, authority, and tests |
| Handoff | Separate component contracts and one implementation task are produced | A validated directory and archive for a receiving agent |

The skill can also audit an existing architecture or kit. An audit does not by
itself change the system or run discovered materials.

## Why this exists

Job titles and product names are weak architecture boundaries. One named role
may be one agent with several skills, several independently operated agents, or
no agent at all. This skill first reconstructs real work and then applies
explicit gates.

The decision order is:

```text
deterministic workflow → tool → skill → subagent → persistent agent → orchestrator
```

A persistent agent requires all three ownership conditions and at least one
isolation condition:

```text
persistent_agent = P1 AND P2 AND P3 AND (I1 OR I2 OR I3 OR I4 OR I5 OR I6)
```

- `P1`: durable outcome ownership;
- `P2`: persistent state ownership;
- `P3`: independent lifecycle;
- `I1–I6`: separate account, authority, data, operations, context, or durable
  parallel load.

An orchestrator requires at least two justified persistent agents, a shared
outcome, a real integration duty, and contextual coordination that cannot be
replaced by stable rules.

## Interview

The user does not need to know architecture terminology. The skill asks one
primary question at a time, beginning with the desired change and a concrete
work episode. When a broad question is difficult, it offers optional examples
adapted to the user's own words and domain.

The interview shows visible progress before every primary question:

Creating an agent · stage 2 of 7

```text
[✓ ● ○ ○ ○ ○ ○]
```

```text
✓ Completed: goal and success
● Current: real work
○ Next: work inventory
```

The seven stages are goal and success, real work, work inventory, autonomy and
control, constraints and environment, architecture, and implementation kit.
Progress follows completed meaning-level stages rather than message count. The
skill does not show a misleading percentage or promise an exact number of
questions.

The interview also asks:

- how work starts and what a complete result looks like;
- what must survive between runs and who owns it;
- which actions need human approval;
- how the person wants to supervise the system;
- whether several people share state;
- which implementation environments are required.

## Result

After the readiness gates pass, the skill creates a self-contained directory and
`.zip` archive containing:

- requirements and evidence;
- a platform-neutral architecture;
- a decision ledger with rejected alternatives;
- state, authority, interface, and storage design;
- one adapter for every selected environment;
- a narrative specification and machine-readable contract for every component;
- a discovery record with reusable-skill candidates and reuse decisions;
- a startup-readiness contract covering required integrations, data,
  configuration, minimum permissions, setup ownership, safe secret references,
  and factual checks;
- acceptance criteria and scenarios;
- one `IMPLEMENTATION.md` task for a receiving coding agent;
- deterministic validation and checksums.

This is not the finished domain agent. It is an exact implementation contract
for Codex, Hermes, or another receiving agent, which creates the actual
`SKILL.md` files, tools, profiles, storage, and interfaces and passes acceptance.

The packager accepts custom platforms. Every selected platform must provide a
local adapter; platform names are not hard-coded.

## Included skills

| Path | Language | Skill name |
|---|---|---|
| `skills/agent-architecture-builder/` | English | `agent-architecture-builder` |
| `skills/agent-architecture-builder-ru/` | Russian | `agent-architecture-builder-ru` |

Install only the language edition you need to avoid duplicate capability
descriptions in the agent's initial context.

## Installation

Cross-agent installer:

```bash
npx skills add kotlyar/agent-architecture-builder
```

Codex, user-wide:

```bash
mkdir -p ~/.agents/skills
cp -R skills/agent-architecture-builder ~/.agents/skills/
```

For one Codex project, copy the folder into `.agents/skills/` instead.

Claude Code, user-wide:

```bash
mkdir -p ~/.claude/skills
cp -R skills/agent-architecture-builder ~/.claude/skills/
```

For one Claude Code project, copy the folder into `.claude/skills/` instead.

Claude Code plugin installation from this repository:

```text
/plugin marketplace add kotlyar/agent-architecture-builder
/plugin install agent-architecture-builder@agent-architecture-builder
```

Explicit invocation:

- Codex standalone skill: `$agent-architecture-builder`;
- Claude Code standalone skill: `/agent-architecture-builder`;
- Claude Code plugin skill:
  `/agent-architecture-builder:agent-architecture-builder`.

Both products can also select the skill automatically from its description.

Claude Code uses the `name`, `description`, and `argument-hint` fields in each
`SKILL.md` for its skill listing and command autocomplete. The plugin itself is
shown as **Agent Architecture Builder** from `.claude-plugin/plugin.json`.
Claude Code has no separate documented `default_prompt` field: invoking the
skill loads its instructions and appends any text supplied after the command.

## Supported adapters

The skill currently includes reference adapters for:

- Hermes;
- Codex;
- Claude Code.

A new environment is added as another adapter under `references/platforms/`.
The universal decision rules remain unchanged.

## Validation

```bash
python scripts/validate_repository.py
```

The checks validate both language editions, plugin manifests, platform adapters,
frontmatter, the package schema, separate skill and tool contracts, reuse
decisions, startup dependency matching, safe secret references, secret
rejection, and archive creation.

## Version 2

Version 2 replaces the former `hermes-agent-builder` and
`hermes-agent-builder-en` names. Hermes remains supported as an adapter, while
the core skill and generated package are platform-neutral.

Starting with version 2.2, kit schema 3 makes every component one implementable
unit and requires existing-skill discovery before a create-new decision.

Version 2.3 uses kit schema 4 and component-contract schema 2. A deployed agent
must verify its required integrations, account, scope, and permissions before
domain work. Until then, only setup guidance and safe diagnostics are allowed.
`AGENTS.md`, `SOUL.md`, `CLAUDE.md`, and the kit contain configuration names and
safe secret references, never secret values.

## License and security

MIT. Review generated files and requested permissions before installation. Do
not put credentials, private memory, or production data in a skill or generated
implementation kit. See [SECURITY.md](SECURITY.md).

Release history: [CHANGELOG.md](CHANGELOG.md).

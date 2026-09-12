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
- component specifications;
- acceptance criteria and scenarios;
- one `IMPLEMENTATION.md` task for a receiving coding agent;
- deterministic validation and checksums.

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
frontmatter, the package schema, custom-platform support, secret rejection, and
archive creation.

## Version 2

Version 2 replaces the former `hermes-agent-builder` and
`hermes-agent-builder-en` names. Hermes remains supported as an adapter, while
the core skill and generated package are platform-neutral.

## License and security

MIT. Review generated files and requested permissions before installation. Do
not put credentials, private memory, or production data in a skill or generated
implementation kit. See [SECURITY.md](SECURITY.md).

Release history: [CHANGELOG.md](CHANGELOG.md).

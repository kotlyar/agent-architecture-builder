# Agent Architecture Builder

![A vintage cartoon workshop where an architect organizes processes, tools, skills, helpers, agent profiles, and a coordinator](assets/agent-architecture-builder-hero.png)

[![skills.sh](https://skills.sh/b/kotlyar/agent-architecture-builder/hermes-agent-builder-en)](https://skills.sh/kotlyar/agent-architecture-builder/hermes-agent-builder-en)
[![Validate skills](https://github.com/kotlyar/agent-architecture-builder/actions/workflows/validate.yml/badge.svg)](https://github.com/kotlyar/agent-architecture-builder/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Русская версия](README.ru.md)

Agent Architecture Builder is a guided method for designing agent systems from
real work rather than from job titles or fashionable components.

It interviews the user in plain language, reconstructs concrete work episodes,
and decides—with explicit criteria—what should be a deterministic workflow, a
tool, a reusable skill, a temporary subagent, a persistent agent profile, or an
orchestrator. When the design is complete, it produces a self-contained kit that
another coding agent can implement and verify.

The decision framework is platform-independent. The current delivery templates
and installers target Hermes and Codex; adapters for other agent runtimes can be
added without changing the core classification model.

## Why this exists

Agent systems are often split too early:

- every job title becomes an agent;
- every platform becomes a separate agent;
- an orchestrator is added before there is anything meaningful to coordinate;
- a web interface and database are selected before the operating need is known;
- prompts are mistaken for ownership, state, and lifecycle.

This project starts with the desired business or work outcome and asks what
actually happens in a real episode. Architecture comes later.

```text
desired change
  → real work episodes
  → bounded functions
  → execution form
  → state and authority boundaries
  → profiles
  → orchestration, only if justified
  → implementation-ready kit
```

## Core decisions

The builder uses the simplest sufficient form:

```text
deterministic process → tool → skill → subagent → profile → orchestrator
```

A separate persistent profile requires all three profile conditions and at least
one isolation condition:

```text
profile = P1 AND P2 AND P3 AND (I1 OR I2 OR I3 OR I4 OR I5 OR I6)
```

- `P1`: owns an enduring outcome or class of decisions;
- `P2`: owns persistent state, such as a backlog or decision history;
- `P3`: has an independent start, pause, retry, recovery, and completion cycle;
- `I1–I6`: account, authority, data, operations, context, or durable workload
  requires isolation.

A language-model orchestrator requires:

```text
model_orchestrator = O1 AND O2 AND O3 AND O4
```

- `O1`: at least two independently justified profiles;
- `O2`: one shared composite outcome;
- `O3`: a real duty to allocate resources, manage dependencies, resolve
  conflicts, or integrate decisions;
- `O4`: coordination requires contextual judgment and cannot be reduced to fixed
  rules.

If `O4` does not pass, use a deterministic router. Unknown conditions do not
pass.

## Interview experience

The user does not need to know agent-system terminology. The skill asks one
primary question per turn, using ordinary language:

- What should become different?
- Why is this important now?
- What happened the last time this work was done?
- What information was used, and what result was handed over?
- What must be remembered next week?
- Which exact actions require approval?
- Where would it be easiest to supervise the work?

When a broad question is difficult, the skill offers optional answer hints. For
example, it can show concrete SEO tasks such as page audits, improvement briefs,
search-demand research, content preparation, backlog ownership, and measurement.
Selections are clues, not architectural decisions; they are verified against a
real work episode.

## Control interface and storage

The builder explicitly asks how the system should be supervised: conversation,
command line, browser panel, API, notifications, or a justified combination.

A browser panel is recommended only when confirmed work requires a shared queue,
structured approvals, dense status views, audit history, or access for
nontechnical users. When needed, the default implementation stack uses free and
open-source components: React, TypeScript, Vite, Tailwind CSS, and shadcn/ui.

Storage is selected independently. The method chooses between files, SQLite,
PostgreSQL, semantic retrieval, or no new database based on concurrency,
transactions, retention, privacy, query needs, and operational cost.

## Output

After discovery and readiness gates pass, the skill creates both a directory and
a `.zip` archive containing:

- project-level `AGENTS.md`;
- one `IMPLEMENTATION.md` instruction for Codex or Hermes;
- requirements and evidence;
- architecture and authority decisions;
- acceptance criteria and end-to-end scenarios;
- blueprints for profiles, skills, tools, workflows, storage, and interface;
- a complete Hermes distribution scaffold for every selected profile;
- a manifest and SHA-256 checksums.

The packager rejects drafts, critical unknowns, incomplete profile distributions,
and files that look like credentials or private state.

## Included skills

| Directory | Language | Skill name |
|---|---|---|
| `skills/hermes-agent-builder-en/` | English | `hermes-agent-builder-en` |
| `skills/hermes-agent-builder/` | Russian | `hermes-agent-builder` |

The two versions are self-contained. They use the same decision gates, but each
has its own templates, messages, and package-status vocabulary.

## Installation

Install interactively with the cross-agent `skills` command:

```bash
npx skills add kotlyar/agent-architecture-builder
```

GitHub CLI 2.90.0 or newer can discover and install either edition:

```bash
gh skill install kotlyar/agent-architecture-builder
```

Manual project-local Hermes installation:

```bash
mkdir -p .hermes/skills
cp -R skills/hermes-agent-builder-en .hermes/skills/
```

For the Russian version, copy `skills/hermes-agent-builder` instead.

Codex installation:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/hermes-agent-builder-en "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Restart or begin a new agent session after installation so the skill can be
discovered.

## Example request

```text
Use $hermes-agent-builder-en to help me design an agent system for marketing.
Start by interviewing me in plain language. Do not decide the number of agents
until you understand the desired outcome and at least one real work episode.
```

The likely first architecture for an early marketing operation is one marketer
profile with SEO and paid-acquisition skills. Separate SEO and paid-acquisition
profiles become justified only when each owns its own outcome, persistent state,
and lifecycle. Yandex Direct and Google Ads normally begin as platform skills and
tools, not as agents.

## Validation

The repository uses only the Python standard library for its checks:

```bash
python scripts/validate_repository.py
```

The validation checks both language editions and runs the package-delivery tests.

## Current scope

The classification framework can be used for any agent system. The generated
profile-distribution files and direct installation instructions currently target
Hermes, while the project-level implementation handoff supports both Hermes and
Codex. Supporting another runtime requires a delivery adapter, not a new decision
framework.

## License

[MIT](LICENSE)

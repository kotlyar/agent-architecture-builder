# Codex implementation adapter

Read this file only when Codex is a selected target environment. Apply it after
the platform-neutral architecture is settled.

## Mapping

- Persistent project guidance: `AGENTS.md`, scoped by directory when needed.
- Reusable skills: `.agents/skills/<skill-name>/SKILL.md` for a project or
  `~/.agents/skills/<skill-name>/SKILL.md` for a user.
- Custom subagents: `.codex/agents/<agent-name>.toml` for a project or
  `~/.codex/agents/<agent-name>.toml` for a user. Each file requires `name`,
  `description`, and `developer_instructions`.
- Agent and execution settings: `.codex/config.toml` or user configuration.
- External systems: MCP configuration and tools, with read/write permissions
  separated when their risks differ.

The package must map every neutral component to an exact Codex file or service,
dependencies, activation method, authority boundary, and test. Every manifest
skill gets its own `SKILL.md` directory, and every tool operation retains a
separate testable contract even when one MCP server implements several of them.

The generated `AGENTS.md` must include a "Work readiness" section. It lists the
dependencies from `requirements/startup-readiness.json`, configuration names and
safe secret references, the check command, and the rule that domain work is
forbidden until checks pass; only setup guidance and safe diagnostics are
allowed. Never put password or token values in `AGENTS.md`. The check must verify
the intended account, scope, and minimum permissions rather than only the
presence of an environment variable.

A Codex custom-agent file defines a specialized spawned session; it does not by
itself create a durable queue, schedule, or state owner. When the neutral design
requires a persistent agent, also implement its trigger, state store, lifecycle,
recovery, and operating boundary. Do not mistake a TOML file for the full agent.

Use Codex subagents for bounded delegated work. Use a normal program or workflow
for deterministic routing. Ask the main Codex agent to coordinate only when the
neutral orchestrator gates passed.

Before implementation, verify current Codex paths and supported fields in the
official documentation because the custom-agent format can evolve.

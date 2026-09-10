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

A Codex custom-agent file defines a specialized spawned session; it does not by
itself create a durable queue, schedule, or state owner. When the neutral design
requires a persistent agent, also implement its trigger, state store, lifecycle,
recovery, and operating boundary. Do not mistake a TOML file for the full agent.

Use Codex subagents for bounded delegated work. Use a normal program or workflow
for deterministic routing. Ask the main Codex agent to coordinate only when the
neutral orchestrator gates passed.

Before implementation, verify current Codex paths and supported fields in the
official documentation because the custom-agent format can evolve.

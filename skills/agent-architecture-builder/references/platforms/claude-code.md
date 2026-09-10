# Claude Code implementation adapter

Read this file only when Claude Code is a selected target environment. Apply it
after the platform-neutral architecture is settled.

## Mapping

- Persistent project guidance: `CLAUDE.md` and path-scoped project rules.
- Reusable skills: `.claude/skills/<skill-name>/SKILL.md` for a project or
  `~/.claude/skills/<skill-name>/SKILL.md` for a user.
- Custom subagents: `.claude/agents/<agent-name>.md` for a project or
  `~/.claude/agents/<agent-name>.md` for a user. Define at least `name` and
  `description`; add tools, skills, memory, isolation, and model only when the
  neutral design requires them.
- Distributable bundles: `.claude-plugin/plugin.json` with `skills/`, `agents/`,
  hooks, or MCP configuration at the plugin root.
- External systems: MCP servers and tools, with explicit permission boundaries.

A Claude Code subagent definition provides a specialized isolated context. It
does not automatically provide a business-owned queue, trigger, durable state,
or recovery process. If the neutral design requires a persistent agent,
implement those lifecycle parts separately and use Claude Code as one execution
surface.

Use a skill for reusable knowledge or procedure in the current context. Use a
subagent for bounded isolated work. Use a deterministic workflow when routing is
fully rule-based. Create semantic coordination only when the orchestrator gates
passed.

Before implementation, verify current Claude Code fields and plugin behavior in
the official documentation.

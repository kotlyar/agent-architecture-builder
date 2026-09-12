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

The package must map every neutral component to an exact Claude Code file or
service, dependencies, activation method, authority boundary, and test. Every
manifest skill gets its own `SKILL.md` directory, and every tool operation keeps
a separate contract even when one MCP server implements several operations.

The generated `CLAUDE.md` must include a "Work readiness" section. It lists the
dependencies from `requirements/startup-readiness.json`, configuration names and
safe secret references, the check command, and the rule that domain work is
forbidden until checks pass; only setup guidance and safe diagnostics are
allowed. Never put password or token values in `CLAUDE.md`. The check must verify
the intended account, scope, and minimum permissions rather than only the
presence of an environment variable.

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

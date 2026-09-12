# Hermes implementation adapter

Read this file only when Hermes is a selected target environment. Apply it after
the platform-neutral architecture is settled.

## Mapping

- Persistent agent: a Hermes profile only when the neutral persistent-agent
  gates passed.
- Reusable procedure or domain method: a Hermes skill.
- Bounded system operation: a Hermes tool.
- Profile guidance and behavior: `SOUL.md` and configuration files required by
  the installed Hermes version.
- Profile distribution: `distribution.yaml`, `SOUL.md`, `config.yaml`,
  `mcp.json`, `.env.EXAMPLE`, and `.gitignore` when those files are required by
  the selected Hermes release.
- Project-local skills: `.hermes/skills/` when supported by the installation.

The package must map every neutral component to an exact Hermes file or service,
activation method, authority boundary, and test. For every profile, show:

`profile → skills → toolset → individual operations → normal or operator mode`.

A `toolset` is a profile access group, not a replacement for tool contracts.
Every `tool` operation remains separate even when one toolset grants several of
them. The receiving agent creates the actual skill directories, profiles, tools,
and configuration from package contracts; it must not invent future skills from
one generic collection file.

The generated `SOUL.md` or other always-loaded profile file must include a
"Work readiness" section. It lists dependencies from
`requirements/startup-readiness.json`, configuration names and safe secret
references, the check command, and the rule that domain work is forbidden until
checks pass; only setup guidance and safe diagnostics are allowed. Never put
password or token values in profile instructions. The check verifies the
intended account, scope, and minimum permissions rather than only the presence
of an environment variable.

Do not create one profile per profession, vendor, or method. A Hermes profile is
only an implementation of a persistent-agent boundary already justified by
outcome ownership, state ownership, lifecycle, and isolation.

Keep account identifiers, credentials, operational state, and results outside
the distribution. Use example environment files only. Separate normal and
operator modes when browser access or external mutations require a person at the
dialog. Validate commands and distribution fields against the installed Hermes
version before implementation.

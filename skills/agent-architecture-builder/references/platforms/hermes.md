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

Do not create one profile per profession, vendor, or method. A Hermes profile is
only an implementation of a persistent-agent boundary already justified by
outcome ownership, state ownership, lifecycle, and isolation.

Keep account identifiers, credentials, operational state, and results outside
the distribution. Use example environment files only. Separate normal and
operator modes when browser access or external mutations require a person at the
dialog. Validate commands and distribution fields against the installed Hermes
version before implementation.

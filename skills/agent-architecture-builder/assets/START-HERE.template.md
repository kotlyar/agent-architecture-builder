# Start here

This kit contains the complete implementation specification for `{system_name}`.
The task is in `IMPLEMENTATION.md`; platform mappings are under `platforms/`.

Open `manifest.json`. Hand the kit to an implementation agent only when status is
`ready_for_implementation`, `schema_version` is `4`, and `critical_unknowns` is
empty.

Send this instruction in Codex, Claude Code, Hermes, or another selected
environment:

> Read `IMPLEMENTATION.md` and implement the complete kit through all acceptance
> criteria. Preserve the platform-neutral architecture and apply only the
> selected platform adapters. Implement the mandatory readiness check and block
> domain work until dependencies are configured.

Implementation does not authorize spending, publication, messages, live-account
changes, deletion, or scheduled external actions without separate exact approval.

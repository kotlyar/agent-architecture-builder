# Agent system implementation

Implement the platform-neutral system and every selected platform adapter
through all acceptance criteria.

1. Read `manifest.json`, `IMPLEMENTER-RULES.md`, `requirements/`,
   `architecture/`, `platforms/`, `blueprint/`, `acceptance/`, `evidence/`, and
   `unresolved.md`.
2. Require `schema_version: 2`, status `ready_for_implementation`, and no
   critical unknowns. Otherwise return a useful partial analysis and the one
   decision needed next.
3. Build under `implementation/`. Do not alter requirements to hide a mismatch.
4. Implement only manifest components and selected platform adapters. Preserve
   neutral ownership, state, lifecycle, and authority boundaries.
5. Verify current platform versions and fields before generating configuration.
6. Use example environment files; never include real secrets or production data.
7. Do not publish, spend, message people, or enable scheduled external actions
   without separate exact approval.
8. Run automated and end-to-end checks. Correct failures or document a proven
   blocker.
9. Write `implementation/IMPLEMENTATION-RESULT.md` with components, commands,
   checks, limitations, credentials still required, adapter deviations, and
   exact next human actions.

A complete result is working code or configuration for every selected platform,
passed checks, and reproducible run instructions.

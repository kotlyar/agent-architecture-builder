# Implementation kit rules

Implement the system in this kit; do not merely restate its architecture.

1. Read `manifest.json` and `IMPLEMENTATION.md` first.
2. Treat `requirements/`, `architecture/`, `platforms/`, `acceptance/`, and
   `blueprint/` as sources of truth.
3. Preserve the platform-neutral component boundaries. Record any necessary
   adapter deviation instead of hiding it.
4. Do not create credentials or make external changes without exact approval.
5. Continue until acceptance criteria pass or a demonstrated external blocker
   prevents progress.
6. Store results in `implementation/` and the final report in
   `implementation/IMPLEMENTATION-RESULT.md`.

An explicit user instruction takes precedence. Record the change and its
consequences in the final report.

# Changelog

## 2.1.1 — 2026-09-12

- Added one transition map for all seven interview stages, including completion
  conditions, produced records, and the next reference to load.
- Aligned critical control, storage, external-action, and browser-interface
  guarantees across the English and Russian editions.
- Added structural parity markers and critical-contract checks that reject
  missing sections or absent safety and decision guarantees in either language
  edition.

## 2.1.0 — 2026-09-12

- Added a visible seven-stage progress indicator before every primary interview
  question in both the English and Russian editions.
- Added completed, current, and next stage labels so the user can understand
  where the interview is and what comes after it.
- Defined semantic progress rules: stages advance when a discovery outcome is
  complete, not after every message, and the skill does not claim a percentage
  or an exact number of remaining questions.
- Documented the progress format and all seven stages in both README editions.

## 2.0.0 — 2026-09-10

- Renamed the English and Russian skills to `agent-architecture-builder` and
  `agent-architecture-builder-ru`.
- Made the interview, decision gates, examples, and delivery package independent
  of profession, industry, vendor, and agent environment.
- Added explicit classification for deterministic workflows, tools, skills,
  subagents, persistent agents, and orchestrators.
- Added platform adapters for Codex, Claude Code, and Hermes without coupling the
  core architecture to any of them.
- Added Codex and Claude Code plugin manifests, Claude marketplace metadata, and
  discovery prompts.
- Reworked the implementation kit to accept arbitrary target platforms and added
  deterministic packaging tests.

## 1.0.0 — 2026-09-09

- Initial bilingual release focused on Hermes agent profiles.

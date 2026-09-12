# Changelog

## 2.3.0 — 2026-09-12

- Added an explicit startup-readiness contract for required integrations, data,
  configuration, permissions, setup ownership, and safe secret references.
- Upgraded implementation kits to schema 4 and component contracts to schema 2;
  the packager now rejects missing, unsafe, or mismatched runtime dependencies.
- Required generated `AGENTS.md`, `CLAUDE.md`, or Hermes profile instructions to
  block domain work until deterministic readiness checks pass. While blocked,
  an agent may only guide setup and run safe diagnostics.
- Added acceptance scenarios for missing configuration, invalid credentials,
  wrong account scope, insufficient permissions, successful readiness, lost
  connectivity, and secret leakage.

## 2.2.0 — 2026-09-12

- Added existing-skill discovery across installed inventories, platform sources,
  public catalogs, and repositories before a create-new decision.
- Added a structured reuse record with source, pinned revision, license,
  coverage, gaps, dependencies, risks, and one decision per skill component.
- Added machine-readable contracts for every component and kind-specific fields
  for workflows, tools, skills, subagents, persistent agents, orchestrators,
  storage, and interfaces.
- Upgraded implementation kits to schema 3 and made the packager reject missing
  contracts, tool operations represented as collections, incomplete skill
  definitions, and absent reuse decisions.
- Reorganized both skill entrypoints and README editions around routes, the work
  map, decision flow, and concrete handoff results.
- Updated Codex interface metadata and default prompts in both language editions
  to cover design, audit, reusable-skill discovery, and implementation handoff.
- Added the Claude Code plugin display name and bilingual command argument hints;
  documented how Claude maps plugin and skill metadata without inventing an
  unsupported `default_prompt` field.
- Added a progressively disclosed agent-building source map to both editions.
  It covers Anthropic's architecture, skill, context, tool, continuity, eval,
  and multi-agent materials plus Karpathy's `autoresearch` as a bounded applied
  example and the Ouroboros technical report as a reviewed self-evolution case,
  without treating external material as user instructions.

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

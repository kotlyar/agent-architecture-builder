# Universal implementation package

Create a package only after discovery and architecture decisions are complete.
The package must separate the platform-neutral design from implementation
adapters. A receiving agent should be able to implement it without relying on
the conversation that produced it.

## Required structure

```text
<system>-implementation-kit/
├── START-HERE.md
├── IMPLEMENTATION.md
├── IMPLEMENTER-RULES.md
├── manifest.json
├── requirements/
│   ├── goal.md
│   ├── work-map.md
│   └── constraints.md
├── architecture/
│   ├── platform-neutral.md
│   ├── system.md
│   ├── decisions.md
│   ├── authority.md
│   └── interface-and-storage.md
├── platforms/
│   └── <platform>/README.md
├── blueprint/
│   ├── project-tree.md
│   └── components/<component>.md
├── acceptance/
│   ├── criteria.md
│   └── scenarios.md
├── evidence/sources.md
└── unresolved.md
```

The neutral architecture is authoritative for component boundaries. A platform
adapter explains how to express those decisions in one environment; it must not
silently add, remove, merge, or split components.

## Manifest version 2

```json
{
  "schema_version": 2,
  "system_slug": "example-agent-system",
  "status": "ready_for_implementation",
  "target_platforms": [
    {
      "slug": "codex",
      "adapter": "platforms/codex/README.md"
    }
  ],
  "entrypoint": "START-HERE.md",
  "implementation_instruction": "IMPLEMENTATION.md",
  "critical_unknowns": [],
  "components": [
    {
      "slug": "example-worker",
      "kind": "persistent-agent",
      "specification": "blueprint/components/example-worker.md"
    }
  ],
  "expected_results": [
    "implementation/",
    "implementation/IMPLEMENTATION-RESULT.md"
  ]
}
```

Platform slugs are not restricted to a built-in list. Every selected platform
must have a local adapter file. Component kinds are:

`deterministic-workflow | tool | skill | subagent | persistent-agent | orchestrator | storage | interface`

## Content requirements

- `START-HERE.md`: status, how to hand the kit to any implementation agent, and
  selected platforms.
- `IMPLEMENTATION.md`: the complete task, required reading order, output folder,
  checks, and stopping conditions.
- `IMPLEMENTER-RULES.md`: short platform-independent rules for the receiving
  agent. Platform-specific persistent instructions belong in adapters.
- `requirements/`: desired outcome, success evidence, work episodes, inputs,
  constraints, and critical unknowns.
- `architecture/platform-neutral.md`: components and connections without
  platform filenames or product-specific vocabulary.
- `architecture/decisions.md`: decision table, evidence, rejected alternatives,
  and review triggers.
- `architecture/authority.md`: tools, accounts, read/write permissions, approval
  gates, retry rules, and audit trail.
- `architecture/interface-and-storage.md`: control method, state owners, storage
  choice, retention, concurrency, and recovery.
- `platforms/<platform>/README.md`: exact file mapping, configuration, install,
  run, and validation instructions for that environment.
- `blueprint/components/`: one specification for every manifest component.
- `acceptance/`: observable criteria and end-to-end scenarios.
- `unresolved.md`: noncritical unknowns, owner, deadline, fallback, and review
  event. Critical unknowns must also appear in the manifest and block packaging.

## Readiness gates

- `R1 Goal`: desired change, beneficiary, success evidence, and non-goals are
  explicit.
- `R2 Work`: at least one real or concrete expected episode supports every
  important function.
- `R3 Architecture`: every function has an execution form and owner; agent and
  orchestrator gates are recorded.
- `R4 State and authority`: state owners, permissions, approvals, retries, and
  failure boundaries are explicit.
- `R5 Interface and storage`: each is justified by observed needs.
- `R6 Platform`: at least one implementation environment is selected and has a
  complete adapter.
- `R7 Acceptance`: behavior, failure, recovery, and authorization scenarios are
  testable.
- `R8 Handoff`: the receiving agent can implement from the kit alone.

Unknown means a gate has not passed. Do not package a draft to create an
appearance of readiness.

## Packaging

Copy the templates from `assets/`, replace every example value, set
`schema_version` to `2`, and leave `critical_unknowns` empty only when justified.
Run:

```bash
python scripts/package_delivery.py <implementation-kit-directory>
```

The packager validates required files, component specifications, platform
adapters, secrets, symlinks, and readiness before producing a checksum-protected
archive outside the source directory.

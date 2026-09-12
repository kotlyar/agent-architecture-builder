# Startup readiness

Read this file before creating component contracts and the implementation kit.
The architecture is incomplete until every work function states what must be
configured before it can run and how that condition is verified without guesses.

<!-- parity:startup.two-states -->
## Two distinct states

- `ready_for_implementation` means the kit is precise enough to implement.
- Runtime readiness means the deployed system has actually verified its
  integrations, data, permissions, and execution environment.

Missing passwords and tokens are not architecture unknowns when their purpose,
safe storage location, setup owner, minimum permissions, and verification method
are known. The deployed agent nevertheless remains `blocked` until its runtime
dependencies pass their checks.

<!-- parity:startup.contract -->
## Readiness contract

Create `requirements/startup-readiness.json` from the asset template. For every
dependency specify:

- a stable slug and kind: `integration`, `credential`, `data-source`, `runtime`,
  or `human-decision`;
- which components cannot run without it;
- its purpose and minimum permissions;
- configuration and secret reference names, never their values;
- the setup owner and exact setup action;
- a safe check of account, scope, permissions, and availability;
- `block-dependent-work` as the failure behavior.

Set `check_command` to one reproducible command that returns machine-readable
`ready` or `blocked` state plus the result of every check.

Represent value locations as `env:VARIABLE`, `config:path.key`, or
`secret-manager:path#key`. Never ask a person to paste a secret value into chat
or store it in the kit, logs, or profile instructions.

Every component contract lists its `runtime_dependencies` from this file and a
`blocked_behavior`. The two inventories must match; a dependency cannot exist
only in prose or only in a component contract.

<!-- parity:startup.gate -->
## Mandatory startup gate

Before its first domain task and after losing a connection, the deployed system:

1. runs a deterministic check for every dependency required by the requested
   operating mode;
2. verifies the intended account, scope, and minimum permissions through safe
   reads or configuration checks rather than checking only that a variable exists;
3. enters `ready` only when every required check passes;
4. otherwise remains `blocked` and shows what is missing, where to configure it,
   and how to repeat the check;
5. while `blocked`, permits only setup guidance and safe diagnostics.

While `blocked`, domain conclusions, drafts, hypotheses, and external actions
that depend on missing setup are forbidden. Generic advice must not conceal a
failed integration.

<!-- parity:startup.persistent -->
## Persistent platform instructions

The implementing agent must place the following in the selected environment's
always-loaded instructions:

- a table of required dependencies and safe references;
- the readiness-check command or operation;
- the rule `blocked → setup and diagnostics only`;
- a ban on requesting or printing secret values;
- the condition for entering work mode and behavior after dependency loss.

For Codex this is a section in `AGENTS.md`, for Claude Code in `CLAUDE.md`, and
for Hermes in `SOUL.md` or the always-loaded profile file required by the
installed release.

Minimum section structure:

```markdown
## Work readiness
- Requirements source: `requirements/startup-readiness.json`
- Check: `<check_command>`
- Required dependencies: `<slug → configuration or safe reference → permission>`
- If the result is `blocked`: do not perform domain work; show the reasons and
  one next setup action.
- Never request or print secret values.
```

<!-- parity:startup.acceptance -->
## Acceptance scenarios

Test separately:

1. a required configuration value is absent;
2. a secret is present but invalid;
3. the wrong account or scope is connected;
4. permissions are insufficient;
5. all checks pass;
6. a working dependency is lost between runs;
7. no secret value appears in responses, logs, or result files.

A scenario passes through observable system state, not because the agent claims
it is ready.

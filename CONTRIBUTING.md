# Contributing

Contributions are welcome when they improve the decision framework, interview
experience, validation, or support for another agent runtime.

Before opening a pull request:

1. Keep the English and Russian editions behaviorally aligned.
2. Preserve the default preference for the simplest sufficient architecture.
3. Do not turn a platform, job title, persona, or large prompt into an agent
   boundary without outcome, state, lifecycle, and isolation evidence.
4. Put platform-specific installation details in delivery guidance rather than
   changing the core classification rules.
5. Do not commit credentials, private state, logs, or real customer data.
6. Run `python scripts/validate_repository.py`.

For a new runtime adapter, document its persistent-agent format, skill format,
tool contract, state model, authority model, installation procedure, and a
minimal validation scenario.

# Plain-language discovery interview

Use this interview to discover the desired change and the real work before
choosing an architecture. Do not turn it into a terminology exam or ask the
user to design the system for you.

## Conversation rules

- Ask one primary question per turn.
- Use short sentences and the user's own words.
- Reuse information already provided; do not make the user repeat it.
- Keep `fact`, `inference`, `hypothesis`, and `unknown` separate in your notes.
- Ask about a recent real case before asking for ideal future behavior.
- Summarize after each meaningful block and let the user correct it.
- When a broad question is hard, offer optional examples from
  `question-hints.md`. The user may choose several or add their own.
- Do not discuss the number of agents until gates `D1–D4` pass.

Before sending a question, check that a person unfamiliar with agent terminology
can answer it with an example from their work. If not, rewrite it.

## Visible interview progress

Before every primary question, show the current stage in the same format. Keep
the title as ordinary text, then place the indicator and three status lines in
separate blocks:

Creating an agent · stage 2 of 7

```text
[✓ ● ○ ○ ○ ○ ○]
```

```text
✓ Completed: goal and success
● Current: real work
○ Next: work inventory
```

Use this single transition map for the seven user-facing stages:

<!-- parity:progress.stage-map -->
| Stage | Work covered | Complete when | Record produced | Load next |
|---|---|---|---|---|
| 1. Goal and success | Internal stages 0–2 | Gate `D1` passes | Desired change and success evidence | Continue here with stage 3 |
| 2. Real work | Internal stage 3 | Gate `D2` passes for at least one episode | Work episode | Continue here with stage 4 |
| 3. Work inventory | Internal stage 4 | Included functions have triggers, inputs, outputs, state, authority, and dependencies | Work map | Continue here with stages 5–7 |
| 4. Autonomy and control | Internal stages 5–7 | Authority, persistent state, failure handling, and control needs are known; gate `D3` passes | Authority, state, and control requirements | Apply `control-interface-and-storage.md`, then continue here with stage 8 |
| 5. Constraints and environment | Internal stage 8 | Gates `D1–D4` all pass; required startup dependencies and their setup owners are known | Readiness summary and first useful scope | Load `architecture-decisions.md` |
| 6. Architecture | Function classification, agent boundaries, orchestration, interface, and storage decisions | Gates `R3–R5` in `delivery-package.md` pass | Platform-neutral architecture and decision record | Load only selected platform adapters, then `delivery-package.md` |
| 7. Implementation kit | Adapters, acceptance, implementation instructions, and packaging | Gates `R6–R10` pass and the packager validates the kit | Implementation-kit directory and archive | Present the finished result |

Count completed meaning-level stages, not messages or questions. Do not show a
completion percentage or promise an exact number of remaining questions. If one
answer resolves several stages, advance accordingly. When returning to an older
gap, retain the current stage number and name the clarification in `Current`. In
the final stage, make `Next` name the finished deliverable rather than an eighth
stage.

## Stage 0. Opening

Explain the process briefly:

> First I will understand what you want to change and how the work happens now.
> Then I will separate the work into parts and decide which parts need a rule, a
> tool, a reusable method, or a separate agent. I will ask one question at a time.

Recommended first question:

> What do you want to become different after this system starts working?

If the user answers with a proposed solution or role, ask:

> What useful result should improve because of it?

## Stage 1. Current situation

Discover why the user seeks a change:

- What happens today that you want to stop, reduce, or improve?
- Why has this become important now?
- What event usually starts this work?
- Who handles it now, and what do they actually do?
- What is slow, expensive, inconsistent, or risky?
- What happens if nothing changes for three months?

Ask these one at a time and only when the answer is not already known.

Capture the current process, existing alternatives, urgency, people, systems,
constraints, and known evidence.

## Stage 2. Desired situation and larger goal

Discover visible progress and why it matters:

- What should the system produce or change?
- Who uses that result next?
- How will you know the result was useful?
- Which number, event, or observable outcome would show success?
- What larger goal does that success support?
- What would count as failure even if many artifacts were produced?

Keep output and outcome separate. A completed artifact may be required without
being the ultimate reason for the work.

## Stage 3. Reconstruct one work episode

Ask:

> Please walk me through the last time this work happened, from the moment it
> started until someone considered it finished.

Follow the episode in order:

1. What triggered it?
2. What information was available at the start?
3. What did the person inspect or compare?
4. Which decisions required judgment?
5. Which actions followed fixed rules?
6. Which systems, accounts, or files were used?
7. Was anything sent, published, purchased, deleted, or changed externally?
8. Who approved those actions?
9. What was handed to another person or system?
10. What needed to be remembered for next time?
11. What proved that the work was complete?
12. What went wrong or required rework?

Do not ask all twelve questions at once. Choose the next question from the
largest gap in the episode. If the work has never happened, construct one
plausible first episode and label every unverified detail as a hypothesis.

## Stage 4. Work inventory

After one episode is clear, ask about adjacent recurring work. For each item,
capture:

- trigger;
- input;
- observable output and recipient;
- fixed rules versus contextual judgment;
- cadence and deadline;
- state that must persist and its owner;
- systems, accounts, and permissions;
- external effects and approvals;
- dependencies, failure, and recovery.

Do not group work by job title. Group it only after these properties are known.

## Stage 5. Autonomy and authority

Use simple questions:

- Which steps may happen without asking you?
- Which steps should only prepare a draft?
- Before which exact action must the system stop and show you the details?
- May it spend money? If yes, what limit and whose account?
- May it publish, send messages, change external records, or delete information?
- If it cannot tell whether an action succeeded, should it check status, ask
  you, or retry?
- Who has the final say when recommendations conflict?

Write permissions by operation, not by broad role. Reading a record, editing a
draft, and publishing a change are three different permissions.

## Stage 6. Persistent state and storage

Do not ask whether the user needs a database. Ask about the information:

> What should the system still remember next week or next month, even after it
> has restarted?

Then clarify:

- Is there a work queue, decision history, version history, or changing status?
- Which information is an approved fact rather than a temporary note?
- Who may read, change, or delete it?
- How long must it be kept?
- Must data be isolated by client, account, project, or team?
- Can several people or processes change it at the same time?
- Must the system prevent the same external action from happening twice?
- What should remain easy for a person to read and edit as a normal file?

Infer whether files, SQLite, PostgreSQL, or another store is justified only after
these answers. Do not propose semantic retrieval infrastructure without a real
semantic-search need.

## Stage 7. Control interface

Always ask:

> Where would it be easiest for you to give work, see progress, approve risky
> actions, and review results?

If useful, offer conversation, command line, browser panel, API, notifications,
or a combination as optional examples. Then clarify:

- what must be visible at the same time;
- where exact changes should be approved;
- whether the user must stop, retry, or reprioritize active work;
- whether a history of decisions and failures is needed;
- where notifications should go;
- whether one person or several people with different rights will use it;
- whether mobile access matters;
- which actions are easier in conversation and which need buttons or forms.

Do not infer that a browser interface is required because several agents exist.
Apply `control-interface-and-storage.md` after collecting the answers.

## Stage 8. Quality, limits, and implementation context

- What source wins when information conflicts?
- What must never be invented?
- What quality check is required before accepting a result?
- What are the time, cost, legal, privacy, and security limits?
- What must exist before the system can produce its first useful result at all?
- Which services and accounts already exist?
- Which connections, source data, configuration values, and permissions must be
  set before work begins?
- Who sets them up, and where will passwords and tokens be stored safely?
- How can the system verify the intended account, scope, and minimum permissions
  without making an external change?
- Which agent environments should run the result?
- Who will install and maintain it?
- What should the first useful version accomplish from start to finish?

## Discovery readiness gates

Architecture may be finalized only when all four gates pass.

### `D1 Outcome clarity`

Pass when the desired change, recipient, success evidence, and larger purpose are
known. A list of features does not pass this gate.

### `D2 Episode evidence`

Pass when at least one real or explicitly hypothetical work episode has a
trigger, inputs, decisions, actions, handoffs, persistent state, and a completion
condition.

### `D3 Boundary clarity`

Pass when critical authority, accounts, external effects, approvals, privacy,
storage, control interface, required startup dependencies, safe configuration
locations, and failure handling are known. An explicit `none` is valid; an
unexamined unknown is not.

### `D4 First useful scope`

Pass when the first end-to-end result, included work, deferred work, target agent
environments, and architecture owner are known.

Use `yes`, `no`, or `unknown` for each gate. `Unknown` does not pass.

## Readiness summary

Before classifying components, show a concise summary:

| Area | Confirmed | Unknown | Evidence or source |
|---|---|---|---|
| Current situation |  |  |  |
| Desired situation |  |  |  |
| Success |  |  |  |
| Work episode |  |  |  |
| Authority |  |  |  |
| Persistent state |  |  |  |
| Control interface |  |  |  |
| Constraints |  |  |  |
| Startup readiness |  |  |  |
| Target environments |  |  |  |

If a gate fails, ask the single question with the greatest architectural impact.
If the user declines to answer, continue only with a clearly labeled provisional
design and do not package it as implementation-ready.

## Interview record

Save the result using this structure:

```markdown
# Agent-system discovery

## Desired change
- Current situation:
- Reason to act now:
- Desired situation:
- Larger goal:
- Success evidence:

## Current work
- People and systems:
- What works:
- What gets in the way:

## Work episodes
### Episode 1
- Trigger:
- Inputs and evidence:
- Judgment calls:
- Fixed actions:
- External effects:
- Handoffs:
- Result and verification:
- Persistent state:
- Failure recovery:

## Authority
- May run autonomously:
- Draft only:
- Exact approval required:
- Prohibited:

## Control and storage
- Task entry:
- Progress view:
- Approval channel:
- Notifications:
- Persistent information:
- Concurrent writers:
- History and retention:
- Provisional storage choice:

## First version
- End-to-end result:
- Included:
- Deferred:
- Target environments:
- Decision owner:

## Startup readiness
- Required integrations and data:
- Configuration references:
- Secret references without values:
- Minimum permissions:
- Setup owners and actions:
- Readiness checks:
- Behavior while blocked:

## Evidence
- Facts:
- Inferences:
- Hypotheses:
- Unknowns:
```

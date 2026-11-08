# Phase Detection

Phase detection is an evidence-backed coordination decision. A filename, repository type, or the mere presence of code is never sufficient.

## Phase vocabulary

- `UNKNOWN`: evidence is insufficient or contradictory.
- `DISCOVERY`: objectives, users, constraints, feasibility, or the problem itself are still being established.
- `PLANNING`: scope and approach are being designed, decomposed, estimated, or approved.
- `PLAN_READY`: an actionable plan, ownership, dependencies, acceptance criteria, and required approvals are ready for execution.
- `DEVELOPMENT`: planned deliverables are being produced or changed.
- `INTEGRATION_TESTING`: deliverables are being combined and evaluated against cross-workflow or acceptance criteria.
- `RELEASE_READY`: acceptance evidence and release/rollback material are sufficient; execution awaits a release decision or window.
- `PRODUCTION`: the deliverable is live, published, distributed, or actively used in its intended environment.
- `MAINTENANCE`: the live or accepted deliverable is being supported, monitored, corrected, or incrementally improved.
- `PAUSED`: intentional pause or unresolved blocker prevents meaningful progress. Preserve `paused_from` so the underlying phase is not lost.

These phases apply to software, websites, documents, research, data, design, and operations. Interpret “development,” “testing,” and “production” as creation, validation, and real-world use for the project type.

## Evidence precedence

Use newer and more authoritative evidence first:

1. the user's current-session description, decisions, and requested outcome;
2. project rules and explicitly designated authoritative sources;
3. the latest status, handoff, checkpoint, task board, or approved decision record;
4. current implementation, artifact, test, integration, release, and deployment evidence;
5. current dependency/configuration metadata and bounded workspace observations;
6. historical plans, archived notes, old reports, and repository history.

Lower-ranked evidence can corroborate but should not override a current authoritative statement without surfacing the contradiction. “Latest” means the newest trustworthy evidence, not the file with the newest filesystem timestamp alone.

## Detection procedure

1. Identify the authoritative root, requested outcome, and candidate workflows.
2. Collect a bounded evidence set, starting with directory shape and candidate current-state files.
3. Extract only claims relevant to phase gates: current outcome, completed work, open work, validation, approvals, release state, blockers.
4. Assign an overall phase and a separate phase for each workflow or module.
5. Record supporting and contradicting evidence, confidence, missing evidence, and the next gate.
6. If confidence is low, perform one focused read-only probe. If still low, ask one high-information question.

Do not read all project history to improve confidence. Stop when another file is unlikely to change the next safe action.

## Mixed phases

A project can be in multiple phases at once. Examples include a live service in `MAINTENANCE`, a new workflow in `DEVELOPMENT`, and a research track in `DISCOVERY`.

Choose the overall phase based on the phase that constrains the next project-level decision, not the most advanced artifact. Record workflow phases independently. If work is paused, set overall phase to `PAUSED`, retain `paused_from`, and describe the blocker.

Do not collapse conflicting evidence into an average. Keep the conflict visible and lower confidence.

## Confidence

Record a qualitative value and, optionally, a score:

- `high` (`0.80–1.00`): current authoritative evidence directly satisfies the phase definition and adjacent gates are distinguishable.
- `medium` (`0.50–0.79`): the likely phase is actionable, but one meaningful ambiguity remains.
- `low` (`0.00–0.49`): evidence is sparse, stale, or contradictory enough that the next action could materially change.

A numeric score is an aid, not a measurement. Always list the evidence and missing information that justify it.

## Phase gates

A transition requires evidence for the destination gate. Multiple transitions may be recorded at once when existing evidence already satisfies them; do not invent intermediate work.

| Destination | Minimum gate evidence |
|---|---|
| `DISCOVERY` | authoritative root or subject identified; objective or problem under investigation; evidence collection bounded |
| `PLANNING` | objective, scope boundaries, constraints, stakeholders or decision owner, and major unknowns recorded |
| `PLAN_READY` | actionable tasks, dependencies, ownership, acceptance criteria, resource conflicts, risk/approval points, and validation approach recorded |
| `DEVELOPMENT` | approved or otherwise authorized task packet exists; executor and writable scope are clear; required inputs are available |
| `INTEGRATION_TESTING` | candidate deliverables exist; relevant component checks are complete or exceptions disclosed; integration/acceptance environment and criteria are defined |
| `RELEASE_READY` | required acceptance checks pass; unresolved issues meet policy; release, rollback/recovery, ownership, and approval evidence are ready |
| `PRODUCTION` | explicit release authorization where required and observed evidence that the deliverable is live/published/in use |
| `MAINTENANCE` | operational ownership exists and active work concerns support, monitoring, correction, or incremental improvement of an accepted/live deliverable |
| `PAUSED` | explicit pause decision or concrete blocker, owner, next review condition, and `paused_from` recorded |

`UNKNOWN` is not a failure. Use it whenever the evidence does not justify another phase.

## Common false signals

- Source code exists: could be a template, archived prototype, dependency, or maintained production system.
- Tests exist: does not prove they ran or passed.
- A deployment file exists: does not prove a release occurred.
- A plan says “complete”: does not prove current artifacts satisfy it.
- A recent timestamp exists: generated or copied files can be newer than authoritative state.
- A live URL exists: does not prove the current workspace matches production.

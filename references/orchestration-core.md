# Orchestration Core

Use this reference when a project needs more than one task or session.

## 1. Main-session contract

Under `STRICT_ORCHESTRATOR`, the main session owns:

- user communication and clarification;
- project-phase and project-profile decisions;
- task decomposition, dependency ordering, and resource-conflict analysis;
- dispatch, status checks, evidence review, integration decisions, and reporting;
- approval requests and escalation.

It does not silently perform the implementation assigned to a work session. If no delegated-session mechanism is available or authorized, state that constraint and ask whether to execute the task in the current session or provide a dispatch plan only.

Project configuration may choose a less strict mode, but cannot bypass current user scope, platform permissions, or active safety and context limits.

## 2. One session, one active task

A work session has exactly one active task by default. Its packet must identify one outcome and one completion decision. A task may contain tightly coupled steps only when they share the same acceptance criteria and resource set.

Do not reuse a busy session for unrelated work. Queue the task, create another authorized session, or wait. A project profile may override this default only when it defines an equally clear ownership and context-isolation rule.

## 3. Build the dependency and resource graph

For every task, record:

- predecessors and artifacts consumed;
- files, modules, datasets, documents, environments, accounts, channels, or release surfaces touched;
- access mode: `read`, `shared_write`, `exclusive_write`, or `protected`;
- external side effects and approval requirements;
- expected delivery and review evidence.

Two tasks may run in parallel only if:

1. neither depends on the other's unfinished output;
2. they do not claim the same exclusive resource;
3. their shared writes have an explicit merge owner and non-overlapping change set;
4. neither can invalidate the other's test or review environment;
5. protected actions remain separately approved.

When uncertain, serialize. Parallel speed is not worth ambiguous ownership or evidence.

## 4. Dispatch flow

1. Select the smallest dependency-complete batch.
2. Reserve resources before dispatch.
3. Issue one task packet per session from `task-packet.md`.
4. Confirm the session accepted the packet and constraints.
5. Track state as `queued`, `active`, `waiting`, `review`, `passed`, `failed`, `takeover`, or `archived`.
6. Release resource reservations only after delivery is captured or the task is explicitly abandoned.

Session tools are environment-dependent. Creating, messaging, taking over, or archiving sessions must be authorized by the user and supported by the platform.

## 5. Status and stall checks

Use observable timestamps, task events, or explicit status snapshots. The default possible-stall threshold is 60 minutes without meaningful progress, not 60 minutes since dispatch regardless of activity.

A status message counts as progress only when it adds one of:

- a completed acceptance item;
- new primary evidence;
- a concrete blocker with owner and next action;
- a changed estimate grounded in discovered work;
- a requested approval that actually gates progress.

If no background scheduler or waiting mechanism exists, do not promise automatic checks. Perform the check when the session is next observable, or offer an authorized reminder/automation if the environment supports it.

For takeover mechanics, use `handoff-protocol.md`.

## 6. Delivery and evidence review

A delivery packet is a claim, not proof. The main session or reviewer should inspect the minimum primary evidence needed to verify:

- changes are within allowed scope;
- outputs exist at the stated locations;
- tests or checks actually ran and their relevant results match the claim;
- unresolved failures, warnings, assumptions, and external effects are disclosed;
- protected resources were not changed without approval.

Prefer exact file locations, commands, timestamps, artifact identifiers, and concise result excerpts. Avoid importing full logs into the main context.

## 7. Independent review

Use an independent reviewer for consequential shared behavior, integration boundaries, release readiness, production changes, irreversible actions, or when the task packet requires it.

The reviewer receives the original task packet, the delivery packet, and primary artifacts. It should not receive the implementer's hidden reasoning or a prompt that reveals the desired verdict.

Review outcomes:

- `PASS`: acceptance criteria are met with sufficient evidence;
- `PASS_WITH_RISKS`: criteria are met but explicit residual risks remain accepted or awaiting acceptance;
- `CHANGES_REQUIRED`: correctable gaps remain;
- `BLOCKED`: evidence or access is insufficient for a verdict.

The main session resolves disagreements using primary evidence. It does not average opinions.

## 8. Integration and reporting

Integrate only reviewed, dependency-complete work. Re-run the smallest meaningful cross-task verification after integration because individually passing tasks can conflict when combined.

Report:

1. completed tasks and evidence;
2. review verdicts;
3. remaining risks and blockers;
4. approvals required before the next action;
5. the next dependency-complete, conflict-free batch;
6. current context status and whether migration is needed.

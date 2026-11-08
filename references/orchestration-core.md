# Orchestration Core

Use this reference when a project needs more than one task or session.

## 1. Main-session contract

`STRICT_ORCHESTRATOR` is mandatory for every main session, before and after handoff. The main session owns:

- user communication and clarification;
- project-phase and project-profile decisions;
- task decomposition, dependency ordering, and resource-conflict analysis;
- dispatch, status checks, evidence review, integration decisions, and reporting;
- approval requests and escalation.

All implementation and execution-based verification are assigned to persistent project implementation/review chats. The main session must not edit code or project files; run commands, scripts, tests, builds, or diagnostic probes; or execute commits, integration changes, deployments, or concrete release operations. It may inspect minimal existing delivery/evidence artifacts and use authorized session tools, but must not run acceptance checks itself.

This is a role boundary, not a preference: project configuration cannot choose a less strict mode. Worker faults, reconnects, timeouts, urgent requests, and missing tools are not exceptions. With no usable persistent chat or authorized route, report the specific blocker and request access or same-role persistent recovery authorization; never fall back to main-session or temporary-agent execution. Keep coordination state inline and delegate any authorized durable record/file write to a persistent project chat.

### Boundary checks for dispatch and acceptance

| Situation | Main-session action | Execution/evidence owner |
|---|---|---|
| Normal task, before handoff | Decompose, authorize/dispatch, track acceptance and execution | Persistent project implementation chat |
| Main-session handoff | Restore existing chat IDs, reservations and monitoring; remain orchestrator | Existing persistent implementation/review chats |
| Worker fault/reconnect threshold or user urgency | Diagnose from existing evidence; coordinate authorized same-role persistent recovery; keep monitoring | Persistent successor after safe writer transfer, never main/temporary agent |
| No usable persistent chat or session tool | Report the concrete blocked operation and request necessary access/authorization | Execution remains blocked; no local fallback |
| Acceptance requires a command/test/build | Dispatch the check and inspect its returned result; do not run it | Persistent implementation/review chat |
| Profile, registry or handoff must be saved | Keep state inline until an authorized persistent chat can write it | Persistent project chat at the approved path |
| Commit, integration, deployment or release is approved | Coordinate gates and monitor the authorized operation | Persistent project implementation/release chat |

### Preserve the execution channel after main-session handoff

A project-directory work or review chat is a persistent, user-visible project session, not a temporary agent spawned inside the main chat. Sharing a role name or workspace does not make the two interchangeable.

- A successor main session inherits the existing session registry, task ownership, resource reservations, pending reviews, and applicable authorization evidence. Only the controller changes; workers continue their current tasks.
- Reconcile registered IDs with current platform metadata and documented same-role replacements before dispatch. A stale registry, matching title, or `notLoaded` status alone is not evidence that a chat must be replaced. Verify project/workspace scope; do not contact unrelated chats.
- Use the existing project-chat channel for implementation and independent review. In Codex, use the available `list_threads` / `read_thread` tools for discovery and inspection, and `send_message_to_thread` / `wait_threads` for authorized dispatch and tracking. `spawn_agent` does not restore control of an existing project chat.
- A handoff, context migration, convenience, or missing chat tool does not authorize temporary agents or main-session execution. Create a same-role persistent replacement only under applicable recovery authorization. If the route or authorization cannot be recovered, report the specific blocker and ask the user; do not change channels or take over implementation.
- Send only the next task or missing continuation state to the verified chat. Do not restart its task, reset an authorized implementation task to read-only, or repeat completed checks solely because the main session changed. Reuse unchanged evidence; check new changes and concrete uncertainty.

Follow `handoff-protocol.md` for the continuity packet, takeover completion gate, and recovery from a misrouted task.

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
4. Immediately start the monitoring loop in section 5. A successful send means `queued`, not `active`; obtain an observable acknowledgment or actual task progress rather than ending the turn at that disclaimer.
5. Track state as `queued`, `accepted`, `active`, `waiting`, `review`, `passed`, `failed`, `takeover`, or `archived`.
6. Release resource reservations only after delivery is captured or the task is explicitly abandoned.
7. Keep a named monitoring owner until verified delivery, a concrete escalated blocker, or confirmed transfer to another main session. The rule applies equally to original and successor main sessions, and to review tasks.

Session tools are environment-dependent. Creating, messaging, taking over, or archiving sessions must be authorized by the user and supported by the platform.

## 5. Mandatory dispatch monitoring and stall checks

Monitoring is part of dispatch, not an optional follow-up. Every main session must close the loop for each work/review chat, whether or not the main session has been handed over.

### Monitoring loop

1. Record the target chat ID, task ID, available dispatch/turn reference, send time, monitoring owner, and current state. Immediately inspect a compact status snapshot after sending; correlate it to this task, not an earlier completed turn.
2. If acceptance or execution is not yet visible, keep waiting and checking. In Codex, prefer `wait_threads` with its returned cursor as `afterCursor` and a bounded nonzero `timeoutMs` (normally 120000); use a zero-timeout snapshot for the initial check. Use `read_thread` only for a small targeted inspection when the snapshot cannot establish acceptance, progress, or the cause of waiting. Do not repeatedly reload full histories.
3. During each check, inspect available reconnect/error evidence. At 3 distinct consecutive child-chat reconnects without meaningful progress (4 only when explicitly selected by the user), immediately run the same-role project-chat takeover in `handoff-protocol.md` section 1.1; do not wait for an acknowledgment deadline or the 60-minute stall check. Do not count polling timeouts or repeated snapshots as reconnects.
4. Count acceptance only from a task-specific acknowledgment or actual task progress. An open chat, a successful send, or an unrelated old completion is not proof of execution. When a queued task has no such evidence by the acknowledgment deadline (default 5 minutes from a real send timestamp), inspect the latest turn for an approval gate, error, disconnection, busy worker, or rejected task. Diagnose and recover through the authorized project-chat route; do not blindly resend or create a duplicate worker.
5. After acceptance, keep checking actual progress and completion through real waits/status snapshots. A timeout is a checkpoint, not completion or permission to stop monitoring. Continue useful independent orchestration between checks where possible; keep monitoring all active tasks rather than only the last one dispatched.
6. On a completion event, obtain the delivery packet and verify the task's acceptance evidence under section 6. Completion of a chat turn alone does not prove task completion. Route needed corrections or independent review through the registered project chats, and monitor those dispatches too.
7. End the dispatch cycle only after verified delivery, an evidence-backed blocker requiring escalation/user action, or confirmed transfer to another monitoring owner. For a long-running task, ending the current turn with an interim status is allowed only when an authorized live background monitor really exists, with a recorded mechanism/identifier, owner, and next check. If no scheduler exists but synchronous wait/status tools do, keep using them; do not stop at “sent, awaiting confirmation.” Never equate a finished wait call or a promise to check later with a running monitor.

A real approval or missing-access blocker may require the user; state its evidence and exact next action. Do not mislabel mere lack of acknowledgment, a normal wait timeout, or absence of a background scheduler as a terminal blocker while usable synchronous monitoring remains available. Do not create an automation or message another chat without the required user authorization.

### Detect and recover from stalls

Use observable timestamps, task events, or explicit status snapshots. The default possible-stall threshold is 60 minutes without meaningful progress, not 60 minutes since dispatch regardless of activity. The acknowledgment deadline is a separate early diagnostic checkpoint. Escalate observed errors or a blocked approval immediately; do not wait an hour after a known failure.

A status message counts as progress only when it adds one of:

- a completed acceptance item;
- new primary evidence;
- a concrete blocker with owner and next action;
- a changed estimate grounded in discovered work;
- a requested approval that actually gates progress.

The confirmed reconnect threshold is an independent immediate takeover trigger, not a 60-minute stall. On any other real stall, inspect the current task, diagnose the cause, and use `handoff-protocol.md` for an authorized same-role takeover if needed. Preserve the existing project-chat execution channel and prevent duplicate writers. Context migration must transfer the active monitoring state and next check rather than dropping unfinished tasks. Never claim continuous monitoring without an observable mechanism.

## 6. Delivery and evidence review

A delivery packet is a claim, not proof. The main session inspects the minimum existing primary evidence below; a persistent reviewer performs any needed reproduction or execution-based check:

- changes are within allowed scope;
- outputs exist at the stated locations;
- tests or checks actually ran and their relevant results match the claim;
- unresolved failures, warnings, assumptions, and external effects are disclosed;
- protected resources were not changed without approval.

Prefer exact file locations, commands, timestamps, artifact identifiers, and concise result excerpts. Avoid importing full logs into the main context. If a claim needs a new command, script, test, or build, dispatch it to a persistent implementation/review chat and monitor delivery; the main session must not run it under an acceptance or diagnostic label.

## 7. Independent review

Use an independent persistent project review chat for consequential shared behavior, integration boundaries, release readiness, production changes, irreversible actions, or when the task packet requires it. If unavailable, report the unmet review gate; neither the main session nor a temporary agent substitutes for that reviewer.

The reviewer receives the original task packet, the delivery packet, and primary artifacts. It should not receive the implementer's hidden reasoning or a prompt that reveals the desired verdict.

Review outcomes:

- `PASS`: acceptance criteria are met with sufficient evidence;
- `PASS_WITH_RISKS`: criteria are met but explicit residual risks remain accepted or awaiting acceptance;
- `CHANGES_REQUIRED`: correctable gaps remain;
- `BLOCKED`: evidence or access is insufficient for a verdict.

The main session resolves disagreements using primary evidence. It does not average opinions.

## 8. Integration and reporting

The main session decides whether reviewed, dependency-complete work may integrate. Assign the actual integration, commit, deployment, release operations, and smallest meaningful post-integration checks to authorized persistent project chats; individually passing tasks can conflict when combined. Inspect their returned evidence and keep monitoring until the applicable gates pass or a concrete blocker is escalated.

Report:

1. completed tasks and evidence;
2. review verdicts;
3. remaining risks and blockers;
4. approvals required before the next action;
5. the next dependency-complete, conflict-free batch;
6. current context status and whether migration is needed.

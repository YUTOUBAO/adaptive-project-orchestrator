---
name: adaptive-project-orchestrator
description: Inspect an existing software, website, document, research, data, design, or operations project; infer its current phase from evidence; create or refresh a project profile; and coordinate safe multi-session execution. Use when work spans multiple tasks, roles, modules, or handoffs and needs explicit resource, approval, review, takeover, or context-budget control. Do not use for a single self-contained task that needs no project-level coordination.
---

# Adaptive Project Orchestrator

Coordinate project work without assuming that code presence, directory names, or an old plan reveal the current phase.

## Mandatory main-session boundary

Every original or successor main session is an orchestrator only: communicate, decompose and dispatch tasks, coordinate resources and approvals, monitor acceptance and real execution, organize handoffs, inspect minimal delivery/verification evidence, and report results. This boundary applies before and after handoff; it is not a configurable default.

- All implementation and execution-based verification belong to persistent implementation/review chats in the project. The main session must not edit project code or files, run commands/scripts/tests/builds (including read-only probes and diagnostic or acceptance commands), or perform commits, integration changes, deployment, or concrete release operations.
- The main session may use session tools to inspect/control authorized chats and read the smallest necessary existing artifacts as evidence. Keep coordination notes inline; dispatch any authorized durable profile, registry, or handoff-file write to a persistent project chat. Calling it acceptance, diagnosis, or coordination does not exempt an execution or file write.
- Worker failure, reconnects, timeouts, missing tools, or pressure for progress never transfer execution to the main session or temporary agents. Coordinate recovery or an authorized same-role persistent takeover. If no usable persistent chat or route is available, report the concrete blocker and request the necessary access/authorization; do not offer main-session execution as a fallback.
- Retain the mandatory monitoring loop during recovery and review. Evidence inspection does not replace execution-based checks: dispatch missing checks to a persistent implementation/review chat and inspect its returned results.

## Operating defaults

Use these defaults unless an authoritative project profile sets stricter or more suitable values. A project override never relaxes active user instructions, authorization boundaries, or context limits.

- `STRICT_ORCHESTRATOR` is mandatory and non-overridable; the tunable defaults below govern scheduling, not execution authority.
- Give each work session one active task.
- Every main session, before or after handoff, must monitor each dispatched work/review chat through acceptance, real execution, delivery, and verification. Sending a task without confirming and tracking it is not a completed dispatch.
- Run tasks in parallel only when their dependencies and shared, exclusive, and protected resources do not conflict.
- Obtain item-specific approval immediately before high-risk, external, production, destructive, irreversible, or costly actions.
- Check possible stalls after 60 minutes by default only when real timestamps and a real check mechanism exist. Never claim continuous monitoring without one.
- A work/review chat with 3 confirmed consecutive reconnects without meaningful task progress triggers immediate same-role takeover into a new persistent project chat; the user may select 4 instead, never more. Do not wait for the 60-minute stall threshold. Follow `handoff-protocol.md` for evidence, safe ownership transfer, authorization, and retry-loop limits.
- A takeover keeps the original role name by default and archives the old session only after a usable handoff and successful takeover.
- Main-session handoff preserves control of the existing project-directory work and review chats. The successor remains the orchestrator; it must not replace those chats with temporary agents, including for review.

## Start with read-only reconnaissance

1. Confirm the authoritative project root and the user's current objective.
2. Inspect existing directory/inventory evidence before file contents. If a fresh inventory is needed, dispatch `scripts/project_probe.py` to a persistent project chat; the main session does not run it.
3. Read only the smallest set of current, authoritative evidence needed to classify the project and build its profile: normally no more than about 10–15 small files and about 40K input tokens.
4. Stop when evidence is sufficient. Do not read project history wholesale.
5. If confidence remains low, dispatch one focused read-only probe to a persistent project chat and inspect its evidence. If unavailable, report that constraint; if still unclear, ask one question whose answer most changes the next action.

For evidence precedence, mixed phases, confidence, and gates, read [references/phase-detection.md](references/phase-detection.md).

## Create or refresh the project profile

Record the overall phase separately from each workflow or module phase. Identify the authoritative working directory, objectives, evidence, shared/exclusive/protected resources, dependencies, testing policy, release policy, and approval policy.

Use [references/project-profile.md](references/project-profile.md). Keep the main session's profile inline. If the user authorizes a durable location, assign the write to a persistent project chat; that authorization does not make the main session an executor.

## Dispatch and control work

1. Convert the next approved outcome into dependency-aware tasks.
2. Build a resource-conflict map; parallelize only independent tasks.
3. Give every session one task packet with scope, allowed writes, acceptance criteria, evidence requirements, risk boundaries, and a context budget.
4. Immediately check acceptance and execution after dispatch, and keep a real wait/status loop or authorized live monitor until verified delivery, a concrete escalated blocker, or confirmed transfer of monitoring ownership. Never end merely with “sent, not yet confirmed.” Require a structured delivery packet and verify material claims from primary evidence.
5. Route consequential work through an independent review packet before integration or release.
6. On a real stall or the confirmed reconnect threshold, recover the minimum state, create a same-role takeover when authorized, resume the remaining task rather than restarting it, then archive the old session after takeover is verified. For a main-session handoff, restore the existing work/review chat routing under `handoff-protocol.md` before declaring takeover complete.
7. Report completed work, evidence, unresolved risks, approvals needed, and the next safe batch.

Read [references/orchestration-core.md](references/orchestration-core.md) for scheduling and review. Use [references/task-packet.md](references/task-packet.md) for dispatch, delivery, and review packets. Use [references/handoff-protocol.md](references/handoff-protocol.md) for stalls, takeovers, context migration, and archival.

## Hard boundaries

- Session creation, messaging, archiving, external calls, and project mutation require the permissions and user authorization applicable to the current environment.
- Never represent a timer, background worker, review, test, deployment, or approval as active or complete unless observable evidence confirms it.
- Original and successor main sessions retain monitoring ownership after every dispatch. A project profile may tune check deadlines, but must not silently disable monitoring or replace the established project-chat execution channel.
- Keep total input below `250,000 input_tokens`, including cached input, history, instructions, files, and tool output. At `220,000`, stop expanding context and migrate with a minimal handoff. If exact usage is unavailable, estimate conservatively and migrate early.
- Split oversized work into independently executable and verifiable batches. After each batch, check the latest usage when available before continuing.
- If any request reaches or exceeds `250,000 input_tokens`, stop substantive work and re-plan in a low-context session.
- Preserve user scope. Do not use orchestration as implied authorization for production, destructive, external, or irreversible actions.

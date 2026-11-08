# Handoff, Takeover, and Context Migration

Use this protocol for stalled work, repeated reconnects, planned session replacement, token-boundary migration, or archival.

## 1. Detect a possible stall

The default threshold is 60 minutes without meaningful progress. Measure only from observable timestamps or platform events. Meaningful progress is new acceptance evidence, completed work, a concrete blocker, or a gating approval request.

A possible stall is not proof of failure. Before takeover:

1. obtain a current status snapshot if the platform allows it;
2. identify whether the task is active, waiting on a dependency, waiting on approval, disconnected, or truly unresponsive;
3. avoid duplicate writers by preserving the resource reservation until ownership is resolved;
4. record the last verified artifact and timestamp.

If the environment cannot wait, schedule, or poll in the background, say so. Do not claim that a future check is active. Check when the session is next observable or create an authorized reminder/automation.

### 1.1. Repeated reconnects: immediate work-chat takeover

Apply this early trigger to work and review chats under both original and successor main sessions. The default threshold is **3 distinct consecutive reconnect events without meaningful task progress**; an explicit user setting may choose **4**, but not a larger threshold. At the threshold, enter `takeover` immediately instead of waiting for the 60-minute stall check or continuing to resend the task. This replaces one failed persistent project chat; it does not authorize switching to a temporary agent pool.

Count only reconnect events actually exposed by platform events, status/error history, or permitted logs and attributable to the same chat, task, and dispatch/turn. Record event references and observed times; deduplicate repeated observations of the same event. A normal wait timeout, slow output, `notLoaded`, failure of the main session's status request, or rereading the same error does not establish another child-chat reconnect. If the count is unavailable, record it as unknown and seek the smallest permitted status/error evidence; do not invent a count. Reset the consecutive streak only on meaningful task progress, not merely a transient connection success or a promise to start.

At the threshold:

1. Stop new dispatches and stop requesting retries of the failed chat. Use supported, authorized stop/interrupt controls to prevent further writes where available. Keep its task and resource reservations until writer ownership is safe; inability to stop an active writer is a real blocker, not permission for concurrent writes.
2. Capture a minimal checkpoint: the original task/authorization references, completed and remaining acceptance items, exact changed/uncommitted artifact locations, valid checks/evidence, any owned running processes, reservations, and the next executable action. If the old chat cannot answer, reconstruct this from bounded primary artifacts; do not wait indefinitely for its handoff or copy its full history.
3. Under the user's applicable automatic-recovery authorization, create a new persistent chat in the same project and authoritative workspace with the same role/title and applicable model settings. Carry the task ID, scope, authorization limits, and checkpoint; instruct it to execute the remaining work, not restart completed work or silently downgrade authorized implementation to read-only. Do not request repeated approval for an already-authorized in-scope replacement; missing tools or missing creation/messaging authorization must still be reported to the user.
4. Record the new chat ID, `replaces_session_id`, and takeover generation in the authorized registry or handoff state. Start a fresh reconnect streak for the new chat while retaining the old chat's trigger evidence. Transfer task ownership only after confirming no conflicting old writer remains, then verify the successor accepted and actually resumed the next action. Continue the mandatory monitoring loop; sending the checkpoint alone is not successful takeover.
5. Archive the old chat only after successful takeover and the ordinary archival conditions. Preserve prior changes and evidence; do not roll them back, overwrite them, or archive unrelated healthy chats.

If the first successor reaches the same reconnect threshold before meaningful progress, stop automatic replacement chaining and escalate the likely shared platform/provider or access problem. Keep the checkpoint and ownership safe instead of creating an unbounded sequence of chats. Creating a replacement does not expand production, external-action, destructive-action, or spending permissions.

## 2. Request the minimum handoff

Ask the current session for only the state needed to continue:

```yaml
handoff_version: 1
task_id: ""
role_name: ""
reason: "stall" # stall | reconnect_loop | planned | context_migration | platform_failure
last_verified_at: ""
status: ""
completed_acceptance_items: []
remaining_acceptance_items: []
artifacts_created_or_changed: []
commands_and_checks_run: []
concise_results: []
current_blocker: ""
resource_reservations: []
protected_or_external_actions: []
uncommitted_or_unpublished_state: []
next_exact_action: ""
context_needed_by_successor: []
latest_input_tokens: null
usage_is_estimated: true
reconnect_recovery: null # For reconnect_loop: source chat/task/dispatch, observed
# event references/times, consecutive count, threshold, takeover generation.
orchestration_state: null # Required for main-session handoff; see section 3.1.
```

Do not copy the full conversation, logs, or unrelated project history into the handoff.

## 3. Same-name takeover

The successor uses the original `role_name` by default so project ownership remains understandable. Distinguish instances with `takeover_generation` or a session identifier, not a new functional role name.

Takeover sequence:

1. freeze new writes or dispatches by the old session when possible; a main-session handoff does not stop healthy workers already executing their assigned tasks;
2. capture or reconstruct the minimum handoff from primary artifacts;
3. create or assign the authorized successor with the original task packet plus the handoff;
4. have the successor confirm the authoritative workspace, resource reservations, last verified state, and next action; for a main-session successor, also complete the session-control checks in section 3.1;
5. release the old session's write ownership only after the successor can continue safely;
6. archive the old session after successful takeover, unless retention policy requires it to remain visible.

If duplicate writes cannot be prevented, stop both writers and reconcile before continuing.

### 3.1. Main-session continuity

A main-session successor must continue controlling the existing project-directory work and review chats, not create a temporary agent pool to replace them. This applies to planned handoff, stalls, platform recovery, and context migration. Changing execution channels requires explicit user authorization; taking over the main role is not that authorization.

For a main-session handoff or migration, replace `orchestration_state: null` with this compact mapping:

```yaml
orchestration_state:
  previous_main_session_id: ""
  execution_channel: "project_chats"
  session_registry: "" # Authorized path/reference, if available.
  controlled_sessions: [] # Inline records when no retrievable registry exists.
  # Each registry/inline record: session_id, host_id, project_id, workspace_root,
  # role_name, kind (work/review), task_id, task_packet, status,
  # resource_reservations, replaces_session_id, last_verified_at
  pending_dispatches: [] # Task-packet references and intended session IDs.
  pending_reviews: []
  monitoring_state: [] # Per task: chat ID, dispatch reference, state, owner,
  # sent_at, last_checked_at, last_progress_at, mechanism, next_check_at,
  # consecutive_reconnects (null if unknown), last_reconnect_event_ref.
  authorization_refs: [] # User evidence, scope, and outstanding approvals.
```

Use an existing authorized registry location; do not invent or write a project file without permission. Prefer a reference over duplicating a large roster, but never leave both the registry and inline records empty when controlled chats exist. Do not copy chat histories into this mapping.

Before declaring takeover complete:

1. Locate the registry and reconcile relevant work/review chats against current platform metadata and documented replacement chains. Verify their stable IDs, host/project/workspace scope, current tasks, and reservations; names and stale status labels are insufficient. If the packet lacks a registry, recover it with bounded read-only discovery rather than spawning agents.
2. Confirm the old main is no longer dispatching and the successor has the tools and applicable user authorization to inspect and message the existing chats. A handoff reference is not itself permission. Perform a bounded read/status check on an active controlled chat when one exists; if access or identity remains unresolved, report incomplete control recovery rather than claiming success.
3. Take ownership of all queued, unacknowledged, active, and review-stage monitoring records, then perform the next real status/wait check. Resume pending dispatches and reviews through verified chats without duplicating a busy worker's task. Preserve scope, authorization, and valid evidence; do not end with an unconfirmed-send disclaimer. If an old monitor exists, confirm its status and transfer/retire it when authorized so monitoring is neither dropped nor duplicated.
4. Report the recovered chat roles/IDs, active tasks, unresolved routes, and next safe dispatch. Archive the old main only after the continuity gate and ordinary archival conditions pass. Do not archive or recreate healthy workers merely because their controller changed.

If work was already sent through the wrong channel, stop new dispatches and request a safe stop from that worker using the available authorized controls. Capture its changed paths, artifacts, checks, remaining work, reservations, and any still-running processes; confirm no conflicting writer remains before resuming in the correct chat. Preserve existing changes and evidence without rollback or forced overwrite. Close the erroneous temporary agent only when safe and authorized; do not close the project chat.

## 4. Context and token boundary

Count total input, including cached input, prior messages, system and project instructions, tool results, and file contents.

- Below `220,000 input_tokens`: continue only if the next batch safely fits.
- At or above `220,000`: stop expanding the context, finish only the minimal safe checkpoint, and migrate.
- At or above `250,000`: stop substantive work immediately. Do not dispatch, review, or load more material until the work is re-planned in a low-context session.
- If exact usage is unavailable: estimate conservatively from all loaded material, include a safety margin, and migrate before confidence is lost.

Cached input still counts. A cheap or cached request is not a small request for this boundary.

After every batch, inspect the latest usage when available. Split larger work into independently executable and verifiable batches before sending content to another session.

## 5. Minimal migration packet

A new low-context session receives only:

```yaml
migration_version: 1
project: ""
authoritative_workspace: ""
current_objective: ""
profile_version: 1
overall_phase: "UNKNOWN"
workflow_phase: "UNKNOWN"
current_task_packet: ""
completed_decisions: []
primary_artifacts: []
resource_reservations: []
required_approvals: []
known_blockers: []
next_exact_action: ""
verification_needed: []
orchestration_state: null # Required for main-session migration; see section 3.1.
```

Prefer paths and identifiers over pasted artifacts. Include evidence excerpts only when the successor cannot safely retrieve the source.

## 6. Archival rules

Archive a session only when:

- its deliverable and evidence were captured, or its failure state was recorded;
- no exclusive resource remains ambiguously owned;
- any successor has confirmed takeover;
- outstanding protected or external actions are visible;
- archival is authorized and supported by the environment.

Do not archive merely to hide a stalled or failed session. Preserve enough status for audit and recovery, but do not retain secrets or oversized logs in the handoff.

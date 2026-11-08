# Handoff, Takeover, and Context Migration

Use this protocol for stalled work, planned session replacement, token-boundary migration, or archival.

## 1. Detect a possible stall

The default threshold is 60 minutes without meaningful progress. Measure only from observable timestamps or platform events. Meaningful progress is new acceptance evidence, completed work, a concrete blocker, or a gating approval request.

A possible stall is not proof of failure. Before takeover:

1. obtain a current status snapshot if the platform allows it;
2. identify whether the task is active, waiting on a dependency, waiting on approval, disconnected, or truly unresponsive;
3. avoid duplicate writers by preserving the resource reservation until ownership is resolved;
4. record the last verified artifact and timestamp.

If the environment cannot wait, schedule, or poll in the background, say so. Do not claim that a future check is active. Check when the session is next observable or create an authorized reminder/automation.

## 2. Request the minimum handoff

Ask the current session for only the state needed to continue:

```yaml
handoff_version: 1
task_id: ""
role_name: ""
reason: "stall" # stall | planned | context_migration | platform_failure
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
```

Do not copy the full conversation, logs, or unrelated project history into the handoff.

## 3. Same-name takeover

The successor uses the original `role_name` by default so project ownership remains understandable. Distinguish instances with `takeover_generation` or a session identifier, not a new functional role name.

Takeover sequence:

1. freeze new writes by the old session when possible;
2. capture or reconstruct the minimum handoff from primary artifacts;
3. create or assign the authorized successor with the original task packet plus the handoff;
4. have the successor confirm the authoritative workspace, resource reservations, last verified state, and next action;
5. release the old session's write ownership only after the successor can continue safely;
6. archive the old session after successful takeover, unless retention policy requires it to remain visible.

If duplicate writes cannot be prevented, stop both writers and reconcile before continuing.

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

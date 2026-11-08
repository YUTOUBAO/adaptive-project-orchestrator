# Project Profile

Create or refresh this profile after bounded reconnaissance. Keep observed facts separate from inferences. A profile coordinates work; it does not grant permission to write, release, message external systems, or perform protected actions.

Do not assume the profile must live inside the project. Keep it in the current session unless the user authorizes a durable path. If an existing authoritative profile exists, preserve its supported fields and update only evidence-backed values.

## YAML template

```yaml
profile_version: 1
updated_at: ""
profile_authority:
  status: "draft" # draft | confirmed | project_authoritative
  sources: []

project:
  name: ""
  kind: "" # software | website | document | research | data | design | operations | mixed
  objective: ""
  deliverables: []
  stakeholders: []
  constraints: []

workspace:
  authoritative_root: ""
  working_directory: ""
  additional_roots: []
  root_evidence: []
  allowed_external_locations: []

phase:
  overall:
    value: "UNKNOWN"
    confidence: "low"
    score: 0.0
    paused_from: null
    supporting_evidence: []
    contradicting_evidence: []
    missing_evidence: []
    next_gate: ""
  workflows: []
  # Each workflow item uses:
  # - id, name, scope, phase, confidence, score, evidence, blockers, next_gate

resources:
  shared: []
  exclusive: []
  protected: []
  # Resource item fields:
  # - id: stable coordination name
  #   kind: file | directory | module | dataset | document | environment | account | channel | release_surface | other
  #   locator: path or unambiguous identifier
  #   access: read | shared_write | exclusive_write | protected
  #   owners: []
  #   conflict_notes: ""
  #   approval_rule: ""

work:
  active_tasks: []
  queued_tasks: []
  blocked_tasks: []
  dependency_edges: []
  integration_owner: ""

policies:
  orchestration:
    mode: "STRICT_ORCHESTRATOR"
    one_active_task_per_session: true
    dispatch_monitoring_required: true
    acknowledgment_timeout_minutes: 5
    parallel_only_without_resource_conflict: true
    stall_check_minutes: 60
    monitoring_mode: "observable_checks_only"
    takeover_reuses_role_name: true
    archive_old_session_after_takeover: true
  reconnaissance:
    target_input_tokens: 40000
    small_file_limit: 15
    directory_first: true
    stop_when_evidence_sufficient: true
  context:
    hard_input_token_limit: 250000
    migration_warning_input_tokens: 220000
    cached_input_counts: true
    unknown_usage_policy: "estimate_conservatively_and_migrate_early"
  approvals:
    per_action_required_for:
      - "high_risk"
      - "external_side_effect"
      - "production"
      - "destructive"
      - "irreversible"
      - "material_cost"
    approvers: []
    evidence_required: true
  testing:
    required_checks: []
    acceptance_owner: ""
    failure_policy: "block_unless_exception_is_explicitly_approved"
    evidence_retention: "paths_commands_and_concise_results"
  release:
    environments: []
    release_owner: ""
    required_approvals: []
    rollback_or_recovery_required: true
    production_verification_required: true

sessions:
  main_role: "orchestrator"
  main_session_id: ""
  execution_channel: "" # Record the established channel, e.g. project_chats.
  registry_location: "" # Existing authorized path/reference, if any.
  work_sessions: []
  review_sessions: []
  # Each work/review item: session_id, host_id, project_id, workspace_root,
  # role_name, kind, task_id, task_packet, status, resource_reservations,
  # replaces_session_id, last_verified_at, monitoring
  # monitoring: owner_session_id, dispatch_ref, sent_at, state,
  # last_checked_at, last_progress_at, mechanism, next_check_at
  role_name_registry: []

policy_overrides: []
# Each override records:
# - key, previous_value, new_value, authoritative_source, reason, effective_at
# Overrides cannot relax active user instructions, authorization boundaries, or hard context limits.

open_questions: []
risks: []
next_safe_batch: []
```

## Profile rules

### Authority and freshness

- Record why the authoritative root is authoritative: user statement, project rule, active workspace binding, or another explicit source.
- Use absolute paths when the environment exposes them; do not guess missing roots.
- Prefer current-session decisions and designated state files over timestamps or old plans.
- Add source locations and dates to evidence where available.

### Session continuity

Record actual persistent project-chat IDs and their documented replacements, not only role names. Reconcile stale entries with current platform evidence before dispatch. On main-session handoff, preserve the work/review chat channel and carry this registry in `orchestration_state` under `handoff-protocol.md`; the receiving session must still verify applicable authorization. Do not treat a missing registry or inaccessible chat as permission to spawn temporary agents.

### Overall and workflow phases

`phase.overall` represents the phase constraining the next project-level decision. `phase.workflows` records different module or workstream phases. Do not force all workflows into the overall phase.

A workflow item should look like:

```yaml
- id: "content-validation"
  name: "Content validation"
  scope: ""
  phase: "INTEGRATION_TESTING"
  confidence: "medium"
  score: 0.7
  evidence: []
  blockers: []
  next_gate: ""
```

If paused, use `value: "PAUSED"` and retain the underlying phase in `paused_from`.

### Resource classes

- `shared`: concurrent read access or explicitly coordinated non-overlapping writes are acceptable.
- `exclusive`: only one active task may write or control the resource.
- `protected`: access requires explicit approval or elevated handling, regardless of scheduling.

A protected resource is not automatically exclusive, and an exclusive resource is not automatically high risk. Record both properties where needed.

### Tests, release, and approvals

Testing policy defines the evidence required to call a task, workflow, integration, or deliverable complete. Release policy defines who can release, required checks, recovery preparation, and post-release verification. Approval policy identifies actions that require item-specific authorization immediately before execution.

Do not infer approval from a task's existence, a plan's approval, or access credentials.

### Overrides

Project configuration may override operating defaults when the authoritative source and reason are recorded. Choose stricter values when sources disagree. Never use an override to exceed the active input-token cap, bypass authorization, fabricate monitoring, or expand user scope.

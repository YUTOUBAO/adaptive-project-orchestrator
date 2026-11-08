# Task, Delivery, and Review Packets

Use structured packets to keep each work session focused and independently verifiable. Keep packets small enough to fit the session's context budget.

## Dispatch packet

```yaml
packet_version: 1
packet_type: "task"
task_id: ""
project_profile_version: 1
role_name: ""
takeover_generation: 0
single_outcome: ""
why_now: ""

inputs:
  required_artifacts: []
  authoritative_sources: []
  assumptions: []

dependencies:
  predecessors: []
  required_states: []

scope:
  allowed_reads: []
  allowed_writes: []
  forbidden_areas: []
  non_goals: []

resources:
  reservations: []
  # Each reservation: id, access, locator, release_condition
  protected_resources: []

acceptance:
  criteria: []
  required_checks: []
  required_artifacts: []
  independent_review_required: false

authorization:
  already_authorized: []
  must_request_before_action: []
  external_side_effects_allowed: false

context_budget:
  target_input_tokens: 0
  warning_input_tokens: 220000
  hard_input_tokens: 250000
  material_loading_rules: []

reporting:
  progress_events: []
  acceptance_confirmation_required: true
  monitoring_owner_session_id: ""
  acknowledgment_deadline: "" # Derived from a real dispatch timestamp.
  delivery_packet_required: true
  stop_conditions: []
```

### Dispatch rules

- `single_outcome` must permit one clear completion verdict.
- Allowed writes are explicit and minimal. Omission does not imply permission.
- State exact predecessors and resource reservations before dispatch.
- Separate authorization to analyze an action from authorization to perform it.
- Include the minimum source material. Point to files instead of pasting large content when the session can read them safely.
- Define stop conditions for missing access, conflicting changes, failed safety checks, unexpected external effects, or context pressure.
- The main session owns acceptance checks, execution/completion monitoring, and delivery verification under `orchestration-core.md`. Do not finish dispatch at “sent”; on main-session handoff, transfer this ownership and its current check state.

## Delivery packet

```yaml
packet_version: 1
packet_type: "delivery"
task_id: ""
role_name: ""
status: "complete" # complete | partial | blocked | failed
summary: ""

changes:
  created: []
  modified: []
  deleted: []
  external_effects: []

acceptance_results: []
# Each result: criterion, verdict, evidence

verification:
  commands: []
  checks: []
  artifacts: []
  concise_results: []

scope_report:
  stayed_within_allowed_writes: true
  unexpected_changes: []
  protected_actions: []

risks:
  unresolved: []
  assumptions: []
  warnings: []

handoff:
  next_action: ""
  state_needed_by_successor: []
  resources_safe_to_release: []
  resources_still_reserved: []

context:
  latest_input_tokens: null
  usage_is_estimated: true
  migration_needed: false
```

### Delivery rules

- Cite primary evidence with exact paths, artifact IDs, commands, or concise result excerpts.
- Do not paste large logs. Preserve their location and quote only the lines needed for the verdict.
- Disclose tests not run, failures, warnings, assumptions, and side effects.
- `complete` means every criterion has a verdict and sufficient evidence; it does not mean “work stopped.”

## Independent review packet

```yaml
packet_version: 1
packet_type: "review"
review_id: ""
task_id: ""
reviewer_role: ""

review_inputs:
  original_task_packet: ""
  delivery_packet: ""
  primary_artifacts: []
  required_checks: []

independence:
  implementer_role: ""
  reviewer_is_independent: true
  intended_verdict_was_not_provided: true

review_scope:
  acceptance_criteria: []
  risk_focus: []
  excluded_questions: []

verdict: "BLOCKED" # PASS | PASS_WITH_RISKS | CHANGES_REQUIRED | BLOCKED
findings: []
# Each finding: severity, criterion, evidence, impact, required_action

verification:
  commands: []
  artifacts_checked: []
  concise_results: []

residual_risks: []
release_recommendation: ""
```

### Review rules

- Review the requested outcome and evidence, not the implementer's style or hidden reasoning.
- Reproduce the smallest decisive checks when practical.
- A finding cites a specific criterion or risk and primary evidence.
- Use `BLOCKED` when evidence or access is insufficient; do not guess a pass or failure.
- The orchestrator resolves conflicting claims from artifacts and observable results, not role seniority.

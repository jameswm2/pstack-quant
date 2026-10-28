# Campaign contract and controller reference

## Authority and host execution

The frozen charter and sequential predecessor-bound events are the campaign authority. `view` derives a head-labelled resume packet. Never edit events, synthesize a replacement history, or treat an exported packet as authority. Studies retain the unchanged `evidence.py` API and scientific gates. A campaign decision does not accept a scientific claim.

The controller validates artifacts, ordering, budgets, and declared review bindings. The coordinator and independent reviewers judge mechanism novelty, materiality, coverage, information gain, independence, and mission adequacy. Declared identities and judgments are not authenticated. A hash detects changed bytes, not true research. Cooperative locking and predecessor hashes do not resist malicious rewriting of all local history.

Use actual host capabilities and existing model and effort configuration. Repeated configured seats remain separate independent agents. Campaign priority uses one fresh independent reviewer under the existing priority extension, distinct from the study scientific panels. Do not recursively review the checkpoint. If a required reviewer is unavailable, leave its dependent work blocked and compare other useful routes.

Within an active authorized turn, execute bounded assignments, inspect evidence, close work, challenge priorities when due, and repeat until a valid stop. At a host boundary, persist the next concrete action. Host budget limits and interruption take precedence. [Codex long-horizon guidance](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex), [native Codex Goals](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex), and [Claude best practices](https://code.claude.com/docs/en/best-practices) describe host facilities. Discover actual tools; these links do not grant permission to start Goals or change host settings.

## Commands and persistence

Python 3.11+ and the standard library are sufficient. From the installed plugin root:

```sh
python3 tools/campaign.py start research/campaign --charter charter.json
python3 tools/campaign.py view research/campaign --json
python3 tools/campaign.py commit research/campaign --proposal decision.json --expect HEAD_FROM_VIEW
python3 tools/campaign.py trial research/campaign --assignment A01 --plan trial-plan.json
```

All commands print JSON; invalid operations exit 2. `view` can succeed with scientific blockers; inspect its study gates. No command launches models or executes research code. Trial registration calls the existing local evidence registration function with safe paths.

`charter/spec.json` freezes the supplied charter, actual UTC start, and computed deadline. `events/000001/record.json` onward contain sequence, predecessor digest, operation key, UTC observation, payload digest, and payload. Atomic directory publication and a short exclusive lock protect cooperative writes. `.pending-*` staging is incomplete and reported, never committed. `plans/STUDY--TRIAL/plan.json` freezes reserved plans. `studies/STUDY` contains ordinary study evidence. `work/ASSIGNMENT/ACTOR` is the recommended private artifact location.

Every proposal has a globally unique `key`, a `kind`, and optional `evidence` refs. A ref is `{"path":"work/A01/report.json","sha256":"64 lowercase hex characters"}` relative to the campaign root. References must exist and match. Referenced evidence remains part of replay integrity; changed or missing bytes block reuse and spending. Correct an upstream artifact by preserving its old bytes and adding a new artifact and decision, never overwriting a cited file.

Identical operation retries succeed after intervening events; changed payloads under the same key fail. A fresh operation needs the exact prior head. Re-run `view` and reconsider a stale proposal rather than replacing its expected head blindly. Clock regression blocks spending until authoritative UTC catches up to the last ledger observation. Do not manually move ledger timestamps or reset the deadline.

## Frozen charter

See the executable [example charter](../../../examples/campaign/charter.json). Fields are:

- `schema`: 1.
- `mission`, `completion`, `coordinator`: nonempty original mission, adequacy criteria, and coordinator identity.
- `scope`: nonempty unique meaningful mission dimensions. Do not narrow them silently.
- `resources`: nonempty object describing authorized data, tools, compute, and spending boundaries.
- `wall_seconds`, `trial_limit`: positive cumulative ceilings.
- `reserve_seconds`, `reserve_trials`: nonnegative protected synthesis or replication capacity, below their respective ceilings.
- `triggers`: positive integers `units`, `same_family`, `no_information`, `failures`, and `active_minutes`.

The example uses 30 coordinator-reported active minutes, three closed units, two same-family commitments, two no-information closures, and two execution failures. A closure marked `material` also triggers review. Active minutes are reported metadata, never measured thinking time or a replacement for wall time. Cumulative failure and assignment histories survive checkpoints. The consecutive same-family run also survives an early checkpoint; it resets only when actual work changes family. Other priority counters start after the latest reviewed frontier checkpoint.

## Proposal schemas

Unlisted scientific text is qualitative judgment, not a mechanically proven fact. All text fields below must be nonempty. Every accepted review is embedded as `review` and also cited in `evidence` as the exact canonical JSON review artifact, serialized with sorted keys, two-space indentation, and a trailing newline. Use `evidence.canonical` when preparing that artifact.

A review has `head`, `reviewer`, `rationale`, `alternatives`, `neglected_scope`, and `verdict:"accept"`. `head` must equal the exact prior ledger head; the declared reviewer must differ from the charter coordinator. The reviewer reads the mission, entire frontier and cumulative failures, actual cited evidence, strongest alternatives, and remaining resources before the coordinator states its preference. It challenges equivalence, coverage and decision value. Receipt shape does not prove review quality or independence.

### `direction`

Fields: `id`, `family`, `parent` as an existing direction ID or null, `claim`, `predictions`, `disconfirmers`, `rationale`, `scope` as charter scope links, and `state:"unexplored"`. IDs use letters, digits, underscores, and hyphens, at most 64 characters. A new root family requires an independent challenge and artifact. A child variant must inherit its parent's family. A new label without a different causal mechanism is a variant even if a reviewer accepts the label.

### `assign`

Fields: unique `id`, existing `direction`, `action`, positive `seconds`, nonnegative `trials`, and text `question`, `evidence_needed`, `stop`, `decision_change`, `alternative`, `diagnostic`, `synthesis`, `rationale`, `reversal`. Actions are `deepen`, `refine`, `expand`, `pivot`, `diagnose`, `replicate`, or `synthesize`.

Only one assignment can be active. Its time cap begins at commit, and its trial cap bounds actual permanent reservations. Work must fit before the deadline and protected reserve. Synthesis and replication can use the reserve. No new assignment or slot is allowed beyond its ceiling. At the next safe boundary `view` reports overruns; the helper cannot preempt a running host job. Closing and final accounting remain allowed after expiry.

Compare alternatives concretely. For each feasible observation, name the uncertainty or decision it changes, known evidence, cost, feasibility, deferred alternatives, and reversal conditions. There is no weighted truth score or mandatory idea count. Deepen when a live discriminator can change interpretation; refine when a diagnosed confound changes the test; pivot when alternatives offer more value; synthesize when adequacy is met or useful tests exceed resources.

A due review blocks another routine narrow assignment. One fresh exact-head challenge can authorize a single assignment using `depth_exception` with positive `seconds`, nonnegative `trials`, `discriminator`, `neglected_value`, and `reversal`. The assignment must fit those caps. Renewal requires fresh reviewed material evidence, named by its `material_basis` SHA, distinct from the new review artifact and all evidence used by earlier depth exceptions. New bytes alone do not establish materiality; the reviewer must judge the actual observation. Reworded prose, renamed variants, and copied rationale cannot justify renewal.

After repeated execution failures in a family, allow one bounded `diagnose` assignment. Further diagnoses or repairs require `repair_basis` naming a fresh cited SHA, distinct from review artifacts and evidence used by previous assignments in that family. Variants share this failure history. The coordinator and reviewer must verify that the new artifact actually diagnoses a changed repair; changed bytes alone are insufficient. Prefer another useful direction when repair has low value.

### `close`

Fields: current `assignment`, `execution` as `completed`, `failed`, or `abandoned`, `outcome` as `supported`, `negative`, `inconclusive`, or `not_evaluated`, `summary`, `next`, boolean `information_gain` and `material`, nonnegative integer `active_minutes`, and nonempty `evidence`. Failed or abandoned execution requires `failure_signature` and `not_evaluated`. It is never a negative experiment.

Supported or negative claims require registered child trials with matching outcomes and all original scientific gates clear. Other closures preserve limitations and cannot promote an incomplete study. A valid negative result can change coverage and retire a mechanism. Work completed successfully without resolving uncertainty may still have no information gain. Cite actual sealed study evidence and private analysis, then inspect the child study before relying on it.

### `frontier`

Fields: `direction`, `state` as `unexplored`, `active`, `parked`, `retired`, or `replication_candidate`, `rationale`, `reopen`, `reversal`, and optional `coverage` as charter scope links with `coverage_status` as `unknown`, `unsupported`, `contested`, or `resolved`. Coverage requires evidence distinct from the review artifact. Coverage and due checkpoints require a fresh independent review. Park on a recoverable constraint; retire on valid disconfirmation, infeasibility, or low remaining decision value. Preserve uncertainty and material reopen conditions.

A due checkpoint names `selected_direction`, an existing alternative for the next assignment. After same-family or no-information repetition it must select a different family. Another same-family commitment instead uses the bounded depth exception on `assign`. The next routine assignment must follow the reviewed choice. Synthesis or replication remains available. One blocked direction does not gate an unrelated useful route.

### `terminal`

Fields: `status`, `rationale`, `unresolved`, `next`. Status is `complete`, `budget_exhausted`, `externally_blocked`, or `host_needs_continuation`. Close active work first. `complete` needs every original scope cell explicitly adjudicated as resolved or unsupported, a nonempty `completion_assessment` against the frozen completion question, cited synthesis evidence distinct from the review artifact, and a fresh independent adequacy challenge. Unknown or contested original scope blocks completion. `externally_blocked` also requires `unblock` and `routes_considered` explaining why no useful authorized route remains. A later reviewed `frontier` proposal with `unblock_basis` can reopen an externally blocked campaign when concrete evidence or authorization changes feasibility. Its original deadline and charges remain frozen. `host_needs_continuation` records a handoff while leaving the ledger open for the same campaign's next host turn. Budget exhaustion requires the actual wall or global trial ceiling, or `resource_exhaustion` describing a different authorized resource boundary with cited evidence and a fresh independent review. An arbitrary status string cannot end a still-useful campaign as exhausted. Budget exhaustion is not mission completion. Final reporting is bounded accounting, not additional unreserved research.

## Trial accounting and interrupted registration

Call `trial` before direct child registration. Child identity is frozen as `studies/STUDY_ID`, obtained from the unchanged TrialPlan schema. The controller reserves one global slot and freezes the exact plan before calling `evidence.register`; charges are never released, including failed, abandoned, unexecuted, and interrupted work. A per-study budget cannot reset the campaign ceiling.

After interruption, `view` lists pending reservations. Retry `trial` with the same assignment and the frozen `plans/STUDY--TRIAL/plan.json`, even after expiry. Recovery completes that existing registration without a new slot or additional research permission. Registration may already exist when the process failed before the completion event; an identical retry recognizes it. Conflicting plans fail. Never substitute a fresh trial ID to recover.

Unreserved child trials and unexplained study roots block spending. Explicitly call `trial` with the exact existing plan and active assignment to charge a discovered unreserved registration, provided current caps permit it; unrelated discrepancies continue to block. If caps cannot absorb it, preserve the discrepancy and stop research for accounting. Do not delete a trial to regain capacity. This controls compliant plugin use, not arbitrary filesystem editing.

## Resume and report

Run `view` from canonical state, inspect all referenced child evidence, reconcile pending registrations, and honor its next action before dispatch. The packet includes original charter, frontier, all assignments and failures, exact head, cumulative charges, study inspections, due review, clock and overrun flags, and staging. Preserve source artifact paths when moving context; never trust only old coordinator prose.

Report original scope and coverage with uncertainty, mechanisms and variants, all attempts including execution failures, parked and retired directions with reopen conditions, cumulative wall and trial accounting, unresolved reviewers, and the exact terminal or handoff reason. A twenty-hour accelerated trace proves state transitions, not twenty-hour host reliability, market findings, or model judgment. The [educational simulation](../../../examples/campaign/run.py) uses only fixture evidence and a simulated internal clock. Actual campaigns leave absent independent reviews blocked.

## Role assignments

Give each role only its bounded assignment, actual source refs, remaining caps, and private output path. Use the existing pstack model and effort configuration rather than hardcoded slugs. Preserve separate independent sessions for repeated configured scientific seats.

- Coordinator: Recover the exact ledger head and original mission. Compare the best feasible alternative, diagnostic, and synthesis before proposing one falsifiable bounded assignment. Keep cumulative failures and neglected original scope visible. Import reviewed private artifacts, allocate global slots, and commit state alone.
- Research worker: Answer the specified discriminator within the assignment's resource, time, and trial caps. Preserve unsuccessful attempts, exact data and code fingerprints, and stop conditions. Request trial registration from the coordinator before implementation. Write private outputs and propose a closure; never edit campaign state or accept your own evidence.
- Independent priority challenger: Read the original charter, exact current head, frontier, cumulative family history, and actual cited evidence before seeing the coordinator preference. Challenge family equivalence and scope adequacy. Compare feasible alternatives qualitatively. Recommend a different direction, a bounded live-discriminator depth exception, diagnosis, or synthesis, with reversal conditions. Renew depth only on materially new observations, not revised prose. State missing evidence or blocked review honestly.
- Synthesizer: Inspect every child study and all campaign attempts. Adjudicate each original scope dimension using real evidence and independent challenge. Distinguish scientific outcomes from execution failure, budget exhaustion from completion, and durable recovery from host uptime. Preserve open uncertainties and exact next actions. Do not invent reviews or results to fill the report.

# Evidence helper reference

`tools/evidence.py` requires Python 3.11 or later and the standard library. It never executes a command from a plan or output bundle. It reads compact evidence bundles into memory. Reference large or restricted datasets by provenance and fingerprint rather than copying them into the bundle.

## Public commands

```sh
python3 <plugin-root>/tools/evidence.py register RUN --plan PLAN.json
python3 <plugin-root>/tools/evidence.py snapshot RUN --trial t001 --source OUTPUT
python3 <plugin-root>/tools/evidence.py inspect RUN
python3 <plugin-root>/tools/evidence.py inspect RUN --json
```

`register` freezes the canonical plan and a registration digest. The first registration freezes the shared study. An advisory process lock serializes registration so concurrent cooperating commands cannot exceed its budget. Failed, abandoned, and unexecuted registrations remain counted. Identical retries succeed, including after a snapshot. A changed plan, study, budget, or sealed output conflicts. The helper does not detect trial-family resets in another run directory.

`snapshot` seals the source directory into `trials/<id>/snapshot/`. It includes canonical metadata and the byte hashes and sizes of all source files. Paths must be safe relative paths. Symlinks inside a dossier or source tree, absolute artifact paths, traversal, and special files are rejected. Normal aliases in a host parent path, such as macOS `/tmp`, are canonicalized. The selected run and source roots themselves cannot be symlinks. Sources cannot overlap the destination snapshot.

Publication uses a staged sibling directory and exclusive directory rename. Existing identical publications are idempotent. Conflicting retries fail. Interrupted `.pending-*` staging directories are ignored as incomplete and reported by inspection. They are never accepted trials. This is process-crash recovery, not a guarantee against power loss or malicious filesystem races. Keep one coordinator owner and do not edit published artifacts.

`inspect` validates stored registrations, snapshot inventories, hashes, explicit outcome evidence, and declared reviews. It derives status without executing research. Missing snapshots or required reviews are incomplete. A corrupt file, stale review, unsafe path, overlapping declared reviewer, or malformed artifact is invalid. It returns all trial outcomes and gate blockers in JSON or text.

| Exit code | Meaning |
| --- | --- |
| 0 | Register or snapshot succeeded, or inspection found complete development evidence with declared accepted reviews |
| 1 | Inspection found valid but incomplete or blocked evidence |
| 2 | Invalid input, corrupt evidence, conflict, or filesystem error |

An exit code of zero does not authenticate reviewers, establish statistical validity, verify actual ordering, or approve trading. `process_integrity: valid` means the checks above passed. The supported automated scope is development evidence. Exposed or unknown holdout access remains blocked even if a separate procedural event exists.

## Storage

```text
RUN/
  study/spec.json
  trials/t001/plan.json
  trials/t001/registration.json
  trials/t001/snapshot/snapshot.json
  trials/t001/snapshot/files/...
  reviews/<unique-receipt>/review.json
  work/<unique-session>/...
  decisions/<ordered-id>/decision.json
  holdout/event.json                  optional procedural record
  report.md                          rebuildable coordinator report
```

Registration and snapshot publication are write-once operations enforced by the helper for cooperating callers. Reviews and decisions are coordinator-published, append-only receipts by convention. Inspection checks them but does not authenticate or cryptographically prevent their replacement. The report is a derived file. Private work and draft plans are not accepted evidence until sealed.

## TrialPlan and study

The plan is a JSON object. Extra descriptive metadata is allowed. The [synthetic generator](../../../examples/synthetic/run.py) supplies an executable, complete example in `make_plan`. Its runner supports that fixed design only and rejects changed splits, estimator, costs, tests, availability rule, or study protocol.

| Field | Required content |
| --- | --- |
| `schema`, `id` | Version `1`, safe trial ID |
| `study` | Frozen study object below |
| `authors` | Nonempty unique declared author IDs |
| `hypothesis`, `availability_rule`, `stopping_rule` | Nonempty descriptions |
| `inputs` | Nonempty list of input records |
| `universe`, `splits`, `estimator`, `costs`, `tests`, `reproduction` | Nonempty objects with study-specific methods and applicability rationale |

The study requires `id`, `question`, `budget`, `protocol`, and `review_seats`. The budget has positive integer `max_trials` and `active_minutes`. The protocol has nonempty `trial_family`, `decision_rule`, and `holdout_policy`. A seat has a unique safe `id`, role `methodology`, `execution-risk`, or `reproduction`, and stage `preregistration` or `result`. Reproduction is a result role. At least one preregistration methodology seat and all three result roles are required. Add every configured panel seat before registration.

Each input requires safe `id`, `status`, and nonempty `provenance`. `present` requires a SHA-256 fingerprint. `missing` and `unavailable` require a reason and block dependent research disposition. The helper checks that a snapshot repeats present-input fingerprints. It cannot verify that the execution actually used those inputs.

Registration is exactly `schema`, `trial_id`, `plan_sha256`, and `study_sha256`. Hashes use UTF-8 JSON with sorted keys, two-space indentation, no nonfinite numbers, and a final newline. Snapshot and review subject hashes refer to those canonical bytes. The helper prints the registration and snapshot metadata after publication, so callers can retain exact hashes without guessing a serializer.

## Execution and Snapshot

The source bundle must contain `execution.json` and every path named in its `outcome_evidence`. Include metrics or diagnostic logs, code, and compact supporting outputs. A registration alone is not an execution result.

| Execution field | Required content |
| --- | --- |
| `schema`, `trial_id`, `authors` | Version `1`, registered trial, nonempty unique author IDs |
| `command` | Actual command as a nonempty argument list |
| `environment`, `seeds` | Nonempty objects; state explicit non-applicability when deterministic without RNG |
| `source_revision` | Source revision or content-hash description, even outside Git |
| `data_fingerprints` | Map of input IDs to SHA-256 hashes matching every registered present input |
| `limitations` | Nonempty list of disclosed limits |
| `execution_status` | `completed`, `failed`, or `abandoned` |
| `outcome` | `supported`, `negative`, `inconclusive`, or `not_evaluated` |
| `holdout_access` | `unopened`, `exposed`, or `unknown` |
| `outcome_evidence` | Nonempty list of safe relative paths that exist in the bundle |

Failed and abandoned executions require `not_evaluated`. A completed execution with no scientific finding can also use `not_evaluated` and remains blocked. Financial outcome is author-declared and must be judged by independent reviewers.

Snapshot stores `schema`, `trial_id`, `registration_sha256`, `plan_sha256`, parsed `execution`, and `files`. Each file entry has `path`, `sha256`, and byte count `bytes`. Inspection rejects missing, altered, extra, or duplicate artifacts and mismatched sealed execution metadata.

## Review receipts

A reviewer writes the receipt to its private output directory. The coordinator verifies it and publishes the entire receipt directory under a fresh `reviews/<id>` using exclusive creation or a staged nonempty-directory rename. Never open an existing receipt for overwrite. Corrections that change the assessed plan or result need a new trial, not a revised old approval.

```json
{
  "schema": 1,
  "id": "receipt-pre-1",
  "trial_id": "t001",
  "seat_id": "pre-method-1",
  "reviewer_id": "actual-independent-session-id",
  "role": "methodology",
  "stage": "preregistration",
  "registration_sha256": "<canonical registration SHA-256>",
  "snapshot_sha256": null,
  "verdict": "blocked",
  "findings": ["Describe observed evidence and unresolved findings."],
  "evidence": ["Name the exact evidence inspected and observed checks."]
}
```

The angle-bracket hash above is notation, not an executable fixture. Use the trial's `registration_sha256` and `snapshot_sha256` from `inspect --json`. Result receipts require both exact hashes. Preregistration receipts require a null snapshot hash. Verdicts are `accept`, `revise`, or `blocked`. Findings and evidence are nonempty text lists. Review evidence entries are descriptive text that `inspect` does not resolve as file paths; actual review quality and truth remain procedural. The helper requires the declared role and stage to match the seat. It rejects author overlap, reviewer reuse across seats, duplicate seat receipts, and stale bindings. It does not determine whether evidence statements are truthful or sufficient.

## Decision receipts and report

A decision object requires `schema: 1`, `id` matching its directory, `action` of `continue`, `narrow`, or `stop`, nonempty `reason` and `next`, nonempty `evidence` containing existing run-relative file paths, nonnegative integer `active_minutes`, `units`, and `failed_attempts`, and `independent_priority_reviewer` containing the real reviewer ID or null. Use ordered IDs such as `d001`. Counters record state since the previous checkpoint. Missing decision receipts do not pass scientific gates or automatically fail them. The workflow requires them for bounded work and resumption. Inspection exposes validated receipts as `priority_receipts`.

The report contract is defined in [contracts](contracts.md). Report all trials even when inspection exits with code 1 or 2. Do not reinterpret invalid evidence as a negative finding.

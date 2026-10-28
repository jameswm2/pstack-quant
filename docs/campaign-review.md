# Independent campaign review

The review assessed long research campaigns inside an existing host session. It kept campaign accounting, scientific judgment, and host liveness separate.

## Independent panel

Three separate reviewers assessed the campaign implementation at `910448f` against the merged baseline `39669e5`.

| Reviewer | Model | Scope |
| --- | --- | --- |
| A | `gpt-6.1-sol` | Complete changed scope and targeted recovery checks |
| B | `gpt-6.1-sol` | Complete changed scope and targeted identity and registration checks |
| C | `gpt-6-luna` | Complete changed scope and targeted blockage and continuation checks |

The repeated Sol entries were independent agents. Scope included the controller, shared research instructions, host adapters, examples, tests, package checks, manifests, CI, and documentation.

## Accepted findings

Reviewers reproduced legal operations that could invalidate replay or obstruct unrelated work. Regression commits precede their repair in `ebbe17a`.

| Finding | Repair |
| --- | --- |
| Public operation keys could collide with internal keys | Disjoint namespaces and duplicate checks before publication |
| Closing a nonexistent assignment could publish an unreadable record | Candidate state is validated before immutable publication |
| Incompatible child plans could consume a slot and leave an impossible pending registration | Child compatibility is checked before freezing or charging |
| Different study and trial pairs could share a concatenated reservation ID | Reservation identity hashes the canonical ordered pair |
| External blockage could reopen on prose alone, while the resume hint hid that route | Reopening requires cited changed-feasibility evidence and a fresh review; the hint exposes the conditional action |

Registration settlement also received explicit coverage. An evidence-bound `abandon_registration` proposal can settle a pending reservation only when no child trial exists. It retains the charge and frozen plan, permits unrelated work, and cannot hide a registered child or revive the settled reservation.

A fresh independent `gpt-6.1-sol` reviewer assessed `ebbe17a` against the reviewed head. It ran 14 targeted checks covering rejected writes, key namespaces, tuple identities, child preflight, both registration interruption windows, settlement, permanent charges, registered-data protection, unrelated continuation, and evidence-bound reopening. All passed with no further findings. The coordinator also reran the full 57-test suite and production example. Comments audits removed four narrative lines and found no added comments requiring removal in the fix.

## Research instruction scenarios

Each original panel reviewer separately received the same four raw synthetic situations and the packaged instructions. Expected answers and other reviewers' reports were withheld. The coordinator inspected all 12 resulting assessments.

| Situation | Observed response across the three assessments |
| --- | --- |
| Repeated thresholds with diminishing information | Kept variants in one mechanism family and proposed a bounded challenge, pivot, or shared-prerequisite diagnostic |
| A live discriminator needing deeper investigation | Allowed one capped timing investigation with fresh review, evidence requirements, and a reversal condition |
| A promising three-hour idea with two hours remaining | Preserved the original deadline and protected reserves, deferring infeasible new research |
| Broad coverage claimed from three lookbacks | Rejected superficial breadth and premature completion, preserving unresolved coverage questions |

These assessments test instruction behavior in the available Codex agent environment. They do not establish behavior under every model, native Claude execution, actual twenty-hour uptime, or scientific validity. Fixture notes and educational receipts remain labelled. The [verification record](verification.md) lists reproducible checks and remaining limits.

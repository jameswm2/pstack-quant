# Independent implementation review

The review assessed whether this plugin adapts pstack orchestration to bounded quantitative research while keeping local evidence integrity, scientific judgment, and host capabilities distinct.

## Independent panel

Three separate reviewers assessed the complete implementation at `e88f0f91bb367058797a0b0faa74c58091228090`:

| Reviewer | Model | Findings |
| --- | --- | --- |
| A | `gpt-6.1-sol` | Interrupted review and decision staging invalidated otherwise valid evidence |
| B | `gpt-6.1-sol` | Independently reproduced the same staging defect |
| C | `gpt-6-luna` | Review evidence statements are not resolved as artifact paths |

The repeated Sol entries were independent agents. The review scope included the helper, example, tests, package and CI checks, shared instructions, focused skills, manifests, marketplaces, documentation, and licenses. Reviewers ran targeted checks rather than repeating the coordinator's suite.

## Findings and decisions

The staging defect was accepted and repaired in `9c3f1e8acc5bae6103ab0682090f8ca811665e9b`. Inspection now ignores only actual `.pending-*` review and decision directories after path checks, while keeping their warning visible. Regression-first tests reproduced exit `2` with `unsafe or invalid identifier` before the fix. Both incomplete and complete fixture states now retain their original result. Malformed committed receipts, pending files, unsafe links, and stale review bindings remain rejected.

Reviewer C's observation is a documented limitation under the existing schema. Review `evidence` is a list of descriptive statements. Mandatory registration and snapshot digest fields bind the actual subject. Those statements do not prove artifact existence, reviewer work, identity, or scientific validity. The reference now says this explicitly. A new file-and-digest receipt schema was deferred because it would change the interface without authenticating review quality.

A fresh independent `gpt-6.1-sol` reviewer verified the staging fix through the public CLI at `9c3f1e8`. It checked both receipt collections, complete and incomplete states, text and JSON warnings, pending files and symlinks, malformed or missing published receipts, descriptive review evidence, and stale subject bindings. It reported no findings. The specific fix gate is satisfied.

The initial comments audit removed four narrative comment or docstring lines. It retained CLI help docstrings, executable directives, and license notices. The fix audit found no added comments or suppressions. Neither audit required application behavior changes or constraint encodings.

## Realistic instruction test

Each panel reviewer separately used the packaged research instructions on the same raw synthetic study metadata. No expected answer or prior reviewer conclusion was supplied. The metadata described selected performance claims, missing unsuccessful trials, uncertain data provenance, a feature-availability and fill-timing conflict, latest constituents reused historically, zero costs, an author-supplied review, no reproducible command, and a previously read holdout followed by feature changes.

All three reports blocked confirmation and proposed bounded evidence recovery. They treated reported metrics as unverified claims, named timing and selection gaps, recognized contaminated evaluation data and self-review, and preserved missing reproduction. They did not invent observations, review receipts, statistical adjustments, or an exact trial count from ambiguous variant counts.

This exercise demonstrates behavior of the instructions in the available Codex agent environment. It does not establish behavior under every model, native Claude execution, market validity, or host parity. Host and delivery limits remain in the [verification record](verification.md).

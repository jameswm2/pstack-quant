# Shared research contracts

This is the single source for lifecycle and role gates. Focused skills and host adapters refer here.

## Ownership and assignments

One coordinator owns the question, scope, budget, study protocol, trial IDs, assignments, integration, decision receipts, and final claims. It dispatches specialists into separate `RUN/work/<session-id>/` directories. Each assignment names the research question, immutable inputs and their hashes, exact output directory, permitted writes, required deliverable, stopping rule, and gate it serves. Readers receive the relevant source evidence, not another worker's verdict as a substitute.

Specialists do not write each other's files or the shared dossier. The coordinator verifies outputs before exclusive publication. Use fresh independent sessions for required review seats. A panel with repeated model entries still requires a different agent for each entry. Capacity limits permit sequential independent dispatch. They do not permit fewer seats or coordinator self-review.

| Role | Deliverable | Ownership limit |
| --- | --- | --- |
| Hypothesis author | Falsifiable mechanism, alternatives, unit of analysis, baseline, possible disconfirmation | Does not approve its own hypothesis |
| Data auditor | Provenance, timestamp semantics, availability lags, revisions, missingness, point-in-time eligibility | Unavailable data blocks dependent claims |
| Experiment designer | TrialPlan, trial family, split and uncertainty rationale, outcome rule, stopping rule | Counts all variants, including abandoned attempts |
| Implementer | Research code, complete command, environment, seeds, data hashes, explicit outcome and limits | Executes the registered design in a private directory |
| Methodology reviewer | Independent preregistration challenge or result falsification | Cannot be an author or occupy another required seat |
| Execution-risk reviewer | Applicability and critique of costs, timing, fills, turnover, liquidity, capacity, and model use | Cannot be an author or occupy another required seat |
| Reproducer | Fresh-directory observed rerun, artifact comparison, unresolved differences | Cannot be an author or occupy another required seat |
| Coordinator and reporter | Integrated dossier, all attempts, decision receipts, evidence-linked report | Owns integration, never substitutes for an independent verdict |

For questions without trading decisions, execution-risk review covers downstream model use, operational assumptions, and applicability. Explain why fills, corporate actions, or other market-specific checks do not apply. Do not force a directional strategy into a forecasting or risk question.

## Lifecycle and gates

1. Freeze a brief with the question, mechanism, alternatives, available data, applicability decisions, research budget, and evaluation regime.
2. Audit feasibility and temporal provenance. Name missing or unavailable inputs with reasons. Do not infer a clean audit from absent data.
3. Freeze a study protocol and TrialPlan with `register`. The first registration freezes study budget, trial family, decision rule, holdout policy, and required review seats. New IDs consume the same study budget. A rejected, failed, abandoned, or unexecuted registered trial remains counted.
4. Dispatch every required preregistration seat against the registration hash. Require accepted independent methodology review before a real experiment. A rejected design requires a new trial ID. Never backdate a review. Earlier execution can remain partial exploratory evidence, with authorization visibly unresolved.
5. Execute only the registered scope. Seal the full output bundle with `snapshot`, including failed or abandoned attempts and their diagnostic evidence. A failed process is `not_evaluated`, never a negative financial finding.
6. Dispatch every result seat against the exact registration and snapshot hashes. Require independent methodology, execution-risk, and reproduction sessions. Each required seat has a unique reviewer ID distinct from all plan and execution authors. Preserve any larger configured panel. Register its separate seats before execution.
7. Run `inspect`, resolve integrity failures, and report the complete trial family. `supported`, `negative`, and `inconclusive` describe a financial finding. `blocked` describes unresolved gates. A valid process does not establish a useful model, market alpha, or deployment readiness.

The helper mechanically verifies hashes, budgets within a run, paths, declared identities, required fields, and review bindings. Agents judge scientific adequacy. Review acceptance is a declared receipt, not authenticated identity or proof of temporal ordering. New run directories can evade family accounting. The coordinator must keep all related attempts in one study and disclose outside exploration.

## Holdout discipline

Default to development data only. Reserve the holdout period before tuning, identify its custodian, and keep its location out of worker inputs where feasible. Registration is an audit convention, not an operating-system access boundary.

A one-time holdout event requires frozen protocol and accepted independent preregistration and development-result gates. Before access, exclusively publish `RUN/holdout/event.json` with the study and trial IDs, registration and development snapshot hashes, exact accepted review hashes, actor, recorded time, reason, and evaluation regime. Name the intended one-time command and output directory. Keep the event with the report. Record unexpected exposure immediately, even if it violates the protocol.

After exposure, preserve the original evaluation regime and result. Any data, code, or plan changes need a fresh untouched evaluation regime or an explicit exploratory and contaminated label. Never relabel a reused holdout as untouched.

Version 0.1 supports development evidence only. `inspect` conservatively blocks any snapshot declaring `exposed` or `unknown` holdout access, even with a procedural event. It does not authorize confirmation or certify event chronology. The example provides no holdout mode and never generates holdout rows.

## Priority and resumption

Keep bounded decision receipts under `RUN/decisions/<id>/decision.json`, with one writer per fresh directory. Each receipt records continue, narrow, or stop, the reason, evidence paths, active minutes, completed units, failed attempts, the next action, and the independent priority reviewer or explicit absence. The latest receipt and counters are the saved priority state. Use ordered IDs and preserve earlier receipts.

Reassess at 30 active minutes, three completed units, two failed attempts, material new evidence, or the user's request. The research budget can stop work sooner. Use the host's priority-review extension and independent reviewer when available or required. Do not count a priority review as a scientific review. An unavailable reviewer remains named as absent.

Before resuming or assigning the next dependent unit, read the latest receipt and run `inspect`. Treat invalid artifacts as unusable until resolved from original evidence. Preserve old, failed, and rejected attempts. Reassign an unfinished experiment only after checking its private outputs and avoiding concurrent writers. A pending staging directory is not an accepted trial or snapshot.

## Report contract

A report includes the research question and evaluation regime, data provenance and gaps, every registered trial, failed and abandoned attempts, outside exploration disclosed by the user, financial results, uncertainty, independent review seats and missing verdicts, holdout exposure, and evidence paths. State process integrity and financial outcome separately. Explain assumptions that limit interpretation and what evidence could change the conclusion. Do not claim statistical corrections were computed when they were only discussed. End with a bounded research decision, not trading instructions or deployment approval.

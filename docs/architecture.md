# Campaign decisions above immutable study evidence

Version 0.2 centers long research missions on a small campaign controller inside the existing host session. The selected architecture uses a frozen charter and immutable predecessor-bound decision records. The host coordinator owns actual dispatch and qualitative research choices. The unchanged study evidence helper remains the scientific authority.

## Why a ledger

Three independent architecture candidates compared a mutable campaign notebook, a scheduled phase program, and a decision ledger. The selected base was the bounded ledger design. A mutable latest-status document loses failed and rejected decisions unless a second archive becomes authoritative. A fixed phase schedule wastes budget on missions whose useful tests have unequal costs. Replay from the charter, records, and cited evidence preserves the original mission and cumulative accounting without a scheduler or database.

The synthesis adds an exact-head independent challenge and a single bounded depth exception whose renewal needs fresh material evidence. It also preserves the existing supported, negative, inconclusive, and not_evaluated outcome vocabulary. Execution failure remains distinct from a negative scientific finding.

## Domain and boundaries

`tools/campaign.py` owns the charter, tagged direction, assignment, closure, frontier, terminal, reservation, and registration records. It derives the frontier, coverage, cumulative failures, resource remainder, current assignment, due reviews, study inspections, and concrete next action. Its public verbs are start, view, commit, and trial. The [campaign reference](../skills/quant-campaign/references/campaign.md) owns schemas and decision instructions.

The coordinator chooses among feasible mechanisms, diagnostics, replication, and synthesis. Independent challenge judges actual family novelty, information gain, coverage, materiality, and adequacy. Mechanical checks bind declared reviews to the exact prior head and real immutable artifacts; they cannot authenticate identity or semantic quality. Parameter variants inherit their family, and family-scoped failure history survives direction renaming. After repeated failures, one bounded diagnostic detour is allowed; further repair needs a fresh non-review artifact basis and qualitative justification.

Repeated narrow or no-information work gates routine continuation. Early checkpoints cannot erase the consecutive same-family work history. A reviewed frontier checkpoint binds its next alternative direction, and fixation triggers require a different family. A one-assignment depth exception instead names the live discriminator, cap, neglected alternatives, and reversal condition. New review prose cannot itself renew material evidence. No numeric score decides scientific truth.

The charter freezes actual UTC start and deadline, including host downtime. New spending cannot enter protected synthesis or replication reserves. Assignments have expiry, trial cap, and stop condition. The controller reports an overrun at a safe boundary; it cannot interrupt a host job. Active minutes are coordinator reports, not measured thinking time. Closing and final accounting remain possible after deadline. Clock regression blocks spending until UTC catches up, preserving the last observation rather than resetting it.

## Registration and recovery

Campaign trial allocation freezes the exact plan and charges a permanent global slot before invoking unchanged `evidence.register` at the stable child identity `studies/STUDY_ID`. A crash before registration or after registration but before its event leaves the same charged pending reservation. Retrying the frozen plan completes the existing charge even after expiry. It does not create a new trial or authorize new research.

Unreserved registrations and unexplained roots block spending. Explicit adoption through trial charges an exact discovered plan under the active assignment's existing caps. If capacity is insufficient, retain the discrepancy and stop for accounting. Changing study IDs cannot release prior campaign charges. This enforces compliant plugin behavior, not arbitrary direct filesystem edits.

A short advisory lock serializes cooperative campaign writes. Atomic staged directory publication, exact predecessor checks, and operation keys provide stale-write rejection and identical retry recovery. Source artifacts and reserved plans are verified on replay; an edited report cannot silently justify a new claim. Incomplete staging is reported. Publication does not promise power-loss durability, malicious tamper resistance, or authenticity of research.

## Host continuation and package

The primary quant-campaign skill routes long missions; bounded quant-research remains available. Resume and report recognize campaign roots before reading ordinary study dossiers. Codex and Claude adapters share policy and preserve existing model and effort configuration, including independent repeated seats. The helper never calls models, executes arbitrary commands, wakes the host, or launches replacement CLI sessions. Native continuation requires actual available tools and appropriate authorization. Durable state and host liveness are separate.

The accelerated example uses a clearly simulated internal clock and explicitly educational priority receipts. Original study scientific reviews remain missing and blocked. Tests cover actual CLI and files, concurrent expected-head writes, deadline and reserve accounting, crash recovery, family inheritance, fixation, diagnostic bounds, and evidence corruption. They do not establish twenty-hour uptime or profitable research. Package checking discovers the new skill and campaign artifacts; both manifests are version 0.2.0.

## Preserved study authority

## Responsibility boundaries

The root `skills/` tree is shared by Codex and Claude Code. Thin focused entries route to one contracts reference. Role prompts describe research work, and host adapters map dispatch and model configuration to actual available capabilities. Platform manifests share identity and version, checked by `tools/check_package.py`.

The coordinator owns the study, budgets, trial IDs, private output paths, publication, priority state, and final claims. Specialists author bounded outputs. Independent reviewers inspect source evidence in separate sessions. Repeated model entries remain separate seats. A missing reviewer leaves its gate blocked.

`tools/evidence.py` parses JSON at the boundary into TrialPlan, Registration, Snapshot, and Review records. It freezes the shared study and per-trial registration, publishes sealed output bundles, verifies file digests and declared review bindings, and derives research disposition. It never invokes research commands or judges a model's financial usefulness.

The helper proves consistency of the stored evidence for cooperating callers. It does not authenticate real-world identities, actual execution order, input truth, a reviewer's work, statistical validity, or holdout isolation. Manual review and decision receipts remain append-only coordinator conventions. Published directories are not protected against an actor that can rewrite all files and recompute hashes.

## Publication and recovery

Registration holds a process advisory lock around study and trial publication to prevent a budget race among cooperating CLI calls. The lock releases when the process exits. Each trial and snapshot publishes from a staged nonempty sibling directory. Identical retries succeed and conflicting retries fail. An interrupted `.pending-*` directory is incomplete evidence and is reported rather than counted.

Only registration needs the shared budget lock. Snapshots and reviewer outputs have separate directories. No shared append log or mutable lifecycle-status field exists. The report is rebuildable. Atomic publication handles process interruption but does not promise durability across power loss or protection against malicious filesystem races.

Paths are checked for traversal, unsafe artifact names, special files, and symlinks within evidence trees. Host parent aliases are canonicalized before establishing run or source roots. The implementation reads evidence bundles into memory. Large or restricted raw market data belongs outside the bundle with precise provenance and fingerprints.

## Scientific states

A registration consumes a trial even if execution fails, is abandoned, or never starts. The budget and protocol are frozen per run, so changing IDs cannot reset the family counter within that run. Individual standalone studies retain local accounting; campaigns additionally reserve every child trial globally.

Financial outcomes are declared as supported, negative, inconclusive, or not evaluated. Process integrity and independent review are separate. Missing evidence does not become a negative result. An accepted review must match the registered seat and exact registration or snapshot. Declared reviewers must differ from all authors and other seats. Actual independence and ordering remain procedural.

The study helper automates development-dossier inspection. It conservatively blocks exposed or unknown holdout access. A one-time holdout event can be documented under the shared protocol, but confirmatory holdout assessment remains a separate human or agent research decision. There is no automated confirmation-approval command. Any post-exposure modification needs a fresh evaluation regime or a contaminated exploratory label.

## Verification boundaries

The deterministic synthetic example has one fixed model, realistic declared availability lag, temporal separation, a zero-position baseline, explicit costs, a negative leakage control, and disclosed uncertainty limits. It never generates or reads holdout rows and never fabricates reviews. Tests compare scientific artifacts across two fresh runs while allowing command paths to differ.

Local CLI tests establish evidence behavior. The package checker establishes file, link, provenance, and manifest consistency. Native host discovery establishes discoverability only. Claude's CI manifest validation establishes packaging only. None of these proves research behavior by agents or parity between host runtimes.

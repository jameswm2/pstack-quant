# Evidence dossiers and shared research instructions

pstack-quant specializes pstack orchestration for bounded, asset-agnostic financial research. Its organizing unit is an immutable trial dossier. Research judgment stays in agents, while a small standard-library helper handles evidence integrity and trial accounting.

## Why this shape

An independent architecture comparison considered a full executable workflow service, a prompt-only research guide, and dossiers with a narrow helper. The dossier design was selected because it protects reproducibility and retry behavior without introducing a database, scheduler, agent SDK, or backtesting engine.

The synthesis adds development-only default execution, exact review bindings, explicit decision receipts, one coordinator owner, and derived lifecycle status. The helper's three public verbs are `register`, `snapshot`, and `inspect`. No hook, MCP server, external data source, or API key is required for the offline example.

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

A registration consumes a trial even if execution fails, is abandoned, or never starts. The budget and protocol are frozen per run, so changing IDs cannot reset the family counter within that run. Moving to a new run can evade that counter and remains a coordinator responsibility.

Financial outcomes are declared as supported, negative, inconclusive, or not evaluated. Process integrity and independent review are separate. Missing evidence does not become a negative result. An accepted review must match the registered seat and exact registration or snapshot. Declared reviewers must differ from all authors and other seats. Actual independence and ordering remain procedural.

Version 0.1 automates development-dossier inspection. It conservatively blocks exposed or unknown holdout access. A one-time holdout event can be documented under the shared protocol, but confirmatory holdout assessment remains a separate human or agent research decision. There is no automated confirmation-approval command. Any post-exposure modification needs a fresh evaluation regime or a contaminated exploratory label.

## Verification boundaries

The deterministic synthetic example has one fixed model, realistic declared availability lag, temporal separation, a zero-position baseline, explicit costs, a negative leakage control, and disclosed uncertainty limits. It never generates or reads holdout rows and never fabricates reviews. Tests compare scientific artifacts across two fresh runs while allowing command paths to differ.

Local CLI tests establish evidence behavior. The package checker establishes file, link, provenance, and manifest consistency. Native host discovery establishes discoverability only. Claude's CI manifest validation establishes packaging only. None of these proves research behavior by agents or parity between host runtimes.

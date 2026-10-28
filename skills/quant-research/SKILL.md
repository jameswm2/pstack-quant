---
name: quant-research
description: Coordinate bounded, asset-agnostic quantitative financial research with preregistered trials, point-in-time data checks, independent challenges, reproducible evidence, and honest negative results. Use for quantitative research, not live trading or deployment.
---

# Quantitative research

Turn the user's question into a bounded research dossier. Accommodate forecasting, event studies, factor research, risk models, portfolio analysis, and strategy experiments. Choose methods for the question and available data. Never promise alpha.

Resolve the plugin root from this file as `../..`. Resolve all bundled files from that root, even after installation outside a Git checkout. Keep research output in a user-authorized workspace, outside the installed plugin.

Read [contracts](references/contracts.md) before coordinating any phase. It owns assignments, gates, budget accounting, holdout policy, priority checkpoints, and final claims. Read [methodology](references/methodology.md) when designing or judging research. Use the [role prompts](references/roles.md) to give each specialist a bounded assignment.

Read only the adapter for the current host, [Codex](references/codex.md) or [Claude Code](references/claude.md). Discover actual runtime capabilities before dispatch. Preserve configured independent panel seats. When a required reviewer cannot run, keep `BLOCKED: independent review` visible and continue useful work that does not depend on the gate. Never replace a reviewer with coordinator self-approval.

Choose the phase from the request and existing evidence. For a new study, establish the brief and budget first. For existing work, run the packaged [evidence helper](../../tools/evidence.py) with `inspect` before reusing results. Read [evidence schemas](references/evidence.md) when producing plans, snapshots, reviews, or decision receipts. The helper checks integrity and completeness, not financial validity or reviewer authenticity.

Route focused requests through the same contracts. `quant-design` scopes the hypothesis and experiment. `quant-data-audit` examines temporal provenance. `quant-experiment` implements a registered design. `quant-review` independently challenges evidence. `quant-report` explains the complete trial family. `quant-resume` verifies saved work before proposing another assignment.

A caller can ask:

- "Use quant-research to test whether publication-lagged regional indicators improve a fixed forecasting baseline. Budget three trials. Report revision and availability gaps."
- "Use quant-research to design an event study around filing timestamps. Audit point-in-time eligibility before estimating effects."
- "Use quant-research to compare covariance estimators for portfolio risk forecasts. Use development data only and preserve the final test period."

For an offline partial dossier, run `python3 <plugin-root>/examples/synthetic/run.py demo <new-run-directory>`. It deliberately generates no reviews and no holdout rows. A blocked review gate is the expected result.

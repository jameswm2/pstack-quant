# pstack-quant

Bounded, asset-agnostic quantitative financial research for Codex and Claude Code. Coordinate hypotheses, temporal data audits, preregistered experiments, independent challenges, reproduction, and reporting. Keep failed attempts and negative findings visible.

The plugin supplies shared skills and a Python evidence helper. It does not supply data, a backtesting engine, live trading, statistical validity, or deployment approval. Forecasting, event studies, factor research, risk models, portfolio analysis, and strategy experiments can all use the same dossier contract.

## Install and invoke

For Codex, add the repository marketplace and install the plugin:

```sh
codex plugin marketplace add jameswm2/pstack-quant
codex plugin add pstack-quant@pstack-quant
```

Invoke `$quant-research` directly or use normal domain-appropriate skill selection. For Claude Code, run these commands in its interactive session:

```text
/plugin marketplace add jameswm2/pstack-quant
/plugin install pstack-quant@pstack-quant
/pstack-quant:quant-research Design a bounded publication-lagged forecasting experiment.
```

For a local Claude packaging check, run `claude plugin validate .` from this repository. For a local session without marketplace installation, use `claude --plugin-dir /absolute/path/to/pstack-quant`.

The plugin has no session hooks and does not change user configuration. It uses the host's available dispatch tools and existing pstack model configuration. Required reviewers remain blocked when independent agents cannot run. Repeated configured model entries always mean separate sessions.

## Run the offline example

Python 3.11 or later is the only requirement. From a checkout, run:

```sh
python3 examples/synthetic/run.py demo /tmp/pstack-quant-demo
python3 tools/evidence.py inspect /tmp/pstack-quant-demo
```

The demo succeeds and writes a report, one frozen registration, a sealed output bundle, and a stop receipt. Inspection exits with code `1` and names four missing independent review seats. This is expected. The demo is partial development evidence and cannot retroactively satisfy preregistration authorization.

The example fits one fixed linear rule on training events and evaluates validation events against a zero-position baseline. It declares a lag between observation, availability, and decision, discloses turnover costs, and reports four block means with their limited uncertainty estimate. It generates no holdout rows and no reviewer receipts. Its outcome concerns synthetic development data, not market alpha.

Read `/tmp/pstack-quant-demo/report.md` for the evidence-linked report. Use a fresh directory for a second invocation. The exact command is recorded, so different run paths produce different execution metadata while scientific artifacts remain deterministic on the same Python version. An identical invocation into the same directory is idempotent.

The intentional future-information control fails with an assertion and a nonzero exit:

```sh
python3 examples/synthetic/run.py negative-control
```

## Use the research skills

The main skill owns end-to-end coordination. Focused skills narrow a research request without duplicating the lifecycle contract:

| Skill | Purpose |
| --- | --- |
| `quant-research` | Coordinate a bounded study |
| `quant-design` | Form a falsifiable question and draft TrialPlan |
| `quant-data-audit` | Audit point-in-time provenance and availability |
| `quant-experiment` | Implement a registered experiment and record outputs |
| `quant-review` | Independently challenge a design or result |
| `quant-report` | Explain all attempts and unresolved gates |
| `quant-resume` | Verify saved evidence and priority state before more work |

Example research requests include:

- "Use quant-research to test whether publication-lagged regional indicators improve a fixed forecast baseline. Budget three trials and preserve the final test period."
- "Use quant-design for an event study around filing timestamps. Audit eligibility and revision history before estimating an effect."
- "Use quant-research to compare covariance estimators for risk forecasts. Explain why trading fills do not apply and require independent reproduction."

See the [shared contracts](skills/quant-research/references/contracts.md), [methodology](skills/quant-research/references/methodology.md), [Codex adapter](skills/quant-research/references/codex.md), and [Claude adapter](skills/quant-research/references/claude.md).

## Inspect evidence

The public helper has three commands:

```sh
python3 tools/evidence.py register RUN --plan PLAN.json
python3 tools/evidence.py snapshot RUN --trial t001 --source OUTPUT
python3 tools/evidence.py inspect RUN --json
```

Registration freezes the plan and shared study budget. Snapshot seals a compact output bundle with code, command, environment, seeds, data fingerprints, limitations, explicit outcome, and outcome evidence. Inspection verifies stored hashes, completeness, trial accounting, and declared review bindings. It derives status without executing research code.

Exit codes are `0` for successful publication or complete development evidence, `1` for valid but incomplete or blocked inspection, and `2` for invalid or corrupt evidence. Negative and inconclusive findings are valid scientific outcomes. They remain separate from independent review status.

The helper checks declared identities, not actual reviewer authenticity or temporal ordering. It cannot prove data truth, statistical validity, or operating-system holdout isolation. A new run can evade family accounting, so related exploration must remain disclosed within the same study. Exposed or unknown holdout access always blocks automated inspection in this version. Confirmatory holdout assessment is a separate research decision, not an automated gate here.

Keep bundles compact because publication reads them into memory. Reference large or restricted source datasets through provenance and fingerprints. Review and decision receipts are published once by coordinator convention; the helper validates them but does not prevent a writer from replacing the whole dossier. Details are in the [evidence reference](skills/quant-research/references/evidence.md).

## Verify a checkout

```sh
python3 -m unittest discover -s tests -v
python3 tools/check_package.py
```

Tests exercise real CLI commands, budget races, retry conflicts, failed attempts, tampering, unsafe paths, review binding and declared independence, blocked holdouts, and repeatable offline outputs. CI runs stdlib checks on supported Python versions and separately runs the official Claude CLI's manifest validator. That validator does not execute models or research.

Native Codex marketplace discovery was verified with Codex `0.160.0` against a local packaging probe during development. Native discovery of this final plugin is checked separately during integration. Discovery does not establish installation or skill execution. Local Claude CLI execution was unavailable, so native Claude research execution remains unverified. Structural checks do not establish cross-host behavioral parity.

The [architecture](docs/architecture.md) explains the selected design and its boundaries. [NOTICE.md](NOTICE.md) records pstack source provenance and preserved MIT notices.

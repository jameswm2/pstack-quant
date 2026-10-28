# pstack-quant

Run long-form autonomous quantitative research inside an existing Codex or Claude Code session. Compare genuinely different mechanisms, justify deeper tests, preserve failed attempts and negative findings, and reserve time for synthesis. A cumulative campaign ledger carries the original mission, frontier, wall deadline, trial charges, and next action across context loss.

Start with `$quant-campaign` for broad missions or repeated studies. Use `$quant-research` for one bounded study. Research judgment stays with the coordinator and independent roles; local standard-library tools validate campaign accounting and immutable study evidence. The plugin supplies no market data, backtesting engine, live trading, or deployment approval.

```text
Use quant-campaign to investigate [mission] for up to 20 wall hours inside this session,
using only [authorized data and compute], with [trial cap]. Compare distinct mechanisms,
justify depth, preserve failures, and reserve time for synthesis. Stop early if adequate.
```

The skill frames mission-specific constraints before freezing a charter. Twenty hours is a ceiling, including host downtime. Durable state supports recovery; it does not guarantee host liveness. Native continuation is used only when available and authorized. No external launcher, daemon, global hook, or replacement session is installed.

```sh
python3 tools/campaign.py start research/campaign --charter examples/campaign/charter.json
python3 tools/campaign.py view research/campaign --json
python3 tools/campaign.py commit research/campaign --proposal decision.json --expect HEAD_FROM_VIEW
python3 tools/campaign.py trial research/campaign --assignment A01 --plan trial-plan.json
```

The shipped charter is an educational local-data example; customize the mission and permissions first. The [campaign reference](skills/quant-campaign/references/campaign.md) defines every payload. To resume, say: `Use quant-resume on research/campaign. Verify its ledger and child evidence, reconcile interrupted registration, then continue its next authorized bounded assignment without resetting the deadline.`

Run the accelerated offline campaign with `python3 examples/campaign/run.py /tmp/new-campaign-demo`. It simulates unequal commitments and a twenty-hour boundary with explicit fixture priority reviews. Missing scientific reviews stay blocked. It does not validate twenty-hour host reliability or produce a real market finding.

## Install and invoke

From an unpacked local copy, add the marketplace and install the plugin in Codex:

```sh
codex plugin marketplace add /absolute/path/to/pstack-quant
codex plugin add pstack-quant@pstack-quant
```

Invoke `$quant-campaign` directly or use normal domain-appropriate skill selection. For Claude Code, run these commands in its interactive session:

```text
/plugin marketplace add /absolute/path/to/pstack-quant
/plugin install pstack-quant@pstack-quant
/pstack-quant:quant-research Design a bounded publication-lagged forecasting experiment.
```

For a local Claude packaging check, run `claude plugin validate .` from this repository. For a local session without marketplace installation, use `claude --plugin-dir /absolute/path/to/pstack-quant`.

The source repository is [jameswm2/pstack-quant](https://github.com/jameswm2/pstack-quant). The marketplace commands also accept `jameswm2/pstack-quant` instead of the local path.

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

The campaign skill owns long missions; the research skill owns individual studies. Focused skills narrow a research request without duplicating the lifecycle contract:

| Skill | Purpose |
| --- | --- |
| `quant-campaign` | Compare mechanisms across bounded studies with cumulative recovery and budgets |
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

Native Codex `0.160.0` previously discovered the v0.1 package as `pstack-quant@pstack-quant`, version `0.1.0`, using an explicit local marketplace source. Discovery does not establish installation or skill execution. Local Claude CLI execution was unavailable, so native Claude research execution remains unverified. Structural checks do not establish cross-host behavioral parity. The [verification record](docs/verification.md) lists the checks and remaining limits.

The [architecture](docs/architecture.md) explains the selected design and its boundaries. [NOTICE.md](NOTICE.md) records pstack source provenance and preserved MIT notices.

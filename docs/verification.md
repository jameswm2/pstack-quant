# Verification record

The coordinator verified version 0.2.0 at `ebbe17a` on 2026-10-28. Subsequent documentation changes preserve the tested runtime and package sources. These checks establish local behavior and packaging. Actual twenty-hour host uptime and native Claude research execution remain unverified.

## Local behavior

```sh
python3 -m unittest discover -s tests -v
python3 tools/check_package.py
```

All 57 tests passed on Python 3.14. Tests exercise actual CLI processes and files, concurrent stale writers, retry conflicts, tampered artifacts, review bindings, permanent trial accounting, interrupted registration, family-level fixation, bounded diagnostic repair, coverage adequacy, deadlines, and reserves. The relocated-package test runs both examples without Git metadata.

The package checker passed for eight shared skills at version 0.2.0. It checks manifests, marketplace paths, local links, provenance, and example paths. `git diff --check 39669e5..HEAD` passed. `tools/evidence.py` is unchanged from the merged version 0.1 baseline.

## Accelerated campaign

```sh
python3 examples/campaign/run.py /tmp/new-campaign-demo
python3 tools/campaign.py view /tmp/new-campaign-demo --json
```

The coordinator ran the example in a fresh directory after the final runtime fix. It ended `budget_exhausted` with one permanently charged trial and zero remaining wall seconds. A separate production `view` reported no clock regression and preserved the charge, child-study blockers, continuation prompt, and next command.

The example injects a simulated UTC clock to cross a twenty-hour boundary. Its priority receipts are explicitly educational fixtures. Real scientific review seats remain missing and blocked. This trace verifies deadline and recovery behavior without measuring host uptime or producing a market finding.

## Independent acceptance

Three independent implementation reviewers inspected the campaign changes. A fresh reviewer then ran 14 targeted checks against the accepted durability fixes. All passed with no further findings. Each original reviewer also completed four raw research scenarios, producing 12 instruction assessments. The coordinator read all 12 reports. The [campaign review record](campaign-review.md) describes their scope and limits.

## Host discovery

Codex CLI `0.160.0` enumerated `pstack-quant@pstack-quant`, version `0.2.0`, using this command with the actual checkout path:

```sh
codex -c 'marketplaces.pstack-quant.source_type="local"' \
  -c 'marketplaces.pstack-quant.source="/absolute/path/to/pstack-quant"' \
  plugin list --available --json --marketplace pstack-quant
```

The returned source was the local checkout and the installation policy was `AVAILABLE`. This command did not change user configuration. Discovery does not establish installation or native model execution.

Local Claude CLI execution was unavailable. A separate CI job invokes the official Claude CLI's manifest validator. Manifest validation establishes packaging only. It does not execute research models or establish parity between hosts.

## Preserved study evidence

The merged version 0.1 checks remain in the complete suite. Two fresh standalone synthetic runs previously produced matching scientific artifacts. Both generated development data only, left the holdout ungenerated, and created no reviewer receipts. Inspection reported valid integrity, a negative development outcome, blocked research disposition, and four missing independent seats.

The future-information control failed with `AssertionError: future information at decision time`. Earlier regression checks reproduced interrupted review and decision staging defects before their repair. The [study review record](review.md) preserves the independent panel and fix verification.

## Limits

Fixture reviews cannot approve real research. The controller validates cited artifacts, declared identities, state transitions, and cumulative accounting for cooperating callers. It does not authenticate a reviewer's work, establish data truth or statistical validity, isolate a holdout at the operating-system level, or prevent an actor from rewriting the whole evidence tree. The [architecture](architecture.md) and [evidence reference](../skills/quant-research/references/evidence.md) define those boundaries.

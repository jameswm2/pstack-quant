#!/usr/bin/env python3
"""Development-only synthetic research. Never generates or reads the holdout."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import platform
import random
import sys

PLUGIN = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PLUGIN / "tools"))
import evidence


def development_rows(leaky: bool = False) -> list[dict]:
    feature_rng, outcome_rng = random.Random(101), random.Random(202)
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    rows = []
    for i in range(120):
        decision = start + timedelta(days=i)
        observed = decision - timedelta(days=1)
        available = decision - timedelta(hours=1)
        if leaky:
            available = decision + timedelta(hours=1)
        rows.append({"i": i, "observed_at": observed.isoformat(), "available_at": available.isoformat(),
                     "decision_at": decision.isoformat(), "label_at": (decision + timedelta(hours=12)).isoformat(),
                     "x": round(feature_rng.uniform(-1, 1), 8), "y": round(outcome_rng.uniform(-0.01, 0.01), 8)})
    return rows


def assert_temporal(rows: list[dict]) -> None:
    for row in rows:
        assert row["observed_at"] <= row["available_at"] <= row["decision_at"] < row["label_at"], "future information at decision time"


def study() -> dict:
    return {"id": "synthetic-lag", "question": "Does a lagged independent feature improve development outcomes over a zero-position baseline?",
            "budget": {"max_trials": 3, "active_minutes": 30},
            "protocol": {"trial_family": "one-fixed-linear-rule", "decision_rule": "Validation net mean at or below zero is negative. Otherwise inconclusive pending a fresh confirmation regime. Educational rule only.",
                         "holdout_policy": "Indices 120 through 159 are reserved. This example never generates or reads them. No confirmation mode is provided."},
            "review_seats": [{"id": "pre-method", "role": "methodology", "stage": "preregistration"},
                             {"id": "result-method", "role": "methodology", "stage": "result"},
                             {"id": "result-risk", "role": "execution-risk", "stage": "result"},
                             {"id": "result-reproduce", "role": "reproduction", "stage": "result"}]}


def make_plan(data_hash: str) -> dict:
    return {"schema": 1, "id": "t001", "study": study(), "authors": ["synthetic-demo-author"],
            "hypothesis": "A feature independent of outcomes offers no stable incremental benefit after declared costs.",
            "inputs": [{"id": "development", "status": "present", "sha256": data_hash, "provenance": "run.py development_rows; independent random streams 101 and 202; 120 rows only"}],
            "availability_rule": "Observation at prior midnight, availability one hour before decision, label twelve hours after decision. All timestamps UTC.",
            "universe": {"membership": "fixed synthetic event stream", "survivorship": "not applicable; no securities or deletions", "corporate_actions": "not applicable; synthetic events", "revisions": "none; fixed generator"},
            "splits": {"train": [0, 80], "validation": [80, 120], "holdout_reserved": [120, 160], "purge_embargo": "No overlapping labels. Twelve-hour labels end before the next daily decision. No additional embargo."},
            "estimator": {"method": "OLS slope with intercept on training only; position is sign(slope*x)", "baseline": "zero position; zero return and zero cost", "variants": 1},
            "costs": {"one_way": 0.001, "turnover": "absolute change of position, including entry from zero", "fill": "idealized fill at decision; no market realism", "liquidity_capacity": "not measured; synthetic unit exposure cannot support a capacity claim"},
            "tests": {"primary": "validation mean net return relative to zero baseline", "negative_control": "future availability must fail temporal assertion", "uncertainty": "Report four consecutive ten-event block means and sample standard error of blocks. Four blocks are too few for reliable inference.", "multiple_testing": "One registered model. No correction computed. No selection across variants."},
            "stopping_rule": "One fit and one validation. Stop without generating holdout; missing independent reviews remain blocked.",
            "reproduction": {"seeds": [101, 202], "environment": "Python 3.11+ standard library", "compare": "canonical data, result, code and dossier hashes on the same Python version"}}


def execute(run: Path) -> Path:
    run = evidence.canonical_root(run)
    registered = run / "trials/t001"
    plan = evidence.parse_plan(evidence.load(registered / "plan.json"))
    evidence.registrations(run, evidence.parse_study(evidence.load(run / "study/spec.json")))
    rows = development_rows()
    assert_temporal(rows)
    data = evidence.canonical({"rows": rows})
    assert evidence.digest(data) == plan.value["inputs"][0]["sha256"], "generator differs from registered inputs"
    expected = make_plan(evidence.digest(data))
    for key in ("splits", "estimator", "costs", "tests", "availability_rule"):
        evidence.require(plan.value[key] == expected[key], f"runner only implements the fixed synthetic design: {key}")
    evidence.require(plan.value["study"]["protocol"] == expected["study"]["protocol"], "runner only implements the fixed synthetic design: protocol")
    train, validation = rows[:80], rows[80:120]
    x_bar = sum(r["x"] for r in train) / len(train)
    y_bar = sum(r["y"] for r in train) / len(train)
    slope = sum((r["x"] - x_bar) * (r["y"] - y_bar) for r in train) / sum((r["x"] - x_bar) ** 2 for r in train)
    position, net, turnover = 0, [], 0
    for row in validation:
        next_position = 1 if slope * row["x"] >= 0 else -1
        change = abs(next_position - position)
        turnover += change
        net.append(next_position * row["y"] - plan.value["costs"]["one_way"] * change)
        position = next_position
    blocks = [sum(net[i:i + 10]) / 10 for i in range(0, 40, 10)]
    mean = sum(net) / len(net)
    block_mean = sum(blocks) / len(blocks)
    standard_error = (sum((b - block_mean) ** 2 for b in blocks) / (len(blocks) - 1) / len(blocks)) ** 0.5
    outcome = "negative" if mean <= 0 else "inconclusive"
    metrics = {"outcome": outcome, "slope": slope, "validation_net_mean": mean, "baseline_net_mean": 0,
               "validation_gross_mean": (sum(net) + turnover * 0.001) / 40, "turnover": turnover,
               "one_way_cost": 0.001, "block_means": blocks, "block_standard_error": standard_error,
               "training_count": 80, "validation_count": 40, "holdout_rows_generated": 0, "holdout_rows_read": 0,
               "interpretation": "Synthetic educational development result; no inference about market alpha or deployment readiness."}
    source = Path(__file__).read_bytes()
    helper_source = (PLUGIN / "tools/evidence.py").read_bytes()
    execution = {"schema": 1, "trial_id": "t001", "authors": ["synthetic-demo-author"],
                 "command": [sys.executable, *sys.argv],
                 "environment": {"python": platform.python_version(), "implementation": platform.python_implementation(), "platform": platform.system()},
                 "seeds": {"feature": 101, "outcome": 202}, "source_revision": "sha256 manifest " + json.dumps({"run.py": hashlib.sha256(source).hexdigest(), "evidence.py": hashlib.sha256(helper_source).hexdigest()}, sort_keys=True),
                 "data_fingerprints": {"development": evidence.digest(data)},
                 "limitations": ["Synthetic independent streams do not establish market behavior.", "Preregistration and result independent reviewers have not run. This is a partial development demonstration.", "Four blocks do not establish reliable uncertainty. No multiple-testing correction was computed.", "Holdout is procedurally reserved; filesystem isolation is not enforced.", "Idealized fills and unit exposure cannot establish liquidity or capacity."],
                 "execution_status": "completed", "outcome": outcome, "holdout_access": "unopened", "outcome_evidence": ["metrics.json"]}
    output = run / "work/demo/output"
    evidence.publish(output, {"development.json": data, "metrics.json": evidence.canonical(metrics),
                              "execution.json": evidence.canonical(execution), "run.py": source, "evidence.py": helper_source})
    return output


def demo(run: Path) -> dict:
    run = evidence.canonical_root(run)
    run.mkdir(parents=True, exist_ok=True)
    plan = make_plan(evidence.digest(evidence.canonical({"rows": development_rows()})))
    plan_path = run / "draft-plan.json"
    if plan_path.exists():
        assert evidence.load(plan_path) == plan, "existing draft differs"
    else:
        plan_path.write_bytes(evidence.canonical(plan))
    evidence.register(run, plan_path)
    output = execute(run)
    evidence.snapshot(run, "t001", output)
    decision = {"schema": 1, "id": "d001", "action": "stop", "reason": "Development demonstration complete; independent reviewers unavailable. Holdout remains unopened.",
                "evidence": ["trials/t001/snapshot/snapshot.json"], "active_minutes": 0, "units": 1, "failed_attempts": 0,
                "independent_priority_reviewer": None, "next": "Dispatch independent preregistration and result reviewers before any gated research claim. Never backdate review."}
    evidence.publish(run / "decisions/d001", {"decision.json": evidence.canonical(decision)})
    result = evidence.inspect(run)
    report = ["# Synthetic development report", "", "The single registered attempt is complete. The holdout remains unopened.", ""]
    for trial in result["trials"]:
        report.extend([f"Trial {trial['id']} has financial outcome `{trial['financial_outcome']}` and research disposition `{trial['research_disposition']}`.",
                       "", "Evidence integrity is valid. Independent preregistration review remains blocked. The execution is partial evidence, not retroactive authorization.", "",
                       "Missing reviews: " + ", ".join(trial["missing_review_seats"]) + ".", ""])
    metrics = evidence.load(output / "metrics.json")
    report.extend([f"Validation net mean is {metrics['validation_net_mean']:.8f}, compared with the zero baseline. Turnover is {metrics['turnover']} units at a one-way cost of {metrics['one_way_cost']} per unit.", "",
                   f"The standard error of four ten-event block means is {metrics['block_standard_error']:.8f}. Four blocks do not establish reliable inference. No multiple-testing correction was computed.", "",
                   "The result uses a fixed synthetic generator, one linear fit, a zero-position baseline, disclosed turnover costs, and development data only.", "",
                   "No market alpha, statistical significance, live execution safety, or deployment readiness is established.", "",
                   "See [metrics](trials/t001/snapshot/files/metrics.json), [sealed execution](trials/t001/snapshot/files/execution.json), and [decision receipt](decisions/d001/decision.json).", ""])
    (run / "report.md").write_text("\n".join(report))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["demo", "execute", "negative-control"])
    parser.add_argument("run", type=Path, nargs="?")
    args = parser.parse_args()
    if args.mode == "negative-control":
        assert_temporal(development_rows(leaky=True))
        raise AssertionError("negative control escaped temporal assertion")
    if args.run is None:
        parser.error("run directory is required")
    if args.mode == "execute":
        print(execute(args.run))
    else:
        result = demo(args.run)
        print(f"Registered {result['registered_trials']} trial; integrity valid; independent review BLOCKED; holdout unopened.")
        print(f"Report: {args.run / 'report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

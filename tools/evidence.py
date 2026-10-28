#!/usr/bin/env python3
"""Immutable local research evidence. No research code is executed here."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
import tempfile
from typing import Any


class Invalid(ValueError):
    pass


class ResearchDisposition(str, Enum):
    SUPPORTED = "supported"
    NEGATIVE = "negative"
    INCONCLUSIVE = "inconclusive"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class TrialPlan:
    value: dict

    @property
    def id(self) -> str:
        return self.value["id"]


@dataclass(frozen=True)
class Registration:
    value: dict


@dataclass(frozen=True)
class Snapshot:
    value: dict


@dataclass(frozen=True)
class Review:
    value: dict


ROLES = {"methodology", "execution-risk", "reproduction"}
OUTCOMES = {"supported", "negative", "inconclusive", "not_evaluated"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Invalid(message)


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def object_value(value: Any, label: str) -> dict:
    require(isinstance(value, dict), f"{label} must be an object")
    return value


def fields(value: dict, names: str, label: str) -> None:
    require(all(name in value for name in names.split()), f"{label} requires {names}")


def text_value(value: Any, label: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"{label} must be nonempty text")
    return value


def strings(value: Any, label: str) -> list[str]:
    require(isinstance(value, list) and bool(value), f"{label} must be a nonempty list")
    for item in value:
        text_value(item, label)
    require(len(value) == len(set(value)), f"{label} has duplicates")
    return value


def identifier(value: Any) -> str:
    require(isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", value) is not None,
            "unsafe or invalid identifier")
    return value


def sha(value: Any) -> str:
    require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None, "invalid sha256")
    return value


def relative(value: Any) -> str:
    text_value(value, "artifact path")
    p = PurePosixPath(value)
    require(bool(p.parts) and not p.is_absolute() and value == p.as_posix() and all(x not in {".", ".."} for x in p.parts)
            and "\\" not in value and ":" not in value, "unsafe artifact path")
    return value


def canonical_root(path: Path) -> Path:
    path = Path(os.path.abspath(path))
    require(not path.is_symlink(), f"symlink root is not allowed: {path}")
    return path.parent.resolve() / path.name


def safe_path(path: Path) -> Path:
    path = Path(os.path.abspath(path))
    for part in [path, *path.parents]:
        require(not part.is_symlink(), f"symlink is not allowed: {part}")
    return path


def reject_constant(value: str) -> None:
    raise Invalid(f"invalid JSON number: {value}")


def load(path: Path) -> dict:
    safe_path(path)
    require(path.is_file(), f"missing file: {path}")
    try:
        value = json.loads(path.read_text(), parse_constant=reject_constant)
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise Invalid(f"invalid JSON: {path}: {exc}") from exc
    return object_value(value, str(path))


def parse_study(value: Any) -> dict:
    study = object_value(value, "study")
    fields(study, "id question budget protocol review_seats", "study")
    identifier(study["id"])
    text_value(study["question"], "question")
    budget = object_value(study["budget"], "budget")
    for key in ("max_trials", "active_minutes"):
        require(type(budget.get(key)) is int and budget[key] > 0, f"budget.{key} must be positive integer")
    protocol = object_value(study["protocol"], "protocol")
    for key in ("trial_family", "decision_rule", "holdout_policy"):
        text_value(protocol.get(key), f"protocol.{key}")
    seats = study["review_seats"]
    require(isinstance(seats, list) and bool(seats), "review_seats must be nonempty")
    ids = []
    for seat in seats:
        object_value(seat, "review seat")
        fields(seat, "id role stage", "review seat")
        ids.append(identifier(seat["id"]))
        require(seat["role"] in ROLES, "unknown review role")
        require(seat["stage"] in {"preregistration", "result"}, "unknown review stage")
        require(seat["role"] != "reproduction" or seat["stage"] == "result", "reproduction is a result review")
    require(len(ids) == len(set(ids)), "duplicate review seat")
    require(any(s["stage"] == "preregistration" and s["role"] == "methodology" for s in seats), "missing preregistration methodology seat")
    require(ROLES <= {s["role"] for s in seats if s["stage"] == "result"}, "missing required result review role")
    return study


def parse_plan(value: dict) -> TrialPlan:
    fields(value, "schema id study authors hypothesis inputs availability_rule universe splits estimator costs tests stopping_rule reproduction", "plan")
    require(value["schema"] == 1, "unsupported plan schema")
    identifier(value["id"])
    parse_study(value["study"])
    strings(value["authors"], "authors")
    for key in ("hypothesis", "availability_rule", "stopping_rule"):
        text_value(value[key], key)
    for key in ("universe", "splits", "estimator", "costs", "tests", "reproduction"):
        require(bool(object_value(value[key], key)), f"{key} must not be empty")
    inputs = value["inputs"]
    require(isinstance(inputs, list) and bool(inputs), "inputs must be nonempty")
    ids = []
    for item in inputs:
        object_value(item, "input")
        fields(item, "id status provenance", "input")
        ids.append(identifier(item["id"]))
        text_value(item["provenance"], "input provenance")
        require(item["status"] in {"present", "missing", "unavailable"}, "invalid input status")
        if item["status"] == "present":
            sha(item.get("sha256"))
        else:
            text_value(item.get("reason"), "missing input reason")
    require(len(ids) == len(set(ids)), "duplicate input id")
    return TrialPlan(value)


def parse_execution(value: dict, plan: TrialPlan) -> dict:
    fields(value, "schema trial_id authors command environment seeds source_revision data_fingerprints limitations execution_status outcome holdout_access outcome_evidence", "execution")
    require(value["schema"] == 1 and value["trial_id"] == plan.id, "execution identity mismatch")
    strings(value["authors"], "execution authors")
    require(isinstance(value["command"], list) and bool(value["command"]), "command must be an argument list")
    text_value(value["command"][0], "command executable")
    require(all(isinstance(arg, str) for arg in value["command"]), "command arguments must be strings")
    require(bool(object_value(value["environment"], "environment")), "missing environment")
    require(bool(object_value(value["seeds"], "seeds")), "missing seeds")
    text_value(value["source_revision"], "source_revision")
    strings(value["limitations"], "limitations")
    require(value["execution_status"] in {"completed", "failed", "abandoned"}, "invalid execution status")
    require(value["outcome"] in OUTCOMES, "invalid outcome")
    require(value["execution_status"] == "completed" or value["outcome"] == "not_evaluated", "failed/abandoned is not a scientific finding")
    require(value["holdout_access"] in {"unopened", "exposed", "unknown"}, "invalid holdout_access")
    for name in strings(value["outcome_evidence"], "outcome_evidence"):
        relative(name)
    fingerprints = object_value(value["data_fingerprints"], "data_fingerprints")
    for item in plan.value["inputs"]:
        if item["status"] == "present":
            require(fingerprints.get(item["id"]) == item["sha256"], "data fingerprint differs from registration")
    for fingerprint in fingerprints.values():
        sha(fingerprint)
    return value


@contextmanager
def register_lock(root: Path):
    path = safe_path(root / ".register.lock")
    with path.open("a+b") as lock:
        if os.name == "nt":
            import msvcrt
            lock.seek(0)
            lock.write(b"0")
            lock.flush()
            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            yield
        finally:
            if os.name == "nt":
                lock.seek(0)
                msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(lock, fcntl.LOCK_UN)


def tree(path: Path) -> dict[str, bytes]:
    safe_path(path)
    require(path.is_dir(), f"missing directory: {path}")
    result = {}
    for file in sorted(path.rglob("*")):
        safe_path(file)
        mode = file.stat().st_mode
        require(stat.S_ISDIR(mode) or stat.S_ISREG(mode), f"special file is not allowed: {file}")
        if file.is_file():
            result[relative(file.relative_to(path).as_posix())] = file.read_bytes()
    return result


def publish(path: Path, contents: dict[str, bytes]) -> None:
    safe_path(path)
    if path.exists():
        require(tree(path) == contents, f"immutable publication conflict: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".pending-", dir=path.parent))
    try:
        for name, data in contents.items():
            file = temporary / relative(name)
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(data)
        try:
            temporary.rename(path)
        except OSError:
            if not path.exists():
                raise
            require(tree(path) == contents, f"immutable publication conflict: {path}")
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)


def registrations(root: Path, study: dict) -> list[tuple[TrialPlan, Registration]]:
    directory = safe_path(root / "trials")
    if not directory.exists():
        return []
    result = []
    for path in sorted(directory.iterdir()):
        safe_path(path)
        if path.name.startswith(".pending-"):
            continue
        identifier(path.name)
        plan = parse_plan(load(path / "plan.json"))
        require(plan.id == path.name and plan.value["study"] == study, "trial differs from frozen study")
        reg = load(path / "registration.json")
        expected = {"schema": 1, "trial_id": plan.id, "plan_sha256": digest(canonical(plan.value)), "study_sha256": digest(canonical(study))}
        require(reg == expected, f"registration mismatch: {path.name}")
        result.append((plan, Registration(reg)))
    require(len(result) <= study["budget"]["max_trials"], "trial budget exceeded")
    return result


def register(root: Path, plan_file: Path) -> Registration:
    root = canonical_root(root)
    plan = parse_plan(load(canonical_root(plan_file)))
    root.mkdir(parents=True, exist_ok=True)
    with register_lock(root):
        publish(root / "study", {"spec.json": canonical(plan.value["study"])})
        study = parse_study(load(root / "study/spec.json"))
        current = registrations(root, study)
        require(plan.value["study"] == study, "study protocol and budget are frozen")
        require(any(p.id == plan.id for p, _ in current) or len(current) < study["budget"]["max_trials"], "trial budget exhausted")
        value = {"schema": 1, "trial_id": plan.id, "plan_sha256": digest(canonical(plan.value)), "study_sha256": digest(canonical(study))}
        target = root / "trials" / plan.id
        if target.exists():
            require(load(target / "plan.json") == plan.value and load(target / "registration.json") == value, "immutable registration conflict")
        else:
            publish(target, {"plan.json": canonical(plan.value), "registration.json": canonical(value)})
    return Registration(value)


def snapshot(root: Path, trial: str, source: Path) -> Snapshot:
    root = canonical_root(root)
    identifier(trial)
    study = parse_study(load(root / "study/spec.json"))
    registered = {plan.id: (plan, reg) for plan, reg in registrations(root, study)}
    require(trial in registered, "trial is not registered")
    plan, reg = registered[trial]
    source = canonical_root(source)
    target = root / "trials" / trial / "snapshot"
    require(not source.is_relative_to(target) and not target.is_relative_to(source), "source and snapshot overlap")
    contents = tree(source)
    require("execution.json" in contents, "missing execution.json")
    execution = parse_execution(object_value(json.loads(contents["execution.json"], parse_constant=reject_constant), "execution"), plan)
    require(all(name in contents for name in execution["outcome_evidence"]), "missing outcome evidence")
    value = {"schema": 1, "trial_id": trial, "registration_sha256": digest(canonical(reg.value)),
             "plan_sha256": reg.value["plan_sha256"], "execution": execution,
             "files": [{"path": name, "sha256": digest(data), "bytes": len(data)} for name, data in sorted(contents.items())]}
    publish(target, {"snapshot.json": canonical(value), **{f"files/{name}": data for name, data in contents.items()}})
    return Snapshot(value)


def read_snapshot(path: Path, plan: TrialPlan, reg: Registration) -> Snapshot:
    value = load(path / "snapshot.json")
    fields(value, "schema trial_id registration_sha256 plan_sha256 execution files", "snapshot")
    require(value["schema"] == 1 and value["trial_id"] == plan.id, "snapshot identity mismatch")
    require(value["registration_sha256"] == digest(canonical(reg.value)) and value["plan_sha256"] == reg.value["plan_sha256"], "snapshot registration mismatch")
    parse_execution(object_value(value["execution"], "execution"), plan)
    files = value["files"]
    require(isinstance(files, list) and bool(files), "snapshot file inventory is missing")
    actual = tree(path / "files")
    expected = {}
    for item in files:
        object_value(item, "snapshot file")
        fields(item, "path sha256 bytes", "snapshot file")
        name = relative(item["path"])
        require(name not in expected, "duplicate snapshot file")
        sha(item["sha256"])
        require(type(item["bytes"]) is int and item["bytes"] >= 0, "invalid file size")
        require(name in actual and digest(actual[name]) == item["sha256"] and len(actual[name]) == item["bytes"], f"missing or corrupt artifact: {name}")
        expected[name] = actual[name]
    require(actual == expected, "unexpected snapshot artifacts")
    require(all(name in actual for name in value["execution"]["outcome_evidence"]), "missing outcome evidence")
    require(load(path / "files/execution.json") == value["execution"], "execution differs from sealed metadata")
    return Snapshot(value)


def parse_review(value: dict) -> Review:
    fields(value, "schema id trial_id seat_id reviewer_id role stage registration_sha256 snapshot_sha256 verdict findings evidence", "review")
    require(value["schema"] == 1, "unsupported review schema")
    for key in ("id", "trial_id", "seat_id"):
        identifier(value[key])
    text_value(value["reviewer_id"], "reviewer_id")
    require(value["role"] in ROLES and value["stage"] in {"preregistration", "result"}, "unknown review role/stage")
    require(value["verdict"] in {"accept", "revise", "blocked"}, "unknown review verdict")
    sha(value["registration_sha256"])
    if value["stage"] == "result":
        sha(value["snapshot_sha256"])
    else:
        require(value["snapshot_sha256"] is None, "preregistration review cannot bind a snapshot")
    strings(value["findings"], "review findings")
    strings(value["evidence"], "review evidence")
    return Review(value)


def inspect(root: Path) -> dict:
    root = canonical_root(root)
    study = parse_study(load(root / "study/spec.json"))
    registered = registrations(root, study)
    require(bool(registered), "study has no registered trials")
    reviews = []
    review_dir = safe_path(root / "reviews")
    if review_dir.exists():
        for directory in sorted(review_dir.iterdir()):
            safe_path(directory)
            identifier(directory.name)
            review = parse_review(load(directory / "review.json"))
            require(review.value["id"] == directory.name, "review directory identity mismatch")
            reviews.append(review)
    known = {plan.id for plan, _ in registered}
    require(all(r.value["trial_id"] in known for r in reviews), "review names an unknown trial")
    trials = []
    for plan, reg in registered:
        blockers = []
        path = safe_path(root / "trials" / plan.id / "snapshot")
        snap = read_snapshot(path, plan, reg) if path.exists() else None
        if snap is None:
            blockers.append("missing execution snapshot")
        inputs = [i["id"] for i in plan.value["inputs"] if i["status"] != "present"]
        if inputs:
            blockers.append("inputs missing or unavailable: " + ", ".join(inputs))
        authors = set(plan.value["authors"]) | (set(snap.value["execution"]["authors"]) if snap else set())
        occupied = {}
        reviewers = set()
        for review in reviews:
            r = review.value
            if r["trial_id"] != plan.id:
                continue
            seat = next((s for s in study["review_seats"] if s["id"] == r["seat_id"]), None)
            require(seat is not None and all(r[k] == seat[k] for k in ("role", "stage")), "review does not match a required seat")
            require(r["seat_id"] not in occupied, "multiple receipts for one seat; register a new trial for revision")
            require(r["reviewer_id"] not in authors and r["reviewer_id"] not in reviewers, "reviewer overlaps authors or another seat")
            require(r["registration_sha256"] == digest(canonical(reg.value)), "stale review registration binding")
            if r["stage"] == "result":
                require(snap is not None and r["snapshot_sha256"] == digest(canonical(snap.value)), "stale review snapshot binding")
            occupied[r["seat_id"]] = r["verdict"]
            reviewers.add(r["reviewer_id"])
        missing = [s["id"] for s in study["review_seats"] if s["id"] not in occupied]
        for seat in study["review_seats"]:
            if occupied.get(seat["id"]) != "accept":
                blockers.append(f"independent review {seat['id']}: {occupied.get(seat['id'], 'missing')}")
        authorization = all(occupied.get(s["id"]) == "accept" for s in study["review_seats"] if s["stage"] == "preregistration")
        outcome = snap.value["execution"]["outcome"] if snap else "not_evaluated"
        execution_status = snap.value["execution"]["execution_status"] if snap else "unrecorded"
        holdout = snap.value["execution"]["holdout_access"] if snap else "unknown"
        if snap and (execution_status != "completed" or outcome == "not_evaluated"):
            blockers.append("execution has no scientific finding")
        if holdout != "unopened":
            blockers.append("holdout exposed or unknown; independent evaluation regime assessment required")
        trials.append({"id": plan.id, "execution_status": execution_status, "financial_outcome": outcome,
                       "process_integrity": "valid", "preregistration_review": "accepted" if authorization else "blocked",
                       "independent_review": "accepted" if not missing and all(v == "accept" for v in occupied.values()) else "blocked",
                       "missing_review_seats": missing, "holdout_access": holdout, "blockers": blockers,
                       "research_disposition": ResearchDisposition.BLOCKED.value if blockers else outcome,
                       "registration_sha256": digest(canonical(reg.value)), "snapshot_sha256": digest(canonical(snap.value)) if snap else None})
    decisions = []
    decision_dir = safe_path(root / "decisions")
    if decision_dir.exists():
        for directory in sorted(decision_dir.iterdir()):
            safe_path(directory)
            identifier(directory.name)
            decision = load(directory / "decision.json")
            fields(decision, "schema id action reason evidence active_minutes units failed_attempts independent_priority_reviewer next", "decision")
            require(decision["schema"] == 1 and decision["id"] == directory.name, "decision identity mismatch")
            require(decision["action"] in {"continue", "narrow", "stop"}, "invalid priority action")
            for key in ("reason", "next"):
                text_value(decision[key], key)
            for key in ("active_minutes", "units", "failed_attempts"):
                require(type(decision[key]) is int and decision[key] >= 0, "invalid priority counter")
            if decision["independent_priority_reviewer"] is not None:
                text_value(decision["independent_priority_reviewer"], "priority reviewer")
            for name in strings(decision["evidence"], "decision evidence"):
                require(safe_path(root / relative(name)).is_file(), "missing decision evidence")
            decisions.append(decision)
    pending = [str(p.relative_to(root)) for p in root.rglob(".pending-*")]
    return {"schema": 1, "study_id": study["id"], "registered_trials": len(trials), "max_trials": study["budget"]["max_trials"],
            "process_integrity": "valid", "complete": all(not t["blockers"] for t in trials), "trials": trials,
            "priority_receipts": decisions,
            "warnings": ["Independent identity, actual ordering, data truth, statistical validity, and holdout isolation are not authenticated."]
                        + (["Interrupted staging directories ignored: " + ", ".join(pending)] if pending else [])}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="verb", required=True)
    reg = commands.add_parser("register", help="freeze a plan and count a trial")
    reg.add_argument("run", type=Path)
    reg.add_argument("--plan", required=True, type=Path)
    snap = commands.add_parser("snapshot", help="seal an output bundle; does not execute it")
    snap.add_argument("run", type=Path)
    snap.add_argument("--trial", required=True)
    snap.add_argument("--source", required=True, type=Path)
    check = commands.add_parser("inspect", help="verify evidence and derive gates")
    check.add_argument("run", type=Path)
    check.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.verb == "register":
            result = register(args.run, args.plan).value
        elif args.verb == "snapshot":
            result = snapshot(args.run, args.trial, args.source).value
        else:
            result = inspect(args.run)
            if not args.json:
                print(f"Study {result['study_id']}: {result['registered_trials']}/{result['max_trials']} trials. Evidence integrity valid.")
                for trial in result["trials"]:
                    print(f"{trial['id']}: outcome={trial['financial_outcome']}; disposition={trial['research_disposition']}; execution={trial['execution_status']}")
                    for blocker in trial["blockers"]:
                        print(f"  BLOCKED: {blocker}")
                for warning in result["warnings"]:
                    print(f"LIMIT: {warning}")
                return 0 if result["complete"] else 1
        print(canonical(result).decode(), end="")
        return 1 if args.verb == "inspect" and not result["complete"] else 0
    except (Invalid, OSError, ValueError, TypeError, KeyError) as exc:
        if args.verb == "inspect" and args.json:
            print(canonical({"process_integrity": "invalid", "complete": False, "research_disposition": "blocked", "error": str(exc)}).decode(), end="")
        else:
            print(f"INVALID: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

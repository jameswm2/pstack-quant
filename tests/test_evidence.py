"""Public CLI behavior and evidence boundaries. Review fixtures are declared test identities."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "examples/synthetic"))
import run as example
sys.path.insert(0, str(ROOT / "tools"))
import evidence


class EvidenceCLI(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.run = self.base / "research"
        self.plan = example.make_plan(evidence.digest(evidence.canonical({"rows": example.development_rows()})))
        self.plan_file = self.base / "plan.json"
        self.write(self.plan_file, self.plan)

    def write(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(evidence.canonical(value))

    def cli(self, *args, code=0):
        result = subprocess.run([sys.executable, str(ROOT / "tools/evidence.py"), *map(str, args)], capture_output=True, text=True)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return result

    def register(self):
        return self.cli("register", self.run, "--plan", self.plan_file)

    def seal(self, outcome=None, status="completed"):
        self.register()
        output = example.execute(self.run)
        if outcome or status != "completed":
            execution = evidence.load(output / "execution.json")
            execution.update(outcome=outcome or "not_evaluated", execution_status=status)
            self.write(output / "execution.json", execution)
        self.cli("snapshot", self.run, "--trial", "t001", "--source", output)
        return output

    def inspect(self, code=1):
        return json.loads(self.cli("inspect", self.run, "--json", code=code).stdout)

    def reviews(self, *, verdict="accept"):
        """Test fixture only. Production example never calls this method."""
        info = self.inspect()["trials"][0]
        for i, seat in enumerate(self.plan["study"]["review_seats"]):
            receipt = {"schema": 1, "id": f"review{i}", "trial_id": "t001", "seat_id": seat["id"], "reviewer_id": f"test-independent-{i}",
                       "role": seat["role"], "stage": seat["stage"], "registration_sha256": info["registration_sha256"],
                       "snapshot_sha256": info["snapshot_sha256"] if seat["stage"] == "result" else None,
                       "verdict": verdict, "findings": ["Test fixture verdict, not a real research review."], "evidence": ["Test fixture evidence."]}
            self.write(self.run / "reviews" / receipt["id"] / "review.json", receipt)

    def test_registration_and_snapshot_idempotence_and_conflict(self):
        first = self.register().stdout
        self.assertEqual(first, self.register().stdout)
        output = self.seal()
        self.assertEqual(first, self.register().stdout)
        one = self.cli("snapshot", self.run, "--trial", "t001", "--source", output).stdout
        self.assertEqual(one, self.cli("snapshot", self.run, "--trial", "t001", "--source", output).stdout)
        (output / "metrics.json").write_text("changed")
        self.cli("snapshot", self.run, "--trial", "t001", "--source", output, code=2)
        self.plan["hypothesis"] = "changed hypothesis"
        self.write(self.plan_file, self.plan)
        self.cli("register", self.run, "--plan", self.plan_file, code=2)

    def test_budget_counts_unexecuted_failed_and_abandoned(self):
        self.seal(status="failed")
        for trial in ("t002", "t003"):
            self.plan["id"] = trial
            self.write(self.plan_file, self.plan)
            self.register()
        self.plan["id"] = "t004"
        self.write(self.plan_file, self.plan)
        self.cli("register", self.run, "--plan", self.plan_file, code=2)
        result = self.inspect()
        self.assertEqual(result["registered_trials"], 3)
        self.assertEqual(result["trials"][0]["execution_status"], "failed")
        self.assertEqual(result["trials"][0]["financial_outcome"], "not_evaluated")
        self.assertEqual(result["trials"][1]["execution_status"], "unrecorded")

    def test_study_budget_and_protocol_cannot_reset_with_new_id(self):
        self.register()
        self.plan["id"] = "t002"
        self.plan["study"]["budget"]["max_trials"] = 900
        self.write(self.plan_file, self.plan)
        self.cli("register", self.run, "--plan", self.plan_file, code=2)
        self.plan["study"]["budget"]["max_trials"] = 3
        self.plan["study"]["protocol"]["trial_family"] = "reset-family"
        self.write(self.plan_file, self.plan)
        self.cli("register", self.run, "--plan", self.plan_file, code=2)

    def test_missing_reviews_are_blocked_and_negative_is_separate(self):
        self.seal(outcome="negative")
        trial = self.inspect()["trials"][0]
        self.assertEqual(trial["financial_outcome"], "negative")
        self.assertEqual(trial["research_disposition"], "blocked")
        self.assertEqual(len(trial["missing_review_seats"]), 4)
        self.assertEqual(trial["preregistration_review"], "blocked")
        self.assertIn("BLOCKED", self.cli("inspect", self.run, code=1).stdout)

    def test_valid_test_receipts_preserve_negative_and_inconclusive(self):
        for outcome in ("negative", "inconclusive"):
            with self.subTest(outcome=outcome):
                self.run = self.base / outcome
                self.seal(outcome=outcome)
                self.reviews()
                trial = self.inspect(code=0)["trials"][0]
                self.assertEqual(trial["research_disposition"], outcome)
                self.assertEqual(trial["process_integrity"], "valid")

    def test_failed_and_abandoned_do_not_become_negative_findings(self):
        for status in ("failed", "abandoned"):
            with self.subTest(status=status):
                self.run = self.base / status
                self.seal(status=status)
                self.reviews()
                self.assertEqual(self.inspect()["trials"][0]["financial_outcome"], "not_evaluated")
        self.run = self.base / "bad"
        self.register()
        output = example.execute(self.run)
        execution = evidence.load(output / "execution.json")
        execution.update(execution_status="failed", outcome="negative")
        self.write(output / "execution.json", execution)
        self.cli("snapshot", self.run, "--trial", "t001", "--source", output, code=2)

    def test_tampering_missing_file_unexpected_file_and_invalid_json(self):
        self.seal()
        metrics = self.run / "trials/t001/snapshot/files/metrics.json"
        original = metrics.read_bytes()
        metrics.write_bytes(b"tampered")
        self.assertEqual(self.inspect(code=2)["process_integrity"], "invalid")
        metrics.write_bytes(original)
        metrics.unlink()
        self.inspect(code=2)
        metrics.write_bytes(original)
        unexpected = metrics.parent / "unsealed.txt"
        unexpected.write_text("unsealed")
        self.inspect(code=2)
        unexpected.unlink()
        snapshot = metrics.parent.parent / "snapshot.json"
        snapshot.write_text("{broken")
        self.inspect(code=2)

    def test_stale_review_author_overlap_and_reused_reviewer(self):
        self.seal()
        self.reviews()
        path = self.run / "reviews/review1/review.json"
        original = evidence.load(path)
        for key, value in (("snapshot_sha256", "0" * 64), ("registration_sha256", "1" * 64),
                           ("reviewer_id", "synthetic-demo-author"), ("reviewer_id", "test-independent-0")):
            with self.subTest(key=key, value=value):
                receipt = {**original, key: value}
                self.write(path, receipt)
                self.inspect(code=2)
        self.write(path, {**original, "verdict": "revise"})
        self.assertEqual(self.inspect()["trials"][0]["independent_review"], "blocked")

    def test_missing_and_unavailable_inputs_block_claims(self):
        for status in ("missing", "unavailable"):
            self.run = self.base / status
            plan = copy.deepcopy(self.plan)
            plan["inputs"].append({"id": "vendor", "status": status, "provenance": "not acquired", "reason": "not available offline"})
            self.write(self.plan_file, plan)
            self.seal()
            self.reviews()
            self.assertTrue(any("inputs missing or unavailable" in b for b in self.inspect()["trials"][0]["blockers"]))

    def test_unsafe_ids_traversal_and_symlinks(self):
        for trial_id in ("../outside", "/tmp/outside", "a/b", "."):
            self.plan["id"] = trial_id
            self.write(self.plan_file, self.plan)
            self.cli("register", self.run, "--plan", self.plan_file, code=2)
        self.plan["id"] = "t001"
        self.write(self.plan_file, self.plan)
        self.register()
        output = example.execute(self.run)
        (output / "link").symlink_to(self.plan_file)
        self.cli("snapshot", self.run, "--trial", "t001", "--source", output, code=2)
        (output / "link").unlink()
        self.cli("snapshot", self.run, "--trial", "t001", "--source", output)
        path = self.run / "trials/t001/snapshot/snapshot.json"
        snap = evidence.load(path)
        snap["files"][0]["path"] = "../escape"
        self.write(path, snap)
        self.inspect(code=2)
        alias = self.base / "alias"
        alias.symlink_to(self.run, target_is_directory=True)
        self.cli("inspect", alias, "--json", code=2)

    def test_symlinked_parent_is_host_alias_not_artifact_link(self):
        real_parent = self.base / "real-parent"
        real_parent.mkdir()
        alias_parent = self.base / "host-alias"
        alias_parent.symlink_to(real_parent, target_is_directory=True)
        self.run = alias_parent / "research"
        self.seal()
        self.assertEqual(self.inspect()["registered_trials"], 1)
        artifact = self.run / "trials/t001/snapshot/files/metrics.json"
        artifact.unlink()
        artifact.symlink_to(self.plan_file)
        self.inspect(code=2)

    def test_missing_snapshot_is_incomplete_not_negative(self):
        self.register()
        trial = self.inspect()["trials"][0]
        self.assertEqual(trial["financial_outcome"], "not_evaluated")
        self.assertEqual(trial["research_disposition"], "blocked")

    def test_exact_command_can_include_empty_arguments(self):
        self.register()
        output = example.execute(self.run)
        path = output / "execution.json"
        execution = evidence.load(path)
        execution["command"] = ["python3", "study.py", "--prefix", ""]
        self.write(path, execution)
        self.cli("snapshot", self.run, "--trial", "t001", "--source", output)
        self.assertEqual(self.inspect()["trials"][0]["process_integrity"], "valid")

    def test_snapshot_requires_outcome_evidence_and_registered_data(self):
        self.register()
        output = example.execute(self.run)
        path = output / "execution.json"
        original = evidence.load(path)
        for change in ({"outcome_evidence": ["missing.json"]}, {"data_fingerprints": {"development": "0" * 64}}):
            self.write(path, {**original, **change})
            self.cli("snapshot", self.run, "--trial", "t001", "--source", output, code=2)

    def test_holdout_unknown_or_exposed_cannot_pass(self):
        self.register()
        output = example.execute(self.run)
        path = output / "execution.json"
        execution = evidence.load(path)
        execution["holdout_access"] = "exposed"
        self.write(path, execution)
        self.cli("snapshot", self.run, "--trial", "t001", "--source", output)
        self.reviews()
        self.assertTrue(any("holdout" in b for b in self.inspect()["trials"][0]["blockers"]))

    def test_interrupted_staging_is_ignored_not_counted(self):
        self.register()
        pending = self.run / "trials/.pending-interrupted"
        pending.mkdir()
        (pending / "partial").write_text("partial")
        self.assertEqual(self.inspect()["registered_trials"], 1)
        self.assertTrue(any("Interrupted" in w for w in self.inspect()["warnings"]))
        self.register()

    def test_concurrent_registration_cannot_overspend(self):
        plans = []
        for i in range(6):
            plan = copy.deepcopy(self.plan)
            plan["id"] = f"t{i:03}"
            path = self.base / f"plan{i}.json"
            self.write(path, plan)
            plans.append(path)
        processes = [subprocess.Popen([sys.executable, str(ROOT / "tools/evidence.py"), "register", str(self.run), "--plan", str(p)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for p in plans]
        codes = []
        for process in processes:
            process.communicate(timeout=20)
            codes.append(process.returncode)
        self.assertEqual(codes.count(0), 3)
        self.assertEqual(codes.count(2), 3)
        self.assertEqual(self.inspect()["registered_trials"], 3)

    def test_example_refuses_a_registered_split_it_does_not_implement(self):
        self.plan["splits"]["validation"] = [60, 120]
        self.write(self.plan_file, self.plan)
        self.register()
        result = subprocess.run([sys.executable, str(ROOT / "examples/synthetic/run.py"), "execute", str(self.run)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0, "runner silently ignored changed registered splits")
        self.assertIn("fixed synthetic design", result.stderr)

    def test_negative_control_fails_at_temporal_boundary(self):
        result = subprocess.run([sys.executable, str(ROOT / "examples/synthetic/run.py"), "negative-control"], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("future information at decision time", result.stderr)

    def test_demo_twice_has_same_scientific_artifacts_no_receipts(self):
        runs = [self.base / "demo-one", self.base / "demo-two"]
        for run in runs:
            result = subprocess.run([sys.executable, str(ROOT / "examples/synthetic/run.py"), "demo", str(run)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((run / "reviews").exists())
        for name in ("metrics.json", "development.json", "run.py", "evidence.py"):
            self.assertEqual((runs[0] / "trials/t001/snapshot/files" / name).read_bytes(), (runs[1] / "trials/t001/snapshot/files" / name).read_bytes())
        for run in runs:
            inspection = json.loads(self.cli("inspect", run, "--json", code=1).stdout)
            self.assertEqual(inspection["trials"][0]["holdout_access"], "unopened")
            self.assertEqual(inspection["priority_receipts"][0]["action"], "stop")
            metrics = evidence.load(run / "trials/t001/snapshot/files/metrics.json")
            self.assertEqual(metrics["holdout_rows_read"], 0)
            self.assertEqual(metrics["holdout_rows_generated"], 0)


if __name__ == "__main__":
    unittest.main()

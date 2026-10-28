#!/usr/bin/env python3
"""Check the shipped plugin's identities, paths, skills, links, and provenance offline."""
import argparse
import json
from pathlib import Path
import re
import sys


class PackageError(ValueError):
    pass


def check(root: Path) -> list[str]:
    root = root.resolve()
    def require(condition, message):
        if not condition:
            raise PackageError(message)

    def read_json(name):
        path = root / name
        require(path.is_file(), f"missing {name}")
        value = json.loads(path.read_text())
        require(isinstance(value, dict), f"{name} must be an object")
        return value

    def local_path(name):
        require(isinstance(name, str) and name.startswith("./"), f"path must be plugin-relative: {name}")
        path = (root / name).resolve()
        require(path.is_relative_to(root) and path.exists(), f"missing or escaping path: {name}")
        return path

    codex = read_json(".codex-plugin/plugin.json")
    claude = read_json(".claude-plugin/plugin.json")
    for key in ("name", "version", "description", "author", "repository", "license"):
        require(codex.get(key) == claude.get(key) and bool(codex.get(key)), f"manifest mismatch: {key}")
    require(codex["name"] == "pstack-quant", "unexpected plugin name")
    require(re.fullmatch(r"\d+\.\d+\.\d+", codex["version"]) is not None, "invalid version")
    require(local_path(codex["skills"]) == root / "skills", "skills must share the root tree")
    require(not any(key in manifest for manifest in (codex, claude) for key in ("hooks", "mcpServers", "agents")), "unexpected runtime component")
    codex_market = read_json(".agents/plugins/marketplace.json")
    claude_market = read_json(".claude-plugin/marketplace.json")
    require(codex_market["name"] == claude_market["name"] == codex["name"], "marketplace identity mismatch")
    for market in (codex_market, claude_market):
        require(len(market["plugins"]) == 1 and market["plugins"][0]["name"] == codex["name"], "wrong marketplace plugin")
    entry = codex_market["plugins"][0]
    require(entry["source"]["source"] == "local" and local_path(entry["source"]["path"]) == root, "invalid Codex marketplace source")
    require(entry["policy"] == {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}, "invalid Codex marketplace policy")
    require(local_path(claude_market["plugins"][0]["source"]) == root, "invalid Claude marketplace source")
    require(bool(claude_market["owner"]["name"]), "missing Claude marketplace owner")
    skills = sorted((root / "skills").glob("*/SKILL.md"))
    require(bool(skills), "no discoverable skills")
    for path in skills:
        content = path.read_text()
        front = re.match(r"\A---\n(.*?)\n---\n", content, re.S)
        require(front is not None, f"invalid skill frontmatter: {path}")
        metadata = {}
        for line in front[1].splitlines():
            key, separator, value = line.partition(":")
            require(bool(separator), f"invalid frontmatter line: {path}")
            metadata[key] = value.strip()
        require(metadata.get("name") == path.parent.name, f"skill name mismatch: {path}")
        require(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", metadata["name"]) is not None, f"unsafe skill name: {path}")
        require(bool(metadata.get("description")), f"missing description: {path}")
        invocation = path.parent / "agents/openai.yaml"
        require(invocation.is_file() and invocation.read_text() == "policy:\n  allow_implicit_invocation: true\n", f"missing normal invocation policy: {path}")
    for path in root.rglob("*.md"):
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text()):
            if target.startswith(("https://", "http://", "#", "mailto:")):
                continue
            relative = target.split("#", 1)[0]
            destination = (path.parent / relative).resolve()
            require(destination.is_relative_to(root) and destination.exists(), f"broken or escaping link in {path.relative_to(root)}: {target}")
    for name in ("tools/evidence.py", "tools/campaign.py", "examples/campaign/run.py", "examples/campaign/charter.json", "tests/test_campaign.py", "skills/quant-campaign/references/campaign.md", "examples/synthetic/run.py", "tests/test_evidence.py", "docs/architecture.md", "README.md", "NOTICE.md", "LICENSE", "licenses/pstack-MIT.txt", ".github/workflows/check.yml"):
        require((root / name).is_file(), f"missing package artifact: {name}")
    for name in ("LICENSE", "licenses/pstack-MIT.txt"):
        require("Permission is hereby granted, free of charge" in (root / name).read_text(), f"missing MIT notice: {name}")
    upstream = (root / "licenses/pstack-MIT.txt").read_text()
    require("Lauren Tan" in upstream and "Michael Denyer" in upstream, "missing upstream copyright")
    notice = (root / "NOTICE.md").read_text()
    require("0.9.103" in notice and "michael-denyer/pstack-claude" in notice, "missing source provenance")
    return [f"Package {codex['name']} {codex['version']} valid.", f"{len(skills)} shared skills; manifests, marketplace paths, local links, provenance, and executable example paths checked."]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, nargs="?", default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        for message in check(args.root):
            print(message)
        return 0
    except (PackageError, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"INVALID PACKAGE: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

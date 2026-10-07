#!/usr/bin/env python3
"""Zero-network repository preflight for FirstRefusal."""

from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "contracts" / "firstrefusal.py"
CONSUMER = ROOT / "contracts" / "protected_transfer.py"


class Fail(RuntimeError):
    pass


def check(ok: bool, message: str) -> None:
    if not ok:
        raise Fail(message)


def dotted(node: ast.AST) -> str:
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return ""


def class_names(tree: ast.Module) -> list[str]:
    result = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            if any(dotted(base) == "gl.Contract" for base in node.bases):
                result.append(node.name)
    return result


def main() -> None:
    count = 0
    main_source = MAIN.read_text(encoding="utf-8")
    consumer_source = CONSUMER.read_text(encoding="utf-8")
    main_tree = ast.parse(main_source)
    consumer_tree = ast.parse(consumer_source)

    check(class_names(main_tree) == ["FirstRefusal"], "expected one FirstRefusal(gl.Contract)")
    count += 1
    check(class_names(consumer_tree) == ["ProtectedTransfer"], "expected one ProtectedTransfer(gl.Contract)")
    count += 1

    deployables = sorted(p.name for p in (ROOT / "contracts").glob("*.py"))
    check(deployables == ["firstrefusal.py", "protected_transfer.py"], f"unexpected deployables: {deployables}")
    count += 1

    check(main_source.count("gl.vm.run_nondet_unsafe") == 1, "main contract must have exactly one custom consensus boundary")
    count += 1
    check("gl.nondet.web.render" in main_source, "public web re-observation missing")
    count += 1
    check("gl.nondet.exec_prompt" in main_source, "semantic classifier missing")
    count += 1
    check("inspect_offer_once(" in main_source and main_source.count("inspect_offer_once(") >= 3,
          "leader and validator must share independent inspection logic")
    count += 1
    check("include_source=True" in main_source, "validator must retain its independently fetched source")
    count += 1
    check("excerpt not in source" in main_source, "validator source-grounding check missing")
    count += 1

    for invariant in (
        "holder must match the exact frozen terms",
        "right definition hash mismatch",
        "offer terms hash mismatch",
        "another unresolved offer is still active",
        "only holder may exercise",
        "only holder may waive",
        "only grantor may submit an offer",
    ):
        check(invariant in main_source, f"missing invariant: {invariant}")
        count += 1

    check("is_transfer_authorized" in consumer_source, "consumer authorization call missing")
    count += 1
    check("blocks_unencumbered_transfer" in consumer_source, "consumer unencumbered gate missing")
    count += 1
    check("self.right_hash" in consumer_source, "consumer does not pin right hash")
    count += 1

    check(not (ROOT / "frontend").exists(), "frontend directory must not exist")
    count += 1

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    config = (ROOT / "gltest.config.yaml").read_text(encoding="utf-8")
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    check("61999" in readme and "https://studio.genlayer.com/api" in readme, "README network lock incomplete")
    count += 1
    check("https://studio.genlayer.com/api" in config and "studionet" in config, "gltest studionet profile missing")
    count += 1
    check(package.get("devDependencies", {}).get("genlayer") == "0.39.1", "CLI must be pinned to genlayer@0.39.1")
    count += 1

    forbidden = "619" + "97"
    hits = []
    ignored_parts = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache"}
    for path in ROOT.rglob("*"):
        if any(part in ignored_parts for part in path.relative_to(ROOT).parts):
            continue
        if path.is_file() and path.suffix.lower() not in {".zip", ".pyc"} and "__pycache__" not in path.parts:
            try:
                text = path.read_text(encoding="utf-8")
            except Exception:
                continue
            if forbidden in text:
                hits.append(str(path.relative_to(ROOT)))
    check(not hits, f"alternate chain ID leaked into repository: {hits}")
    count += 1

    for fixture_name in ("covered_offer.json", "outside_scope_offer.json"):
        data = json.loads((ROOT / "fixtures" / fixture_name).read_text(encoding="utf-8"))
        check(data.get("asset_key") == "asset-x", f"bad fixture asset in {fixture_name}")
        check(isinstance(data.get("terms"), dict) and data["terms"], f"missing fixture terms in {fixture_name}")
        count += 2

    handoff = (ROOT / "FIRSTREFUSAL_CODEX_HANDOFF.txt").read_text(encoding="utf-8")
    check("lolaaa00/First-refusal-" in handoff, "handoff target repository missing")
    check("61999" in handoff, "handoff network lock missing")
    check("NO FRONTEND" in handoff, "handoff frontend prohibition missing")
    count += 3

    print(f"PASS: {count} FirstRefusal preflight checks")


if __name__ == "__main__":
    try:
        main()
    except Fail as exc:
        raise SystemExit(f"FAIL: {exc}")

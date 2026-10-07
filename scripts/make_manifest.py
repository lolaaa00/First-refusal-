#!/usr/bin/env python3
"""Create a deterministic pre-deployment file digest manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREDEPLOYMENT_OUT = ROOT / "artifacts" / "PREDEPLOYMENT_MANIFEST.json"
FINAL_OUT = ROOT / "artifacts" / "FINAL_MANIFEST.json"
SKIP_PARTS = {".git", ".venv", "node_modules", "__pycache__", "artifacts"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    entries = {}
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        if path.suffix == ".zip":
            continue
        entries[str(path.relative_to(ROOT)).replace("\\", "/")] = digest(path)

    payload = {
        "project": "firstrefusal",
        "target_repository": "lolaaa00/First-refusal-",
        "network": {
            "name": "Studionet",
            "chain_id": 61999,
            "rpc": "https://studio.genlayer.com/api",
            "explorer": "https://explorer-studio.genlayer.com",
        },
        "files": entries,
    }
    PREDEPLOYMENT_OUT.parent.mkdir(parents=True, exist_ok=True)
    PREDEPLOYMENT_OUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    fixture_placeholder = "REPLACE_WITH_FUNDED_STUDIONET_THIRD_PARTY_ADDRESS"
    fixtures_final = all(
        fixture_placeholder not in (ROOT / "fixtures" / name).read_text(encoding="utf-8")
        for name in ("covered_offer.json", "outside_scope_offer.json")
    )
    final_payload = {
        "project": "firstrefusal",
        "completion_status": "awaiting_external_checkpoints",
        "network": payload["network"],
        "cli_version_required": "0.39.1",
        "git": {
            "target_repository": "https://github.com/lolaaa00/First-refusal-",
            "final_head": None,
            "fixture_commit": None,
            "ci_run_url": None,
        },
        "fixtures": {
            "final_addresses_installed": fixtures_final,
            "covered_url": None,
            "outside_scope_url": None,
        },
        "source_sha256": {
            "firstrefusal": digest(ROOT / "contracts" / "firstrefusal.py"),
            "protected_transfer": digest(ROOT / "contracts" / "protected_transfer.py"),
        },
        "deployments": {
            "firstrefusal": None,
            "protected_transfer": [],
        },
        "live_lifecycles": {
            "covered": None,
            "outside_scope": None,
            "waiver": None,
            "match_window_expiry": None,
            "fail_closed_negative": None,
        },
        "verification": {
            "direct_mode": "60 passed locally on 2026-10-07",
            "ast_lint_firstrefusal": "passed",
            "ast_lint_protected_transfer": "passed",
            "full_sdk_validation": "blocked: official SDK artifact missing from linter index",
            "preflight": "31 checks passed locally on 2026-10-07",
            "source_parity": None,
        },
        "limitations": [
            "GitHub repository exists; checkpoint history, fixtures, CI, and live evidence are pending.",
            "Final fixture buyer address and immutable fixture commit are not available.",
            "Only one existing local Studionet account is funded; holder and third-party accounts have zero balance.",
            "No contracts or lifecycle transactions have been deployed or signed.",
            "GenVM full SDK validation cannot load the documented SDK hash because the linter artifact index reports it missing.",
            "The required genlayer@0.39.1 development dependency tree has six npm audit findings (four moderate, two critical); automatic replacement would violate the CLI pin.",
        ],
    }
    FINAL_OUT.write_text(
        json.dumps(final_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(PREDEPLOYMENT_OUT)
    print(FINAL_OUT)


if __name__ == "__main__":
    main()

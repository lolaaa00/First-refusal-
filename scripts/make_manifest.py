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
    if FINAL_OUT.exists():
        final_payload = json.loads(FINAL_OUT.read_text(encoding="utf-8"))
    else:
        final_payload = {
            "completion_status": "awaiting_external_checkpoints",
            "git": {},
            "deployments": {"firstrefusal": None, "protected_transfer": []},
            "live_lifecycles": {
                "covered": None,
                "outside_scope": None,
                "waiver": None,
                "match_window_expiry": None,
                "fail_closed_negative": None,
            },
            "verification": {},
            "limitations": [],
        }

    # Refresh reproducible facts without erasing observed deployment/lifecycle
    # evidence recorded between checkpoints.
    final_payload["project"] = "firstrefusal"
    final_payload["network"] = payload["network"]
    final_payload["cli_version_required"] = "0.39.1"
    final_payload.setdefault("git", {})["target_repository"] = (
        "https://github.com/lolaaa00/First-refusal-"
    )
    final_payload["git"]["fixture_commit"] = (
        "019c8b2587b10fab430760ef01f2281617f24f2b"
    )
    final_payload["fixtures"] = {
        "final_addresses_installed": fixtures_final,
        "covered_url": "https://raw.githubusercontent.com/lolaaa00/First-refusal-/019c8b2587b10fab430760ef01f2281617f24f2b/fixtures/covered_offer.json",
        "outside_scope_url": "https://raw.githubusercontent.com/lolaaa00/First-refusal-/019c8b2587b10fab430760ef01f2281617f24f2b/fixtures/outside_scope_offer.json",
    }
    final_payload["source_sha256"] = {
        "firstrefusal": digest(ROOT / "contracts" / "firstrefusal.py"),
        "protected_transfer": digest(ROOT / "contracts" / "protected_transfer.py"),
    }
    FINAL_OUT.write_text(
        json.dumps(final_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(PREDEPLOYMENT_OUT)
    print(FINAL_OUT)


if __name__ == "__main__":
    main()

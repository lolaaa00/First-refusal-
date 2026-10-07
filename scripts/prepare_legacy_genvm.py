#!/usr/bin/env python3
"""Build the small v0.29 Direct Mode cache from a current GenVM tree.

The v0.29 testing suite still looks for the retired ``genvm`` release asset.
Current ``genvm-manager`` bundles retain the same content-addressed legacy
runner archives under ``executor/*/legacy-runners``.  This script copies only
the immutable runner named by the contract header and its declared standard
library dependency into the old outer-tar layout.
"""

from __future__ import annotations

import argparse
import io
import json
import re
import tarfile
from pathlib import Path


RUNNER_PATTERN = re.compile(r'"Depends"\s*:\s*"py-genlayer:([^"]+)"')


def runner_archive(root: Path, runner_type: str, runner_hash: str) -> Path:
    relative = Path(runner_type) / runner_hash[:2] / f"{runner_hash[2:]}.tar"
    matches = sorted(root.glob(f"executor/*/legacy-runners/{relative}"))
    if len(matches) != 1:
        raise SystemExit(
            f"expected one {runner_type}:{runner_hash} archive, found {len(matches)}"
        )
    return matches[0]


def manifest(archive: Path) -> dict:
    with tarfile.open(archive, "r:") as inner:
        member = inner.getmember("runner.json")
        extracted = inner.extractfile(member)
        if extracted is None:
            raise SystemExit(f"runner.json missing from {archive}")
        return json.load(extracted)


def dependency_hash(data: dict, dependency: str) -> str:
    prefix = f"{dependency}:"
    for step in data.get("Seq", []):
        value = step.get("Depends", "")
        if value.startswith(prefix):
            return value[len(prefix) :]
    raise SystemExit(f"{dependency} dependency missing from runner manifest")


def add_archive(
    output: tarfile.TarFile, source: Path, runner_type: str, runner_hash: str
) -> None:
    payload = source.read_bytes()
    info = tarfile.TarInfo(
        f"runners/{runner_type}/{runner_hash[:2]}/{runner_hash[2:]}.tar"
    )
    info.size = len(payload)
    info.mode = 0o644
    info.mtime = 0
    output.addfile(info, io.BytesIO(payload))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tree", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    header = args.contract.read_text(encoding="utf-8")[:2000]
    match = RUNNER_PATTERN.search(header)
    if match is None:
        raise SystemExit("py-genlayer dependency missing from contract header")

    runner_hash = match.group(1)
    runner = runner_archive(args.tree, "py-genlayer", runner_hash)
    std_hash = dependency_hash(manifest(runner), "py-lib-genlayer-std")
    std = runner_archive(args.tree, "py-lib-genlayer-std", std_hash)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(args.output, "w:xz") as output:
        add_archive(output, runner, "py-genlayer", runner_hash)
        add_archive(output, std, "py-lib-genlayer-std", std_hash)

    print(f"prepared {args.output} with py-genlayer:{runner_hash}")
    print(f"prepared py-lib-genlayer-std:{std_hash}")


if __name__ == "__main__":
    main()

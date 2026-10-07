#!/usr/bin/env python3
"""Fail closed unless the canonical Studionet RPC reports chain ID 61999."""

from __future__ import annotations

import json
import urllib.request

RPC = "https://studio.genlayer.com/api"
EXPECTED_CHAIN_ID = 61999


def rpc(method: str):
    payload = json.dumps(
        {"jsonrpc": "2.0", "id": 1, "method": method, "params": []}
    ).encode("utf-8")
    request = urllib.request.Request(
        RPC,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "firstrefusal-network-guard/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        body = json.loads(response.read().decode("utf-8"))
    if "error" in body:
        raise RuntimeError(f"RPC error for {method}: {body['error']}")
    return body.get("result")


def parse_chain_id(value) -> int:
    if isinstance(value, int):
        return value
    text = str(value).strip().lower()
    if text.startswith("0x"):
        return int(text, 16)
    return int(text)


def main() -> None:
    try:
        value = rpc("eth_chainId")
        actual = parse_chain_id(value)
    except Exception as first_error:
        try:
            actual = parse_chain_id(rpc("net_version"))
        except Exception as second_error:
            raise SystemExit(
                f"Could not verify Studionet chain ID. eth_chainId={first_error!r}; "
                f"net_version={second_error!r}"
            )

    if actual != EXPECTED_CHAIN_ID:
        raise SystemExit(
            f"NETWORK LOCK FAILED: expected chain ID {EXPECTED_CHAIN_ID}, got {actual}"
        )

    print(f"OK: canonical Studionet RPC {RPC}")
    print(f"OK: chain ID {actual}")
    print("Safe to continue with 61999-only deployment checks.")


if __name__ == "__main__":
    main()

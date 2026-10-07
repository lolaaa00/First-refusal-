# Deployment evidence

**Target:** stable Studionet, chain ID `61999`.

This document records only observed evidence; absent values are marked `not yet available`.

## Network verification

- RPC: `https://studio.genlayer.com/api`
- Chain ID observed independently from RPC: `61999` (`0xf22f`)
- Repository-local CLI: `0.39.1`
- CLI effective network: `studionet`, chain ID `61999`, canonical RPC
- Verification date: `2026-10-07`
- Note: the CLI's display metadata currently reports a legacy explorer URL; canonical evidence links will use `https://explorer-studio.genlayer.com`.

## Local verification

- Direct Mode: `60 passed` on Python `3.12`
- GenVM AST safety lint, `contracts/firstrefusal.py`: passed (`3 checks`)
- GenVM AST safety lint, `contracts/protected_transfer.py`: passed (`3 checks`)
- Full GenVM SDK validation: passed for both contracts using the exact legacy runner archives retained in the checksum-pinned official `genvm-manager` `v0.6.0-rc8` bundle
- Repository preflight: `31 checks passed`
- Integration harness: compiles and collects `2` environment-gated Studionet tests
- CI: passed, GitHub Actions run `37666888213` at commit `5d18e072acff57e617d730768eb511250318d5f4`

## Source record

- FirstRefusal SHA-256: `e8bbfb30651456c1ae42e4e60ddb125aee395d05cde386ef12cd321a667aa41d`
- ProtectedTransfer SHA-256: `639f2b6b8ce0466c418862a231dd558a739c6b001870972a3d59f51cc2a24b7c`
- Deployment checkpoint git HEAD: `5d18e072acff57e617d730768eb511250318d5f4`
- Deployed-source parity: exact byte equality (`41,437` bytes); local and on-chain SHA-256 both `e8bbfb30651456c1ae42e4e60ddb125aee395d05cde386ef12cd321a667aa41d`

These hashes were recomputed after the final fixture commit and verified immediately before deployment.

## Main contract

- Address: `0x4093EA34e2E346aE61B0239FAb5a2adA985f8d83`
- Deployment transaction: `0x0061ff7efbd9e05caaec0c24e3f23e9bab538ade814414764d912e3adfe127db`
- Finalized state: `ACCEPTED`, `MAJORITY_AGREE`, one consensus round
- Explorer link: not yet available
- On-chain source SHA-256: `e8bbfb30651456c1ae42e4e60ddb125aee395d05cde386ef12cd321a667aa41d`

## ProtectedTransfer consumers

No consumer has been deployed from this revision.

## Live lifecycle evidence

The covered, exact-term exercise, waiver, match-window expiry, outside-scope, unresolved-offer/expiry, serialization/race, consumer-enforcement, and live fail-closed scenarios have not yet been executed. No transaction hashes or consensus outcomes are claimed.

## Immutable public evidence

- Fixture commit: `019c8b2587b10fab430760ef01f2281617f24f2b`
- Covered fixture URL: `https://raw.githubusercontent.com/lolaaa00/First-refusal-/019c8b2587b10fab430760ef01f2281617f24f2b/fixtures/covered_offer.json`
- Outside-scope fixture URL: `https://raw.githubusercontent.com/lolaaa00/First-refusal-/019c8b2587b10fab430760ef01f2281617f24f2b/fixtures/outside_scope_offer.json`
- Both URLs were fetched after the push and contain buyer `0x7099f2f0d13a9e0c208a9e140f681334cc3d6b89` with the exact frozen terms used by the integration harness.

## External blockers as of 2026-10-07

1. Lifecycle evidence and ProtectedTransfer consumer deployments remain pending.
2. `npm audit` reports four moderate and two critical advisories in transitive development dependencies bundled by the required `genlayer@0.39.1` CLI (Vitest/Tinypool and Dockerode/UUID paths). The suggested automatic change would replace the mandated CLI version and therefore has not been applied. These packages are tooling dependencies, not contract runtime code.

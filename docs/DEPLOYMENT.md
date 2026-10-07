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

- Covered/exercise consumer: `0xa3eFf29D04e8f35A7c7971aF2400C8e9E4E81dcA`
- Deployment transaction: `0xe62426d0c4edbbb63f693f4ff8642e3136b2c2dbf6e47e27b1331d81e1befdf1`
- Bound right: `1`, definition hash `8399d737b66f0954f3cfc258071a728faddcd91c0ffd77fc345c5bba69d4ebcc`
- Exact source parity: `6,548` bytes; local and on-chain SHA-256 both `639f2b6b8ce0466c418862a231dd558a739c6b001870972a3d59f51cc2a24b7c`

## Live lifecycle evidence

Covered/exact-term exercise and consumer enforcement are complete:

- Right creation: `0x19eb36f62ae6446d03c06cfa6f435ce40c92113e584e455ea070dd9fb5fcacd9`
- Holder ratification: `0xcdd234e4da605be7df4dbcb8e0d3d49bdeb11be693de79f5d60d3d572dd2c1e4`
- Covered offer submission: `0xdfd6ea333a0e70654afef8202ba393cfc08e749e459e9aa1fc7dfe29a7e8ff06`
- Live resolution: `0xe2f664c5cf00288d56cb899f8258f31519da979b594fdde7776585e45a2b5dec` (`COVERED`, `SUPPORTS`, `MAJORITY_AGREE`)
- Expected pre-exercise consumer denial: `0x6317171fc39df45b3a8a33b46c78a17b1b16ad436c3d0f00fb8716c13f93d2a0` (`EXPECTED: FirstRefusal authorization denied`)
- Exact-term holder exercise: `0x78b87cbc35da190a82b184de3d729b8a63e4a5f483df815ec71424487654cfce`
- Authorized consumer transfer: `0x1b6abe09c5e747bdca952d0371f0ff89160dd6a18cac0377d06911217fe5f275`
- Stored transfer: seller `0xE36AEeC44999a1C347782b4459BEdd98329B9147`, buyer `0x19Fbc43de9F8dbcE33FBa7ad34e9F4eE49E565E1`, offer `1`, frozen terms hash `61f5bbce68cd8d3e54fe9ebde2f90a937e08f862a5982bbdbcb73cfd924eb67c`.

The outside-scope lifecycle now passes on Studionet with the clarified immutable fixture: finalized `OUTSIDE_SCOPE / SUPPORTS`, exact third-party authorization, and ProtectedTransfer exercise. The test runner did not emit the transaction hash, so no hash is claimed here. Waiver, match-window expiry, unresolved-offer/expiry, serialization/race, and live fail-closed scenarios remain pending.

## Immutable public evidence

- Fixture commit: `019c8b2587b10fab430760ef01f2281617f24f2b`
- Covered fixture URL: `https://raw.githubusercontent.com/lolaaa00/First-refusal-/019c8b2587b10fab430760ef01f2281617f24f2b/fixtures/covered_offer.json`
- Outside-scope fixture URL: `https://raw.githubusercontent.com/lolaaa00/First-refusal-/8f1acdde09309d0a65541aa28a7ec7a07f1c66ce/fixtures/outside_scope_offer.json`
- Both URLs were fetched after the push and contain buyer `0x7099f2f0d13a9e0c208a9e140f681334cc3d6b89` with the exact frozen terms used by the integration harness.

## External blockers as of 2026-10-07

1. Additional branch-specific ProtectedTransfer deployments and live lifecycle evidence remain pending.
2. `npm audit` reports four moderate and two critical advisories in transitive development dependencies bundled by the required `genlayer@0.39.1` CLI (Vitest/Tinypool and Dockerode/UUID paths). The suggested automatic change would replace the mandated CLI version and therefore has not been applied. These packages are tooling dependencies, not contract runtime code.

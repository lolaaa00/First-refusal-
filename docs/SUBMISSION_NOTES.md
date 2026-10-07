# FirstRefusal submission notes

FirstRefusal is a contract-only GenLayer primitive for rights of first refusal on Studionet (chain `61999`). A grantor and holder freeze an exact right definition, public-offer scope, required terms, match window, and expiry. Validators independently inspect the immutable public offer evidence and classify only evidence support and scope coverage. Ambiguous, unavailable, contradicted, or unsafe evidence fails closed.

Covered offers block the third party while the holder’s match window is open. The holder can exercise only with the exact canonical terms hash. Waiver and expiry release only the original third party under those exact terms. `ProtectedTransfer` pins the right definition hash and consumes each authorized offer once.

## Verified

- Direct Mode: 60 tests passed.
- Repository preflight: 31 checks passed.
- AST safety lint passed for both contracts.
- Required CLI: `genlayer@0.39.1`.
- CI passed: [GitHub Actions run 37666888213](https://github.com/lolaaa00/First-refusal-/actions/runs/37666888213).
- FirstRefusal deployment: `0x4093EA34e2E346aE61B0239FAb5a2adA985f8d83`.
- Covered lifecycle and ProtectedTransfer enforcement finalized successfully; transaction evidence is recorded in `docs/DEPLOYMENT.md` and `artifacts/FINAL_MANIFEST.json`.

## Final submission condition

Before submitting as fully live-proven, rerun the outside-scope lifecycle using the immutable fixture pinned in the manifest and record a finalized `OUTSIDE_SCOPE / SUPPORTS` result. Then update the manifest and deployment record with that transaction hash. Do not claim the remaining waiver and expiry branches as live-proven unless their finalized transactions are also recorded.

The implementation is fail-closed and locally verified; the current evidence package is transparent about the remaining live checkpoints.

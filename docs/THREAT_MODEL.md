# Threat model

## Assets protected

FirstRefusal protects the integrity of a right-of-first-refusal decision surface:

- the holder cannot be bypassed by changing terms after semantic resolution;
- the grantor cannot make the model choose a buyer;
- an unsupported/ambiguous source cannot authorize a transfer;
- a holder cannot exercise on cheaper or otherwise changed terms;
- a consumer cannot substitute a different right definition hash;
- a second offer cannot race an unresolved/open offer.

## Threat: malicious grantor submits a fake or misleading offer

Mitigation:

- the offer is not consequential merely because the grantor stores it;
- `resolve_offer` requires public evidence;
- validators independently re-fetch and reclassify the evidence;
- a `SUPPORTS` result requires a literal source-grounded excerpt;
- contradicted/insufficient evidence fails closed.

Residual risk:

A public source can still be false or non-authoritative. The primitive proves consensus over the observed public evidence, not legal truth.

## Threat: prompt injection in evidence

Mitigation:

- the page is treated as untrusted data in the semantic prompt;
- obvious machine-control phrases trigger deterministic quarantine before LLM analysis;
- validators independently fetch the source;
- the model has no authority to execute tools, move funds, select buyers, or write arbitrary state.

Residual risk:

The deterministic marker list is intentionally not claimed to be a complete prompt-injection detector. The bounded prompt and independent validation remain necessary.

## Threat: leader fabricates a favourable classification

Mitigation:

- custom `run_nondet_unsafe` validator;
- validators independently fetch and classify the source;
- exact bounded evidence and coverage codes must match;
- the supporting excerpt must occur in validator-fetched source and exactly match the independently selected supporting excerpt.

## Threat: holder exercises on different terms

Mitigation:

- offer terms are canonicalized deterministically;
- the holder's proposed match is canonicalized again;
- Keccak hashes must be exactly equal;
- no semantic “substantially similar” escape hatch exists.

## Threat: grantor changes buyer after holder waiver/expiry

Mitigation:

`is_transfer_authorized` binds the authorization to the original `third_party` address and exact terms hash.

A different buyer requires a new offer lifecycle.

## Threat: grantor changes terms after holder waiver/expiry

Same mitigation: the exact terms hash is pinned.

## Threat: draft right griefs the grantor

A draft is not active and does not block unencumbered transfer. Only holder ratification moves it to `ACTIVE`.

## Threat: grantor cancels a pending offer to bypass the holder

Cancelling the offer does not cancel the active right. A consumer still observes that the right encumbers unstructured transfer. The grantor must submit another valid offer path or wait for the right itself to end according to its frozen definition.

## Threat: offer is never resolved

`resolve_offer` is permissionless. The grantor does not control whether validators are asked to resolve the frozen public evidence.

## Threat: right expires while an offer is unresolved

`expire_right` refuses to finalize expiry while an active offer lock exists. Before expiry, the grantor may cancel a still-pending offer, but the active right continues to block unencumbered transfer. At or after expiry, cancellation is disabled and the pending offer must be resolved. A covered resolution can therefore create a holder match window that survives the right's nominal expiry; only after the offer reaches a protected terminal state can the right itself be expired.

## Threat: private commercial terms

Unsupported by this primitive's semantic proof path. The consensus source must be public HTTPS evidence. Do not upload confidential terms to public contract state or public web fixtures.

## Threat: consumer claims enforcement without integration

FirstRefusal has no such claim. Enforcement is only as strong as the downstream system that voluntarily checks its authorization views.

## Threat: consumer pins wrong contract/right

`ProtectedTransfer` pins the FirstRefusal address, right ID, and right definition hash at deployment. Hash mismatch fails closed.

## Threat: terminal authorization replay

`ProtectedTransfer` marks an offer ID consumed before recording the owner transition. The same terminal FirstRefusal authorization cannot be consumed again by that consumer even if the asset later cycles back to the original owner.

## Threat: legal ambiguity

The contract is a technical coordination primitive, not legal advice and not a universal statement about enforceability of ROFR clauses under any jurisdiction.

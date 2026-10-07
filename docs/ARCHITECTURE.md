# Architecture

## Primitive boundary

FirstRefusal does not sell assets, custody funds, determine legal title, or rank buyers. It maintains a reusable state machine that answers one operational question for downstream Intelligent Contracts:

> Is this exact transfer to this exact buyer under this exact frozen terms hash authorized under this exact right-of-first-refusal definition?

The main contract owns:

- immutable right definitions;
- bilateral activation by holder ratification;
- serialized third-party offers;
- canonical terms hashes;
- public evidence resolution under GenLayer consensus;
- deterministic match windows;
- exact-term holder exercise;
- holder waiver;
- deterministic release after the window;
- authorization views for consumers.

The consumer owns the asset-specific consequence.

## Separation of semantic and deterministic work

### Semantic consensus

Only `resolve_offer` enters nondeterministic execution.

Inputs are already frozen:

- right definition hash;
- asset key;
- natural-language ROFR scope;
- third-party identity;
- canonical declared terms;
- public HTTPS evidence URL.

The consensus result is bounded to evidence status and scope relation.

### Deterministic protocol

Everything after consensus is code:

- right activation;
- offer serialization;
- required term-key checks;
- terms canonicalization;
- Keccak hashing;
- holder identity;
- deadlines;
- exact-match exercise;
- waiver;
- expiry;
- authorized buyer;
- authorized terms hash;
- right-hash pinning.

## Why exact matching matters

A right-of-first-refusal primitive becomes dangerous if the model decides whether the holder's counteroffer is “commercially equivalent.” That gives the model settlement authority.

FirstRefusal avoids that entirely.

Once a covered third-party offer is frozen, the holder must submit a terms payload whose deterministic canonical hash is exactly the same as the third-party offer hash.

Semantic judgement determines whether the third-party offer triggers the right. It does not decide whether the holder matched it.

## Offer serialization

One unresolved/open offer may encumber a right at a time.

The active-offer lock is set when the grantor submits an offer, before semantic resolution. It is released only when that offer reaches a safe terminal state or when a covered offer is exercised, waived, or released. Once the right-expiry timestamp is reached, a pending offer cannot be cancelled: it must be resolved, so expiry cannot erase an unresolved claim.

This prevents two simultaneous offer windows from producing contradictory transfer authorizations.

## Fail-closed states

These states never authorize a transfer:

```text
PENDING
COVERED (while window is open)
AMBIGUOUS
UNAVAILABLE
CONTRADICTED
QUARANTINED
CANCELLED
```

Authorization exists only for:

```text
EXERCISED
  -> holder, exact terms hash

WAIVED
  -> original third party, exact terms hash

RELEASED
  -> original third party, exact terms hash

OUTSIDE_SCOPE
  -> original third party, exact terms hash
```

## Public evidence model

The source is evidence about the declared offer. It is not assumed to be legally authoritative merely because it is public.

A consumer should only rely on evidence surfaces it accepts operationally. For the reviewer demo, repository fixtures are published through an immutable commit-pinned `raw.githubusercontent.com` URL so validators inspect fixed public bytes.

## Cross-contract consumer

`ProtectedTransfer` pins:

```text
FirstRefusal address
right_id
right_hash
initial owner
```

A transfer through a resolved offer calls the main contract's view:

```text
is_transfer_authorized(...)
```

A transfer without an offer is possible only when:

```text
blocks_unencumbered_transfer(...) == false
```

The consumer records its own transfer and changes its owner. The main primitive never pretends it can reverse or control systems that do not integrate it.

Each offer authorization is consumable only once by a `ProtectedTransfer` instance. This explicit consumer-side guard prevents a terminal authorization from being replayed after later ownership changes.

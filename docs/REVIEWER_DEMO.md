# Reviewer demo

The final repository should prove **two** live 61999 lifecycles:

1. a covered offer that the holder exercises;
2. an outside-scope offer that does not trigger the right.

Do not use leader-only execution for final evidence.

It must also record independent covered-window expiry, holder waiver, pending-offer/right-expiry serialization, offer-race rejection, and one meaningful fail-closed live negative. Direct Mode evidence is not a substitute for the mandatory deployed-consumer rejection in the covered scenario.

## Network lock

Before signing:

```bash
python scripts/check_studionet.py
npm run genlayer -- network set studionet
npm run genlayer -- network info
```

The effective chain ID must be `61999` and the RPC must be:

```text
https://studio.genlayer.com/api
```

## Public fixture preparation

After the repository exists on `lolaaa00/First-refusal-`:

1. commit the fixtures;
2. push;
3. obtain that commit SHA;
4. use immutable public URLs in this form:

```text
https://raw.githubusercontent.com/lolaaa00/First-refusal-/<COMMIT_SHA>/fixtures/covered_offer.json
https://raw.githubusercontent.com/lolaaa00/First-refusal-/<COMMIT_SHA>/fixtures/outside_scope_offer.json
```

Never use an unpinned mutable branch URL as final reviewer evidence.

## Scenario A: covered offer -> holder exercises

Use three distinct accounts:

```text
A = grantor/current owner
B = ROFR holder
C = third-party buyer
```

Create the right from A:

```text
holder: B
asset_key: asset-x
scope:
  full transfer of asset-x to a third party for monetary consideration;
  temporary licences, collateral pledges, and partial interests are excluded
required term keys:
  currency
  price_minor
  settlement_days
  transfer_type
match window:
  choose a practical reviewer-demo window
expiry:
  safely in the future
```

Then:

```text
A create_right
B ratify_right
A submit_offer(C, exact covered terms, immutable covered fixture URL)
any account resolve_offer
```

Required state:

```text
right = ACTIVE
offer = COVERED
evidence = SUPPORTS
relation = COVERED
match_deadline > resolved_at
```

Before B exercises, verify:

```text
is_transfer_authorized(... buyer=C ...) == false
```

Deploy `ProtectedTransfer` pinned to the same right hash.

Attempt transfer to C during the match window. It must fail.

Then B calls:

```text
exercise(offer_id, exact original terms JSON)
```

Verify:

```text
offer = EXERCISED
is_transfer_authorized(... buyer=B, exact terms hash ...) == true
is_transfer_authorized(... buyer=C, exact terms hash ...) == false
```

Call `ProtectedTransfer.transfer_with_offer` to B and verify its recorded owner changes to B.

Also attempt a one-field-mutated terms hash and show it is denied.

## Scenario B: outside-scope offer

Use a fresh right/consumer so the first scenario's ownership transition cannot confuse the proof.

Submit the immutable `outside_scope_offer.json` fixture whose transaction is a temporary non-exclusive licence with no ownership transfer.

Resolve it.

Required state:

```text
evidence = SUPPORTS
relation = OUTSIDE_SCOPE
offer = OUTSIDE_SCOPE
```

Then show:

```text
original third-party + exact terms hash -> authorized
wrong buyer -> denied
wrong terms hash -> denied
```

## Adversarial proof

At minimum preserve finalized evidence for these properties:

- public evidence re-observation reached validator consensus;
- unsupported or ambiguous evidence does not authorize transfer;
- wrong right hash does not authorize transfer;
- holder cannot exercise with changed terms;
- third party cannot transfer while covered match window is open;
- consumer actually blocks and later permits a state transition.

## Additional live branches

Use fresh rights where state from the exercise path would otherwise obscure the result:

1. **Waiver:** grantor and third party fail to waive; holder waives; only the original third party plus exact frozen terms becomes authorized.
2. **Window expiry:** before the exact deadline the third party is denied; at the deadline the holder still has the inclusive final instant; after the deadline `expire_offer` releases only the original buyer and terms.
3. **Right expiry with pending offer:** `expire_right` and post-expiry cancellation both fail while the offer is unresolved; resolve it and complete the protected offer path before expiring the right.
4. **Serialization:** a second offer fails while the first is pending or covered, and no terminal offer can be resolved, exercised, or waived twice.
5. **Fail-closed negative:** use immutable contradictory, materially ambiguous, or clearly unsafe evidence and prove no transfer authorization results.

Record failed transaction receipts as evidence only when the explorer exposes them reliably. Otherwise record the exact read/state proof and plainly identify the limitation.

## Final source parity

After deployment:

```bash
npm run genlayer -- code <FIRSTREFUSAL_ADDRESS> > artifacts/onchain-firstrefusal.py
```

Compare normalized bytes to `contracts/firstrefusal.py` and record SHA-256 digests in `docs/DEPLOYMENT.md`.

Do the same for the consumer.

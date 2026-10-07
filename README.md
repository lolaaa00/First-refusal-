# FirstRefusal

**A reusable GenLayer Intelligent Contract primitive for enforceable rights of first refusal over semantically covered third-party offers.**

FirstRefusal is intentionally **contract-only**. There is no frontend, no dashboard, no hosted backend, and no application-specific wallet flow. The repository targets the standalone **Intelligent Contracts** category.

## What problem it solves

A right of first refusal is easy to describe and surprisingly hard to automate.

A holder may have a contractual right such as:

> If the grantor receives a bona fide third-party offer for a full transfer of Asset X for monetary consideration, the holder may match that offer before the grantor transfers the asset to the third party.

The deterministic parts are straightforward:

- who the grantor and holder are;
- the exact asset key;
- the holder's match window;
- the exact third-party terms hash;
- whether the holder matched those exact terms;
- whether the right is still active;
- which buyer is authorized after exercise, waiver, expiry, or an outside-scope determination.

The hard part is semantic:

> Does the public third-party offer actually fall inside the frozen transaction scope of the right?

FirstRefusal uses GenLayer consensus **only** for that bounded semantic boundary. Everything else is deterministic protocol logic.

## Core invariant

```text
third-party offer
      |
      v
public evidence + frozen terms + frozen ROFR scope
      |
      v
GenLayer consensus
      |
      +--> COVERED --------> holder gets exact-term match window
      |
      +--> OUTSIDE_SCOPE --> exact third-party transfer may proceed
      |
      +--> AMBIGUOUS ------> fail closed; no transfer authorization
      |
      +--> bad/unavailable evidence --> fail closed
```

If a covered offer exists, the grantor cannot obtain authorization for the third-party transfer while the holder's match window is open.

If the holder exercises, authorization flips to the holder **only for the exact frozen offer terms hash**.

If the holder waives or the match window expires, authorization flips to the originally declared third party **only for the exact frozen offer terms hash**.

A changed buyer or changed terms require a new offer path.

## Why this is not an AI deal-maker

The model cannot:

- invent a price;
- rewrite an offer;
- decide the match window;
- choose the buyer;
- grant the right;
- waive the right;
- extend the right;
- create a compromise;
- authorize a transfer by itself.

The semantic result is deliberately bounded to:

```text
EVIDENCE:
SUPPORTS | CONTRADICTS | INSUFFICIENT | UNAVAILABLE | UNSAFE

SCOPE:
COVERED | OUTSIDE_SCOPE | AMBIGUOUS
```

Only when public evidence supports the frozen declared offer can a scope result become consequential.

## Two-contract proof of reuse

`contracts/firstrefusal.py` is the reusable primitive.

`contracts/protected_transfer.py` is intentionally tiny. It proves that another Intelligent Contract can pin a specific FirstRefusal `definition_hash` and refuse its own transfer unless:

```text
is_transfer_authorized(...)
```

returns true.

The consumer also supports an unencumbered path only when:

```text
blocks_unencumbered_transfer(...)
```

returns false.

This keeps the primitive reusable: FirstRefusal does not custody the asset and does not pretend to enforce transfers in systems that have not integrated it.

The consumer records each offer authorization as consumed before changing ownership, so a terminal authorization cannot be replayed after a later owner cycle.

## Right lifecycle

```text
DRAFT
  |
  | holder ratifies
  v
ACTIVE
  |
  +--> EXPIRED
  |
  +--> offer submitted
          |
          v
       PENDING
          |
          +--> COVERED -----------+
          |                       |
          |                       +--> EXERCISED
          |                       +--> WAIVED
          |                       +--> RELEASED after match deadline
          |
          +--> OUTSIDE_SCOPE
          +--> AMBIGUOUS
          +--> UNAVAILABLE
          +--> CONTRADICTED
          +--> QUARANTINED
```

Only one unresolved/open offer may encumber a right at a time. That serialization removes race ambiguity around simultaneous offers.

## Public evidence and consensus

`resolve_offer` performs the only nondeterministic operation in the main protocol.

The leader:

1. independently fetches the frozen public HTTPS evidence URL;
2. rejects obvious machine-control/prompt-injection language before semantic analysis;
3. checks whether the source supports the exact declared offer facts and terms;
4. if supported, classifies the offer against the frozen ROFR scope;
5. returns bounded status codes plus a short source-grounded excerpt.

The validator does **not** check JSON shape and accept the leader.

Each validator independently re-fetches the same public source, independently re-runs the bounded analysis, requires the evidence status and coverage relation to match, and requires the leader's supporting excerpt to both exist in the validator-fetched source and equal the validator's independently selected excerpt.

If validators cannot independently reproduce the substantive classification, consensus does not settle it.

## Exact-term matching

Offer terms are restricted to a flat JSON object containing string, integer, or boolean values.

Keys are normalized and sorted deterministically. The canonical JSON is hashed with Keccak-256.

A holder exercises with `matching_terms_json`. The contract independently canonicalizes and hashes those terms. If the hash differs by even one term, exercise reverts.

This means the LLM never determines whether the holder's counteroffer is “close enough.” It must be the exact frozen terms payload.

## Security boundaries

FirstRefusal deliberately does **not** claim that:

- every commercial offer can be made public;
- a URL is authoritative merely because it is HTTPS;
- public evidence proves legal enforceability in every jurisdiction;
- a consumer contract can reverse an off-chain transfer;
- the primitive can force systems that did not integrate it to obey the right;
- `OUTSIDE_SCOPE` is appropriate when the evidence itself is ambiguous or unsupported.

Ambiguous, unavailable, contradicted, or unsafe evidence fails closed.

See `docs/THREAT_MODEL.md`.

## Stable Studionet target

This repository is locked to **Studionet chain ID 61999**.

| Setting | Value |
|---|---|
| Network | Studionet |
| Chain ID | `61999` / `0xF22F` |
| RPC | `https://studio.genlayer.com/api` |
| Explorer | `https://explorer-studio.genlayer.com` |
| Currency | GEN |
| CLI | repository-pinned `genlayer@0.39.1` |

The repository contains no alternate deployment profile. `scripts/check_studionet.py` fails if the configured RPC does not report chain ID 61999.

## Repository layout

```text
contracts/
  firstrefusal.py
  protected_transfer.py

tests/direct/
  test_firstrefusal.py
  test_protected_transfer_source.py

tests/integration/
  test_studionet_lifecycle.py

fixtures/
  covered_offer.json
  outside_scope_offer.json

docs/
  ARCHITECTURE.md
  THREAT_MODEL.md
  REVIEWER_DEMO.md
  DEPLOYMENT.md
  SUBMISSION_NOTES_DRAFT.md

scripts/
  check_studionet.py
  preflight.py
  make_manifest.py

FIRSTREFUSAL_CODEX_HANDOFF.txt
```

## Local verification

Use Python 3.12+.

```bash
python -m venv .venv
source .venv/bin/activate              # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

npm install
npm run genlayer -- --version          # must report 0.39.1

python scripts/preflight.py
genvm-lint check contracts/firstrefusal.py
genvm-lint check contracts/protected_transfer.py
pytest tests/direct -v
```

Direct Mode requires no Docker.

## Studionet verification

Before any signing or deployment:

```bash
python scripts/check_studionet.py
npm run genlayer -- network set studionet
npm run genlayer -- network info
```

Both checks must identify chain ID `61999`.

Then deploy only after Direct Mode and lint are green:

```bash
npm run genlayer -- deploy --contract contracts/firstrefusal.py --rpc https://studio.genlayer.com/api
```

After the main contract is deployed and a right is created, deploy `protected_transfer.py` with the FirstRefusal address, right ID, right hash, and initial owner.

The final agent must execute the funded live lifecycle in `docs/REVIEWER_DEMO.md`, record finalized explorer evidence in `docs/DEPLOYMENT.md`, and verify deployed-source parity with `genlayer code` before submission.

## No fabricated deployment evidence

This ZIP is a pre-deployment package. `docs/DEPLOYMENT.md` intentionally contains placeholders rather than invented transaction hashes or addresses.

## License

MIT

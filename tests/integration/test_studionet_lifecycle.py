"""Funded 61999-only lifecycle proof for FirstRefusal.

This file is intentionally environment-gated because the final public fixture
must contain the real funded third-party address and then be pinned to an
immutable repository commit before live consensus is executed.
"""

import json
import os
import re
import time

import pytest

from gltest import get_accounts, get_contract_factory
from gltest.assertions import tx_execution_failed, tx_execution_succeeded


FIRSTREFUSAL = "contracts/firstrefusal.py"
PROTECTED = "contracts/protected_transfer.py"
RUN = os.environ.get("RUN_STUDIONET") == "1"
COVERED_URL = os.environ.get("PUBLIC_COVERED_OFFER_URL", "")
OUTSIDE_URL = os.environ.get("PUBLIC_OUTSIDE_SCOPE_OFFER_URL", "")

TERMS = json.dumps(
    {
        "price_minor": 8000,
        "currency": "GEN",
        "transfer_type": "full transfer",
        "settlement_days": 2,
    }
)
REQUIRED = json.dumps(["price_minor", "currency", "transfer_type", "settlement_days"])
SCOPE = (
    "This right covers a full transfer of asset asset-x to a third party for monetary "
    "consideration. It does not cover a temporary licence, collateral pledge, or partial interest."
)

TX_KW = {
    "consensus_max_rotations": 3,
    "wait_until": "finalized",
    "wait_interval": 10000,
    "wait_retries": 60,
}



def assert_pinned_fixture(url: str, filename: str) -> None:
    pattern = rf"^https://raw\.githubusercontent\.com/lolaaa00/First-refusal-/[0-9a-fA-F]{{40}}/fixtures/{re.escape(filename)}$"
    if re.match(pattern, url) is None:
        pytest.fail(
            f"{filename} URL must use an immutable 40-hex commit-pinned lolaaa00/First-refusal- raw URL"
        )


def tx(function):
    return function.transact(**TX_KW)


def ok(receipt):
    assert tx_execution_succeeded(receipt), receipt


@pytest.mark.skipif(not RUN, reason="set RUN_STUDIONET=1 for funded Studionet lifecycle")
def test_covered_offer_exercise_and_consumer_gate():
    assert_pinned_fixture(COVERED_URL, "covered_offer.json")

    accounts = get_accounts()
    if len(accounts) < 3:
        pytest.skip("configure at least three funded Studionet accounts: grantor, holder, third party")
    grantor, holder, third_party = accounts[:3]

    factory = get_contract_factory(contract_file_path=FIRSTREFUSAL)
    first = factory.deploy(account=grantor, **TX_KW)
    assert first.address

    expiry = int(time.time()) + 30 * 24 * 60 * 60
    ok(tx(first.create_right(
        args=[holder.address, "Asset X ROFR", "asset-x", SCOPE, REQUIRED, 3600, expiry],
        account=grantor,
    )))
    right_id = 1
    right = first.get_right(args=[right_id]).call()
    assert right["status_name"] == "DRAFT"

    ok(tx(first.ratify_right(args=[right_id], account=holder)))
    right = first.get_right(args=[right_id]).call()
    assert right["status_name"] == "ACTIVE"
    right_hash = right["definition_hash"]

    ok(tx(first.submit_offer(
        args=[right_id, third_party.address, TERMS, COVERED_URL],
        account=grantor,
    )))
    offer_id = 1
    ok(tx(first.resolve_offer(args=[offer_id], account=grantor)))
    offer = first.get_offer(args=[offer_id]).call()
    assert offer["status_name"] == "COVERED", offer
    assert offer["evidence_status_name"] == "SUPPORTS", offer
    assert offer["relation_name"] == "COVERED", offer

    consumer_factory = get_contract_factory(contract_file_path=PROTECTED)
    consumer = consumer_factory.deploy(
        args=[first.address, right_id, right_hash, grantor.address],
        account=grantor,
        **TX_KW,
    )
    assert consumer.address

    denied = tx(consumer.transfer_with_offer(
        args=[offer_id, third_party.address, offer["terms_hash"], "11" * 32],
        account=grantor,
    ))
    assert tx_execution_failed(denied), denied
    assert consumer.get_owner().call().lower() == grantor.address.lower()

    ok(tx(first.exercise(args=[offer_id, TERMS], account=holder)))
    exercised = first.get_offer(args=[offer_id]).call()
    assert exercised["status_name"] == "EXERCISED"

    ok(tx(consumer.transfer_with_offer(
        args=[offer_id, holder.address, offer["terms_hash"], "22" * 32],
        account=grantor,
    )))
    assert consumer.get_owner().call().lower() == holder.address.lower()


@pytest.mark.skipif(not RUN, reason="set RUN_STUDIONET=1 for funded Studionet lifecycle")
def test_outside_scope_offer_releases_only_exact_third_party_terms():
    assert_pinned_fixture(OUTSIDE_URL, "outside_scope_offer.json")

    accounts = get_accounts()
    if len(accounts) < 3:
        pytest.skip("configure at least three funded Studionet accounts: grantor, holder, third party")
    grantor, holder, third_party = accounts[:3]

    factory = get_contract_factory(contract_file_path=FIRSTREFUSAL)
    first = factory.deploy(account=grantor, **TX_KW)
    assert first.address

    expiry = int(time.time()) + 30 * 24 * 60 * 60
    ok(tx(first.create_right(
        args=[holder.address, "Asset X ROFR", "asset-x", SCOPE, REQUIRED, 3600, expiry],
        account=grantor,
    )))
    right_id = 1
    ok(tx(first.ratify_right(args=[right_id], account=holder)))
    right = first.get_right(args=[right_id]).call()
    right_hash = right["definition_hash"]

    outside_terms = json.dumps(
        {
            "price_minor": 8000,
            "currency": "GEN",
            "transfer_type": "temporary licence",
            "settlement_days": 2,
        }
    )
    ok(tx(first.submit_offer(
        args=[right_id, third_party.address, outside_terms, OUTSIDE_URL],
        account=grantor,
    )))
    offer_id = 1
    ok(tx(first.resolve_offer(args=[offer_id], account=grantor)))
    offer = first.get_offer(args=[offer_id]).call()
    assert offer["status_name"] == "OUTSIDE_SCOPE", offer
    assert offer["evidence_status_name"] == "SUPPORTS", offer
    assert offer["relation_name"] == "OUTSIDE_SCOPE", offer

    assert first.is_transfer_authorized(
        args=[right_id, offer_id, right_hash, third_party.address, offer["terms_hash"]]
    ).call() is True
    assert first.is_transfer_authorized(
        args=[right_id, offer_id, right_hash, holder.address, offer["terms_hash"]]
    ).call() is False
    assert first.is_transfer_authorized(
        args=[right_id, offer_id, right_hash, third_party.address, "00" * 32]
    ).call() is False

    consumer_factory = get_contract_factory(contract_file_path=PROTECTED)
    consumer = consumer_factory.deploy(
        args=[first.address, right_id, right_hash, grantor.address],
        account=grantor,
        **TX_KW,
    )
    ok(tx(consumer.transfer_with_offer(
        args=[offer_id, third_party.address, offer["terms_hash"], "33" * 32],
        account=grantor,
    )))
    assert consumer.get_owner().call().lower() == third_party.address.lower()

"""Direct Mode adversarial tests for the enforcing consumer contract."""

import pytest


CONTRACT = "contracts/protected_transfer.py"
RIGHT_HASH = "11" * 32
TERMS_HASH = "22" * 32
TRANSFER_HASH = "33" * 32


def install_authorization_hook(vm, authorized=True, blocks=False):
    from genlayer.py import calldata
    from genlayer.py.public_abi import ResultCode

    calls = []

    def hook(_vm, request):
        if "CallContract" not in request:
            return None
        call = request["CallContract"]
        calls.append(call)
        method = call["calldata"]["method"]
        if method == "is_transfer_authorized":
            value = authorized
        elif method == "blocks_unencumbered_transfer":
            value = blocks
        else:
            raise AssertionError(f"unexpected cross-contract method: {method}")
        return bytes([int(ResultCode.RETURN)]) + calldata.encode(value)

    vm._gl_call_hook = hook
    return calls


def deploy_consumer(direct_vm, direct_deploy, owner):
    direct_vm.sender = owner
    return direct_deploy(CONTRACT, bytes.fromhex("44" * 20), 7, RIGHT_HASH, owner)


def test_constructor_rejects_zero_addresses_and_bad_right_hash(
    direct_vm, direct_deploy, direct_alice
):
    direct_vm.sender = direct_alice
    zero = bytes(20)
    nonzero = bytes.fromhex("44" * 20)
    with direct_vm.expect_revert("zero address"):
        direct_deploy(CONTRACT, zero, 7, RIGHT_HASH, direct_alice)


@pytest.mark.parametrize("bad_hash", ["", "AA" * 32, "0" * 63, "g" * 64])
def test_constructor_rejects_malformed_right_hash(
    bad_hash, direct_vm, direct_deploy, direct_alice
):
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("right_hash"):
        direct_deploy(CONTRACT, bytes.fromhex("44" * 20), 7, bad_hash, direct_alice)


def test_authorized_offer_transfer_changes_owner_and_forwards_exact_binding(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    consumer = deploy_consumer(direct_vm, direct_deploy, direct_alice)
    calls = install_authorization_hook(direct_vm, authorized=True)
    consumer.transfer_with_offer(9, direct_bob, TERMS_HASH, TRANSFER_HASH)
    assert consumer.get_owner().lower() == "0x" + direct_bob.hex()
    assert calls[0]["calldata"]["args"][0:3] == [7, 9, RIGHT_HASH]
    assert calls[0]["calldata"]["args"][4] == TERMS_HASH
    receipt = consumer.get_transfer(1)
    assert receipt["offer_id"] == 9
    assert receipt["terms_hash"] == TERMS_HASH


def test_denied_authorization_cannot_change_consumer_state(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    consumer = deploy_consumer(direct_vm, direct_deploy, direct_alice)
    install_authorization_hook(direct_vm, authorized=False)
    with direct_vm.expect_revert("authorization denied"):
        consumer.transfer_with_offer(9, direct_bob, TERMS_HASH, TRANSFER_HASH)
    assert consumer.get_owner().lower() == "0x" + direct_alice.hex()


def test_only_current_owner_can_transfer_and_zero_or_self_buyer_fails(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    consumer = deploy_consumer(direct_vm, direct_deploy, direct_alice)
    install_authorization_hook(direct_vm, authorized=True)
    with direct_vm.prank(direct_bob):
        with direct_vm.expect_revert("only current owner"):
            consumer.transfer_with_offer(9, direct_bob, TERMS_HASH, TRANSFER_HASH)
    with direct_vm.expect_revert("invalid buyer"):
        consumer.transfer_with_offer(9, bytes(20), TERMS_HASH, TRANSFER_HASH)
    with direct_vm.expect_revert("invalid buyer"):
        consumer.transfer_with_offer(9, direct_alice, TERMS_HASH, TRANSFER_HASH)


@pytest.mark.parametrize("field", ["terms", "transfer"])
def test_malformed_hashes_fail_before_cross_contract_call(
    field, direct_vm, direct_deploy, direct_alice, direct_bob
):
    consumer = deploy_consumer(direct_vm, direct_deploy, direct_alice)
    calls = install_authorization_hook(direct_vm, authorized=True)
    terms = "AA" * 32 if field == "terms" else TERMS_HASH
    transfer = "short" if field == "transfer" else TRANSFER_HASH
    with direct_vm.expect_revert("lowercase 32-byte hex"):
        consumer.transfer_with_offer(9, direct_bob, terms, transfer)
    assert calls == []


def test_offer_authorization_is_consumed_once_even_after_owner_cycle(
    direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie
):
    consumer = deploy_consumer(direct_vm, direct_deploy, direct_alice)
    install_authorization_hook(direct_vm, authorized=True, blocks=False)
    consumer.transfer_with_offer(9, direct_bob, TERMS_HASH, TRANSFER_HASH)
    with direct_vm.prank(direct_bob):
        consumer.transfer_after_right_ends(direct_charlie, "55" * 32)
    with direct_vm.prank(direct_charlie):
        consumer.transfer_after_right_ends(direct_alice, "66" * 32)
    with direct_vm.expect_revert("already consumed"):
        consumer.transfer_with_offer(9, direct_bob, TERMS_HASH, "77" * 32)
    assert consumer.get_owner().lower() == "0x" + direct_alice.hex()


def test_unencumbered_transfer_requires_explicit_nonblocking_answer(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    consumer = deploy_consumer(direct_vm, direct_deploy, direct_alice)
    install_authorization_hook(direct_vm, blocks=True)
    with direct_vm.expect_revert("right still encumbers"):
        consumer.transfer_after_right_ends(direct_bob, TRANSFER_HASH)
    assert consumer.get_owner().lower() == "0x" + direct_alice.hex()


def test_unencumbered_transfer_succeeds_only_when_primitive_reports_clear(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    consumer = deploy_consumer(direct_vm, direct_deploy, direct_alice)
    calls = install_authorization_hook(direct_vm, blocks=False)
    consumer.transfer_after_right_ends(direct_bob, TRANSFER_HASH)
    assert consumer.get_owner().lower() == "0x" + direct_bob.hex()
    assert calls[0]["calldata"]["method"] == "blocks_unencumbered_transfer"
    assert calls[0]["calldata"]["args"] == [7, RIGHT_HASH]

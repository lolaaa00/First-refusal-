# v0.1.0
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *

import typing
from dataclasses import dataclass


ERR_EXPECTED = "EXPECTED"
ZERO_ADDRESS = Address("0x0000000000000000000000000000000000000000")


def as_address(value: typing.Any) -> Address:
    if isinstance(value, Address):
        return value
    return Address(value)


@gl.contract_interface
class IFirstRefusal:
    class View:
        def is_transfer_authorized(
            self,
            right_id: u256,
            offer_id: u256,
            expected_right_hash: str,
            buyer: Address,
            terms_hash: str,
        ) -> bool: ...

        def blocks_unencumbered_transfer(
            self,
            right_id: u256,
            expected_right_hash: str,
        ) -> bool: ...

    class Write:
        pass


@allow_storage
@dataclass
class TransferReceipt:
    seller: Address
    buyer: Address
    offer_id: u256
    terms_hash: str
    transfer_hash: str


class ProtectedTransfer(gl.Contract):
    """Minimal consumer proving that FirstRefusal can gate an actual transfer."""

    firstrefusal_address: Address
    right_id: u256
    right_hash: str
    current_owner: Address
    transfers: TreeMap[u256, TransferReceipt]
    consumed_offers: TreeMap[u256, bool]
    transfer_count: u256

    def __init__(
        self,
        firstrefusal_address: Address,
        right_id: u256,
        right_hash: str,
        initial_owner: Address,
    ):
        firstrefusal_address = as_address(firstrefusal_address)
        initial_owner = as_address(initial_owner)
        if firstrefusal_address == ZERO_ADDRESS or initial_owner == ZERO_ADDRESS:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: zero address")
        raw_hash = str(right_hash).strip()
        normalized_hash = raw_hash.lower()
        if raw_hash != normalized_hash:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: right_hash must be lowercase 32-byte hex")
        if len(normalized_hash) != 64 or any(c not in "0123456789abcdef" for c in normalized_hash):
            raise gl.vm.UserError(f"{ERR_EXPECTED}: right_hash must be lowercase 32-byte hex")
        self.firstrefusal_address = firstrefusal_address
        self.right_id = right_id
        self.right_hash = normalized_hash
        self.current_owner = initial_owner
        self.transfer_count = u256(0)

    @gl.public.write
    def transfer_with_offer(
        self,
        offer_id: u256,
        buyer: Address,
        terms_hash: str,
        transfer_hash: str,
    ) -> None:
        if as_address(gl.message.sender_address) != self.current_owner:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: only current owner may transfer")
        buyer = as_address(buyer)
        if buyer == ZERO_ADDRESS or buyer == self.current_owner:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: invalid buyer")
        if bool(self.consumed_offers.get(offer_id)):
            raise gl.vm.UserError(f"{ERR_EXPECTED}: offer authorization already consumed")

        raw_terms = str(terms_hash).strip()
        raw_transfer = str(transfer_hash).strip()
        terms_digest = raw_terms.lower()
        transfer_digest = raw_transfer.lower()
        for label, raw_value, value in (
            ("terms_hash", raw_terms, terms_digest),
            ("transfer_hash", raw_transfer, transfer_digest),
        ):
            if raw_value != value:
                raise gl.vm.UserError(f"{ERR_EXPECTED}: {label} must be lowercase 32-byte hex")
            if len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
                raise gl.vm.UserError(f"{ERR_EXPECTED}: {label} must be lowercase 32-byte hex")

        firstrefusal = IFirstRefusal(self.firstrefusal_address)
        if not firstrefusal.view().is_transfer_authorized(
            self.right_id,
            offer_id,
            self.right_hash,
            buyer,
            terms_digest,
        ):
            raise gl.vm.UserError(f"{ERR_EXPECTED}: FirstRefusal authorization denied")

        self.consumed_offers[offer_id] = True
        self._record_transfer(offer_id, buyer, terms_digest, transfer_digest)

    @gl.public.write
    def transfer_after_right_ends(
        self,
        buyer: Address,
        transfer_hash: str,
    ) -> None:
        if as_address(gl.message.sender_address) != self.current_owner:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: only current owner may transfer")
        buyer = as_address(buyer)
        if buyer == ZERO_ADDRESS or buyer == self.current_owner:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: invalid buyer")
        raw_digest = str(transfer_hash).strip()
        digest = raw_digest.lower()
        if raw_digest != digest:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: transfer_hash must be lowercase 32-byte hex")
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise gl.vm.UserError(f"{ERR_EXPECTED}: transfer_hash must be lowercase 32-byte hex")

        firstrefusal = IFirstRefusal(self.firstrefusal_address)
        if firstrefusal.view().blocks_unencumbered_transfer(
            self.right_id,
            self.right_hash,
        ):
            raise gl.vm.UserError(f"{ERR_EXPECTED}: right still encumbers this transfer")

        self._record_transfer(u256(0), buyer, "", digest)

    def _record_transfer(
        self,
        offer_id: u256,
        buyer: Address,
        terms_hash: str,
        transfer_hash: str,
    ) -> None:
        seller = self.current_owner
        self.transfer_count = u256(int(self.transfer_count) + 1)
        receipt = self.transfers.get_or_insert_default(self.transfer_count)
        receipt.seller = seller
        receipt.buyer = buyer
        receipt.offer_id = offer_id
        receipt.terms_hash = str(terms_hash)
        receipt.transfer_hash = str(transfer_hash)
        self.current_owner = buyer

    @gl.public.view
    def get_owner(self) -> str:
        return str(self.current_owner)

    @gl.public.view
    def get_transfer(self, transfer_id: u256) -> dict[str, typing.Any]:
        receipt = self.transfers.get(transfer_id)
        if receipt is None:
            raise gl.vm.UserError(f"{ERR_EXPECTED}: unknown transfer")
        return {
            "seller": str(receipt.seller),
            "buyer": str(receipt.buyer),
            "offer_id": int(receipt.offer_id),
            "terms_hash": str(receipt.terms_hash),
            "transfer_hash": str(receipt.transfer_hash),
        }

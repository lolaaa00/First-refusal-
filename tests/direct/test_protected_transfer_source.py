"""Static source checks for the tiny consumer contract.

Direct Mode cross-contract mocking differs across testing-suite versions, so the
live handoff must add a real Studionet consumer lifecycle. This file still makes
sure the checked-in example retains the expected fail-closed call boundary.
"""

from pathlib import Path


def test_consumer_pins_right_hash_and_calls_authorization():
    source = Path("contracts/protected_transfer.py").read_text(encoding="utf-8")
    assert "is_transfer_authorized" in source
    assert "blocks_unencumbered_transfer" in source
    assert "self.right_hash" in source
    assert "FirstRefusal authorization denied" in source
    assert "right still encumbers this transfer" in source

from pathlib import Path

import pytest

from control_plane.durable_effects import DurableEffectJournal, JournalEffectState


@pytest.mark.parametrize(
    "states, expected",
    [
        ([JournalEffectState.AUTHORIZED], JournalEffectState.AUTHORIZED),
        ([JournalEffectState.AUTHORIZED, JournalEffectState.PREPARED], JournalEffectState.PREPARED),
        ([JournalEffectState.AUTHORIZED, JournalEffectState.PREPARED, JournalEffectState.FAILED], JournalEffectState.FAILED),
        ([JournalEffectState.AUTHORIZED, JournalEffectState.PREPARED, JournalEffectState.UNKNOWN], JournalEffectState.UNKNOWN),
        ([JournalEffectState.AUTHORIZED, JournalEffectState.REVOKED], JournalEffectState.REVOKED),
        ([JournalEffectState.AUTHORIZED, JournalEffectState.PREPARED, JournalEffectState.COMMITTED], JournalEffectState.COMMITTED),
    ],
)
def test_latest_state_survives_restart(tmp_path: Path, states, expected):
    path = tmp_path / "effects.jsonl"
    journal = DurableEffectJournal(path)
    for state in states:
        journal.append("effect-1", "lease-1", state)

    recovered = DurableEffectJournal(path)
    assert recovered.get("effect-1").state is expected


def test_unknown_requires_reconciliation_state(tmp_path: Path):
    path = tmp_path / "effects.jsonl"
    journal = DurableEffectJournal(path)
    journal.append("effect-1", "lease-1", JournalEffectState.AUTHORIZED)
    journal.append("effect-1", "lease-1", JournalEffectState.PREPARED)
    journal.append("effect-1", "lease-1", JournalEffectState.UNKNOWN)

    recovered = DurableEffectJournal(path)
    assert recovered.unresolved()[0].state is JournalEffectState.UNKNOWN

    # Recovery must not manufacture permission by itself.
    assert recovered.get("effect-1").state is not JournalEffectState.AUTHORIZED


def test_duplicate_effect_identity_remains_single_logical_record(tmp_path: Path):
    path = tmp_path / "effects.jsonl"
    journal = DurableEffectJournal(path)
    journal.append("effect-1", "lease-1", JournalEffectState.AUTHORIZED)

    with pytest.raises(ValueError):
        journal.append("effect-1", "lease-2", JournalEffectState.AUTHORIZED)

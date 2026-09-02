from pathlib import Path

import pytest

from control_plane.durable_effects import DurableEffectJournal, JournalEffectState


def test_effect_state_survives_reopen(tmp_path: Path):
    path = tmp_path / "effects.jsonl"
    journal = DurableEffectJournal(path)

    journal.append("effect-1", "lease-1", JournalEffectState.AUTHORIZED)
    journal.append("effect-1", "lease-1", JournalEffectState.PREPARED)
    journal.append("effect-1", "lease-1", JournalEffectState.UNKNOWN)

    recovered = DurableEffectJournal(path)
    record = recovered.get("effect-1")

    assert record.state is JournalEffectState.UNKNOWN
    assert recovered.unresolved()[0].effect_key == "effect-1"
    assert recovered.verify_integrity() is True


def test_unknown_cannot_be_blindly_reauthorized(tmp_path: Path):
    journal = DurableEffectJournal(tmp_path / "effects.jsonl")
    journal.append("effect-1", "lease-1", JournalEffectState.AUTHORIZED)
    journal.append("effect-1", "lease-1", JournalEffectState.PREPARED)
    journal.append("effect-1", "lease-1", JournalEffectState.UNKNOWN)

    with pytest.raises(ValueError, match="invalid effect transition"):
        journal.append("effect-1", "lease-1", JournalEffectState.AUTHORIZED)


def test_terminal_states_cannot_transition(tmp_path: Path):
    journal = DurableEffectJournal(tmp_path / "effects.jsonl")
    journal.append("effect-1", "lease-1", JournalEffectState.AUTHORIZED)
    journal.append("effect-1", "lease-1", JournalEffectState.PREPARED)
    journal.append("effect-1", "lease-1", JournalEffectState.FAILED)

    with pytest.raises(ValueError, match="invalid effect transition"):
        journal.append("effect-1", "lease-1", JournalEffectState.COMMITTED)


def test_non_monotonic_sequence_is_rejected(tmp_path: Path):
    path = tmp_path / "effects.jsonl"
    journal = DurableEffectJournal(path)
    journal.append("effect-1", "lease-1", JournalEffectState.AUTHORIZED)
    journal.append("effect-1", "lease-1", JournalEffectState.PREPARED)

    lines = path.read_text(encoding="utf-8").splitlines()
    lines[1] = lines[1].replace('"sequence": 2', '"sequence": 1')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="non-monotonic journal sequence"):
        DurableEffectJournal(path)


def test_hash_tampering_is_rejected(tmp_path: Path):
    path = tmp_path / "effects.jsonl"
    journal = DurableEffectJournal(path)
    journal.append("effect-1", "lease-1", JournalEffectState.AUTHORIZED)
    journal.append("effect-1", "lease-1", JournalEffectState.PREPARED)

    lines = path.read_text(encoding="utf-8").splitlines()
    lines[1] = lines[1].replace('"state": "PREPARED"', '"state": "UNKNOWN"')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="journal integrity check failed"):
        DurableEffectJournal(path)


def test_effect_identity_cannot_rebind_to_another_lease(tmp_path: Path):
    journal = DurableEffectJournal(tmp_path / "effects.jsonl")
    journal.append("effect-1", "lease-1", JournalEffectState.AUTHORIZED)

    with pytest.raises(ValueError, match="rebound to another lease"):
        journal.append("effect-1", "lease-2", JournalEffectState.PREPARED)

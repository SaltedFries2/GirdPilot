"""Illustrative tests; the prototype has not been verified in CI."""
from pathlib import Path
from gridpilot.validation import validate

BASE = Path(__file__).resolve().parents[1]
REF = BASE / "examples" / "signals.json"


def test_valid_mapping():
    assert validate(BASE / "examples" / "bess_valid.icd", REF) == []


def test_swapped_mapping():
    issues = validate(BASE / "examples" / "bess_swapped.icd", REF)
    assert any("Ind76" in issue for issue in issues)
    assert any("Ind77" in issue for issue in issues)

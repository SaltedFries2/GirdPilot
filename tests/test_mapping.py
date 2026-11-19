"""Illustrative tests; the prototype has not been verified in CI."""
from pathlib import Path

import pytest

from gridpilot.events import scenario, scenario_names
from gridpilot.validation import model_errors, validate

BASE = Path(__file__).resolve().parents[1]
REF = BASE / "examples" / "signals.json"
FIXTURES = BASE / "examples" / "fixtures"


def test_valid_mapping():
    assert validate(BASE / "examples" / "bess_valid.icd", REF) == []


def test_swapped_mapping():
    issues = validate(BASE / "examples" / "bess_swapped.icd", REF)
    assert any("Ind76" in issue for issue in issues)
    assert any("Ind77" in issue for issue in issues)


def test_missing_fcda_entry():
    """The fixture dataset lacks the third FCDA declared by the reference."""
    issues = validate(FIXTURES / "missing_fcda.icd", FIXTURES / "dc_overvoltage.json")
    assert any("length mismatch" in issue for issue in issues)
    assert any("Missing position 2" in issue for issue in issues)


def test_dangling_ggio_reference():
    issues = model_errors(FIXTURES / "dangling_ggio.icd")
    assert any("undeclared logical node" in issue for issue in issues)


@pytest.mark.parametrize("name", [
    "breaker_status", "dc_overvoltage", "bms_warning", "inverter_fault",
])
def test_fixture_mappings_valid(name):
    assert validate(FIXTURES / f"{name}.icd", FIXTURES / f"{name}.json") == []
    assert model_errors(FIXTURES / f"{name}.icd") == []


def test_simulator_scenarios_are_deterministic():
    assert scenario_names() == ["bms-warning", "breaker-status", "dc-overvoltage", "inverter-fault"]
    for name in scenario_names():
        assert scenario(name) == scenario(name)
        assert all(e.time_ms >= 0 for e in scenario(name))

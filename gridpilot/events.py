"""Deterministic synthetic BESS event source; does not transmit network packets.

Each scenario is a fixed list of state transitions with explicit event
timestamps, so repeated runs always produce identical output.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class BessEvent:
    time_ms: int
    signal: str
    value: bool
    description: str


# name -> (description, [(time_ms, signal, value, description), ...])
_SCENARIOS: dict[str, tuple[str, list[tuple[int, str, bool, str]]]] = {
    "dc-overvoltage": ("DC bus overvoltage and breaker trip", [
        (0, "DC_OVER_VOLTAGE", False, "Nominal DC bus"),
        (125, "DC_OVER_VOLTAGE", True, "Injected DC overvoltage"),
        (128, "BREAKER_TRIP", True, "Protection trip commanded"),
        (500, "DC_OVER_VOLTAGE", False, "Fault cleared"),
    ]),
    "breaker-status": ("Breaker open/close state transitions", [
        (0, "BREAKER_OPEN", False, "Breaker closed, current flowing"),
        (50, "BREAKER_OPEN", True, "Breaker opened by dispatcher command"),
        (60, "BREAKER_CLOSED", False, "Closed indication follows open"),
        (800, "BREAKER_OPEN", False, "Breaker reclosed"),
        (810, "BREAKER_CLOSED", True, "Closed indication restored"),
    ]),
    "bms-warning": ("BMS cell overtemperature escalation", [
        (0, "BMS_CELL_OVERTEMP", False, "Cell temperatures nominal"),
        (200, "BMS_CELL_OVERTEMP", True, "Cell 14 exceeds warning threshold"),
        (450, "BMS_CELL_UNDERVOLT", True, "Adjacent pack sags under load"),
        (900, "BMS_CELL_OVERTEMP", False, "Cooling brings temperature back"),
        (950, "BMS_CELL_UNDERVOLT", False, "Pack voltage recovers"),
    ]),
    "inverter-fault": ("Inverter overcurrent trip and restart", [
        (0, "INV_OVERCURRENT", False, "Inverter current within limits"),
        (100, "INV_OVERCURRENT", True, "Grid-side overcurrent detected"),
        (105, "INV_GRID_LOSS", True, "Inverter disconnects from grid"),
        (1200, "INV_OVERCURRENT", False, "Fault current decays"),
        (1500, "INV_GRID_LOSS", False, "Inverter resynchronizes"),
    ]),
}


def scenario_names() -> list[str]:
    return sorted(_SCENARIOS)


def scenario(name: str = "dc-overvoltage") -> list[BessEvent]:
    if name not in _SCENARIOS:
        raise ValueError(f"Unknown scenario: {name} (available: {', '.join(scenario_names())})")
    return [BessEvent(*transition) for transition in _SCENARIOS[name][1]]

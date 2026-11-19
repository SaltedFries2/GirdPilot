"""Deterministic synthetic BESS event source; does not transmit network packets."""
from dataclasses import dataclass


@dataclass(frozen=True)
class BessEvent:
    time_ms: int
    signal: str
    value: bool
    description: str


def scenario(name: str = "dc-overvoltage") -> list[BessEvent]:
    if name != "dc-overvoltage":
        raise ValueError(f"Unknown scenario: {name}")
    return [
        BessEvent(0, "DC_OVER_VOLTAGE", False, "Nominal DC bus"),
        BessEvent(125, "DC_OVER_VOLTAGE", True, "Injected DC overvoltage"),
        BessEvent(128, "BREAKER_TRIP", True, "Protection trip commanded"),
        BessEvent(500, "DC_OVER_VOLTAGE", False, "Fault cleared"),
    ]

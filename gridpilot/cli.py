"""GridPilot prototype command line."""
import argparse
import json
import sys
from .events import scenario, scenario_names
from .validation import validate_full


def run_validate(icd: str, reference: str, as_json: bool) -> int:
    errors = validate_full(icd, reference)
    if as_json:
        print(json.dumps({
            "tool": "gridpilot",
            "icd": icd,
            "reference": reference,
            "result": "PASS" if not errors else "FAIL",
            "errors": errors,
        }, indent=2))
    else:
        print("GridPilot SCL mapping validation")
        print(f"  ICD:       {icd}")
        print(f"  Reference: {reference}")
        if errors:
            print(f"  Found {len(errors)} problem(s):")
            for i, error in enumerate(errors, 1):
                print(f"    {i}. ERROR: {error}")
        else:
            print("  No mapping problems found.")
        print(f"RESULT: {'FAIL' if errors else 'PASS'}")
    return 1 if errors else 0


def run_simulate(name: str, as_json: bool) -> int:
    events = scenario(name)
    if as_json:
        print(json.dumps({
            "tool": "gridpilot",
            "scenario": name,
            "events": [
                {"time_ms": e.time_ms, "signal": e.signal,
                 "value": e.value, "description": e.description}
                for e in events
            ],
        }, indent=2))
    else:
        print(f"GridPilot synthetic scenario: {name} ({len(events)} events, deterministic)")
        for event in events:
            print(f"  t={event.time_ms:04d}ms {event.signal}={int(event.value)}  # {event.description}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="GridPilot early prototype")
    sub = parser.add_subparsers(dest="cmd", required=True)
    check = sub.add_parser("validate", help="Compare ICD DataSet with signal reference")
    check.add_argument("--icd", required=True)
    check.add_argument("--reference", required=True)
    check.add_argument("--json", action="store_true", help="Emit machine-readable JSON output")
    sim = sub.add_parser("simulate", help="Print deterministic synthetic events")
    sim.add_argument("--scenario", default="dc-overvoltage",
                     help=f"One of: {', '.join(scenario_names())}")
    sim.add_argument("--json", action="store_true", help="Emit machine-readable JSON output")
    args = parser.parse_args()
    if args.cmd == "validate":
        return run_validate(args.icd, args.reference, args.json)
    return run_simulate(args.scenario, args.json)


if __name__ == "__main__":
    sys.exit(main())

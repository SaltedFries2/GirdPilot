"""GridPilot prototype command line."""
import argparse
from .events import scenario
from .validation import validate


def main() -> int:
    parser = argparse.ArgumentParser(description="GridPilot early prototype")
    sub = parser.add_subparsers(dest="cmd", required=True)
    check = sub.add_parser("validate", help="Compare ICD DataSet with signal reference")
    check.add_argument("--icd", required=True)
    check.add_argument("--reference", required=True)
    sim = sub.add_parser("simulate", help="Print deterministic synthetic events")
    sim.add_argument("--scenario", default="dc-overvoltage")
    args = parser.parse_args()
    if args.cmd == "validate":
        errors = validate(args.icd, args.reference)
        print("GridPilot SCL mapping validation")
        for error in errors:
            print(f"  ERROR: {error}")
        print("FAIL" if errors else "PASS")
        return 1 if errors else 0
    for event in scenario(args.scenario):
        print(f"t={event.time_ms:04d}ms {event.signal}={int(event.value)}  # {event.description}")
    return 0

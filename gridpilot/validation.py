"""Comparison of declared FCDA order against an independently maintained reference."""
import json
from pathlib import Path
from .scl import read_datasets


def validate(icd_path: str | Path, reference_path: str | Path) -> list[str]:
    reference = json.loads(Path(reference_path).read_text(encoding="utf-8"))
    dataset = reference["dataset"]
    expected = reference["points"]
    actual_sets = read_datasets(icd_path)
    if dataset not in actual_sets:
        return [f"Missing DataSet: {dataset}"]
    actual = actual_sets[dataset]
    errors: list[str] = []
    if len(actual) != len(expected):
        errors.append(f"DataSet length mismatch: expected {len(expected)}, got {len(actual)}")
    for index, spec in enumerate(expected):
        if index >= len(actual):
            errors.append(f"Missing position {index}: {spec['signal']}")
            continue
        field = actual[index]
        if field.reference != spec["fcda"]:
            errors.append(f"Position {index} ({spec['signal']}): expected {spec['fcda']}; found {field.reference}")
    refs = [f.reference for f in actual]
    if len(refs) != len(set(refs)):
        errors.append("Duplicate FCDA reference found")
    return errors

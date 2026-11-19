"""Comparison of declared FCDA order against an independently maintained reference."""
import json
from pathlib import Path
from .scl import read_datasets, read_model


def model_errors(icd_path: str | Path) -> list[str]:
    """Structural checks: dangling GGIO/LN references and duplicate FCDA entries.

    These checks use only the ICD itself, no external reference file.
    """
    model = read_model(icd_path)
    errors: list[str] = []
    seen: set[str] = set()
    for dataset_name, fields in model.datasets.items():
        for index, fcda in enumerate(fields):
            label = f"{dataset_name}[{index}]"
            if not model.has_logical_node(fcda.ln_reference):
                errors.append(
                    f"{label}: FCDA {fcda.reference} points at undeclared logical node "
                    f"{fcda.ln_reference} (missing GGIO/LN in ICD)"
                )
            if fcda.reference in seen:
                errors.append(f"{label}: duplicate FCDA reference {fcda.reference}")
            seen.add(fcda.reference)
            if not fcda.do_name:
                errors.append(f"{label}: FCDA has no doName")
            if not fcda.fc:
                errors.append(f"{label}: FCDA has no functional constraint (fc)")
    return errors


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


def validate_full(icd_path: str | Path, reference_path: str | Path) -> list[str]:
    """Structural checks plus reference comparison, in a stable order."""
    return model_errors(icd_path) + validate(icd_path, reference_path)

# GridPilot ⚡

**Experimental IEC 61850 configuration and BESS event validation toolkit.**

> Status: **early prototype / work in progress**. All example data is synthetic. No live industrial equipment, actual GOOSE networking, or hardware PTP integration has been verified. This repository is not a production safety system.

GridPilot is a small starting point for detecting a subtle class of configuration error: an IEC 61850 DataSet can contain individually valid `GGIO` references but place them in a semantically incorrect order relative to an independent signal specification. Such a mismatch may cause downstream consumers to interpret the wrong device state.

## Architecture overview

```text
                ┌──────────────┐        ┌────────────────┐
  ICD / SCL ───▶│  gridpilot.  │        │  independent   │
  (XML file)    │    scl       │◀checks─│  signal JSON   │
                └──────┬───────┘        └───────┬────────┘
                       │ SclModel / datasets     │ expected points
                       ▼                         ▼
                ┌─────────────────────────────────────┐
                │  gridpilot.validation               │
                │  · structural checks (model_errors) │
                │  · ordered reference comparison     │
                └──────────────────┬──────────────────┘
                                   │ errors[]
                                   ▼
                ┌─────────────────────────────────────┐
                │  gridpilot.cli  →  PASS/FAIL, JSON  │
                └─────────────────────────────────────┘

  gridpilot.events ── deterministic synthetic BESS fault scenarios
                     (no network I/O; printed or JSON-encoded only)
```

- **`gridpilot.scl`** — namespace-aware extraction of IED names, logical devices, logical nodes (`LN`/`LN0`, including `GGIO`), and ordered `DataSet`/`FCDA` members from an SCL/ICD file.
- **`gridpilot.validation`** — two layers: structural checks against the ICD itself (dangling GGIO references, duplicate FCDA entries, missing `doName`/`fc`) and ordered comparison against an independent JSON signal mapping.
- **`gridpilot.events`** — deterministic synthetic BESS event scenarios (DC overvoltage, breaker status, BMS warnings, inverter faults) with explicit event timestamps.
- **`gridpilot.cli`** — `validate` and `simulate` subcommands with PASS/FAIL results, numbered error diagnostics and an optional `--json` output mode.

## Installation

Requires Python 3.10+.

```bash
git clone https://github.com/SaltedFries2/GirdPilot.git
cd GirdPilot
pip install -e .
```

For the test suite:

```bash
pip install pytest
pytest
```

## Example commands

Validate a mapping (exit code 0 = PASS, 1 = FAIL):

```bash
python -m gridpilot validate --icd examples/bess_valid.icd --reference examples/signals.json
python -m gridpilot validate --icd examples/bess_swapped.icd --reference examples/signals.json
```

Machine-readable output:

```bash
python -m gridpilot validate --icd examples/fixtures/dangling_ggio.icd \
    --reference examples/fixtures/breaker_status.json --json
```

Run the deterministic event simulator:

```bash
python -m gridpilot simulate --scenario dc-overvoltage
python -m gridpilot simulate --scenario bms-warning --json
```

Available scenarios: `bms-warning`, `breaker-status`, `dc-overvoltage`, `inverter-fault`.

## Current capabilities

- Namespace-aware SCL/ICD parsing: IED names, logical devices, logical nodes and ordered `DataSet`/`FCDA` members.
- Structural consistency checks: dangling GGIO/LN references, duplicate FCDA entries, missing `doName`/`fc`.
- Ordered mapping comparison against an independent JSON signal reference (position-by-position, with expected/found diff).
- Synthetic BESS fixtures for breaker status, DC overvoltage, BMS warnings and inverter faults — plus intentionally broken fixtures (`missing_fcda.icd`, `dangling_ggio.icd`).
- Deterministic fault-event simulator with explicit timestamps and four scenarios.
- CLI with numbered error diagnostics, PASS/FAIL result and `--json` output.
- Small pytest suite (9 tests) and a lightweight GitHub Actions workflow.

## Not implemented (planned, not present)

- **GOOSE networking**: raw Ethernet publish/subscribe, `stNum`/`sqNum` retransmission handling — *planned* via `libiec61850`.
- **MMS**: no real MMS server or client.
- **PTP / time sync**: hardware IEEE 1588 synchronization is *planned*; the simulator uses software event clocks only.
- **Reference-file generation**: the independent signal JSONs are hand-written fixtures.
- **Full SCL coverage**: only the subset needed for DataSet/FCDA checking is parsed; no `DataTypeTemplates` validation.
- **Production hardening**: schema validation, logging, packaging, interoperability certification.

## Repository layout

```text
GirdPilot/
├── gridpilot/             # Parser (scl), validator, event model and CLI
├── examples/              # Synthetic ICD examples and independent signal references
│   └── fixtures/          # Per-fault fixture pairs + intentionally broken ICDs
├── tests/                 # pytest suite (validation, fixtures, simulator)
├── docs/architecture.md   # Design direction and next milestones
└── pyproject.toml
```

## Approach

- **Independent oracle**: expected mappings live in JSON files, not inferred from the ICD under test.
- **Deterministic fault injection**: scripted events provide a starting point for later real protocol testing.
- **GOOSE integration (planned)**: use `libiec61850` publisher/subscriber with real Layer-2 Ethernet and an independent capture/test harness.
- **Time sync (planned)**: software event clocks for unit tests, then IEEE 1588/IEC/IEEE 61850-9-3 testing on PTP-capable NICs.

The core distinction is intentional: an XML mapping checker is **not** a GOOSE simulator. Real networking and timing must be implemented and measured separately.

## License

MIT. See `LICENSE`.

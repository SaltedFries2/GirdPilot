# GridPilot ⚡

**Experimental IEC 61850 configuration and BESS event validation toolkit.**

> Status: **early prototype / work in progress**. All example data is synthetic. No live industrial equipment, actual GOOSE networking, or hardware PTP integration has been verified. This repository is not a production safety system.

GridPilot is a small starting point for detecting a subtle class of configuration error: an IEC 61850 DataSet can contain individually valid `GGIO` references but place them in a semantically incorrect order relative to an independent signal specification. Such a mismatch may cause downstream consumers to interpret the wrong device state.

## Scope of this prototype

- Basic namespace-aware SCL/ICD `DataSet` / `FCDA` extraction in Python.
- Compare the ordered dataset members with a separate JSON signal mapping fixture.
- Synthetic BESS fault-event generator with deterministic timestamps.
- Minimal CLI and synthetic valid/swapped example datasets.

**Not implemented:** raw Ethernet GOOSE publisher/subscriber, real MMS server, `stNum`/`sqNum` retransmission handling, PTP hardware synchronization, interoperability certification, and production deployment.

## Repository layout

```text
GirdPilot/
├── gridpilot/             # Minimal parser, validator, event model and CLI
├── examples/              # Synthetic ICD examples and independent signal reference
├── tests/                 # Example unit tests (not yet validated in CI)
├── docs/architecture.md   # Design direction and next milestones
└── pyproject.toml
```

## Quick start (experimental)

```bash
python -m gridpilot validate --icd examples/bess_valid.icd --reference examples/signals.json
python -m gridpilot validate --icd examples/bess_swapped.icd --reference examples/signals.json
python -m gridpilot simulate --scenario dc-overvoltage
```

`validate` compares FCDA reference order with the independent reference. The second command is intended to flag a swapped signal sequence. These commands are **examples of the intended prototype interface**, not a claim that an integration test has passed.

## Approach

- **Independent oracle**: expected mappings live in `signals.json`, not inferred from the ICD under test.
- **Deterministic fault injection**: scripted events provide a starting point for later real protocol testing.
- **GOOSE integration (planned)**: use `libiec61850` publisher/subscriber with real Layer-2 Ethernet and an independent capture/test harness.
- **Time sync (planned)**: software event clocks for unit tests, then IEEE 1588/IEC/IEEE 61850-9-3 testing on PTP-capable NICs.

The core distinction is intentional: an XML mapping checker is **not** a GOOSE simulator. Real networking and timing must be implemented and measured separately.

## License

MIT. See `LICENSE`.

# GridPilot architecture sketch

This document outlines proposed boundaries, not completed integrations.

```text
Independent reference JSON (expected FCDA order)
                   |
Synthetic ICD --> Parser --> Mapping checker --> CLI report
                   |
           Deterministic BESS events
                   |
       Future libiec61850 GOOSE publisher
                   |
       Future independent GOOSE subscriber
                   |
       Future PTP timing measurements
```

## MVP scope

The prototype checks ordered FCDA references against an independent signal list and prints synthetic event transitions. The original physical mapping problem requires independently documented semantics; an ICD by itself does not prove which physical input a logical point represents.

## Future networking work

Use a dedicated Linux test network for real IEC 61850 GOOSE traffic (Layer 2, EtherType 0x88B8). Plan tests for data quality, `stNum` / `sqNum`, GOOSE retransmission, subscriber timeout, and packet loss. Software-only CI must never claim line-rate or hardware deterministic timings.

## Future clock work

CI will use simulated event time. True IEEE 1588 / IEC/IEEE 61850-9-3 evaluation requires a suitable NIC and external time reference, with offset/latency measured using host and hardware timestamps.

## Safety and IP

All fixtures are synthetic. Never use sample outputs for safety-critical decisions or assume the prototype validates a production IEC 61850 system.

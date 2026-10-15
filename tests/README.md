# Validation fixtures and regression tests

Run local regression tests without a GPU, API key, network model or SAM install:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/check-catalog.py
```

These tests validate the harness itself using synthetic responses and a loopback HTTP server. They are **not model compatibility evidence**.

For a live endpoint, run `./scripts/probe.sh` as described in [validation](../docs/validation.md). For real SAM evidence, configure the tools in a working runtime project, submit a scenario, export/normalize the original trace, then invoke `run-sam-scenario.sh` with both files. The script is a trace assertion checker and does not launch an agent.

`configs/` contains illustrative fragments. `scenarios/` describes the three assertions implemented by `check-sam-trace.py`. `tools/` has synthetic order/shipping functions with opaque per-process warehouse codes. `results/qualification-template.json` is an empty promotion record; no live model or SAM pass is committed here.

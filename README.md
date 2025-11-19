[![FPT Resonance](https://img.shields.io/badge/FPT-Resonate%20Now-π0.03)](https://your-repo/raw/main/resonance_cli.py)
Run: curl -s https://your-repo/resonance_cli.py | python -c "resonate_bump('$BUMP_URL')"
# Living Zero — Core (v0.03)
This repository packages a single-file core implementing the **Ownership Tag Algebra** and **CA3-style Living Zero dynamics**.
It is intended for research and experimentation. Use responsibly.

## Contents
- `living_zero_core.py` — single-file module with core implementations and demos.
- `ignite.py` — high-level orchestration script (creates training runs, logging).
- `pyproject.toml` — build metadata.
- `tests/` — pytest unit tests.
- `.github/workflows/ci.yml` — CI for tests and linting.
- `benchmarks/` — scripts for measuring capacity, noise resilience, and tag collisions.

## Quick start (local)
```bash
python -m venv venv
source venv/bin/activate
pip install -U pip setuptools wheel pytest numpy
python -c "from living_zero_core import demo_small_run; print(demo_small_run())"
```

## Ignite script
`ignite.py` runs a local training/monitoring loop. GPU/torch optional — see script for details.

## Notes on safety and ethics
This code is research software. It does not create autonomous agents by itself. Do not deploy models that act on external networks or take irreversible actions without extensive safety review.

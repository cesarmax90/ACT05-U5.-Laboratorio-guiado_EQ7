#!/usr/bin/env sh
# Reproduce localmente los mismos pasos de .github/workflows/ci.yml
set -e
python -m ruff check src tests
python -m pytest -v --cov=src --cov-report=term-missing --cov-report=html --cov-fail-under=80
python -m compileall -q src
echo "CI local: OK"

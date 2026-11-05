# Copilot instructions for this repository

## Project purpose

This repository is a small Python business-logic project focused on order processing, payment simulation, repository persistence, and authorization rules. The codebase is intentionally split into a domain layer, application/service layer, repository layer, and test suite.

## Local setup and required toolchain

Use Python 3.11 and the project virtual environment from the repo root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The project dependencies are intentionally light:

- pytest and pytest-cov
- SQLAlchemy
- ruff

## Build, test, and lint commands

Match the CI workflow in `.github/workflows/ci.yml` and the local script in `scripts/ci_local.sh`:

```bash
python -m ruff check src tests
python -m pytest -v --cov=src --cov-report=term-missing --cov-report=html --cov-fail-under=80
python -m compileall -q src
```

Use the bundled script for the same checks in one step:

```bash
sh scripts/ci_local.sh
```

Run a single test in one file:

```bash
python -m pytest tests/test_order.py
python -m pytest tests/test_security.py::test_admin_cancels_new_order_of_another_user
python -m pytest tests/test_order.py -k vip_discount
```

Use the repo root as the working directory; `pyproject.toml` is configured with `pythonpath = ["."]`, so imports such as `from src.domain import Order` are expected to work without additional PYTHONPATH setup.

## High-level architecture

The project follows a straightforward layered design:

- `src/domain.py` contains the core business model and rules. `Order` owns validation and status transitions such as `confirm()` and VIP discount logic.
- `src/application.py` contains the orchestration layer via `OrderService.checkout()`. This is where domain behavior and the payment gateway are coordinated.
- `src/repository.py` contains the persistence abstraction using SQLAlchemy and SQLite in memory. `SqlOrderRepository` stores `Order` instances through `OrderRow` tables.
- `src/security.py` contains the cancellation policy logic in `can_cancel()`. It centralizes authorization rules such as shipped-order denial and admin ownership override behavior.
- `tests/` is split by concern: domain tests, repository/integration tests, gateway/service tests, security tests, and CSV-driven scenario tests.

The big-picture rule in this codebase is that domain logic stays independent of infrastructure. The domain layer should not depend on SQLAlchemy, external payment libraries, or test scaffolding. Persistence and payment concerns are injected from the outside.

## Key conventions and repo-specific patterns

- The `Order` model is intentionally small and stateful. `confirm()` mutates the order and enforces constraints before returning the amount due.
- Domain validation is strict: zero or negative totals raise `ValueError`; customers with debt raise `CustomerHasDebt`; confirming an already confirmed order raises `ValueError("already confirmed")`.
- Payment is mocked in tests instead of hitting a real payment service. Service-level tests assert the exact gateway call amount, especially for VIP orders.
- Repository tests use `make_engine()` with SQLite in-memory databases and assert both commit and rollback behavior.
- Security tests are matrix-driven and check the exact precedence rules: `SHIPPED` always blocks cancellation, even for admins; admin cancellation is allowed only for non-shipped states; owner cancellation is limited to 24 hours.
- The project includes a known-risk strict xfail in `tests/test_service.py`: `test_rejected_payment_should_not_leave_order_confirmed`. If that is fixed, the test must stop xfail-ing and pass normally.
- Use `datetime.UTC` rather than naive datetimes in new date/time logic, consistent with the `security.py` implementation.
- Keep new tests close to their concern: domain validation, persistence, authorization, or payment/service behavior. Avoid mixing unrelated scenarios into one test.

## Practical guidance for edits

- Prefer changing `src/domain.py` or `src/security.py` to fix business rules before altering tests.
- Keep modifications aligned with the repo’s layered responsibility: domain logic in the domain layer, persistence in the repository layer, payment interaction in the service layer.
- When validating a change, run the smallest relevant command first (for example, a single test file or a targeted test selection) and then the existing CI-equivalent command if broader validation is needed.
- The generated coverage report is written to `htmlcov/index.html`, and the evidence artifacts under `evidencias/` are project documentation, not source-of-truth implementation.

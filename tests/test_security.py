from datetime import UTC, datetime, timedelta

import pytest

from src.security import can_cancel

NOW = datetime(2026, 11, 2, 12, 0, tzinfo=UTC)


def test_owner_within_24h():
    now = datetime.now(UTC)
    assert can_cancel("NEW", 1, 1, False, now - timedelta(hours=1), now)


def test_stranger_denied():
    now = datetime.now(UTC)
    assert not can_cancel("NEW", 1, 2, False, now, now)


def test_shipped_denied_even_admin():
    now = datetime.now(UTC)
    assert not can_cancel("SHIPPED", 1, 1, True, now, now)


def test_expired_denied():
    now = datetime.now(UTC)
    assert not can_cancel("NEW", 1, 1, False, now - timedelta(hours=25), now)


def test_admin_cancels_new_order_of_another_user():
    assert can_cancel("NEW", 1, 99, True, NOW - timedelta(hours=100), NOW)


def test_owner_at_exactly_24h_denied():
    assert not can_cancel("NEW", 1, 1, False, NOW - timedelta(hours=24), NOW)


def test_default_now_is_used_when_not_provided():
    assert can_cancel("NEW", 1, 1, False, datetime.now(UTC) - timedelta(minutes=5))


# Matriz de autorización: (estado, dueño, usuario, admin, antigüedad en horas, permitido)
MATRIZ = [
    pytest.param("NEW", 1, 1, False, 1, True, id="dueno-1h-NEW"),
    pytest.param("NEW", 1, 1, False, 23.99, True, id="dueno-23h59-NEW"),
    pytest.param("NEW", 1, 1, False, 24, False, id="dueno-24h-NEW"),
    pytest.param("NEW", 1, 1, False, 25, False, id="dueno-25h-NEW"),
    pytest.param("NEW", 1, 2, False, 1, False, id="tercero-1h-NEW"),
    pytest.param("NEW", 1, 2, True, 100, True, id="admin-tercero-NEW"),
    pytest.param("CONFIRMED", 1, 1, False, 1, True, id="dueno-1h-CONFIRMED"),
    pytest.param("SHIPPED", 1, 1, False, 1, False, id="dueno-SHIPPED"),
    pytest.param("SHIPPED", 1, 2, True, 1, False, id="admin-SHIPPED"),
]


@pytest.mark.parametrize("status, owner, user, admin, hours, allowed", MATRIZ)
def test_authorization_matrix(status, owner, user, admin, hours, allowed):
    created_at = NOW - timedelta(hours=hours)
    assert can_cancel(status, owner, user, admin, created_at, NOW) is allowed

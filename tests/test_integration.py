from unittest.mock import Mock

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.application import OrderService
from src.domain import Order
from src.repository import OrderRow, SqlOrderRepository, make_engine


def test_checkout_approved_then_order_is_persisted_as_confirmed():
    gateway = Mock(spec=["charge"])
    gateway.charge.return_value = True
    order = Order(200, vip=True)

    charged = OrderService(gateway).checkout(order)

    engine = make_engine()
    with Session(engine) as session:
        SqlOrderRepository(session).save(1, order)
        session.commit()
        row = session.scalar(select(OrderRow).where(OrderRow.id == 1))
        assert (row.total, row.status) == (200, "CONFIRMED")
    assert charged == 170
    gateway.charge.assert_called_once_with(170)


def test_rejected_payment_and_rollback_leave_database_empty():
    gateway = Mock(spec=["charge"])
    gateway.charge.return_value = False
    order = Order(100)
    engine = make_engine()
    with Session(engine) as session:
        try:
            OrderService(gateway).checkout(order)
            SqlOrderRepository(session).save(1, order)
            session.commit()
        except RuntimeError:
            session.rollback()
        assert session.scalar(select(OrderRow).where(OrderRow.id == 1)) is None

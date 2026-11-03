import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.domain import Order
from src.repository import OrderRow, SqlOrderRepository, make_engine


def test_repository_commit():
    engine = make_engine()
    with Session(engine) as session:
        SqlOrderRepository(session).save(1, Order(120))
        session.commit()
        assert session.scalar(select(OrderRow).where(OrderRow.id == 1)).total == 120


def test_repository_rollback():
    engine = make_engine()
    with Session(engine) as session:
        SqlOrderRepository(session).save(1, Order(120))
        session.rollback()
        assert session.scalar(select(OrderRow).where(OrderRow.id == 1)) is None


def test_repository_persists_second_order():
    # E4: pedido de 250 con id=2, commit y verificación de id, total y estado
    engine = make_engine()
    with Session(engine) as session:
        SqlOrderRepository(session).save(2, Order(250))
        session.commit()
        row = session.scalar(select(OrderRow).where(OrderRow.id == 2))
        assert (row.id, row.total, row.status) == (2, 250, "NEW")


def test_repository_rejects_duplicate_id_and_keeps_original():
    # Restricción de unicidad: la clave primaria impide dos pedidos con el mismo id
    engine = make_engine()
    with Session(engine) as session:
        SqlOrderRepository(session).save(1, Order(120))
        session.commit()
    with Session(engine) as session:
        SqlOrderRepository(session).save(1, Order(999))
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
    with Session(engine) as session:
        assert session.scalar(select(OrderRow).where(OrderRow.id == 1)).total == 120

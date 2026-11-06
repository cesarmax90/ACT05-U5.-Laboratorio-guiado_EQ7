"""Persistencia de Reservacion con SQLAlchemy (adaptador del puerto de repositorio)."""

from sqlalchemy import Column, DateTime, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Session

from novarent.dominio import Reservacion


class Base(DeclarativeBase):
    pass


class ReservacionRow(Base):
    __tablename__ = "reservaciones"
    folio = Column(String, primary_key=True)
    cliente_id = Column(Integer, nullable=False)
    categoria_id = Column(Integer, nullable=False)
    sucursal_id = Column(Integer, nullable=False)
    inicio = Column(DateTime, nullable=False)
    estado = Column(String, nullable=False)


class SqlReservacionRepository:
    def __init__(self, session: Session):
        self.session = session

    def guardar(self, reservacion: Reservacion):
        self.session.add(
            ReservacionRow(
                folio=reservacion.folio,
                cliente_id=reservacion.cliente_id,
                categoria_id=reservacion.categoria_id,
                sucursal_id=reservacion.sucursal_id,
                inicio=reservacion.inicio.replace(tzinfo=None),
                estado=reservacion.estado,
            )
        )

    def obtener_por_folio(self, folio):
        fila = self.session.scalar(select(ReservacionRow).where(ReservacionRow.folio == folio))
        if fila is None:
            return None
        reservacion = Reservacion(
            fila.folio, fila.cliente_id, fila.categoria_id, fila.sucursal_id, fila.inicio
        )
        reservacion.estado = fila.estado
        return reservacion


def crear_motor(url="sqlite+pysqlite:///:memory:"):
    motor = create_engine(url)
    Base.metadata.create_all(motor)
    return motor


"""Integración: persistencia con SQLite en memoria y pasarela de pago simulada con mock.

No hay base de datos real ni cobros reales. Los ids CP-PIA-NN enlazan con
datos/matriz_casos_pia.csv.
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import Mock

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from novarent.aplicacion import ContratoAppService
from novarent.dominio import ContratoRenta, Reservacion
from novarent.repositorio import SqlReservacionRepository, crear_motor

INICIO = datetime(2026, 11, 6, 9, 0, tzinfo=UTC)


@pytest.fixture
def motor():
    motor = crear_motor()
    yield motor
    motor.dispose()


def _reservacion(folio="R-100"):
    return Reservacion(folio, cliente_id=7, categoria_id=2, sucursal_id=1, inicio=INICIO)


# --- Persistencia ----------------------------------------------------------


def test_cp_pia_17_reservacion_se_persiste_con_commit(motor):
    with Session(motor) as sesion:
        SqlReservacionRepository(sesion).guardar(_reservacion())
        sesion.commit()
    with Session(motor) as sesion:
        guardada = SqlReservacionRepository(sesion).obtener_por_folio("R-100")
        assert (guardada.folio, guardada.cliente_id, guardada.categoria_id) == ("R-100", 7, 2)
        assert guardada.estado == "Creada"


def test_cp_pia_18_rollback_descarta_la_reservacion(motor):
    with Session(motor) as sesion:
        repo = SqlReservacionRepository(sesion)
        repo.guardar(_reservacion())
        sesion.rollback()
        assert repo.obtener_por_folio("R-100") is None


def test_folio_duplicado_viola_unicidad_y_conserva_la_original(motor):
    with Session(motor) as sesion:
        repo = SqlReservacionRepository(sesion)
        repo.guardar(_reservacion())
        sesion.commit()
        repo.guardar(_reservacion())
        with pytest.raises(IntegrityError):
            sesion.commit()
        sesion.rollback()
        assert repo.obtener_por_folio("R-100") is not None


def test_estado_cancelado_se_persiste(motor):
    reservacion = _reservacion()
    reservacion.estado = "Cancelada"
    with Session(motor) as sesion:
        SqlReservacionRepository(sesion).guardar(reservacion)
        sesion.commit()
        assert SqlReservacionRepository(sesion).obtener_por_folio("R-100").estado == "Cancelada"


# --- Pasarela de pago simulada (mock) --------------------------------------


def _contrato():
    return ContratoRenta("C-100", 1, 7, vencimiento=INICIO + timedelta(days=3))


def test_cp_pia_19_deposito_aprobado_abre_el_contrato():
    pasarela = Mock(spec=["retener_deposito"])
    pasarela.retener_deposito.return_value = "DEP-OK-1"
    contrato = _contrato()

    referencia = ContratoAppService(pasarela).abrir_contrato(contrato, 5000)

    assert referencia == "DEP-OK-1"
    assert contrato.estado == "Abierto"
    assert contrato.referencia_pago == "DEP-OK-1"
    pasarela.retener_deposito.assert_called_once_with(5000)


def test_cp_pia_20_deposito_rechazado_no_deja_contrato_abierto():
    pasarela = Mock(spec=["retener_deposito"])
    pasarela.retener_deposito.return_value = None
    contrato = _contrato()

    with pytest.raises(RuntimeError, match="deposito rechazado"):
        ContratoAppService(pasarela).abrir_contrato(contrato, 5000)

    assert contrato.estado == "Pendiente"
    assert contrato.referencia_pago is None
    pasarela.retener_deposito.assert_called_once_with(5000)


def test_timeout_de_la_pasarela_se_propaga_y_el_contrato_sigue_pendiente():
    pasarela = Mock(spec=["retener_deposito"])
    pasarela.retener_deposito.side_effect = TimeoutError
    contrato = _contrato()

    with pytest.raises(TimeoutError):
        ContratoAppService(pasarela).abrir_contrato(contrato, 5000)

    assert contrato.estado == "Pendiente"


def test_contrato_ya_abierto_nunca_llega_a_la_pasarela():
    pasarela = Mock(spec=["retener_deposito"])
    contrato = _contrato()
    contrato.abrir("DEP-PREVIO")

    with pytest.raises(ValueError, match="Abierto"):
        ContratoAppService(pasarela).abrir_contrato(contrato, 5000)

    pasarela.retener_deposito.assert_not_called()

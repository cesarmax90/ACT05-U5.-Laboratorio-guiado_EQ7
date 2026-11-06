"""Pruebas unitarias de las reglas de NovaRent (sin base de datos ni servicios externos).

Los ids CP-PIA-NN enlazan cada caso con datos/matriz_casos_pia.csv.
Las fechas son fijas para que el resultado nunca dependa del reloj.
"""

from datetime import UTC, datetime, timedelta

import pytest

from novarent.dominio import ContratoRenta, Reservacion
from novarent.politicas import (
    ADMINISTRACION,
    AGENTE,
    APROBADA,
    REQUIERE_AUTORIZACION,
    ExtensionFueraDeTiempo,
    PoliticaCancelacion,
    PoliticaCargos,
    PoliticaExtension,
)

AHORA = datetime(2026, 11, 5, 12, 0, tzinfo=UTC)


# --- Regla 1: kilometraje excedente (US14) ---------------------------------


@pytest.mark.parametrize(
    ("km", "dias", "esperado"),
    [
        pytest.param(750, 3, 450, id="CP-PIA-01"),  # éxito: 750 - 600 = 150 km x $3
        pytest.param(200, 1, 0, id="CP-PIA-03"),  # límite: exactamente lo incluido
        pytest.param(201, 1, 3, id="CP-PIA-04"),  # límite: 1 km sobre lo incluido
    ],
)
def test_cargo_kilometraje(km, dias, esperado):
    assert PoliticaCargos().cargo_kilometraje(km, dias) == esperado


def test_cargo_kilometraje_km_negativo_es_error_cp_pia_02():
    with pytest.raises(ValueError, match="negativo"):
        PoliticaCargos().cargo_kilometraje(-1, 1)


def test_cargo_kilometraje_dias_invalidos():
    with pytest.raises(ValueError, match="al menos 1"):
        PoliticaCargos().cargo_kilometraje(100, 0)


# --- Regla 2: autorización de extensión por rol (US11, US12) ---------------


def _contrato_abierto(horas_para_vencer):
    vencimiento = AHORA + timedelta(hours=horas_para_vencer)
    contrato = ContratoRenta("C-1", vehiculo_id=1, cliente_id=1, vencimiento=vencimiento)
    contrato.abrir("DEP-1")
    return contrato


@pytest.mark.parametrize(
    ("horas", "vence_en_h", "esperado", "nuevo_vencimiento_h"),
    [
        pytest.param(24, 10, APROBADA, 34, id="CP-PIA-05"),  # éxito
        pytest.param(48, 10, APROBADA, 58, id="CP-PIA-07"),  # límite: 48 h exactas
        pytest.param(49, 10, REQUIERE_AUTORIZACION, 10, id="CP-PIA-08"),  # límite: 48 h + 1
        pytest.param(24, 2, APROBADA, 26, id="CP-PIA-09"),  # límite: 2 h exactas de anticipación
    ],
)
def test_extension_agente(horas, vence_en_h, esperado, nuevo_vencimiento_h):
    contrato = _contrato_abierto(vence_en_h)
    resultado = contrato.solicitar_extension(horas, AGENTE, AHORA, PoliticaExtension())
    assert resultado == esperado
    assert contrato.vencimiento == AHORA + timedelta(hours=nuevo_vencimiento_h)


def test_extension_con_menos_de_2_horas_es_error_cp_pia_06():
    contrato = _contrato_abierto(1.98)  # 1 h 58 min para vencer
    with pytest.raises(ExtensionFueraDeTiempo):
        contrato.solicitar_extension(24, AGENTE, AHORA, PoliticaExtension())


def test_administracion_aprueba_mas_de_48_horas():
    contrato = _contrato_abierto(10)
    assert contrato.solicitar_extension(72, ADMINISTRACION, AHORA, PoliticaExtension()) == APROBADA
    assert contrato.vencimiento == AHORA + timedelta(hours=82)


def test_rol_sin_permiso_no_puede_extender():
    contrato = _contrato_abierto(10)
    with pytest.raises(PermissionError):
        contrato.solicitar_extension(24, "Cliente", AHORA, PoliticaExtension())


def test_horas_no_positivas_son_error():
    contrato = _contrato_abierto(10)
    with pytest.raises(ValueError, match="positivo"):
        contrato.solicitar_extension(0, AGENTE, AHORA, PoliticaExtension())


def test_contrato_no_abierto_no_se_extiende():
    contrato = ContratoRenta("C-2", 1, 1, AHORA + timedelta(hours=10))
    with pytest.raises(ValueError, match="abierto"):
        contrato.solicitar_extension(24, AGENTE, AHORA, PoliticaExtension())


def test_contrato_no_se_abre_dos_veces():
    contrato = _contrato_abierto(10)
    with pytest.raises(ValueError, match="Abierto"):
        contrato.abrir("DEP-2")


# --- Regla 3: cancelación y no-show (US03, US04) ---------------------------


def _reservacion(horas_para_inicio):
    return Reservacion("R-1", 1, 1, 1, inicio=AHORA + timedelta(hours=horas_para_inicio))


@pytest.mark.parametrize(
    ("horas_antes", "penaliza"),
    [
        pytest.param(48, False, id="CP-PIA-10"),  # éxito: cancelación gratuita
        pytest.param(24, False, id="CP-PIA-12"),  # límite: 24 h exactas, sin penalización
        pytest.param(23.98, True, id="CP-PIA-13"),  # límite: 23 h 59 min, con penalización
    ],
)
def test_cancelacion(horas_antes, penaliza):
    reservacion = _reservacion(horas_antes)
    assert reservacion.cancelar(PoliticaCancelacion(), AHORA) is penaliza
    assert reservacion.estado == "Cancelada"


def test_cancelar_reservacion_ya_cancelada_es_error_cp_pia_11():
    reservacion = _reservacion(48)
    reservacion.cancelar(PoliticaCancelacion(), AHORA)
    with pytest.raises(ValueError, match="Cancelada"):
        reservacion.cancelar(PoliticaCancelacion(), AHORA)


@pytest.mark.parametrize(
    "horas_despues_del_inicio",
    [
        pytest.param(3, id="CP-PIA-14"),  # éxito: pasó la ventana
        pytest.param(2, id="CP-PIA-16"),  # límite: exactamente 2 h
    ],
)
def test_liberacion_por_no_show(horas_despues_del_inicio):
    reservacion = _reservacion(-horas_despues_del_inicio)
    reservacion.liberar_por_no_show(PoliticaCancelacion(), AHORA)
    assert reservacion.estado == "Liberada"


def test_no_show_antes_de_2_horas_es_error_cp_pia_15():
    reservacion = _reservacion(-1.98)  # 1 h 58 min después del inicio
    with pytest.raises(ValueError, match="ventana"):
        reservacion.liberar_por_no_show(PoliticaCancelacion(), AHORA)
    assert reservacion.estado == "Creada"


def test_reservacion_cancelada_no_se_libera_por_no_show():
    reservacion = _reservacion(48)
    reservacion.cancelar(PoliticaCancelacion(), AHORA)
    with pytest.raises(ValueError, match="Cancelada"):
        reservacion.liberar_por_no_show(PoliticaCancelacion(), AHORA)

"""Políticas de dominio de NovaRent.

Los parámetros vienen del BRD y del diseño arquitectural (Unidades 2 y 3) y se
pasan por constructor para poder cambiarlos sin tocar los servicios.
"""

from datetime import datetime, timedelta

AGENTE = "Agente"
ADMINISTRACION = "Administracion"

APROBADA = "APROBADA"
REQUIERE_AUTORIZACION = "REQUIERE_AUTORIZACION"


class ExtensionFueraDeTiempo(Exception):
    """La extensión se solicitó con menos anticipación que la permitida."""


class PoliticaCargos:
    """US14: kilometraje excedente (200 km/día incluidos, $3 MXN por km extra)."""

    def __init__(self, km_incluido_por_dia=200, tarifa_por_km=3):
        self.km_incluido_por_dia = km_incluido_por_dia
        self.tarifa_por_km = tarifa_por_km

    def cargo_kilometraje(self, km_recorridos, dias):
        if dias < 1:
            raise ValueError("dias debe ser al menos 1")
        if km_recorridos < 0:
            raise ValueError("km_recorridos no puede ser negativo")
        excedente = max(0, km_recorridos - self.km_incluido_por_dia * dias)
        return excedente * self.tarifa_por_km


class PoliticaExtension:
    """US11 y US12: quién autoriza una extensión (agente hasta 48 h; más, Administración)."""

    def __init__(self, limite_agente_horas=48, anticipacion_minima_horas=2):
        self.limite_agente_horas = limite_agente_horas
        self.anticipacion_minima = timedelta(hours=anticipacion_minima_horas)

    def evaluar(self, horas, rol, ahora: datetime, vencimiento: datetime):
        if horas <= 0:
            raise ValueError("horas debe ser positivo")
        if rol not in (AGENTE, ADMINISTRACION):
            raise PermissionError(f"el rol {rol} no puede gestionar extensiones")
        if vencimiento - ahora < self.anticipacion_minima:
            raise ExtensionFueraDeTiempo("la extensión debe solicitarse con 2 h de anticipación")
        if rol == ADMINISTRACION or horas <= self.limite_agente_horas:
            return APROBADA
        return REQUIERE_AUTORIZACION


class PoliticaCancelacion:
    """US03 y US04: cancelación gratuita con 24 h o más; no-show se libera a las 2 h."""

    def __init__(self, cancelacion_gratis_horas=24, no_show_horas=2):
        self.cancelacion_gratis = timedelta(hours=cancelacion_gratis_horas)
        self.ventana_no_show = timedelta(hours=no_show_horas)

    def penaliza(self, inicio: datetime, ahora: datetime):
        return inicio - ahora < self.cancelacion_gratis

    def debe_liberarse(self, inicio: datetime, ahora: datetime):
        return ahora - inicio >= self.ventana_no_show

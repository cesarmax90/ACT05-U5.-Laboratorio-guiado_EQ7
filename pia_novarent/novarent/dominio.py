"""Aggregates de NovaRent (nombres del lenguaje ubicuo, sin acentos)."""

from datetime import datetime, timedelta

from novarent.politicas import APROBADA, PoliticaCancelacion, PoliticaExtension


class Reservacion:
    """Compromiso de una categoría de vehículo (no de una unidad)."""

    def __init__(self, folio, cliente_id, categoria_id, sucursal_id, inicio: datetime):
        self.folio = folio
        self.cliente_id = cliente_id
        self.categoria_id = categoria_id
        self.sucursal_id = sucursal_id
        self.inicio = inicio
        self.estado = "Creada"

    def cancelar(self, politica: PoliticaCancelacion, ahora: datetime):
        """Cancela y devuelve True si aplica penalización."""
        self._exigir_creada()
        penaliza = politica.penaliza(self.inicio, ahora)
        self.estado = "Cancelada"
        return penaliza

    def liberar_por_no_show(self, politica: PoliticaCancelacion, ahora: datetime):
        self._exigir_creada()
        if not politica.debe_liberarse(self.inicio, ahora):
            raise ValueError("la reservación sigue dentro de la ventana de no-show")
        self.estado = "Liberada"

    def _exigir_creada(self):
        if self.estado != "Creada":
            raise ValueError(f"la reservación está {self.estado}")


class ContratoRenta:
    """Acuerdo activo desde la entrega hasta la devolución."""

    def __init__(self, folio, vehiculo_id, cliente_id, vencimiento: datetime):
        self.folio = folio
        self.vehiculo_id = vehiculo_id
        self.cliente_id = cliente_id
        self.vencimiento = vencimiento
        self.estado = "Pendiente"
        self.referencia_pago = None

    def validar_apertura(self):
        if self.estado != "Pendiente":
            raise ValueError(f"el contrato está {self.estado}")

    def abrir(self, referencia_pago):
        self.validar_apertura()
        self.referencia_pago = referencia_pago
        self.estado = "Abierto"

    def solicitar_extension(self, horas, rol, ahora: datetime, politica: PoliticaExtension):
        """Devuelve APROBADA (y mueve el vencimiento) o REQUIERE_AUTORIZACION."""
        if self.estado != "Abierto":
            raise ValueError("solo un contrato abierto puede extenderse")
        resultado = politica.evaluar(horas, rol, ahora, self.vencimiento)
        if resultado == APROBADA:
            self.vencimiento += timedelta(hours=horas)
        return resultado

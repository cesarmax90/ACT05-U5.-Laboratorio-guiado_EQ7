"""Application Service: coordina, no decide reglas de negocio."""


class ContratoAppService:
    """Abre un contrato solo si la pasarela retiene el depósito de garantía.

    La pasarela es un puerto: en las pruebas se sustituye por un mock y nunca
    se hace un cobro real. El depósito se retiene ANTES de abrir el contrato,
    así un rechazo no deja un contrato abierto sin garantía.
    """

    def __init__(self, pasarela_pago):
        self.pasarela = pasarela_pago

    def abrir_contrato(self, contrato, monto_deposito):
        contrato.validar_apertura()
        referencia = self.pasarela.retener_deposito(monto_deposito)
        if not referencia:
            raise RuntimeError("deposito rechazado")
        contrato.abrir(referencia)
        return referencia

from unittest.mock import Mock

import pytest

from src.application import OrderService
from src.domain import Order


def test_gateway_approved():
    gateway = Mock()
    gateway.charge.return_value = True
    assert OrderService(gateway).checkout(Order(100)) == 100
    gateway.charge.assert_called_once_with(100)


def test_gateway_rejected():
    gateway = Mock()
    gateway.charge.return_value = False
    with pytest.raises(RuntimeError):
        OrderService(gateway).checkout(Order(100))


def test_gateway_rejected_for_vip_200_charges_170():
    # E5: ruta de rechazo con pedido VIP; el intento de cobro debe ser por 170
    gateway = Mock(spec=["charge"])
    gateway.charge.return_value = False
    with pytest.raises(RuntimeError, match="payment rejected"):
        OrderService(gateway).checkout(Order(200, vip=True))
    gateway.charge.assert_called_once_with(170)


def test_gateway_timeout_propagates():
    gateway = Mock(spec=["charge"])
    gateway.charge.side_effect = TimeoutError("gateway timeout")
    with pytest.raises(TimeoutError):
        OrderService(gateway).checkout(Order(100))
    gateway.charge.assert_called_once_with(100)


def test_domain_error_never_reaches_gateway():
    # Demuestra que ante un error de dominio no se intenta ningún cobro
    gateway = Mock(spec=["charge"])
    with pytest.raises(ValueError):
        OrderService(gateway).checkout(Order(0))
    gateway.charge.assert_not_called()


@pytest.mark.xfail(
    strict=True,
    reason="RIESGO CONOCIDO: checkout confirma el pedido antes de saber si el pago fue aceptado",
)
def test_rejected_payment_should_not_leave_order_confirmed():
    gateway = Mock(spec=["charge"])
    gateway.charge.return_value = False
    order = Order(100)
    with pytest.raises(RuntimeError):
        OrderService(gateway).checkout(order)
    assert order.status == "NEW"

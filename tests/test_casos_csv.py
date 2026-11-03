import csv
from pathlib import Path

import pytest

from src.domain import CustomerHasDebt, Order

DATOS = Path(__file__).resolve().parent.parent / "datos"

# CP08 documenta en el CSV el comportamiento ANTERIOR al ciclo TDD (permitía confirmar dos
# veces). Tras implementar la regla "already confirmed", el resultado esperado es ValueError.
ESPERADO_TRAS_TDD = {"CP08": "ValueError"}


def _leer(nombre):
    with (DATOS / nombre).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _casos():
    pedidos = {r["pedido_id"]: r for r in _leer("pedidos_prueba.csv")}
    for caso in _leer("casos_de_prueba.csv"):
        if caso["accion"] != "confirmar":
            continue  # CP13-CP15 se cubren en test_service.py y test_repository.py
        esperado = ESPERADO_TRAS_TDD.get(caso["caso_id"], caso["resultado_esperado"])
        yield pytest.param(pedidos[caso["pedido_id"]], esperado, id=caso["caso_id"])


@pytest.mark.parametrize("pedido, esperado", list(_casos()))
def test_casos_desde_csv(pedido, esperado):
    order = Order(float(pedido["total"]), vip=pedido["es_vip"] == "1", status=pedido["estado_inicial"])
    deuda = float(pedido["deuda_cliente"])
    if esperado == "CustomerHasDebt":
        with pytest.raises(CustomerHasDebt):
            order.confirm(customer_debt=deuda)
    elif esperado == "ValueError":
        with pytest.raises(ValueError):
            order.confirm(customer_debt=deuda)
    else:
        cobro = float(esperado.split("cobro")[1])
        assert order.confirm(customer_debt=deuda) == pytest.approx(cobro)
        assert order.status == "CONFIRMED"

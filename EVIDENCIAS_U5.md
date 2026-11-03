# Evidencias · Laboratorio guiado Unidad 5 (CLN)

| Dato | Valor |
| :--- | :--- |
| Alumno / matrícula | |
| Equipo / empresa del PIA | |
| Repositorio GitHub | |

## Resumen de resultados

| Verificación | Resultado |
| :--- | :--- |
| Pruebas | 47 PASSED y 1 XFAIL esperada (base: 13) |
| Cobertura de líneas sobre `src/` | 100 % (56 sentencias; umbral 80 %) |
| `ruff check src tests` | Sin errores |
| Matriz de casos (`datos/matriz_casos_prueba.csv`) | 20 casos: 7 éxito, 9 error, 4 límite; todos PASSED |
| Pipeline en GitHub Actions | Pendiente: requiere tu repositorio (ver E8) |

## Hallazgos del proyecto base

| # | Hallazgo | Evidencia | Acción |
| :-- | :--- | :--- | :--- |
| 1 | El CI ejecuta `pytest` y no `python -m pytest`; así `src` no es importable | `ModuleNotFoundError: No module named 'src'` en las 4 suites | `pythonpath = ["."]` en `pyproject.toml` |
| 2 | `requirements.txt` permite `ruff>=0.6`; con ruff 0.17.3 el código base no pasa el lint | E1b: 12 errores (I001, UP017) | `ruff check --fix`; se recomienda fijar la versión de ruff |
| 3 | `checkout` confirma el pedido antes de saber si el pago fue aceptado | `test_rejected_payment_should_not_leave_order_confirmed` (XFAIL) | Propuesta en E5 |
| 4 | CP08 del CSV describe el comportamiento previo al TDD (confirmaba dos veces) | `ESPERADO_TRAS_TDD` en `tests/test_casos_csv.py` | Esperado actualizado a `ValueError` |

## Tipos de prueba en este proyecto

| Tipo | Qué prueba | Dependencias reales | Archivos |
| :--- | :--- | :--- | :--- |
| Unitaria | Reglas de `Order` y `can_cancel` | Ninguna | `test_order.py`, `test_security.py`, `test_casos_csv.py` |
| Integración | `OrderService` con mock de pasarela y `SqlOrderRepository` con SQLite en memoria | Base de datos de prueba | `test_repository.py`, `test_service.py`, `test_integration.py` |
| E2E | No existe en el proyecto base (no hay API ni interfaz) | — | Solo escenario propuesto |

**Escenario E2E propuesto (no implementado):** un cliente VIP crea un pedido de 200 por la API; el sistema cobra 170 con la pasarela de pruebas, el pedido queda CONFIRMED en una base temporal y el dueño lo cancela dentro de las primeras 24 h.

## E1 · Instalación y ejecución

```text
$ python -m pytest -v
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.2.0, pluggy-1.7.0 -- /home/claude/u5/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/claude/u5/proyecto_u5
configfile: pyproject.toml
testpaths: tests
plugins: cov-7.1.0
collecting ... collected 13 items

tests/test_order.py::test_vip_discount PASSED                            [  7%]
tests/test_order.py::test_regular_no_discount PASSED                     [ 15%]
tests/test_order.py::test_customer_debt PASSED                           [ 23%]
tests/test_order.py::test_invalid_total[0] PASSED                        [ 30%]
tests/test_order.py::test_invalid_total[-1] PASSED                       [ 38%]
tests/test_repository.py::test_repository_commit PASSED                  [ 46%]
tests/test_repository.py::test_repository_rollback PASSED                [ 53%]
tests/test_security.py::test_owner_within_24h PASSED                     [ 61%]
tests/test_security.py::test_stranger_denied PASSED                      [ 69%]
tests/test_security.py::test_shipped_denied_even_admin PASSED            [ 76%]
tests/test_security.py::test_expired_denied PASSED                       [ 84%]
tests/test_service.py::test_gateway_approved PASSED                      [ 92%]
tests/test_service.py::test_gateway_rejected PASSED                      [100%]

============================== 13 passed in 0.26s ==============================
```

Explicación: `pytest` descubre las funciones `test_*` y reporta cuáles cumplen sus aserciones. El entorno virtual (`venv`) aísla las dependencias del curso para que el resultado sea reproducible en otra máquina.

Línea base de ruff y corrección del CI:

```text
$ python -m ruff check src tests  (línea base, antes de corregir)
src/domain.py:1:1: I001 [*] Import block is un-sorted or un-formatted
src/repository.py:1:1: I001 [*] Import block is un-sorted or un-formatted
src/security.py:1:1: I001 [*] Import block is un-sorted or un-formatted
src/security.py:4:31: UP017 [*] Use `datetime.UTC` alias
tests/test_order.py:1:1: I001 [*] Import block is un-sorted or un-formatted
tests/test_repository.py:1:1: I001 [*] Import block is un-sorted or un-formatted
tests/test_security.py:1:1: I001 [*] Import block is un-sorted or un-formatted
tests/test_security.py:5:24: UP017 [*] Use `datetime.UTC` alias
tests/test_security.py:9:24: UP017 [*] Use `datetime.UTC` alias
tests/test_security.py:13:24: UP017 [*] Use `datetime.UTC` alias
tests/test_security.py:17:24: UP017 [*] Use `datetime.UTC` alias
tests/test_service.py:1:1: I001 [*] Import block is un-sorted or un-formatted
Found 12 errors.
[*] 12 fixable with `--fix`.
```

```text
$ pytest -q --cov=src --cov-fail-under=80   (invocación exacta de CI)
.............                                                            [100%]
================================ tests coverage ================================
_______________ coverage: platform linux, python 3.12.3-final-0 ________________

Name                 Stmts   Miss  Cover
----------------------------------------
src/__init__.py          0      0   100%
src/application.py       8      0   100%
src/domain.py           17      0   100%
src/repository.py       18      0   100%
src/security.py          8      1    88%
----------------------------------------
TOTAL                   51      1    98%
Required test coverage of 80% reached. Total coverage: 98.04%
13 passed in 0.49s
```

Un defecto inyectado a propósito (descuento VIP 0.15 → 0.10) es detectado por la suite:

```text
$ (defecto inyectado: VIP_DISCOUNT_RATE 0.15 -> 0.10)  python -m pytest -q
E             comparison failed
E             comparison failed
E             comparison failed
E             comparison failed
        Raises an AssertionError if the args and keyword args passed in are
FAILED tests/test_casos_csv.py::test_casos_desde_csv[CP02] - assert 180.0 == ...
FAILED tests/test_casos_csv.py::test_casos_desde_csv[CP06] - assert 900.0 == ...
FAILED tests/test_casos_csv.py::test_casos_desde_csv[CP09] - assert 270.0 == ...
FAILED tests/test_casos_csv.py::test_casos_desde_csv[CP12] - assert 89.99 == ...
FAILED tests/test_integration.py::test_checkout_approved_then_order_is_persisted_as_confirmed
FAILED tests/test_order.py::test_vip_discount - AssertionError: assert 90.0 =...
FAILED tests/test_order.py::test_vip_discount_on_200 - assert 180.0 == 170
FAILED tests/test_service.py::test_gateway_rejected_for_vip_200_charges_170
8 failed, 39 passed, 1 xfailed in 0.37s
```

**Captura requerida:** tu terminal con `python -m pytest -v` y el resumen final.

## E2 · Pruebas unitarias nuevas (Arrange–Act–Assert)

| Entrada | Regla | Resultado esperado | Resultado real |
| :--- | :--- | :--- | :--- |
| Total 200, VIP | Descuento VIP 15 % | Cobro 170, descuento 30, CONFIRMED | PASSED |
| Total 200, regular | Sin descuento | Cobro 200, descuento 0, CONFIRMED | PASSED |

```text
$ python -m pytest tests/test_order.py -v
tests/test_order.py::test_vip_discount PASSED                            [ 14%]
tests/test_order.py::test_regular_no_discount PASSED                     [ 28%]
tests/test_order.py::test_customer_debt PASSED                           [ 42%]
tests/test_order.py::test_invalid_total[0] PASSED                        [ 57%]
tests/test_order.py::test_invalid_total[-1] PASSED                       [ 71%]
tests/test_order.py::test_vip_discount_on_200 PASSED                     [ 85%]
tests/test_order.py::test_regular_customer_pays_full_200 PASSED          [100%]
============================== 7 passed in 0.02s ===============================
```

**Captura requerida:** salida de `python -m pytest tests/test_order.py -v`.

## E3 · TDD: Red → Green → Refactor

Regla nueva: no confirmar un pedido ya confirmado.

**RED** (la prueba se escribió antes de tocar `src/domain.py`):

```text
$ python -m pytest tests/test_order.py::test_cannot_confirm_twice -v   (FASE RED)
============================= test session starts ==============================
collecting ... collected 1 item

tests/test_order.py::test_cannot_confirm_twice FAILED                    [100%]

=================================== FAILURES ===================================
__________________________ test_cannot_confirm_twice ___________________________

    def test_cannot_confirm_twice():
        order = Order(100)
        order.confirm()
>       with pytest.raises(ValueError, match="already confirmed"):
E       Failed: DID NOT RAISE ValueError

tests/test_order.py:45: Failed
=========================== short test summary info ============================
FAILED tests/test_order.py::test_cannot_confirm_twice - Failed: DID NOT RAISE...
============================== 1 failed in 0.03s ===============================
```

**GREEN** (implementación mínima):

```python
def confirm(self, customer_debt=0):
    if self.status == "CONFIRMED":
        raise ValueError("already confirmed")
    ...
```

```text
$ python -m pytest tests/test_order.py::test_cannot_confirm_twice -v   (FASE GREEN)
tests/test_order.py::test_cannot_confirm_twice PASSED                    [100%]
============================== 1 passed in 0.01s ===============================
--- suite completa tras GREEN ---
................                                                         [100%]
16 passed in 0.31s
```

**REFACTOR** (validaciones extraídas a `_ensure_confirmable`, mismo comportamiento):

```python
def confirm(self, customer_debt=0):
    self._ensure_confirmable(customer_debt)
    self.discount = round(self.total * VIP_DISCOUNT_RATE, 2) if self.vip else 0.0
    self.status = "CONFIRMED"
    return self.total - self.discount
```

```text
$ python -m pytest -v   (FASE REFACTOR: mismo comportamiento, suite completa)
tests/test_order.py::test_vip_discount PASSED                            [  6%]
tests/test_order.py::test_regular_no_discount PASSED                     [ 12%]
tests/test_order.py::test_customer_debt PASSED                           [ 18%]
tests/test_order.py::test_invalid_total[0] PASSED                        [ 25%]
tests/test_order.py::test_invalid_total[-1] PASSED                       [ 31%]
tests/test_order.py::test_vip_discount_on_200 PASSED                     [ 37%]
tests/test_order.py::test_regular_customer_pays_full_200 PASSED          [ 43%]
tests/test_order.py::test_cannot_confirm_twice PASSED                    [ 50%]
tests/test_repository.py::test_repository_commit PASSED                  [ 56%]
tests/test_repository.py::test_repository_rollback PASSED                [ 62%]
tests/test_security.py::test_owner_within_24h PASSED                     [ 68%]
tests/test_security.py::test_stranger_denied PASSED                      [ 75%]
tests/test_security.py::test_shipped_denied_even_admin PASSED            [ 81%]
tests/test_security.py::test_expired_denied PASSED                       [ 87%]
tests/test_service.py::test_gateway_approved PASSED                      [ 93%]
tests/test_service.py::test_gateway_rejected PASSED                      [100%]
============================== 16 passed in 0.28s ==============================
```

Por qué TDD no es ejecutar pruebas después de programar: la prueba roja demuestra que el defecto existe y que la prueba es capaz de detectarlo; el código se escribe solo para ponerla en verde y el refactor queda protegido por la suite. Una prueba escrita después nunca ha fallado, así que no hay evidencia de que detecte algo.

**Capturas requeridas:** salida RED, salida GREEN y suite completa tras el refactor.

## E4 · Persistencia, commit y rollback

```python
def test_repository_persists_second_order():
    engine = make_engine()
    with Session(engine) as session:
        SqlOrderRepository(session).save(2, Order(250))
        session.commit()
        row = session.scalar(select(OrderRow).where(OrderRow.id == 2))
        assert (row.id, row.total, row.status) == (2, 250, "NEW")
```

```text
$ python -m pytest tests/test_repository.py -v

tests/test_repository.py::test_repository_commit PASSED                  [ 25%]
tests/test_repository.py::test_repository_rollback PASSED                [ 50%]
tests/test_repository.py::test_repository_persists_second_order PASSED   [ 75%]
tests/test_repository.py::test_repository_rejects_duplicate_id_and_keeps_original PASSED [100%]

============================== 4 passed in 0.25s ===============================
```

Diferencia: `commit` hace permanentes los cambios de la transacción dentro de la base; `rollback` los descarta y la base queda como antes. Además se probó la restricción de unicidad: un segundo pedido con `id=1` lanza `IntegrityError` y se conserva el original (total 120). Todo ocurre en SQLite en memoria, sin datos reales.

**Captura requerida:** salida de `python -m pytest tests/test_repository.py -v`.

## E5 · Pasarela de pago con mocks

- Pago aprobado: el servicio devuelve el importe y la pasarela se llama una sola vez (`assert_called_once_with(100)`).
- Pago rechazado, VIP de 200: se lanza `RuntimeError("payment rejected")` y el intento de cobro fue por 170.
- Timeout: `TimeoutError` se propaga al llamador.
- Error de dominio (total 0): `charge` no se llama (`assert_not_called`).
- El mock usa `Mock(spec=["charge"])`: solo existe `charge`, no hay red ni dinero real.

```text
$ python -m pytest tests/test_service.py -v -rx

tests/test_service.py::test_gateway_approved PASSED                      [ 16%]
tests/test_service.py::test_gateway_rejected PASSED                      [ 33%]
tests/test_service.py::test_gateway_rejected_for_vip_200_charges_170 PASSED [ 50%]
tests/test_service.py::test_gateway_timeout_propagates PASSED            [ 66%]
tests/test_service.py::test_domain_error_never_reaches_gateway PASSED    [ 83%]
tests/test_service.py::test_rejected_payment_should_not_leave_order_confirmed XFAIL [100%]

=========================== short test summary info ============================
XFAIL tests/test_service.py::test_rejected_payment_should_not_leave_order_confirmed - RIESGO CONOCIDO: checkout confirma el pedido antes de saber si el pago fue aceptado
========================= 5 passed, 1 xfailed in 0.05s =========================
```

**Riesgo de consistencia (sin ocultarlo):** `checkout` ejecuta `order.confirm()` antes de cobrar. Si la pasarela rechaza o expira, el objeto queda en CONFIRMED sin pago. La prueba `test_rejected_payment_should_not_leave_order_confirmed` lo documenta con `xfail(strict=True)`.

Propuestas de mejora:

| Opción | Idea |
| :--- | :--- |
| A | Calcular el importe sin cambiar el estado, cobrar y marcar CONFIRMED solo si el cobro fue exitoso |
| B | Estado intermedio `PENDING_PAYMENT`; pasa a CONFIRMED al aprobarse el pago |
| C | Compensación: si el cobro falla, restaurar el estado anterior y no hacer commit |

**Captura requerida:** salida de `python -m pytest tests/test_service.py -v -rx`.

## E6 · Seguridad y autorización

Reglas implementadas: `SHIPPED` nunca se cancela (ni por administrador); para otros estados el administrador puede cancelar; el dueño no administrador solo durante las primeras 24 h (estrictamente menos de 24 h). Las pruebas usan una fecha fija y pasan `now` explícito.

| Rol | ¿Es el dueño? | Estado | Antigüedad | Resultado | Prueba |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Dueño | Sí | NEW | 1 h | Permitido | `dueno-1h-NEW` |
| Dueño | Sí | NEW | 23 h 59 min | Permitido | `dueno-23h59-NEW` |
| Dueño | Sí | NEW | 24 h | Denegado | `dueno-24h-NEW` |
| Dueño | Sí | NEW | 25 h | Denegado | `dueno-25h-NEW` |
| Tercero | No | NEW | 1 h | Denegado | `tercero-1h-NEW` |
| Administrador | No | NEW | 100 h | Permitido | `admin-tercero-NEW` |
| Dueño | Sí | CONFIRMED | 1 h | Permitido | `dueno-1h-CONFIRMED` |
| Dueño | Sí | SHIPPED | 1 h | Denegado | `dueno-SHIPPED` |
| Administrador | No | SHIPPED | 1 h | Denegado | `admin-SHIPPED` |

```text
$ python -m pytest tests/test_security.py -v

tests/test_security.py::test_owner_within_24h PASSED                     [  6%]
tests/test_security.py::test_stranger_denied PASSED                      [ 12%]
tests/test_security.py::test_shipped_denied_even_admin PASSED            [ 18%]
tests/test_security.py::test_expired_denied PASSED                       [ 25%]
tests/test_security.py::test_admin_cancels_new_order_of_another_user PASSED [ 31%]
tests/test_security.py::test_owner_at_exactly_24h_denied PASSED          [ 37%]
tests/test_security.py::test_default_now_is_used_when_not_provided PASSED [ 43%]
tests/test_security.py::test_authorization_matrix[dueno-1h-NEW] PASSED   [ 50%]
tests/test_security.py::test_authorization_matrix[dueno-23h59-NEW] PASSED [ 56%]
tests/test_security.py::test_authorization_matrix[dueno-24h-NEW] PASSED  [ 62%]
tests/test_security.py::test_authorization_matrix[dueno-25h-NEW] PASSED  [ 68%]
tests/test_security.py::test_authorization_matrix[tercero-1h-NEW] PASSED [ 75%]
tests/test_security.py::test_authorization_matrix[admin-tercero-NEW] PASSED [ 81%]
tests/test_security.py::test_authorization_matrix[dueno-1h-CONFIRMED] PASSED [ 87%]
tests/test_security.py::test_authorization_matrix[dueno-SHIPPED] PASSED  [ 93%]
tests/test_security.py::test_authorization_matrix[admin-SHIPPED] PASSED  [100%]

============================== 16 passed in 0.02s ==============================
```

**Captura requerida:** salida de `python -m pytest tests/test_security.py -v`.

## E7 · Cobertura y calidad

```text
$ python -m ruff check src tests
All checks passed!

$ python -m pytest -v --cov=src --cov-report=term-missing --cov-report=html --cov-fail-under=80
============================= test session starts ==============================

tests/test_casos_csv.py::test_casos_desde_csv[CP01] PASSED               [  2%]
tests/test_casos_csv.py::test_casos_desde_csv[CP02] PASSED               [  4%]
tests/test_casos_csv.py::test_casos_desde_csv[CP03] PASSED               [  6%]
tests/test_casos_csv.py::test_casos_desde_csv[CP04] PASSED               [  8%]
tests/test_casos_csv.py::test_casos_desde_csv[CP05] PASSED               [ 10%]
tests/test_casos_csv.py::test_casos_desde_csv[CP06] PASSED               [ 12%]
tests/test_casos_csv.py::test_casos_desde_csv[CP07] PASSED               [ 14%]
tests/test_casos_csv.py::test_casos_desde_csv[CP08] PASSED               [ 16%]
tests/test_casos_csv.py::test_casos_desde_csv[CP09] PASSED               [ 18%]
tests/test_casos_csv.py::test_casos_desde_csv[CP10] PASSED               [ 20%]
tests/test_casos_csv.py::test_casos_desde_csv[CP11] PASSED               [ 22%]
tests/test_casos_csv.py::test_casos_desde_csv[CP12] PASSED               [ 25%]
tests/test_integration.py::test_checkout_approved_then_order_is_persisted_as_confirmed PASSED [ 27%]
tests/test_integration.py::test_rejected_payment_and_rollback_leave_database_empty PASSED [ 29%]
tests/test_order.py::test_vip_discount PASSED                            [ 31%]
tests/test_order.py::test_regular_no_discount PASSED                     [ 33%]
tests/test_order.py::test_customer_debt PASSED                           [ 35%]
tests/test_order.py::test_invalid_total[0] PASSED                        [ 37%]
tests/test_order.py::test_invalid_total[-1] PASSED                       [ 39%]
tests/test_order.py::test_vip_discount_on_200 PASSED                     [ 41%]
tests/test_order.py::test_regular_customer_pays_full_200 PASSED          [ 43%]
tests/test_order.py::test_cannot_confirm_twice PASSED                    [ 45%]
tests/test_repository.py::test_repository_commit PASSED                  [ 47%]
tests/test_repository.py::test_repository_rollback PASSED                [ 50%]
tests/test_repository.py::test_repository_persists_second_order PASSED   [ 52%]
tests/test_repository.py::test_repository_rejects_duplicate_id_and_keeps_original PASSED [ 54%]
tests/test_security.py::test_owner_within_24h PASSED                     [ 56%]
tests/test_security.py::test_stranger_denied PASSED                      [ 58%]
tests/test_security.py::test_shipped_denied_even_admin PASSED            [ 60%]
tests/test_security.py::test_expired_denied PASSED                       [ 62%]
tests/test_security.py::test_admin_cancels_new_order_of_another_user PASSED [ 64%]
tests/test_security.py::test_owner_at_exactly_24h_denied PASSED          [ 66%]
tests/test_security.py::test_default_now_is_used_when_not_provided PASSED [ 68%]
tests/test_security.py::test_authorization_matrix[dueno-1h-NEW] PASSED   [ 70%]
tests/test_security.py::test_authorization_matrix[dueno-23h59-NEW] PASSED [ 72%]
tests/test_security.py::test_authorization_matrix[dueno-24h-NEW] PASSED  [ 75%]
tests/test_security.py::test_authorization_matrix[dueno-25h-NEW] PASSED  [ 77%]
tests/test_security.py::test_authorization_matrix[tercero-1h-NEW] PASSED [ 79%]
tests/test_security.py::test_authorization_matrix[admin-tercero-NEW] PASSED [ 81%]
tests/test_security.py::test_authorization_matrix[dueno-1h-CONFIRMED] PASSED [ 83%]
tests/test_security.py::test_authorization_matrix[dueno-SHIPPED] PASSED  [ 85%]
tests/test_security.py::test_authorization_matrix[admin-SHIPPED] PASSED  [ 87%]
tests/test_service.py::test_gateway_approved PASSED                      [ 89%]
tests/test_service.py::test_gateway_rejected PASSED                      [ 91%]
tests/test_service.py::test_gateway_rejected_for_vip_200_charges_170 PASSED [ 93%]
tests/test_service.py::test_gateway_timeout_propagates PASSED            [ 95%]
tests/test_service.py::test_domain_error_never_reaches_gateway PASSED    [ 97%]
tests/test_service.py::test_rejected_payment_should_not_leave_order_confirmed XFAIL [100%]

---------------------- generated xml file: /tmp/junit.xml ----------------------
================================ tests coverage ================================
_______________ coverage: platform linux, python 3.12.3-final-0 ________________

Name                 Stmts   Miss  Cover   Missing
--------------------------------------------------
src/__init__.py          0      0   100%
src/application.py       8      0   100%
src/domain.py           22      0   100%
src/repository.py       18      0   100%
src/security.py          8      0   100%
--------------------------------------------------
TOTAL                   56      0   100%
Coverage HTML written to dir htmlcov
Required test coverage of 80% reached. Total coverage: 100.00%
=========================== short test summary info ============================
XFAIL tests/test_service.py::test_rejected_payment_should_not_leave_order_confirmed - RIESGO CONOCIDO: checkout confirma el pedido antes de saber si el pago fue aceptado
======================== 47 passed, 1 xfailed in 0.62s =========================
```

La cobertura de líneas es 100 %, pero eso no significa que no haya comportamientos sin probar. Ejemplos reales que ninguna prueba ejercita:

- `can_cancel` con `created_at` sin zona horaria lanza `TypeError` (no se puede restar fecha ingenua y fecha con zona); no hay regla ni prueba que defina qué debe pasar.
- `OrderRow` no tiene columna de descuento: el repositorio guarda el total sin descuento y el estado, no el importe cobrado.
- `customer_debt` negativo se trata como "sin deuda"; no hay prueba que fije ese comportamiento.

**Capturas requeridas:** resumen de cobertura en terminal y `evidencias/reporte_cobertura_html/index.html` abierto en el navegador.

## E8 · GitHub Actions

Simulación local del ciclo verde → rojo → verde con los mismos pasos que `ci.yml` (no sustituye la ejecución en GitHub):

```text
== COMMIT 1 (verde) ==
1db7138 Unidad 5: pruebas y CI
All checks passed!
Required test coverage of 80% reached. Total coverage: 100.00%
======================== 47 passed, 1 xfailed in 0.57s =========================
CI local: OK
codigo_de_salida=0

== COMMIT 2 (rojo: aserción falsa) ==
3e9fcdc ROMPER: aserción falsa (fallo controlado)
All checks passed!
tests/test_order.py::test_vip_discount FAILED                            [ 31%]
E       AssertionError: assert 85.0 == 86
tests/test_order.py:8: AssertionError
Required test coverage of 80% reached. Total coverage: 100.00%
FAILED tests/test_order.py::test_vip_discount - AssertionError: assert 85.0 =...
codigo_de_salida=1

== COMMIT 3 (revertido, verde otra vez) ==
1883e1f Revert "ROMPER: aserción falsa (fallo controlado)"
All checks passed!
Required test coverage of 80% reached. Total coverage: 100.00%
======================== 47 passed, 1 xfailed in 0.59s =========================
CI local: OK
codigo_de_salida=0

== historial ==
1883e1f Revert "ROMPER: aserción falsa (fallo controlado)"
3e9fcdc ROMPER: aserción falsa (fallo controlado)
1db7138 Unidad 5: pruebas y CI
```

Lo que debes hacer tú en GitHub:

```bash
git init
git add .
git commit -m "Unidad 5: pruebas y CI"
git branch -M main
git remote add origin URL_DE_TU_REPOSITORIO
git push -u origin main
```

Después rompe una aserción (por ejemplo `assert o.confirm() == 85` → `== 86` en `tests/test_order.py`), haz commit y push, y revierte con `git revert HEAD`. La protección de rama (branch protection / rulesets) se configura aparte; el YAML por sí solo no bloquea merges.

**Entregables E8:** URL del repositorio y capturas de la pestaña Actions (workflow *CI Business Logic*) en verde, rojo y verde.

## E9 · Aplicación al PIA

Pendiente: requiere las reglas aprobadas de tu empresa (mínimo 3 reglas × éxito, error y límite = 9 casos; una prueba de persistencia y, si hay servicio externo, una con mock).

| ID | Regla | Entrada | Resultado esperado | Tipo |
| :--- | :--- | :--- | :--- | :--- |
| CP-PIA-01 | | | | Éxito |
| CP-PIA-02 | | | | Error |
| CP-PIA-03 | | | | Límite |

## Registro de uso de IA

| Campo | Detalle |
| :--- | :--- |
| Prompt usado | |
| Caso sugerido y corregido | Tomar el resultado esperado de CP08 desde el CSV (`CONFIRMED`) habría hecho fallar la prueba después del TDD |
| Corrección manual | `ESPERADO_TRAS_TDD = {"CP08": "ValueError"}` en `tests/test_casos_csv.py` |
| Prueba añadida | `test_cannot_confirm_twice` y la parametrización desde `datos/casos_de_prueba.csv` |

## Reflexión final (borrador de unas 165 palabras; personalízalo)

El defecto más costoso en producción sería cobrar mal o dejar confirmado un pedido cuyo pago fue rechazado. En este proyecto el servicio de checkout confirma el pedido antes de saber si la pasarela aceptó el cobro, de modo que un rechazo deja el objeto en estado CONFIRMED sin pago: la empresa entregaría mercancía sin cobrarla. Otro defecto grave sería permitir confirmar dos veces el mismo pedido, porque podría duplicar cobros. Las pruebas que lo evitan son test_cannot_confirm_twice, que nació del ciclo TDD, y test_rejected_payment_should_not_leave_order_confirmed, que combina un mock de la pasarela con la verificación del estado final y hoy está marcada como xfail estricta para dejar visible el riesgo hasta corregirlo. También comprobé que el 100 % de cobertura no demuestra corrección: el riesgo del checkout existía con todas las líneas ejecutadas. Las pruebas valen por sus aserciones y por los escenarios que cubren, no por el porcentaje, y el pipeline garantiza que ningún cambio posterior rompa estas reglas sin que alguien lo note.

## Autoevaluación

- [x] Una prueba unitaria no requiere base de datos (dominio y seguridad se prueban sin SQLAlchemy)
- [x] Evidencia real de RED y GREEN
- [x] Diferencia entre commit y rollback
- [x] El mock no genera cargo real (`Mock(spec=["charge"])`)
- [x] Permisos y límites temporales comprobados con fechas fijas
- [x] Cobertura ≥ 80 % sin ocultar módulos (`src/` completo)
- [ ] Pipeline ejecutado en GitHub y fallo detectado (E8, depende de tu repositorio)
- [ ] Nueve casos del PIA con reglas reales de tu empresa (E9)

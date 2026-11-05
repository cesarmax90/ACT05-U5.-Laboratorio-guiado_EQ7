# Evidencias · Laboratorio guiado Unidad 5 (CLN)

| Dato | Valor |
| :--- | :--- |
| Equipo | EQ7 |
| Integrantes y matrícula | Cesar Maximiliano Peña Mendoza · 2144135 <br> Diego Alberto Sierra Mendoza · 2143733 <br> Arturo Sebastian Pérez Zapata · 2142942 |
| Empresa del PIA | En definición (ver E9) |
| Repositorio GitHub | https://github.com/cesarmax90/ACT05-U5.-Laboratorio-guiado_EQ7 |

## Resumen de resultados

| Verificación | Resultado |
| :--- | :--- |
| Pruebas | 47 PASSED y 1 XFAIL esperada (proyecto base: 13) |
| Cobertura de líneas sobre `src/` | 100 % (55 sentencias; umbral 80 %) |
| `ruff check src tests` | Sin errores |
| Matriz de casos (`datos/matriz_casos_prueba.csv`) | 20 casos: 7 éxito, 9 error, 4 límite; todos PASSED |
| Pipeline en GitHub Actions | Ver E8 |

## Hallazgos del proyecto base

| # | Hallazgo | Evidencia | Acción |
| :-- | :--- | :--- | :--- |
| 1 | El CI ejecuta `pytest` y no `python -m pytest`; así `src` no es importable | `ModuleNotFoundError: No module named 'src'` en las 4 suites | `pythonpath = ["."]` en `pyproject.toml` |
| 2 | `requirements.txt` permite `ruff>=0.6`; con ruff 0.17.3 el código base no pasa el lint | `evidencias/E1b_ruff_base.txt`: 12 errores (I001, UP017) | `ruff check --fix`; se recomienda fijar la versión de ruff |
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

Comando: `python -m pytest -v` (la salida completa se capturó en dos imágenes consecutivas).

![E1 - pytest, primera parte](evidencias/Capturas/E1.jpeg)

![E1 - pytest, segunda parte y resumen: 47 passed, 1 xfailed](evidencias/Capturas/E1.2.jpeg)

Explicación: `pytest` descubre las funciones `test_*` y reporta cuáles cumplen sus aserciones. El entorno virtual (`venv`) aísla las dependencias del curso para que el resultado sea reproducible en otra máquina.

**Ruff en el proyecto base.** Con ruff 0.17.3 el código original marcaba 12 errores (`I001` imports sin ordenar y `UP017` alias `datetime.UTC`), corregidos con `ruff check --fix`. Salida completa en `evidencias/E1b_ruff_base.txt`.

**La suite detecta defectos.** Al inyectar un defecto a propósito (`VIP_DISCOUNT_RATE` de 0.15 a 0.10), la suite falló en 8 pruebas (`8 failed, 39 passed, 1 xfailed`), entre ellas `test_vip_discount` y `test_vip_discount_on_200`. Salida completa en `evidencias/E1d_defecto_detectado.txt`.

## E2 · Pruebas unitarias nuevas (Arrange–Act–Assert)

```python
def test_vip_discount_on_200():
    # Arrange
    order = Order(200, vip=True)
    # Act
    charge = order.confirm()
    # Assert
    assert charge == 170
    assert order.discount == 30
    assert order.status == "CONFIRMED"


def test_regular_customer_pays_full_200():
    order = Order(200)
    assert order.confirm() == 200
    assert order.discount == 0
    assert order.status == "CONFIRMED"
```

| Entrada | Regla | Resultado esperado | Resultado real |
| :--- | :--- | :--- | :--- |
| Total 200, VIP | Descuento VIP 15 % | Cobro 170, descuento 30, CONFIRMED | PASSED |
| Total 200, regular | Sin descuento | Cobro 200, descuento 0, CONFIRMED | PASSED |

Comando: `python -m pytest tests/test_order.py -v`

![E2 - pruebas de dominio, 8 passed](evidencias/Capturas/E2.jpeg)

## E3 · TDD: Red → Green → Refactor

Regla nueva: no confirmar un pedido ya confirmado.

**RED.** La prueba se escribió antes de tocar `src/domain.py` y falla porque la versión inicial permite confirmar dos veces:

```python
def test_cannot_confirm_twice():
    order = Order(100)
    order.confirm()
    with pytest.raises(ValueError, match="already confirmed"):
        order.confirm()
```

![E3 - fase RED: DID NOT RAISE ValueError](evidencias/Capturas/E3%20Fase%20RED.jpeg)

**GREEN.** Implementación mínima al inicio de `confirm()`:

```python
def confirm(self, customer_debt=0):
    if self.status == "CONFIRMED":
        raise ValueError("already confirmed")
    ...
```

![E3 - fase GREEN: 1 passed](evidencias/Capturas/E3%20Fase%20GREEN.jpeg)

**REFACTOR.** Las validaciones se extrajeron a `_ensure_confirmable`, sin cambiar el comportamiento:

```python
def confirm(self, customer_debt=0):
    self._ensure_confirmable(customer_debt)
    self.discount = round(self.total * VIP_DISCOUNT_RATE, 2) if self.vip else 0.0
    self.status = "CONFIRMED"
    return self.total - self.discount
```

La suite completa en verde después del refactor es la de las capturas de E1 (47 passed, 1 xfailed).

Por qué TDD no es ejecutar pruebas después de programar: la prueba roja demuestra que el defecto existe y que la prueba es capaz de detectarlo; el código se escribe solo para ponerla en verde y el refactor queda protegido por la suite. Una prueba escrita después nunca ha fallado, así que no hay evidencia de que detecte algo.

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

Comando: `python -m pytest tests/test_repository.py -v`

![E4 - pruebas del repositorio, 4 passed](evidencias/Capturas/E4.jpeg)

Diferencia: `commit` hace permanentes los cambios de la transacción dentro de la base; `rollback` los descarta y la base queda como antes. Además se probó la restricción de unicidad: un segundo pedido con `id=1` lanza `IntegrityError` y se conserva el original (total 120). Todo ocurre en SQLite en memoria, sin datos reales.

## E5 · Pasarela de pago con mocks

- Pago aprobado: el servicio devuelve el importe y la pasarela se llama una sola vez (`assert_called_once_with(100)`).
- Pago rechazado, VIP de 200: se lanza `RuntimeError("payment rejected")` y el intento de cobro fue por 170.
- Timeout: `TimeoutError` se propaga al llamador.
- Error de dominio (total 0): `charge` no se llama (`assert_not_called`).
- El mock usa `Mock(spec=["charge"])`: solo existe `charge`, no hay red ni dinero real.

Comando: `python -m pytest tests/test_service.py -v -rx`

![E5 - pruebas del servicio con mock, 5 passed y 1 xfailed](evidencias/Capturas/E5.jpeg)

**Riesgo de consistencia (sin ocultarlo).** `checkout` ejecuta `order.confirm()` antes de cobrar. Si la pasarela rechaza o expira, el objeto queda en CONFIRMED sin pago. La prueba `test_rejected_payment_should_not_leave_order_confirmed` lo documenta con `xfail(strict=True)`.

Propuestas de mejora:

| Opción | Idea |
| :--- | :--- |
| A | Calcular el importe sin cambiar el estado, cobrar y marcar CONFIRMED solo si el cobro fue exitoso |
| B | Estado intermedio `PENDING_PAYMENT`; pasa a CONFIRMED al aprobarse el pago |
| C | Compensación: si el cobro falla, restaurar el estado anterior y no hacer commit |

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

Comando: `python -m pytest tests/test_security.py -v`

![E6 - pruebas de autorización, 16 passed](evidencias/Capturas/E6.jpeg)

## E7 · Cobertura y calidad

Comandos: `python -m ruff check src tests` y `python -m pytest -v --cov=src --cov-report=term-missing --cov-report=html --cov-fail-under=80`

![E7 - ruff sin errores y resumen de cobertura en terminal: 100 %](evidencias/Capturas/E7%20resumen%20en%20cobertura%20en%20terminal.jpeg)

Reporte HTML (`htmlcov/index.html`, copia en `evidencias/reporte_cobertura_html/`):

![E7 - reporte HTML de cobertura: 100 %, 55 sentencias](evidencias/Capturas/E7%20Resumen%20del%20navegador.jpeg)

La cobertura de líneas es 100 %, pero eso no significa que no haya comportamientos sin probar. Ejemplos reales que ninguna prueba ejercita:

- `can_cancel` con `created_at` sin zona horaria lanza `TypeError` (no se puede restar fecha ingenua y fecha con zona); no hay regla ni prueba que defina qué debe pasar.
- `OrderRow` no tiene columna de descuento: el repositorio guarda el total sin descuento y el estado, no el importe cobrado.
- `customer_debt` negativo se trata como "sin deuda"; no hay prueba que fije ese comportamiento.

Observación: al terminar la ejecución aparecen dos `ResourceWarning` por conexiones SQLite que no se cierran explícitamente en las pruebas de integración. No afectan los resultados; la mejora sería cerrar el motor (`engine.dispose()`) al final de cada prueba.

## E8 · GitHub Actions

Repositorio: https://github.com/cesarmax90/ACT05-U5.-Laboratorio-guiado_EQ7

El workflow `CI Business Logic` (`.github/workflows/ci.yml`) se ejecuta en cada push y pull request: instala dependencias, corre `ruff`, `pytest` con cobertura y umbral de 80 %, `compileall` y publica el reporte `htmlcov` como artefacto.

Simulación local del ciclo verde → rojo → verde con los mismos pasos del workflow (`scripts/ci_local.sh`):

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
FAILED tests/test_order.py::test_vip_discount - AssertionError: assert 85.0 =...
codigo_de_salida=1

== COMMIT 3 (revertido, verde otra vez) ==
1883e1f Revert "ROMPER: aserción falsa (fallo controlado)"
All checks passed!
Required test coverage of 80% reached. Total coverage: 100.00%
======================== 47 passed, 1 xfailed in 0.59s =========================
CI local: OK
codigo_de_salida=0
```

Qué detecta el pipeline: con una aserción falsa (`assert o.confirm() == 85` cambiada a `== 86`) `pytest` termina con código de salida 1, el job falla y el cambio defectuoso queda marcado en rojo; al revertir el commit el pipeline regresa a verde. La protección obligatoria de merge requeriría configurar branch protection o rulesets en GitHub; el YAML por sí solo no la activa.

### Ejecuciones en GitHub Actions

<!-- AGREGAR AQUÍ: captura 1 (ejecución verde), captura 2 (ejecución roja), captura 3 (ejecución verde tras revertir) de la pestaña Actions -->

## E9 · Aplicación al PIA

En desarrollo junto con el PIA del equipo: mínimo 3 reglas reales de la empresa × (éxito, error y límite) = 9 casos, con una prueba de persistencia y, si hay servicio externo, una prueba con mock.

| ID | Regla | Entrada | Resultado esperado | Tipo |
| :--- | :--- | :--- | :--- | :--- |
| CP-PIA-01 | | | | Éxito |
| CP-PIA-02 | | | | Error |
| CP-PIA-03 | | | | Límite |

<!-- AGREGAR AQUÍ: matriz CSV de 9 casos, pruebas, cobertura y decisiones de diseño del PIA -->

## Registro de uso de IA

| Campo | Detalle |
| :--- | :--- |
| Prompt usado | |
| Caso sugerido y corregido | Tomar el resultado esperado de CP08 desde el CSV (`CONFIRMED`) habría hecho fallar la prueba después del TDD |
| Corrección manual | `ESPERADO_TRAS_TDD = {"CP08": "ValueError"}` en `tests/test_casos_csv.py` |
| Prueba añadida | `test_cannot_confirm_twice` y la parametrización desde `datos/casos_de_prueba.csv` |

## Reflexión final

El defecto más costoso en producción sería cobrar mal o dejar confirmado un pedido cuyo pago fue rechazado. En nuestro proyecto, el servicio de checkout confirma el pedido antes de saber si la pasarela aceptó el cobro; si el pago se rechaza o expira, el pedido queda en estado CONFIRMED sin haberse pagado y la empresa entregaría mercancía sin cobrarla. Otro defecto grave sería permitir confirmar dos veces el mismo pedido, porque podría duplicar cobros. Dos pruebas evitan estos casos: test_cannot_confirm_twice, que surgió del ciclo TDD, y test_rejected_payment_should_not_leave_order_confirmed, que usa un mock de la pasarela para verificar el estado final y está marcada como xfail estricta para dejar visible el riesgo hasta que se corrija. También comprobamos que el 100 % de cobertura no demuestra corrección: el riesgo del checkout existía con todas las líneas ejecutadas. Lo que da valor a una prueba son sus aserciones y los escenarios que cubre, no el porcentaje, y el pipeline de integración continua evita que un cambio posterior rompa estas reglas sin que el equipo se entere.

## Autoevaluación

- [x] Una prueba unitaria no requiere base de datos (dominio y seguridad se prueban sin SQLAlchemy)
- [x] Evidencia real de RED y GREEN
- [x] Diferencia entre commit y rollback
- [x] El mock no genera cargo real (`Mock(spec=["charge"])`)
- [x] Permisos y límites temporales comprobados con fechas fijas
- [x] Cobertura ≥ 80 % sin ocultar módulos (`src/` completo)
- [ ] Pipeline ejecutado en GitHub y fallo detectado (E8)
- [ ] Nueve casos del PIA con reglas reales de la empresa (E9)

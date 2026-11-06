# pia_novarent · Reglas de NovaRent probadas (Unidad 5, E9)

Adaptación del laboratorio de la Unidad 5 a la empresa del PIA (NovaRent, renta de autos). Las reglas salen del BRD, las User Stories y el diseño arquitectural de las Unidades 2 y 3. La carpeta es autocontenida: se puede copiar tal cual al repositorio del PIA.

## Reglas probadas

| Regla | US | Parámetros | Clase |
| :--- | :--- | :--- | :--- |
| Cargo por kilometraje excedente | US14 | 200 km/día incluidos, $3 MXN por km extra | `PoliticaCargos` |
| Autorización de extensión por rol | US11, US12 | Agente hasta 48 h; más, Administración; solicitud con 2 h o más de anticipación | `PoliticaExtension` |
| Cancelación y no-show | US03, US04 | Gratis con 24 h o más; no-show se libera a las 2 h | `PoliticaCancelacion` |

Además: persistencia de `Reservacion` con SQLAlchemy y SQLite en memoria (commit, rollback, unicidad) y apertura de contrato con la `PasarelaPago` simulada con un mock (nunca hay cobros reales).

## Estructura

| Ruta | Contenido |
| :--- | :--- |
| `novarent/politicas.py` | Políticas parametrizables (sin dependencias externas) |
| `novarent/dominio.py` | `Reservacion` y `ContratoRenta` |
| `novarent/aplicacion.py` | `ContratoAppService`: coordina, no decide reglas |
| `novarent/repositorio.py` | `SqlReservacionRepository` (SQLAlchemy) |
| `tests/test_reglas_novarent.py` | Pruebas unitarias de las reglas |
| `tests/test_integracion_novarent.py` | Persistencia y mock de la pasarela |
| `datos/matriz_casos_pia.csv` | Matriz de 20 casos (6 éxito, 6 error, 8 límite) con resultado real |

## Ejecución

Desde esta carpeta, con las dependencias del `requirements.txt` del repositorio raíz:

```bash
python -m ruff check novarent tests
python -m pytest -v --cov=novarent --cov-report=term-missing --cov-fail-under=80
```

El pipeline de GitHub Actions ejecuta estos mismos comandos en el job `pia_novarent`.

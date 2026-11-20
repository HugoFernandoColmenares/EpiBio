# Arquitectura de EpiBio

**Autor:** [HugoFernandoColmenares](https://github.com/HugoFernandoColmenares)  
**Versión:** 0.1.0  
**Fecha:** 2026-11-20  
**Estado:** Implementación base (pipeline CLI); capa FastAPI/Angular marcada como evolución

---

## 1. Propósito

EpiBio es un pipeline reproducible de bioinformática que compara comunidades microbianas (abundancias 16S) entre superficies de acero corroído y sedimentos marinos profundos, a partir de datos públicos de EMBL-EBI (MGnify + ENA).

El sistema transforma datos crudos en métricas ecológicas (diversidad alfa/beta, PCoA, PERMANOVA) y visualizaciones HTML, sin claves de API ni infraestructura pesada.

---

## 2. Principios de diseño

| Principio | Cómo se aplica |
| :--- | :--- |
| **SRP** | Un módulo = una responsabilidad. Red, taxonomía, estadística, visualización y orquestación viven separados. |
| **OCP** | Rangos taxonómicos, grupos funcionales (SRB) y accesiones de estudio son datos declarativos; el núcleo estadístico no se reescribe al cambiar de estudio. |
| **LSP / ISP** | No hay jerarquías de clases; los contratos son firmas de funciones puras sobre `DataFrame` / `DistanceMatrix`. |
| **DIP** | `diversidad` y `graficas` dependen de abstracciones de datos (tablas, series, matrices), no de rutas ni de HTTP. |
| **DRY** | `partir_linaje` es la única fuente de verdad del parsing; la semilla `SEMILLA = 42` unifica rarefacción y PERMANOVA. |
| **KISS** | Funciones puras en lugar de clases con estado. Sin ORM, sin cola de trabajos, sin notebook obligatorio. |

Flujo unidireccional (sin ciclos):

```text
[EMBL-EBI] → descarga → taxonomia → diversidad / graficas → reporte (CLI)
                                              ↓
                                    (evolución) FastAPI → Angular
```

---

## 3. Capas lógicas

```text
┌─────────────────────────────────────────────────────────────┐
│  Presentación                                               │
│  reporte.py (CLI) · graficas.py (HTML Plotly)               │
│  [evolución] api/ · web/                                    │
├─────────────────────────────────────────────────────────────┤
│  Dominio / análisis                                         │
│  taxonomia.py · diversidad.py                               │
├─────────────────────────────────────────────────────────────┤
│  Infraestructura                                            │
│  descarga.py (httpx → data/raw/)                            │
└─────────────────────────────────────────────────────────────┘
```

### 3.1 Infraestructura — `descarga.py`

- Cliente HTTP único (`_get`) con timeout y `User-Agent`.
- Descarga de tabla SSU (MGnify) y metadatos (ENA).
- Bitácora de procedencia en `DESCARGAS.txt` (ISO-8601 UTC).
- **No** conoce estadísticas ni taxonomía.

### 3.2 Dominio — `taxonomia.py`

- `partir_linaje`: linaje MGnify → diccionario de rangos (`None` si falta).
- `agrupar_por`: agregación por rango; incompletos → `"Sin asignar"`.
- `abundancia_relativa`: normalización columnar (suma = 1).
- `leer_tabla`: lectura del TSV con índice de linaje.

### 3.3 Dominio — `diversidad.py`

- Rarefacción determinista (`SEMILLA`).
- Alfa (Shannon, riqueza), Bray-Curtis, PCoA, PERMANOVA.
- Encapsula la transposición `tabla.T` (MGnify ≠ scikit-bio).
- Entrada/salida: DataFrames y matrices; sin I/O de archivos.

### 3.4 Presentación — `graficas.py` y `reporte.py`

- Plotly → HTML estático (`include_plotlyjs="cdn"`).
- `reporte.main` orquesta el pipeline e imprime el resumen.
- `clasificar(alias)` traduce alias ENA → grupo ecológico.

---

## 4. Contratos entre módulos

| Productor | Consumidor | Contrato |
| :--- | :--- | :--- |
| `descarga` | `reporte` | Archivos en `data/raw/` + bitácora |
| `taxonomia.leer_tabla` | `reporte`, `diversidad` | `DataFrame` (linajes × muestras) |
| `taxonomia.agrupar_por` | `reporte`, `graficas` | `DataFrame` agregado por rango |
| `diversidad.bray_curtis` | `ordenar`, `probar_grupos` | `DistanceMatrix` scikit-bio |
| `diversidad.ordenar` | `graficas` | coords (`PC1`, `PC2`) + % varianza |
| `reporte` | usuario / CLI | stdout + rutas HTML en `docs/` |

Reglas invariantes:

1. Las columnas de la tabla de abundancias coinciden con `meta["run_accession"]`.
2. Tras `abundancia_relativa`, cada columna suma ~1.0 (incluye `"Sin asignar"`).
3. Toda aleatoriedad usa `SEMILLA = 42`.

---

## 5. Estructura del repositorio

```text
EpiBio/  (paquete: epibio)
├── pyproject.toml
├── uv.lock
├── .python-version
├── .gitignore
├── LICENSE
├── README.md
├── data/
│   └── raw/                 # gitignored; TSV + DESCARGAS.txt
├── docs/
│   ├── files/               # especificaciones y este documento
│   ├── barras_generos.html  # generado por el pipeline
│   └── pcoa.html
├── src/
│   └── epibio/
│       ├── __init__.py      # entry point CLI `epibio`
│       ├── descarga.py
│       ├── taxonomia.py
│       ├── diversidad.py
│       ├── graficas.py
│       └── reporte.py
└── tests/
    ├── test_taxonomia.py
    └── test_diversidad.py
```

---

## 6. Decisiones técnicas clave

| Decisión | Motivo |
| :--- | :--- |
| Tabla SSU de MGnify (no FASTQ crudo) | Enseñar análisis, no instalar un pipeline de amplicones |
| Filtrar ENA por `AMPLICON` | El proyecto mezcla WGS; la tabla SSU solo cubre amplicones |
| Conservar `"Sin asignar"` | Mantiene ∑pᵢ = 1 y hace visible la incertidumbre taxonómica |
| Rarefacción con semilla fija | Comparabilidad entre muestras + reproducibilidad |
| Funciones puras | Menos superficie de estado; tests triviales |
| Constantes de estudio en código | Legibilidad del tutorial; CLI/config queda para evolución |

---

## 7. Extensibilidad (Open/Closed)

Para analizar otro estudio **sin** tocar `diversidad` ni `taxonomia`:

1. Cambiar `ESTUDIO`, `PROYECTO`, `TABLA` en `descarga.py`.
2. Ajustar `clasificar` en `reporte.py` a los alias del nuevo estudio.
3. Vaciar `data/raw/` y reejecutar el reporte.

Evolución prevista (sin romper el núcleo):

- Argumentos CLI / archivo de configuración para accesiones y grupos.
- Endpoints FastAPI que sirvan JSON tipado (Pydantic).
- SPA Angular (signals, OnPush) con estética deep-sea telemetry.

---

## 8. Calidad y pruebas

| Área | Cobertura |
| :--- | :--- |
| `partir_linaje` | Linaje completo, corto, `k__` vacío |
| `agrupar_por` + normalización | Agregación + ∑ columnas = 1 |
| `diversidad` | Matriz sintética: rarefacción a profundidad fija, alfa ≥ 0 |
| `clasificar` | Alias Sediment / MC*a / MC*b |

Ejecución: `uv run pytest -q` (8 passed en verificación 2026-11-20).

Además del unit test, el pipeline E2E se corre con `uv run python -m epibio.reporte` y se compara con el informe del artículo. Evidencia visual en `docs/screenshots/` y detalle en `docs/files/verificacion_e2e.md`.

| Captura | Contenido |
| :--- | :--- |
| `docs/screenshots/01_barras_generos.png` | Barras apiladas top géneros |
| `docs/screenshots/02_pcoa.png` | PCoA Bray-Curtis |
| `docs/screenshots/03_verificacion_consola.png` | Consola + comparación métrica |

---

## 9. Seguridad y procedencia de datos

- Sin secretos ni claves de API (endpoints públicos EMBL-EBI).
- `User-Agent` identificable y timeout de 60 s.
- `data/raw/` fuera de git; la bitácora documenta cuándo se descargó cada URL.
- Citar el artículo original (Rajala et al., 2022) y los términos de uso de EMBL-EBI al republicar resultados.

---

## 10. Relación con otros documentos

| Documento | Rol |
| :--- | :--- |
| `epibio_technical_specification.md` | Blueprint técnico y stack completo (incl. evolución web) |
| Artículo DevChronicle (borrador) | Caso de uso, código comentado e interpretación de resultados |
| `verificacion_e2e.md` | Evidencia de corrida real vs cifras del informe + capturas |
| **Este archivo** | Contrato arquitectónico SOLID/KISS/DRY que guía la implementación |

La implementación en `src/epibio/` debe respetar este documento. Cualquier desviación se documenta aquí primero.

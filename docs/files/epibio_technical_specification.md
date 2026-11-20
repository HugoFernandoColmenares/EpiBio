# Technical Specification & Architectural Blueprint: EpiBio (MIC Microbial Community Pipeline & Web Explorer)

## 1. Executive Summary & Core Vision

**EpiBio** is a reproducible bioinformatics data pipeline and full-stack analytical explorer designed to compare microbial communities (16S rRNA amplicon abundance profiles) between corroded marine steel surfaces and surrounding deep-sea sediments. 

Originating from research into **Microbially Influenced Corrosion (MIC)**, the system automates keyless data ingestion from public EMBL-EBI repositories (**MGnify** and **ENA**), parses complex taxonomic lineages, computes ecological diversity metrics (Alpha, Beta Bray-Curtis, PCoA, PERMANOVA), and scales from a lightweight CLI/Python package into a decoupled **FastAPI + Angular 22+** interactive laboratory dashboard.

---

## 2. Technology Stack & Tooling

### A. Core Bioinformatics & Data Engine (Current Implementation)
| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Runtime & Packaging** | Python 3.14+ & `uv` | Deterministic dependency locking (`uv.lock`), isolated virtual environments, and fast build execution. |
| **Data Manipulation** | `pandas` (3.1+) & `numpy` (2.5+) | Tabular taxonomy transformation, lineage parsing, relative abundance normalization, and matrix transposition. |
| **Biostatistics Engine** | `scikit-bio` (0.7.4+) | Deterministic rarefaction (`subsample_counts`), Shannon/Observed richness, Bray-Curtis dissimilarity, PCoA ordination, and PERMANOVA permutation testing. |
| **HTTP & Ingestion** | `httpx` (0.28+) | Resilient, timeout-guarded HTTP client with custom `User-Agent` headers for keyless EMBL-EBI API queries. |
| **Static Reporting** | `plotly` (7.1+) | Standalone interactive HTML visualizations (stacked bar charts and PCoA scatter plots). |
| **Testing Suite** | `pytest` (9.2+) | Unit verification for lineage parsing edge cases and normalization invariants. |

### B. Full-Stack Evolution Layer (Web Dashboard Architecture)
| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **API Gateway** | FastAPI (Python 3.14) | Exposes cached statistical outputs, PCoA coordinates, and taxonomic breakdowns via typed Pydantic schemas. |
| **Frontend Framework** | Angular 22+ (Standalone, Signals) | Reactive laboratory explorer utilizing Zoneless/OnPush change detection and modern `@if`/`@for` control flow. |
| **Styling & Layout** | Pure Vanilla CSS + Design Tokens | High-contrast scientific instrumentation UI using CSS Grid/Flexbox (`gap`-only spacing, zero margins). |

---

## 3. Architecture & Engineering Standards (SOLID, DRY, KISS)

The system is architected as a modular, stateless pipeline where data flows unidirectionally from raw ingestion to statistical inference and presentation:

```text
[EMBL-EBI APIs] ──► [descarga.py] ──► [data/raw/ + DESCARGAS.txt]
                                              │
                                              ▼
                                      [taxonomia.py] (Lineage Parsing & Normalization)
                                        │         │
                     ┌──────────────────┘         └──────────────────┐
                     ▼                                               ▼
             [diversidad.py] (Rarefaction, Alpha/Beta, PCoA)   [graficas.py] (Plotly HTML)
                     │                                               │
                     └──────────────────┬────────────────────────────┘
                                        ▼
                          [reporte.py / FastAPI Endpoint]
                                        │
                                        ▼
                        [Angular 22+ Laboratory Explorer]
```

### Adherence to Engineering Principles
* **Single Responsibility Principle (SRP):**
  * `descarga.py` handles network I/O and provenance logging (`DESCARGAS.txt`) exclusively, completely unaware of downstream statistics.
  * `taxonomia.py` isolates string parsing (`partir_linaje`) and matrix aggregation (`agrupar_por`).
  * `diversidad.py` encapsulates `scikit-bio` statistical routines without touching filesystem paths or visualization logic.
  * In the Angular layer, smart coordinator pages fetch DTOs via injected services (`inject()`), while pure presentational components render charts and metric cards.
* **Open/Closed Principle (OCP):**
  * Taxonomic ranks (`RANGOS`, `PREFIJOS`) and target functional groups (e.g., sulfate-reducing bacteria like *Desulfovibrio*) are defined as declarative structures, allowing researchers to extend functional groupings or switch study accessions (`MGYS...` / `PRJ...`) without modifying core statistical functions.
* **Dependency Inversion Principle (DIP):**
  * Statistical functions accept standard `pd.DataFrame` and `DistanceMatrix` abstractions rather than hardcoded file paths, enabling seamless unit testing with synthetic matrices.
* **DRY (Don't Repeat Yourself) & KISS (Keep It Simple, Stupid):**
  * Lineage splitting is centralized in a single pure function (`partir_linaje`) shared across aggregation pipelines and `pytest` suites.
  * Pure functions over stateful classes in the Python core—avoiding unnecessary OOP boilerplate where stateless data transformations suffice.
  * Deterministic reproducibility enforced via a single global random seed (`SEMILLA = 42`) across both rarefaction subsampling and PERMANOVA permutations.

---

## 4. Performance, Data Integrity & Optimization

* **Matrix Orientation Guardrails:** `scikit-bio` expects samples as rows and taxa as columns, whereas MGnify delivers taxa as rows. Transposition (`tabla.T`) is strictly encapsulated within `diversidad.py` to prevent silent statistical corruption.
* **Unassigned Taxa Preservation:** Incomplete 16S classifications (lineages lacking `g__`) are explicitly bucketed into `"Sin asignar"` rather than dropped, preserving exact column sums ($\sum p_i = 1.0$) for compositional accuracy.
* **Reproducible Provenance Ledger:** Every API fetch appends an ISO-8601 UTC timestamp and source URL to `data/raw/DESCARGAS.txt`, mitigating upstream database reprocessing drift.
* **Frontend Rendering Optimization:**
  * Angular components enforce `ChangeDetectionStrategy.OnPush` and granular `signal()` / `computed()` state primitives to prevent unnecessary re-renders when filtering 600+ taxonomic lineages.
  * Virtual scrolling (`@angular/cdk/scrolling`) or paginated taxonomic tables prevent DOM bloat when inspecting deep ASV/OTU abundance tables.

---

## 5. UI/UX Design System (Anti-Generic Aesthetic)

To avoid sterile, generic AI-generated templates, the visual interface adopts a **Deep-Sea Benthic Telemetry & Oceanographic Lab** aesthetic—evoking deep-sea mooring chains, sonar readouts, and oxidized marine steel:

* **Color Palette (CSS Custom Properties):**
  * *Primary Abyssal Dark Base:* Hadal Trench Black (`#090D14`) and Oxidized Hull Slate (`#111822`).
  * *Surface & Elevated Panels:* Pressurized Steel (`#182230`) with subtle structural borders (`#263447`).
  * *Dominant Warm / Rust Accents:* Corroded Iron Ochre (`#D96B27`) and Brass Telemetry Gold (`#E0A948`) representing steel mooring links.
  * *Sediment & Biological Contrasts:* Benthic Silt Sand (`#C2B280`) for sediment groups and Bioluminescent Sonar Teal (`#14B8A6`) for microbial diversity metrics.
* **Typography & Layout Constraints:**
  * Tabular monospace fonts (`JetBrains Mono` / `IBM Plex Mono`) for all numerical readouts ($p$-values, pseudo-$F$, Shannon indices, relative abundances) paired with crisp geometric sans-serif headings (`Space Grotesk` or `Inter`).
  * **Strict Spacing Rule (No-Margin Mandate):** Zero `margin` properties are permitted on sibling elements. All structural layouts rely exclusively on CSS Grid and Flexbox using explicit `gap` tokens, with internal `padding` managing container breathing room.
* **Accessibility (a11y):**
  * Color-blind safe categorical palettes (distinguishing `cadena-externa`, `cadena-interna`, and `sedimento` via both luminance contrast and distinct geometric point markers in PCoA scatter plots).
  * Full keyboard navigation (`aria-label`, focus rings, and tabular data screen-reader semantics) across all interactive plots and taxonomic filters.

---

## 6. Modular Directory Structure

```text
EpiBio/
├── pyproject.toml                  # uv package definition & Python 3.14 constraints
├── uv.lock                         # Deterministic dependency lockfile
├── data/
│   └── raw/                        # Git-ignored raw TSVs & DESCARGAS.txt ledger
├── docs/                           # Generated HTML plots & technical specs
├── src/
│   ├── epibio/                     # Core Python package (import: epibio)
│   │   ├── __init__.py             # CLI entry point
│   │   ├── descarga.py             # Keyless MGnify & ENA ingestion
│   │   ├── taxonomia.py            # Lineage splitting & relative abundance
│   │   ├── diversidad.py           # Rarefaction, Alpha/Beta, PCoA, PERMANOVA
│   │   ├── graficas.py             # Plotly interactive visualizations
│   │   └── reporte.py              # End-to-end pipeline orchestrator
│   └── api/                        # Optional FastAPI evolution layer
│       └── main.py                 # Typed REST endpoints serving JSON metrics
├── web/                            # Optional Angular 22+ Laboratory Explorer
│   └── src/app/
│       ├── core/                   # Data services & DTO interfaces
│       ├── shared/                 # Metric cards, taxonomic badges, Plotly wrappers
│       └── features/               # Ordination viewer, SRB abundance comparator
└── tests/
    ├── test_taxonomia.py           # Lineage parsing & normalization unit tests
    └── test_diversidad.py          # Synthetic matrix statistical verification
```
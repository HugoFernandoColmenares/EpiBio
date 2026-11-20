"""EpiBio — análisis de comunidades microbianas del estudio MGYS00006080 (MGnify)."""

__version__ = "0.1.0"


def main() -> None:
    from epibio.reporte import main as reporte

    reporte()

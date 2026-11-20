"""Limpieza de la tabla de abundancias: linaje en columnas y agrupación por rango."""
import pandas as pd

RANGOS = ["superreino", "reino", "filo", "clase", "orden", "familia", "genero", "especie"]
PREFIJOS = ["sk", "k", "p", "c", "o", "f", "g", "s"]


def partir_linaje(linaje: str) -> dict[str, str | None]:
    """'sk__Bacteria;k__;p__Proteobacteria' -> {'superreino': 'Bacteria', 'reino': None, ...}."""
    resultado: dict[str, str | None] = dict.fromkeys(RANGOS)
    for pedazo in linaje.split(";"):
        prefijo, _, nombre = pedazo.partition("__")
        if prefijo in PREFIJOS and nombre:
            resultado[RANGOS[PREFIJOS.index(prefijo)]] = nombre
    return resultado


def leer_tabla(ruta) -> pd.DataFrame:
    """Lee el TSV de MGnify: filas = linajes, columnas = corridas (SRR...)."""
    tabla = pd.read_csv(ruta, sep="\t", index_col=0)
    tabla.index.name = "linaje"
    return tabla


def agrupar_por(tabla: pd.DataFrame, rango: str) -> pd.DataFrame:
    """Suma conteos por rango; lo que no llega a ese nivel queda como 'Sin asignar'."""
    nombres = [partir_linaje(l)[rango] or "Sin asignar" for l in tabla.index]
    return tabla.groupby(nombres).sum()


def abundancia_relativa(tabla: pd.DataFrame) -> pd.DataFrame:
    """Cada columna (muestra) pasa a proporciones que suman 1."""
    return tabla / tabla.sum(axis=0)

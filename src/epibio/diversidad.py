"""Diversidad alfa, beta (Bray-Curtis), PCoA y PERMANOVA con scikit-bio."""
import numpy as np
import pandas as pd
from skbio.diversity import alpha_diversity, beta_diversity
from skbio.stats import subsample_counts
from skbio.stats.distance import permanova
from skbio.stats.ordination import pcoa

SEMILLA = 42


def rarefaccion(tabla: pd.DataFrame, profundidad: int | None = None) -> pd.DataFrame:
    """Submuestrea cada muestra a la misma cantidad de lecturas (la de la muestra más pequeña)."""
    profundidad = profundidad or int(tabla.sum(axis=0).min())
    rng = np.random.default_rng(SEMILLA)
    columnas = {}
    for muestra in tabla.columns:
        conteos = tabla[muestra].to_numpy(dtype=int)
        columnas[muestra] = subsample_counts(conteos, profundidad, seed=rng)
    return pd.DataFrame(columnas, index=tabla.index)


def alfa(tabla: pd.DataFrame) -> pd.DataFrame:
    """Shannon y riqueza observada por muestra. scikit-bio quiere muestras en filas."""
    muestras = tabla.T
    return pd.DataFrame(
        {
            "shannon": alpha_diversity("shannon", muestras.values, ids=muestras.index),
            "riqueza": alpha_diversity("observed_features", muestras.values, ids=muestras.index),
        }
    )


def bray_curtis(tabla: pd.DataFrame):
    muestras = tabla.T
    return beta_diversity("braycurtis", muestras.values, ids=list(muestras.index))


def ordenar(distancias):
    """PCoA: coordenadas de los 2 primeros ejes y su % de varianza explicada."""
    resultado = pcoa(distancias)
    coords = resultado.samples.iloc[:, :2].copy()
    coords.columns = ["PC1", "PC2"]
    explicado = resultado.proportion_explained.iloc[:2].to_numpy()
    return coords, explicado


def probar_grupos(distancias, grupos: pd.Series, permutaciones: int = 999):
    """PERMANOVA: ¿la composición difiere entre grupos más de lo esperado al azar?"""
    return permanova(
        distancias,
        grupos.loc[list(distancias.ids)],
        permutations=permutaciones,
        seed=SEMILLA,
    )

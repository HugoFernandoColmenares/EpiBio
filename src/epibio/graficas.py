"""Gráficas en HTML con plotly (se abren en cualquier navegador, sin servidor)."""
from pathlib import Path

import pandas as pd
import plotly.express as px


def barras_apiladas(
    relativa: pd.DataFrame,
    meta: pd.DataFrame,
    top: int = 10,
    destino: Path = Path("docs"),
) -> Path:
    """Barras apiladas con los géneros más abundantes; el resto va a 'Otros'."""
    orden = relativa.mean(axis=1).sort_values(ascending=False)
    principales = [g for g in orden.index if g != "Sin asignar"][:top]
    recorte = relativa.loc[principales].copy()
    recorte.loc["Otros"] = 1 - recorte.sum(axis=0)
    largo = recorte.reset_index(names="genero").melt(
        id_vars="genero", var_name="run", value_name="proporcion"
    )
    largo = largo.merge(
        meta[["run_accession", "sample_alias"]],
        left_on="run",
        right_on="run_accession",
    )
    fig = px.bar(
        largo,
        x="sample_alias",
        y="proporcion",
        color="genero",
        title=f"Top {top} géneros por muestra",
    )
    return _guardar(fig, destino / "barras_generos.html")


def dispersion_pcoa(
    coords: pd.DataFrame,
    explicado,
    meta: pd.DataFrame,
    destino: Path = Path("docs"),
) -> Path:
    datos = coords.join(meta.set_index("run_accession")[["sample_alias", "grupo"]])
    fig = px.scatter(
        datos,
        x="PC1",
        y="PC2",
        color="grupo",
        text="sample_alias",
        labels={
            "PC1": f"PC1 ({explicado[0]:.1%})",
            "PC2": f"PC2 ({explicado[1]:.1%})",
        },
        title="PCoA (Bray-Curtis)",
    )
    fig.update_traces(textposition="top center")
    return _guardar(fig, destino / "pcoa.html")


def _guardar(fig, ruta: Path) -> Path:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(ruta, include_plotlyjs="cdn")
    return ruta

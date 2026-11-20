"""Corre todo el análisis de punta a punta e imprime un resumen en consola."""
import pandas as pd

from epibio import descarga, diversidad, graficas, taxonomia

SULFATORREDUCTORES = (
    "Desulfovibrio",
    "Desulfobulbus",
    "Desulfobacter",
    "Desulfuromonas",
    "Desulfosarcina",
)


def clasificar(alias: str) -> str:
    """MC1a = cara externa; MC1b = cara interna; Sediment_x-y = capa de sedimento."""
    if alias.startswith("Sediment"):
        return "sedimento"
    return "cadena-externa" if alias.endswith("a") else "cadena-interna"


def main() -> None:
    ruta_tabla = descarga.RAW / descarga.TABLA
    if not ruta_tabla.exists():
        descarga.descargar_tabla()
    ruta_meta = descarga.RAW / "metadatos_ena.tsv"
    if not ruta_meta.exists():
        descarga.descargar_metadatos()

    tabla = taxonomia.leer_tabla(ruta_tabla)
    meta = pd.read_csv(ruta_meta, sep="\t")
    meta["grupo"] = meta["sample_alias"].map(clasificar)
    tabla = tabla[meta["run_accession"]]
    print(f"Tabla: {tabla.shape[0]} linajes x {tabla.shape[1]} muestras")
    print("Lecturas asignadas por muestra:")
    print(tabla.sum(axis=0).rename(meta.set_index("run_accession")["sample_alias"]).to_string())

    generos = taxonomia.agrupar_por(tabla, "genero")
    relativa = taxonomia.abundancia_relativa(generos)
    top = (
        relativa.drop(index="Sin asignar", errors="ignore")
        .mean(axis=1)
        .sort_values(ascending=False)
        .head(8)
    )
    print("\nGéneros más abundantes (promedio de abundancia relativa):")
    print(top.round(4).to_string())

    srb = relativa.loc[relativa.index.intersection(SULFATORREDUCTORES)]
    print("\nSulfatorreductores por grupo (promedio):")
    print(
        srb.T.groupby(meta.set_index("run_accession")["grupo"]).mean().T.round(4).to_string()
    )

    rarificada = diversidad.rarefaccion(tabla)
    print(f"\nRarefacción a {int(rarificada.sum(axis=0).iloc[0])} lecturas por muestra")
    alfa = diversidad.alfa(rarificada).join(
        meta.set_index("run_accession")[["sample_alias", "grupo"]]
    )
    print("\nDiversidad alfa:")
    print(alfa.round(2).to_string())
    print("\nPromedio por grupo:")
    print(alfa.groupby("grupo")[["shannon", "riqueza"]].mean().round(2).to_string())

    distancias = diversidad.bray_curtis(rarificada)
    coords, explicado = diversidad.ordenar(distancias)
    print(f"\nPCoA: PC1 explica {explicado[0]:.1%}, PC2 explica {explicado[1]:.1%}")
    grupos = meta.set_index("run_accession")["grupo"]
    print("\nPERMANOVA (999 permutaciones):")
    print(diversidad.probar_grupos(distancias, grupos).to_string())

    print("\nGráficas:")
    print(graficas.barras_apiladas(relativa, meta))
    print(graficas.dispersion_pcoa(coords, explicado, meta))


if __name__ == "__main__":
    main()

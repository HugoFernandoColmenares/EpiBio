import pandas as pd

from epibio.taxonomia import abundancia_relativa, agrupar_por, partir_linaje


def test_linaje_completo():
    linaje = (
        "sk__Bacteria;k__;p__Proteobacteria;c__Deltaproteobacteria;"
        "o__Desulfovibrionales;f__Desulfovibrionaceae;g__Desulfovibrio"
    )
    r = partir_linaje(linaje)
    assert r["superreino"] == "Bacteria"
    assert r["reino"] is None  # MGnify deja k__ vacío en bacterias
    assert r["genero"] == "Desulfovibrio"
    assert r["especie"] is None


def test_linaje_corto_no_inventa_rangos():
    r = partir_linaje("sk__Archaea")
    assert r["superreino"] == "Archaea"
    assert r["filo"] is None


def test_agrupar_y_normalizar():
    tabla = pd.DataFrame(
        {"A": [3, 1, 6], "B": [0, 2, 2]},
        index=[
            "sk__Bacteria;p__X;g__Uno",
            "sk__Bacteria;p__X;g__Uno",
            "sk__Bacteria;p__Y",
        ],
    )
    generos = agrupar_por(tabla, "genero")
    assert generos.loc["Uno", "A"] == 4
    assert generos.loc["Sin asignar", "B"] == 2
    rel = abundancia_relativa(generos)
    assert rel.sum(axis=0).round(6).tolist() == [1.0, 1.0]

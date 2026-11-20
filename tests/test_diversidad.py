import pandas as pd

from epibio.diversidad import alfa, bray_curtis, rarefaccion


def _tabla_sintetica() -> pd.DataFrame:
    """Matriz pequeña (taxones × muestras) con totales controlados."""
    return pd.DataFrame(
        {
            "muestra_a": [10, 5, 0, 5],
            "muestra_b": [8, 8, 2, 2],
            "muestra_c": [20, 0, 0, 0],
        },
        index=["tax1", "tax2", "tax3", "tax4"],
    )


def test_rarefaccion_iguala_profundidad():
    tabla = _tabla_sintetica()
    profundidad = 10
    rarificada = rarefaccion(tabla, profundidad=profundidad)
    assert (rarificada.sum(axis=0) == profundidad).all()
    assert list(rarificada.index) == list(tabla.index)


def test_alfa_valores_positivos():
    tabla = _tabla_sintetica()
    resultado = alfa(tabla)
    assert list(resultado.columns) == ["shannon", "riqueza"]
    # Shannon = 0 si la muestra tiene un solo taxón (muestra_c); el resto > 0.
    assert resultado.loc["muestra_a", "shannon"] > 0
    assert resultado.loc["muestra_b", "shannon"] > 0
    assert resultado.loc["muestra_c", "shannon"] == 0
    assert (resultado["riqueza"] >= 1).all()
    assert resultado.loc["muestra_c", "riqueza"] == 1


def test_bray_curtis_ids():
    tabla = _tabla_sintetica()
    distancias = bray_curtis(tabla)
    assert list(distancias.ids) == list(tabla.columns)

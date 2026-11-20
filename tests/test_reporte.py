from epibio.reporte import clasificar


def test_clasificar_sedimento():
    assert clasificar("Sediment_2-4") == "sedimento"
    assert clasificar("Sediment_7-9") == "sedimento"


def test_clasificar_cadena():
    assert clasificar("MC1a") == "cadena-externa"
    assert clasificar("MC2b") == "cadena-interna"
    assert clasificar("MC3a") == "cadena-externa"

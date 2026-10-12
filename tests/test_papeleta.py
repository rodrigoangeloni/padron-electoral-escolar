"""Tests del layout adaptativo de la papeleta (puro, sin display)."""
import ast
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voting_app import calcular_layout_papeleta


def test_pocos_candidatos_imagen_grande():
    assert calcular_layout_papeleta(1) == (1, 220, 16)
    assert calcular_layout_papeleta(2) == (2, 200, 16)
    assert calcular_layout_papeleta(4) == (4, 170, 14)


def test_ocho_candidatos_foto_grande_dos_filas():
    cols, img, fuente = calcular_layout_papeleta(8)

    assert cols == 4
    assert img == 150
    assert fuente == 13
    assert (8 + cols - 1) // cols == 2  # solo 2 filas


def test_once_candidatos_entran_en_dos_filas():
    cols, img, _ = calcular_layout_papeleta(11)

    assert cols == 6
    assert img == 110
    assert (11 + cols - 1) // cols == 2  # solo 2 filas


def test_muchos_candidatos_achica_y_usa_scroll():
    cols, img, _ = calcular_layout_papeleta(20)

    assert cols == 6
    assert img == 90


def test_layout_siempre_valido():
    for n in range(0, 30):
        cols, img, fuente = calcular_layout_papeleta(n)
        assert cols >= 1
        assert img >= 90
        assert fuente >= 11


def test_grilla_con_padding_compacto():
    """Las tarjetas usan padding compacto (12) para no flotar desconectadas."""
    ruta = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "voting_app.py")
    with open(ruta, encoding="utf-8") as archivo:
        arbol = ast.parse(archivo.read())
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.FunctionDef) and nodo.name == "show_role_selection_screen":
            for hijo in ast.walk(nodo):
                if (isinstance(hijo, ast.Call) and isinstance(hijo.func, ast.Attribute)
                        and hijo.func.attr == "grid"):
                    valores = {kw.arg: kw.value.value for kw in hijo.keywords
                               if isinstance(kw.value, ast.Constant)}
                    if "padx" in valores:
                        assert valores["padx"] == 12
                        assert valores.get("pady") == 12
                        return
    raise AssertionError("No se encontró el .grid() de las tarjetas en show_role_selection_screen")

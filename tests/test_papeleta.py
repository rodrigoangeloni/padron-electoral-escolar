"""Tests del layout adaptativo de la papeleta (puro, sin display)."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voting_app import calcular_layout_papeleta


def test_pocos_candidatos_imagen_grande():
    assert calcular_layout_papeleta(1) == (1, 220, 16)
    assert calcular_layout_papeleta(2) == (2, 200, 16)
    assert calcular_layout_papeleta(4) == (4, 170, 14)


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

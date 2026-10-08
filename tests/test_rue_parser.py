"""Tests del parser RUE (puro, sin pypdf ni GUI)."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from utils.rue_parser import (
    normalizar_grado_rue,
    normalizar_turno_rue,
    dividir_nombre_completo,
    ci_o_nacimiento,
    parse_fila_rue,
    verificar_orden,
)


def test_grados_rue():
    assert normalizar_grado_rue("Jardín de Infantes") == "Jardín"
    assert normalizar_grado_rue("Pre Escolar") == "Pre Escolar"
    assert normalizar_grado_rue("1º Grado") == "1er Grado"
    assert normalizar_grado_rue("6º Grado") == "6to Grado"
    with pytest.raises(ValueError):
        normalizar_grado_rue("7mo Grado")


def test_turnos_rue():
    assert normalizar_turno_rue("Mañana") == "TM"
    assert normalizar_turno_rue("tarde") == "TT"
    with pytest.raises(ValueError):
        normalizar_turno_rue("Noche")


def test_dividir_nombre():
    assert dividir_nombre_completo("BENITEZ CORONEL, MELODY ARAMI") == ("MELODY ARAMI", "BENITEZ CORONEL")
    with pytest.raises(ValueError):
        dividir_nombre_completo("SIN COMA")


def test_ci_con_documento():
    ci, aviso = ci_o_nacimiento("Cédula de Identidad", "8.734.643", "27/02/2020")
    assert (ci, aviso) == ("8734643", None)


def test_ci_fallback_nacimiento():
    ci, aviso = ci_o_nacimiento("Sin Documento", "", "27/02/2020")
    assert ci == "27022020"
    assert aviso is not None


def test_parse_fila_completa():
    linea = "1 BENITEZ CORONEL, MELODY ARAMI Cédula de Identidad 8734643 27/02/2020 Mujer"

    assert parse_fila_rue(linea) == (1, "MELODY ARAMI", "BENITEZ CORONEL", "8734643", None)


def test_parse_fila_certificado_sin_ci():
    linea = ("5 DELGADO CASTILLO, GENESIS MISHELL Certificado de Nacimiento Paraguayo "
             "Oficina: 0593 Libro: 00002 Acta: 00220 Folio: 17/12/2021 Mujer")

    orden, nombres, apellidos, ci, aviso = parse_fila_rue(linea)
    assert (orden, nombres, apellidos, ci) == (5, "GENESIS MISHELL", "DELGADO CASTILLO", "17122021")
    assert aviso is not None  # usa fecha de nacimiento como CI


def test_parse_fila_folio_suelto_no_confunde_ci():
    """El 'Folio: 90' suelto no debe tomarse como documento."""
    linea = ("15 ROMERO MARTINEZ, TAMARA MAGALI Certificado de Nacimiento Paraguayo "
             "Oficina: 15 Libro: 85068 Acta: 333 Folio: 90 16/04/2021 Mujer")

    orden, nombres, apellidos, ci, aviso = parse_fila_rue(linea)
    assert (orden, nombres, apellidos, ci) == (15, "TAMARA MAGALI", "ROMERO MARTINEZ", "16042021")
    assert aviso is not None


def test_parse_fila_pasaporte_usa_nacimiento():
    linea = "20 SALDARRIAGA GONZALEZ, MAXIMILIANO Pasaporte AX672244 13/12/2018 Varón"

    orden, nombres, apellidos, ci, aviso = parse_fila_rue(linea)
    assert (orden, nombres, apellidos, ci) == (20, "MAXIMILIANO", "SALDARRIAGA GONZALEZ", "13122018")
    assert aviso is not None


def test_parse_fila_no_es_fila():
    assert parse_fila_rue("Ministerio de Educación y Ciencias") is None
    assert parse_fila_rue("") is None


def test_verificar_orden():
    assert verificar_orden([(1, 0, 0, 0, 0), (2, 0, 0, 0, 0)]) == []
    assert verificar_orden([(1, 0, 0, 0, 0), (3, 0, 0, 0, 0)]) != []

"""Tests de turno en votantes (Fase 1).

Seams bajo prueba:
- utils.turno_utils.parse_grado_turno(): separa "1er Grado TM"
- migración: DBs viejas sin columna turno se rellenan desde grado_curso
- add_votante()/get_votante(): turno por defecto y explícito
"""
import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from database import DatabaseManager
from utils.turno_utils import parse_grado_turno, parse_fila_votante


@pytest.fixture
def db_manager(tmp_path):
    """DB aislada por test en directorio temporal."""
    db_path = str(tmp_path / "test_turno.db")
    manager = DatabaseManager(db_path=db_path)
    yield manager
    manager.close()


def test_parse_turno_manana():
    assert parse_grado_turno("1er Grado TM") == ("1er Grado", "MAÑANA")


def test_parse_turno_tarde_minusculas_y_espacios():
    assert parse_grado_turno("  6to grado  tt ") == ("6to grado", "TARDE")


def test_parse_acepta_grado_fuera_de_lista():
    """Jardin no está en config.GRADOS_VOTANTES pero es válido igual."""
    assert parse_grado_turno("Jardin TM") == ("Jardin", "MAÑANA")


@pytest.mark.parametrize("texto", ["1er Grado", "TM", "", "   ", "3er Grado XM", "1er Grado TMT"])
def test_parse_invalido_falla(texto):
    with pytest.raises(ValueError):
        parse_grado_turno(texto)


def _crear_db_vieja(db_path):
    """Crea una DB con el schema anterior (sin columna turno)."""
    conn = sqlite3.connect(db_path)
    conn.execute('''CREATE TABLE votantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ci TEXT NOT NULL UNIQUE,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        grado_curso TEXT NOT NULL,
        ya_voto BOOLEAN DEFAULT 0)''')
    conn.execute("INSERT INTO votantes (ci, nombre, apellido, grado_curso, ya_voto)"
                 " VALUES ('1111111','A','B','1er Grado TM',0)")
    conn.execute("INSERT INTO votantes (ci, nombre, apellido, grado_curso, ya_voto)"
                 " VALUES ('2222222','C','D','6to Grado TT',1)")
    conn.execute("INSERT INTO votantes (ci, nombre, apellido, grado_curso, ya_voto)"
                 " VALUES ('3333333','E','F','5to Grado',0)")
    conn.commit()
    conn.close()


def test_migracion_rellena_turno_y_normaliza_grado(tmp_path):
    db_path = str(tmp_path / "vieja.db")
    _crear_db_vieja(db_path)
    manager = DatabaseManager(db_path=db_path)

    manana = manager.get_votante("1111111")
    assert manana[4] == "1er Grado"  # grado normalizado
    assert manana[5] == 0  # ya_voto conserva su índice
    assert manana[6] == "MAÑANA"

    tarde = manager.get_votante("2222222")
    assert tarde[4] == "6to Grado"
    assert tarde[5] == 1
    assert tarde[6] == "TARDE"

    sin_sufijo = manager.get_votante("3333333")
    assert sin_sufijo[4] == "5to Grado"  # intacto
    assert sin_sufijo[6] == "MAÑANA"  # valor por defecto

    manager.close()
    # Reabrir no debe romper ni duplicar nada (migración idempotente).
    manager2 = DatabaseManager(db_path=db_path)
    assert manager2.get_votante("1111111")[6] == "MAÑANA"
    manager2.close()


def test_add_votante_turno_por_defecto(db_manager):
    db_manager.add_votante("1111111", "Juan", "Perez", "5to Grado")

    assert db_manager.get_votante("1111111")[6] == "MAÑANA"


def test_add_votante_turno_explicito(db_manager):
    db_manager.add_votante("2222222", "Ana", "Gomez", "5to Grado", "TARDE")

    assert db_manager.get_votante("2222222")[6] == "TARDE"


def test_add_votante_turno_invalido_falla(db_manager):
    assert db_manager.add_votante("3333333", "Luz", "Diaz", "5to Grado", "NOCHE") is False
    assert db_manager.get_votante("3333333") is None


def test_import_lista_con_turno_y_duplicadas(db_manager):
    lista = [
        ("1111111", "Juan", "Perez", "1er Grado", "MAÑANA"),
        ("2222222", "Ana", "Gomez", "1er Grado", "TARDE"),
        ("1111111", "Otro", "Duplicado", "2do Grado", "MAÑANA"),
        ("3333333", "Luz", "Diaz", "2do Grado", "NOCHE"),
    ]

    ok_count, err_count = db_manager.import_votantes_from_list(lista)

    assert (ok_count, err_count) == (2, 2)
    assert db_manager.get_votante("1111111")[6] == "MAÑANA"
    assert db_manager.get_votante("2222222")[6] == "TARDE"


def test_parse_fila_formato_nuevo_5_columnas():
    fila = ["8734643", "Melody Arami", "Benitez Coronel", "1er Grado", "TM"]

    assert parse_fila_votante(fila, 2) == ("8734643", "Melody Arami", "Benitez Coronel", "1er Grado", "MAÑANA")


def test_parse_fila_turno_minusculas():
    fila = ["1234567", "A", "B", "Jardín", "tt"]

    assert parse_fila_votante(fila, 2)[4] == "TARDE"


def test_parse_fila_formato_anterior_4_columnas():
    fila = ["1234567", "A", "B", "1er Grado TM"]

    assert parse_fila_votante(fila, 2) == ("1234567", "A", "B", "1er Grado", "MAÑANA")


@pytest.mark.parametrize("fila", [
    ["1234567", "A", "B", "1er Grado", "XX"],
    ["1234567", "A", "B", "1er Grado", ""],
    ["1234567", "A", "B", "1er Grado"],
    ["ABC", "A", "B", "1er Grado", "TM"],
    ["123", "A", "B", "1er Grado", "TM"],
    ["1234567", "", "B", "1er Grado", "TM"],
    ["1234567", "A", "B"],
])
def test_parse_fila_invalida_falla_con_linea(fila):
    with pytest.raises(ValueError, match="línea 5"):
        parse_fila_votante(fila, 5)


def _crear_db_vieja_sin_turno_candidatos(db_path):
    conn = sqlite3.connect(db_path)
    conn.execute('''CREATE TABLE candidatos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        cargo TEXT NOT NULL,
        grado TEXT NOT NULL,
        foto TEXT)''')
    conn.execute("INSERT INTO candidatos (nombre, apellido, cargo, grado, foto)"
                 " VALUES ('Ana','Lopez','DIRECTORA','5to Grado','x.jpg')")
    conn.commit()
    conn.close()


def test_migracion_candidatos_turno_por_defecto(tmp_path):
    db_path = str(tmp_path / "vieja_cand.db")
    _crear_db_vieja_sin_turno_candidatos(db_path)
    manager = DatabaseManager(db_path=db_path)

    candidato = manager.get_candidatos()[0]
    assert candidato[5] == "x.jpg"  # foto conserva su índice
    assert candidato[6] == "MAÑANA"
    manager.close()


def test_add_candidato_con_turno(db_manager):
    db_manager.add_candidato("Ana", "Lopez", "DIRECTORA", "5to Grado", turno="TARDE")
    db_manager.add_candidato("Eva", "Diaz", "DIRECTORA", "5to Grado")

    assert db_manager.get_candidatos()[0][6] == "TARDE"
    assert db_manager.get_candidatos()[1][6] == "MAÑANA"  # defecto


def test_add_candidato_turno_invalido_falla(db_manager):
    with pytest.raises(ValueError):
        db_manager.add_candidato("Ana", "Lopez", "DIRECTORA", "5to Grado", turno="NOCHE")


def test_get_candidatos_filtra_por_turno(db_manager):
    db_manager.add_candidato("Ana", "Lopez", "DIRECTORA", "5to Grado", turno="MAÑANA")
    db_manager.add_candidato("Eva", "Diaz", "DIRECTORA", "5to Grado", turno="TARDE")
    db_manager.add_candidato("Luis", "Perez", "VICEDIRECTORA", "6to Grado", turno="TARDE")

    assert len(db_manager.get_candidatos()) == 3
    assert len(db_manager.get_candidatos(turno="MAÑANA")) == 1
    assert len(db_manager.get_candidatos(turno="TARDE")) == 2
    assert len(db_manager.get_candidatos(cargo="DIRECTORA", turno="TARDE")) == 1
    assert db_manager.get_candidatos(cargo="DIRECTORA", turno="TARDE")[0][1] == "Eva"


def test_cargos_sin_candidatos_por_turno(db_manager):
    db_manager.add_candidato("Ana", "Lopez", "DIRECTORA", "5to Grado", turno="MAÑANA")

    assert "DIRECTORA" not in db_manager.cargos_sin_candidatos(turno="MAÑANA")
    assert "DIRECTORA" in db_manager.cargos_sin_candidatos(turno="TARDE")
    # Sin turno mantiene el comportamiento global (compatibilidad).
    assert "DIRECTORA" not in db_manager.cargos_sin_candidatos()
    assert "VICEDIRECTORA" in db_manager.cargos_sin_candidatos()


def test_papeleta_solo_muestra_turno_del_votante(db_manager):
    """Simula start_voting_flow: por cargo, solo candidatos del turno."""
    db_manager.add_candidato("Ana", "Lopez", "DIRECTORA", "5to Grado", turno="MAÑANA")
    db_manager.add_candidato("Eva", "Diaz", "DIRECTORA", "5to Grado", turno="TARDE")
    db_manager.add_votante("1111111", "Juan", "Perez", "5to Grado", "TARDE")

    votante = db_manager.get_votante("1111111")
    turno = votante[6]
    papeleta = {role: db_manager.get_candidatos(role, turno=turno)
                for role in db_manager.get_cargos() if role == "DIRECTORA"}

    assert [c[1] for c in papeleta["DIRECTORA"]] == ["Eva"]

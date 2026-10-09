"""Tests del turno activo (sesión de votación controlada por el admin)."""
import ast
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from database import DatabaseManager


@pytest.fixture
def db_manager(tmp_path):
    """DB aislada por test en directorio temporal."""
    db_path = str(tmp_path / "test_turno_activo.db")
    manager = DatabaseManager(db_path=db_path)
    yield manager
    manager.close()


def test_turno_activo_default_mañana(db_manager):
    assert db_manager.get_turno_activo() == "MAÑANA"


def test_set_get_turno_activo(db_manager):
    db_manager.set_turno_activo("TARDE")
    assert db_manager.get_turno_activo() == "TARDE"

    db_manager.set_turno_activo("MAÑANA")
    assert db_manager.get_turno_activo() == "MAÑANA"


def test_set_turno_activo_rechaza_invalido(db_manager):
    with pytest.raises(ValueError):
        db_manager.set_turno_activo("NOCHE")

    # El valor almacenado no cambia
    assert db_manager.get_turno_activo() == "MAÑANA"


def test_migracion_db_vieja_sin_columna(tmp_path):
    """DBs viejas (sin turno_activo) obtienen la columna con default MAÑANA."""
    db_path = str(tmp_path / "vieja.db")
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE configuracion ("
                 "id INTEGER PRIMARY KEY, "
                 "estado_votacion TEXT DEFAULT 'cerrada', "
                 "fecha_inicio TIMESTAMP, fecha_fin TIMESTAMP)")
    conn.execute("INSERT INTO configuracion (id, estado_votacion) VALUES (1, 'activa')")
    conn.commit()
    conn.close()

    manager = DatabaseManager(db_path=db_path)
    try:
        assert manager.get_turno_activo() == "MAÑANA"
        manager.set_turno_activo("TARDE")
        assert manager.get_turno_activo() == "TARDE"
    finally:
        manager.close()


def _funcion_voting_app(nombre):
    """Devuelve el AST de una función de voting_app.py."""
    ruta = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "voting_app.py")
    with open(ruta, encoding="utf-8") as archivo:
        arbol = ast.parse(archivo.read())
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.FunctionDef) and nodo.name == nombre:
            return nodo
    raise AssertionError(f"No se encontró la función {nombre}() en voting_app.py")


def _usa_llamada(nodo, metodo):
    return any(isinstance(hijo, ast.Call)
               and isinstance(hijo.func, ast.Attribute)
               and hijo.func.attr == metodo
               for hijo in ast.walk(nodo))


def test_papeleta_usa_turno_activo():
    """start_voting_flow filtra por el turno activo (config), no por el votante."""
    funcion = _funcion_voting_app("start_voting_flow")
    assert _usa_llamada(funcion, "get_turno_activo")
    # No debe derivar el turno del votante
    assert not any(isinstance(hijo, ast.Subscript)
                   and isinstance(hijo.value, ast.Attribute)
                   and hijo.value.attr == "current_votante"
                   for hijo in ast.walk(funcion))


def test_validate_ci_bloquea_otro_turno():
    """validate_ci compara el turno del votante con el turno activo."""
    funcion = _funcion_voting_app("validate_ci")
    assert _usa_llamada(funcion, "get_turno_activo")
    fuentes = [hijo.value for hijo in ast.walk(funcion)
               if isinstance(hijo, ast.Constant) and isinstance(hijo.value, str)]
    assert any("pertenece al turno" in texto for texto in fuentes)

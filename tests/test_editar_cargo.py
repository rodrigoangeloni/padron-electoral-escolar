"""Tests de la edición de cargo de candidatos."""
import ast
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from database import DatabaseManager


@pytest.fixture
def db_manager(tmp_path):
    """DB aislada por test en directorio temporal."""
    db_path = str(tmp_path / "test_editar_cargo.db")
    manager = DatabaseManager(db_path=db_path)
    yield manager
    manager.close()


def _crear_candidato(db_manager, cargo="DIRECTORA"):
    db_manager.add_candidato("Ana", "Perez", cargo, "1er Grado")
    return db_manager.get_candidato_by_name("Ana", "Perez")[0]


def test_update_candidate_cargo_cambia_solo_cargo(db_manager):
    cid = _crear_candidato(db_manager)

    db_manager.update_candidate_cargo(cid, "VICEDIRECTORA")

    candidato = db_manager.get_candidato_by_id(cid)
    assert candidato[3] == "VICEDIRECTORA"
    assert candidato[1] == "Ana"
    assert candidato[2] == "Perez"
    assert candidato[4] == "1er Grado"


def test_update_candidate_cargo_rechaza_cargo_inexistente(db_manager):
    cid = _crear_candidato(db_manager)

    with pytest.raises(ValueError):
        db_manager.update_candidate_cargo(cid, "PRESIDENTE")

    assert db_manager.get_candidato_by_id(cid)[3] == "DIRECTORA"


def test_get_votos_candidato_cuenta_votos(db_manager):
    cid = _crear_candidato(db_manager)
    assert db_manager.get_votos_candidato(cid) == 0

    db_manager.add_votante("1234567", "Juan", "Lopez", "1er Grado")
    db_manager.add_multiple_votes([cid], "1234567")

    assert db_manager.get_votos_candidato(cid) == 1


def test_boton_editar_cargo_conectado():
    """La UI tiene el botón Editar Cargo y llama a update_candidate_cargo."""
    ruta = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "utils", "candidate_ui.py")
    with open(ruta, encoding="utf-8") as archivo:
        fuente = archivo.read()
    assert "Editar Cargo" in fuente
    assert "command=self.edit_candidate_cargo" in fuente

    arbol = ast.parse(fuente)
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.FunctionDef) and nodo.name == "edit_candidate_cargo":
            llamadas = [hijo.func.attr for hijo in ast.walk(nodo)
                        if isinstance(hijo, ast.Call) and isinstance(hijo.func, ast.Attribute)]
            assert "update_candidate_cargo" in llamadas
            assert "get_votos_candidato" in llamadas
            return
    raise AssertionError("No se encontró edit_candidate_cargo() en candidate_ui.py")

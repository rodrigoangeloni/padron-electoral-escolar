"""Tests de edición de CI de votantes.

Seams bajo prueba (interfaces públicas de DatabaseManager):
- update_votante_ci(): cambia la CI y reasigna los votos en transacción
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from database import DatabaseManager


@pytest.fixture
def db_manager(tmp_path):
    """DB aislada por test en directorio temporal."""
    db_path = str(tmp_path / "test_editar_ci.db")
    manager = DatabaseManager(db_path=db_path)
    yield manager
    manager.close()


def _votar(db_manager, ci):
    """Registra un votante con un voto emitido para DIRECTORA."""
    db_manager.add_candidato("Ana", "Lopez", "DIRECTORA", "5to Grado")
    candidato_id = db_manager.get_candidatos()[0][0]
    db_manager.add_votante(ci, "Juan", "Perez", "5to Grado")
    ok, _ = db_manager.add_multiple_votes([candidato_id], ci)
    assert ok


def test_actualizar_ci_mueve_votos(db_manager):
    """Cambiar la CI reasigna los votos y conserva ya_voto=1."""
    _votar(db_manager, "1111111")

    ok, _ = db_manager.update_votante_ci("1111111", "2222222")

    assert ok
    assert db_manager.get_votante("1111111") is None
    votante = db_manager.get_votante("2222222")
    assert votante is not None
    assert votante[5] == 1  # ya_voto se conserva
    db_manager.cursor.execute("SELECT ci_votante FROM votos")
    assert [row[0] for row in db_manager.cursor.fetchall()] == ["2222222"]


def test_actualizar_ci_duplicada_falla(db_manager):
    """No se puede asignar una CI que pertenece a otro votante."""
    db_manager.add_votante("1111111", "Juan", "Perez", "5to Grado")
    db_manager.add_votante("2222222", "Ana", "Gomez", "5to Grado")

    ok, _ = db_manager.update_votante_ci("1111111", "2222222")

    assert not ok
    assert db_manager.get_votante("1111111") is not None
    assert db_manager.get_votante("2222222")[2] == "Ana"


def test_actualizar_ci_formato_invalido(db_manager):
    """La CI nueva debe tener 7-8 dígitos numéricos."""
    db_manager.add_votante("1111111", "Juan", "Perez", "5to Grado")

    for ci_mala in ["abc", "123456", "123456789", ""]:
        ok, _ = db_manager.update_votante_ci("1111111", ci_mala)
        assert not ok

    assert db_manager.get_votante("1111111") is not None


def test_actualizar_ci_votante_inexistente(db_manager):
    """Cambiar la CI de un votante que no existe debe fallar."""
    ok, _ = db_manager.update_votante_ci("9999999", "8888888")

    assert not ok
    assert db_manager.get_votante("8888888") is None

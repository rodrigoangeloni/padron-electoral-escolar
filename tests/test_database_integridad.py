"""Tests de integridad de la base de datos (Fase 1).

Seams bajo prueba (interfaces públicas de DatabaseManager):
- DatabaseManager(db_path): conexión con FK activadas
- add_multiple_votes(candidato_ids, ci): rechaza lista vacía
- init_db(): DEFAULT de estado_votacion es 'cerrada'
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from database import DatabaseManager
import config


@pytest.fixture
def db_manager(tmp_path):
    """DB aislada por test en directorio temporal."""
    db_path = str(tmp_path / "test_election.db")
    manager = DatabaseManager(db_path=db_path)
    yield manager
    manager.close()


def test_foreign_keys_activadas(db_manager):
    """La conexión debe enforcing FK (evita votos huérfanos)."""
    db_manager.cursor.execute("PRAGMA foreign_keys")
    assert db_manager.cursor.fetchone()[0] == 1


def test_borrar_candidato_elimina_sus_votos(db_manager):
    """Sin votos huérfanos tras eliminar candidato."""
    db_manager.add_candidato("Borrar", "Me", "DIRECTORA", "5to Grado")
    candidato_id = db_manager.get_candidatos()[0][0]
    db_manager.add_votante("8888888", "Huerf", "Ano", "1er Grado")
    ok, _ = db_manager.add_multiple_votes([candidato_id], "8888888")
    assert ok is True

    db_manager.delete_candidato(candidato_id)

    db_manager.cursor.execute("SELECT COUNT(*) FROM votos")
    assert db_manager.cursor.fetchone()[0] == 0


def test_rechaza_voto_vacio(db_manager):
    """Votar sin candidatos no debe marcar ya_voto=1."""
    db_manager.add_votante("7777777", "Test", "Vacio", "5to Grado")

    ok, _ = db_manager.add_multiple_votes([], "7777777")

    assert ok is False
    votante = db_manager.get_votante("7777777")
    assert votante[5] == 0


def test_default_estado_votacion_es_cerrada(db_manager):
    """El DDL debe defaultear a 'cerrada', no al literal '{VOTACION_CERRADA}'."""
    db_manager.cursor.execute(
        "SELECT sql FROM sqlite_master WHERE name='configuracion'"
    )
    ddl = db_manager.cursor.fetchone()[0]
    assert "{VOTACION_CERRADA}" not in ddl
    assert config.VOTACION_CERRADA in ddl

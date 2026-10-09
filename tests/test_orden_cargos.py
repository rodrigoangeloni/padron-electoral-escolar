"""Tests del orden configurable de cargos."""
import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from database import DatabaseManager


@pytest.fixture
def db_manager(tmp_path):
    """DB aislada por test en directorio temporal."""
    db_path = str(tmp_path / "test_orden.db")
    manager = DatabaseManager(db_path=db_path)
    yield manager
    manager.close()


def test_seed_respeta_orden_definido(db_manager):
    assert db_manager.get_cargos() == ["DIRECTORA", "VICEDIRECTORA", "COORDINADORA"]


def test_add_cargo_va_al_final(db_manager):
    db_manager.add_cargo("TESORERA")

    assert db_manager.get_cargos()[-1] == "TESORERA"


def test_mover_cargo_sube_y_baja(db_manager):
    ok, _ = db_manager.mover_cargo("VICEDIRECTORA", -1)
    assert ok
    assert db_manager.get_cargos() == ["VICEDIRECTORA", "DIRECTORA", "COORDINADORA"]

    ok, _ = db_manager.mover_cargo("VICEDIRECTORA", +1)
    assert ok
    assert db_manager.get_cargos() == ["DIRECTORA", "VICEDIRECTORA", "COORDINADORA"]


def test_mover_cargo_en_extremos_no_hace_nada(db_manager):
    ok, _ = db_manager.mover_cargo("DIRECTORA", -1)
    assert not ok
    ok, _ = db_manager.mover_cargo("COORDINADORA", +1)
    assert not ok
    assert db_manager.get_cargos() == ["DIRECTORA", "VICEDIRECTORA", "COORDINADORA"]


def test_mover_cargo_inexistente_falla(db_manager):
    ok, _ = db_manager.mover_cargo("INEXISTENTE", -1)
    assert not ok


def test_migracion_conserva_orden_alfabetico(tmp_path):
    """DBs viejas sin columna orden quedan como se veían (alfabético)."""
    db_path = str(tmp_path / "vieja_cargos.db")
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE cargos (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL UNIQUE)")
    conn.execute("INSERT INTO cargos (nombre) VALUES ('VICEDIRECTORA'), ('COORDINADORA'), ('DIRECTORA')")
    conn.commit()
    conn.close()

    manager = DatabaseManager(db_path=db_path)
    assert manager.get_cargos() == ["COORDINADORA", "DIRECTORA", "VICEDIRECTORA"]
    manager.close()

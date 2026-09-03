"""Tests de reglas de voto (Fase 2).

Seams bajo prueba (interfaces públicas de DatabaseManager):
- cargos_sin_candidatos(): cargos configurados sin candidatos
- get_resultados(): incluye id para distinguir homónimos
- get_ganadores(): lista por cargo, con empates incluidos
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from database import DatabaseManager


@pytest.fixture
def db_manager(tmp_path):
    """DB aislada por test en directorio temporal."""
    db_path = str(tmp_path / "test_reglas.db")
    manager = DatabaseManager(db_path=db_path)
    yield manager
    manager.close()


def test_detecta_cargo_sin_candidatos(db_manager):
    """Un cargo configurado sin candidatos debe reportarse (bloquea votación)."""
    db_manager.add_cargo("CARGO_VACIO")
    db_manager.add_candidato("Ana", "Lopez", "DIRECTORA", "5to Grado")

    vacios = db_manager.cargos_sin_candidatos()

    assert "CARGO_VACIO" in vacios
    assert "DIRECTORA" not in vacios


def test_homonimos_se_distinguen_por_id(db_manager):
    """Dos candidatos con mismo nombre deben distinguirse por id en resultados."""
    db_manager.add_candidato("Ana", "Lopez", "DIRECTORA", "5to Grado")
    db_manager.add_candidato("Ana", "Lopez", "DIRECTORA", "6to Grado")

    resultados, _ = db_manager.get_resultados()

    filas = [r for r in resultados if r[1] == "Ana" and r[2] == "Lopez"]
    assert len(filas) == 2
    assert filas[0][0] != filas[1][0]  # id distinto


def test_empate_devuelve_ambos_ganadores(db_manager):
    """Con igual cantidad de votos, ambos candidatos son ganadores del cargo."""
    db_manager.add_candidato("Ana", "Lopez", "DIRECTORA", "5to Grado")
    db_manager.add_candidato("Eva", "Diaz", "DIRECTORA", "5to Grado")
    candidatos = db_manager.get_candidatos()
    ids = { (c[1], c[2]): c[0] for c in candidatos }
    db_manager.add_votante("1111111", "Vot", "Uno", "5to Grado")
    db_manager.add_votante("2222222", "Vot", "Dos", "5to Grado")
    db_manager.add_multiple_votes([ids[("Ana", "Lopez")]], "1111111")
    # Segundo votante vota por la otra candidata (empate 1-1)
    db_manager.cursor.execute(
        "INSERT INTO votos (candidato_id, ci_votante) VALUES (?, ?)",
        (ids[("Eva", "Diaz")], "2222222"),
    )
    db_manager.cursor.execute(
        "UPDATE votantes SET ya_voto = 1 WHERE ci = ?", ("2222222",)
    )
    db_manager.conn.commit()

    ganadores = db_manager.get_ganadores()

    assert len(ganadores["DIRECTORA"]) == 2

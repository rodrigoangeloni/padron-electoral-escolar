"""Tests de resultados y rendimiento (Fase 5).

Seams bajo prueba:
- DatabaseManager.get_ganadores(): sin N+1 (foto en la query única)
- crear_figura_resultados(): un subplot por cargo, función pura
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from database import DatabaseManager


def _metodos_clase_results_ui():
    """Métodos directos de la clase ResultsUI (parseo AST, sin GUI)."""
    import ast

    ruta = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "utils",
        "results_ui.py",
    )
    with open(ruta, encoding="utf-8") as f:
        arbol = ast.parse(f.read())
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.ClassDef) and nodo.name == "ResultsUI":
            return {
                n.name for n in nodo.body if isinstance(n, ast.FunctionDef)
            }
    raise AssertionError("Clase ResultsUI no encontrada")


def test_results_ui_expone_exportar_pdf():
    """Regresión: setup_results_tab usa self._export_results_to_pdf (crash exe)."""
    assert "_export_results_to_pdf" in _metodos_clase_results_ui()


@pytest.fixture
def db_manager(tmp_path):
    """DB aislada por test en directorio temporal."""
    db_path = str(tmp_path / "test_perf.db")
    manager = DatabaseManager(db_path=db_path)
    yield manager
    manager.close()


def test_ganadores_sin_n_mas_1(db_manager):
    """get_ganadores debe resolver fotos sin una query por candidato."""
    db_manager.add_candidato("Ana", "Lopez", "DIRECTORA", "5to Grado")
    db_manager.add_candidato("Eva", "Diaz", "DIRECTORA", "5to Grado")
    db_manager.add_candidato("Luis", "Perez", "VICEDIRECTORA", "6to Grado")

    llamadas = []
    db_manager.conn.set_trace_callback(llamadas.append)
    try:
        ganadores = db_manager.get_ganadores()
    finally:
        db_manager.conn.set_trace_callback(None)

    selects = [q for q in llamadas if q.lstrip().upper().startswith("SELECT")]
    # get_resultados hace 2 SELECTs (detalle + por grado); nada más.
    assert len(selects) == 2
    assert len(ganadores["DIRECTORA"]) == 2
    assert all("foto" in c for c in ganadores["DIRECTORA"])


def test_figura_un_subplot_por_cargo():
    """La figura tiene un subplot horizontal por cargo."""
    plt = pytest.importorskip("matplotlib.pyplot")
    from utils.results_ui import crear_figura_resultados

    resultados = [
        (1, "Ana", "Lopez", "DIRECTORA", "5to Grado", 3, "foto1"),
        (2, "Eva", "Diaz", "DIRECTORA", "5to Grado", 1, "foto2"),
        (3, "Luis", "Perez", "VICEDIRECTORA", "6to Grado", 2, "foto3"),
    ]

    fig = crear_figura_resultados(resultados, ["DIRECTORA", "VICEDIRECTORA"])
    try:
        assert len(fig.axes) == 2
        assert fig.axes[0].get_title() == "DIRECTORA"
        assert fig.axes[1].get_title() == "VICEDIRECTORA"
    finally:
        plt.close(fig)


def test_reemplazo_no_acumula_figuras():
    """Cerrar la figura anterior evita el leak al refrescar."""
    plt = pytest.importorskip("matplotlib.pyplot")
    from utils.results_ui import crear_figura_resultados

    resultados = [
        (1, "Ana", "Lopez", "DIRECTORA", "5to Grado", 3, "foto1"),
    ]
    antes = set(plt.get_fignums())

    fig1 = crear_figura_resultados(resultados, ["DIRECTORA"])
    plt.close(fig1)  # lo que debe hacer _update_graphs con la anterior
    fig2 = crear_figura_resultados(resultados, ["DIRECTORA"])
    try:
        assert set(plt.get_fignums()) - antes == {fig2.number}
    finally:
        plt.close(fig2)
    assert set(plt.get_fignums()) == antes

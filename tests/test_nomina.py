"""Tests de la nómina de votantes (votaron / no votaron).

Seams bajo prueba:
- DatabaseManager.get_nomina(): split por ya_voto, con y sin turno.
- utils.pdf_exporter.export_nomina(): secciones Votaron/No votaron
  (fpdf funciona sin display, estos tests corren headless).
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import DatabaseManager
from utils.pdf_exporter import export_nomina


def _padron(db_manager):
    """3 votantes: 1 votó (MAÑANA), 2 no (uno por turno)."""
    db_manager.add_candidato("Ana", "Lopez", "DIRECTORA", "5to Grado", turno="MAÑANA")
    manana_id = db_manager.get_candidatos(turno="MAÑANA")[0][0]
    db_manager.add_votante("1111111", "Vot", "Uno", "5to Grado", "MAÑANA")
    db_manager.add_votante("2222222", "Vot", "Dos", "5to Grado", "MAÑANA")
    db_manager.add_votante("3333333", "Vot", "Tres", "5to Grado", "TARDE")
    db_manager.add_multiple_votes([manana_id], "1111111")


def _secciones(db_manager, turnos):
    secciones = []
    for turno in turnos:
        votaron, no_votaron = db_manager.get_nomina(turno)
        secciones.append({"turno": turno, "votaron": votaron,
                          "no_votaron": no_votaron})
    return secciones


def _nuevo_manager(tmp_path, nombre):
    manager = DatabaseManager(db_path=str(tmp_path / nombre))
    _padron(manager)
    return manager


def test_nomina_split_por_turno(tmp_path):
    db = _nuevo_manager(tmp_path, "nom1.db")
    try:
        votaron, no_votaron = db.get_nomina("MAÑANA")
        assert [v[0] for v in votaron] == ["1111111"]
        assert [v[0] for v in no_votaron] == ["2222222"]
    finally:
        db.close()


def test_nomina_todos_los_turnos(tmp_path):
    db = _nuevo_manager(tmp_path, "nom2.db")
    try:
        votaron, no_votaron = db.get_nomina(None)
        assert [v[0] for v in votaron] == ["1111111"]
        assert sorted(v[0] for v in no_votaron) == ["2222222", "3333333"]
        # filas (ci, nombre, apellido, grado, turno)
        assert no_votaron[0][1:] == ("Vot", "Dos", "5to Grado", "MAÑANA")
    finally:
        db.close()


def test_nomina_una_sola_query(tmp_path):
    """Sin N+1: get_nomina resuelve todo en un SELECT."""
    db = _nuevo_manager(tmp_path, "nom3.db")
    try:
        llamadas = []
        db.conn.set_trace_callback(llamadas.append)
        try:
            db.get_nomina(None)
        finally:
            db.conn.set_trace_callback(None)
        selects = [q for q in llamadas if q.lstrip().upper().startswith("SELECT")]
        assert len(selects) == 1
    finally:
        db.close()


def test_export_nomina_secciones_y_nombres(tmp_path):
    from pypdf import PdfReader

    db = _nuevo_manager(tmp_path, "nom4.db")
    try:
        ruta = str(tmp_path / "nomina.pdf")
        export_nomina(_secciones(db, ["MAÑANA", "TARDE"]), ruta)

        assert os.path.getsize(ruta) > 0
        texto = "\n".join((p.extract_text() or "") for p in PdfReader(ruta).pages)
        assert "Mina de Votantes" in texto or "Nómina de Votantes" in texto
        assert "No votaron (1)" in texto
        assert "2222222" in texto  # ausente de MAÑANA
        assert "1111111" in texto  # presente
    finally:
        db.close()


def test_export_nomina_padron_vacio_no_falla(tmp_path):
    db = DatabaseManager(db_path=str(tmp_path / "nom5.db"))
    try:
        ruta = str(tmp_path / "nomina_vacia.pdf")
        export_nomina(_secciones(db, ["MAÑANA"]), ruta)

        assert os.path.getsize(ruta) > 0
    finally:
        db.close()

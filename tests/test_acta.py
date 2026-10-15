"""Tests del acta PDF (Fase 4).

Seams bajo prueba:
- utils.pdf_exporter.export_acta(): genera el PDF por secciones de turno
  (fpdf funciona sin display, estos tests corren headless).
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from database import DatabaseManager
from utils.pdf_exporter import export_acta, _totales_por_cargo


@pytest.fixture
def db_manager(tmp_path):
    """DB aislada por test en directorio temporal."""
    db_path = str(tmp_path / "test_acta.db")
    manager = DatabaseManager(db_path=db_path)
    yield manager
    manager.close()


def _seccion(db_manager, turno):
    resultados, _ = db_manager.get_resultados(turno)
    winners = {}
    for cargo, top in db_manager.get_ganadores(turno).items():
        if len(top) == 1:
            winners[cargo] = {'nombre': top[0]['nombre'],
                              'apellido': top[0]['apellido'],
                              'votos': top[0]['votos'],
                              'foto': top[0]['foto']}
        else:
            empatados = ", ".join(f"{c['nombre']} {c['apellido']}" for c in top)
            winners[cargo] = {'nombre': f"Empate: {empatados}",
                              'apellido': "",
                              'votos': top[0]['votos'],
                              'foto': None}
    return {"turno": turno,
            "participacion": db_manager.get_participacion(turno),
            "winners": winners,
            "resultados": resultados}


def _eleccion(db_manager):
    db_manager.add_candidato("Ana", "Lopez", "DIRECTORA", "5to Grado", turno="MAÑANA")
    db_manager.add_candidato("Eva", "Diaz", "DIRECTORA", "5to Grado", turno="TARDE")
    manana_id = db_manager.get_candidatos(turno="MAÑANA")[0][0]
    db_manager.add_votante("1111111", "Vot", "Uno", "5to Grado", "MAÑANA")
    db_manager.add_votante("2222222", "Vot", "Dos", "5to Grado", "TARDE")
    db_manager.add_multiple_votes([manana_id], "1111111")


def test_totales_por_cargo():
    filas = [(1, "Ana", "Lopez", "DIRECTORA", "5to Grado", 2, "f", "MAÑANA"),
             (2, "Eva", "Diaz", "DIRECTORA", "5to Grado", 1, "f", "MAÑANA")]

    assert _totales_por_cargo(filas) == {"DIRECTORA": 3}


def test_export_acta_un_turno(db_manager, tmp_path):
    _eleccion(db_manager)
    ruta = str(tmp_path / "acta_manana.pdf")

    export_acta([_seccion(db_manager, "MAÑANA")], ruta)

    assert os.path.getsize(ruta) > 0


def test_export_acta_ambos_turnos(db_manager, tmp_path):
    _eleccion(db_manager)
    ruta_uno = str(tmp_path / "acta_uno.pdf")
    ruta_ambos = str(tmp_path / "acta_ambos.pdf")

    export_acta([_seccion(db_manager, "MAÑANA")], ruta_uno)
    export_acta([_seccion(db_manager, "MAÑANA"),
                 _seccion(db_manager, "TARDE")], ruta_ambos)

    assert os.path.getsize(ruta_ambos) > os.path.getsize(ruta_uno)


def test_export_acta_sin_datos_no_falla(db_manager, tmp_path):
    ruta = str(tmp_path / "acta_vacia.pdf")

    export_acta([_seccion(db_manager, "TARDE")], ruta)

    assert os.path.getsize(ruta) > 0


def test_export_acta_muchos_datos_no_falla(db_manager, tmp_path):
    """Nombres largos y varios cargos: pagina sin errores."""
    for n in range(6):
        db_manager.add_cargo(f"CARGO_{n}")
        for m in range(3):
            db_manager.add_candidato(f"Nombre Largo {n}{m}", f"Apellido Extenso {n}{m}",
                                     f"CARGO_{n}", "5to Grado", turno="MAÑANA")
    ruta = str(tmp_path / "acta_grande.pdf")

    export_acta([_seccion(db_manager, "MAÑANA"),
                 _seccion(db_manager, "TARDE")], ruta)

    assert os.path.getsize(ruta) > 0


def test_acta_firma_unica_y_pie_con_desarrollador(db_manager, tmp_path):
    """El acta trae solo la firma del presidente/encargado y el pie con autor y versión."""
    from pypdf import PdfReader
    import config

    _eleccion(db_manager)
    ruta = str(tmp_path / "acta_firma.pdf")

    export_acta([_seccion(db_manager, "MAÑANA")], ruta)

    texto = "\n".join((pagina.extract_text() or "") for pagina in PdfReader(ruta).pages)
    assert "Presidente de Mesa o Encargado" in texto
    assert "Fiscal" not in texto
    assert config.DESARROLLADOR in texto
    assert f"v{config.APP_VERSION}" in texto


def test_acta_encabezado_y_pie_con_nombre_del_sistema(db_manager, tmp_path):
    """Encabezado con SISTEMA DE VOTACIÓN ESCOLAR + versión; pie completo."""
    from pypdf import PdfReader
    import config

    _eleccion(db_manager)
    ruta = str(tmp_path / "acta_membrete.pdf")

    export_acta([_seccion(db_manager, "MAÑANA")], ruta)

    texto = "\n".join((pagina.extract_text() or "") for pagina in PdfReader(ruta).pages)
    assert "SISTEMA DE VOTACIÓN ESCOLAR" in texto
    assert (f"SISTEMA DE VOTACIÓN ESCOLAR - Desarrollado por {config.DESARROLLADOR} "
            f"- v{config.APP_VERSION}") in texto


def _tiene_imagenes(ruta):
    """Detecta objetos /Image dentro del PDF (fpdf incrusta la foto del ganador)."""
    from pypdf import PdfReader

    for pagina in PdfReader(ruta).pages:
        xobjects = (pagina.get("/Resources") or {}).get("/XObject", {}) or {}
        for obj in xobjects.values():
            if obj.get_object().get("/Subtype") == "/Image":
                return True
    return False


def test_acta_incluye_foto_del_ganador(db_manager, tmp_path):
    """El ganador con foto disponible la lleva incrustada en el acta."""
    import config

    db_manager.add_candidato("Ana", "Lopez", "DIRECTORA", "5to Grado",
                             foto=config.DEFAULT_CANDIDATE_IMAGE, turno="MAÑANA")
    manana_id = db_manager.get_candidatos(turno="MAÑANA")[0][0]
    db_manager.add_votante("1111111", "Vot", "Uno", "5to Grado", "MAÑANA")
    db_manager.add_multiple_votes([manana_id], "1111111")
    ruta = str(tmp_path / "acta_foto.pdf")

    export_acta([_seccion(db_manager, "MAÑANA")], ruta)

    assert os.path.getsize(ruta) > 0
    assert _tiene_imagenes(ruta)


def test_acta_foto_inexistente_no_falla(db_manager, tmp_path):
    """Foto del ganador borrada o ruta inválida: el acta sale igual (con la de defecto)."""
    _eleccion(db_manager)
    seccion = _seccion(db_manager, "MAÑANA")
    for datos in seccion["winners"].values():
        datos["foto"] = "/ruta/que/no/existe.jpg"
    ruta = str(tmp_path / "acta_sin_foto.pdf")

    export_acta([seccion], ruta)

    assert os.path.getsize(ruta) > 0


def test_acta_empate_sin_foto_no_falla(db_manager, tmp_path):
    """Empate (foto=None): el acta sale sin foto pero con el texto del empate."""
    from pypdf import PdfReader

    db_manager.add_candidato("Ana", "Lopez", "DIRECTORA", "5to Grado", turno="MAÑANA")
    db_manager.add_candidato("Eva", "Diaz", "DIRECTORA", "5to Grado", turno="MAÑANA")
    ids = [c[0] for c in db_manager.get_candidatos(turno="MAÑANA")]
    db_manager.add_votante("1111111", "Vot", "Uno", "5to Grado", "MAÑANA")
    db_manager.add_votante("2222222", "Vot", "Dos", "5to Grado", "MAÑANA")
    db_manager.add_multiple_votes([ids[0]], "1111111")
    db_manager.add_multiple_votes([ids[1]], "2222222")
    ruta = str(tmp_path / "acta_empate.pdf")

    export_acta([_seccion(db_manager, "MAÑANA")], ruta)

    texto = "\n".join((pagina.extract_text() or "") for pagina in PdfReader(ruta).pages)
    assert os.path.getsize(ruta) > 0
    assert "Empate:" in texto

"""Tests de fotos portables (mover la app no debe perder las fotos).

Seams bajo prueba:
- utils.foto_utils.resolver_ruta_foto(): ruta tal cual si existe,
  basename contra la carpeta actual, defecto, None.
- DatabaseManager._migrar_fotos_relativas(): absolutas -> solo-nombre.
- DatabaseManager.update_candidate_photo(): guarda solo el nombre.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image

from database import DatabaseManager
from utils.foto_utils import resolver_ruta_foto


def _crear_jpg(ruta):
    Image.new("RGB", (20, 20), color="blue").save(ruta, "JPEG")


def test_resolver_respeta_ruta_existente(tmp_path):
    foto = tmp_path / "candidate_1.jpg"
    _crear_jpg(str(foto))

    assert resolver_ruta_foto(str(foto), directorio=str(tmp_path)) == str(foto)


def test_resolver_reconstruye_absoluta_vieja(tmp_path):
    """Ruta absoluta de otra PC: usa el basename dentro del directorio actual."""
    foto = tmp_path / "candidate_2.jpg"
    _crear_jpg(str(foto))
    vieja = r"C:\carpeta_inexistente_xyz\images\candidate_2.jpg"

    assert resolver_ruta_foto(vieja, directorio=str(tmp_path)) == str(foto)


def test_resolver_solo_nombre(tmp_path):
    foto = tmp_path / "candidate_3.jpg"
    _crear_jpg(str(foto))

    assert resolver_ruta_foto("candidate_3.jpg", directorio=str(tmp_path)) == str(foto)


def test_resolver_sin_foto_devuelve_defecto_o_none(tmp_path):
    import config

    resultado = resolver_ruta_foto(None, directorio=str(tmp_path))
    assert resultado in (config.DEFAULT_CANDIDATE_IMAGE, None)
    assert resolver_ruta_foto("/ruta/que/no/existe.jpg",
                              directorio=str(tmp_path)) == resultado


def test_migracion_convierte_absolutas_a_nombres(tmp_path):
    db_path = str(tmp_path / "fotos.db")
    db = DatabaseManager(db_path=db_path)
    db.add_candidato("Ana", "Lopez", "DIRECTORA", "5to Grado",
                     foto=r"C:\otra\carpeta\images\candidate_9.jpg", turno="MAÑANA")
    db.cursor.execute("SELECT foto FROM candidatos WHERE nombre='Ana'")
    assert db.cursor.fetchone()[0] == r"C:\otra\carpeta\images\candidate_9.jpg"
    db.close()

    db2 = DatabaseManager(db_path=db_path)  # init_db corre la migración
    db2.cursor.execute("SELECT foto FROM candidatos WHERE nombre='Ana'")
    assert db2.cursor.fetchone()[0] == "candidate_9.jpg"
    # segunda apertura: idempotente, no cambia nada
    db2.close()
    db3 = DatabaseManager(db_path=db_path)
    db3.cursor.execute("SELECT foto FROM candidatos WHERE nombre='Ana'")
    assert db3.cursor.fetchone()[0] == "candidate_9.jpg"
    db3.close()


def test_migracion_no_toca_imagen_por_defecto(tmp_path):
    import config

    db_path = str(tmp_path / "fotos2.db")
    db = DatabaseManager(db_path=db_path)
    db.add_candidato("Eva", "Diaz", "DIRECTORA", "5to Grado", turno="MAÑANA")
    db.close()

    db2 = DatabaseManager(db_path=db_path)
    db2.cursor.execute("SELECT foto FROM candidatos WHERE nombre='Eva'")
    assert db2.cursor.fetchone()[0] == config.DEFAULT_CANDIDATE_IMAGE
    db2.close()


def test_update_candidate_photo_guarda_solo_nombre(tmp_path):
    db_path = str(tmp_path / "fotos3.db")
    db = DatabaseManager(db_path=db_path)
    db.add_candidato("Luz", "Paz", "DIRECTORA", "5to Grado", turno="MAÑANA")
    cid = db.get_candidatos(turno="MAÑANA")[0][0]

    db.update_candidate_photo(cid, r"C:\otra\carpeta\images\candidate_1.png")

    assert db.get_candidato_by_id(cid)[5] == "candidate_1.png"
    db.close()

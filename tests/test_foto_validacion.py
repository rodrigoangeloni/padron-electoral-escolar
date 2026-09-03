"""Tests de validación de fotos de candidatos (Fase 4).

Seam bajo prueba (función pura, sin GUI):
- validar_foto_candidato(ruta): (ok, mensaje) según extensión,
  tamaño y contenido real de imagen.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from PIL import Image
from utils.foto_utils import validar_foto_candidato, TAMANO_MAX_FOTO_BYTES


def _crear_jpg(ruta, tamaño=(100, 100)):
    img = Image.new("RGB", tamaño, color="red")
    img.save(ruta, "JPEG")


def test_acepta_jpg_valido(tmp_path):
    """Una foto JPG real y pequeña debe aceptarse."""
    foto = tmp_path / "candidato.jpg"
    _crear_jpg(str(foto))

    ok, _ = validar_foto_candidato(str(foto))

    assert ok is True


def test_acepta_extension_en_mayusculas(tmp_path):
    """La extensión se normaliza: .JPG vale igual que .jpg."""
    foto = tmp_path / "candidato.JPG"
    _crear_jpg(str(foto))

    ok, _ = validar_foto_candidato(str(foto))

    assert ok is True


def test_rechaza_exe(tmp_path):
    """Un ejecutable renombrado no debe pasar como foto."""
    exe = tmp_path / "malware.jpg"
    # Contenido EXE real con extensión de imagen: debe fallar por contenido.
    exe.write_bytes(b"MZ" + b"\x00" * 1024)

    ok, mensaje = validar_foto_candidato(str(exe))

    assert ok is False
    assert mensaje != ""


def test_rechaza_extension_no_permitida(tmp_path):
    """Extensiones fuera de {.jpg, .jpeg, .png} se rechazan."""
    exe = tmp_path / "programa.exe"
    exe.write_bytes(b"MZ" + b"\x00" * 100)

    ok, _ = validar_foto_candidato(str(exe))

    assert ok is False


def test_rechaza_archivo_gigante(tmp_path):
    """Archivos sobre el límite se rechazan aunque sean imagen válida."""
    grande = tmp_path / "gigante.jpg"
    _crear_jpg(str(grande))
    with open(str(grande), "ab") as f:
        f.write(b"\x00" * (TAMANO_MAX_FOTO_BYTES + 1))

    ok, _ = validar_foto_candidato(str(grande))

    assert ok is False


def test_rechaza_imagen_corrupta(tmp_path):
    """Bytes aleatorios con extensión .png no son una imagen válida."""
    corrupta = tmp_path / "corrupta.png"
    corrupta.write_bytes(os.urandom(2048))

    ok, _ = validar_foto_candidato(str(corrupta))

    assert ok is False


def test_rechaza_inexistente(tmp_path):
    """Ruta inexistente se rechaza con mensaje explícito."""
    ok, mensaje = validar_foto_candidato(str(tmp_path / "no_existe.jpg"))

    assert ok is False
    assert mensaje != ""

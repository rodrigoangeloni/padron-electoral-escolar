"""
Validación de fotos de candidatos.

Separa la validación (función pura, testeable sin GUI) de la
interfaz de subida en `candidate_ui.py`.
"""
import os

from PIL import Image, UnidentifiedImageError

# Extensiones permitidas (siempre en minúsculas) y tamaño máximo.
EXTENSIONES_PERMITIDAS = frozenset({".jpg", ".jpeg", ".png"})
TAMANO_MAX_FOTO_BYTES = 5 * 1024 * 1024


def validar_foto_candidato(ruta, tamano_max_bytes=TAMANO_MAX_FOTO_BYTES):
    """Valida un archivo como foto de candidato.

    Args:
        ruta: Ruta al archivo a validar.
        tamano_max_bytes: Tamaño máximo permitido en bytes.

    Returns:
        tuple: (ok, mensaje) con el motivo del rechazo si falla.
    """
    if not ruta or not os.path.isfile(ruta):
        return False, "El archivo no existe."

    extension = os.path.splitext(ruta)[1].lower()
    if extension not in EXTENSIONES_PERMITIDAS:
        return False, "Formato no permitido. Use JPG o PNG."

    try:
        if os.path.getsize(ruta) > tamano_max_bytes:
            return False, "La imagen supera el tamaño máximo de 5 MB."
    except OSError:
        return False, "No se pudo leer el archivo."

    try:
        with Image.open(ruta) as img:
            img.verify()
        # verify() deja el objeto inutilizable: reabrir y decodificar
        # para confirmar que el contenido es una imagen real.
        with Image.open(ruta) as img:
            img.load()
    except (UnidentifiedImageError, OSError, ValueError):
        return False, "El archivo no es una imagen válida."

    return True, "Foto válida."

"""
Parseo de grado y turno desde el texto del padrón.

Los CSV traen el turno como sufijo del grado (ej. "1er Grado TM").
Funciones puras, testeables sin GUI ni base de datos.
"""
import re

TURNO_MANANA = "MAÑANA"
TURNO_TARDE = "TARDE"
TURNOS_VALIDOS = (TURNO_MANANA, TURNO_TARDE)

_SUFIJO_A_TURNO = {"TM": TURNO_MANANA, "TT": TURNO_TARDE}


def parse_grado_turno(texto):
    """Separa "1er Grado TM" en ("1er Grado", "MAÑANA").

    Acepta minúsculas y espacios extra ("  6to grado  tt ").
    El grado base no se valida contra lista: cualquier texto con
    sufijo válido pasa (la lista de config solo alimenta los combos).

    Raises:
        ValueError: si no termina en sufijo TM/TT o falta el grado.
    """
    if not texto or not texto.strip():
        raise ValueError("Grado vacío.")
    coincidencia = re.match(r"^(.*?)\s*(TM|TT)\s*$", texto.strip(), re.IGNORECASE)
    if not coincidencia:
        raise ValueError(f"Sin turno TM/TT al final: '{texto}'.")
    grado = coincidencia.group(1).strip()
    if not grado:
        raise ValueError(f"Sin grado antes del turno: '{texto}'.")
    return grado, _SUFIJO_A_TURNO[coincidencia.group(2).upper()]


def parse_turno_columna(valor):
    """Valida una columna Turno suelta ("TM"/"TT", insensible a caso/espacios).

    Raises:
        ValueError: si no es TM ni TT.
    """
    codigo = (valor or "").strip().upper()
    if codigo not in _SUFIJO_A_TURNO:
        raise ValueError(f"Turno inválido: '{valor}' (use TM o TT).")
    return _SUFIJO_A_TURNO[codigo]


def parse_fila_votante(row, numero_linea=0):
    """Valida una fila del CSV y devuelve (ci, nombre, apellido, grado, turno).

    Formato canónico (5+ columnas): CI,Nombre,Apellido,Grado,Turno.
    Formato anterior (4 columnas): grado con sufijo TM/TT pegado.

    Raises:
        ValueError: con el motivo (incluye la línea si se indica).
    """
    prefijo = f"línea {numero_linea}: " if numero_linea else ""
    if len(row) < 4 or not row[0].strip():
        raise ValueError(f"{prefijo}Fila incompleta o sin CI.")
    ci, nombre, apellido = row[0].strip(), row[1].strip(), row[2].strip()
    if not ci.isdigit() or not (7 <= len(ci) <= 8):
        raise ValueError(f"{prefijo}CI inválida '{ci}'.")
    if not nombre or not apellido:
        raise ValueError(f"{prefijo}Nombre y apellido son obligatorios.")
    if len(row) >= 5:
        grado = row[3].strip()
        if not grado:
            raise ValueError(f"{prefijo}Grado vacío.")
        try:
            turno = parse_turno_columna(row[4])
        except ValueError as e:
            raise ValueError(f"{prefijo}{e}")
    else:
        try:
            grado, turno = parse_grado_turno(row[3].strip())
        except ValueError as e:
            raise ValueError(f"{prefijo}{e}")
    return ci, nombre, apellido, grado, turno

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
    El grado base no se valida contra lista (ej. "Jardin" no está
    en config.GRADOS_VOTANTES pero es un grado real del padrón).

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

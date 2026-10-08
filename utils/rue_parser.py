"""
Parseo de listas oficiales RUE (PDF con texto extraíble).

Funciones puras sobre texto ya extraído: testeables sin pypdf ni GUI.
La extracción con pypdf vive en tools/rue_a_csv.py.
"""
import re

# Curso RUE -> grado del sistema.
GRADO_RUE_A_SISTEMA = {
    "Jardín de Infantes": "Jardín",
    "Pre Escolar": "Pre Escolar",
    "1º Grado": "1er Grado",
    "2º Grado": "2do Grado",
    "3º Grado": "3er Grado",
    "4º Grado": "4to Grado",
    "5º Grado": "5to Grado",
    "6º Grado": "6to Grado",
}

TURNO_RUE_A_CSV = {"Mañana": "TM", "Tarde": "TT"}

_FILA_RE = re.compile(r"^(\d+)\s+(.*?)\s+(\d{2}/\d{2}/\d{4})\s+(Varón|Mujer)\s*$")
_TIPO_RE = re.compile(
    r"Cédula de Identidad|Pasaporte|Documento Extranjero|Certificado de Nacimiento(?: Paraguayo)?|"
    r"Sin Documento|Partida de Nacimiento"
)
_DOC_RE = re.compile(r"^([\d.]+)")


def normalizar_grado_rue(curso):
    """Convierte el CURSO del encabezado RUE al grado del sistema."""
    curso = (curso or "").strip()
    if curso not in GRADO_RUE_A_SISTEMA:
        raise ValueError(f"Curso RUE no reconocido: '{curso}'.")
    return GRADO_RUE_A_SISTEMA[curso]


def normalizar_turno_rue(turno):
    """Convierte el TURNO del encabezado RUE a TM/TT."""
    turno = (turno or "").strip().capitalize()
    if turno not in TURNO_RUE_A_CSV:
        raise ValueError(f"Turno RUE no reconocido: '{turno}'.")
    return TURNO_RUE_A_CSV[turno]


def _limpiar(texto):
    return " ".join((texto or "").split())


def dividir_nombre_completo(nombre_completo):
    """Separa 'APELLIDOS, NOMBRES' en (nombres, apellidos)."""
    partes = (nombre_completo or "").split(",", 1)
    if len(partes) != 2 or not _limpiar(partes[0]) or not _limpiar(partes[1]):
        raise ValueError(f"Nombre sin formato 'APELLIDOS, NOMBRES': '{nombre_completo}'.")
    return _limpiar(partes[1]), _limpiar(partes[0])


def ci_o_nacimiento(tipo_doc, num_doc, fecha_nac):
    """Devuelve la CI si hay documento, o la fecha DDMMYYYY si no.

    Returns:
        tuple: (ci, aviso) donde aviso es None o describe el fallback.
    """
    digitos = re.sub(r"\D", "", num_doc or "")
    if digitos:
        return digitos, None
    m = re.match(r"^(\d{2})/(\d{2})/(\d{4})$", (fecha_nac or "").strip())
    if not m:
        raise ValueError(f"Sin documento válido ni fecha de nacimiento: '{fecha_nac}'.")
    return f"{m.group(1)}{m.group(2)}{m.group(3)}", f"sin {tipo_doc or 'documento'}: usa nacimiento {fecha_nac}"


def parse_fila_rue(linea):
    """Parsea una línea de la tabla RUE (anclada en fecha+sexo al final).

    Returns:
        tuple: (orden, nombres, apellidos, ci, aviso) o None si no es fila.

    Raises:
        ValueError: si tiene forma de fila pero contenido inválido
            (tipo desconocido o nombre sin coma).
    """
    m = _FILA_RE.match((linea or "").strip())
    if not m:
        return None
    orden, medio, fecha_nac = int(m.group(1)), m.group(2), m.group(3)
    t = _TIPO_RE.search(medio)
    if not t:
        raise ValueError(f"Tipo de documento no reconocido: '{linea.strip()[:80]}'.")
    nombres, apellidos = dividir_nombre_completo(medio[:t.start()].strip())
    resto = medio[t.end():].strip()
    dm = _DOC_RE.match(resto)
    ci, aviso = ci_o_nacimiento(t.group(0), dm.group(1) if dm else "", fecha_nac)
    return orden, nombres, apellidos, ci, aviso


def verificar_orden(filas):
    """Verifica que los números de orden sean 1..N continuos.

    Returns:
        list: mensajes de advertencia (vacía si está bien).
    """
    ordenes = [f[0] for f in filas]
    esperados = list(range(1, len(ordenes) + 1))
    if ordenes != esperados:
        faltan = sorted(set(esperados) - set(ordenes))
        return [f"orden discontinuo: faltan {faltan} (posible corte entre páginas)"]
    return []

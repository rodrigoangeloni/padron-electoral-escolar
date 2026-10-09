"""
Convierte listas oficiales RUE (PDF) a CSV del padrón.

Uso:
    .venv\\Scripts\\python.exe tools/rue_a_csv.py [--entrada DIR] [--salida DIR]

Por defecto lee padron_votantes_2026/PDF_LISTA_RUE y escribe los CSV
(CI,Nombre,Apellido,Grado,Turno) en padron_votantes_2026/.

Requiere: pip install pypdf  (solo para esta utilidad, no va en requirements.txt)

- Sin CI en el RUE: usa fecha de nacimiento DDMMYYYY (con aviso).
- Valida cada fila con la misma función que usa la importación (parse_fila_votante).
- Sale con código 1 si alguna fila fue rechazada.
"""
import argparse
import csv
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

try:
    from pypdf import PdfReader
    _FALTA_PYPDF = None
except ImportError as e:
    PdfReader = None
    _FALTA_PYPDF = e

from utils.rue_parser import (
    normalizar_grado_rue,
    normalizar_turno_rue,
    parse_fila_rue,
    verificar_orden,
)
from utils.turno_utils import parse_fila_votante

CURSO_RE = re.compile(r"CURSO\s+(.+?)(?:\n|CODIGO)")
TURNO_RE = re.compile(r"TURNO\s+(Mañana|Tarde)")


def convertir_pdf(ruta_pdf):
    """Extrae (grado, turno, filas) de un PDF RUE.

    Returns:
        tuple: (grado, turno_tm_tt, [(ci, nombres, apellidos, aviso)], advertencias).

    Raises:
        ImportError: si pypdf no está instalado.
    """
    if PdfReader is None:
        raise ImportError(
            "Falta pypdf: instalalo con  .venv\\Scripts\\python.exe -m pip install pypdf"
        ) from _FALTA_PYPDF
    texto = "\n".join((p.extract_text() or "") for p in PdfReader(ruta_pdf).pages)
    advertencias = []

    m_curso = CURSO_RE.search(texto)
    m_turno = TURNO_RE.search(texto)
    if not m_curso or not m_turno:
        raise ValueError(f"Sin encabezado CURSO/TURNO en {os.path.basename(ruta_pdf)}.")
    grado = normalizar_grado_rue(m_curso.group(1).strip())
    turno = normalizar_turno_rue(m_turno.group(1))

    lineas = texto.split("\n")
    parseadas = []
    con_error = set()
    for i, l in enumerate(lineas):
        try:
            parseadas.append((i, parse_fila_rue(l)))
        except ValueError as e:
            advertencias.append(str(e))
            parseadas.append((i, None))
            con_error.add(i)
            continue
    filas = [p for _, p in parseadas if p]
    if parseadas:
        primero = next(i for i, p in parseadas if p)
        ultimo = max(i for i, p in parseadas if p)
        # Solo importan las líneas con pinta de fila (empiezan con orden):
        # el membrete entre medio es ruido esperado.
        ignoradas = [lineas[i].strip() for i, p in parseadas
                     if p is None and i not in con_error and primero < i < ultimo
                     and lineas[i].strip() and re.match(r"^\d+\s", lineas[i].strip())]
        for texto_ign in ignoradas[:5]:
            advertencias.append(f"línea no reconocida: '{texto_ign[:80]}'")
    advertencias.extend(verificar_orden(filas))

    votantes = []
    for orden, nombres, apellidos, ci, aviso in filas:
        try:
            votantes.append(parse_fila_votante([ci, nombres, apellidos, grado, turno], orden))
        except ValueError as e:
            advertencias.append(str(e))
        if aviso:
            advertencias.append(f"orden {orden}: {aviso}")
    return grado, turno, votantes, advertencias


def main():
    parser = argparse.ArgumentParser(description="Convierte PDF RUE a CSV del padrón.")
    parser.add_argument("--entrada", default=os.path.join(RAIZ, "padron_votantes_2026", "PDF_LISTA_RUE"))
    parser.add_argument("--salida", default=os.path.join(RAIZ, "padron_votantes_2026"))
    args = parser.parse_args()

    pdfs = sorted(f for f in os.listdir(args.entrada) if f.lower().endswith(".pdf"))
    if not pdfs:
        sys.exit(f"Sin PDF en {args.entrada}.")
    os.makedirs(args.salida, exist_ok=True)

    total_ok, total_adv, fallos = 0, 0, []
    for pdf in pdfs:
        try:
            grado, turno, votantes, advertencias = convertir_pdf(os.path.join(args.entrada, pdf))
        except ImportError as e:
            sys.exit(str(e))
        except ValueError as e:
            fallos.append(f"{pdf}: {e}")
            continue
        nombre_csv = f"{grado} {turno}.csv"
        with open(os.path.join(args.salida, nombre_csv), "w", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["CI", "Nombre", "Apellido", "Grado", "Turno"])
            writer.writerows(votantes)
        total_ok += len(votantes)
        total_adv += len(advertencias)
        estado = f"OK {len(votantes)} filas -> {nombre_csv}"
        if advertencias:
            estado += f"  ({len(advertencias)} avisos)"
            for a in advertencias[:5]:
                estado += f"\n    - {a}"
        print(estado)

    print(f"--- total: {total_ok} votantes en {len(pdfs) - len(fallos)} archivos, {total_adv} avisos")
    if fallos:
        print("FALLOS:")
        for f in fallos:
            print(f"  - {f}")
        sys.exit(1)


if __name__ == "__main__":
    main()

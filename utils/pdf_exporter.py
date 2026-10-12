"""
Exportación del acta de resultados a PDF.

Cada sección corresponde a un turno (o al general) e incluye:
participación del padrón, ganadores con porcentaje y tabla detallada.
Al final va la línea de firma del presidente de mesa o encargado.
El pie de página acredita al desarrollador y la versión del programa.
"""
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from datetime import datetime
import config

FONT = "helvetica"


class PDFExporter(FPDF):
    def header(self):
        self.set_font(FONT, 'B', 16)
        self.cell(0, 10, 'Acta de Resultados Electorales', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.set_font(FONT, '', 8)
        self.cell(0, 10, f"Generada el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font(FONT, 'I', 8)
        self.cell(0, 10, f'Desarrollado por {config.DESARROLLADOR} - v{config.APP_VERSION}',
                  new_x=XPos.RIGHT, new_y=YPos.TOP, align='L')
        self.set_x(-60)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}',
                  new_x=XPos.RIGHT, new_y=YPos.TOP, align='R')

    def chapter_title(self, title):
        self.set_font(FONT, 'B', 14)
        self.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)

    def add_participacion(self, habilitados, votaron):
        pct = (votaron / habilitados * 100) if habilitados else 0.0
        self.set_font(FONT, '', 11)
        self.cell(0, 8, f"Habilitados: {habilitados}   Votaron: {votaron}   "
                        f"Participación: {pct:.1f}%",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)

    def add_ganadores(self, winners, totales_por_cargo):
        if not winners:
            self.set_font(FONT, '', 12)
            self.cell(0, 10, "Sin votos registrados.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            return
        for cargo, datos in winners.items():
            total = totales_por_cargo.get(cargo, 0)
            pct = (datos['votos'] / total * 100) if total else 0.0
            self.set_font(FONT, 'B', 12)
            self.cell(0, 9, f"Cargo: {cargo}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_font(FONT, '', 12)
            self.cell(0, 9, f"  Ganador: {datos['nombre']} {datos['apellido']}".rstrip()
                        + f"  ({datos['votos']} votos, {pct:.1f}%)",
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(5)

    def add_results_table(self, headers, data):
        self.set_font(FONT, 'B', 9)
        if len(headers) == 7:  # sección general: incluye columna Turno
            col_widths = [34, 34, 28, 20, 18, 14, 14]
        else:
            col_widths = [42, 42, 34, 24, 16, 16]
        self.set_fill_color(30, 130, 200)
        self.set_text_color(255, 255, 255)
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 9, header, border=1, new_x=XPos.RIGHT, new_y=YPos.TOP,
                      align='C', fill=True)
        self.ln()
        self.set_text_color(0, 0, 0)
        self.set_font(FONT, '', 9)
        zebra = False
        for row in data:
            if zebra:
                self.set_fill_color(235, 245, 255)
            for i, item in enumerate(row):
                align = 'C' if i >= 4 else 'L'
                self.cell(col_widths[i], 8, str(item), border=1, new_x=XPos.RIGHT, new_y=YPos.TOP,
                          align=align, fill=zebra)
            self.ln()
            zebra = not zebra

    def add_firmas(self):
        self.ln(12)
        self.chapter_title("Firma")
        y = self.get_y() + 14
        x = 75
        self.line(x, y, x + 60, y)
        self.set_xy(x, y + 2)
        self.cell(60, 8, "Presidente de Mesa o Encargado", align='C')
        self.set_y(y + 12)


def _totales_por_cargo(resultados):
    """Suma votos por cargo desde filas crudas de get_resultados()."""
    totales = {}
    for fila in resultados:
        totales[fila[3]] = totales.get(fila[3], 0) + fila[5]
    return totales


def export_acta(secciones, file_path):
    """Exporta el acta con una sección por turno.

    Args:
        secciones: lista de dicts con claves:
            turno: 'MAÑANA'/'TARDE'/None (None = general sin filtro).
            participacion: (habilitados, votaron).
            winners: {cargo: {'nombre', 'apellido', 'votos'}}
                (nombre puede ser "Empate: ..." si corresponde).
            resultados: filas crudas de get_resultados()
                (id, nombre, apellido, cargo, grado, votos, foto, turno).
        file_path: ruta del PDF a generar.
    """
    pdf = PDFExporter()
    pdf.alias_nb_pages('{nb}')
    pdf.set_auto_page_break(True, margin=20)
    pdf.add_page()

    for seccion in secciones:
        turno = seccion.get("turno")
        titulo = f"Turno {turno.capitalize()}" if turno else "Resultados Generales"
        pdf.chapter_title(titulo)

        habilitados, votaron = seccion.get("participacion", (0, 0))
        pdf.add_participacion(habilitados, votaron)

        resultados = seccion.get("resultados", [])
        pdf.add_ganadores(seccion.get("winners", {}), _totales_por_cargo(resultados))

        if resultados:
            pdf.chapter_title("Resultados Detallados")
            totales = _totales_por_cargo(resultados)
            filas = []
            for fila in resultados:
                nombre, apellido, cargo, grado, votos = fila[1], fila[2], fila[3], fila[4], fila[5]
                total = totales[cargo]
                pct = (votos / total * 100) if total else 0.0
                base = (nombre, apellido, cargo, grado)
                if turno is None:
                    turno_txt = fila[7].capitalize() if fila[7] else ""
                    filas.append(base + (turno_txt, votos, f"{pct:.1f}%"))
                else:
                    filas.append(base + (votos, f"{pct:.1f}%"))
            if turno is None:
                headers = ["Nombre", "Apellido", "Cargo", "Grado", "Turno", "Votos", "%"]
            else:
                headers = ["Nombre", "Apellido", "Cargo", "Grado", "Votos", "%"]
            pdf.add_results_table(headers, filas)
        pdf.ln(5)

    pdf.add_firmas()
    pdf.output(file_path)

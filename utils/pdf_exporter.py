"""
Módulo para exportar resultados a PDF
"""
from fpdf import FPDF
from datetime import datetime
import config

class PDFExporter(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Reporte Oficial de Resultados Electorales', 0, 1, 'C')
        self.set_font('Arial', '', 8)
        self.cell(0, 10, f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        
        # Número de página
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')
        
        # Créditos
        self.set_x(-80) 
        self.cell(0, 10, 'Sistema de Votación Escolar - Desarrollado por Rodrigo Angeloni', 0, 0, 'R')


    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(5)

    def chapter_body(self, data):
        self.set_font('Arial', '', 12)
        for key, value in data.items():
            self.multi_cell(0, 10, f"{key}: {value}")
        self.ln()

    def add_results_table(self, headers, data):
        self.set_font('Arial', 'B', 10)
        col_widths = [40, 40, 40, 30, 20]
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 10, header, 1, 0, 'C')
        self.ln()

        self.set_font('Arial', '', 10)
        for row in data:
            for i, item in enumerate(row):
                self.cell(col_widths[i], 10, str(item), 1, 0, 'C')
            self.ln()

def export_results_to_pdf(winners, results, file_path):
    """
    Exporta los resultados de la elección a un archivo PDF.
    
    :param winners: Un diccionario con los ganadores por cargo.
    :param results: Una lista de tuplas con los resultados detallados.
    :param file_path: La ruta donde se guardará el archivo PDF.
    """
    pdf = PDFExporter()
    pdf.add_page()
    
    pdf.chapter_title("Ganadores de la Elección")
    
    if not winners:
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, "No hay ganadores definidos.", 0, 1)
    else:
        for cargo, winner_data in winners.items():
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, f"Cargo: {cargo}", 0, 1)
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, f"  Nombre: {winner_data['nombre']} {winner_data['apellido']}", 0, 1)
            pdf.cell(0, 10, f"  Votos: {winner_data['votos']}", 0, 1)
            pdf.ln(5)

    pdf.ln(10)
    
    pdf.chapter_title("Resultados Detallados")
    
    headers = ["Nombre", "Apellido", "Cargo", "Grado", "Votos"]
    pdf.add_results_table(headers, results)
    
    pdf.output(file_path)

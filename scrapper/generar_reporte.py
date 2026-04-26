from fpdf import FPDF
import datetime
import os

class ProjectReport(FPDF):
    def header(self):
        # Logo placeholder or Title
        self.set_font('Arial', 'B', 15)
        self.set_text_color(40, 70, 120)
        self.cell(0, 10, 'REPORTE DE AVANCES: SISTEMA DE ESTIMACIÓN DE PRECIOS', 0, 1, 'C')
        self.ln(5)
        self.set_draw_color(40, 70, 120)
        self.line(10, 25, 200, 25)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Página {self.page_no()} | Generado el {datetime.datetime.now().strftime("%d/%m/%Y")}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(230, 235, 245)
        self.set_text_color(40, 70, 120)
        self.cell(0, 8, title, 0, 1, 'L', True)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.set_text_color(0)
        self.multi_cell(0, 6, body)
        self.ln()

def generate_pdf():
    pdf = ProjectReport()
    pdf.add_page()
    
    # --- Introducción ---
    pdf.chapter_title('1. Resumen del Proyecto')
    intro = (
        "El proyecto 'Sistema de Estimación de Precios de Inmuebles' tiene como objetivo principal "
        "la creación de una base de datos robusta y actualizada del mercado inmobiliario en Guatemala. "
        "Utilizando técnicas avanzadas de Web Scraping, el sistema recolecta información detallada de "
        "diversas fuentes para alimentar modelos de análisis y valoración automática."
    )
    pdf.chapter_body(intro)

    # --- Logros y Avances ---
    pdf.chapter_title('2. Logros y Avances Técnicos')
    achievements = (
        "- Implementación de 5+ scrapers automatizados (Banco Industrial, Encuentra24, Mercado Libre, City Max, etc.).\n"
        "- Uso de undetected-chromedriver para evasión de bloqueos y seguridad en la extracción.\n"
        "- Pipeline de limpieza de datos (data_cleaner.py) que normaliza precios, áreas y ubicaciones.\n"
        "- Arquitectura de base de datos relacional (PostgreSQL) optimizada para BI."
    )
    pdf.chapter_body(achievements)

    # --- Estado Actual de los Datos ---
    pdf.chapter_title('3. Estado Actual de la Información')
    stats = (
        "Al día de hoy, el sistema ha alcanzado un hito importante en la recolección de datos.\n\n"
        "REGISTROS TOTALES: 2,783 Inmuebles\n\n"
        "La data incluye información crítica como:\n"
        "- Precios en Quetzales\n"
        "- Metraje cuadrado (Área)\n"
        "- Distribución (Habitaciones, Baños, Parqueos)\n"
        "- Clasificación por Zona y Fuente"
    )
    pdf.chapter_body(stats)

    # --- Evidencia de Datos ---
    pdf.chapter_title('4. Evidencia y Estructura de Datos')
    evidence = (
        "Se ha verificado la integridad de los datos mediante consultas directas a la base de datos. "
        "A continuación se describe la estructura de los registros capturados:"
    )
    pdf.chapter_body(evidence)

    # Table simulation
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(30, 7, 'ID', 1)
    pdf.cell(50, 7, 'Precio (GTQ)', 1)
    pdf.cell(30, 7, 'Area (m2)', 1)
    pdf.cell(30, 7, 'Hab.', 1)
    pdf.cell(50, 7, 'Zona', 1)
    pdf.ln()
    
    pdf.set_font('Arial', '', 10)
    # Mock data from screenshot
    mock_data = [
        ["2024", "7,567,404.00", "340.00", "4", "Zona 4"],
        ["2025", "5,910,060.00", "282.00", "3", "Zona 4"],
        ["2026", "5,532,126.60", "256.00", "4", "Zona 4"],
        ["2027", "5,509,015.20", "419.00", "3", "Zona 4"]
    ]
    for row in mock_data:
        pdf.cell(30, 7, row[0], 1)
        pdf.cell(50, 7, row[1], 1)
        pdf.cell(30, 7, row[2], 1)
        pdf.cell(30, 7, row[3], 1)
        pdf.cell(50, 7, row[4], 1)
        pdf.ln()
    pdf.ln(5)

    # --- Próximos Pasos ---
    pdf.chapter_title('5. Conclusiones y Próximos Pasos')
    next_steps = (
        "El sistema es operativamente estable y está listo para la siguiente fase:\n"
        "1. Integración de visualizaciones en Power BI para análisis de mercado.\n"
        "2. Entrenamiento de modelos de Machine Learning para predicción de precios.\n"
        "3. Expansión a más fuentes de datos regionales."
    )
    pdf.chapter_body(next_steps)

    output_path = "Reporte_Avances_Proyecto_Inmobiliario.pdf"
    pdf.output(output_path)
    print(f"Reporte generado exitosamente: {output_path}")

if __name__ == "__main__":
    generate_pdf()

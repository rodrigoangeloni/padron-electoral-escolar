"""
Módulo para la funcionalidad de UI de resultados
"""
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import config
from utils.path_handler import get_images_dir
from utils.pdf_exporter import export_results_to_pdf


class ResultsUI:
    def __init__(self, parent_frame, db_manager):
        self.parent_frame = parent_frame
        self.db_manager = db_manager
        self.results_tree = None
        self.winners_widgets = {}
        self.graphs_frame = None
        self._figura_actual = None

    def setup_results_tab(self, refresh_callback=None, reset_callback=None):
        """Configura la pestaña de resultados"""
        controls_frame = tk.Frame(self.parent_frame)
        controls_frame.pack(fill="x", padx=10, pady=10)
        
        refresh_button = tk.Button(controls_frame, text="Actualizar Resultados", command=refresh_callback, bg=config.COLOR_PRIMARY, fg=config.COLOR_WHITE)
        refresh_button.pack(side="left", padx=5)
        reset_button = tk.Button(controls_frame, text="Reiniciar Votación", command=reset_callback, bg=config.COLOR_WARNING, fg=config.COLOR_WHITE)
        reset_button.pack(side="left", padx=5)
        
        export_button = tk.Button(controls_frame, text="Exportar a PDF", command=self._export_results_to_pdf, bg=config.COLOR_SUCCESS, fg=config.COLOR_WHITE)
        export_button.pack(side="left", padx=5)

        results_notebook = ttk.Notebook(self.parent_frame)
        results_notebook.pack(fill="both", expand=True, padx=10, pady=10)

        summary_frame = tk.Frame(results_notebook)
        results_notebook.add(summary_frame, text="Resumen")
        self.setup_summary_tab(summary_frame)

        self.graphs_frame = tk.Frame(results_notebook)
        results_notebook.add(self.graphs_frame, text="Gráficos")

    def setup_summary_tab(self, parent_frame):
        """Configura la pestaña de resumen de resultados"""
        self.winners_frame = tk.LabelFrame(parent_frame, text="Ganadoras de la Elección", font=("Arial", 14, "bold"), padx=20, pady=20)
        self.winners_frame.pack(fill="x", padx=10, pady=10)
        
        self.results_general_frame = tk.LabelFrame(parent_frame, text="Resultados Detallados", padx=10, pady=10)
        self.results_general_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("Nombre", "Apellido", "Cargo", "Grado", "Votos")
        self.results_tree = ttk.Treeview(self.results_general_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=120, anchor="center")
        
        scrollbar = ttk.Scrollbar(self.results_general_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        self.results_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _setup_winners_ui(self, cargos):
        """Crea la UI de ganadores dinámicamente."""
        for widget in self.winners_frame.winfo_children():
            widget.destroy()
        
        self.winners_widgets = {}
        
        num_cargos = len(cargos)
        self.winners_frame.grid_columnconfigure(tuple(range(num_cargos)), weight=1)
        
        for i, cargo in enumerate(cargos):
            cargo_frame = tk.Frame(self.winners_frame)
            cargo_frame.grid(row=0, column=i, padx=10, pady=10, sticky="n")
            tk.Label(cargo_frame, text=cargo, font=("Arial", 16, "bold"), fg="#2980b9").pack(pady=(0,10))
            img_label = tk.Label(cargo_frame, text="Esperando...", font=("Arial", 10), wraplength=150, height=8, width=20, relief="groove")
            img_label.pack()
            name_label = tk.Label(cargo_frame, text="", font=("Arial", 12, "bold"))
            name_label.pack(pady=5)
            votes_label = tk.Label(cargo_frame, text="", font=("Arial", 12))
            votes_label.pack()
            self.winners_widgets[cargo] = {'img': img_label, 'name': name_label, 'votes': votes_label}

    def refresh_results(self):
        """Actualiza los resultados mostrados"""
        cargos = self.db_manager.get_cargos()
        self._setup_winners_ui(cargos)

        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        for widget in self.graphs_frame.winfo_children():
            widget.destroy()

        resultados, _ = self.db_manager.get_resultados()

        # Columnas visibles: (Nombre, Apellido, Cargo, Grado, Votos); el id
        # va primero y la foto al final: no se muestran.
        for resultado in resultados:
            self.results_tree.insert('', 'end', values=resultado[1:6])

        winners = self.db_manager.get_ganadores()

        for cargo, widgets in self.winners_widgets.items():
            top = winners.get(cargo, [])
            if top:
                winner_data = top[0]
                try:
                    img = Image.open(winner_data['foto']).resize((150, 150), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                except:
                    photo = None

                widgets['img'].config(image=photo, text="", height=150, width=150)
                if photo: widgets['img'].image = photo
                if len(top) == 1:
                    widgets['name'].config(text=f"{winner_data['nombre']} {winner_data['apellido']}")
                else:
                    empatados = ", ".join(f"{c['nombre']} {c['apellido']}" for c in top)
                    widgets['name'].config(text=f"Empate: {empatados}")
                widgets['votes'].config(text=f"{winner_data['votos']} votos")
            else:
                widgets['img'].config(image='', text="Sin votos", height=8, width=20)
                widgets['name'].config(text="")
                widgets['votes'].config(text="")

        self._update_graphs(resultados, cargos)

    def _update_graphs(self, resultados, cargos):
        """Actualiza los gráficos de resultados"""
        for widget in self.graphs_frame.winfo_children():
            widget.destroy()

        if self._figura_actual is not None:
            plt.close(self._figura_actual)
            self._figura_actual = None

        num_cargos = len(cargos)
        if num_cargos == 0:
            return

        fig = crear_figura_resultados(resultados, cargos)
        self._figura_actual = fig

        canvas = FigureCanvasTkAgg(fig, master=self.graphs_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def _export_results_to_pdf(self):
        """Exporta los resultados actuales a un archivo PDF."""
        resultados, _ = self.db_manager.get_resultados()

        if not resultados:
            messagebox.showinfo("Exportar a PDF", "No hay resultados para exportar.")
            return

        winners_pdf = {}
        for cargo, top in self.db_manager.get_ganadores().items():
            if len(top) == 1:
                winners_pdf[cargo] = {'nombre': top[0]['nombre'],
                                      'apellido': top[0]['apellido'],
                                      'votos': top[0]['votos']}
            else:
                empatados = ", ".join(f"{c['nombre']} {c['apellido']}" for c in top)
                winners_pdf[cargo] = {'nombre': f"Empate: {empatados}",
                                      'apellido': "",
                                      'votos': top[0]['votos']}

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf"), ("All files", "*.*")],
            title="Guardar resultados como PDF"
        )

        if not file_path:
            return

        try:
            filas_pdf = [r[1:6] for r in resultados]
            export_results_to_pdf(winners_pdf, filas_pdf, file_path)
            messagebox.showinfo("Exportar a PDF", f"Resultados exportados exitosamente a:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error de Exportación", f"No se pudo exportar el archivo PDF.\nError: {e}")


def crear_figura_resultados(resultados, cargos):
    """Crea la figura de barras horizontales (un subplot por cargo).

    Función pura sin dependencias de Tk: testeable sin display.

    Args:
        resultados: filas (id, nombre, apellido, cargo, grado, votos, foto).
        cargos: lista de nombres de cargo.

    Returns:
        matplotlib.figure.Figure lista para embeber.
    """
    num_cargos = len(cargos)
    fig = plt.figure(figsize=(4 * num_cargos, 6))

    for i, cargo in enumerate(cargos):
        ax = fig.add_subplot(1, num_cargos, i + 1)

        cargo_results = [row for row in resultados if row[3] == cargo]

        if not cargo_results:
            ax.text(0.5, 0.5, 'Sin datos', ha='center', va='center')
            ax.set_title(cargo)
            ax.set_xticks([])
            ax.set_yticks([])
            continue

        nombres = [f"{r[1]} {r[2]}" for r in cargo_results]
        votos = [r[5] for r in cargo_results]

        ax.barh(nombres, votos, color='#3498db')
        ax.set_title(cargo)
        ax.set_xlabel('Votos')
        ax.invert_yaxis()

        for index, value in enumerate(votos):
            ax.text(value, index, f' {value}')

    fig.tight_layout(pad=3.0)
    return fig
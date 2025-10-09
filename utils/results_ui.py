"""
Módulo para la funcionalidad de UI de resultados
"""
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import config
from utils.path_handler import get_images_dir


class ResultsUI:
    def __init__(self, parent_frame, db_manager):
        self.parent_frame = parent_frame
        self.db_manager = db_manager
        self.results_tree = None
        self.winners_widgets = {}
        self.graphs_frame = None

    def setup_results_tab(self, refresh_callback=None, reset_callback=None):
        """Configura la pestaña de resultados"""
        controls_frame = tk.Frame(self.parent_frame)
        controls_frame.pack(fill="x", padx=10, pady=10)
        
        refresh_button = tk.Button(controls_frame, text="Actualizar Resultados", command=refresh_callback, bg=config.COLOR_PRIMARY, fg=config.COLOR_WHITE)
        refresh_button.pack(side="left", padx=5)
        reset_button = tk.Button(controls_frame, text="Reiniciar Votación", command=reset_callback, bg=config.COLOR_WARNING, fg=config.COLOR_WHITE)
        reset_button.pack(side="left", padx=5)

        results_notebook = ttk.Notebook(self.parent_frame)
        results_notebook.pack(fill="both", expand=True, padx=10, pady=10)

        summary_frame = tk.Frame(results_notebook)
        results_notebook.add(summary_frame, text="Resumen")
        self.setup_summary_tab(summary_frame)

        self.graphs_frame = tk.Frame(results_notebook)
        results_notebook.add(self.graphs_frame, text="Gráficos")

    def setup_summary_tab(self, parent_frame):
        """Configura la pestaña de resumen de resultados"""
        winners_frame = tk.LabelFrame(parent_frame, text="Ganadoras de la Elección", font=("Arial", 14, "bold"), padx=20, pady=20)
        winners_frame.pack(fill="x", padx=10, pady=10)
        winners_frame.grid_columnconfigure((0, 1, 2), weight=1)

        for i, cargo in enumerate(config.CARGOS):
            cargo_frame = tk.Frame(winners_frame)
            cargo_frame.grid(row=0, column=i, padx=10, pady=10, sticky="n")
            tk.Label(cargo_frame, text=cargo, font=("Arial", 16, "bold"), fg="#2980b9").pack(pady=(0,10))
            img_label = tk.Label(cargo_frame, text="Esperando...", font=("Arial", 10), wraplength=150, height=8, width=20, relief="groove")
            img_label.pack()
            name_label = tk.Label(cargo_frame, text="", font=("Arial", 12, "bold"))
            name_label.pack(pady=5)
            votes_label = tk.Label(cargo_frame, text="", font=("Arial", 12))
            votes_label.pack()
            self.winners_widgets[cargo] = {'img': img_label, 'name': name_label, 'votes': votes_label}

        results_general_frame = tk.LabelFrame(parent_frame, text="Resultados Detallados", padx=10, pady=10)
        results_general_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        columns = ("Nombre", "Apellido", "Cargo", "Grado", "Votos")
        self.results_tree = ttk.Treeview(results_general_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=120, anchor="center")
        
        scrollbar = ttk.Scrollbar(results_general_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        self.results_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def refresh_results(self):
        """Actualiza los resultados mostrados"""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        for widget in self.graphs_frame.winfo_children():
            widget.destroy()

        resultados, _ = self.db_manager.get_resultados()
        
        for resultado in resultados:
            self.results_tree.insert('', 'end', values=resultado)

        winners = {}
        for row in resultados:
            cargo, votos = row[2], row[4]
            if cargo not in winners or votos > winners[cargo]['votos']:
                candidato_obj = self.db_manager.get_candidato_by_name(row[0], row[1])
                if candidato_obj:
                    winners[cargo] = {'nombre': row[0], 'apellido': row[1], 'votos': votos, 'foto': candidato_obj[5]}

        for cargo, widgets in self.winners_widgets.items():
            if cargo in winners:
                winner_data = winners[cargo]
                try:
                    img = Image.open(winner_data['foto']).resize((150, 150), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                except:
                    photo = None
                
                widgets['img'].config(image=photo, text="", height=150, width=150)
                if photo: widgets['img'].image = photo
                widgets['name'].config(text=f"{winner_data['nombre']} {winner_data['apellido']}")
                widgets['votes'].config(text=f"{winner_data['votos']} votos")
            else:
                widgets['img'].config(image='', text="Sin votos", height=8, width=20)
                widgets['name'].config(text="")
                widgets['votes'].config(text="")

        self._update_graphs(resultados)

    def _update_graphs(self, resultados):
        """Actualiza los gráficos de resultados"""
        for widget in self.graphs_frame.winfo_children():
            widget.destroy()

        fig = plt.figure(figsize=(12, 6))
        
        for i, cargo in enumerate(config.CARGOS):
            ax = fig.add_subplot(1, 3, i + 1)
            
            cargo_results = [row for row in resultados if row[2] == cargo]
            
            if not cargo_results:
                ax.text(0.5, 0.5, 'Sin datos', ha='center', va='center')
                ax.set_title(cargo)
                ax.set_xticks([])
                ax.set_yticks([])
                continue

            nombres = [f"{r[0]} {r[1]}" for r in cargo_results]
            votos = [r[4] for r in cargo_results]
            
            ax.barh(nombres, votos, color='#3498db')
            ax.set_title(cargo)
            ax.set_xlabel('Votos')
            ax.invert_yaxis()

            for index, value in enumerate(votos):
                ax.text(value, index, f' {value}')

        fig.tight_layout(pad=3.0)

        canvas = FigureCanvasTkAgg(fig, master=self.graphs_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
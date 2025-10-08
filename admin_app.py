import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import sys
import os
import shutil
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager
from utils.auth import AuthManager
import config

class AdminApp(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db_manager = controller.db_manager
        self.auth_manager = AuthManager()

        if not os.path.exists(config.ADMIN_PASSWORD_FILE):
            self.auth_manager.set_admin_password(config.DEFAULT_ADMIN_PASSWORD)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self._create_frames()
        self.show_login_frame()

    def _create_frames(self):
        login_frame = tk.Frame(self)
        admin_panel_frame = tk.Frame(self)

        self.frames["LoginFrame"] = login_frame
        self.frames["AdminPanel"] = admin_panel_frame

        login_frame.grid(row=0, column=0, sticky="nsew")
        admin_panel_frame.grid(row=0, column=0, sticky="nsew")

        self.setup_login_ui(login_frame)
        self.setup_admin_ui(admin_panel_frame)

    def show_login_frame(self):
        self.frames["LoginFrame"].tkraise()
        self.controller.geometry(config.MAIN_WINDOW_GEOMETRY)
        self.controller.center_window()

    def show_admin_panel_frame(self):
        self.frames["AdminPanel"].tkraise()
        self.controller.geometry(config.ADMIN_WINDOW_GEOMETRY)
        self.controller.center_window()

    def setup_login_ui(self, parent_frame):
        title_label = tk.Label(parent_frame, text="Acceso Administrativo", font=("Arial", 16, "bold"))
        title_label.pack(pady=30)
        
        password_frame = tk.Frame(parent_frame)
        password_frame.pack(pady=20)
        
        password_label = tk.Label(password_frame, text="Contraseña:", font=("Arial", 12))
        password_label.pack()
        
        self.password_entry = tk.Entry(parent_frame, show="*", font=("Arial", 12), width=20)
        self.password_entry.pack(pady=5)
        self.password_entry.bind('<Return>', lambda event: self.login())
        
        login_button = tk.Button(parent_frame, text="Iniciar Sesión", font=("Arial", 12), bg=config.COLOR_PRIMARY, fg=config.COLOR_WHITE, command=self.login, width=15, height=1)
        login_button.pack(pady=20)

        back_button = tk.Button(parent_frame, text="Volver al Menú", font=("Arial", 12), bg=config.COLOR_WARNING, fg=config.COLOR_WHITE, command=lambda: self.controller.show_frame("MainMenu"), width=15, height=1)
        back_button.pack()

    def login(self):
        password = self.password_entry.get()
        if self.auth_manager.verify_admin_password(password):
            self.show_admin_panel_frame()
        else:
            messagebox.showerror("Error", "Contraseña incorrecta")
            self.password_entry.delete(0, tk.END)
    
    def setup_admin_ui(self, parent_frame):
        close_button = tk.Button(parent_frame, text="Cerrar Sesión", font=("Arial", 12), bg=config.COLOR_DANGER, fg=config.COLOR_WHITE, command=self.logout)
        close_button.pack(pady=5, padx=5, anchor="ne")
        
        self.notebook = ttk.Notebook(parent_frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.candidates_frame = tk.Frame(self.notebook)
        self.notebook.add(self.candidates_frame, text="Candidatos")
        self.setup_candidates_tab()
        
        self.voters_frame = tk.Frame(self.notebook)
        self.notebook.add(self.voters_frame, text="Votantes")
        self.setup_voters_tab()
        
        self.results_frame = tk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="Resultados")
        self.setup_results_tab()
        
        self.config_frame = tk.Frame(self.notebook)
        self.notebook.add(self.config_frame, text="Configuración")
        self.setup_config_tab()

    def logout(self):
        self.password_entry.delete(0, tk.END)
        self.show_login_frame()

    def setup_candidates_tab(self):
        add_frame = tk.LabelFrame(self.candidates_frame, text="Agregar Candidato", padx=10, pady=10)
        add_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(add_frame, text="Nombre:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.nombre_entry = tk.Entry(add_frame, width=20)
        self.nombre_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(add_frame, text="Apellido:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.apellido_entry = tk.Entry(add_frame, width=20)
        self.apellido_entry.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(add_frame, text="Cargo:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.cargo_var = tk.StringVar(value=config.CARGOS[0])
        cargo_combo = ttk.Combobox(add_frame, textvariable=self.cargo_var, values=config.CARGOS, state="readonly")
        cargo_combo.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(add_frame, text="Grado:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.grado_var = tk.StringVar(value=config.GRADOS_CANDIDATOS[0])
        grado_combo = ttk.Combobox(add_frame, textvariable=self.grado_var, values=config.GRADOS_CANDIDATOS, state="readonly")
        grado_combo.grid(row=1, column=3, padx=5, pady=5)
        
        add_button = tk.Button(add_frame, text="Agregar Candidato", command=self.add_candidate, bg=config.COLOR_SUCCESS, fg=config.COLOR_WHITE)
        add_button.grid(row=2, column=0, columnspan=4, pady=10)
        
        list_container = tk.Frame(self.candidates_frame)
        list_container.pack(fill="both", expand=True, padx=10, pady=10)

        list_frame = tk.LabelFrame(list_container, text="Candidatos Registrados", padx=10, pady=10)
        list_frame.pack(side="left", fill="both", expand=True)
        
        columns = ("ID", "Nombre", "Apellido", "Cargo", "Grado", "Foto")
        self.candidates_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.candidates_tree.heading(col, text=col)
            self.candidates_tree.column(col, width=120)
        self.candidates_tree.column("Foto", width=50, anchor="center")
        
        self.candidates_tree.bind('<<TreeviewSelect>>', self.on_candidate_select)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.candidates_tree.yview)
        self.candidates_tree.configure(yscrollcommand=scrollbar.set)
        self.candidates_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        preview_frame = tk.LabelFrame(list_container, text="Vista Previa", padx=10, pady=10)
        preview_frame.pack(side="right", fill="y", padx=(10,0))
        self.photo_preview = tk.Label(preview_frame, width=20, height=10, relief="groove")
        self.photo_preview.pack()

        buttons_frame_candidates = tk.Frame(list_frame)
        buttons_frame_candidates.pack(pady=10)
        
        self.update_photo_button = tk.Button(buttons_frame_candidates, text="Actualizar Foto", command=self.update_candidate_photo, state="disabled")
        self.update_photo_button.pack(side="left", padx=5)

        delete_button = tk.Button(buttons_frame_candidates, text="Eliminar Candidato", command=self.delete_candidate, bg=config.COLOR_DANGER, fg=config.COLOR_WHITE)
        delete_button.pack(side="left", padx=5)
        
        self.refresh_candidates_list()

    def on_candidate_select(self, event):
        selected_item = self.candidates_tree.selection()
        if selected_item:
            self.update_photo_button.config(state="normal")
            # Obtener la ruta de la foto de la DB, no del treeview
            candidato_id = self.candidates_tree.item(selected_item)['values'][0]
            # Esto es ineficiente, pero para la UI es aceptable
            candidatos = self.db_manager.get_candidatos() 
            photo_path = config.DEFAULT_CANDIDATE_IMAGE
            for c in candidatos:
                if c[0] == candidato_id:
                    photo_path = c[5]
                    break
            
            try:
                img = Image.open(photo_path).resize((150, 150), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.photo_preview.config(image=photo, width=150, height=150)
                self.photo_preview.image = photo
            except:
                self.photo_preview.config(image='', text="Sin imagen")
        else:
            self.update_photo_button.config(state="disabled")
            self.photo_preview.config(image='', text="")


    def update_candidate_photo(self):
        selected_item = self.candidates_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un candidato para actualizar su foto.")
            return

        candidato_id = self.candidates_tree.item(selected_item)['values'][0]
        
        file_path = filedialog.askopenfilename(
            title="Seleccionar foto del candidato",
            filetypes=[("Archivos de Imagen", "*.jpg *.jpeg *.png"), ("Todos los archivos", "*.*")]
        )
        if not file_path:
            return

        try:
            file_extension = os.path.splitext(file_path)[1]
            new_filename = f"candidate_{candidato_id}{file_extension}"
            destination_path = os.path.join(config.IMG_DIR, new_filename)

            shutil.copy(file_path, destination_path)

            self.db_manager.update_candidate_photo(candidato_id, destination_path)
            
            self.refresh_candidates_list()
            messagebox.showinfo("Éxito", "Foto del candidato actualizada correctamente.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar la foto: {e}")

    def setup_voters_tab(self):
        add_frame = tk.LabelFrame(self.voters_frame, text="Agregar Votante", padx=10, pady=10)
        add_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(add_frame, text="CI:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.ci_voter_entry = tk.Entry(add_frame, width=20)
        self.ci_voter_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(add_frame, text="Nombre:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.nombre_voter_entry = tk.Entry(add_frame, width=20)
        self.nombre_voter_entry.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(add_frame, text="Apellido:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.apellido_voter_entry = tk.Entry(add_frame, width=20)
        self.apellido_voter_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(add_frame, text="Grado/Curso:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.grado_curso_var = tk.StringVar(value=config.GRADOS_VOTANTES[0])
        grado_curso_combo = ttk.Combobox(add_frame, textvariable=self.grado_curso_var, values=config.GRADOS_VOTANTES, state="readonly", width=17)
        grado_curso_combo.grid(row=1, column=3, padx=5, pady=5)
        
        add_voter_button = tk.Button(add_frame, text="Agregar Votante", command=self.add_voter, bg=config.COLOR_SUCCESS, fg=config.COLOR_WHITE)
        add_voter_button.grid(row=2, column=0, columnspan=4, pady=10)
        
        import_frame = tk.LabelFrame(self.voters_frame, text="Importar Votantes desde Archivo", padx=10, pady=10)
        import_frame.pack(fill="x", padx=10, pady=10)
        
        import_desc = tk.Label(import_frame, text="Importar votantes desde archivo CSV (CI,Nombre,Apellido,Grado/Curso)")
        import_desc.pack(pady=5)
        
        self.import_button = tk.Button(import_frame, text="Seleccionar Archivo CSV", command=self.import_voters_from_file, bg=config.COLOR_WARNING, fg=config.COLOR_WHITE)
        self.import_button.pack(pady=5)
        
        list_frame = tk.LabelFrame(self.voters_frame, text="Votantes Registrados", padx=10, pady=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("ID", "CI", "Nombre", "Apellido", "Grado/Curso", "Ya Votó")
        self.voters_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.voters_tree.heading(col, text=col)
            self.voters_tree.column(col, width=120)
        
        self.voters_tree.column("Ya Votó", width=80, anchor="center")
        
        voters_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.voters_tree.yview)
        self.voters_tree.configure(yscrollcommand=voters_scrollbar.set)
        self.voters_tree.pack(side="left", fill="both", expand=True)
        voters_scrollbar.pack(side="right", fill="y")
        
        buttons_frame = tk.Frame(list_frame)
        buttons_frame.pack(pady=10)
        
        delete_voter_button = tk.Button(buttons_frame, text="Eliminar Votante Seleccionado", command=self.delete_voter, bg=config.COLOR_DANGER, fg=config.COLOR_WHITE)
        delete_voter_button.pack(side="left", padx=5)
        
        refresh_voters_button = tk.Button(buttons_frame, text="Actualizar Lista", command=self.refresh_voters_list, bg=config.COLOR_PRIMARY, fg=config.COLOR_WHITE)
        refresh_voters_button.pack(side="left", padx=5)
        
        self.refresh_voters_list()

    def setup_results_tab(self):
        controls_frame = tk.Frame(self.results_frame)
        controls_frame.pack(fill="x", padx=10, pady=10)
        refresh_button = tk.Button(controls_frame, text="Actualizar Resultados", command=self.refresh_results, bg=config.COLOR_PRIMARY, fg=config.COLOR_WHITE)
        refresh_button.pack(side="left", padx=5)
        reset_button = tk.Button(controls_frame, text="Reiniciar Votación", command=self.reset_votes, bg=config.COLOR_WARNING, fg=config.COLOR_WHITE)
        reset_button.pack(side="left", padx=5)

        results_notebook = ttk.Notebook(self.results_frame)
        results_notebook.pack(fill="both", expand=True, padx=10, pady=10)

        summary_frame = tk.Frame(results_notebook)
        results_notebook.add(summary_frame, text="Resumen")
        self.setup_summary_tab(summary_frame)

        self.graphs_frame = tk.Frame(results_notebook)
        results_notebook.add(self.graphs_frame, text="Gráficos")

        self.refresh_results()

    def setup_summary_tab(self, parent_frame):
        winners_frame = tk.LabelFrame(parent_frame, text="Ganadoras de la Elección", font=("Arial", 14, "bold"), padx=20, pady=20)
        winners_frame.pack(fill="x", padx=10, pady=10)
        winners_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.winners_widgets = {}
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

    def setup_config_tab(self):
        status_frame = tk.LabelFrame(self.config_frame, text="Estado de la Votación", padx=10, pady=10)
        status_frame.pack(fill="x", padx=10, pady=10)
        
        self.status_label = tk.Label(status_frame, text="", font=("Arial", 12, "bold"))
        self.status_label.pack(pady=10)
        
        button_frame = tk.Frame(status_frame)
        button_frame.pack(pady=10)
        
        activate_button = tk.Button(button_frame, text="Activar Votación", command=lambda: self.set_votation_status(config.VOTACION_ACTIVA), bg=config.COLOR_SUCCESS, fg=config.COLOR_WHITE, width=15)
        activate_button.pack(side="left", padx=5)
        
        deactivate_button = tk.Button(button_frame, text="Cerrar Votación", command=lambda: self.set_votation_status(config.VOTACION_CERRADA), bg=config.COLOR_DANGER, fg=config.COLOR_WHITE, width=15)
        deactivate_button.pack(side="left", padx=5)
        
        password_frame = tk.LabelFrame(self.config_frame, text="Cambiar Contraseña de Administrador", padx=10, pady=10)
        password_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(password_frame, text="Contraseña Actual:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.current_password_entry = tk.Entry(password_frame, show="*", width=20)
        self.current_password_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(password_frame, text="Nueva Contraseña:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.new_password_entry = tk.Entry(password_frame, show="*", width=20)
        self.new_password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(password_frame, text="Confirmar Nueva Contraseña:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.confirm_password_entry = tk.Entry(password_frame, show="*", width=20)
        self.confirm_password_entry.grid(row=2, column=1, padx=5, pady=5)
        
        change_password_button = tk.Button(password_frame, text="Cambiar Contraseña", command=self.change_password, bg=config.COLOR_WARNING, fg=config.COLOR_WHITE)
        change_password_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.update_status_display()
    
    def add_candidate(self):
        nombre = self.nombre_entry.get().strip()
        apellido = self.apellido_entry.get().strip()
        cargo = self.cargo_var.get()
        grado = self.grado_var.get()
        if not nombre or not apellido:
            messagebox.showerror("Error", "Por favor, ingrese el nombre y apellido del candidato")
            return
        self.db_manager.add_candidato(nombre, apellido, cargo, grado)
        self.nombre_entry.delete(0, tk.END)
        self.apellido_entry.delete(0, tk.END)
        self.refresh_candidates_list()
        messagebox.showinfo("Éxito", "Candidato agregado correctamente")
    
    def delete_candidate(self):
        selected_item = self.candidates_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un candidato para eliminar")
            return
        item = self.candidates_tree.item(selected_item)
        candidato_id = item['values'][0]
        if messagebox.askyesno("Confirmar", "¿Está seguro que desea eliminar este candidato?"):
            self.db_manager.delete_candidato(candidato_id)
            self.refresh_candidates_list()
            messagebox.showinfo("Éxito", "Candidato eliminado correctamente")
    
    def add_voter(self):
        ci = self.ci_voter_entry.get().strip()
        nombre = self.nombre_voter_entry.get().strip()
        apellido = self.apellido_voter_entry.get().strip()
        grado_curso = self.grado_curso_var.get()
        if not ci or not nombre or not apellido:
            messagebox.showerror("Error", "Por favor, complete todos los campos obligatorios (CI, Nombre, Apellido)")
            return
        if not ci.isdigit() or len(ci) < 7 or len(ci) > 8:
            messagebox.showerror("Error", "La CI debe tener entre 7 y 8 dígitos numéricos")
            return
        success = self.db_manager.add_votante(ci, nombre, apellido, grado_curso)
        if success:
            self.ci_voter_entry.delete(0, tk.END)
            self.nombre_voter_entry.delete(0, tk.END)
            self.apellido_voter_entry.delete(0, tk.END)
            self.refresh_voters_list()
            messagebox.showinfo("Éxito", "Votante agregado correctamente")
        else:
            messagebox.showerror("Error", "La CI ya está registrada en el sistema")
    
    def delete_voter(self):
        selected_item = self.voters_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un votante para eliminar")
            return
        ci = self.voters_tree.item(selected_item)['values'][1]
        if messagebox.askyesno("Confirmar", f"¿Está seguro que desea eliminar al votante con CI {ci}?"):
            self.db_manager.delete_votante(ci)
            self.refresh_voters_list()
            messagebox.showinfo("Éxito", "Votante eliminado correctamente")
    
    def import_voters_from_file(self):
        file_path = filedialog.askopenfilename(title="Seleccionar archivo CSV", filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")])
        if not file_path:
            return

        self.controller.config(cursor="watch")
        self.import_button.config(state="disabled", text="Importando...")
        self.controller.update_idletasks()

        try:
            import csv
            votantes_list = []
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Omitir el encabezado
                for row in reader:
                    if len(row) >= 4:
                        ci, nombre, apellido, grado_curso = row[0].strip(), row[1].strip(), row[2].strip(), row[3].strip()
                        if ci.isdigit() and 7 <= len(ci) <= 8:
                            votantes_list.append((ci, nombre, apellido, grado_curso))
                        else:
                            print(f"CI inválido omitido: {ci}")
            if votantes_list:
                success_count, error_count = self.db_manager.import_votantes_from_list(votantes_list)
                self.refresh_voters_list()
                messagebox.showinfo("Importación completada", f"Importación completada: {success_count} votantes agregados, {error_count} errores (CI duplicadas)")
            else:
                messagebox.showwarning("Advertencia", "No se encontraron votantes válidos en el archivo")
        except Exception as e:
            messagebox.showerror("Error", f"Error al leer el archivo: {str(e)}")
        finally:
            self.controller.config(cursor="")
            self.import_button.config(state="normal", text="Seleccionar Archivo CSV")
    
    def refresh_candidates_list(self):
        for item in self.candidates_tree.get_children():
            self.candidates_tree.delete(item)
        candidatos = self.db_manager.get_candidatos()
        for candidato in candidatos:
            has_photo = "Sí" if candidato[5] and candidato[5] != config.DEFAULT_CANDIDATE_IMAGE else "No"
            values = (candidato[0], candidato[1], candidato[2], candidato[3], candidato[4], has_photo)
            self.candidates_tree.insert('', 'end', values=values)
    
    def refresh_voters_list(self):
        for item in self.voters_tree.get_children():
            self.voters_tree.delete(item)
        votantes = self.db_manager.get_votantes()
        for votante in votantes:
            ya_voto_text = "Sí" if votante[5] == 1 else "No"
            values = (votante[0], votante[1], votante[2], votante[3], votante[4], ya_voto_text)
            self.voters_tree.insert('', 'end', values=values)
    
    def refresh_results(self):
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

    def reset_votes(self):
        if messagebox.askyesno("Confirmar", "¿Está seguro que desea reiniciar todos los votos? Esta acción no se puede deshacer."):
            self.db_manager.reset_votos()
            self.refresh_results()
            self.refresh_voters_list()
            messagebox.showinfo("Éxito", "Votos reiniciados correctamente")
    
    def set_votation_status(self, status):
        self.db_manager.set_estado_votacion(status)
        self.update_status_display()
        status_text = "activa" if status == config.VOTACION_ACTIVA else "cerrada"
        messagebox.showinfo("Éxito", f"La votación ha sido {status_text}")
    
    def update_status_display(self):
        status = self.db_manager.get_estado_votacion()
        status_text = f"Estado actual: Votación {'ACTIVA' if status == config.VOTACION_ACTIVA else 'CERRADA'}"
        self.status_label.config(text=status_text, fg="green" if status == config.VOTACION_ACTIVA else "red")
    
    def change_password(self):
        current_password = self.current_password_entry.get()
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        if not current_password or not new_password or not confirm_password:
            messagebox.showerror("Error", "Por favor, complete todos los campos")
            return
        if new_password != confirm_password:
            messagebox.showerror("Error", "Las nuevas contraseñas no coinciden")
            return
        if len(new_password) < 6:
            messagebox.showerror("Error", "La nueva contraseña debe tener al menos 6 caracteres")
            return
        if self.auth_manager.change_admin_password(current_password, new_password):
            messagebox.showinfo("Éxito", "Contraseña cambiada correctamente")
            self.current_password_entry.delete(0, tk.END)
            self.new_password_entry.delete(0, tk.END)
            self.confirm_password_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Contraseña actual incorrecta")

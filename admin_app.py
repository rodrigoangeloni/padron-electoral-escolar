import tkinter as tk
from tkinter import messagebox, ttk, filedialog, simpledialog
import sys
import os
import shutil
import secrets
import string
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.candidate_ui import CandidateUI
from utils.voter_ui import VoterUI
from utils.results_ui import ResultsUI
from database import DatabaseManager
from utils.auth import AuthManager
import config
from utils.path_handler import get_images_dir

class AdminApp(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db_manager = controller.db_manager
        self.auth_manager = AuthManager()

        if not os.path.exists(config.ADMIN_PASSWORD_FILE):
            # Establecer una contraseña inicial segura cuando no existe archivo de contraseña
            # Generar una contraseña segura inicial
            initial_password = self.auth_manager.generate_initial_password()
            self.auth_manager.set_initial_password(initial_password)
            self.show_initial_password(initial_password)

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
        
    def show_initial_password(self, password):
        """Muestra la contraseña inicial en una ventana emergente con opción de copiar"""
        # Crear ventana emergente para mostrar la contraseña inicial
        password_window = tk.Toplevel(self)
        password_window.title("Contraseña Inicial de Administrador")
        password_window.geometry("400x200")
        password_window.resizable(False, False)
        # Centrar la ventana
        password_window.transient(self)
        password_window.grab_set()
        
        # Centrar la ventana emergente en la pantalla
        password_window.update_idletasks()
        screen_width = password_window.winfo_screenwidth()
        screen_height = password_window.winfo_screenheight()
        window_width = 400
        window_height = 200
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        password_window.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
        # Etiqueta con instrucciones
        instructions = tk.Label(password_window, text="Se ha generado una contraseña inicial de administrador:", font=("Arial", 10))
        instructions.pack(pady=10)
        
        # Campo para mostrar la contraseña
        password_var = tk.StringVar(value=password)
        password_display = tk.Entry(password_window, textvariable=password_var, font=("Arial", 12), justify="center", state="readonly")
        password_display.pack(pady=5, padx=20, fill="x")
        
        # Botón para copiar la contraseña
        copy_button = tk.Button(password_window, text="Copiar Contraseña", font=("Arial", 10), bg=config.COLOR_PRIMARY, fg=config.COLOR_WHITE,
                                command=lambda: self.copy_password(password, password_window))
        copy_button.pack(pady=10)
        
        # Botón para continuar
        continue_button = tk.Button(password_window, text="Entendido", font=("Arial", 10), bg=config.COLOR_SUCCESS, fg=config.COLOR_WHITE,
                                    command=password_window.destroy)
        continue_button.pack(pady=5)
        
        # Advertencia
        warning = tk.Label(password_window, text="Por favor, cambie esta contraseña desde la interfaz de administración", 
                          font=("Arial", 9), fg="red")
        warning.pack(pady=10)
        
        # Esperar a que se cierre la ventana antes de continuar
        password_window.wait_window()
        
    def copy_password(self, password, window):
        """Copia la contraseña al portapapeles"""
        self.clipboard_clear()
        self.clipboard_append(password)
        messagebox.showinfo("Copiado", "Contraseña copiada al portapapeles", parent=window)

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
        if self.auth_manager.esta_bloqueado():
            messagebox.showerror("Error", "Demasiados intentos fallidos. Intente de nuevo en unos segundos.")
            self.password_entry.delete(0, tk.END)
            return
        if self.auth_manager.verify_admin_password(password):
            # Verificar si se está usando la contraseña inicial
            if self.auth_manager.is_initial_password_used():
                messagebox.showwarning("Contraseña Inicial", "Está usando la contraseña inicial. Por favor, cámbiela antes de continuar.")
                self.show_admin_panel_frame()
                # Mostrar directamente la pestaña de configuración para cambiar la contraseña
                self.notebook.select(3)  # Seleccionar la pestaña de configuración (índice 3)
            else:
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
        self.candidate_ui = CandidateUI(self.candidates_frame, self.db_manager)
        self.candidate_ui.setup_candidates_tab()
        
        # Asignar referencias para que otros métodos puedan acceder a los elementos
        self.candidates_tree = self.candidate_ui.candidates_tree
        self.photo_preview = self.candidate_ui.photo_preview
        self.update_photo_button = self.candidate_ui.update_photo_button

    def setup_voters_tab(self):
        self.voter_ui = VoterUI(self.voters_frame, self.db_manager)
        self.voter_ui.setup_voters_tab()
        
        # Asignar referencias para que otros métodos puedan acceder a los elementos
        self.voters_tree = self.voter_ui.voters_tree
        self.ci_voter_entry = self.voter_ui.ci_voter_entry
        self.nombre_voter_entry = self.voter_ui.nombre_voter_entry
        self.apellido_voter_entry = self.voter_ui.apellido_voter_entry
        self.grado_curso_var = self.voter_ui.grado_curso_var
        self.import_button = self.voter_ui.import_button

    def setup_results_tab(self):
        self.results_ui = ResultsUI(self.results_frame, self.db_manager)
        self.results_ui.setup_results_tab(
            refresh_callback=self.refresh_results,
            reset_callback=self.reset_votes
        )
        
        # Asignar referencias para que otros métodos puedan acceder a los elementos
        self.results_tree = self.results_ui.results_tree
        self.graphs_frame = self.results_ui.graphs_frame

    def setup_config_tab(self):
        # Frame principal para la pestaña de configuración
        main_config_frame = tk.Frame(self.config_frame)
        main_config_frame.pack(fill="both", expand=True, padx=10, pady=10)
        main_config_frame.grid_columnconfigure(0, weight=1)

        # --- Frame para Estado de Votación y Contraseña ---
        left_frame = tk.Frame(main_config_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        status_frame = tk.LabelFrame(left_frame, text="Estado de la Votación", padx=10, pady=10)
        status_frame.pack(fill="x", pady=(0, 10))
        
        self.status_label = tk.Label(status_frame, text="", font=("Arial", 12, "bold"))
        self.status_label.pack(pady=10)
        
        button_frame = tk.Frame(status_frame)
        button_frame.pack(pady=10)
        
        activate_button = tk.Button(button_frame, text="Activar Votación", command=lambda: self.set_votation_status(config.VOTACION_ACTIVA), bg=config.COLOR_SUCCESS, fg=config.COLOR_WHITE, width=15)
        activate_button.pack(side="left", padx=5)
        
        deactivate_button = tk.Button(button_frame, text="Cerrar Votación", command=lambda: self.set_votation_status(config.VOTACION_CERRADA), bg=config.COLOR_DANGER, fg=config.COLOR_WHITE, width=15)
        deactivate_button.pack(side="left", padx=5)
        
        password_frame = tk.LabelFrame(left_frame, text="Cambiar Contraseña de Administrador", padx=10, pady=10)
        password_frame.pack(fill="x")
        
        tk.Label(password_frame, text="Contraseña Actual:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.current_password_entry = tk.Entry(password_frame, show="*", width=30)
        self.current_password_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(password_frame, text="Nueva Contraseña:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.new_password_entry = tk.Entry(password_frame, show="*", width=30)
        self.new_password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(password_frame, text="Confirmar Nueva Contraseña:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.confirm_password_entry = tk.Entry(password_frame, show="*", width=30)
        self.confirm_password_entry.grid(row=2, column=1, padx=5, pady=5)
        
        change_password_button = tk.Button(password_frame, text="Cambiar Contraseña", command=self.change_password, bg=config.COLOR_WARNING, fg=config.COLOR_WHITE)
        change_password_button.grid(row=3, column=0, columnspan=2, pady=10)

        # --- Frame para Gestión de Cargos ---
        right_frame = tk.Frame(main_config_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        main_config_frame.grid_columnconfigure(1, weight=1)

        cargos_frame = tk.LabelFrame(right_frame, text="Gestionar Cargos", padx=10, pady=10)
        cargos_frame.pack(fill="both", expand=True)

        # Frame para agregar cargo
        add_cargo_frame = tk.Frame(cargos_frame)
        add_cargo_frame.pack(fill="x", pady=5)
        tk.Label(add_cargo_frame, text="Nuevo Cargo:").pack(side="left", padx=(0, 5))
        self.new_cargo_entry = tk.Entry(add_cargo_frame, width=25)
        self.new_cargo_entry.pack(side="left", expand=True, fill="x", padx=5)
        add_cargo_button = tk.Button(add_cargo_frame, text="Agregar", command=self.add_cargo, bg=config.COLOR_SUCCESS, fg=config.COLOR_WHITE)
        add_cargo_button.pack(side="left", padx=(5, 0))

        # Frame para la lista de cargos
        cargos_list_frame = tk.Frame(cargos_frame)
        cargos_list_frame.pack(fill="both", expand=True, pady=5)
        
        self.cargos_tree = ttk.Treeview(cargos_list_frame, columns=("Cargo",), show="headings", height=8)
        self.cargos_tree.heading("Cargo", text="Cargo")
        self.cargos_tree.pack(side="left", fill="both", expand=True)
        
        cargos_scrollbar = ttk.Scrollbar(cargos_list_frame, orient="vertical", command=self.cargos_tree.yview)
        self.cargos_tree.configure(yscrollcommand=cargos_scrollbar.set)
        cargos_scrollbar.pack(side="right", fill="y")
        
        delete_cargo_button = tk.Button(cargos_frame, text="Eliminar Cargo Seleccionado", command=self.delete_cargo, bg=config.COLOR_DANGER, fg=config.COLOR_WHITE)
        delete_cargo_button.pack(pady=5)
        
        self.update_status_display()
        self.refresh_cargos_list()

    def add_cargo(self):
        """Agrega un nuevo cargo a la base de datos."""
        new_cargo = self.new_cargo_entry.get().strip()
        if not new_cargo:
            messagebox.showerror("Error", "El nombre del cargo no puede estar vacío.")
            return
        
        success, message = self.db_manager.add_cargo(new_cargo)
        if success:
            messagebox.showinfo("Éxito", message)
            self.new_cargo_entry.delete(0, tk.END)
            self.refresh_cargos_list()
            # Actualizar el combobox de candidatos
            if hasattr(self, 'candidate_ui'):
                self.candidate_ui.update_cargos_combobox()
        else:
            messagebox.showerror("Error", message)

    def delete_cargo(self):
        """Elimina el cargo seleccionado de la lista."""
        selected_item = self.cargos_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un cargo para eliminar.")
            return
            
        cargo_name = self.cargos_tree.item(selected_item, 'values')[0]
        
        if messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de que desea eliminar el cargo '{cargo_name}'?"):
            success, message = self.db_manager.delete_cargo(cargo_name)
            if success:
                messagebox.showinfo("Éxito", message)
                self.refresh_cargos_list()
                # Actualizar el combobox de candidatos
                if hasattr(self, 'candidate_ui'):
                    self.candidate_ui.update_cargos_combobox()
            else:
                messagebox.showerror("Error", message)

    def refresh_cargos_list(self):
        """Actualiza la lista de cargos en la interfaz."""
        for item in self.cargos_tree.get_children():
            self.cargos_tree.delete(item)
        
        cargos = self.db_manager.get_cargos()
        for cargo in cargos:
            self.cargos_tree.insert("", "end", values=(cargo,))

    def refresh_results(self):
        self.results_ui.refresh_results()
    
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
    
    def refresh_voters_list(self):
        # Actualizar la lista de votantes si es necesario
        if hasattr(self, 'voter_ui'):
            self.voter_ui.refresh_voters_list()

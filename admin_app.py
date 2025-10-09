import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import sys
import os
import shutil
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

class AdminApp(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db_manager = controller.db_manager
        self.auth_manager = AuthManager()

        if not os.path.exists(config.ADMIN_PASSWORD_FILE):
            # Establecer una contraseña inicial segura cuando no existe archivo de contraseña
            import secrets
            import string
            # Generar una contraseña segura inicial
            initial_password = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(12))
            self.auth_manager.set_admin_password(initial_password)
            print(f"Contraseña inicial generada: {initial_password}")
            print("Por favor, cambie esta contraseña desde la interfaz de administración")

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

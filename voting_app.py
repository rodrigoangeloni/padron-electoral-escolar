import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager
import config

class VotingApp(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db_manager = controller.db_manager
        
        self.configure(bg=config.COLOR_WHITE)

        # --- Estado de la Aplicación ---
        self.current_votante = None
        self.current_step = 0
        self.roles = config.CARGOS
        self.is_fullscreen = False
        
        # --- Selecciones ---
        self.selected_candidates = {} 

        # --- Carga de Datos ---
        self.all_candidates = {} # Se cargará al iniciar el flujo
        
        self.show_ci_input()

    def _clear_screen(self):
        """Limpia todos los widgets de este frame."""
        for widget in self.winfo_children():
            widget.destroy()

    def show_ci_input(self):
        """Muestra la interfaz para ingresar la CI del votante."""
        self._clear_screen()
        
        main_frame = tk.Frame(self, bg=config.COLOR_WHITE)
        main_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        title_label = tk.Label(main_frame, text="SISTEMA DE VOTACIÓN ESCOLAR", font=("Arial", 32, "bold"), bg=config.COLOR_WHITE, fg='#2c3e50')
        title_label.pack(pady=20)
        
        instruction_label = tk.Label(main_frame, text="Por favor, ingrese su Cédula de Identidad (CI)", font=("Arial", 22), bg=config.COLOR_WHITE, fg='#7f8c8d')
        instruction_label.pack(pady=10)
        
        ci_frame = tk.Frame(main_frame, bg=config.COLOR_WHITE)
        ci_frame.pack(pady=20)
        
        ci_label = tk.Label(ci_frame, text="CI:", font=("Arial", 18), bg=config.COLOR_WHITE)
        ci_label.pack(side='left', padx=(0, 10))
        
        self.ci_entry = tk.Entry(ci_frame, font=("Arial", 18), width=20, justify='center')
        self.ci_entry.pack(side='left')
        self.ci_entry.bind('<Return>', self.validate_ci)
        
        validate_button = tk.Button(main_frame, text="VALIDAR CI", font=("Arial", 16, "bold"), bg=config.COLOR_PRIMARY, fg=config.COLOR_WHITE, width=15, height=1, command=self.validate_ci)
        validate_button.pack(pady=20)
        
        # Botones de control de ventana
        controls_frame = tk.Frame(self, bg=config.COLOR_WHITE)
        controls_frame.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=10)
        
        fullscreen_button = tk.Button(controls_frame, text="Pantalla Completa", font=("Arial", 10), command=self.toggle_fullscreen)
        fullscreen_button.pack(side='left', padx=5)

        exit_button = tk.Button(controls_frame, text="Salir de Votación", font=("Arial", 10), bg=config.COLOR_DANGER, fg=config.COLOR_WHITE, command=self.exit_to_main_menu)
        exit_button.pack(side='left', padx=5)
        
        self.ci_entry.focus()

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.controller.attributes('-fullscreen', self.is_fullscreen)

    def validate_ci(self, event=None):
        """Valida la CI y, si es correcta, inicia el flujo de votación."""
        ci = self.ci_entry.get().strip()
        
        if not ci.isdigit() or not (7 <= len(ci) <= 8):
            messagebox.showerror("Error", "La CI debe tener entre 7 y 8 dígitos numéricos.")
            return
        
        votante = self.db_manager.get_votante(ci)
        if votante is None:
            messagebox.showerror("Error", "Votante no registrado en el sistema.")
            return
        
        if votante[5] == 1:
            messagebox.showerror("Error", "Este votante ya ha emitido su voto.")
            return
        
        self.current_votante = votante
        self.start_voting_flow()

    def start_voting_flow(self):
        """Inicia el proceso de votación paso a paso."""
        # Recargar los candidatos cada vez que se inicia un nuevo voto
        self.all_candidates = {role: self.db_manager.get_candidatos(role) for role in self.roles}
        
        self.current_step = 0
        self.selected_candidates = {}
        self.show_role_selection_screen()

    def show_role_selection_screen(self):
        """Muestra la pantalla de selección para el cargo actual."""
        self._clear_screen()
        
        current_role = self.roles[self.current_step]
        candidates_for_role = self.all_candidates[current_role]
        
        # Frame principal para centrar todo
        main_container = tk.Frame(self, bg=config.COLOR_WHITE)
        main_container.pack(fill="both", expand=True)

        step_label = tk.Label(main_container, text=f"Paso {self.current_step + 1} de {len(self.roles)}", font=("Arial", 20, "italic"), bg=config.COLOR_WHITE, fg='#7f8c8d')
        step_label.pack(pady=(20, 0))
        
        role_label = tk.Label(main_container, text=f"Elige a tu {current_role}", font=("Arial", 32, "bold"), bg=config.COLOR_WHITE, fg='#2c3e50')
        role_label.pack(pady=(0, 20))

        # Frame para la grilla de candidatos
        candidates_frame = tk.Frame(main_container, bg=config.COLOR_WHITE)
        candidates_frame.pack(expand=True)

        # Configuración de la grilla
        max_cols = 4  # Máximo de candidatos por fila
        
        for i, candidato in enumerate(candidates_for_role):
            row = i // max_cols
            col = i % max_cols
            
            candidato_frame = tk.Frame(candidates_frame, bg=config.COLOR_WHITE)
            candidato_frame.grid(row=row, column=col, padx=25, pady=25)

            img = self._load_candidate_image(candidato[5], (200, 200)) # Tamaño de imagen ajustado
            
            btn_img = tk.Button(
                candidato_frame,
                image=img,
                command=lambda c=candidato: self.select_candidate_and_advance(c),
                borderwidth=4,
                relief="groove",
                bg=config.COLOR_WHITE
            )
            btn_img.image = img
            btn_img.pack(pady=5)
            
            info_text = f"{candidato[1]} {candidato[2]}\n({candidato[4]})"
            name_label = tk.Label(candidato_frame, text=info_text, font=("Arial", 14), bg=config.COLOR_WHITE, fg='#34495e', justify="center")
            name_label.pack()

    def _load_candidate_image(self, path, size):
        """Carga una imagen de candidato o una por defecto."""
        try:
            img = Image.open(path)
        except (FileNotFoundError, IOError):
            try:
                img = Image.open(config.DEFAULT_CANDIDATE_IMAGE)
            except (FileNotFoundError, IOError):
                img = Image.new('RGB', size, color='#ecf0f1')
        
        img = img.resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)

    def select_candidate_and_advance(self, candidato):
        """Guarda la selección y avanza al siguiente paso o a la confirmación."""
        role = candidato[3]
        self.selected_candidates[role] = candidato
        
        self.current_step += 1
        
        if self.current_step < len(self.roles):
            self.show_role_selection_screen()
        else:
            self.show_final_confirmation()

    def show_final_confirmation(self):
        """Muestra las 3 selecciones finales antes de guardar el voto."""
        self._clear_screen()

        title_label = tk.Label(self, text="Revisa tu selección", font=("Arial", 32, "bold"), bg=config.COLOR_WHITE, fg='#2c3e50')
        title_label.pack(pady=(40, 20))

        selections_frame = tk.Frame(self, bg=config.COLOR_WHITE)
        selections_frame.pack(expand=True)

        for i, role in enumerate(self.roles):
            candidato = self.selected_candidates[role]
            
            selection_frame = tk.Frame(selections_frame, bg=config.COLOR_WHITE)
            selection_frame.grid(row=0, column=i, padx=20)

            role_label = tk.Label(selection_frame, text=role, font=("Arial", 20, "bold"), bg=config.COLOR_WHITE, fg='#2980b9')
            role_label.pack(pady=10)

            img = self._load_candidate_image(candidato[5], (200, 200))
            
            img_label = tk.Label(selection_frame, image=img, bg=config.COLOR_WHITE)
            img_label.image = img
            img_label.pack(pady=5)
            
            name_label = tk.Label(selection_frame, text=f"{candidato[1]} {candidato[2]}", font=("Arial", 16), bg=config.COLOR_WHITE)
            name_label.pack()

        button_frame = tk.Frame(self, bg=config.COLOR_WHITE)
        button_frame.pack(pady=40)

        change_button = tk.Button(button_frame, text="Cambiar Selección", font=("Arial", 18), bg=config.COLOR_DANGER, fg=config.COLOR_WHITE, command=self.start_voting_flow)
        change_button.grid(row=0, column=0, padx=20, ipady=10)

        confirm_button = tk.Button(button_frame, text="CONFIRMAR MI VOTO", font=("Arial", 18, "bold"), bg=config.COLOR_SUCCESS, fg=config.COLOR_WHITE, command=self._save_vote_and_reset)
        confirm_button.grid(row=0, column=1, padx=20, ipady=10)

    def _save_vote_and_reset(self):
        """Guarda los votos en la BD y reinicia la app para el siguiente votante."""
        ci_votante = self.current_votante[1]
        
        # Obtener los IDs de los candidatos seleccionados
        candidato_ids = [self.selected_candidates[role][0] for role in self.roles]
        
        # Registrar todos los votos de una vez
        success, message = self.db_manager.add_multiple_votes(candidato_ids, ci_votante)
        
        if not success:
            messagebox.showerror("Error", message)
            self.show_ci_input()
            return

        self._clear_screen()
        thanks_label = tk.Label(self, text="¡Gracias por tu voto!", font=("Arial", 40, "bold"), bg=config.COLOR_WHITE, fg=config.COLOR_SUCCESS)
        thanks_label.place(relx=0.5, rely=0.5, anchor='center')
        
        self.after(2000, self.show_ci_input)

    def exit_to_main_menu(self):
        """Sale del modo votación y regresa al menú principal."""
        if self.is_fullscreen:
            self.toggle_fullscreen()
        self.controller.show_frame("MainMenu")
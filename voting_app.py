import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import sys

# Añadir el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager

class VotingApp:
    def __init__(self):
        self.root = tk.Tk()
        self.db_manager = DatabaseManager()
        
        # --- Estado de la Aplicación ---
        self.current_votante = None
        self.current_step = 0
        self.roles = ['DIRECTORA', 'VICEDIRECTORA', 'COORDINADORA']
        
        # --- Selecciones ---
        self.selected_candidates = {} # Usaremos un diccionario para las selecciones

        # --- Carga de Datos ---
        self.all_candidates = {
            'DIRECTORA': self.db_manager.get_candidatos('DIRECTORA'),
            'VICEDIRECTORA': self.db_manager.get_candidatos('VICEDIRECTORA'),
            'COORDINADORA': self.db_manager.get_candidatos('COORDINADORA')
        }
        
        self.show_ci_input()

    def _clear_screen(self):
        """Limpia todos los widgets de la ventana principal."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_ci_input(self):
        """Muestra la interfaz para ingresar la CI del votante."""
        self._clear_screen()
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='white')
        
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        title_label = tk.Label(main_frame, text="SISTEMA DE VOTACIÓN ESCOLAR", font=("Arial", 32, "bold"), bg='white', fg='#2c3e50')
        title_label.pack(pady=20)
        
        instruction_label = tk.Label(main_frame, text="Por favor, ingrese su Cédula de Identidad (CI)", font=("Arial", 22), bg='white', fg='#7f8c8d')
        instruction_label.pack(pady=10)
        
        ci_frame = tk.Frame(main_frame, bg='white')
        ci_frame.pack(pady=20)
        
        ci_label = tk.Label(ci_frame, text="CI:", font=("Arial", 18), bg='white')
        ci_label.pack(side='left', padx=(0, 10))
        
        self.ci_entry = tk.Entry(ci_frame, font=("Arial", 18), width=20, justify='center')
        self.ci_entry.pack(side='left')
        self.ci_entry.bind('<Return>', self.validate_ci)
        
        validate_button = tk.Button(main_frame, text="VALIDAR CI", font=("Arial", 16, "bold"), bg="#3498db", fg="white", width=15, height=1, command=self.validate_ci)
        validate_button.pack(pady=20)
        
        exit_button = tk.Button(self.root, text="Salir (Prueba)", font=("Arial", 10), bg="#e74c3c", fg="white", command=self.exit_fullscreen)
        exit_button.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=10)
        
        self.ci_entry.focus()

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
        self.current_step = 0
        self.selected_candidates = {}
        self.show_role_selection_screen()

    def show_role_selection_screen(self):
        """Muestra la pantalla de selección para el cargo actual."""
        self._clear_screen()
        
        current_role = self.roles[self.current_step]
        candidates_for_role = self.all_candidates[current_role]
        
        # Título del paso
        step_label = tk.Label(self.root, text=f"Paso {self.current_step + 1} de 3", font=("Arial", 20, "italic"), bg='white', fg='#7f8c8d')
        step_label.pack(pady=(20, 0))
        
        role_label = tk.Label(self.root, text=f"Elige a tu {current_role}", font=("Arial", 32, "bold"), bg='white', fg='#2c3e50')
        role_label.pack(pady=(0, 20))

        # Contenedor para los candidatos
        candidates_frame = tk.Frame(self.root, bg='white')
        candidates_frame.pack(expand=True)

        # Crear widgets para cada candidato
        for i, candidato in enumerate(candidates_for_role):
            # Frame para un candidato individual
            candidato_frame = tk.Frame(candidates_frame, bg='white')
            candidato_frame.grid(row=0, column=i, padx=25, pady=25)

            # Cargar imagen (más grande)
            img = self._load_candidate_image(candidato[5], (250, 250))
            
            # Botón con la imagen del candidato
            btn_img = tk.Button(
                candidato_frame,
                image=img,
                command=lambda c=candidato: self.select_candidate_and_advance(c),
                borderwidth=4,
                relief="groove",
                bg="white"
            )
            btn_img.image = img
            btn_img.pack(pady=5)
            
            # Nombre y Grado
            info_text = f"{candidato[1]} {candidato[2]}\n({candidato[4]})"
            name_label = tk.Label(candidato_frame, text=info_text, font=("Arial", 16, "bold"), bg='white', fg='#34495e', justify="center")
            name_label.pack()

    def _load_candidate_image(self, path, size):
        """Carga una imagen de candidato o una por defecto."""
        try:
            img = Image.open(path)
        except (FileNotFoundError, IOError):
            try:
                img = Image.open('assets/images/default_candidate.jpg')
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

        title_label = tk.Label(self.root, text="Revisa tu selección", font=("Arial", 32, "bold"), bg='white', fg='#2c3e50')
        title_label.pack(pady=(40, 20))

        # Contenedor para las selecciones
        selections_frame = tk.Frame(self.root, bg='white')
        selections_frame.pack(expand=True)

        for i, role in enumerate(self.roles):
            candidato = self.selected_candidates[role]
            
            selection_frame = tk.Frame(selections_frame, bg='white')
            selection_frame.grid(row=0, column=i, padx=20)

            role_label = tk.Label(selection_frame, text=role, font=("Arial", 20, "bold"), bg='white', fg='#2980b9')
            role_label.pack(pady=10)

            img = self._load_candidate_image(candidato[5], (200, 200))
            
            img_label = tk.Label(selection_frame, image=img, bg='white')
            img_label.image = img
            img_label.pack(pady=5)
            
            name_label = tk.Label(selection_frame, text=f"{candidato[1]} {candidato[2]}", font=("Arial", 16), bg='white')
            name_label.pack()

        # Botones de acción
        button_frame = tk.Frame(self.root, bg='white')
        button_frame.pack(pady=40)

        change_button = tk.Button(button_frame, text="Cambiar Selección", font=("Arial", 18), bg="#e74c3c", fg="white", command=self.start_voting_flow)
        change_button.grid(row=0, column=0, padx=20, ipady=10)

        confirm_button = tk.Button(button_frame, text="CONFIRMAR MI VOTO", font=("Arial", 18, "bold"), bg="#27ae60", fg="white", command=self._save_vote_and_reset)
        confirm_button.grid(row=0, column=1, padx=20, ipady=10)

    def _save_vote_and_reset(self):
        """Guarda los votos en la BD y reinicia la app para el siguiente votante."""
        ci_votante = self.current_votante[1]
        
        # Guardar cada voto
        for role in self.roles:
            candidato_id = self.selected_candidates[role][0]
            self.db_manager.add_voto(candidato_id, ci_votante)

        # Mostrar mensaje de agradecimiento
        self._clear_screen()
        thanks_label = tk.Label(self.root, text="¡Gracias por tu voto!", font=("Arial", 40, "bold"), bg='white', fg='#27ae60')
        thanks_label.place(relx=0.5, rely=0.5, anchor='center')
        
        # Esperar 2 segundos y reiniciar
        self.root.after(2000, self.show_ci_input)

    def exit_fullscreen(self):
        """Sale del modo pantalla completa y regresa al menú principal."""
        self.root.destroy()
        from main import MainApp
        main_app = MainApp()
        main_app.run()
    
    def run(self):
        """Ejecuta la aplicación."""
        self.root.mainloop()

if __name__ == "__main__":
    app = VotingApp()
    app.run()

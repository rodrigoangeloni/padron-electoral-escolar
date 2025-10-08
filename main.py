import tkinter as tk
from tkinter import messagebox
import sys
import os

# Añadir el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from voting_app import VotingApp
from admin_app import AdminApp
from database import DatabaseManager

class MainApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Votación Escolar")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        self.db_manager = DatabaseManager()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario principal"""
        # Título
        title_label = tk.Label(self.root, text="Sistema de Votación Escolar", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Botón para iniciar votación
        vote_button = tk.Button(self.root, text="Iniciar Votación", font=("Arial", 12), 
                               command=self.start_voting, bg="#4CAF50", fg="white", 
                               width=20, height=2)
        vote_button.pack(pady=10)
        
        # Botón para modo administración
        admin_button = tk.Button(self.root, text="Modo Administración", font=("Arial", 12),
                                command=self.start_admin, bg="#2196F3", fg="white",
                                width=20, height=2)
        admin_button.pack(pady=10)
        
        # Botón para salir
        exit_button = tk.Button(self.root, text="Salir", font=("Arial", 12),
                               command=self.root.quit, bg="#f44336", fg="white",
                               width=20, height=1)
        exit_button.pack(pady=10)
    
    def start_voting(self):
        """Inicia la aplicación de votación"""
        if self.db_manager.get_estado_votacion() != 'activa':
            messagebox.showwarning("Votación no activa", "La votación no está activa. Contacte al administrador.")
            return
        
        self.root.destroy()
        voting_app = VotingApp()
        voting_app.run()
    
    def start_admin(self):
        """Inicia la aplicación de administración"""
        self.root.destroy()
        admin_app = AdminApp()
        admin_app.run()
    
    def run(self):
        """Ejecuta la aplicación principal"""
        # Centrar la ventana
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
        self.root.mainloop()

if __name__ == "__main__":
    app = MainApp()
    app.run()
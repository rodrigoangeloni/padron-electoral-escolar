import tkinter as tk
from tkinter import messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from voting_app import VotingApp
from admin_app import AdminApp
from database import DatabaseManager
import config

class MainApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Sistema de Votación Escolar")
        self.geometry(config.MAIN_WINDOW_GEOMETRY)
        self.resizable(False, False)

        self.db_manager = DatabaseManager()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (MainMenu, AdminApp, VotingApp):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainMenu")
        self.center_window()

    def show_frame(self, page_name):
        '''Muestra un frame para la página dada'''
        frame = self.frames[page_name]
        frame.tkraise()
        
        if page_name == "MainMenu":
            self.geometry(config.MAIN_WINDOW_GEOMETRY)
            self.resizable(False, False)
        elif page_name == "VotingApp":
            self.geometry(config.VOTING_WINDOW_GEOMETRY)
            self.resizable(True, True)
        
        self.center_window()

    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def on_closing(self):
        """Maneja el evento de cierre de la ventana."""
        if messagebox.askokcancel("Salir", "¿Está seguro que desea salir?"):
            self.db_manager.close()
            self.quit() # Usar quit() para terminar el mainloop
            self.destroy() # Asegurarse de que la ventana se destruya

class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        title_label = tk.Label(self, text="Sistema de Votación Escolar", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        vote_button = tk.Button(self, text="Iniciar Votación", font=("Arial", 12), 
                               command=self.start_voting, bg=config.COLOR_SUCCESS, fg=config.COLOR_WHITE, 
                               width=20, height=2)
        vote_button.pack(pady=10)
        
        admin_button = tk.Button(self, text="Modo Administración", font=("Arial", 12),
                                command=lambda: controller.show_frame("AdminApp"), bg=config.COLOR_PRIMARY, fg=config.COLOR_WHITE,
                                width=20, height=2)
        admin_button.pack(pady=10)
        
        exit_button = tk.Button(self, text="Salir", font=("Arial", 12),
                               command=controller.on_closing, bg=config.COLOR_DANGER, fg=config.COLOR_WHITE,
                               width=20, height=1)
        exit_button.pack(pady=10)

    def start_voting(self):
        if self.controller.db_manager.get_estado_votacion() != config.VOTACION_ACTIVA:
            messagebox.showwarning("Votación no activa", "La votación no está activa. Contacte al administrador.")
            return
        self.controller.show_frame("VotingApp")


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
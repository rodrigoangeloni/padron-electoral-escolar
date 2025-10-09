"""
Módulo para la funcionalidad de UI de candidatos
"""
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import os
import shutil
from tkinter import filedialog
import config


class CandidateUI:
    def __init__(self, parent_frame, db_manager):
        self.parent_frame = parent_frame
        self.db_manager = db_manager
        self.nombre_entry = None
        self.apellido_entry = None
        self.cargo_var = None
        self.grado_var = None
        self.candidates_tree = None
        self.photo_preview = None
        self.update_photo_button = None

    def setup_candidates_tab(self):
        """Configura la pestaña de candidatos"""
        add_frame = tk.LabelFrame(self.parent_frame, text="Agregar Candidato", padx=10, pady=10)
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
        
        list_container = tk.Frame(self.parent_frame)
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
        """Maneja la selección de un candidato"""
        selected_item = self.candidates_tree.selection()
        if selected_item:
            self.update_photo_button.config(state="normal")
            # Obtener la ruta de la foto de la DB usando el ID del candidato
            candidato_id = self.candidates_tree.item(selected_item)['values'][0]
            candidato = self.db_manager.get_candidato_by_id(candidato_id)
            
            if candidato:
                photo_path = candidato[5] # foto está en la posición 5
            else:
                photo_path = config.DEFAULT_CANDIDATE_IMAGE
            
            try:
                img = Image.open(photo_path).resize((150, 150), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.photo_preview.config(image=photo, width=150, height=150)
                self.photo_preview.image = photo
            except (FileNotFoundError, OSError) as e:
                print(f"Error al cargar la imagen: {e}")
                self.photo_preview.config(image='', text="Sin imagen")
        else:
            self.update_photo_button.config(state="disabled")
            self.photo_preview.config(image='', text="")

    def update_candidate_photo(self):
        """Actualiza la foto de un candidato"""
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

    def add_candidate(self):
        """Agrega un nuevo candidato"""
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
        """Elimina un candidato seleccionado"""
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

    def refresh_candidates_list(self):
        """Actualiza la lista de candidatos"""
        for item in self.candidates_tree.get_children():
            self.candidates_tree.delete(item)
        candidatos = self.db_manager.get_candidatos()
        for candidato in candidatos:
            has_photo = "Sí" if candidato[5] and candidato[5] != config.DEFAULT_CANDIDATE_IMAGE else "No"
            values = (candidato[0], candidato[1], candidato[2], candidato[3], candidato[4], has_photo)
            self.candidates_tree.insert('', 'end', values=values)
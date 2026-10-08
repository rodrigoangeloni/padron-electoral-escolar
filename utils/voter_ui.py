"""
Módulo para la funcionalidad de UI de votantes
"""
import tkinter as tk
from tkinter import messagebox, ttk
import csv
from tkinter import filedialog
import config


class VoterUI:
    def __init__(self, parent_frame, db_manager):
        self.parent_frame = parent_frame
        self.db_manager = db_manager
        self.ci_voter_entry = None
        self.nombre_voter_entry = None
        self.apellido_voter_entry = None
        self.grado_curso_var = None
        self.voters_tree = None
        self.import_button = None

    def setup_voters_tab(self):
        """Configura la pestaña de votantes"""
        add_frame = tk.LabelFrame(self.parent_frame, text="Agregar Votante", padx=10, pady=10)
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
        
        import_frame = tk.LabelFrame(self.parent_frame, text="Importar Votantes desde Archivo", padx=10, pady=10)
        import_frame.pack(fill="x", padx=10, pady=10)
        
        import_desc = tk.Label(import_frame, text="Importar votantes desde archivo CSV (CI,Nombre,Apellido,Grado/Curso)")
        import_desc.pack(pady=5)
        
        self.import_button = tk.Button(import_frame, text="Seleccionar Archivo CSV", command=self.import_voters_from_file, bg=config.COLOR_WARNING, fg=config.COLOR_WHITE)
        self.import_button.pack(pady=5)
        
        list_frame = tk.LabelFrame(self.parent_frame, text="Votantes Registrados", padx=10, pady=10)
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

        edit_ci_button = tk.Button(buttons_frame, text="Editar CI Seleccionada", command=self.edit_voter_ci, bg=config.COLOR_WARNING, fg=config.COLOR_WHITE)
        edit_ci_button.pack(side="left", padx=5)
        
        refresh_voters_button = tk.Button(buttons_frame, text="Actualizar Lista", command=self.refresh_voters_list, bg=config.COLOR_PRIMARY, fg=config.COLOR_WHITE)
        refresh_voters_button.pack(side="left", padx=5)
        
        self.refresh_voters_list()

    def add_voter(self):
        """Agrega un nuevo votante"""
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
        """Elimina un votante seleccionado"""
        selected_item = self.voters_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un votante para eliminar")
            return
        ci = self.voters_tree.item(selected_item)['values'][1]
        if messagebox.askyesno("Confirmar", f"¿Está seguro que desea eliminar al votante con CI {ci}?"):
            self.db_manager.delete_votante(ci)
            self.refresh_voters_list()
            messagebox.showinfo("Éxito", "Votante eliminado correctamente")

    def edit_voter_ci(self):
        """Abre un diálogo para editar la CI del votante seleccionado"""
        selected_item = self.voters_tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un votante para editar su CI")
            return
        values = self.voters_tree.item(selected_item)['values']
        ci_actual, nombre, apellido = str(values[1]), values[2], values[3]

        dialog = tk.Toplevel(self.parent_frame)
        dialog.title("Editar CI")
        dialog.geometry("350x180")
        dialog.resizable(False, False)
        dialog.transient(self.parent_frame)
        dialog.grab_set()

        tk.Label(dialog, text=f"Votante: {nombre} {apellido}", font=("Arial", 10, "bold")).pack(pady=10)
        tk.Label(dialog, text=f"CI actual: {ci_actual}").pack()
        tk.Label(dialog, text="CI nueva:").pack(pady=(10, 0))
        nueva_entry = tk.Entry(dialog, width=20)
        nueva_entry.insert(0, ci_actual)
        nueva_entry.pack(pady=5)
        nueva_entry.focus()
        nueva_entry.select_range(0, tk.END)

        def guardar():
            ci_nueva = nueva_entry.get().strip()
            ok, mensaje = self.db_manager.update_votante_ci(ci_actual, ci_nueva)
            if ok:
                dialog.destroy()
                self.refresh_voters_list()
                messagebox.showinfo("Éxito", mensaje)
            else:
                messagebox.showerror("Error", mensaje)

        tk.Button(dialog, text="Guardar", command=guardar, bg=config.COLOR_SUCCESS, fg=config.COLOR_WHITE).pack(pady=10)
        nueva_entry.bind("<Return>", lambda event: guardar())

    def import_voters_from_file(self):
        """Importa votantes desde un archivo CSV"""
        file_path = filedialog.askopenfilename(title="Seleccionar archivo CSV", filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")])
        if not file_path:
            return

        # Suponiendo que el controller es accesible desde aquí, o se pasará como parámetro
        # self.controller.config(cursor="watch")
        self.import_button.config(state="disabled", text="Importando...")
        # self.controller.update_idletasks()

        try:
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
            # self.controller.config(cursor="")
            self.import_button.config(state="normal", text="Seleccionar Archivo CSV")

    def refresh_voters_list(self):
        """Actualiza la lista de votantes"""
        for item in self.voters_tree.get_children():
            self.voters_tree.delete(item)
        votantes = self.db_manager.get_votantes()
        for votante in votantes:
            ya_voto_text = "Sí" if votante[5] == 1 else "No"
            values = (votante[0], votante[1], votante[2], votante[3], votante[4], ya_voto_text)
            self.voters_tree.insert('', 'end', values=values)
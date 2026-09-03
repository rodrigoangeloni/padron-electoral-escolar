import sqlite3
import os
from config import DB_PATH, DEFAULT_CANDIDATE_IMAGE, VOTACION_CERRADA, GRADOS_CANDIDATOS
from utils.path_handler import get_images_dir
import random


class DatabaseManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        # Las FK están OFF por defecto en SQLite: activar por conexión
        # (no-op dentro de transacción, por eso va aquí, antes de init_db).
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self):
        """Inicializa las tablas y puebla con datos de prueba si está vacía."""
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS candidatos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                cargo TEXT NOT NULL,
                grado TEXT NOT NULL,
                foto TEXT DEFAULT '{DEFAULT_CANDIDATE_IMAGE}'
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS votantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ci TEXT NOT NULL UNIQUE,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                grado_curso TEXT NOT NULL,
                ya_voto BOOLEAN DEFAULT 0
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS votos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidato_id INTEGER NOT NULL,
                fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ci_votante TEXT NOT NULL,
                FOREIGN KEY (candidato_id) REFERENCES candidatos (id) ON DELETE CASCADE,
                FOREIGN KEY (ci_votante) REFERENCES votantes (ci) ON DELETE CASCADE
            )
        ''')
        
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS configuracion (
                id INTEGER PRIMARY KEY,
                estado_votacion TEXT DEFAULT '{VOTACION_CERRADA}',
                fecha_inicio TIMESTAMP,
                fecha_fin TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cargos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE
            )
        ''')

        self.cursor.execute('SELECT COUNT(*) FROM configuracion')
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute('INSERT INTO configuracion (id, estado_votacion) VALUES (1, ?)', (VOTACION_CERRADA,))
        
        self._seed_data()
        self.conn.commit()

    def _seed_data(self):
        """Puebla la tabla de cargos con valores iniciales si está vacía."""
        self.cursor.execute('SELECT COUNT(*) FROM cargos')
        if self.cursor.fetchone()[0] == 0:
            default_cargos = ["DIRECTORA", "VICEDIRECTORA", "COORDINADORA"]
            for cargo in default_cargos:
                try:
                    self.cursor.execute('INSERT INTO cargos (nombre) VALUES (?)', (cargo,))
                except sqlite3.IntegrityError:
                    pass
    
    # --- Gestión de Cargos ---
    def get_cargos(self):
        """Obtiene todos los cargos de la base de datos."""
        self.cursor.execute('SELECT nombre FROM cargos ORDER BY nombre')
        return [row[0] for row in self.cursor.fetchall()]

    def add_cargo(self, nombre_cargo):
        """Agrega un nuevo cargo a la base de datos."""
        try:
            self.cursor.execute('INSERT INTO cargos (nombre) VALUES (?)', (nombre_cargo,))
            self.conn.commit()
            return True, "Cargo agregado exitosamente."
        except sqlite3.IntegrityError:
            return False, f"El cargo '{nombre_cargo}' ya existe."

    def delete_cargo(self, nombre_cargo):
        """Elimina un cargo de la base de datos."""
        self.cursor.execute('SELECT COUNT(*) FROM candidatos WHERE cargo = ?', (nombre_cargo,))
        if self.cursor.fetchone()[0] > 0:
            return False, "No se puede eliminar el cargo porque está asignado a uno o más candidatos."
        
        self.cursor.execute('DELETE FROM cargos WHERE nombre = ?', (nombre_cargo,))
        self.conn.commit()
        return True, "Cargo eliminado exitosamente."
        
    def get_candidatos(self, cargo=None, grado=None):
        """
        Obtiene candidatos con filtros opcionales
        
        Args:
            cargo: Filtro por cargo (opcional)
            grado: Filtro por grado (opcional)
            
        Returns:
            list: Lista de tuplas (id, nombre, apellido, cargo, grado, foto)
        """
        if cargo and grado:
            self.cursor.execute('SELECT id, nombre, apellido, cargo, grado, foto FROM candidatos WHERE cargo = ? AND grado = ?', (cargo, grado))
        elif cargo:
            self.cursor.execute('SELECT id, nombre, apellido, cargo, grado, foto FROM candidatos WHERE cargo = ?', (cargo,))
        elif grado:
            self.cursor.execute('SELECT id, nombre, apellido, cargo, grado, foto FROM candidatos WHERE grado = ?', (grado,))
        else:
            self.cursor.execute('SELECT id, nombre, apellido, cargo, grado, foto FROM candidatos')
        return self.cursor.fetchall()

    def get_candidato_by_name(self, nombre, apellido):
        self.cursor.execute('SELECT * FROM candidatos WHERE nombre = ? AND apellido = ?', (nombre, apellido))
        return self.cursor.fetchone()
    
    def get_candidato_by_id(self, candidato_id):
        """
        Obtiene un candidato por su ID
        
        Args:
            candidato_id: ID del candidato a buscar
            
        Returns:
            tuple: (id, nombre, apellido, cargo, grado, foto) o None si no se encuentra
        """
        self.cursor.execute('SELECT id, nombre, apellido, cargo, grado, foto FROM candidatos WHERE id = ?', (candidato_id,))
        return self.cursor.fetchone()
    
    def add_candidato(self, nombre, apellido, cargo, grado, foto=DEFAULT_CANDIDATE_IMAGE):
        self.cursor.execute('INSERT INTO candidatos (nombre, apellido, cargo, grado, foto) VALUES (?, ?, ?, ?, ?)', (nombre, apellido, cargo, grado, foto))
        self.conn.commit()
    
    def delete_candidato(self, candidato_id):
        self.cursor.execute('DELETE FROM candidatos WHERE id = ?', (candidato_id,))
        self.conn.commit()

    def update_candidate_photo(self, candidato_id, photo_path):
        self.cursor.execute('UPDATE candidatos SET foto = ? WHERE id = ?', (photo_path, candidato_id))
        self.conn.commit()
    
    def add_votante(self, ci, nombre, apellido, grado_curso):
        try:
            self.cursor.execute('INSERT INTO votantes (ci, nombre, apellido, grado_curso, ya_voto) VALUES (?, ?, ?, ?, 0)', (ci, nombre, apellido, grado_curso))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_votante(self, ci):
        self.cursor.execute('SELECT id, ci, nombre, apellido, grado_curso, ya_voto FROM votantes WHERE ci = ?', (ci,))
        return self.cursor.fetchone()
    
    def add_voto(self, candidato_id, ci_votante):
        self.cursor.execute('SELECT ya_voto FROM votantes WHERE ci = ?', (ci_votante,))
        result = self.cursor.fetchone()
        
        if result is None:
            return False, "Votante no registrado"
        if result[0] == 1:
            return False, "El votante ya ha emitido su voto"
            
        self.cursor.execute('INSERT INTO votos (candidato_id, ci_votante) VALUES (?, ?)', (candidato_id, ci_votante))
        self.cursor.execute('UPDATE votantes SET ya_voto = 1 WHERE ci = ?', (ci_votante,))
        self.conn.commit()
        return True, "Voto registrado exitosamente"
    
    def add_multiple_votes(self, candidato_ids, ci_votante):
        """
        Registra múltiples votos para un votante y marca al votante como que ya votó
        solo después de registrar todos los votos.
        
        Args:
            candidato_ids: Lista de IDs de candidatos por los que votó el votante
            ci_votante: Cédula de identidad del votante
            
        Returns:
            bool: True si todos los votos se registraron exitosamente, False en caso contrario
        """
        # Verificar que el votante no haya votado aún
        self.cursor.execute('SELECT ya_voto FROM votantes WHERE ci = ?', (ci_votante,))
        result = self.cursor.fetchone()
        
        if result is None:
            return False, "Votante no registrado"
        if result[0] == 1:
            return False, "El votante ya ha emitido su voto"
        if not candidato_ids:
            return False, "Debe seleccionar al menos un candidato"
        
        # Registrar todos los votos en una transacción
        try:
            for candidato_id in candidato_ids:
                self.cursor.execute('INSERT INTO votos (candidato_id, ci_votante) VALUES (?, ?)', (candidato_id, ci_votante))
            
            # Marcar al votante como que ya votó solo después de registrar todos los votos
            self.cursor.execute('UPDATE votantes SET ya_voto = 1 WHERE ci = ?', (ci_votante,))
            self.conn.commit()
            return True, "Votos registrados exitosamente"
        except Exception as e:
            self.conn.rollback()
            return False, f"Error al registrar votos: {str(e)}"
    
    def cargos_sin_candidatos(self):
        """Devuelve los cargos configurados que no tienen candidatos.

        Returns:
            list: Nombres de cargos sin candidatos (vacía si la elección
                está lista para votar).
        """
        vacios = []
        for cargo in self.get_cargos():
            self.cursor.execute(
                'SELECT COUNT(*) FROM candidatos WHERE cargo = ?', (cargo,)
            )
            if self.cursor.fetchone()[0] == 0:
                vacios.append(cargo)
        return vacios

    def get_resultados(self):
        """Obtiene resultados con id de candidato para distinguir homónimos.

        Returns:
            tuple: (resultados, resultados_por_grado) donde cada fila de
                resultados es (id, nombre, apellido, cargo, grado, votos).
        """
        self.cursor.execute('''
            SELECT c.id, c.nombre, c.apellido, c.cargo, c.grado, COUNT(v.id) as votos
            FROM candidatos c
            LEFT JOIN votos v ON c.id = v.candidato_id
            GROUP BY c.id, c.nombre, c.apellido, c.cargo, c.grado
            ORDER BY c.cargo, c.grado, votos DESC
        ''')
        resultados = self.cursor.fetchall()
        
        self.cursor.execute('''
            SELECT v.grado_curso, c.nombre, c.apellido, c.cargo, COUNT(vot.id) as votos
            FROM votantes v
            JOIN votos vot ON v.ci = vot.ci_votante
            JOIN candidatos c ON vot.candidato_id = c.id
            GROUP BY v.grado_curso, c.id
            ORDER BY v.grado_curso, c.cargo, votos DESC
        ''')
        resultados_por_grado = self.cursor.fetchall()
        
        return resultados, resultados_por_grado

    def get_ganadores(self):
        """Calcula ganadores por cargo incluyendo empates.

        Returns:
            dict: {cargo: [{id, nombre, apellido, votos, foto}, ...]} con
                todos los candidatos que comparten el máximo de votos.
        """
        resultados, _ = self.get_resultados()
        por_cargo = {}
        for row in resultados:
            candidato_id, nombre, apellido, cargo, _, votos = row
            por_cargo.setdefault(cargo, []).append(
                {"id": candidato_id, "nombre": nombre,
                 "apellido": apellido, "votos": votos}
            )
        ganadores = {}
        for cargo, candidatos in por_cargo.items():
            max_votos = max(c["votos"] for c in candidatos)
            top = [c for c in candidatos if c["votos"] == max_votos]
            for c in top:
                candidato_obj = self.get_candidato_by_id(c["id"])
                c["foto"] = candidato_obj[5] if candidato_obj else None
            ganadores[cargo] = top
        return ganadores
    
    def get_estado_votacion(self):
        self.cursor.execute('SELECT estado_votacion FROM configuracion WHERE id = 1')
        return self.cursor.fetchone()[0]
    
    def set_estado_votacion(self, estado):
        self.cursor.execute('UPDATE configuracion SET estado_votacion = ? WHERE id = 1', (estado,))
        self.conn.commit()
    
    def reset_votos(self):
        self.cursor.execute('UPDATE votantes SET ya_voto = 0')
        self.cursor.execute('DELETE FROM votos')
        self.conn.commit()
    
    def get_votantes(self):
        """
        Obtiene todos los votantes registrados
        
        Returns:
            list: Lista de tuplas (id, ci, nombre, apellido, grado_curso, ya_voto)
        """
        self.cursor.execute('SELECT id, ci, nombre, apellido, grado_curso, ya_voto FROM votantes')
        return self.cursor.fetchall()
    
    def delete_votante(self, ci):
        self.cursor.execute('DELETE FROM votantes WHERE ci = ?', (ci,))
        self.conn.commit()
    
    def import_votantes_from_list(self, votantes_list):
        success_count = 0
        error_count = 0
        for ci, nombre, apellido, grado_curso in votantes_list:
            try:
                self.cursor.execute('INSERT INTO votantes (ci, nombre, apellido, grado_curso, ya_voto) VALUES (?, ?, ?, ?, 0)', (ci, nombre, apellido, grado_curso))
                success_count += 1
            except sqlite3.IntegrityError:
                error_count += 1
        self.conn.commit()
        return success_count, error_count

    def close(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()

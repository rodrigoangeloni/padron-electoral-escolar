import sqlite3
import os
from config import DB_PATH, DEFAULT_CANDIDATE_IMAGE, VOTACION_CERRADA, CARGOS, GRADOS_CANDIDATOS
import random

class DatabaseManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
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
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracion (
                id INTEGER PRIMARY KEY,
                estado_votacion TEXT DEFAULT '{VOTACION_CERRADA}',
                fecha_inicio TIMESTAMP,
                fecha_fin TIMESTAMP
            )
        ''')
        
        self.cursor.execute('SELECT COUNT(*) FROM configuracion')
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute('INSERT INTO configuracion (id, estado_votacion) VALUES (1, ?)', (VOTACION_CERRADA,))
        
        self._seed_data()
        self.conn.commit()

    def _seed_data(self):
        """Puebla la base de datos con candidatos de prueba si la tabla está vacía."""
        self.cursor.execute('SELECT COUNT(*) FROM candidatos')
        if self.cursor.fetchone()[0] == 0:
            nombres = ["Sofía", "Valentina", "Isabella", "Camila", "Mariana", "Luciana", "Daniela", "Valeria", "Renata", "Victoria", "Martina", "Emma", "Catalina", "Julieta", "Mía", "Antonella"]
            apellidos = ["González", "Rodríguez", "Gómez", "Fernández", "López", "Díaz", "Martínez", "Pérez", "García", "Sánchez", "Romero", "Torres", "Álvarez", "Ruiz", "Ramírez", "Flores"]
            
            candidatos_a_insertar = []
            for cargo in CARGOS:
                for i in range(8):
                    nombre = random.choice(nombres)
                    apellido = random.choice(apellidos)
                    grado = random.choice(GRADOS_CANDIDATOS)
                    candidatos_a_insertar.append((nombre, apellido, cargo, grado, DEFAULT_CANDIDATE_IMAGE))
            
            self.cursor.executemany('INSERT INTO candidatos (nombre, apellido, cargo, grado, foto) VALUES (?, ?, ?, ?, ?)', candidatos_a_insertar)

    def get_candidatos(self, cargo=None, grado=None):
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
    
    def get_resultados(self):
        self.cursor.execute('''
            SELECT c.nombre, c.apellido, c.cargo, c.grado, COUNT(v.id) as votos
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

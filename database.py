import sqlite3
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self, db_path='assets/db/election.db'):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidatos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                cargo TEXT NOT NULL,
                grado TEXT NOT NULL,
                foto TEXT DEFAULT 'assets/images/default_candidate.jpg'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS votantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ci TEXT NOT NULL UNIQUE,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                grado_curso TEXT NOT NULL,
                ya_voto BOOLEAN DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS votos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidato_id INTEGER NOT NULL,
                fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ci_votante TEXT NOT NULL,
                FOREIGN KEY (candidato_id) REFERENCES candidatos (id),
                FOREIGN KEY (ci_votante) REFERENCES votantes (ci)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracion (
                id INTEGER PRIMARY KEY,
                estado_votacion TEXT DEFAULT 'cerrada',
                fecha_inicio TIMESTAMP,
                fecha_fin TIMESTAMP
            )
        ''')
        
        cursor.execute('SELECT COUNT(*) FROM configuracion')
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO configuracion (id, estado_votacion) VALUES (1, \'cerrada\')')
        
        conn.commit()
        conn.close()
    
    def get_candidatos(self, cargo=None, grado=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if cargo and grado:
            cursor.execute('SELECT id, nombre, apellido, cargo, grado, foto FROM candidatos WHERE cargo = ? AND grado = ?', (cargo, grado))
        elif cargo:
            cursor.execute('SELECT id, nombre, apellido, cargo, grado, foto FROM candidatos WHERE cargo = ?', (cargo,))
        elif grado:
            cursor.execute('SELECT id, nombre, apellido, cargo, grado, foto FROM candidatos WHERE grado = ?', (grado,))
        else:
            cursor.execute('SELECT id, nombre, apellido, cargo, grado, foto FROM candidatos')
        candidatos = cursor.fetchall()
        conn.close()
        return candidatos

    def get_candidato_by_name(self, nombre, apellido):
        """Obtiene los datos de un candidato por su nombre y apellido."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM candidatos WHERE nombre = ? AND apellido = ?', (nombre, apellido))
        candidato = cursor.fetchone()
        conn.close()
        return candidato
    
    def add_candidato(self, nombre, apellido, cargo, grado, foto='assets/images/default_candidate.jpg'):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO candidatos (nombre, apellido, cargo, grado, foto) VALUES (?, ?, ?, ?, ?)', (nombre, apellido, cargo, grado, foto))
        conn.commit()
        conn.close()
    
    def delete_candidato(self, candidato_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM candidatos WHERE id = ?', (candidato_id,))
        conn.commit()
        conn.close()
    
    def add_votante(self, ci, nombre, apellido, grado_curso):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO votantes (ci, nombre, apellido, grado_curso, ya_voto) VALUES (?, ?, ?, ?, 0)', (ci, nombre, apellido, grado_curso))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False
    
    def get_votante(self, ci):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, ci, nombre, apellido, grado_curso, ya_voto FROM votantes WHERE ci = ?', (ci,))
        votante = cursor.fetchone()
        conn.close()
        return votante
    
    def add_voto(self, candidato_id, ci_votante):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT ya_voto FROM votantes WHERE ci = ?', (ci_votante,))
        result = cursor.fetchone()
        if result is None:
            conn.close()
            return False, "Votante no registrado"
        if result[0] == 1:
            conn.close()
            return False, "El votante ya ha emitido su voto"
        cursor.execute('INSERT INTO votos (candidato_id, ci_votante) VALUES (?, ?)', (candidato_id, ci_votante))
        cursor.execute('UPDATE votantes SET ya_voto = 1 WHERE ci = ?', (ci_votante,))
        conn.commit()
        conn.close()
        return True, "Voto registrado exitosamente"
    
    def get_resultados(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.nombre, c.apellido, c.cargo, c.grado, COUNT(v.id) as votos
            FROM candidatos c
            LEFT JOIN votos v ON c.id = v.candidato_id
            GROUP BY c.id, c.nombre, c.apellido, c.cargo, c.grado
            ORDER BY c.cargo, c.grado, votos DESC
        ''')
        resultados = cursor.fetchall()
        cursor.execute('''
            SELECT v.grado_curso, c.nombre, c.apellido, c.cargo, COUNT(vot.id) as votos
            FROM votantes v
            JOIN votos vot ON v.ci = vot.ci_votante
            JOIN candidatos c ON vot.candidato_id = c.id
            GROUP BY v.grado_curso, c.id
            ORDER BY v.grado_curso, c.cargo, votos DESC
        ''')
        resultados_por_grado = cursor.fetchall()
        conn.close()
        return resultados, resultados_por_grado
    
    def get_estado_votacion(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT estado_votacion FROM configuracion WHERE id = 1')
        estado = cursor.fetchone()[0]
        conn.close()
        return estado
    
    def set_estado_votacion(self, estado):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE configuracion SET estado_votacion = ? WHERE id = 1', (estado,))
        conn.commit()
        conn.close()
    
    def reset_votos(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE votantes SET ya_voto = 0')
        cursor.execute('DELETE FROM votos')
        conn.commit()
        conn.close()
    
    def get_votantes(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, ci, nombre, apellido, grado_curso, ya_voto FROM votantes')
        votantes = cursor.fetchall()
        conn.close()
        return votantes
    
    def delete_votante(self, ci):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM votantes WHERE ci = ?', (ci,))
        conn.commit()
        conn.close()
    
    def import_votantes_from_list(self, votantes_list):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        success_count = 0
        error_count = 0
        for ci, nombre, apellido, grado_curso in votantes_list:
            try:
                cursor.execute('INSERT INTO votantes (ci, nombre, apellido, grado_curso, ya_voto) VALUES (?, ?, ?, ?, 0)', (ci, nombre, apellido, grado_curso))
                success_count += 1
            except sqlite3.IntegrityError:
                error_count += 1
        conn.commit()
        conn.close()
        return success_count, error_count

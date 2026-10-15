import sqlite3
import os
from config import DB_PATH, DEFAULT_CANDIDATE_IMAGE, VOTACION_CERRADA, GRADOS_CANDIDATOS
from utils.path_handler import get_images_dir
from utils.turno_utils import parse_grado_turno, TURNOS_VALIDOS
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
                foto TEXT DEFAULT '{DEFAULT_CANDIDATE_IMAGE}',
                turno TEXT NOT NULL DEFAULT 'MAÑANA'
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS votantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ci TEXT NOT NULL UNIQUE,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                grado_curso TEXT NOT NULL,
                ya_voto BOOLEAN DEFAULT 0,
                turno TEXT NOT NULL DEFAULT 'MAÑANA'
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
                turno_activo TEXT DEFAULT 'MAÑANA',
                fecha_inicio TIMESTAMP,
                fecha_fin TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cargos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                orden INTEGER NOT NULL DEFAULT 0
            )
        ''')

        self.cursor.execute('SELECT COUNT(*) FROM configuracion')
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute('INSERT INTO configuracion (id, estado_votacion) VALUES (1, ?)', (VOTACION_CERRADA,))

        self._migrar_turno_votantes()
        self._migrar_turno_candidatos()
        self._migrar_orden_cargos()
        self._migrar_turno_activo()
        self._migrar_fotos_relativas()
        self._seed_data()
        self.conn.commit()

    def _migrar_turno_votantes(self):
        """Agrega la columna turno a DBs viejas y la rellena desde grado_curso.

        "1er Grado TM" -> turno MAÑANA + grado normalizado "1er Grado".
        Filas sin sufijo válido conservan el grado y quedan en MAÑANA
        (valor por defecto, sin destruir datos).
        """
        columnas = [fila[1] for fila in self.cursor.execute('PRAGMA table_info(votantes)')]
        if 'turno' in columnas:
            return
        self.cursor.execute("ALTER TABLE votantes ADD COLUMN turno TEXT NOT NULL DEFAULT 'MAÑANA'")
        filas = self.cursor.execute('SELECT id, grado_curso FROM votantes').fetchall()
        for vid, grado_curso in filas:
            try:
                grado, turno = parse_grado_turno(grado_curso)
            except ValueError:
                continue
            self.cursor.execute('UPDATE votantes SET grado_curso = ?, turno = ? WHERE id = ?', (grado, turno, vid))

    def _migrar_turno_candidatos(self):
        """Agrega la columna turno a DBs viejas.

        Los candidatos existentes no tienen turno registrado: quedan en
        MAÑANA (valor por defecto). Corregirlos manualmente si corresponde.
        """
        columnas = [fila[1] for fila in self.cursor.execute('PRAGMA table_info(candidatos)')]
        if 'turno' not in columnas:
            self.cursor.execute("ALTER TABLE candidatos ADD COLUMN turno TEXT NOT NULL DEFAULT 'MAÑANA'")

    def _migrar_orden_cargos(self):
        """Agrega la columna orden a DBs viejas.

        Los cargos existentes conservan su orden visual actual
        (alfabético): se numeran 0, 1, 2... por nombre.
        """
        columnas = [fila[1] for fila in self.cursor.execute('PRAGMA table_info(cargos)')]
        if 'orden' in columnas:
            return
        self.cursor.execute('ALTER TABLE cargos ADD COLUMN orden INTEGER NOT NULL DEFAULT 0')
        ids = [fila[0] for fila in
               self.cursor.execute('SELECT id FROM cargos ORDER BY nombre').fetchall()]
        for posicion, cid in enumerate(ids):
            self.cursor.execute('UPDATE cargos SET orden = ? WHERE id = ?', (posicion, cid))

    def _migrar_turno_activo(self):
        """Agrega la columna turno_activo a DBs viejas (default MAÑANA)."""
        columnas = [fila[1] for fila in self.cursor.execute('PRAGMA table_info(configuracion)')]
        if 'turno_activo' not in columnas:
            self.cursor.execute("ALTER TABLE configuracion ADD COLUMN turno_activo TEXT DEFAULT 'MAÑANA'")

    def _migrar_fotos_relativas(self):
        """Convierte rutas absolutas de fotos a solo-nombre (idempotente).

        Las rutas absolutas viejas se rompen al mover la app de carpeta;
        con solo el nombre, `resolver_ruta_foto()` reconstruye la ruta
        contra la carpeta de imágenes actual. Las filas con la imagen
        por defecto no se tocan.
        """
        defecto = os.path.basename(DEFAULT_CANDIDATE_IMAGE)
        for cid, foto in self.cursor.execute('SELECT id, foto FROM candidatos').fetchall():
            if not foto or os.path.basename(foto) == defecto:
                continue
            base = os.path.basename(foto)
            if base != foto:
                self.cursor.execute('UPDATE candidatos SET foto = ? WHERE id = ?', (base, cid))

    def _seed_data(self):
        """Puebla la tabla de cargos con valores iniciales si está vacía."""
        self.cursor.execute('SELECT COUNT(*) FROM cargos')
        if self.cursor.fetchone()[0] == 0:
            default_cargos = ["DIRECTORA", "VICEDIRECTORA", "COORDINADORA"]
            for posicion, cargo in enumerate(default_cargos):
                try:
                    self.cursor.execute('INSERT INTO cargos (nombre, orden) VALUES (?, ?)', (cargo, posicion))
                except sqlite3.IntegrityError:
                    pass

    # --- Gestión de Cargos ---
    def get_cargos(self):
        """Obtiene todos los cargos en el orden configurado por el admin."""
        self.cursor.execute('SELECT nombre FROM cargos ORDER BY orden, nombre')
        return [row[0] for row in self.cursor.fetchall()]

    def add_cargo(self, nombre_cargo):
        """Agrega un nuevo cargo a la base de datos (al final del orden)."""
        try:
            self.cursor.execute('SELECT COALESCE(MAX(orden), -1) + 1 FROM cargos')
            siguiente = self.cursor.fetchone()[0]
            self.cursor.execute('INSERT INTO cargos (nombre, orden) VALUES (?, ?)', (nombre_cargo, siguiente))
            self.conn.commit()
            return True, "Cargo agregado exitosamente."
        except sqlite3.IntegrityError:
            return False, f"El cargo '{nombre_cargo}' ya existe."

    def mover_cargo(self, nombre_cargo, direccion):
        """Sube (direccion=-1) o baja (direccion=+1) un cargo en el orden.

        Intercambia el valor de orden con el vecino. En los extremos
        no hace nada.

        Returns:
            tuple: (ok, mensaje).
        """
        cargos = self.get_cargos()
        if nombre_cargo not in cargos:
            return False, "Cargo no encontrado."
        i = cargos.index(nombre_cargo)
        j = i + direccion
        if j < 0 or j >= len(cargos):
            return False, f"'{nombre_cargo}' ya está al {'principio' if direccion < 0 else 'final'}."
        try:
            self.cursor.execute('SELECT id, orden FROM cargos WHERE nombre = ?', (nombre_cargo,))
            id_a, orden_a = self.cursor.fetchone()
            self.cursor.execute('SELECT id, orden FROM cargos WHERE nombre = ?', (cargos[j],))
            id_b, orden_b = self.cursor.fetchone()
            self.cursor.execute('UPDATE cargos SET orden = ? WHERE id = ?', (orden_b, id_a))
            self.cursor.execute('UPDATE cargos SET orden = ? WHERE id = ?', (orden_a, id_b))
            self.conn.commit()
            return True, "Orden actualizado."
        except Exception as e:
            self.conn.rollback()
            return False, f"Error al reordenar: {str(e)}"

    def delete_cargo(self, nombre_cargo):
        """Elimina un cargo de la base de datos."""
        self.cursor.execute('SELECT COUNT(*) FROM candidatos WHERE cargo = ?', (nombre_cargo,))
        if self.cursor.fetchone()[0] > 0:
            return False, "No se puede eliminar el cargo porque está asignado a uno o más candidatos."
        
        self.cursor.execute('DELETE FROM cargos WHERE nombre = ?', (nombre_cargo,))
        self.conn.commit()
        return True, "Cargo eliminado exitosamente."
        
    def get_candidatos(self, cargo=None, grado=None, turno=None):
        """
        Obtiene candidatos con filtros opcionales
        
        Args:
            cargo: Filtro por cargo (opcional)
            grado: Filtro por grado (opcional)
            turno: Filtro por turno 'MAÑANA'/'TARDE' (opcional)
            
        Returns:
            list: Lista de tuplas (id, nombre, apellido, cargo, grado, foto, turno)
        """
        condiciones = []
        parametros = []
        if cargo:
            condiciones.append('cargo = ?')
            parametros.append(cargo)
        if grado:
            condiciones.append('grado = ?')
            parametros.append(grado)
        if turno:
            condiciones.append('turno = ?')
            parametros.append(turno)
        sql = 'SELECT id, nombre, apellido, cargo, grado, foto, turno FROM candidatos'
        if condiciones:
            sql += ' WHERE ' + ' AND '.join(condiciones)
        self.cursor.execute(sql, parametros)
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
            tuple: (id, nombre, apellido, cargo, grado, foto, turno) o None si no se encuentra
        """
        self.cursor.execute('SELECT id, nombre, apellido, cargo, grado, foto, turno FROM candidatos WHERE id = ?', (candidato_id,))
        return self.cursor.fetchone()
    
    def add_candidato(self, nombre, apellido, cargo, grado, foto=DEFAULT_CANDIDATE_IMAGE, turno='MAÑANA'):
        if turno not in TURNOS_VALIDOS:
            raise ValueError(f"Turno inválido: '{turno}' (use MAÑANA o TARDE).")
        self.cursor.execute('INSERT INTO candidatos (nombre, apellido, cargo, grado, foto, turno) VALUES (?, ?, ?, ?, ?, ?)', (nombre, apellido, cargo, grado, foto, turno))
        self.conn.commit()
    
    def delete_candidato(self, candidato_id):
        self.cursor.execute('DELETE FROM candidatos WHERE id = ?', (candidato_id,))
        self.conn.commit()

    def update_candidate_photo(self, candidato_id, photo_path):
        """Guarda solo el nombre del archivo (portable al mover la app)."""
        self.cursor.execute('UPDATE candidatos SET foto = ? WHERE id = ?',
                            (os.path.basename(photo_path), candidato_id))
        self.conn.commit()

    def update_candidate_cargo(self, candidato_id, nuevo_cargo):
        """Cambia el cargo de un candidato. Lanza ValueError si el cargo no existe."""
        if nuevo_cargo not in self.get_cargos():
            raise ValueError(f"Cargo inexistente: '{nuevo_cargo}'.")
        self.cursor.execute('UPDATE candidatos SET cargo = ? WHERE id = ?', (nuevo_cargo, candidato_id))
        self.conn.commit()

    def get_votos_candidato(self, candidato_id):
        """Devuelve la cantidad de votos que tiene un candidato."""
        self.cursor.execute('SELECT COUNT(*) FROM votos WHERE candidato_id = ?', (candidato_id,))
        return self.cursor.fetchone()[0]
    
    def add_votante(self, ci, nombre, apellido, grado_curso, turno='MAÑANA'):
        if turno not in TURNOS_VALIDOS:
            return False
        try:
            self.cursor.execute('INSERT INTO votantes (ci, nombre, apellido, grado_curso, ya_voto, turno) VALUES (?, ?, ?, ?, 0, ?)', (ci, nombre, apellido, grado_curso, turno))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_votante(self, ci):
        self.cursor.execute('SELECT id, ci, nombre, apellido, grado_curso, ya_voto, turno FROM votantes WHERE ci = ?', (ci,))
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
    
    def cargos_sin_candidatos(self, turno=None):
        """Devuelve los cargos configurados que no tienen candidatos.

        Args:
            turno: si se indica ('MAÑANA'/'TARDE'), solo cuenta los
                candidatos de ese turno (cada turno es una elección).

        Returns:
            list: Nombres de cargos sin candidatos (vacía si la elección
                está lista para votar).
        """
        vacios = []
        for cargo in self.get_cargos():
            if turno:
                self.cursor.execute(
                    'SELECT COUNT(*) FROM candidatos WHERE cargo = ? AND turno = ?',
                    (cargo, turno)
                )
            else:
                self.cursor.execute(
                    'SELECT COUNT(*) FROM candidatos WHERE cargo = ?', (cargo,)
                )
            if self.cursor.fetchone()[0] == 0:
                vacios.append(cargo)
        return vacios

    def get_resultados(self, turno=None):
        """Obtiene resultados con id y foto para distinguir homónimos sin N+1.

        Args:
            turno: si se indica ('MAÑANA'/'TARDE'), solo la elección de
                ese turno.

        Returns:
            tuple: (resultados, resultados_por_grado) donde cada fila de
                resultados es
                (id, nombre, apellido, cargo, grado, votos, foto, turno).
        """
        filtro = 'WHERE c.turno = ?' if turno else ''
        params = (turno,) if turno else ()
        self.cursor.execute(f'''
            SELECT c.id, c.nombre, c.apellido, c.cargo, c.grado, COUNT(v.id) as votos, c.foto, c.turno
            FROM candidatos c
            LEFT JOIN votos v ON c.id = v.candidato_id
            {filtro}
            GROUP BY c.id, c.nombre, c.apellido, c.cargo, c.grado
            ORDER BY c.cargo, c.grado, votos DESC
        ''', params)
        resultados = self.cursor.fetchall()

        self.cursor.execute(f'''
            SELECT v.grado_curso, c.nombre, c.apellido, c.cargo, COUNT(vot.id) as votos
            FROM votantes v
            JOIN votos vot ON v.ci = vot.ci_votante
            JOIN candidatos c ON vot.candidato_id = c.id
            {filtro}
            GROUP BY v.grado_curso, c.id
            ORDER BY v.grado_curso, c.cargo, votos DESC
        ''', params)
        resultados_por_grado = self.cursor.fetchall()

        return resultados, resultados_por_grado

    def get_ganadores(self, turno=None):
        """Calcula ganadores por cargo incluyendo empates.

        Args:
            turno: si se indica, solo la elección de ese turno.

        Returns:
            dict: {cargo: [{id, nombre, apellido, votos, foto}, ...]} con
                todos los candidatos que comparten el máximo de votos.
        """
        resultados, _ = self.get_resultados(turno)
        por_cargo = {}
        for row in resultados:
            candidato_id, nombre, apellido, cargo, _, votos, foto, _turno = row
            por_cargo.setdefault(cargo, []).append(
                {"id": candidato_id, "nombre": nombre,
                 "apellido": apellido, "votos": votos, "foto": foto}
            )
        ganadores = {}
        for cargo, candidatos in por_cargo.items():
            max_votos = max(c["votos"] for c in candidatos)
            ganadores[cargo] = [c for c in candidatos if c["votos"] == max_votos]
        return ganadores

    def get_participacion(self, turno=None):
        """Devuelve (habilitados, votaron) del padrón, opcionalmente por turno."""
        if turno:
            self.cursor.execute(
                'SELECT COUNT(*), COALESCE(SUM(ya_voto), 0) FROM votantes WHERE turno = ?',
                (turno,))
        else:
            self.cursor.execute('SELECT COUNT(*), COALESCE(SUM(ya_voto), 0) FROM votantes')
        habilitados, votaron = self.cursor.fetchone()
        return habilitados, votaron
    
    def get_estado_votacion(self):
        self.cursor.execute('SELECT estado_votacion FROM configuracion WHERE id = 1')
        return self.cursor.fetchone()[0]
    
    def set_estado_votacion(self, estado):
        self.cursor.execute('UPDATE configuracion SET estado_votacion = ? WHERE id = 1', (estado,))
        self.conn.commit()

    def get_turno_activo(self):
        """Devuelve el turno activo ('MAÑANA'/'TARDE') para la votación."""
        self.cursor.execute('SELECT turno_activo FROM configuracion WHERE id = 1')
        fila = self.cursor.fetchone()
        return (fila[0] if fila and fila[0] else 'MAÑANA')

    def set_turno_activo(self, turno):
        """Guarda el turno activo. Lanza ValueError si el turno es inválido."""
        if turno not in TURNOS_VALIDOS:
            raise ValueError(f"Turno inválido: '{turno}' (use MAÑANA o TARDE).")
        self.cursor.execute('UPDATE configuracion SET turno_activo = ? WHERE id = 1', (turno,))
        self.conn.commit()
    
    def reset_votos(self):
        self.cursor.execute('UPDATE votantes SET ya_voto = 0')
        self.cursor.execute('DELETE FROM votos')
        self.conn.commit()
    
    def get_votantes(self):
        """
        Obtiene todos los votantes registrados
        
        Returns:
            list: Lista de tuplas (id, ci, nombre, apellido, grado_curso, ya_voto, turno)
        """
        self.cursor.execute('SELECT id, ci, nombre, apellido, grado_curso, ya_voto, turno FROM votantes')
        return self.cursor.fetchall()
    
    def delete_votante(self, ci):
        self.cursor.execute('DELETE FROM votantes WHERE ci = ?', (ci,))
        self.conn.commit()

    def update_votante_ci(self, ci_actual, ci_nueva):
        """Actualiza la CI de un votante y reasigna sus votos a la nueva CI.

        La FK votos.ci_votante no tiene ON UPDATE CASCADE, así que no se puede
        hacer UPDATE directo: se inserta la fila con la CI nueva (copiando
        nombre, apellido, grado y ya_voto), se mueven los votos y se borra la
        fila vieja. Todo en una transacción: si algo falla, no cambia nada.

        Returns:
            tuple: (ok, mensaje).
        """
        if not ci_nueva or not ci_nueva.isdigit() or not (7 <= len(ci_nueva) <= 8):
            return False, "La CI debe tener entre 7 y 8 dígitos numéricos."
        if ci_actual == ci_nueva:
            return True, "Sin cambios."
        self.cursor.execute(
            'SELECT nombre, apellido, grado_curso, ya_voto, turno FROM votantes WHERE ci = ?',
            (ci_actual,))
        fila = self.cursor.fetchone()
        if fila is None:
            return False, "Votante no encontrado."
        self.cursor.execute('SELECT id FROM votantes WHERE ci = ?', (ci_nueva,))
        if self.cursor.fetchone() is not None:
            return False, "La CI nueva ya está registrada en otro votante."
        try:
            self.cursor.execute(
                'INSERT INTO votantes (ci, nombre, apellido, grado_curso, ya_voto, turno) VALUES (?, ?, ?, ?, ?, ?)',
                (ci_nueva, fila[0], fila[1], fila[2], fila[3], fila[4]))
            self.cursor.execute('UPDATE votos SET ci_votante = ? WHERE ci_votante = ?', (ci_nueva, ci_actual))
            self.cursor.execute('DELETE FROM votantes WHERE ci = ?', (ci_actual,))
            self.conn.commit()
            return True, "CI actualizada correctamente."
        except Exception as e:
            self.conn.rollback()
            return False, f"Error al actualizar la CI: {str(e)}"
    
    def import_votantes_from_list(self, votantes_list):
        success_count = 0
        error_count = 0
        for ci, nombre, apellido, grado_curso, turno in votantes_list:
            if turno not in TURNOS_VALIDOS:
                error_count += 1
                continue
            try:
                self.cursor.execute('INSERT INTO votantes (ci, nombre, apellido, grado_curso, ya_voto, turno) VALUES (?, ?, ?, ?, 0, ?)', (ci, nombre, apellido, grado_curso, turno))
                success_count += 1
            except sqlite3.IntegrityError:
                error_count += 1
        self.conn.commit()
        return success_count, error_count

    def close(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()

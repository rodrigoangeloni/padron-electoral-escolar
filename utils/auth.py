import hashlib
import hmac
import os
import secrets
import string
import time
import config

# Iteraciones PBKDF2 (solo stdlib, sin deps nuevas).
_ITERACIONES_PBKDF2 = 200_000
_SALT_BYTES = 16


class AuthManager:
    def __init__(self, password_file=None, initial_flag_file=None,
                 max_intentos=5, bloqueo_segundos=30):
        if password_file is None:
            password_file = os.path.join(config.CONFIG_DIR, '.admin_password')
        if initial_flag_file is None:
            initial_flag_file = os.path.join(config.CONFIG_DIR, '.initial_password_used')

        self.password_file = password_file
        self.initial_flag_file = initial_flag_file
        self.max_intentos = max_intentos
        self.bloqueo_segundos = bloqueo_segundos
        self._fallos_consecutivos = 0
        self._bloqueado_hasta = 0.0
        # Crear directorios si no existen
        os.makedirs(os.path.dirname(password_file), exist_ok=True)
        os.makedirs(os.path.dirname(initial_flag_file), exist_ok=True)

    def generate_initial_password(self):
        """Genera una contraseña inicial segura"""
        initial_password = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(12))
        return initial_password

    def _generar_hash(self, password):
        """Genera hash PBKDF2 con salt aleatorio: 'salt_hex$hash_hex'."""
        salt = secrets.token_bytes(_SALT_BYTES)
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), salt, _ITERACIONES_PBKDF2
        )
        return f"{salt.hex()}${digest.hex()}"

    def _verificar_hash(self, password, stored):
        """Verifica contra formato nuevo (salt$hash) o legacy (sha256 plano)."""
        if "$" in stored:
            try:
                salt_hex, hash_hex = stored.split("$", 1)
                digest = hashlib.pbkdf2_hmac(
                    "sha256", password.encode(),
                    bytes.fromhex(salt_hex), _ITERACIONES_PBKDF2,
                )
                return hmac.compare_digest(digest.hex(), hash_hex)
            except (ValueError, TypeError):
                return False
        # Formato legacy: SHA-256 plano (migración: verifica hasta el cambio).
        return hmac.compare_digest(
            hashlib.sha256(password.encode()).hexdigest(), stored
        )

    def _guardar_hash(self, password):
        """Guarda el hash con permisos restringidos al propietario."""
        with open(self.password_file, 'w') as f:
            f.write(self._generar_hash(password))
        try:
            os.chmod(self.password_file, 0o600)
        except OSError:
            pass  # Windows no aplica permisos POSIX; se ignora.

    def set_initial_password(self, password):
        """Establece la contraseña inicial de administrador"""
        self._guardar_hash(password)
        # Marcar que se está usando la contraseña inicial
        self.mark_initial_password_used(True)

    def set_admin_password(self, password):
        """Establece la contraseña de administrador (después de la inicial)"""
        self._guardar_hash(password)
        # Marcar que ya no se está usando la contraseña inicial
        self.mark_initial_password_used(False)

    def mark_initial_password_used(self, is_initial=True):
        """Marca si se está usando la contraseña inicial"""
        with open(self.initial_flag_file, 'w') as f:
            f.write('true' if is_initial else 'false')

    def is_initial_password_used(self):
        """Verifica si aún se está usando la contraseña inicial"""
        if not os.path.exists(self.initial_flag_file):
            # Si no existe el archivo de bandera, asumimos que se está usando la inicial
            return True
        with open(self.initial_flag_file, 'r') as f:
            content = f.read().strip()
            return content == 'true'

    def esta_bloqueado(self):
        """Indica si el login está bloqueado por exceso de intentos fallidos."""
        return time.monotonic() < self._bloqueado_hasta

    def registrar_intento_fallido(self):
        """Registra un fallo y bloquea al alcanzar el máximo permitido."""
        self._fallos_consecutivos += 1
        if self._fallos_consecutivos >= self.max_intentos:
            self._bloqueado_hasta = time.monotonic() + self.bloqueo_segundos

    def reiniciar_intentos(self):
        """Reinicia el contador de fallos (tras un login exitoso)."""
        self._fallos_consecutivos = 0
        self._bloqueado_hasta = 0.0

    def verify_admin_password(self, password):
        """Verifica la contraseña de administrador"""
        if self.esta_bloqueado():
            return False
        if not os.path.exists(self.password_file):
            # Sin archivo no hay fallback: el admin debe crear la inicial.
            return False

        with open(self.password_file, 'r') as f:
            stored_hash = f.read().strip()

        if self._verificar_hash(password, stored_hash):
            self.reiniciar_intentos()
            return True
        self.registrar_intento_fallido()
        return False

    def change_admin_password(self, old_password, new_password):
        """Cambia la contraseña de administrador"""
        if self.verify_admin_password(old_password):
            self.set_admin_password(new_password)
            return True
        return False

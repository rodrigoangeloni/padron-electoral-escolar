import hashlib
import os
import secrets
import string
import sys
import config

class AuthManager:
    def __init__(self, password_file=None, initial_flag_file=None):
        if password_file is None:
            password_file = os.path.join(config.CONFIG_DIR, '.admin_password')
        if initial_flag_file is None:
            initial_flag_file = os.path.join(config.CONFIG_DIR, '.initial_password_used')
        
        self.password_file = password_file
        self.initial_flag_file = initial_flag_file
        # Crear directorios si no existen
        os.makedirs(os.path.dirname(password_file), exist_ok=True)
        os.makedirs(os.path.dirname(initial_flag_file), exist_ok=True)
    
    def generate_initial_password(self):
        """Genera una contraseña inicial segura"""
        initial_password = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(12))
        return initial_password
    
    def set_initial_password(self, password):
        """Establece la contraseña inicial de administrador"""
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        with open(self.password_file, 'w') as f:
            f.write(hashed_password)
        # Marcar que se está usando la contraseña inicial
        self.mark_initial_password_used(True)
    
    def set_admin_password(self, password):
        """Establece la contraseña de administrador (después de la inicial)"""
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        with open(self.password_file, 'w') as f:
            f.write(hashed_password)
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
    
    def verify_admin_password(self, password):
        """Verifica la contraseña de administrador"""
        if not os.path.exists(self.password_file):
            # Si no hay archivo de contraseña, se asume que es la contraseña por defecto
            # En una implementación real, se debería forzar a establecer una contraseña
            return password == "admin123"  # Contraseña por defecto temporal
        
        with open(self.password_file, 'r') as f:
            stored_hash = f.read().strip()
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return password_hash == stored_hash

    def is_using_initial_password(self, password):
        """Verifica si la contraseña proporcionada es la contraseña inicial"""
        # Para verificar si es la contraseña inicial, necesitamos generarla y compararla
        # con la contraseña proporcionada
        if self.is_initial_password_used() and not os.path.exists(self.initial_flag_file):
            # Si no hay archivo de bandera, asumimos que la contraseña actual es la inicial
            # y que aún no ha sido cambiada
            initial_password = self.generate_initial_password()
            initial_hash = hashlib.sha256(initial_password.encode()).hexdigest()
            provided_hash = hashlib.sha256(password.encode()).hexdigest()
            return initial_hash == provided_hash
        return False
    
    def change_admin_password(self, old_password, new_password):
        """Cambia la contraseña de administrador"""
        if self.verify_admin_password(old_password):
            self.set_admin_password(new_password)
            return True
        return False
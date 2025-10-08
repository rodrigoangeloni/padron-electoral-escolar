import hashlib
import os

class AuthManager:
    def __init__(self, password_file='assets/config/.admin_password'):
        self.password_file = password_file
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(password_file), exist_ok=True)
    
    def set_admin_password(self, password):
        """Establece la contraseña de administrador"""
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        with open(self.password_file, 'w') as f:
            f.write(hashed_password)
    
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
    
    def change_admin_password(self, old_password, new_password):
        """Cambia la contraseña de administrador"""
        if self.verify_admin_password(old_password):
            self.set_admin_password(new_password)
            return True
        return False
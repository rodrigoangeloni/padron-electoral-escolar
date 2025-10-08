import subprocess
import sys
import os

def run_application():
    """Ejecuta la aplicación usando el entorno virtual si existe"""
    
    # Determinar el comando python según el sistema operativo
    if os.name == 'nt':  # Windows
        python_cmd = ".venv\\Scripts\\python"
    else:  # macOS y Linux
        python_cmd = ".venv/bin/python"
    
    # Verificar si existe el entorno virtual
    venv_exists = os.path.exists('.venv')
    
    if venv_exists:
        print("Usando entorno virtual para ejecutar la aplicación...")
        # Ejecutar la aplicación con el entorno virtual
        result = subprocess.run([python_cmd, "main.py"])
    else:
        print("No se encontró entorno virtual, usando Python del sistema...")
        # Ejecutar la aplicación con Python del sistema
        result = subprocess.run([sys.executable, "main.py"])
    
    return result.returncode

if __name__ == "__main__":
    exit_code = run_application()
    sys.exit(exit_code)
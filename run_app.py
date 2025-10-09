import subprocess
import sys
import os

def run_application():
    """Ejecuta la aplicación usando el entorno virtual si existe, 
    de lo contrario crea el entorno virtual, lo activa e instala los requirements"""
    
    # Determinar el comando python según el sistema operativo
    if os.name == 'nt':  # Windows
        python_cmd = ".venv\\Scripts\\python"
        venv_python = ".venv\\Scripts\\python.exe"
    else:  # macOS y Linux
        python_cmd = ".venv/bin/python"
        venv_python = ".venv/bin/python"
    
    # Verificar si existe el entorno virtual
    venv_exists = os.path.exists('.venv')
    
    if venv_exists:
        print("Usando entorno virtual para ejecutar la aplicación...")
        # Ejecutar la aplicación con el entorno virtual
        result = subprocess.run([python_cmd, "main.py"])
    else:
        print("No se encontró entorno virtual, creando uno nuevo...")
        # Crear entorno virtual
        subprocess.run([sys.executable, "-m", "venv", ".venv"])
        
        # Instalar requirements.txt en el entorno virtual
        print("Instalando dependencias desde requirements.txt...")
        subprocess.run([venv_python, "-m", "pip", "install", "-r", "requirements.txt"])
        
        print("Ejecutando la aplicación con el entorno virtual recién creado...")
        # Ejecutar la aplicación con el entorno virtual recién creado
        result = subprocess.run([python_cmd, "main.py"])
    
    return result.returncode

if __name__ == "__main__":
    exit_code = run_application()
    sys.exit(exit_code)
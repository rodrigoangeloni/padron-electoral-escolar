"""
Módulo para manejar rutas de archivos correctamente en versiones compiladas
"""
import os
import sys


def get_resource_path(relative_path):
    """
    Obtiene la ruta absoluta a un recurso, funciona tanto en modo desarrollo como compilado
    """
    try:
        # PyInstaller crea un directorio temporal y almacena la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
        # Subir un nivel para llegar a la raíz del proyecto
        base_path = os.path.dirname(base_path)
    
    return os.path.join(base_path, relative_path)


def get_data_dir():
    """
    Obtiene el directorio donde se deben almacenar los datos persistentes
    """
    if getattr(sys, 'frozen', False):
        # Si está compilado, usar directorio del ejecutable
        data_dir = os.path.dirname(sys.executable)
    else:
        # Si está en modo desarrollo, usar directorio assets
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')
    
    # Asegurarse de que el directorio exista
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def get_db_path():
    """
    Obtiene la ruta al archivo de base de datos
    """
    data_dir = get_data_dir()
    db_dir = os.path.join(data_dir, 'db')
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, 'election.db')


def get_config_dir():
    """
    Obtiene el directorio de configuración
    """
    data_dir = get_data_dir()
    config_dir = os.path.join(data_dir, 'config')
    os.makedirs(config_dir, exist_ok=True)
    return config_dir


def get_images_dir():
    """
    Obtiene el directorio de imágenes
    """
    data_dir = get_data_dir()
    images_dir = os.path.join(data_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)
    return images_dir
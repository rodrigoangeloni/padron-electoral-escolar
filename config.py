"""
Módulo de Configuración Central

Este archivo centraliza todas las constantes y parámetros de configuración
de la aplicación para facilitar su mantenimiento y modificación.
"""

import os
from utils.path_handler import get_db_path, get_config_dir, get_images_dir

# --- Rutas del Proyecto ---
DB_PATH = get_db_path()
CONFIG_DIR = get_config_dir()
IMG_DIR = get_images_dir()
ASSETS_DIR = os.path.dirname(CONFIG_DIR)
DB_DIR = os.path.join(ASSETS_DIR, 'db')

# --- Autenticación ---
ADMIN_PASSWORD_FILE = os.path.join(CONFIG_DIR, '.admin_password')
# DEFAULT_ADMIN_PASSWORD = "admin123" # Eliminado por razones de seguridad

# --- Candidatos ---
DEFAULT_CANDIDATE_IMAGE = os.path.join(IMG_DIR, 'default_candidate.jpg')

GRADOS_CANDIDATOS = [
    "Jardín", "Pre Escolar", "1er Grado", "2do Grado", "3er Grado", "4to Grado",
    "5to Grado", "6to Grado", "7mo Grado", "8vo Grado", "9no Grado",
    "1er Curso", "2do Curso", "3er Curso"
]

# --- Votantes ---
GRADOS_VOTANTES = [
    "Jardín", "Pre Escolar", "1er Grado", "2do Grado", "3er Grado", "4to Grado",
    "5to Grado", "6to Grado", "7mo Grado", "8vo Grado", "9no Grado",
    "1er Curso", "2do Curso", "3er Curso"
]

# --- Estados de la Aplicación ---
VOTACION_ACTIVA = 'activa'
VOTACION_CERRADA = 'cerrada'

# --- Aplicación ---
APP_VERSION = "1.6.1"
DESARROLLADOR = "Rodrigo Angeloni"

# --- Interfaz Gráfica ---
# Dimensiones de la ventana principal
MAIN_WINDOW_GEOMETRY = "400x300"
VOTING_WINDOW_GEOMETRY = "1200x680"

# Dimensiones del panel de administración
ADMIN_WINDOW_GEOMETRY = "1200x680"

# Colores (ejemplos, se pueden ampliar)
COLOR_PRIMARY = "#2196F3"
COLOR_SUCCESS = "#4CAF50"
COLOR_WARNING = "#FF9800"
COLOR_DANGER = "#f44336"
COLOR_WHITE = "white"
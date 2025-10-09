"""
Módulo de Configuración Central

Este archivo centraliza todas las constantes y parámetros de configuración
de la aplicación para facilitar su mantenimiento y modificación.
"""

import os

# --- Rutas del Proyecto ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
DB_DIR = os.path.join(ASSETS_DIR, 'db')
IMG_DIR = os.path.join(ASSETS_DIR, 'images')
CONFIG_DIR = os.path.join(ASSETS_DIR, 'config')

# --- Base de Datos ---
DB_PATH = os.path.join(DB_DIR, 'election.db')

# --- Autenticación ---
ADMIN_PASSWORD_FILE = os.path.join(CONFIG_DIR, '.admin_password')
# DEFAULT_ADMIN_PASSWORD = "admin123" # Eliminado por razones de seguridad

# --- Candidatos ---
DEFAULT_CANDIDATE_IMAGE = os.path.join(IMG_DIR, 'default_candidate.jpg')

CARGOS = [
    "DIRECTORA",
    "VICEDIRECTORA",
    "COORDINADORA"
]

GRADOS_CANDIDATOS = [
    "Pre Escolar", "1er Grado", "2do Grado", "3er Grado", "4to Grado",
    "5to Grado", "6to Grado", "7mo Grado", "8vo Grado", "9no Grado",
    "1er Curso", "2do Curso", "3er Curso"
]

# --- Votantes ---
GRADOS_VOTANTES = [
    "Pre Escolar", "1er Grado", "2do Grado", "3er Grado", "4to Grado",
    "5to Grado", "6to Grado", "7mo Grado", "8vo Grado", "9no Grado",
    "1er Curso", "2do Curso", "3er Curso"
]

# --- Estados de la Aplicación ---
VOTACION_ACTIVA = 'activa'
VOTACION_CERRADA = 'cerrada'

# --- Interfaz Gráfica ---
# Dimensiones de la ventana principal
MAIN_WINDOW_GEOMETRY = "400x300"

# Dimensiones del panel de administración
ADMIN_WINDOW_GEOMETRY = "1200x700"

# Colores (ejemplos, se pueden ampliar)
COLOR_PRIMARY = "#2196F3"
COLOR_SUCCESS = "#4CAF50"
COLOR_WARNING = "#FF9800"
COLOR_DANGER = "#f44336"
COLOR_WHITE = "white"
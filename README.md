# Sistema de Votación Escolar

Aplicación de escritorio para gestionar elecciones estudiantiles, permitiendo a los estudiantes votar por sus representantes para los cargos de Directora, Vice Directora y Coordinadora.

## Tecnologías Utilizadas

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/Tkinter-2C5E8B?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557c?style=for-the-badge&logo=matplotlib&logoColor=white)

---

## Tabla de Contenidos
1. [Descripción General](#descripción-general)
2. [Arquitectura del Proyecto](#arquitectura-del-proyecto)
3. [Instalación y Uso](#instalación-y-uso)
4. [Módulos del Sistema](#módulos-del-sistema)
5. [Flujo de la Aplicación](#flujo-de-la-aplicación)
6. [Funcionalidades Principales](#funcionalidades-principales)
7. [Desarrollo y Contribución](#desarrollo-y-contribución)

## Descripción General

El Sistema de Votación Escolar es una aplicación de escritorio desarrollada en Python con Tkinter que facilita elecciones escolares. La aplicación permite la gestión completa del proceso electoral, desde la inscripción de candidatos y votantes hasta la emisión y conteo de votos en tiempo real.

### Características Principales
- **Interfaz Unificada:** La aplicación se ejecuta en una única ventana con una navegación fluida entre el menú principal, el panel de administración y la interfaz de votación.
- **Arquitectura Moderna:** Sigue un patrón de controlador principal que mejora la eficiencia y la mantenibilidad.
- **Gestión de Datos Optimizada:** Utiliza una base de datos SQLite con una conexión única y persistente para un rendimiento superior.
- **Panel de Administración Avanzado:**
    - Gestión de candidatos con **actualización de fotos individual** y **vista previa**.
    - Gestión de votantes con importación masiva desde CSV.
    - Configuración de la elección (activar/cerrar votación, cambio de contraseña).
- **Votación Adaptable y Segura:**
    - Autenticación de votantes por Cédula de Identidad (CI) y prevención de votos duplicados.
    - **Diseño de grilla adaptable** que ajusta la disposición de los candidatos al tamaño de la pantalla.
    - **Modo de pantalla completa opcional** para la votación.
- **Resultados en Tiempo Real:** Visualización de los resultados con tablas detalladas y gráficos.
- **Configuración Centralizada:** Todas las constantes y rutas del proyecto están en `config.py` para una fácil personalización.
- **Datos de Prueba:** La base de datos se puebla automáticamente con candidatos de ejemplo para facilitar las pruebas.

## Arquitectura del Proyecto

La arquitectura sigue un patrón de controlador principal para una gestión eficiente de las vistas.

```
padron-electoral/
├── main.py                 # Controlador principal y punto de entrada
├── config.py               # Módulo de configuración central
├── database.py             # Manejo de la base de datos
├── voting_app.py           # Frame de la interfaz de votación
├── admin_app.py            # Frame de la interfaz de administración
├── requirements.txt        # Dependencias del proyecto
├── README.md               # Documentación principal
├── CHANGELOG.md            # Registro de cambios
├── ...
└── assets/
    └── ...
```

## Instalación y Uso

### Requisitos
- Python 3.7 o superior
- Librerías: `tkinter`, `sqlite3`, `Pillow`, `matplotlib`

### Instalación
1. Clona o descarga el proyecto.
2. Crea un entorno virtual (recomendado): `python -m venv venv`
3. Instala las dependencias:
   ```bash
   # En Windows
   .\venv\Scripts\python.exe -m pip install -r requirements.txt
   # En macOS/Linux
   source venv/bin/activate && pip install -r requirements.txt
   ```

### Uso
Para iniciar la aplicación, ejecuta el siguiente comando en la raíz del proyecto:
```bash
# En Windows
.\venv\Scripts\python.exe main.py
# En macOS/Linux
python main.py
```

## Módulos del Sistema

- **`main.py`**: Punto de entrada y controlador principal (`MainApp`). Gestiona la ventana única de la aplicación y el cambio entre las diferentes vistas.
- **`config.py`**: Centraliza todas las constantes de la aplicación.
- **`database.py`**: Gestiona todas las operaciones con la base de datos SQLite.
- **`admin_app.py`**: Frame (`tk.Frame`) que implementa la interfaz de administración.
- **`voting_app.py`**: Frame (`tk.Frame`) que implementa la interfaz de votación.
- **`utils/auth.py`**: Maneja la lógica de autenticación.

## Flujo de la Aplicación

1.  **Inicio:** La aplicación se inicia ejecutando `main.py`, que crea una única ventana principal y muestra el menú.
2.  **Navegación:** El usuario puede seleccionar "Iniciar Votación" o "Modo Administración". El controlador principal cambia la vista activa dentro de la misma ventana.
3.  **Votación:** El votante se autentica, selecciona sus candidatos (con sus fotos visibles en una grilla adaptable) y confirma su voto.
4.  **Administración:** El administrador se autentica y accede a un panel con pestañas para gestionar candidatos (incluyendo la carga de fotos), votantes, ver resultados y configurar la elección.

## Funcionalidades Principales

### Gestión de Candidatos
- Agregar y eliminar candidatos.
- **Actualizar Foto:** Selecciona un candidato de la lista y presiona "Actualizar Foto" para asignarle una imagen personalizada. Una vista previa y una columna en la tabla te indicarán quién ya tiene foto.

### Gestión de Votantes
- Agregar y eliminar votantes individualmente.
- **Importación Masiva:** Importar votantes desde un archivo CSV con el formato `CI,Nombre,Apellido,Grado/Curso`.

### Resultados
- Visualización de resultados en tiempo real con tablas y gráficos de barras.

### Contraseña de Administrador
- La contraseña por defecto es `admin123`. Se recomienda cambiarla desde la pestaña "Configuración".

## Desarrollo y Contribución

Este proyecto es de código abierto. Para contribuir:
1.  Haz un fork del repositorio.
2.  Crea una nueva rama.
3.  Realiza tus cambios.
4.  Envía un pull request.
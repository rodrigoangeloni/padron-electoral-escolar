# Documentación del Sistema de Votación Escolar

## Tabla de Contenidos
1. [Descripción General](#descripción-general)
2. [Arquitectura del Proyecto](#arquitectura-del-proyecto)
3. [Instalación y Configuración](#instalación-y-configuración)
4. [Módulos del Sistema](#módulos-del-sistema)
5. [Flujo de la Aplicación](#flujo-de-la-aplicación)
6. [Interfaz de Usuario](#interfaz-de-usuario)
7. [Base de Datos](#base-de-datos)
8. [Seguridad y Autenticación](#seguridad-y-autenticación)
9. [Funcionalidades Principales](#funcionalidades-principales)
10. [Configuración y Personalización](#configuración-y-personalización)

## Descripción General

El Sistema de Votación Escolar es una aplicación de escritorio desarrollada en Python que facilita elecciones escolares para posiciones de liderazgo estudiantil como Directora, Vice Directora y Coordinadora. La aplicación permite la gestión completa del proceso electoral, desde la inscripción de candidatos y votantes hasta la emisión y conteo de votos.

### Características Principales
- Interfaz de votación en pantalla completa
- Registro de votos en base de datos SQLite
- Panel de administración para gestionar candidatos y ver resultados
- Control de acceso con contraseña para el modo administrativo
- Prevención de votos duplicados
- Sistema de resultados en tiempo real
- Autenticación por Cédula de Identidad (CI) de votantes
- Gestión de votantes por grado/curso
- Importación masiva de votantes desde archivos CSV
- Soporte para 3 cargos: Directora, Vice Directora y Coordinadora
- Candidatos organizados por grado que representan

## Arquitectura del Proyecto

```
padron-electoral/
├── main.py                 # Punto de entrada principal
├── database.py             # Manejo de la base de datos
├── voting_app.py           # Interfaz de votación
├── admin_app.py            # Interfaz de administración
├── setup_env.py            # Script para configurar entorno virtual
├── run_app.py              # Script para ejecutar la aplicación
├── ejemplo_votantes.csv    # Archivo de ejemplo para importar votantes
├── requirements.txt        # Dependencias
├── README.md              # Documentación
├── .gitignore             # Archivos a ignorar
├── models/
│   ├── __init__.py        # Inicialización del paquete
│   ├── candidate.py       # Modelo de candidato
│   └── vote.py            # Modelo de voto
├── utils/
│   ├── __init__.py        # Inicialización del paquete
│   └── auth.py            # Funciones de autenticación
└── assets/
    ├── config/
    │   └── .admin_password # Contraseña de administrador (hasheada)
    ├── db/
    │   └── election.db    # Base de datos SQLite
    └── images/
        └── default_candidate.jpg # Imagen por defecto para candidatos
```

## Instalación y Configuración

### Requisitos
- Python 3.7 o superior
- Librerías: tkinter, sqlite3, Pillow, matplotlib

### Instalación
1. Clonar o descargar el proyecto
2. Opcional: Configurar entorno virtual (recomendado para maximizar el rendimiento):
   ```bash
   python setup_env.py
   ```
   Esto creará un entorno virtual e instalará Pillow en él.

3. Si no usas el script de configuración, instalar directamente Pillow:
   ```bash
   pip install Pillow matplotlib
   ```

### Uso
#### Iniciar la aplicación
Opción 1: Ejecutar directamente (asegúrate de tener Pillow instalado)
```bash
python main.py
```

Opción 2: Usar el script de ejecución (recomendado, usa el entorno virtual si está disponible)
```bash
python run_app.py
```

## Módulos del Sistema

### main.py
Punto de entrada principal de la aplicación. Contiene la clase `MainApp` que gestiona la interfaz principal con botones para iniciar la votación o acceder al modo administración.

### database.py
Contiene la clase `DatabaseManager` que maneja todas las operaciones con la base de datos SQLite, incluyendo:
- Creación y gestión de tablas
- Operaciones CRUD para candidatos, votantes y votos
- Gestión del estado de la votación
- Funciones de resultados y estadísticas

### voting_app.py
Contiene la clase `VotingApp` que implementa la interfaz de votación para los usuarios finales, incluyendo:
- Autenticación por CI
- Selección de candidatos por cargo
- Confirmación de votos
- Prevención de votos duplicados

### admin_app.py
Contiene la clase `AdminApp` que implementa la interfaz de administración, con pestañas para:
- Gestión de candidatos
- Gestión de votantes
- Visualización de resultados
- Configuración del sistema

### setup_env.py
Script para configurar un entorno virtual Python e instalar las dependencias necesarias.

### run_app.py
Script para ejecutar la aplicación, usando el entorno virtual si está disponible.

## Flujo de la Aplicación

### Flujo Principal
1. La aplicación inicia en `main.py` mostrando la interfaz principal
2. El usuario puede elegir entre "Iniciar Votación" o "Modo Administración"
3. Cada opción destruye la ventana actual y crea una nueva instancia de la aplicación correspondiente

### Flujo de Votación
1. El votante ingresa su CI
2. La aplicación valida que el votante esté registrado y no haya votado aún
3. El votante selecciona candidatos para cada cargo (Directora, Vice Directora, Coordinadora)
4. Se muestra una pantalla de confirmación con las selecciones
5. El voto se registra en la base de datos
6. El sistema actualiza el estado del votante para evitar votos duplicados

### Flujo de Administración
1. El administrador ingresa la contraseña
2. Accede al panel con pestañas para diferentes funcionalidades
3. Puede gestionar candidatos, votantes, ver resultados y configurar el sistema

## Interfaz de Usuario

### Interfaz Principal
- Título: "Sistema de Votación Escolar"
- Botón "Iniciar Votación"
- Botón "Modo Administración"
- Botón "Salir"

### Interfaz de Votación
- Diseño en pantalla completa
- Ingreso de CI para autenticación
- Selección de candidatos por cargo en pasos sucesivos
- Vista previa de candidatos con foto, nombre y grado
- Confirmación final de selecciones
- Mensaje de agradecimiento después de votar

### Interfaz de Administración
- Autenticación por contraseña
- Pestañas organizadas:
  - Candidatos: Agregar, eliminar y gestionar candidatos
 - Votantes: Agregar, eliminar y gestionar votantes (con importación CSV)
  - Resultados: Ver resultados en tiempo real con gráficos
  - Configuración: Activar/cerrar votación, cambiar contraseña

## Base de Datos

La aplicación utiliza SQLite para almacenar:
- Información de candidatos (nombre, apellido, cargo, grado, imagen)
- Información de votantes (CI, nombre, apellido, grado/curso, estado de votación)
- Votos registrados (con referencia a candidato y CI del votante)
- Configuración del sistema (estado de la votación)

### Tablas de la Base de Datos
1. **candidatos**: Almacena información de los candidatos
2. **votantes**: Almacena información de los votantes registrados
3. **votos**: Registra cada voto emitido
4. **configuracion**: Almacena la configuración del sistema

## Seguridad y Autenticación

### Contraseña de Administrador
- Contraseña para acceso administrativo (hasheada con SHA-256)
- Se almacena en `assets/config/.admin_password`
- Valor por defecto: `admin123`

### Autenticación de Votantes
- Autenticación obligatoria por CI para votar
- Control automático de votos duplicados
- Verificación de formato de CI (7-8 dígitos numéricos)
- Almacenamiento seguro de datos sensibles

## Funcionalidades Principales

### Gestión de Candidatos
#### Registrar Candidatos
1. Ir a la pestaña "Candidatos" en el modo administración
2. Completar los campos: Nombre, Apellido, Cargo (DIRECTORA, VICEDIRECTORA, COORDINADORA), Grado
3. Hacer clic en "Agregar Candidato"

#### Cargos Disponibles
- DIRECTORA
- VICEDIRECTORA
- COORDINADORA

#### Grados Disponibles para Candidatos
- Pre Escolar
- 1er Grado a 9no Grado
- 1er Curso a 3er Curso

### Gestión de Votantes
#### Agregar Votantes Individualmente
1. Ir a la pestaña "Votantes" en el modo administración
2. Completar los campos: CI, Nombre, Apellido, Grado/Curso
3. Hacer clic en "Agregar Votante"

#### Importar Votantes desde Archivo CSV
1. Crear un archivo CSV con el formato: `CI,Nombre,Apellido,Grado/Curso`
2. Ir a la pestaña "Votantes" en el modo administración
3. Hacer clic en "Seleccionar Archivo CSV"
4. Seleccionar el archivo y confirmar la importación

**Nota**: Se incluye un archivo de ejemplo `ejemplo_votantes.csv` en el proyecto con datos de prueba.

#### Grados/Cursos Disponibles para Votantes
- Pre Escolar
- 1er Grado, 2do Grado, 3er Grado, 4to Grado, 5to Grado, 6to Grado, 7mo Grado, 8vo Grado, 9no Grado
- 1er Curso, 2do Curso, 3er Curso

### Resultados
- Visualización en tiempo real de resultados
- Tabla con resultados detallados por candidato
- Gráficos visuales de resultados por cargo
- Identificación clara de ganadores por cargo

### Configuración
- Activación/cierre de la votación
- Cambio de contraseña de administrador
- Reinicio de votos (funcionalidad de limpieza)

## Configuración y Personalización

### Contraseña de Administrador
- Por defecto: `admin123`
- Se recomienda cambiarla después de la primera configuración
- Se puede cambiar desde la pestaña "Configuración" en el modo administrativo

### Personalización
La aplicación puede ser personalizada según las necesidades específicas:
- Cambiar la contraseña de administrador
- Agregar imágenes de candidatas
- Modificar tiempos de votación
- Adaptar la interfaz gráfica
- Configurar grados/cursos disponibles

## Desarrollo

Para contribuir al proyecto:
1. Hacer fork del repositorio
2. Crear una rama para la nueva funcionalidad
3. Realizar los cambios
4. Enviar un pull request

## Licencia

Este proyecto es de código abierto y puede ser utilizado libremente para fines educativos.
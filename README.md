# Sistema de Votación Escolar

Aplicación de escritorio para elecciones estudiantiles en una escuela, donde los estudiantes pueden votar para elegir a su directora, vice directora y coordinadora.

## Características

- Interfaz de votación en pantalla completa
- Registro de votos en base de datos SQLite
- Panel de administración para gestionar candidatos y ver resultados
- Control de acceso con contraseña para el modo administrativo
- Prevención de votos duplicados (opcional)
- Sistema de resultados en tiempo real
- Autenticación por Cédula de Identidad (CI) de votantes
- Gestión de votantes por grado/curso
- Importación masiva de votantes desde archivos CSV
- Soporte para 3 cargos: Directora, Vice Directora y Coordinadora
- Candidatos organizados por grado que representan

## Requisitos

- Python 3.7 o superior
- Librerías: tkinter, sqlite3, Pillow

## Instalación

1. Clonar o descargar el proyecto
2. Opcional: Configurar entorno virtual (recomendado para maximizar el rendimiento):
   ```bash
   python setup_env.py
   ```
   Esto creará un entorno virtual e instalará Pillow en él.

3. Si no usas el script de configuración, instalar directamente Pillow:
   ```bash
   pip install Pillow
   ```

## Uso

### Iniciar la aplicación

Opción 1: Ejecutar directamente (asegúrate de tener Pillow instalado)
```bash
python main.py
```

Opción 2: Usar el script de ejecución (recomendado, usa el entorno virtual si está disponible)
```bash
python run_app.py
```

## Contraseña de Administrador

- Por defecto: `admin123`
- Se recomienda cambiarla después de la primera configuración
- Se puede cambiar desde la pestaña "Configuración" en el modo administrativo

## Funcionalidades

### Modo Votación
- Interfaz en pantalla completa
- Autenticación por Cédula de Identidad (CI) de 7-8 dígitos
- Verificación automática de votantes registrados
- Prevención de votos duplicados
- Visualización de 3 columnas por cargo (Directora, Vice Directora, Coordinadora)
- Candidatos organizados por grado que representan
- Selección intuitiva de candidatos
- Confirmación de voto

### Modo Administración
- Gestión de candidatos (agregar, eliminar)
- Gestión de votantes por CI (agregar, eliminar, importar desde CSV)
- Visualización de resultados en tiempo real
- Resultados generales y por grado/curso
- Activación/cierre de la votación
- Cambio de contraseña de administrador
- Reinicio de votos (funcionalidad de limpieza)

## Gestión de Candidatos

### Registrar Candidatos
1. Ir a la pestaña "Candidatos" en el modo administración
2. Completar los campos: Nombre, Apellido, Cargo (DIRECTORA, VICEDIRECTORA, COORDINADORA), Grado
3. Hacer clic en "Agregar Candidato"

### Cargos Disponibles
- DIRECTORA
- VICEDIRECTORA
- COORDINADORA

### Grados Disponibles para Candidatos
- Pre Escolar
- 1er Grado a 9no Grado
- 1er Curso a 3er Curso

## Gestión de Votantes

### Agregar Votantes Individualmente
1. Ir a la pestaña "Votantes" en el modo administración
2. Completar los campos: CI, Nombre, Apellido, Grado/Curso
3. Hacer clic en "Agregar Votante"

### Importar Votantes desde Archivo CSV
1. Crear un archivo CSV con el formato: `CI,Nombre,Apellido,Grado/Curso`
2. Ir a la pestaña "Votantes" en el modo administración
3. Hacer clic en "Seleccionar Archivo CSV"
4. Seleccionar el archivo y confirmar la importación

**Nota**: Se incluye un archivo de ejemplo `ejemplo_votantes.csv` en el proyecto con datos de prueba.

### Grados/Cursos Disponibles para Votantes
- Pre Escolar
- 1er Grado, 2do Grado, 3er Grado, 4to Grado, 5to Grado, 6to Grado, 7mo Grado, 8vo Grado, 9no Grado
- 1er Curso, 2do Curso, 3er Curso

## Estructura del Proyecto

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

## Seguridad

- Contraseña para acceso administrativo (hasheada con SHA-256)
- Autenticación obligatoria por CI para votar
- Control automático de votos duplicados
- Verificación de formato de CI (7-8 dígitos numéricos)
- Almacenamiento seguro de datos sensibles

## Personalización

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
# 📝 Changelog

<div align="center">

[![Version](https://img.shields.io/badge/Version-v1.4.2-blue.svg?style=for-the-badge)](https://github.com/rodrigoangeloni/padron-electoral-escolar)
[![Python](https://img.shields.io/badge/Python-3.7+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

</div>

---

<div align="center">

### 🔄 Registro de Cambios y Actualizaciones del Sistema de Votación Escolar

</div>

---

## 🚀 [Sin publicar] - Conversor RUE a CSV

### ✨ Añadido
- **🧾 Utilidad `tools/rue_a_csv.py`**: genera los 16 CSV del padrón desde los PDF oficiales (`PDF_LISTA_RUE`). Parser puro y testeado en `utils/rue_parser.py` (11 tests). Botón "Importar desde PDF RUE" en la pestaña Votantes (multiselección, import directo a DB con reporte). Sin CI → fecha de nacimiento DDMMYYYY; documento extranjero/pasaporte con número válido se usa tal cual; filas irreconocibles se reportan (sale código 1). `pypdf` en `requirements.txt` (se empaqueta en el exe). Padrón regenerado: 370 votantes (+11 vs CSV anterior, 0 bajas).

---

## 🚀 [v1.5.1] - 2026-10-08 - Fix Jardín en listas de grado

### 🐛 Corregido
- **🌱 Falta Jardín para alta manual**: `GRADOS_VOTANTES` y `GRADOS_CANDIDATOS` empiezan en Pre Escolar, pero el padrón trae Jardín (importado por CSV sin problema, pero no seleccionable a mano). Agregado `"Jardín"` al inicio de ambas listas + test.

---

## 🚀 [v1.5.0] - 2026-10-08 - Votación por turnos (Mañana/Tarde)

### ✨ Añadido
- **🕐 Turno en Candidatos (Fase 2)**: columna `turno` con migración (existentes quedan en `MAÑANA`). Campo Turno en el alta, filtro Todos/Mañana/Tarde en la lista + columna Turno, y la importación por CI hereda el turno del votante. `get_candidatos()` acepta `turno` y combina filtros.
- **🗳️ Votación por turno (Fase 3)**: la papeleta muestra solo candidatos del turno del votante; `cargos_sin_candidatos(turno)` bloquea por turno con mensaje que indica cuál.
- **📄 Acta por turno (Fase 4)**: selector Mañana/Tarde/Ambos en resultados y PDF. El acta trae participación (habilitados/votaron/%), ganadores con % por cargo, tabla con % y líneas de firma (presidente + 2 fiscales). Nuevo `get_participacion()` y `export_acta()` (API fpdf2 moderna, sin warnings deprecados).

### ✨ Añadido
- **🕐 Turno en Votantes**: nueva columna `turno` (`MAÑANA`/`TARDE`). Migración automática: DBs viejas la crean y la rellenan deduciendo el turno del grado (`"1er Grado TM"` → grado normalizado + turno).
- **📥 Importación CSV con turno**: el grado debe terminar en `TM`/`TT`; las filas sin turno o CI inválida se rechazan con reporte de línea (primeras 10) y resumen por turno. Resumen muestra conteo Mañana/Tarde.
- **📝 Alta manual y lista con turno**: selector Mañana/Tarde en el formulario y columna Turno en la lista.
- **📝 CSV con columna Turno**: formato canónico `CI,Nombre,Apellido,Grado,Turno` (Turno `TM`/`TT` separado por coma); el formato anterior con sufijo pegado sigue aceptado. Parsing centralizado en `parse_fila_votante()` (testeable sin GUI). Padrón 2026 convertido (359 filas: 183 TM + 176 TT).

---

## 🚀 [v1.4.3] - 2026-10-08 - Edición de CI y cambios sin publicar

### ✨ Añadido
- **🪪 Editar CI de Votante**: botón "Editar CI Seleccionada" en la pestaña Votantes; cambia la CI y reasigna los votos en transacción conservando `ya_voto` (nuevo método `update_votante_ci()` + 4 tests, suite 27/27).
- **📥 Importar Candidato desde el Padrón por CI**: campo CI en el alta de candidatos que autocompleta nombre, apellido y grado desde el padrón, con confirmación si el candidato ya existe.
- **🔢 Votantes sin CI**: convención documentada — usar fecha de nacimiento DDMMYYYY como CI (ej. `01092000` = 01/09/2000); vale para alta manual, CSV e importación.

### 🔧 Cambiado
- **🖱️ Lanzador sin consola**: `1_iniciar.bat` abre la app con `pythonw` (crea `.venv` si falta); script de compilación renombrado a `2_build.bat`.

---

## 🚀 [v1.4.2] - 2026-09-03 - Hotfix crash panel de administración

### 🐛 Corregido
- **🚨 Crash al Abrir Administración**: `_export_results_to_pdf` había quedado como función anidada muerta tras extraer `crear_figura_resultados()` (Fase 5), por lo que `ResultsUI` perdía el método y el exe fallaba con `AttributeError` al crear el panel. El método vuelve a la clase y se agrega test estructural de regresión (vía AST, corre sin display) que verifica que el método exista.

---

## 🚀 [v1.4.1] - 2026-09-03 - Integridad, Seguridad y Rendimiento

<div align="center">

[![](https://img.shields.io/badge/Added-%2B5_Features-green?style=for-the-badge)](https://github.com/rodrigoangeloni/padron-electoral-escolar)
[![](https://img.shields.io/badge/Changed-%2B4_Features-yellow?style=for-the-badge)](https://github.com/rodrigoangeloni/padron-electoral-escolar)
[![](https://img.shields.io/badge/Fixed-%2B7_Bugs-red?style=for-the-badge)](https://github.com/rodrigoangeloni/padron-electoral-escolar)
[![](https://img.shields.io/badge/Security-%2B3_Hardening-orange?style=for-the-badge)](https://github.com/rodrigoangeloni/padron-electoral-escolar)

</div>

### ✨ Añadido
- **🧪 Suite de Tests con Pytest**: 22 tests automatizados (`tests/`) con DB aislada por test (`tmp_path`): integridad DB, reglas de voto, seguridad de auth, validación de fotos y rendimiento de resultados.
- **⚙️ Detección de Cargos Vacíos**: Nuevo método `cargos_sin_candidatos()`; la votación se bloquea con mensaje claro si algún cargo no tiene candidatos, en vez de mostrar una pantalla vacía sin salida.
- **🏆 Ganadores con Empates**: Nuevo método `get_ganadores()` que devuelve todos los candidatos empatados en el máximo de votos; la UI muestra "Empate: ..." y el PDF lo refleja.
- **🖼️ Validación de Fotos**: Nuevo módulo `utils/foto_utils.py` (`validar_foto_candidato()`): solo JPG/PNG, máximo 5 MB y verificación de contenido real (rechaza ejecutables disfrazados e imágenes corruptas).
- **📦 Entorno Dev Reproducible**: Nuevo `requirements-dev.txt` (`pytest`) y suite verificada 22/22 con dependencias pinneadas.

### 🔧 Cambiado
- **🔐 Contraseñas con PBKDF2 + Salt**: `AuthManager` usa `PBKDF2-HMAC-SHA256` (200.000 iteraciones, salt aleatorio) en lugar de SHA-256 plano. Los hashes viejos siguen verificando hasta el próximo cambio de contraseña (migración sin bloqueo).
- **🗃️ Resultados con ID y Foto**: `get_resultados()` incluye `id` y `foto`, eliminando colisiones de homónimos y el patrón N+1 en ganadores (2 queries fijas).
- **📊 Gráficos sin Fugas de Memoria**: La creación de figuras se extrajo a `crear_figura_resultados()` (testeable sin display) y `_update_graphs` cierra la figura anterior con `plt.close()`.
- **🗳️ Voto Vacío Rechazado**: `add_multiple_votes()` con lista vacía retorna error y no marca `ya_voto`.

### 🐛 Corregido
- **🔑 FK No Aplicadas**: Se activa `PRAGMA foreign_keys = ON` por conexión; eliminar un candidato ya elimina sus votos (antes quedaban huérfanos).
- **📝 DEFAULT Literal**: El `DEFAULT` de `estado_votacion` era el texto `'{VOTACION_CERRADA}'`; ahora es `'cerrada'`.
- **🔓 Fallback `admin123` Eliminado**: Sin archivo de contraseña ya no se acepta la clave por defecto; el admin debe crear la inicial.
- **🚪 Login sin Límite**: Bloqueo tras 5 intentos fallidos (30 segundos) con aviso en la UI.
- **📂 Permisos del Password**: El archivo `.admin_password` se guarda con `chmod 0600`.
- **🧹 Código Muerto**: Eliminado `is_using_initial_password()` (siempre retornaba False) y la dependencia de `get_candidato_by_name()` en resultados.
- **🖼️ Extensión Normalizada**: Las fotos se guardan con extensión en minúsculas.

### 🛡️ Seguridad
- Hash con salt + comparación en tiempo constante (`hmac.compare_digest`).
- Rate-limit de login + validación real de uploads + secretos fuera del repo (sin cambios, verificado).

---

## 🚀 [v1.4.0] - 2025-10-15 - Gestión Dinámica de Cargos Electorales

<div align="center">

[![](https://img.shields.io/badge/Added-%2B1_Feature-green?style=for-the-badge)](https://github.com/rodrigoangeloni/padron-electoral-escolar)
[![](https://img.shields.io/badge/Changed-%2B4_Features-yellow?style=for-the-badge)](https://github.com/rodrigoangeloni/padron-electoral-escolar)
[![](https://img.shields.io/badge/Removed-%2B1_Component-red?style=for-the-badge)](https://github.com/rodrigoangeloni/padron-electoral-escolar)

</div>

### ✨ Añadido
- **⚙️ Gestión Dinámica de Cargos**: Se ha introducido una nueva sección en la pestaña "Configuración" que permite al administrador **añadir y eliminar los cargos electorales** (ej. "Presidente", "Secretario", etc.). Esto otorga una flexibilidad total para adaptar la elección a las necesidades de cada institución.

### 🔧 Cambiado
- **🗃️ Base de Datos Actualizada**: Se ha añadido una tabla `cargos` a la base de datos para almacenar los cargos de forma dinámica.
- **🗳️ Interfaz de Candidatos Mejorada**: El menú desplegable para asignar un cargo a un candidato ahora se puebla dinámicamente desde la base de datos, mostrando siempre los cargos disponibles.
- **🔄 Flujo de Votación Adaptativo**: La pantalla de votación ahora presenta los pasos de selección basados en los cargos configurados en la base de datos, en lugar de una lista fija.
- **📊 Resultados Dinámicos**: La visualización de resultados y los gráficos ahora se generan dinámicamente en función de los cargos existentes, asegurando que todos los puestos elegidos se muestren correctamente.

### ❌ Eliminado
- **🗑️ Lista Estática de Cargos**: Se ha eliminado la lista `CARGOS` del archivo `config.py`. Toda la lógica de la aplicación ahora depende de la base de datos para una gestión centralizada y dinámica.

---

## 🚀 [v1.3.5] - 2025-10-10 - Exportación de Resultados a PDF y Mejoras de Diseño

<div align="center">

[![](https://img.shields.io/badge/Added-%2B3_Features-green?style=for-the-badge)](https://github.com/rodrigoangeloni/padron-electoral-escolar)
[![](https://img.shields.io/badge/Changed-%2B2_Features-yellow?style=for-the-badge)](https://github.com/rodrigoangeloni/padron-electoral-escolar)

</div>

### ✨ Añadido
- **📄 Exportación de Resultados a PDF**: Se ha añadido la capacidad de exportar los resultados de las elecciones a un archivo PDF. Esta funcionalidad permite a los administradores generar un informe profesional con los ganadores y un resumen detallado de los votos.
- **📦 Nuevo Módulo `pdf_exporter`**: Se ha creado el módulo `utils/pdf_exporter.py` para encapsular la lógica de generación de archivos PDF, utilizando la librería `fpdf2`.
- **➕ Nueva Dependencia `fpdf2`**: Se ha añadido `fpdf2` al archivo `requirements.txt` para soportar la creación de documentos PDF.

### 🔧 Cambiado
- **🎨 Interfaz de Resultados Mejorada**: Se ha añadido un botón "Exportar a PDF" en la pestaña de resultados del panel de administración, permitiendo una fácil generación de informes.
- **📄 Diseño del Reporte PDF Mejorado**: Se ha mejorado el diseño del PDF exportado, incluyendo un título más prominente y un pie de página con créditos de desarrollador.

---

## 🚀 [v1.3.4] - 2025-10-10 - Metadatos y Personalización del Ejecutable

<div align="center">

[![](https://img.shields.io/badge/Added-%2B1_Feature-green?style=for-the-badge)](https://github.com/rodrigoangeloni/padron-electoral-escolar)
[![](https://img.shields.io/badge/Changed-%2B2_Features-yellow?style=for-the-badge)](https://github.com/rodrigoangeloni/padron-electoral-escolar)
[![](https://img.shields.io/badge/Fixed-%2B1_Bug-red?style=for-the-badge)](https://github.com/rodrigoangeloni/padron-electoral-escolar)

</div>

### ✨ Añadido
- **📝 Metadatos Detallados en Ejecutable**: Se ha incorporado un archivo de información de versión (`version_info.txt`) para enriquecer el ejecutable de Windows con metadatos profesionales, incluyendo descripción, versión, nombre del producto, copyright y compañía.

### 🔧 Cambiado
- **🖼️ Icono Personalizado**: Se ha configurado PyInstaller para utilizar un ícono personalizado (`icon.ico`) en el ejecutable, mejorando la identidad visual de la aplicación.
- **🌐 Idioma de Metadatos**: Se ha ajustado el idioma en las propiedades del ejecutable a "Español" para una correcta localización y presentación.

### 🐛 Corregido
- **🔢 Sincronización de Versiones**: Se corrigió la discrepancia en las propiedades del ejecutable, asegurando que tanto la "Versión del archivo" como la "Versión del producto" muestren `1.3.4.0`.

---

## 🚀 [1.3.3] - 2025-10-09 - Solución de Persistencia de Datos en Versión Compilada

<div align="center">

[![](https://img.shields.io/badge/Added-%2B2_Features-green?style=for-the-badge)](https://github.com/rodrigoangeloni/padron-electoral-escolar)
[![](https://img.shields.io/badge/Fixed-%2B1_Bug-red?style=for-the-badge)](https://github.com/rodrigoangeloni/padron-electoral-escolar)

</div>

### ✨ Añadido

- **📁 Nuevo Módulo de Manejo de Rutas**: Se ha añadido el módulo `utils/path_handler.py` que contiene funciones para manejar correctamente las rutas de archivos tanto en modo desarrollo como en versión compilada.
- **📦 Soporte para Persistencia en Compilación**: Se ha añadido soporte para que la base de datos y archivos de configuración se almacenen en ubicaciones persistentes fuera del directorio temporal cuando se compila la aplicación con PyInstaller.

### 🐛 Corregido

- **💾 Persistencia de Datos en Versión Compilada**: Se corrigió el problema donde los datos no se mantenían entre ejecuciones cuando se usaba la versión compilada del programa. Ahora la base de datos y los archivos de configuración se almacenan en ubicaciones persistentes.

---

## 🚀 [1.3.2] - 2025-10-09 - Disponibilidad de Ejecutable para Windows

<div align="center">

[![](https://img.shields.io/badge/Added-%2B1_Feature-green?style=for-the-badge)](https://github.com/rodrigoangeloni/padron-electoral-escolar)
[![](https://img.shields.io/badge/Changed-%2B1_Feature-yellow?style=for-the-badge)](https://github.com/rodrigoangeloni/padron-electoral-escolar)

</div>

### ✨ Añadido

- **📦 Distribución como Ejecutable**: Se ha añadido soporte para crear un ejecutable de Windows (.exe) usando PyInstaller, facilitando la instalación del sistema en entornos escolares sin necesidad de Python o dependencias adicionales. El archivo `SistemaVotacionEscolar.exe` puede descargarse y ejecutarse directamente en sistemas Windows sin instalación adicional.

### 🔧 Cambiado

- **📝 Documentación Actualizada**: Se ha actualizado el README.md para incluir instrucciones claras sobre cómo descargar y usar el ejecutable directamente, además de la instalación tradicional desde código fuente.

---

## 🚀 [1.3.1] - 2025-10-09 - Corrección de Registro de Votos Múltiples y Creación del Instalador

<div align="center">

[![](https://img.shields.io/badge/Added-%2B2_Features-green?style=for-the-badge)](https://github.com/rodrigoangeloni/padron-electoral-escolar)
[![](https://img.shields.io/badge/Fixed-%2B1_Bug-red?style=for-the-badge)](https://github.com/rodrigoangeloni/padron-electoral-escolar)

</div>

### ✨ Añadido

- **💾 Nuevo Método `add_multiple_votes`**: Se ha añadido un nuevo método en `DatabaseManager` que permite registrar múltiples votos para un mismo votante y marcarlo como que ya votó solo después de registrar todos los votos.
- **📦 Script de Instalación para Windows**: Se ha añadido soporte para crear un instalador de Windows (.exe) usando NSIS, facilitando la instalación del sistema en entornos escolares sin necesidad de Python o dependencias adicionales.

### 🐛 Corregido

- **🗳️ Registro Completo de Votos por Cargo**: Se corrigió el problema donde solo se registraba el voto para DIRECTORA y no para VICEDIRECTORA y COORDINADORA. Ahora todos los votos seleccionados se registran correctamente en la base de datos antes de marcar al votante como que ya votó.

---

## 🚀 [1.3.0] - 2025-10-09 - Mejora en la Ejecución de la Aplicación

<div align="center">

[![](https://img.shields.io/badge/Added-%2B1_Feature-green?style=for-the-badge)](https://github.com/rodrigoangeloni/padron-electoral-escolar)
[![](https://img.shields.io/badge/Changed-%2B1_Feature-yellow?style=for-the-badge)](https://github.com/rodrigoangeloni/padron-electoral-escolar)

</div>

### ✨ Añadido

- **🔧 Script de Ejecución Mejorado**: El archivo `run_app.py` ahora verifica si existe un entorno virtual `.venv`, y si no existe, lo crea, lo activa e instala las dependencias del archivo `requirements.txt`.

### 🔧 Cambiado

- **📦 Gestión de Dependencias**: El proceso de ejecución ahora se encarga automáticamente de la creación del entorno virtual y la instalación de dependencias, simplificando el inicio de la aplicación.

---

## 🎉 [1.2.0] - 2025-10-08 - Mejoras de Usabilidad y Funcionalidad

<div align="center">

[![](https://img.shields.io/badge/Added-%2B3_Features-green?style=for-the-badge)](https://github.com/rodrigoangeloni/padron-electoral-escolar)
[![](https://img.shields.io/badge/Changed-%2B2_Features-yellow?style=for-the-badge)](https://github.com/rodrigoangeloni/padron-electoral-escolar)
[![](https://img.shields.io/badge/Fixed-%2B3_Bugs-red?style=for-the-badge)](https://github.com/rodrigoangeloni/padron-electoral-escolar)

</div>

### ✨ Añadido

- **🖼️ Actualización de Fotos de Candidatos**: Se ha añadido la funcionalidad para subir o actualizar la foto de un candidato después de su registro desde el panel de administración.
- **👁️ Vista Previa de Foto**: En la pestaña de candidatos, ahora se muestra una vista previa de la imagen del candidato seleccionado.
- **📊 Indicador de Foto en Lista**: La lista de candidatos ahora incluye una columna "Foto" que indica ("Sí"/"No") si un candidato tiene una imagen personalizada.

### 🔧 Cambiado

- **📱 Diseño Adaptable en Votación**: La pantalla de selección de candidatos ahora utiliza una grilla que se ajusta dinámicamente, mejorando la visualización con un número variable de candidatos.
- **🖥️ Pantalla Completa Opcional**: La interfaz de votación ya no se inicia en pantalla completa por defecto. Se ha añadido un botón para que el usuario active esta opción si lo desea.

### 🐛 Corregido

- **🔄 Error de Sincronización de Fotos**: Se ha corregido un error que impedía que las fotos recién actualizadas se mostraran en la interfaz de votación.
- **🚪 Error de Cierre de Aplicación**: Se solucionó un problema que causaba que el proceso de la aplicación no terminara correctamente al cerrar la ventana principal.
- **📋 Error de Importación de CSV**: Se corrigió un error que intentaba procesar la fila del encabezado de los archivos CSV.

---

## 🏗️ [1.1.0] - 2025-10-08 - Refactorización Arquitectónica y de UX

<div align="center">

[![](https://img.shields.io/badge/Added-%2B3_Features-green?style=for-the-badge)](https://github.com/rodrigoangeloni/padron-electoral-escolar)
[![](https://img.shields.io/badge/Changed-%2B3_Features-yellow?style=for-the-badge)](https://github.com/rodrigoangeloni/padron-electoral-escolar)
[![](https://img.shields.io/badge/Removed-%2B1_Component-red?style=for-the-badge)](https://github.com/rodrigoangeloni/padron-electoral-escolar)

</div>

### ✨ Añadido

- **🏗️ Arquitectura de Controlador Principal** en `main.py`.
- **⚙️ Módulo de Configuración Central** `config.py`.
- **📊 Feedback de Usuario** en Importación de CSV.

### 🔧 Cambiado

- **💾 `DatabaseManager`** ahora usa una conexión única.
- **👥 `AdminApp` y `VotingApp`** convertidas a `tk.Frame`.
- **🔄 Flujo de navegación** mejorado en una única ventana.

### ❌ Eliminado

- **🔄 Dependencias circulares** y gestión ineficiente de ventanas.

---

## 🎯 [1.0.0] - 2025-10-07 - Versión Inicial

<div align="center">

[![](https://img.shields.io/badge/Initial-Release-blue?style=for-the-badge)](https://github.com/rodrigoangeloni/padron-electoral-escolar)

</div>

### ✨ Características Iniciales

- **🏛️ Sistema de Votación Escolar** completo con interfaz gráfica
- **👥 Gestión de Candidatos y Votantes** con base de datos SQLite
- **🔐 Autenticación de Usuarios** y control de votos duplicados
- **📊 Visualización de Resultados** en tiempo real

---

## 📊 Estadísticas del Proyecto

<div align="center">

| Versión | Fecha de Lanzamiento | Características | Correcciones | Tamaño del Código |
|:---:|:---:|:---:|
| 1.4.2 | 2026-09-03 | 0 | 1 | 🚨 Hotfix crash admin |
| 1.4.1 | 2026-09-03 | 5 | 7 | 🧪 +Suite de tests |
| 1.3.2 | 2025-10-09 | 1 | 0 | 📈 Aumentado |
| 1.3.1 | 2025-10-09 | 2 | 1 | 📈 Aumentado |
| 1.3.0 | 2025-10-09 | 1 | 0 | 🔄 Mejorado |
| 1.2.0 | 2025-10-08 | 3 | 3 | 📈 Aumentado |
| 1.1.0 | 2025-10-08 | 3 | 0 | 🔄 Refactorizado |
| 1.0 | 2025-10-07 | 4 | 0 | 🆕 Inicial |

</div>

---

## 🤝 Contribuciones

<div align="center">

¡Agradecemos todas las contribuciones al proyecto! Si encuentras un error o tienes una sugerencia, por favor abre un [issue](https://github.com/rodrigoangeloni/padron-electoral-escolar/issues) o envía un [pull request](https://github.com/rodrigoangeloni/padron-electoral-escolar/pulls).

</div>

---

<div align="center">

### 📞 Soporte

Para soporte técnico o consultas sobre el sistema, contacta con el equipo de desarrollo.

</div>
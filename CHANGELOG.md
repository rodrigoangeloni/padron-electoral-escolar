# 📝 Changelog

<div align="center">

[![Version](https://img.shields.io/badge/Version-1.2.0-blue.svg?style=for-the-badge)](https://github.com/rodrigoangeloni/padron-electoral-escolar)
[![Python](https://img.shields.io/badge/Python-3.7+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

</div>

---

<div align="center">

### 🔄 Registro de Cambios y Actualizaciones del Sistema de Votación Escolar

</div>

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
| 1.2.0 | 2025-10-08 | 3 | 3 | 📈 Aumentado |
| 1.1.0 | 2025-10-08 | 3 | 0 | 🔄 Refactorizado |
| 1.0.0 | 2025-10-07 | 4 | 0 | 🆕 Inicial |

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
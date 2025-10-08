# Changelog

## [1.2.0] - 2025-10-08 - Mejoras de Usabilidad y Funcionalidad

### Added
- **Actualización de Fotos de Candidatos:** Se ha añadido la funcionalidad para subir o actualizar la foto de un candidato después de su registro desde el panel de administración.
- **Vista Previa de Foto:** En la pestaña de candidatos, ahora se muestra una vista previa de la imagen del candidato seleccionado.
- **Indicador de Foto en Lista:** La lista de candidatos ahora incluye una columna "Foto" que indica ("Sí"/"No") si un candidato tiene una imagen personalizada.
- **Datos de Prueba Automáticos:** La base de datos se puebla automáticamente con 24 candidatos de prueba si está vacía, facilitando la demostración y el testeo.

### Changed
- **Diseño Adaptable en Votación:** La pantalla de selección de candidatos ahora utiliza una grilla que se ajusta dinámicamente, mejorando la visualización con un número variable de candidatos.
- **Pantalla Completa Opcional:** La interfaz de votación ya no se inicia en pantalla completa por defecto. Se ha añadido un botón para que el usuario active esta opción si lo desea.

### Fixed
- **Error de Sincronización de Fotos:** Se ha corregido un error que impedía que las fotos recién actualizadas se mostraran en la interfaz de votación.
- **Error de Cierre de Aplicación:** Se solucionó un problema que causaba que el proceso de la aplicación no terminara correctamente al cerrar la ventana principal.
- **Error de Importación de CSV:** Se corrigió un error que intentaba procesar la fila del encabezado de los archivos CSV.

---

## [1.1.0] - 2025-10-08 - Refactorización Arquitectónica y de UX

### Added
- Arquitectura de Controlador Principal en `main.py`.
- Módulo de Configuración Central `config.py`.
- Feedback de Usuario en Importación de CSV.

### Changed
- `DatabaseManager` ahora usa una conexión única.
- `AdminApp` y `VotingApp` convertidas a `tk.Frame`.
- Flujo de navegación mejorado en una única ventana.

### Removed
- Dependencias circulares y gestión ineficiente de ventanas.

---

## [1.0.0] - Initial Version
- Versión inicial del Sistema de Votación Escolar.
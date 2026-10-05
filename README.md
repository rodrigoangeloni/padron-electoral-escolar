# Sistema de Votación Escolar

Aplicación de escritorio para gestionar elecciones estudiantiles: cargos dinámicos, candidatos, padrón de votantes, votación por CI y resultados con gráficos y PDF.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Version](https://img.shields.io/badge/Version-v1.4.2-blue.svg?style=flat-square)](https://github.com/rodrigoangeloni/padron-electoral-escolar)
[![Platform](https://img.shields.io/badge/Windows-exe-0078D6?style=flat-square&logo=windows&logoColor=white)](https://github.com/rodrigoangeloni/padron-electoral-escolar/releases)
[![Tests](https://img.shields.io/badge/tests-23_passed-brightgreen?style=flat-square)](tests/)

## Características

- **Cargos dinámicos**: crear y eliminar cargos desde Configuración, sin tocar código.
- **Candidatos**: alta, baja y fotos (JPG/PNG hasta 5 MB, validadas).
- **Votantes**: registro individual o importación masiva desde CSV, validación de CI (7-8 dígitos) y prevención de voto duplicado.
- **Votación guiada**: un paso por cargo, confirmación final y comprobante en pantalla.
- **Resultados**: tabla, ganadores por cargo (con empates), gráficos y exportación a PDF.
- **Seguridad**: contraseña admin con PBKDF2 + salt, bloqueo tras intentos fallidos y control de estado (activa/cerrada).

## Descarga rápida (usuarios finales)

1. Ve a [Releases](https://github.com/rodrigoangeloni/padron-electoral-escolar/releases) y descarga `SistemaVotacionEscolar.exe`.
2. Ejecuta el archivo. No requiere instalar Python ni nada más.
3. Los datos se guardan junto al ejecutable y persisten entre sesiones.

## Instalación desde código (desarrolladores)

Requisitos: Windows 7+ (también funciona en macOS/Linux desde código), Python 3.11, 512 MB RAM.

```bash
git clone https://github.com/rodrigoangeloni/padron-electoral-escolar.git
cd padron-electoral-escolar

python -m venv .venv
.\.venv\Scripts\activate        # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Para desarrollo y tests:

```bash
pip install -r requirements-dev.txt
```

## Uso

```bash
python main.py        # o: python run_app.py (crea el .venv si falta)
```

En Windows también podés doble clic en `1_iniciar.bat`: crea el `.venv` si falta y abre la app sin consola.

### Primer uso (administrador)

1. Entra a **Modo Administración**. La primera vez se genera una contraseña inicial aleatoria: cópiala y guárdala.
2. Cambia la contraseña en la pestaña **Configuración**.
3. Carga **cargos**, **candidatos** y **votantes**, y pulsa **Activar Votación**.

### Votación

1. En el menú principal pulsa **Iniciar Votación** (requiere votación activa).
2. Ingresa la CI (7-8 dígitos numéricos).
3. Elige un candidato por cargo, revisa y confirma. Cada CI vota una sola vez.

### Importar votantes desde CSV

Archivo UTF-8 con encabezado (ver `ejemplo_votantes.csv`):

```csv
CI,Nombre,Apellido,Grado/Curso
1234567,María,González,Pre Escolar
2345678,Juan,Pérez,1er Grado
```

## Tests

```bash
.\.venv\Scripts\python -m pytest tests/ -q
```

Suite en `tests/` (23 tests, DB aislada por test con `tmp_path`): integridad de la base de datos, reglas de voto, seguridad de auth, validación de fotos y rendimiento de resultados.

## Seguridad

- Contraseñas con PBKDF2-HMAC-SHA256 (200.000 iteraciones, salt aleatorio, comparación en tiempo constante). Los hashes antiguos migran solos al cambiar la clave.
- Bloqueo temporal tras 5 intentos fallidos de login.
- Consultas SQL parametrizadas y claves foráneas activas (`PRAGMA foreign_keys = ON`).
- Fotos validadas por extensión, tamaño y contenido real.
- La base de datos (`.db`) y la contraseña nunca se suben al repo (ver `.gitignore`).

## Arquitectura

```
main.py            Controlador MainApp: menú, AdminApp y VotingApp en una ventana
config.py          Constantes centrales (rutas, grados, estados, colores)
database.py        DatabaseManager: SQLite, cargos/candidatos/votantes/votos
admin_app.py       Login + panel (Candidatos / Votantes / Resultados / Configuración)
voting_app.py      Flujo CI → selección por cargo → confirmación
utils/auth.py      AuthManager (PBKDF2, rate-limit)
utils/candidate_ui.py · voter_ui.py · results_ui.py   Pestañas del panel
utils/foto_utils.py   Validación de fotos (testeable sin GUI)
utils/pdf_exporter.py Exportación de resultados a PDF (fpdf2)
utils/path_handler.py Rutas dev vs compilado (persistencia junto al exe)
```

## Compilar el ejecutable

```bash
2_build.bat
# o manual: pip install pyinstaller && pyinstaller main.spec
# salida: dist/SistemaVotacionEscolar.exe (versión en version_info.txt)
```

## Cómo contribuir

1. Haz fork y crea una rama (`git checkout -b feature/mi-cambio`).
2. Agrega o actualiza tests en `tests/` y verifica con `pytest tests/ -q`.
3. Sigue PEP 8, docstrings y mensajes en español.
4. Abre un Pull Request.

## Licencia

Copyright (c) 2025 Rodrigo Angeloni. Uso, copia y modificación libres incluyendo el aviso de copyright; **prohibida la venta** sin permiso escrito. Ver [`LICENSE`](LICENSE). Detalle de cambios en [`CHANGELOG.md`](CHANGELOG.md).

---
*Última revisión: 2026-09-03 (v1.4.2). ¿Algo que agregar o corregir? Abre un [issue](https://github.com/rodrigoangeloni/padron-electoral-escolar/issues).*

# AGENTS.md — padron-electoral-escolar

Sistema de votación escolar desktop (Tkinter + SQLite). Cargos dinámicos, candidatos, votantes (CI), votación por pasos y resultados con gráficos + PDF.

## Stack
- README pide Python 3.11. Deps pinneadas en `requirements.txt`: `Pillow==11.3.0`, `matplotlib==3.10.7`, `fpdf2==2.7.9`, `pyinstaller==6.16.0`, `pypdf==6.19.0` (solo la usa el importador RUE). Tkinter/SQLite son stdlib. Dev: `requirements-dev.txt` (`pytest==9.1.1`).
- Suite pytest en `tests/` (121 tests verificados, fixtures `tmp_path` con DB aislada). Sin linter/formatter. PEP 8 + docstrings en español.
- Commits: Conventional Commits (tipo en inglés, descripción en español, ej. `feat: importar candidato desde el padron por CI`).
- Releases: secuencia fija — (1) suite verde, (2) sync versión (`version_info.txt` filevers/prodvers + strings, `config.APP_VERSION`, badges README/CHANGELOG, última revisión README), (3) sección `## 🚀 [vX.Y.Z] - YYYY-MM-DD` en CHANGELOG + fila en tabla de versiones, (4) commit `release: vX.Y.Z <resumen>` , (5) **tag anotado** `git tag -a vX.Y.Z -m "vX.Y.Z - <Resumen sin tildes>"` (sin tildes por encoding de consola Windows; el tag apunta al commit release), (6) `git push origin main` + `git push origin vX.Y.Z`, (7) recompilar exe (`cmd /c "echo.| 2_build.bat"`) y verificar estampa con `(Get-Item dist/...).VersionInfo`, (8) release GitHub con tag `vX.Y.Z` + adjuntar exe. Versionado: fix menor → parche (`x.x.Z+1`). Excepciones legacy no tocar: `v1.3.4`/`v1.4.2` son livianos (apuntan directo al commit).
- Texto del release GitHub (español, mismo esqueleto siempre; título en el campo título, NO en el cuerpo): título `vX.Y.Z — <Resumen>`; cuerpo: `## <emoji> Sistema de Votación Escolar vX.Y.Z` + 1 línea de resumen con el tipo (parche = "solo corrige… actualización segura"), secciones `### ✨ Novedades` y/o `### 🐛 Corregido` (una línea por cambio = efecto visible + condición que lo disparaba, no implementación), `### ✅ Verificación` (`N/N tests en verde`), `### 📥 Instalación` (3 pasos fijos: descargar exe de la página → ejecutar sin Python → datos junto al exe), cita `> ⚠️ Al actualizar: conservar assets/db/election.db y assets/config/…`, `### 📋 Detalle completo de cambios` con `**Full Changelog**: https://github.com/rodrigoangeloni/padron-electoral-escolar/compare/vA...vB` + link a `CHANGELOG.md` en main. Sin PRs en el repo, el texto es manual (el generador de GitHub no aplica). Al entregar el texto al usuario: título primero en su propio bloque copiable, luego la descripción en otro bloque separado.

## Comandos
```bash
# setup
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# run (dev)
python main.py
# alternativa: crea .venv + instala deps si falta y luego corre main.py
python run_app.py
# doble clic en Windows: lanza la app sin consola (crea .venv si falta)
1_iniciar.bat

# tests (requiere .venv con requirements + requirements-dev)
.\.venv\Scripts\python -m pytest tests/ -q
# build Windows exe (preferido)
2_build.bat
# manual:
pip install pyinstaller
pyinstaller main.spec
# salida: dist/SistemaVotacionEscolar.exe
```

## Estructura
- `main.py` — `MainApp(tk.Tk)` controlador. Registra frames `MainMenu`, `AdminApp`, `VotingApp` en un container y navega con `show_frame(name)`. Cada frame fija su geometría + `resizable` (`MAIN` no redimensionable; `VOTING`/`ADMIN` 1200x680 sí — `resizable(False, False)` también deshabilita maximizar). Maneja centrado (`center_window()`) y cierre (`db_manager.close()`).
- `config.py` — constantes centrales. Importa rutas desde `utils/path_handler`. Define `GRADOS_CANDIDATOS/VOTANTES` (listas idénticas), estados `VOTACION_ACTIVA/CERRADA`, colores, geometrías. `DEFAULT_ADMIN_PASSWORD` eliminado (comentado, línea 20).
- `database.py` — `DatabaseManager`: conexión única sqlite3, `PRAGMA foreign_keys = ON`, `init_db()` + `_seed_data()` + `_migrar_turno_votantes()` + `_migrar_turno_activo()`. Tablas: `candidatos(turno)`, `votantes(ci UNIQUE, ya_voto, turno)`, `votos`, `configuracion(estado_votacion, turno_activo)`, `cargos(nombre UNIQUE, orden)`. Cargos default: DIRECTORA, VICEDIRECTORA, COORDINADORA. `get_turno_activo()/set_turno_activo()` gestionan la sesión por turno (valida `TURNOS_VALIDOS`, default `MAÑANA`).
- `admin_app.py` — `AdminApp(tk.Frame)`: si no existe `ADMIN_PASSWORD_FILE`, genera inicial de 12 chars y la muestra una vez en popup; login → Notebook (Candidatos/Votantes/Resultados/Configuración). Delega a `utils/candidate_ui.py`, `voter_ui.py`, `results_ui.py`. En Configuración: combo "Turno a votar" (Mañana/Tarde) que se guarda al pulsar **Activar Votación**; queda `disabled` mientras la votación está activa.
- `voting_app.py` — `VotingApp(tk.Frame)`: flujo CI → selección por cargo (`roles = get_cargos()`) → confirmación → `add_multiple_votes()` → gracias 2s → reset a CI. La papeleta filtra por el **turno activo** (`get_turno_activo()`, decide el admin); `validate_ci` rechaza votantes de otro turno con mensaje. Bloquea cargos sin candidatos **del turno activo** (`cargos_sin_candidatos(turno)`). Grilla con scroll vertical (Canvas + `bind_all` rueda, liberado en `_clear_screen`); columnas con peso para centrar. Tamaño adaptativo vía `calcular_layout_papeleta(n)` pura/testeable → `(cols, img, fuente)`; >12 candidatos usa scroll.
- `utils/auth.py` — `AuthManager`: PBKDF2-HMAC-SHA256 (200.000 iteraciones, salt aleatorio, formato `salt_hex$hash_hex` en `assets/config/.admin_password` + flag `.initial_password_used`, comparación con `hmac.compare_digest`). Bloqueo 5 intentos/30s **en memoria** (se pierde al reiniciar). Sin archivo de password el login falla (sin fallback). Hash legacy SHA-256 plano solo se acepta para migrar al cambiar la clave.
- `utils/path_handler.py` — CLAVE para persistencia: `get_data_dir()` usa `dirname(sys.executable)` si `sys.frozen`, sino `assets/`. De ahí derivan `get_db_path()` (`db/election.db`), `get_config_dir()`, `get_images_dir()`. `get_resource_path()` usa `sys._MEIPASS` en compilado, raíz del repo en dev.
- `utils/foto_utils.py` — `validar_foto_candidato(ruta)` pura y testeable (sin GUI): solo `.jpg/.jpeg/.png`, ≤5 MB (`TAMANO_MAX_FOTO_BYTES`), contenido real (`verify()` + `load()`).
- `utils/pdf_exporter.py` — `export_acta(secciones, file_path)` con fpdf2 (API moderna: `helvetica`, `new_x/new_y`). Cada sección = un turno (`turno`, `participacion`, `winners`, `resultados` crudos de `get_resultados()`): participación con %, ganadores con % por cargo, tabla con % y firma única al final ("Presidente de Mesa o Encargado"). Pie con `Desarrollado por <DESARROLLADOR> - v<APP_VERSION>` (constantes en `config.py`) + página. `turno=None` = sección general con columna Turno.
- `models/` — `candidate.py`, `vote.py` sin uso (ningún import en el repo; lógica en `database.py`). No agregar lógica ahí sin migrar callers.
- `assets/` — `db/`, `config/`, `images/` creados en runtime. Solo `default_candidate.jpg` e `icon.ico` versionados (ver `.gitignore`).
- `tools/rue_a_csv.py` — conversor PDF RUE → CSV (`padron_votantes_2026/PDF_LISTA_RUE/` → `padron_votantes_2026/`) y función `convertir_pdf()` reutilizada por el botón "Importar desde PDF RUE" de `voter_ui` (import directo a DB, multiselección de PDFs). Parser puro en `utils/rue_parser.py` (sin pypdf: testeable). `pypdf` va en `requirements.txt` (se empaqueta en el exe); el import de `tools` es lazy con mensaje si falta. Sin CI → fecha DDMMYYYY; doc extranjero/pasaporte con número válido se usa tal cual; filas irreconocibles se reportan y el CLI sale con código 1.

## Convenciones
- Idioma: todo UI, mensajes, docstrings y CSV en español.
- Validación CI: `ci.isdigit() and 7 <= len(ci) <= 8` — aplicar igual en `voting_app.validate_ci`, `candidate_ui.import_voter_by_ci`, `voter_ui.add_voter/import_voters_from_file`. Sin CI: fecha de nacimiento DDMMYYYY manual (ej. `01092000`); mismo campo, sin código especial. Ojo con colisiones (misma fecha o CI real coincidente): `ci` es UNIQUE.
- Importar candidato por CI (`candidate_ui.import_voter_by_ci`): campo CI (fila 0 del form, Enter lo dispara) → `get_votante(ci)` (tupla `id, ci, nombre, apellido, grado_curso, ya_voto, turno`; usar índices 2/3/4) → rellena nombre/apellido/grado. Si nombre+apellido ya existe como candidato, pedir confirmación (`askyesno`). No hay columna CI en `candidatos`: la importación solo rellena campos.
- Cargos 100% dinámicos vía tabla `cargos`: al agregar/eliminar refrescar `candidate_ui.update_cargos_combobox()` y `refresh_cargos_list()`. No eliminar cargo asignado a candidatos (`delete_cargo` lo bloquea). Orden configurable: `get_cargos()` devuelve `ORDER BY orden, nombre`; `mover_cargo(nombre, ±1)` intercambia con el vecino (extremos = no-op); migración numera por nombre para no cambiar lo visible.
- Candidatos con turno: columna `turno` (`_migrar_turno_candidatos()` solo agrega con default `MAÑANA`, sin backfill — corregir manual si corresponde). `get_candidatos(cargo, grado, turno)` combina filtros con AND; `turno` al FINAL (índice 6, foto sigue en 5). Filtro Todos/Mañana/Tarde en la lista (`filtro_turno_var`, `None` = todos). Import por CI hereda el turno del votante (`votante[6]`).
- Votos: usar siempre `add_multiple_votes(ids, ci)` (transacción con rollback + `ya_voto=1` al final). `add_voto` single es legacy. Cambio de CI: `update_votante_ci(actual, nueva)` (valida formato/duplicados; inserta fila nueva copiando `ya_voto`, mueve `votos`, borra la vieja — UPDATE directo violaría la FK sin `ON UPDATE CASCADE`).
- Imágenes candidatos: validar con `validar_foto_candidato()`, copiar a `get_images_dir()` como `candidate_<id>.<ext>`, luego `update_candidate_photo()`. Fallback a `config.DEFAULT_CANDIDATE_IMAGE`.
- CSV votantes: encabezado `CI,Nombre,Apellido,Grado,Turno` (ver `ejemplo_votantes.csv`), encoding `utf-8`, saltar header con `next(reader)`. Turno en columna propia `TM`/`TT`; formato anterior con sufijo pegado (`1er Grado TM`) también aceptado. Parsing central en `utils/turno_utils.parse_fila_votante(row, linea)` → 5-tupla o `ValueError` (usado por `voter_ui`; testeable sin GUI). Grado base NO se valida contra `GRADOS_VOTANTES` (cualquier texto con sufijo válido pasa; la lista solo alimenta combos). `import_votantes_from_list` recibe 5-tuplas `(ci, nombre, apellido, grado, turno)`.
- Turno: columna `turno` (`MAÑANA`/`TARDE`, NOT NULL DEFAULT `'MAÑANA'`) en `votantes`. Migración `_migrar_turno_votantes()` (ALTER + backfill desde sufijo, normaliza grado; idempotente). `turno` va al FINAL de los SELECTs (`get_votante`/`get_votantes` índice 6) para no romper índices existentes (`ya_voto` sigue en 5). `add_votante(..., turno='MAÑANA')` rechaza turnos inválidos.
- Colores/geometrías solo vía `config.py` (`COLOR_PRIMARY/SUCCESS/WARNING/DANGER/WHITE`).
- Gráficos: `matplotlib` embebido con `FigureCanvasTkAgg`, un subplot horizontal por cargo.
- Reportes: selector Mañana/Tarde/Ambos en la pestaña (`results_ui.turno_actual`, `None` = ambos → dos secciones). Participación vía `get_participacion(turno)` → `(habilitados, votaron)`. `get_resultados/get_ganadores(turno=None)` filtran; `turno` al final de las filas (índice 7, foto sigue en 6).

## Gotchas operativos
- `.gitignore` ignora `*.db`, `assets/config/`, `assets/images/*` (excepto default + icon), `.venv/`, `padron_votantes_2026/` (CSVs con datos personales). DB y password nunca se commitean.
- Estado inicial votación: `cerrada`. Activarla en pestaña Configuración antes de votar (`MainMenu.start_voting` la bloquea si no está activa). El **turno activo** se elige en el combo "Turno a votar" y se persiste al activar: flujo Mañana (activar → votar → cerrar) → Tarde (cambiar combo → activar → votar).
- Ambos `.bat` terminan en `pause` y `2_build.bat` pregunta interactivamente si instalar pyinstaller → **nunca correrlos directo en shell no interactiva** (se cuelga); usar `cmd /c "echo.| 2_build.bat"`. `1_iniciar.bat` usa `pythonw.exe` (sin consola) si `.venv` existe y pasa el preflight (`import tkinter, PIL, matplotlib, fpdf`); si no, cae a `python run_app.py`.
- `2_build.bat` activa `.venv` si existe, si no usa python global; limpia `build/` + `dist/`. `main.spec` verificado: `datas=[('assets','assets')]`, `console=False`, `icon='icon.ico'`, `version='version_info.txt'`.
- Cierre app: `MainApp.on_closing` hace `askokcancel` + `close()` + `quit()` + `destroy()` — respetar ese orden (fix v1.2.0).
- Tests corren headless salvo GUI real: al menos un test usa `ast` para verificación estructural sin display. Sin tests nuevos, verificar manualmente — flujo admin (login → CRUD candidato/votante/cargo → activar votación) y flujo voto (CI válida/duplicada/inválida → multiselección → resultados → export PDF).

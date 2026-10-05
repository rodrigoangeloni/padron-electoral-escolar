# AGENTS.md — padron-electoral-escolar

Sistema de votación escolar desktop (Tkinter + SQLite). Gestión de cargos dinámicos, candidatos, votantes (CI), votación por pasos y resultados con gráficos + PDF.

## Stack
- Python 3.11.8 (README). Entorno actual verificado: 3.10.11 — funciona pero usar 3.11 para release.
- Deps pinneadas en `requirements.txt`: `Pillow==11.3.0`, `matplotlib==3.10.7`, `fpdf2==2.7.9`, `pyinstaller==6.16.0`. Tkinter/SQLite son stdlib. Dev: `requirements-dev.txt` (`pytest==9.1.1`).
- Suite pytest en `tests/` (23 tests, fixtures `tmp_path` con DB aislada). Sin linter/formatter configurado. Seguir PEP 8 + docstrings en español.

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
- `main.py` — `MainApp(tk.Tk)` controlador. Registra frames `MainMenu`, `AdminApp`, `VotingApp` en un container y navega con `show_frame(name)`. Maneja geometría (`config.MAIN/VOTING_WINDOW_GEOMETRY`) y cierre (`db_manager.close()`).
- `config.py` — constantes centrales. Importa rutas desde `utils/path_handler`. Define `GRADOS_CANDIDATOS/VOTANTES`, estados `VOTACION_ACTIVA/CERRADA`, colores, geometrías. No hay lista estática de cargos (eliminada en v1.4.0).
- `database.py` — `DatabaseManager`: conexión única sqlite3, `init_db()` + `_seed_data()`. Tablas: `candidatos`, `votantes(ci UNIQUE, ya_voto)`, `votos`, `configuracion`, `cargos(nombre UNIQUE)`. Cargos default: DIRECTORA, VICEDIRECTORA, COORDINADORA.
- `admin_app.py` — `AdminApp(tk.Frame)`: login admin → Notebook (Candidatos/Votantes/Resultados/Configuración). Delega a `utils/candidate_ui.py`, `voter_ui.py`, `results_ui.py`.
- `voting_app.py` — `VotingApp(tk.Frame)`: flujo CI → selección por cargo (`roles = get_cargos()`) → confirmación → `add_multiple_votes()` → gracias 2s → reset a CI.
- `utils/auth.py` — `AuthManager`: SHA-256 en `assets/config/.admin_password` + flag `.initial_password_used`. Si no existe archivo, genera password inicial aleatoria de 12 chars (mostrada una vez) y fuerza cambio. Fallback legacy `admin123` solo si falta archivo.
- `utils/path_handler.py` — CLAVE para persistencia: `get_data_dir()` usa `dirname(sys.executable)` si `sys.frozen`, sino `assets/`. De ahí derivan `get_db_path()` (`db/election.db`), `get_config_dir()`, `get_images_dir()`. `get_resource_path()` usa `sys._MEIPASS` en compilado.
- `utils/pdf_exporter.py` — `export_results_to_pdf(winners, results, file_path)` con fpdf2.
- `models/` — `candidate.py`, `vote.py` actualmente sin uso por la app (lógica está en `database.py`). No agregar lógica ahí sin migrar callers.
- `assets/` — `db/`, `config/`, `images/` creados en runtime. Solo `default_candidate.jpg` e `icon.ico` versionados (ver `.gitignore`).

## Convenciones
- Idioma: todo UI, mensajes, docstrings y CSV en español.
- Validación CI: `ci.isdigit() and 7 <= len(ci) <= 8` — aplicar igual en `voting_app.validate_ci`, `voter_ui.add_voter/import_voters_from_file`.
- Cargos 100% dinámicos vía tabla `cargos`: al agregar/eliminar refrescar `candidate_ui.update_cargos_combobox()` y `refresh_cargos_list()`. No eliminar cargo asignado a candidatos (`delete_cargo` lo bloquea).
- Votos: usar siempre `add_multiple_votes(ids, ci)` (transacción + `ya_voto=1` al final). `add_voto` single es legacy.
- Imágenes candidatos: copiar a `get_images_dir()` como `candidate_<id>.<ext>`, luego `update_candidate_photo()`. Fallback a `config.DEFAULT_CANDIDATE_IMAGE`.
- CSV votantes: encabezado `CI,Nombre,Apellido,Grado/Curso` (ver `ejemplo_votantes.csv`), encoding `utf-8`, saltar header con `next(reader)`.
- Colores/geometrías solo vía `config.py` (`COLOR_PRIMARY/SUCCESS/WARNING/DANGER/WHITE`).
- Gráficos: `matplotlib` embebido con `FigureCanvasTkAgg`, un subplot horizontal por cargo.

## Gotchas operativos
- `.gitignore` ignora `*.db`, `assets/config/`, `assets/images/*` (excepto default + icon), `.venv/`. La DB y password nunca se commitean — no esperar encontrarlas en repo limpio.
- Estado inicial votación: `cerrada`. Hay que activarla en pestaña Configuración antes de votar (`MainMenu.start_voting` la bloquea si no está activa).
- `2_build.bat` activa `.venv` si existe, si no usa python global; limpia `build/` + `dist/`. `main.spec` incluye `datas=[('assets','assets')]`, `console=False`, `icon='icon.ico'`, `version='version_info.txt'`.
- Cierre app: `MainApp.on_closing` hace `askokcancel` + `close()` + `quit()` + `destroy()` — respetar ese orden (fix v1.2.0).
- Sin tests: verificar manualmente — flujo admin (login → CRUD candidato/votante/cargo → activar votación) y flujo voto (CI válida/duplicada/inválida → multiselección → resultados → export PDF).

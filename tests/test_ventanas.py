"""Tests de la gestión de ventanas (estructural, sin display)."""
import ast
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _show_frame():
    """Devuelve el AST de MainApp.show_frame() en main.py."""
    ruta = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "main.py")
    with open(ruta, encoding="utf-8") as archivo:
        arbol = ast.parse(archivo.read())
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.FunctionDef) and nodo.name == "show_frame":
            return nodo
    raise AssertionError("No se encontró show_frame() en main.py")


def _rama_pagina(funcion, pagina):
    """Devuelve el If cuya condición menciona la página (MainMenu/VotingApp/AdminApp)."""
    for nodo in ast.walk(funcion):
        if isinstance(nodo, ast.If) and pagina in ast.dump(nodo.test):
            return nodo
    raise AssertionError(f"No se encontró la rama {pagina} en show_frame()")


def _llamadas(rama):
    """Lista (metodo, args_constantes, attrs) de las llamadas en la rama."""
    resultado = []
    for hijo in ast.walk(rama):
        if isinstance(hijo, ast.Call) and isinstance(hijo.func, ast.Attribute):
            args = [a.value for a in hijo.args if isinstance(a, ast.Constant)]
            attrs = [a.attr for a in hijo.args if isinstance(a, ast.Attribute)]
            resultado.append((hijo.func.attr, args, attrs))
    return resultado


def test_show_frame_cubre_los_tres_modos():
    funcion = _show_frame()
    for pagina in ("MainMenu", "VotingApp", "AdminApp"):
        _rama_pagina(funcion, pagina)


def test_admin_redimensionable_y_con_geometria_propia():
    """AdminApp usa ADMIN_WINDOW_GEOMETRY y resizable(True, True)."""
    llamadas = _llamadas(_rama_pagina(_show_frame(), "AdminApp"))
    assert ("resizable", [True, True], []) in llamadas
    assert any(metodo == "geometry" and "ADMIN_WINDOW_GEOMETRY" in attrs
               for metodo, _, attrs in llamadas)


def test_show_frame_restaura_ventana_maximizada():
    """Si está maximizada (zoomed), vuelve a normal: si no, geometry() se ignora."""
    funcion = _show_frame()
    for nodo in ast.walk(funcion):
        if isinstance(nodo, ast.If) and "zoomed" in ast.dump(nodo.test):
            llamadas = _llamadas(nodo)
            assert ("state", ["normal"], []) in llamadas
            return
    raise AssertionError("show_frame() no restaura la ventana maximizada")


def test_restauracion_antes_de_aplicar_geometria():
    """El restore a normal ocurre antes de cualquier geometry()."""
    funcion = _show_frame()

    def es_restore(nodo):
        return (isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Attribute)
                and nodo.func.attr == "state"
                and any(isinstance(a, ast.Constant) and a.value == "normal"
                        for a in nodo.args))

    def es_geometry(nodo):
        return (isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Attribute)
                and nodo.func.attr == "geometry")

    restores = [n.lineno for n in ast.walk(funcion) if es_restore(n)]
    geometrias = [n.lineno for n in ast.walk(funcion) if es_geometry(n)]
    assert restores and geometrias
    assert min(restores) < min(geometrias)

"""Tests de seguridad de autenticación (Fase 3).

Seams bajo prueba (interfaces públicas de AuthManager):
- verify_admin_password(): sin fallback admin123, con bloqueo y legacy
- set_admin_password(): hash con salt (mismo password → hashes distintos)
- esta_bloqueado()/registrar_intento_fallido()/reiniciar_intentos()
"""
import sys
import os
import hashlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from utils.auth import AuthManager


@pytest.fixture
def auth_manager(tmp_path):
    """AuthManager aislado con archivos temporales."""
    return AuthManager(
        password_file=str(tmp_path / ".admin_password"),
        initial_flag_file=str(tmp_path / ".initial_password_used"),
    )


def test_sin_archivo_no_acepta_admin123(auth_manager):
    """Sin archivo de contraseña no hay fallback: admin123 debe fallar."""
    assert auth_manager.verify_admin_password("admin123") is False


def test_hash_con_salt_difiere(tmp_path):
    """El mismo password genera hashes distintos (salt aleatorio)."""
    am1 = AuthManager(
        password_file=str(tmp_path / "pw1"),
        initial_flag_file=str(tmp_path / "flag1"),
    )
    am2 = AuthManager(
        password_file=str(tmp_path / "pw2"),
        initial_flag_file=str(tmp_path / "flag2"),
    )
    am1.set_admin_password("MismaClave123")
    am2.set_admin_password("MismaClave123")

    with open(am1.password_file) as f:
        hash1 = f.read().strip()
    with open(am2.password_file) as f:
        hash2 = f.read().strip()

    assert hash1 != hash2
    assert am1.verify_admin_password("MismaClave123") is True
    assert am2.verify_admin_password("MismaClave123") is True


def test_nuevo_formato_no_es_sha_plano(auth_manager):
    """El hash almacenado no debe ser el SHA-256 plano del password."""
    auth_manager.set_admin_password("NuevaSegura456")

    with open(auth_manager.password_file) as f:
        stored = f.read().strip()

    plano = hashlib.sha256("NuevaSegura456".encode()).hexdigest()
    assert stored != plano
    assert "$" in stored


def test_bloqueo_tras_intentos_fallidos(tmp_path):
    """Tras N fallos el manager se bloquea (rate-limit de login)."""
    am = AuthManager(
        password_file=str(tmp_path / ".admin_password"),
        initial_flag_file=str(tmp_path / ".initial_password_used"),
        max_intentos=3,
        bloqueo_segundos=60,
    )
    am.set_admin_password("Correcta123")

    assert am.verify_admin_password("wrong1") is False
    assert am.verify_admin_password("wrong2") is False
    assert am.verify_admin_password("wrong3") is False

    assert am.esta_bloqueado() is True
    # Bloqueado: ni la correcta pasa
    assert am.verify_admin_password("Correcta123") is False


def test_hash_legacy_sigue_verificando(tmp_path):
    """Migración: un hash SHA-256 viejo aún verifica hasta el cambio."""
    pw_file = str(tmp_path / ".admin_password")
    flag_file = str(tmp_path / ".initial_password_used")
    with open(pw_file, "w") as f:
        f.write(hashlib.sha256("Vieja123".encode()).hexdigest())

    am = AuthManager(password_file=pw_file, initial_flag_file=flag_file)

    assert am.verify_admin_password("Vieja123") is True
    assert am.verify_admin_password("OtraClave") is False

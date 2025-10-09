#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para hacer commit y push de los cambios realizados
"""
import subprocess
import sys
import os


def run_command(command):
    """Ejecuta un comando y devuelve el resultado"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def main():
    print("🚀 Iniciando proceso de commit y push...")
    
    # Verificar si estamos en un repositorio git
    success, stdout, stderr = run_command("git status")
    if not success:
        print("❌ No se encontró un repositorio git en el directorio actual")
        print(f"Error: {stderr}")
        return False
    
    print("✅ Repositorio git encontrado")
    
    # Agregar todos los archivos modificados
    print("🔄 Agregando archivos al commit...")
    success, stdout, stderr = run_command("git add .")
    if not success:
        print(f"❌ Error al agregar archivos: {stderr}")
        return False
    
    print("✅ Archivos agregados correctamente")
    
    # Hacer commit
    print("📝 Haciendo commit...")
    commit_message = " feat: Persistencia de datos en versión compilada\n\n- Se añadió módulo para manejar rutas de archivos correctamente en versiones compiladas\n- Se solucionó problema de persistencia de datos en versión ejecutable\n- Se actualizó CHANGELOG.md con nueva versión 1.3\n- Se actualizó información de versión en version_info.txt"
    
    success, stdout, stderr = run_command(f'git commit -m "{commit_message}"')
    if not success:
        if "nothing to commit" in stderr or "no changes added to commit" in stderr:
            print("ℹ️  No hay cambios para hacer commit")
            return True
        else:
            print(f"❌ Error al hacer commit: {stderr}")
            return False
    
    print("✅ Commit realizado correctamente")
    
    # Hacer push
    print("📤 Haciendo push...")
    success, stdout, stderr = run_command("git push")
    if not success:
        print(f"❌ Error al hacer push: {stderr}")
        return False
    
    print("✅ Push realizado correctamente")
    print("🎉 ¡Proceso de commit y push completado exitosamente!")
    
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Ocurrió un error durante el proceso de commit y push")
        sys.exit(1)
    else:
        print("\n✅ Todos los cambios han sido subidos exitosamente al repositorio")
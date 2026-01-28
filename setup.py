#!/usr/bin/env python3
"""Script de instalación del Agente Vendedor de IA."""

import os
import sys
import shutil


def check_python_version():
    """Verifica la versión de Python."""
    if sys.version_info < (3, 8):
        print("Error: Se requiere Python 3.8 o superior")
        sys.exit(1)
    print(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")


def create_directories():
    """Crea directorios necesarios."""
    dirs = ["data", "logs"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"Directorio creado: {d}/")


def create_env_file():
    """Crea archivo .env si no existe."""
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            shutil.copy(".env.example", ".env")
            print("Archivo .env creado desde .env.example")
        else:
            with open(".env", "w") as f:
                f.write("# Configuración del Agente Vendedor de IA\n")
                f.write("AGENT_NAME=Luna\n")
                f.write("COMPANY_NAME=IAgentic Solutions\n")
                f.write("# OPENAI_API_KEY=tu_clave_aqui\n")
                f.write("# ANTHROPIC_API_KEY=tu_clave_aqui\n")
            print("Archivo .env creado")
    else:
        print("Archivo .env ya existe")


def install_dependencies():
    """Instala dependencias."""
    print("\nInstalando dependencias...")
    os.system(f"{sys.executable} -m pip install -r requirements.txt")


def main():
    """Función principal de setup."""
    print("\n" + "=" * 50)
    print("  Instalación del Agente Vendedor de IA")
    print("=" * 50 + "\n")

    print("1. Verificando Python...")
    check_python_version()

    print("\n2. Creando directorios...")
    create_directories()

    print("\n3. Configurando archivos...")
    create_env_file()

    print("\n4. Instalando dependencias...")
    install_dependencies()

    print("\n" + "=" * 50)
    print("  Instalación completada")
    print("=" * 50)

    print("\nPróximos pasos:")
    print("1. Edita el archivo .env con tus API keys (opcional)")
    print("2. Ejecuta: python main.py")
    print("\nModos de ejecución disponibles:")
    print("  python main.py        - Interfaz completa con Rich")
    print("  python simple_chat.py - Interfaz simple de texto")
    print("  python web_app.py     - Interfaz web (requiere Flask)")
    print()


if __name__ == "__main__":
    main()

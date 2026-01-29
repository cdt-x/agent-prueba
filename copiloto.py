#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COPILOTO DE VENTAS
==================
Tu asistente personal que te susurra al oido durante las ventas.
"""

import sys
import os
import subprocess
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configurar consola Windows para UTF-8
if sys.platform == 'win32':
    subprocess.run(['chcp', '65001'], shell=True, capture_output=True)

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.sales_copilot import SalesCopilot


def clear_screen():
    """Limpia la pantalla."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    """Imprime el header del copiloto."""
    print("")
    print("================================================================")
    print("         COPILOTO DE VENTAS - TU ALIADO")
    print("    'Como tener un experto susurrandote al oido'")
    print("================================================================")
    print("")


def main():
    """Función principal del copiloto."""
    clear_screen()
    print_header()

    # Detectar API disponible
    api_provider = None
    if os.getenv("OPENAI_API_KEY"):
        api_provider = "openai"
        print("[OK] OpenAI detectado")
    elif os.getenv("ANTHROPIC_API_KEY"):
        api_provider = "anthropic"
        print("[OK] Anthropic detectado")
    elif os.getenv("GEMINI_API_KEY"):
        api_provider = "gemini"
        print("[OK] Gemini detectado")
    elif os.getenv("GROQ_API_KEY"):
        api_provider = "groq"
        print("[OK] Groq detectado")
    else:
        print("[!] Modo demo (sin API). Configura una API key para respuestas mas inteligentes.")
        api_provider = "openai"

    # Inicializar copiloto
    copilot = SalesCopilot(
        seller_name="Vendedor",
        api_provider=api_provider
    )

    # Mostrar bienvenida
    print(copilot.get_welcome())

    # Loop principal
    while True:
        try:
            user_input = input("\nTu: ").strip()

            if not user_input:
                continue

            # Comandos de salida
            if user_input.lower() in ["salir", "exit", "quit", "/salir", "/exit"]:
                print("\nBuena suerte con tus ventas!\n")
                break

            # Procesar y mostrar respuesta
            response = copilot.process_input(user_input)
            print(response)

        except KeyboardInterrupt:
            print("\n\nHasta luego!\n")
            break
        except Exception as e:
            print(f"\n[ERROR] {e}")
            print("Intenta de nuevo.\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Agente Vendedor de IA - IAgentic Solutions
Punto de entrada principal de la aplicación.
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.agent import SalesAgent
from ui.console import ConsoleUI
from config.settings import get_settings
from config.products import get_all_products


def main():
    """Función principal del agente vendedor."""
    # Cargar configuración
    settings = get_settings()

    # Inicializar UI
    ui = ConsoleUI(
        agent_name=settings.agent_name,
        company_name=settings.company_name
    )

    # Determinar proveedor de API
    api_provider = "openai"
    api_key = settings.openai_api_key

    if not api_key and settings.anthropic_api_key:
        api_provider = "anthropic"
        api_key = settings.anthropic_api_key

    # Inicializar agente
    agent = SalesAgent(
        agent_name=settings.agent_name,
        company_name=settings.company_name,
        api_provider=api_provider,
        api_key=api_key
    )

    # Mostrar bienvenida
    ui.show_welcome()

    if agent.demo_mode:
        ui.show_info("Ejecutando en modo DEMO (sin API key configurada)")
        ui.show_info("Para usar IA real, configura OPENAI_API_KEY o ANTHROPIC_API_KEY en .env")
        print()

    # Mostrar saludo inicial
    greeting = agent.get_greeting()
    ui.show_agent_message(greeting)

    # Loop principal de conversación
    while agent.is_active:
        try:
            # Obtener input del usuario
            user_input = ui.get_user_input().strip()

            if not user_input:
                continue

            # Procesar comandos especiales
            if user_input.startswith("/"):
                handle_command(user_input, agent, ui)
                continue

            # Mostrar mensaje del usuario
            ui.show_user_message(user_input)

            # Verificar si quiere salir
            if user_input.lower() in ["salir", "exit", "quit", "bye", "adios", "adiós"]:
                farewell = agent.end_conversation()
                ui.show_farewell(farewell)
                break

            # Mostrar indicador de pensamiento
            ui.show_thinking()

            # Procesar mensaje y obtener respuesta
            response = agent.process_message(user_input)

            # Mostrar respuesta del agente
            ui.show_agent_message(response)

        except KeyboardInterrupt:
            print()
            if ui.confirm("¿Deseas salir?"):
                farewell = agent.end_conversation()
                ui.show_farewell(farewell)
                break
            continue

        except Exception as e:
            ui.show_error(f"Ocurrió un error: {str(e)}")
            continue

    ui.show_success("¡Gracias por usar el Agente Vendedor de IA!")


def handle_command(command: str, agent: SalesAgent, ui: ConsoleUI):
    """Maneja comandos especiales."""
    cmd = command.lower().strip()

    if cmd in ["/ayuda", "/help", "/?", "/h"]:
        ui.show_help()

    elif cmd in ["/productos", "/products", "/catalogo"]:
        products = list(get_all_products().values())
        ui.show_products_menu(products)

    elif cmd in ["/perfil", "/profile"]:
        profile = agent.get_profile()
        ui.show_profile_summary(profile.to_dict())

    elif cmd in ["/resumen", "/summary"]:
        summary = agent.get_conversation_summary()
        ui.show_conversation_summary(summary)

    elif cmd in ["/reiniciar", "/reset", "/nuevo"]:
        if ui.confirm("¿Reiniciar la conversación?"):
            agent.reset()
            ui.show_success("Conversación reiniciada")
            greeting = agent.get_greeting()
            ui.show_agent_message(greeting)

    elif cmd in ["/salir", "/exit", "/quit"]:
        farewell = agent.end_conversation()
        ui.show_farewell(farewell)
        sys.exit(0)

    elif cmd in ["/recomendados", "/recommended"]:
        products = agent.get_recommended_products()
        ui.show_products_menu(products)

    else:
        ui.show_error(f"Comando no reconocido: {command}")
        ui.show_help()


if __name__ == "__main__":
    main()

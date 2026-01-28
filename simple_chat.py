#!/usr/bin/env python3
"""
Versión simple del agente vendedor (sin dependencias de Rich).
Ideal para pruebas rápidas o entornos sin soporte de consola avanzada.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.agent import SalesAgent
from config.settings import get_settings


def print_header():
    """Imprime el encabezado."""
    print("\n" + "=" * 60)
    print("   AGENTE VENDEDOR DE IA - IAgentic Solutions")
    print("=" * 60)
    print("\nComandos: /ayuda, /productos, /perfil, /salir")
    print("-" * 60 + "\n")


def print_agent(name: str, message: str):
    """Imprime mensaje del agente."""
    print(f"\n[{name}]:")
    print(message)
    print()


def print_user(message: str):
    """Imprime mensaje del usuario."""
    print(f"\n[Tú]: {message}")


def main():
    """Función principal."""
    settings = get_settings()

    # Inicializar agente
    agent = SalesAgent(
        agent_name=settings.agent_name,
        company_name=settings.company_name
    )

    print_header()

    if agent.demo_mode:
        print("[INFO] Modo DEMO activo (sin API key)")
        print("[INFO] Configura OPENAI_API_KEY o ANTHROPIC_API_KEY en .env para IA real\n")

    # Saludo inicial
    greeting = agent.get_greeting()
    print_agent(settings.agent_name, greeting)

    # Loop principal
    while agent.is_active:
        try:
            user_input = input(">>> ").strip()

            if not user_input:
                continue

            # Comandos
            if user_input.startswith("/"):
                cmd = user_input.lower()

                if cmd in ["/ayuda", "/help"]:
                    print("\nComandos disponibles:")
                    print("  /productos  - Ver catálogo")
                    print("  /perfil     - Ver perfil del cliente")
                    print("  /resumen    - Ver resumen")
                    print("  /reiniciar  - Nueva conversación")
                    print("  /salir      - Salir\n")
                    continue

                elif cmd in ["/productos", "/catalogo"]:
                    from config.products import get_all_products
                    products = get_all_products()
                    print("\n--- CATÁLOGO DE PRODUCTOS ---")
                    for pid, p in products.items():
                        print(f"\n• {p['nombre']}")
                        print(f"  Precio: {p['precio_base']}")
                        print(f"  Implementación: {p['tiempo_implementacion']}")
                    print()
                    continue

                elif cmd in ["/perfil", "/profile"]:
                    profile = agent.get_profile()
                    print("\n--- PERFIL DEL CLIENTE ---")
                    print(f"Industria: {profile.industry or 'No detectada'}")
                    print(f"Tipo: {profile.customer_type.value}")
                    print(f"Urgencia: {profile.urgency.value}")
                    print(f"Engagement: {profile.engagement_score:.0f}%")
                    print(f"Calificación: {profile.qualification_score:.0f}%")
                    print()
                    continue

                elif cmd in ["/resumen", "/summary"]:
                    summary = agent.get_conversation_summary()
                    print("\n--- RESUMEN ---")
                    print(f"Turnos: {summary['conversation']['total_turns']}")
                    print(f"Fase: {summary['conversation']['current_phase']}")
                    print()
                    continue

                elif cmd in ["/reiniciar", "/reset"]:
                    agent.reset()
                    print("\n[Conversación reiniciada]\n")
                    greeting = agent.get_greeting()
                    print_agent(settings.agent_name, greeting)
                    continue

                elif cmd in ["/salir", "/exit", "/quit"]:
                    farewell = agent.end_conversation()
                    print_agent(settings.agent_name, farewell)
                    break

                else:
                    print(f"Comando no reconocido: {user_input}")
                    continue

            # Verificar salida
            if user_input.lower() in ["salir", "exit", "bye", "adios"]:
                farewell = agent.end_conversation()
                print_agent(settings.agent_name, farewell)
                break

            # Procesar mensaje
            print_user(user_input)
            print("\n[Pensando...]")

            response = agent.process_message(user_input)
            print_agent(settings.agent_name, response)

        except KeyboardInterrupt:
            print("\n\n¿Salir? (s/n): ", end="")
            if input().lower() in ["s", "si", "y", "yes"]:
                farewell = agent.end_conversation()
                print_agent(settings.agent_name, farewell)
                break

        except Exception as e:
            print(f"\n[ERROR] {str(e)}\n")

    print("\n¡Gracias por usar el Agente Vendedor de IA!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

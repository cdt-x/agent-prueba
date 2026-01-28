#!/usr/bin/env python3
"""
Demostración de una conversación completa con el agente.
Útil para pruebas y demostración de capacidades.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import SalesAgent
from config.settings import get_settings


def run_demo():
    """Ejecuta una conversación demo."""
    print("\n" + "=" * 60)
    print("  DEMOSTRACIÓN DEL AGENTE VENDEDOR DE IA")
    print("=" * 60 + "\n")

    settings = get_settings()
    agent = SalesAgent(
        agent_name=settings.agent_name,
        company_name=settings.company_name
    )

    # Conversación de ejemplo
    demo_messages = [
        "Hola, tengo una tienda de ropa online y necesito mejorar mi atención al cliente",
        "Recibimos unas 200 consultas diarias y mi equipo no da abasto",
        "El principal problema es que perdemos ventas porque tardamos mucho en responder",
        "¿Cuánto cuesta la solución de atención al cliente?",
        "Me parece interesante, ¿cómo funciona la implementación?",
        "Sí, me gustaría agendar una demostración"
    ]

    # Saludo inicial
    greeting = agent.get_greeting()
    print(f"\n[{settings.agent_name}]:")
    print(greeting)
    print()

    # Procesar cada mensaje
    for message in demo_messages:
        print("-" * 50)
        print(f"\n[Cliente]: {message}\n")

        response = agent.process_message(message)

        print(f"[{settings.agent_name}]:")
        print(response)
        print()

    # Mostrar perfil final
    print("=" * 60)
    print("  PERFIL DEL CLIENTE (DETECTADO AUTOMÁTICAMENTE)")
    print("=" * 60)

    profile = agent.get_profile()
    print(f"""
Industria detectada: {profile.industry or 'No detectada'}
Tipo de cliente: {profile.customer_type.value}
Etapa de compra: {profile.buying_stage.value}
Urgencia: {profile.urgency.value}
Engagement Score: {profile.engagement_score:.0f}%
Qualification Score: {profile.qualification_score:.0f}%
Objeciones detectadas: {', '.join(profile.objections) or 'Ninguna'}
Productos de interés: {', '.join(profile.interested_products) or 'Por determinar'}
""")

    # Resumen de conversación
    print("=" * 60)
    print("  RESUMEN DE CONVERSACIÓN")
    print("=" * 60)

    summary = agent.get_conversation_summary()
    conv = summary['conversation']
    print(f"""
Turnos totales: {conv['total_turns']}
Fase alcanzada: {conv['current_phase']}
Duración: {conv['duration']} segundos
""")


if __name__ == "__main__":
    run_demo()

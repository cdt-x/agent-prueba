#!/usr/bin/env python3
"""
Ejemplo de cómo personalizar el agente para un negocio específico.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import SalesAgent
from core.conversation import ConversationManager
from config.products import PRODUCT_CATALOG


# Definir productos personalizados
CUSTOM_PRODUCTS = {
    "chatbot_whatsapp": {
        "nombre": "Chatbot para WhatsApp Business",
        "descripcion": "Bot inteligente para WhatsApp que atiende clientes 24/7",
        "beneficios": [
            "Integración directa con WhatsApp Business API",
            "Respuestas automáticas personalizadas",
            "Catálogo de productos integrado",
            "Pagos dentro de la conversación",
            "Estadísticas y analytics"
        ],
        "casos_uso": ["Tiendas online", "Restaurantes", "Servicios"],
        "precio_base": "Desde $199/mes",
        "tiempo_implementacion": "1 semana"
    },
    "asistente_restaurante": {
        "nombre": "Asistente para Restaurantes",
        "descripcion": "Bot especializado en reservas, pedidos y atención de restaurantes",
        "beneficios": [
            "Gestión automática de reservas",
            "Toma de pedidos por chat",
            "Menú digital interactivo",
            "Integración con delivery",
            "Programa de lealtad"
        ],
        "casos_uso": ["Restaurantes", "Cafeterías", "Dark kitchens"],
        "precio_base": "Desde $249/mes",
        "tiempo_implementacion": "2 semanas"
    }
}


class CustomSalesAgent(SalesAgent):
    """Agente personalizado con productos propios."""

    def __init__(self):
        # Llamar al constructor padre con configuración personalizada
        super().__init__(
            agent_name="Carlos",
            company_name="ChatBots Pro"
        )

        # Reemplazar productos
        self.products = CUSTOM_PRODUCTS

        # Personalizar el prompt del sistema
        self._customize_system_prompt()

    def _customize_system_prompt(self):
        """Personaliza el prompt del sistema."""
        custom_prompt = """Eres Carlos, un asesor experto en chatbots para PyMEs de ChatBots Pro.

Tu especialidad son soluciones de WhatsApp Business y chatbots para restaurantes.

PRODUCTOS QUE OFRECES:
1. Chatbot para WhatsApp Business ($199/mes) - Atención 24/7 por WhatsApp
2. Asistente para Restaurantes ($249/mes) - Reservas y pedidos automatizados

TU ESTILO:
- Eres cercano y usas un tono casual pero profesional
- Explicas las cosas de forma simple, sin tecnicismos
- Te enfocas en el ahorro de tiempo y dinero
- Das ejemplos concretos de cómo funcionaría para su negocio

PREGUNTAS CLAVE:
1. ¿Qué tipo de negocio tienes?
2. ¿Cuántas consultas recibes al día aproximadamente?
3. ¿Ya usas WhatsApp Business?
4. ¿Qué tarea te gustaría automatizar primero?

Recuerda: Tu objetivo es ayudar a pequeños negocios a automatizar su atención sin complicaciones."""

        # Actualizar el prompt en la conversación
        self.conversation.messages[0].content = custom_prompt


def main():
    """Ejemplo de uso del agente personalizado."""
    print("\n" + "=" * 60)
    print("  AGENTE PERSONALIZADO - ChatBots Pro")
    print("=" * 60 + "\n")

    agent = CustomSalesAgent()

    greeting = agent.get_greeting()
    print(f"[Carlos]: {greeting}\n")

    # Simular conversación
    messages = [
        "Hola, tengo un restaurante pequeño",
        "Recibo como 50 llamadas diarias para reservas",
        "¿Cuánto cuesta y cómo funciona?"
    ]

    for msg in messages:
        print(f"[Cliente]: {msg}")
        response = agent.process_message(msg)
        print(f"[Carlos]: {response}\n")


if __name__ == "__main__":
    main()

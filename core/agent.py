"""Agente de ventas principal."""

import os
from typing import Optional, Dict, Any, Generator
from .conversation import ConversationManager, ConversationPhase
from .customer_profile import CustomerProfiler, CustomerProfile
from .message_interpreter import MessageInterpreter, UserIntent
from config.products import get_all_products, get_products_for_industry, PRODUCT_CATALOG


class SalesAgent:
    """Agente de ventas de IA."""

    def __init__(
        self,
        agent_name: str = "FUTURE",
        company_name: str = "IAgentic Solutions",
        api_provider: str = "openai",
        api_key: Optional[str] = None
    ):
        self.agent_name = agent_name
        self.company_name = company_name
        self.api_provider = api_provider
        self.api_key = api_key or self._get_api_key()

        # Inicializar componentes
        self.conversation = ConversationManager(agent_name, company_name)
        self.profiler = CustomerProfiler()
        self.products = get_all_products()
        self.interpreter = MessageInterpreter()

        # Estado
        self.is_active = True
        self.demo_mode = not bool(self.api_key)

        # Cliente de API
        self.client = None
        if not self.demo_mode:
            self._initialize_client()

    def _get_api_key(self) -> Optional[str]:
        """Obtiene la API key del entorno."""
        if self.api_provider == "openai":
            return os.getenv("OPENAI_API_KEY")
        elif self.api_provider == "anthropic":
            return os.getenv("ANTHROPIC_API_KEY")
        return None

    def _initialize_client(self):
        """Inicializa el cliente de API."""
        try:
            if self.api_provider == "openai":
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            elif self.api_provider == "anthropic":
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
            elif self.api_provider == "gemini":
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel('gemini-2.0-flash')
            elif self.api_provider == "groq":
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
        except ImportError as e:
            print(f"Error importando cliente: {e}")
            self.demo_mode = True
        except Exception as e:
            print(f"Error inicializando cliente: {e}")
            self.demo_mode = True

    def get_greeting(self) -> str:
        """Obtiene el mensaje de bienvenida inicial."""
        greeting = f"""¡Hola! Soy {self.agent_name}, tu asesora de soluciones de IA en {self.company_name}.

Estoy aquí para ayudarte a descubrir cómo la Inteligencia Artificial puede transformar tu negocio, automatizar tareas repetitivas y mejorar la experiencia de tus clientes.

¿Me cuentas un poco sobre ti y tu empresa? Me encantaría saber a qué te dedicas y qué desafíos enfrentas actualmente."""

        # Agregar al historial
        self.conversation.add_assistant_message(greeting)

        return greeting

    def process_message(self, user_message: str) -> str:
        """Procesa un mensaje del usuario y genera una respuesta."""
        # Agregar mensaje al historial
        self.conversation.add_user_message(user_message)

        # Analizar mensaje para actualizar perfil
        self.profiler.analyze_message(user_message)

        # Verificar si debe avanzar de fase
        new_phase = self.conversation.should_advance_phase()
        if new_phase:
            self.conversation.transition_phase(new_phase)

        # Generar respuesta
        if self.demo_mode:
            response = self._generate_demo_response(user_message)
        else:
            response = self._generate_ai_response()

        # Agregar respuesta al historial
        self.conversation.add_assistant_message(response)

        return response

    def _generate_ai_response(self) -> str:
        """Genera respuesta usando la API de IA."""
        try:
            if self.api_provider == "openai":
                return self._generate_openai_response()
            elif self.api_provider == "anthropic":
                return self._generate_anthropic_response()
            elif self.api_provider == "gemini":
                return self._generate_gemini_response()
            elif self.api_provider == "groq":
                return self._generate_groq_response()
        except Exception as e:
            return f"Disculpa, tuve un problema técnico. ¿Podrías repetir tu mensaje? (Error: {str(e)})"

    def _generate_openai_response(self) -> str:
        """Genera respuesta usando OpenAI."""
        messages = self.conversation.get_messages_for_api()

        # Agregar contexto de fase y perfil
        context = self._build_context()
        messages.append({"role": "system", "content": context})

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )

        return response.choices[0].message.content

    def _generate_anthropic_response(self) -> str:
        """Genera respuesta usando Anthropic."""
        messages = self.conversation.get_messages_for_api()

        # Separar system message
        system_content = ""
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_content += msg["content"] + "\n"
            else:
                chat_messages.append(msg)

        # Agregar contexto
        system_content += "\n" + self._build_context()

        response = self.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            system=system_content,
            messages=chat_messages
        )

        return response.content[0].text

    def _generate_gemini_response(self) -> str:
        """Genera respuesta usando Gemini."""
        messages = self.conversation.get_messages_for_api()
        context = self._build_context()

        # Construir el prompt para Gemini
        prompt_parts = []

        # Agregar mensajes del sistema
        for msg in messages:
            if msg["role"] == "system":
                prompt_parts.append(f"[Instrucciones del sistema]: {msg['content']}")

        prompt_parts.append(f"[Contexto adicional]: {context}")
        prompt_parts.append("\n[Conversación]:")

        # Agregar historial de conversación
        for msg in messages:
            if msg["role"] == "user":
                prompt_parts.append(f"Cliente: {msg['content']}")
            elif msg["role"] == "assistant":
                prompt_parts.append(f"{self.agent_name}: {msg['content']}")

        prompt_parts.append(f"\n{self.agent_name}:")

        full_prompt = "\n".join(prompt_parts)

        response = self.client.generate_content(full_prompt)
        return response.text

    def _generate_groq_response(self) -> str:
        """Genera respuesta usando Groq (Llama 3)."""
        messages = self.conversation.get_messages_for_api()
        context = self._build_context()

        # Agregar contexto al sistema
        groq_messages = []
        system_content = ""

        for msg in messages:
            if msg["role"] == "system":
                system_content += msg["content"] + "\n"
            else:
                groq_messages.append(msg)

        system_content += "\n" + context

        # Insertar mensaje de sistema al inicio
        groq_messages.insert(0, {"role": "system", "content": system_content})

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=groq_messages,
            max_tokens=1000,
            temperature=0.7
        )

        return response.choices[0].message.content

    def _build_context(self) -> str:
        """Construye contexto adicional para la respuesta."""
        profile = self.profiler.get_profile()
        phase_context = self.conversation.get_phase_context()

        context_parts = [
            f"[FASE ACTUAL: {self.conversation.current_phase.value}]",
            phase_context,
            f"[PERFIL DEL CLIENTE: {profile.get_summary()}]"
        ]

        # Agregar productos recomendados si hay industria detectada
        if profile.industry:
            recommended = get_products_for_industry(profile.industry)
            if recommended:
                products_str = ", ".join([p["nombre"] for p in recommended[:3]])
                context_parts.append(f"[PRODUCTOS RECOMENDADOS: {products_str}]")

        return "\n".join(context_parts)

    def _generate_demo_response(self, user_message: str) -> str:
        """Genera respuestas en modo demo (sin API)."""
        profile = self.profiler.get_profile()
        phase = self.conversation.current_phase
        message_lower = user_message.lower()

        # Respuestas según la fase y contenido del mensaje
        if phase == ConversationPhase.GREETING or phase == ConversationPhase.DISCOVERY:
            return self._demo_discovery_response(message_lower, profile)

        elif phase == ConversationPhase.QUALIFICATION:
            return self._demo_qualification_response(message_lower, profile)

        elif phase == ConversationPhase.PRESENTATION:
            return self._demo_presentation_response(message_lower, profile)

        elif phase == ConversationPhase.OBJECTION_HANDLING:
            return self._demo_objection_response(message_lower, profile)

        elif phase == ConversationPhase.CLOSING:
            return self._demo_closing_response(message_lower, profile)

        return self._demo_generic_response(message_lower)

    def _demo_discovery_response(self, message: str, profile: CustomerProfile) -> str:
        """Respuestas para fase de descubrimiento."""
        # Contar turnos para variar respuestas
        turn = self.conversation.turn_count

        # Detectar industria mencionada
        if profile.industry:
            industry_responses = {
                "retail": "¡El retail es una industria fascinante! La competencia online ha cambiado mucho las reglas del juego. ¿Cuál dirías que es tu mayor desafío actualmente: atraer clientes, convertir visitas en ventas, o fidelizar a los que ya tienes?",
                "salud": "El sector salud tiene necesidades muy especiales en cuanto a atención y seguimiento de pacientes. ¿Me cuentas más sobre tu práctica? ¿Cuántos pacientes atienden aproximadamente al mes?",
                "educacion": "¡La educación está viviendo una transformación increíble! ¿Tu institución ya ofrece cursos online o es presencial? Me encantaría entender mejor cómo puedo ayudarte.",
                "tecnologia": "¡Excelente! En tech entendemos bien el valor de la automatización. ¿Tu producto es B2B o B2C? ¿Cuál es el principal cuello de botella en tu proceso de ventas o soporte?",
                "legal": "Los despachos de abogados manejan muchísima documentación y consultas repetitivas. ¿Cuántas consultas atienden aproximadamente al día? ¿Tienen ya algún sistema de gestión documental?",
                "finanzas": "El sector financiero requiere mucha precisión y disponibilidad. ¿Qué tipo de servicios financieros ofrecen? ¿Atención a personas o empresas?",
                "inmobiliaria": "¡El sector inmobiliario tiene un potencial enorme para la automatización! Entre mostrar propiedades, responder consultas y dar seguimiento... ¿cuál te quita más tiempo actualmente?",
                "gastronomia": "¡El sector gastronómico tiene muchísimo potencial! Entre pedidos, reservas y atención al cliente hay mucho que podemos automatizar. ¿Cuántos pedidos o consultas reciben aproximadamente al día?",
                "cafeteria": "¡Las cafeterías y restaurantes son perfectos para la automatización! Pedidos por WhatsApp, reservas, atención... ¿Cuál de estas tareas te consume más tiempo actualmente?"
            }
            if profile.industry in industry_responses:
                return industry_responses[profile.industry]

        # Detectar si menciona tareas específicas a automatizar
        normalized = self.interpreter.normalize(message)
        specific_tasks = {
            "caja": "¡La automatización de caja es muy útil! Podemos ayudarte con sistemas que procesan pagos y generan reportes automáticamente. ¿Actualmente usan algún sistema de punto de venta o todo es manual?",
            "pedidos": "Los pedidos automatizados son una de nuestras especialidades. Un agente puede recibir pedidos por WhatsApp 24/7, confirmarlos y hasta cobrar. ¿Cuántos pedidos reciben aproximadamente por día?",
            "whatsapp": "¡WhatsApp es el canal perfecto para automatizar! Nuestros agentes pueden atender consultas, tomar pedidos y enviar confirmaciones automáticamente. ¿Qué tipo de mensajes reciben más seguido?",
            "wsp": "¡WhatsApp es el canal perfecto para automatizar! Nuestros agentes pueden atender consultas, tomar pedidos y enviar confirmaciones automáticamente. ¿Qué tipo de mensajes reciben más seguido?",
            "reserv": "Las reservas automatizadas ahorran muchísimo tiempo. El agente puede verificar disponibilidad, confirmar y hasta enviar recordatorios. ¿Cuántas reservas manejan por semana?",
            "atencion": "La atención al cliente automatizada es nuestro fuerte. Imagina responder consultas frecuentes 24/7 sin esfuerzo. ¿Cuáles son las preguntas que más te hacen los clientes?",
            "cliente": "La atención al cliente automatizada es nuestro fuerte. Imagina responder consultas frecuentes 24/7 sin esfuerzo. ¿Cuáles son las preguntas que más te hacen los clientes?"
        }

        for keyword, response in specific_tasks.items():
            if keyword in normalized:
                # Avanzar a calificación si ya dieron detalles específicos
                if turn >= 2:
                    self.conversation.transition_phase(ConversationPhase.QUALIFICATION)
                return response

        # Usar interpretador inteligente
        if self.interpreter.mentions_problem(message):
            return "Entiendo perfectamente. Ese tipo de desafíos son más comunes de lo que imaginas. ¿Me podrías contar un poco más sobre cómo afecta esto a tu día a día? ¿Cuánto tiempo o recursos estimas que pierden por esta situación?"

        if self.interpreter.mentions_automation(message):
            # Variar la respuesta según el turno
            if turn <= 1:
                return "¡Genial que estés explorando la IA! Hay muchas posibilidades según tu caso específico. Para recomendarte la mejor solución, ¿me cuentas cuál es la tarea o proceso que más te gustaría automatizar?"
            else:
                # Ya mencionó automatización antes, profundizar
                self.conversation.transition_phase(ConversationPhase.QUALIFICATION)
                return "Perfecto, ya tengo una mejor idea de lo que necesitas. Déjame hacerte unas preguntas rápidas: ¿Cuántas consultas o tareas de este tipo manejan aproximadamente al día? Y ¿eres tú quien toma las decisiones de tecnología o necesitarías consultarlo con alguien?"

        return "Gracias por compartir eso. Para poder recomendarte la solución ideal, me gustaría entender un poco mejor tu situación. ¿Cuál dirías que es el principal desafío o 'dolor de cabeza' que enfrentas en tu negocio actualmente?"

    def _demo_qualification_response(self, message: str, profile: CustomerProfile) -> str:
        """Respuestas para fase de calificación."""
        if self.interpreter.is_price_inquiry(message):
            self.conversation.transition_phase(ConversationPhase.OBJECTION_HANDLING)
            return """¡Buena pregunta! Nuestras soluciones van desde $299/mes para un agente de atención al cliente hasta soluciones personalizadas para necesidades más complejas.

Lo interesante es que el retorno de inversión suele verse en el primer mes. Por ejemplo, un agente de atención 24/7 puede manejar el equivalente a 2-3 empleados de tiempo completo.

¿Tienes un presupuesto específico en mente? Así puedo recomendarte la opción que mejor se ajuste."""

        normalized = self.interpreter.normalize(message)
        if any(word in normalized for word in ["empleados", "equipo", "personas", "trabajadores", "gente", "colaboradores"]):
            return "Perfecto, eso me ayuda a entender mejor la escala. ¿Y en cuanto a la decisión de implementar una solución como esta, eres tú quien toma la decisión final o necesitarías consultarlo con alguien más?"

        return "Gracias por esa información. ¿Me podrías contar si ya han considerado alguna solución antes, o es la primera vez que exploran opciones de IA para su negocio?"

    def _demo_presentation_response(self, message: str, profile: CustomerProfile) -> str:
        """Respuestas para fase de presentación."""
        # Detectar si el usuario seleccionó una opción
        selected_option = self.interpreter.detect_selected_option(message)

        if selected_option:
            # El usuario eligió una opción específica
            option_products = {
                1: ("Agente de Atención 24/7", "atencion_cliente"),
                2: ("Agente de Ventas", "agente_ventas"),
                3: ("Agente Personalizado", "personalizado")
            }

            product_name, product_key = option_products.get(selected_option, option_products[1])

            # Avanzar a cierre
            self.conversation.transition_phase(ConversationPhase.CLOSING)

            return f"""¡Excelente elección! El **{product_name}** es una de nuestras soluciones más populares.

Este agente puede:
• Trabajar 24/7 sin descanso
• Manejar múltiples conversaciones simultáneamente
• Aprender y mejorar con cada interacción
• Integrarse con tus sistemas existentes

El siguiente paso sería agendar una demo de 20 minutos donde te muestro exactamente cómo funcionaría para tu negocio. ¿Te parece bien?"""

        # Recomendar productos según industria
        if profile.industry:
            products = get_products_for_industry(profile.industry)
            if products:
                product = products[0]
                return f"""Basándome en lo que me has contado, creo que el **{product['nombre']}** sería perfecto para ti.

**Beneficios principales:**
{chr(10).join(['• ' + b for b in product['beneficios'][:4]])}

**Precio:** {product['precio_base']}
**Implementación:** {product['tiempo_implementacion']}

¿Te gustaría que te cuente más sobre cómo funcionaría específicamente para tu caso? O si prefieres, podemos agendar una demostración personalizada."""

        # Respuesta genérica de presentación
        return """Tenemos varias soluciones que podrían ayudarte:

1. **Agente de Atención 24/7** - Para responder consultas automáticamente
2. **Agente de Ventas** - Para calificar leads y aumentar conversiones
3. **Agente Personalizado** - Diseñado 100% a tu medida

¿Cuál de estas te llama más la atención? O si prefieres, cuéntame más sobre tu necesidad principal y te recomiendo la más adecuada."""

    def _demo_objection_response(self, message: str, profile: CustomerProfile) -> str:
        """Respuestas para manejo de objeciones."""
        normalized = self.interpreter.normalize(message)

        # Objeción de precio
        price_objections = ["caro", "costoso", "mucho dinero", "barato", "economico", "muy caro", "no tengo presupuesto", "fuera de mi presupuesto"]
        if any(word in normalized for word in price_objections) or self.interpreter.is_price_inquiry(message):
            return """Entiendo la preocupación por la inversión. Déjame ponerlo en perspectiva:

Un empleado de atención al cliente cuesta aproximadamente $1,000-$2,000/mes (salario + prestaciones). Nuestro agente de IA por $299/mes trabaja 24/7, nunca se enferma, y puede atender múltiples conversaciones simultáneamente.

Además, ofrecemos:
• Prueba gratuita de 14 días
• Planes flexibles según tu volumen
• Garantía de satisfacción

¿Te gustaría probar sin compromiso para ver los resultados?"""

        # Objeción de tiempo
        if self.interpreter.is_time_inquiry(message):
            return """¡La implementación es más rápida de lo que imaginas!

Nuestros agentes pre-configurados están listos en **1-2 semanas**. El proceso es:
1. Configuración inicial (1-2 días)
2. Personalización con tu información (3-5 días)
3. Pruebas y ajustes (2-3 días)
4. ¡Lanzamiento!

Y lo mejor: tú no necesitas hacer nada técnico. Nosotros nos encargamos de todo.

¿Tienes alguna fecha límite en mente para tener esto funcionando?"""

        # Objeción de confianza/dudas
        if self.interpreter.has_doubt(message):
            return """¡Es una pregunta muy válida! Tenemos:

• **Casos de éxito comprobados**: Clientes que han reducido 70% sus tiempos de respuesta
• **Demo personalizada**: Te mostramos cómo funcionaría con TU negocio
• **Prueba gratuita de 14 días**: Sin compromiso ni tarjeta de crédito
• **Garantía de satisfacción**: Si no ves resultados, te devolvemos tu dinero

¿Qué te daría más confianza: ver una demo o empezar con la prueba gratuita?"""

        return "Entiendo tu preocupación. ¿Me podrías contar un poco más sobre qué es específicamente lo que te genera dudas? Quiero asegurarme de darte la información correcta."

    def _demo_closing_response(self, message: str, profile: CustomerProfile) -> str:
        """Respuestas para fase de cierre."""
        # Usar interpretador inteligente para detectar intención
        if self.interpreter.is_affirmative(message):
            return f"""¡Excelente decisión! Me alegra mucho poder ayudarte.

Para dar el siguiente paso, necesitaría:
1. Tu nombre completo
2. Tu correo electrónico
3. Un número donde podamos contactarte

Con esos datos, nuestro equipo te contactará en las próximas 24 horas para:
• Agendar la demo personalizada
• Configurar tu prueba gratuita
• Resolver cualquier duda adicional

¿Me compartes tus datos?"""

        if self.interpreter.is_negative(message):
            return """¡Por supuesto! Entiendo que es una decisión importante.

¿Te parece si te envío información por correo para que puedas revisarla con calma? Incluiría:
• Resumen de la solución que conversamos
• Casos de éxito relevantes para tu industria
• Precios y planes disponibles

Solo necesitaría tu correo electrónico. ¿Me lo compartes?"""

        # Detectar si seleccionó una opción (mañana/tarde, demo/prueba, etc.)
        normalized = self.interpreter.normalize(message)
        if any(word in normalized for word in ["manana", "mañana", "am", "temprano"]):
            return """¡Perfecto! Tenemos disponibilidad por las mañanas.

Para agendarte, necesito:
1. Tu nombre completo
2. Tu correo electrónico
3. Tu número de teléfono

¿Me los compartes?"""

        if any(word in normalized for word in ["tarde", "pm", "noche", "despues del medio"]):
            return """¡Muy bien! Tenemos horarios disponibles por las tardes.

Para agendarte, necesito:
1. Tu nombre completo
2. Tu correo electrónico
3. Tu número de teléfono

¿Me los compartes?"""

        if any(word in normalized for word in ["demo", "demostracion", "ver", "mostrar"]):
            return """¡Excelente! Una demo es la mejor forma de ver el potencial.

Para agendarte una demostración personalizada, necesito:
1. Tu nombre completo
2. Tu correo electrónico
3. Tu número de teléfono

¿Me los compartes?"""

        if any(word in normalized for word in ["prueba", "probar", "trial", "gratis", "gratuita"]):
            return """¡Genial! La prueba gratuita es perfecta para conocer la herramienta.

Para activar tu prueba de 14 días sin compromiso, necesito:
1. Tu nombre completo
2. Tu correo electrónico
3. Tu número de teléfono

¿Me los compartes?"""

        return """Basándome en todo lo que conversamos, creo que tenemos una solución que realmente puede ayudarte.

El siguiente paso sería agendar una demo de 20 minutos donde te muestro exactamente cómo funcionaría para tu caso específico. Sin compromiso.

¿Qué horario te vendría mejor: mañanas o tardes?"""

    def _demo_generic_response(self, message: str) -> str:
        """Respuesta genérica de fallback."""
        return "Gracias por tu mensaje. ¿Podrías contarme un poco más sobre lo que estás buscando? Así puedo orientarte hacia la solución más adecuada para tu caso."

    def get_profile(self) -> CustomerProfile:
        """Obtiene el perfil del cliente actual."""
        return self.profiler.get_profile()

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de la conversación."""
        return {
            "conversation": self.conversation.get_conversation_summary(),
            "profile": self.profiler.get_profile().to_dict()
        }

    def get_recommended_products(self) -> list:
        """Obtiene productos recomendados basado en el perfil."""
        profile = self.profiler.get_profile()
        if profile.industry:
            return get_products_for_industry(profile.industry)
        return list(PRODUCT_CATALOG.values())[:3]

    def reset(self):
        """Reinicia la conversación."""
        self.conversation.clear_history()
        self.profiler = CustomerProfiler()

    def end_conversation(self) -> str:
        """Finaliza la conversación con un mensaje de despedida."""
        profile = self.profiler.get_profile()

        farewell = f"""¡Gracias por tu tiempo hoy! Ha sido un placer conversar contigo.

Resumen de nuestra conversación:
• Fase alcanzada: {self.conversation.current_phase.value}
• Engagement: {profile.engagement_score:.0f}%
• Calificación: {profile.qualification_score:.0f}%

Si tienes más preguntas en el futuro, aquí estaré. ¡Que tengas un excelente día!"""

        self.is_active = False
        return farewell

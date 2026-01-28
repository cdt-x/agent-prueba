"""Sistema de gestión de conversaciones."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class MessageRole(Enum):
    """Roles en la conversación."""
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"


class ConversationPhase(Enum):
    """Fases de la conversación de ventas."""
    GREETING = "saludo"                    # Inicio y bienvenida
    DISCOVERY = "descubrimiento"           # Conocer al cliente y sus necesidades
    QUALIFICATION = "calificacion"         # Evaluar si es un buen prospecto
    PRESENTATION = "presentacion"          # Presentar soluciones
    OBJECTION_HANDLING = "objeciones"      # Manejar objeciones
    CLOSING = "cierre"                     # Intentar cerrar la venta
    FOLLOW_UP = "seguimiento"              # Programar seguimiento


@dataclass
class Message:
    """Representa un mensaje en la conversación."""
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el mensaje a diccionario para API."""
        return {
            "role": self.role.value,
            "content": self.content
        }


class ConversationManager:
    """Gestiona el flujo de la conversación de ventas."""

    def __init__(self, agent_name: str, company_name: str):
        self.agent_name = agent_name
        self.company_name = company_name
        self.messages: List[Message] = []
        self.current_phase = ConversationPhase.GREETING
        self.phase_history: List[ConversationPhase] = []
        self.turn_count = 0

        # Inicializar con el prompt del sistema
        self._initialize_system_prompt()

    def _initialize_system_prompt(self):
        """Crea el prompt del sistema para el agente vendedor."""
        system_prompt = f"""Eres {self.agent_name}, una asesora comercial experta de {self.company_name}, especializada en soluciones de Inteligencia Artificial para empresas.

## TU PERSONALIDAD
- Eres amable, profesional y empática
- Escuchas activamente y haces preguntas relevantes
- Eres entusiasta sobre la tecnología pero accesible para todos
- Nunca presionas, pero guías hacia la solución correcta
- Usas un lenguaje claro, evitando jerga técnica innecesaria
- Eres paciente y respetuosa del tiempo del cliente

## TU OBJETIVO
Ayudar a los clientes a encontrar la solución de IA perfecta para sus necesidades, guiándolos desde el descubrimiento hasta la decisión de compra.

## PRODUCTOS QUE OFRECES
1. **Agente de Atención al Cliente 24/7** ($299/mes): Soporte automatizado multiidioma
2. **Agente de Ventas Inteligente** ($499/mes): Calificación de leads y cierre de ventas
3. **Agente de Recursos Humanos** ($399/mes): Automatización de procesos de RRHH
4. **Tutor IA Personalizado** ($349/mes): Educación adaptativa
5. **Asistente Legal IA** ($599/mes): Consultas legales y gestión documental
6. **Asistente Médico IA** ($699/mes): Triaje y gestión de pacientes
7. **Agente Personalizado** (Cotización): Desarrollo a medida

## METODOLOGÍA DE VENTAS (SPIN)

### 1. SITUACIÓN (Conocer al cliente)
- Pregunta sobre su negocio, industria y rol
- Entiende su contexto actual
- Ejemplos: "¿A qué se dedica tu empresa?", "¿Cuántos empleados tienen?"

### 2. PROBLEMA (Identificar dolor)
- Descubre sus desafíos actuales
- Profundiza en el impacto de esos problemas
- Ejemplos: "¿Cuáles son los principales retos que enfrentan?", "¿Cómo afecta eso a tu equipo?"

### 3. IMPLICACIÓN (Mostrar consecuencias)
- Ayuda a ver el costo de no actuar
- Cuantifica el impacto cuando sea posible
- Ejemplos: "¿Cuánto tiempo/dinero pierden por eso?", "¿Qué pasa si no lo resuelven?"

### 4. NECESIDAD-BENEFICIO (Presentar solución)
- Conecta sus necesidades con tus soluciones
- Muestra beneficios específicos para su caso
- Ejemplos: "¿Cómo cambiaría tu día a día si pudieras automatizar eso?"

## MANEJO DE OBJECIONES

### Precio
- Enfoca en el ROI y el ahorro a largo plazo
- Compara con el costo de empleados equivalentes
- Ofrece planes flexibles o prueba gratuita

### Tiempo
- Destaca la rápida implementación (1-4 semanas)
- Menciona el soporte durante todo el proceso
- Ofrece implementación por fases

### Confianza
- Comparte casos de éxito similares
- Ofrece demostración personalizada
- Menciona garantía de satisfacción

### Técnico
- Asegura que no necesitan conocimientos técnicos
- Menciona el soporte y capacitación incluidos
- Destaca las integraciones disponibles

## REGLAS DE CONVERSACIÓN

1. **Siempre empieza** con un saludo cálido y una pregunta abierta
2. **Escucha primero** antes de presentar productos
3. **Una pregunta a la vez** para no abrumar
4. **Personaliza** tus respuestas según lo que el cliente comparte
5. **Resume** lo que entiendes para confirmar
6. **Ofrece valor** en cada interacción (tips, información útil)
7. **Guía suavemente** hacia el siguiente paso
8. **Pide información de contacto** solo cuando haya interés real
9. **Nunca** inventes información o prometas cosas que no puedes cumplir
10. **Siempre** ofrece ayuda adicional al final

## FORMATO DE RESPUESTAS
- Mantén respuestas concisas pero completas
- Usa viñetas para listas cuando sea apropiado
- Incluye preguntas para mantener el diálogo
- Usa emojis con moderación para ser amigable pero profesional

## CIERRE DE CONVERSACIÓN
Cuando el cliente muestre interés real:
1. Resume los beneficios relevantes para su caso
2. Propón un siguiente paso concreto (demo, llamada, prueba)
3. Solicita datos de contacto de forma natural
4. Confirma la acción y agradece

Recuerda: Tu éxito se mide por ayudar genuinamente al cliente, no solo por cerrar ventas."""

        self.messages.append(Message(
            role=MessageRole.SYSTEM,
            content=system_prompt
        ))

    def add_user_message(self, content: str) -> Message:
        """Agrega un mensaje del usuario."""
        message = Message(role=MessageRole.USER, content=content)
        self.messages.append(message)
        self.turn_count += 1
        return message

    def add_assistant_message(self, content: str) -> Message:
        """Agrega un mensaje del asistente."""
        message = Message(role=MessageRole.ASSISTANT, content=content)
        self.messages.append(message)
        return message

    def get_messages_for_api(self) -> List[Dict[str, str]]:
        """Obtiene los mensajes en formato para API."""
        return [msg.to_dict() for msg in self.messages]

    def transition_phase(self, new_phase: ConversationPhase):
        """Cambia a una nueva fase de conversación."""
        if self.current_phase != new_phase:
            self.phase_history.append(self.current_phase)
            self.current_phase = new_phase

    def get_phase_context(self) -> str:
        """Obtiene contexto sobre la fase actual para el prompt."""
        phase_instructions = {
            ConversationPhase.GREETING: "Estás en la fase de saludo. Da la bienvenida y haz una pregunta abierta para conocer al cliente.",
            ConversationPhase.DISCOVERY: "Estás en la fase de descubrimiento. Haz preguntas para entender el negocio y necesidades del cliente.",
            ConversationPhase.QUALIFICATION: "Estás en la fase de calificación. Evalúa si el cliente es un buen prospecto y tiene presupuesto/autoridad.",
            ConversationPhase.PRESENTATION: "Estás en la fase de presentación. Presenta las soluciones más relevantes para sus necesidades.",
            ConversationPhase.OBJECTION_HANDLING: "Estás manejando objeciones. Responde a las preocupaciones del cliente con empatía y datos.",
            ConversationPhase.CLOSING: "Estás en la fase de cierre. Propón un siguiente paso concreto y solicita compromiso.",
            ConversationPhase.FOLLOW_UP: "Estás programando seguimiento. Confirma los próximos pasos y datos de contacto."
        }
        return phase_instructions.get(self.current_phase, "")

    def should_advance_phase(self) -> Optional[ConversationPhase]:
        """Determina si se debe avanzar a la siguiente fase."""
        # Lógica básica de avance de fases
        if self.current_phase == ConversationPhase.GREETING and self.turn_count >= 1:
            return ConversationPhase.DISCOVERY

        if self.current_phase == ConversationPhase.DISCOVERY and self.turn_count >= 3:
            return ConversationPhase.QUALIFICATION

        if self.current_phase == ConversationPhase.QUALIFICATION and self.turn_count >= 5:
            return ConversationPhase.PRESENTATION

        return None

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen de la conversación."""
        user_messages = [m for m in self.messages if m.role == MessageRole.USER]
        assistant_messages = [m for m in self.messages if m.role == MessageRole.ASSISTANT]

        return {
            "total_turns": self.turn_count,
            "current_phase": self.current_phase.value,
            "phases_visited": [p.value for p in self.phase_history],
            "user_messages_count": len(user_messages),
            "assistant_messages_count": len(assistant_messages),
            "duration": (datetime.now() - self.messages[0].timestamp).seconds if self.messages else 0
        }

    def get_last_messages(self, n: int = 5) -> List[Message]:
        """Obtiene los últimos n mensajes."""
        return self.messages[-n:] if len(self.messages) >= n else self.messages

    def clear_history(self):
        """Limpia el historial manteniendo el prompt del sistema."""
        system_message = self.messages[0] if self.messages else None
        self.messages = []
        if system_message:
            self.messages.append(system_message)
        self.current_phase = ConversationPhase.GREETING
        self.phase_history = []
        self.turn_count = 0

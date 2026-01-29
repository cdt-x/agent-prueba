"""Copiloto de ventas - Asistente personal para el vendedor."""

import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from config.products import get_all_products, get_products_for_industry, PRODUCT_CATALOG, INDUSTRY_SOLUTIONS


class SalePhase(Enum):
    """Fases de la venta."""
    INICIO = "inicio"
    DESCUBRIMIENTO = "descubrimiento"
    CALIFICACION = "calificacion"
    PRESENTACION = "presentacion"
    OBJECIONES = "objeciones"
    CIERRE = "cierre"


@dataclass
class ClientInfo:
    """Información del cliente actual."""
    industry: Optional[str] = None
    business_type: Optional[str] = None
    business_size: Optional[str] = None
    main_problem: Optional[str] = None
    budget_mentioned: bool = False
    is_decision_maker: Optional[bool] = None
    contact_info: Dict[str, str] = field(default_factory=dict)
    objections: List[str] = field(default_factory=list)
    interests: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


class SalesCopilot:
    """Copiloto de ventas - Te guía en tiempo real durante la venta."""

    def __init__(
        self,
        seller_name: str = "Vendedor",
        api_provider: str = "openai",
        api_key: Optional[str] = None
    ):
        self.seller_name = seller_name
        self.api_provider = api_provider
        self.api_key = api_key or self._get_api_key()

        # Estado de la venta actual
        self.current_phase = SalePhase.INICIO
        self.client = ClientInfo()
        self.conversation_history: List[Dict[str, str]] = []
        self.products = get_all_products()

        # Cliente de API
        self.client_api = None
        self.demo_mode = not bool(self.api_key)
        if not self.demo_mode:
            self._initialize_client()

    def _get_api_key(self) -> Optional[str]:
        """Obtiene la API key del entorno."""
        providers = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "gemini": "GEMINI_API_KEY",
            "groq": "GROQ_API_KEY"
        }
        return os.getenv(providers.get(self.api_provider, ""))

    def _initialize_client(self):
        """Inicializa el cliente de API."""
        try:
            if self.api_provider == "openai":
                from openai import OpenAI
                self.client_api = OpenAI(api_key=self.api_key)
            elif self.api_provider == "anthropic":
                import anthropic
                self.client_api = anthropic.Anthropic(api_key=self.api_key)
            elif self.api_provider == "gemini":
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client_api = genai.GenerativeModel('gemini-2.0-flash')
            elif self.api_provider == "groq":
                from groq import Groq
                self.client_api = Groq(api_key=self.api_key)
        except Exception as e:
            print(f"Error inicializando API: {e}")
            self.demo_mode = True

    def get_welcome(self) -> str:
        """Mensaje de bienvenida del copiloto."""
        return """
================================================================
         QORAX - COPILOTO DE VENTAS
         "Tu asistente para cerrar ventas"
================================================================

Cuentame que te dice el cliente y te ayudo con:

  * Que preguntarle
  * Que producto ofrecerle
  * Como manejar objeciones
  * Texto listo para copiar y enviarle

PRECIOS QORAX:
  Setup: $1,500,000 COP (unico)
  Mensual: $250,000 COP/mes

Comandos:
  /nuevo     - Nuevo cliente
  /resumen   - Ver resumen del cliente
  /productos - Ver catalogo
  /ayuda     - Ver comandos

================================================================

Que te dijo el cliente?
"""

    def process_input(self, user_input: str) -> str:
        """Procesa lo que el vendedor escribe y da sugerencias."""
        # Comandos especiales
        if user_input.startswith("/"):
            return self._handle_command(user_input)

        # Guardar en historial
        self.conversation_history.append({
            "type": "seller_input",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })

        # Analizar y extraer información del cliente
        self._analyze_client_info(user_input)

        # Generar respuesta del copiloto
        if self.demo_mode:
            return self._generate_demo_response(user_input)
        else:
            return self._generate_ai_response(user_input)

    def _handle_command(self, command: str) -> str:
        """Maneja comandos especiales."""
        cmd = command.lower().strip()

        if cmd == "/nuevo":
            self.reset()
            return """
[OK] Nueva conversación iniciada.

Cliente anterior borrado. Cuéntame sobre el nuevo cliente.
"""

        elif cmd == "/resumen":
            return self._get_client_summary()

        elif cmd == "/productos":
            return self._get_products_list()

        elif cmd == "/ayuda":
            return """
[AYUDA] COMANDOS DISPONIBLES:

/nuevo      - Borrar todo y empezar con nuevo cliente
/resumen    - Ver lo que sabemos del cliente actual
/productos  - Ver catálogo completo de productos
/fase       - Ver en qué fase de la venta estamos
/precio X   - Ver precio del producto X
/ayuda      - Ver este menú

TIPS:
• Cuéntame lo que dice el cliente tal cual
• Si el cliente pregunta algo, te doy respuesta para copiar
• Puedes decirme "el cliente es abogado" para dar contexto
"""

        elif cmd == "/fase":
            return f"""
>> FASE ACTUAL: {self.current_phase.value.upper()}

Fases de venta:
1. Inicio ← Presentación inicial
2. Descubrimiento ← Conocer necesidades
3. Calificación ← ¿Es buen prospecto?
4. Presentación ← Mostrar solución
5. Objeciones ← Resolver dudas
6. Cierre ← Cerrar la venta
"""

        elif cmd.startswith("/precio"):
            product_query = cmd.replace("/precio", "").strip()
            return self._get_product_price(product_query)

        return "Comando no reconocido. Escribe /ayuda para ver los comandos disponibles."

    def _analyze_client_info(self, text: str) -> None:
        """Extrae información del cliente del texto."""
        text_lower = text.lower()

        # Detectar industria
        industry_keywords = {
            "legal": ["abogado", "abogados", "despacho", "legal", "juridico", "notaria", "notario", "ley", "leyes"],
            "salud": ["medico", "médico", "doctor", "doctora", "clinica", "clínica", "hospital", "paciente", "salud", "medicina", "consultorio"],
            "educacion": ["escuela", "colegio", "universidad", "educacion", "educación", "maestro", "profesor", "academia", "curso", "capacitacion"],
            "retail": ["tienda", "comercio", "venta", "ventas", "productos", "retail", "mayoreo", "menudeo", "ecommerce"],
            "inmobiliaria": ["inmobiliaria", "bienes raices", "propiedades", "casas", "departamentos", "rentas", "inmuebles"],
            "tecnologia": ["software", "tecnologia", "tecnología", "app", "aplicacion", "desarrollo", "programacion", "startup", "tech", "saas"],
            "finanzas": ["banco", "finanzas", "credito", "crédito", "prestamo", "préstamo", "inversiones", "contabilidad", "contador"],
            "gastronomia": ["restaurante", "cafeteria", "cafetería", "comida", "cocina", "chef", "bar", "antro", "cafe", "café"],
            "recursos_humanos": ["rrhh", "recursos humanos", "personal", "nomina", "nómina", "empleados", "contratacion"]
        }

        # Solo detectar industria si no hay una ya detectada
        if not self.client.industry:
            for industry, keywords in industry_keywords.items():
                if any(kw in text_lower for kw in keywords):
                    self.client.industry = industry
                    break

        # Detectar tamaño del negocio
        if any(word in text_lower for word in ["pequeño", "pequeña", "solo", "sola", "independiente", "freelance"]):
            self.client.business_size = "pequeño"
        elif any(word in text_lower for word in ["mediano", "mediana", "varios empleados", "equipo"]):
            self.client.business_size = "mediano"
        elif any(word in text_lower for word in ["grande", "corporativo", "empresa grande", "multinacional"]):
            self.client.business_size = "grande"

        # Detectar problemas/necesidades
        problem_keywords = {
            "atencion_cliente": ["atender", "responder", "consultas", "clientes", "cliente", "mensajes", "whatsapp", "24/7", "atencion", "atención", "soporte"],
            "ventas": ["vender", "ventas", "leads", "prospectos", "cerrar", "cotizar", "cotizaciones"],
            "automatizacion": ["automatizar", "repetitivo", "tiempo", "manual", "agilizar", "automatizacion", "automatización"],
            "documentos": ["documentos", "contratos", "papeles", "archivos", "organizar", "documentacion", "documentación"],
            "citas": ["citas", "agendar", "reservas", "calendario", "horarios", "agenda", "cita"]
        }

        for problem, keywords in problem_keywords.items():
            if any(kw in text_lower for kw in keywords):
                if problem not in self.client.interests:
                    self.client.interests.append(problem)

        # Detectar objeciones
        if any(word in text_lower for word in ["caro", "costoso", "precio", "presupuesto", "muy caro", "no tengo", "no cuento"]):
            if "precio" not in self.client.objections:
                self.client.objections.append("precio")

        if any(word in text_lower for word in ["tiempo", "demora", "tarda", "rapido", "urgente", "cuanto tiempo"]):
            if "tiempo" not in self.client.objections:
                self.client.objections.append("tiempo")

        if any(word in text_lower for word in ["funciona", "seguro", "confiable", "garantia", "duda", "dudas"]):
            if "confianza" not in self.client.objections:
                self.client.objections.append("confianza")

        # "Lo voy a pensar" es una objeción de indecisión
        if any(phrase in text_lower for phrase in ["lo voy a pensar", "lo va a pensar", "pensarlo", "dejame pensar", "tengo que pensarlo", "lo pienso", "voy a pensar"]):
            if "indecision" not in self.client.objections:
                self.client.objections.append("indecision")

        # Detectar aceptación/cierre
        cierre_phrases = [
            "dice que si", "dijo que si", "acepta", "acepto",
            "quiere contratar", "quiere agendar", "listo para",
            "va a contratar", "quiere la demo", "quiere una demo",
            "le interesa", "esta interesado", "está interesado",
            "quiere empezar", "quiere comenzar", "quiere probar",
            "me da sus datos", "me dio sus datos", "me paso su correo",
            "me compartio", "me comparti"
        ]
        if any(phrase in text_lower for phrase in cierre_phrases):
            self.current_phase = SalePhase.CIERRE
            return  # No seguir procesando, ya está en cierre

        # Actualizar fase automáticamente
        self._update_phase()

    def _update_phase(self) -> None:
        """Actualiza la fase de venta según la información recolectada."""
        if self.client.objections:
            self.current_phase = SalePhase.OBJECIONES
        elif self.client.industry and self.client.interests:
            if len(self.conversation_history) > 4:
                self.current_phase = SalePhase.PRESENTACION
            else:
                self.current_phase = SalePhase.CALIFICACION
        elif self.client.industry or self.client.interests:
            self.current_phase = SalePhase.DESCUBRIMIENTO
        else:
            self.current_phase = SalePhase.INICIO

    def _generate_demo_response(self, user_input: str) -> str:
        """Genera respuesta en modo demo (sin API)."""
        text_lower = user_input.lower()

        response_parts = []

        # === ANÁLISIS ===
        analysis = self._build_analysis()
        if analysis:
            response_parts.append(analysis)

        # === SUGERENCIAS ===
        suggestions = self._build_suggestions(text_lower)
        response_parts.append(suggestions)

        # === TEXTO PARA COPIAR ===
        copyable = self._build_copyable_response(text_lower)
        response_parts.append(copyable)

        return "\n".join(response_parts)

    def _build_analysis(self) -> str:
        """Construye la sección de análisis."""
        parts = ["", "[ANALISIS] ANÁLISIS:"]

        if self.client.industry:
            industry_names = {
                "legal": "Legal/Abogados",
                "salud": "Salud/Médico",
                "educacion": "Educación",
                "retail": "Retail/Comercio",
                "inmobiliaria": "Inmobiliaria",
                "tecnologia": "Tecnología",
                "finanzas": "Finanzas",
                "gastronomia": "Gastronomía",
                "recursos_humanos": "Recursos Humanos"
            }
            parts.append(f"   Industria: {industry_names.get(self.client.industry, self.client.industry)}")

        if self.client.business_size:
            parts.append(f"   Tamaño: Negocio {self.client.business_size}")

        if self.client.interests:
            parts.append(f"   Intereses: {', '.join(self.client.interests)}")

        if self.client.objections:
            parts.append(f"   [!] Objeciones: {', '.join(self.client.objections)}")

        parts.append(f"   Fase: {self.current_phase.value}")

        if len(parts) > 2:
            return "\n".join(parts)
        return ""

    def _build_suggestions(self, text: str) -> str:
        """Construye sugerencias para el vendedor."""
        parts = ["", "[SUGERENCIA] TE SUGIERO:"]

        # Sugerencias según la fase
        if self.current_phase == SalePhase.INICIO:
            parts.append("   • Pregúntale a qué se dedica su negocio")
            parts.append("   • Averigua cuál es su principal dolor/problema")
            parts.append("   • Muestra interés genuino en su situación")

        elif self.current_phase == SalePhase.DESCUBRIMIENTO:
            if not self.client.business_size:
                parts.append("   • Pregunta cuántos empleados o qué volumen maneja")
            parts.append("   • Profundiza en el problema: ¿cuánto tiempo/dinero pierde?")
            parts.append("   • Pregunta si ya intentó alguna solución antes")

        elif self.current_phase == SalePhase.CALIFICACION:
            parts.append("   • Verifica si él toma las decisiones")
            parts.append("   • Tantea si tiene presupuesto disponible")
            parts.append("   • Ya puedes mencionar que tienes una solución")

        elif self.current_phase == SalePhase.PRESENTACION:
            recommended = self._get_recommended_product()
            if recommended:
                parts.append(f"   • >> OFRÉCELE: {recommended['nombre']}")
                parts.append(f"   • Precio: {recommended['precio_base']}")
                parts.append(f"   • Beneficio clave: {recommended['beneficios'][0]}")

        elif self.current_phase == SalePhase.OBJECIONES:
            if "precio" in self.client.objections:
                parts.append("   * Compara con el costo de un empleado ($1,000-2,000/mes)")
                parts.append("   * Menciona la prueba gratuita de 14 dias")
                parts.append("   * Enfoca en el ROI, no en el costo")
            if "tiempo" in self.client.objections:
                parts.append("   * Asegurale que la implementacion es rapida (1-2 semanas)")
                parts.append("   * Dile que ustedes hacen todo el trabajo tecnico")
            if "confianza" in self.client.objections:
                parts.append("   * Ofrece una demo personalizada")
                parts.append("   * Menciona la garantia de satisfaccion")
                parts.append("   * Comparte un caso de exito similar")
            if "indecision" in self.client.objections:
                parts.append("   * NO lo presiones - dale espacio")
                parts.append("   * Ofrecele enviar info por correo")
                parts.append("   * Pregunta si tiene alguna duda especifica")
                parts.append("   * Propone una fecha para dar seguimiento")

        elif self.current_phase == SalePhase.CIERRE:
            parts.append("   * EXCELENTE! El cliente esta listo")
            parts.append("   * Pide sus datos de contacto")
            parts.append("   * Confirma el siguiente paso (demo/llamada)")
            parts.append("   * Agradece y confirma cuando te dara seguimiento")

        # Detectar si el cliente pregunta qué le recomiendas
        recomendacion_phrases = [
            "que me recomiendas", "qué me recomiendas",
            "que me sugieres", "qué me sugieres",
            "que le recomiendas", "qué le recomiendas",
            "que le sugieres", "qué le sugieres",
            "que opinas", "qué opinas",
            "tu que dices", "tú qué dices",
            "me recomiendas", "le recomiendas",
            "tu opinion", "tu opinión",
            "que me aconsejas", "qué me aconsejas",
            "cual me conviene", "cuál me conviene",
            "cual le conviene", "cuál le conviene",
            "que es mejor", "qué es mejor",
            "cual es mejor", "cuál es mejor",
            "que deberia", "qué debería"
        ]
        if any(phrase in text for phrase in recomendacion_phrases):
            parts.append("")
            parts.append("   >>> EL CLIENTE PIDE TU OPINION - Dale una recomendacion directa")

        return "\n".join(parts)

    def _build_copyable_response(self, text: str) -> str:
        """Construye texto listo para copiar y enviar al cliente."""
        parts = ["", "=" * 50, "[MENSAJE] COPIA Y ENVÍALE ESTO:", "=" * 50, ""]

        # Detectar si el cliente pregunta qué le recomiendas
        recomendacion_phrases = [
            "que me recomiendas", "qué me recomiendas",
            "que me sugieres", "qué me sugieres",
            "que le recomiendas", "qué le recomiendas",
            "que le sugieres", "qué le sugieres",
            "que opinas", "qué opinas",
            "tu que dices", "tú qué dices",
            "me recomiendas", "le recomiendas",
            "tu opinion", "tu opinión",
            "que me aconsejas", "qué me aconsejas",
            "cual me conviene", "cuál me conviene",
            "cual le conviene", "cuál le conviene",
            "que es mejor", "qué es mejor",
            "cual es mejor", "cuál es mejor",
            "que deberia", "qué debería"
        ]
        if any(phrase in text for phrase in recomendacion_phrases):
            recommended = self._get_recommended_product()
            if recommended:
                response = f"""Basándome en lo que me cuentas, te recomiendo el **{recommended['nombre']}**.

¿Por qué? Porque {recommended['beneficios'][0].lower()}

Además:
• {recommended['beneficios'][1]}
• {recommended['beneficios'][2]}

El precio es {recommended['precio_base']} y la implementación toma {recommended['tiempo_implementacion']}.

¿Te gustaría que te muestre cómo funcionaría específicamente para tu caso?"""
            else:
                response = """Te recomiendo que primero hagamos una llamada rápida de 15 minutos.

Así puedo entender mejor tu situación y diseñar una solución a la medida. No es lo mismo un negocio que otro, y quiero asegurarme de darte exactamente lo que necesitas.

¿Qué día te vendría bien? Puedo adaptarme a tu horario."""

            parts.append(response)
            return "\n".join(parts)

        # Respuestas según la fase y contexto
        if self.current_phase == SalePhase.INICIO or self.current_phase == SalePhase.DESCUBRIMIENTO:
            if self.client.industry:
                industry_responses = {
                    "legal": "¡Qué interesante! El sector legal tiene muchísimo potencial para automatizar. Entre consultas frecuentes, organización de documentos y seguimiento de casos... ¿cuál de estas tareas te quita más tiempo actualmente?",
                    "salud": "El sector salud es fascinante. Entre agendar citas, dar seguimiento a pacientes y responder dudas frecuentes, hay mucho que podemos automatizar. ¿Cuántas consultas o llamadas recibes aproximadamente al día?",
                    "gastronomia": "¡El sector gastronómico tiene mucho potencial! Pedidos por WhatsApp, reservas, consultas sobre el menú... ¿Cuál de estas te gustaría automatizar primero?",
                    "inmobiliaria": "Las inmobiliarias son perfectas para la automatización. Entre responder consultas de propiedades, agendar visitas y dar seguimiento... ¿cuál te consume más tiempo?",
                    "educacion": "¡La educación es un sector muy interesante! Desde responder dudas de alumnos hasta gestionar inscripciones. ¿Qué proceso te gustaría agilizar?",
                    "retail": "El comercio tiene muchísimas oportunidades de automatización. Atención al cliente, seguimiento de pedidos, consultas de inventario... ¿qué te quita más tiempo hoy?",
                    "tecnologia": "¡Genial! En tech entendemos bien el valor de la automatización. ¿Tu principal desafío es en soporte, ventas, o ambos?"
                }
                response = industry_responses.get(
                    self.client.industry,
                    "Gracias por contarme. Para darte una mejor recomendación, ¿me podrías contar cuál es el proceso o tarea que más tiempo te consume actualmente?"
                )
            else:
                response = "¡Gracias por contactarme! Me encantaría conocer más sobre tu negocio. ¿A qué te dedicas y cuál es el principal desafío que enfrentas actualmente?"

            parts.append(response)

        elif self.current_phase == SalePhase.CALIFICACION:
            response = """Perfecto, ya tengo una mejor idea de lo que necesitas.

Tenemos soluciones que van desde $250,000/mes hasta proyectos personalizados. El precio final depende de tus necesidades específicas.

Para darte una cotización precisa, ¿te parece si agendamos una llamada de 15 minutos? Así te muestro exactamente cómo funcionaría para tu caso.

¿Qué día te viene mejor?"""
            parts.append(response)

        elif self.current_phase == SalePhase.PRESENTACION:
            recommended = self._get_recommended_product()
            if recommended:
                response = f"""Para lo que me describes, te recomiendo el **{recommended['nombre']}**.

**¿Qué hace?**
{recommended['descripcion']}

**Beneficios:**
• {recommended['beneficios'][0]}
• {recommended['beneficios'][1]}
• {recommended['beneficios'][2]}

**Inversión:** {recommended['precio_base']}
**Implementación:** {recommended['tiempo_implementacion']}

¿Te gustaría ver una demo de cómo funcionaría específicamente para tu negocio?"""
            else:
                response = "Tengo varias opciones que podrían funcionarte. ¿Prefieres que te muestre las opciones en una llamada rápida de 15 minutos?"

            parts.append(response)

        elif self.current_phase == SalePhase.OBJECIONES:
            if "precio" in self.client.objections:
                response = """Entiendo la preocupación por la inversión. Déjame ponerlo en perspectiva:

Un empleado dedicado a estas tareas cuesta entre $1,000 y $2,000 al mes (salario + prestaciones). Nuestro agente por una fracción de eso trabaja 24/7, sin vacaciones, sin errores.

Además, ofrecemos:
• Prueba gratuita de 14 días (sin tarjeta)
• Garantía de satisfacción
• Planes flexibles según tu volumen

¿Te gustaría probarlo sin compromiso para ver los resultados primero?"""
            elif "tiempo" in self.client.objections:
                response = """¡La implementación es más rápida de lo que imaginas!

La mayoría de nuestros clientes están operando en 1-2 semanas. Y lo mejor: tú no tienes que hacer nada técnico. Nosotros nos encargamos de todo.

El proceso es:
1. Configuración inicial (1-2 días)
2. Personalización (3-5 días)
3. Pruebas y ajustes (2-3 días)
4. ¡Lanzamiento!

¿Tienes alguna fecha en mente para tener esto funcionando?"""
            elif "confianza" in self.client.objections:
                response = """Entiendo perfectamente. Es una decision importante.

Te propongo lo siguiente:
1. Una demo personalizada donde te muestro exactamente como funcionaria para TU negocio
2. Prueba gratuita de 14 dias para que lo pruebes sin riesgo
3. Garantia de satisfaccion - si no ves resultados, te devolvemos tu dinero

Que te daria mas confianza: la demo primero o empezar directo con la prueba gratuita?"""
            elif "indecision" in self.client.objections:
                response = """Por supuesto, tomate tu tiempo. Es una decision importante y quiero que estes seguro.

Te propongo lo siguiente: te envio un resumen por correo con toda la informacion que conversamos, para que puedas revisarla con calma.

Incluiria:
- Resumen de la solucion ideal para tu caso
- Precios y planes disponibles
- Casos de exito de negocios similares

Solo necesitaria tu correo. Y si quieres, podemos agendar una llamada de seguimiento para la proxima semana. Sin presion.

Que te parece?"""
            else:
                response = "Entiendo tu preocupacion. Me podrias contar un poco mas sobre que es lo que te genera dudas? Quiero asegurarme de darte la informacion correcta."

            parts.append(response)

        elif self.current_phase == SalePhase.CIERRE:
            response = """¡Perfecto! Para avanzar, solo necesito:

1. Tu nombre completo
2. Correo electrónico
3. Número de WhatsApp

Con eso te contactamos en las próximas 24 horas para:
• Agendar tu demo personalizada
• Configurar tu prueba gratuita
• Resolver cualquier duda

¿Me los compartes?"""
            parts.append(response)

        parts.append("")
        parts.append("=" * 50)

        return "\n".join(parts)

    def _get_recommended_product(self) -> Optional[Dict[str, Any]]:
        """Obtiene el producto recomendado según el cliente."""
        if self.client.industry:
            products = get_products_for_industry(self.client.industry)
            if products:
                return products[0]

        # Producto por defecto
        return PRODUCT_CATALOG.get("asistente_atencion_cliente")

    def _get_client_summary(self) -> str:
        """Genera resumen del cliente actual."""
        parts = ["", "[INFO] RESUMEN DEL CLIENTE ACTUAL:", ""]

        if self.client.industry:
            parts.append(f"   Industria: {self.client.industry}")
        else:
            parts.append("   Industria: No identificada aún")

        if self.client.business_size:
            parts.append(f"   Tamaño: {self.client.business_size}")

        if self.client.interests:
            parts.append(f"   Intereses: {', '.join(self.client.interests)}")

        if self.client.objections:
            parts.append(f"   Objeciones: {', '.join(self.client.objections)}")

        parts.append(f"   Fase actual: {self.current_phase.value}")
        parts.append(f"   Mensajes intercambiados: {len(self.conversation_history)}")

        recommended = self._get_recommended_product()
        if recommended:
            parts.append("")
            parts.append(f"   >> Producto recomendado: {recommended['nombre']}")
            parts.append(f"   $ Precio: {recommended['precio_base']}")

        return "\n".join(parts)

    def _get_products_list(self) -> str:
        """Muestra lista de productos disponibles."""
        parts = ["", "[PRODUCTO] CATÁLOGO DE PRODUCTOS:", ""]

        for pid, product in PRODUCT_CATALOG.items():
            parts.append(f"   {product['nombre']}")
            parts.append(f"   └── {product['precio_base']} | {product['tiempo_implementacion']}")
            parts.append("")

        return "\n".join(parts)

    def _get_product_price(self, query: str) -> str:
        """Busca precio de un producto específico."""
        query_lower = query.lower()

        for pid, product in PRODUCT_CATALOG.items():
            if query_lower in product['nombre'].lower() or query_lower in pid:
                return f"""
[PRODUCTO] {product['nombre']}

{product['descripcion']}

$ Precio: {product['precio_base']}
Tiempo: Implementación: {product['tiempo_implementacion']}

Beneficios:
{chr(10).join(['• ' + b for b in product['beneficios'][:3]])}
"""

        return f"No encontré un producto con '{query}'. Escribe /productos para ver el catálogo."

    def _generate_ai_response(self, user_input: str) -> str:
        """Genera respuesta usando la API de IA."""
        try:
            system_prompt = self._build_system_prompt()
            context = self._build_context_for_ai()

            # Construir historial reciente para contexto
            recent_history = ""
            if len(self.conversation_history) > 1:
                last_messages = self.conversation_history[-5:]  # Últimos 5 mensajes
                history_parts = []
                for msg in last_messages[:-1]:  # Excluir el actual
                    history_parts.append(f"- {msg['content'][:200]}")
                if history_parts:
                    recent_history = "\n\n## HISTORIAL RECIENTE\n" + "\n".join(history_parts)

            full_context = f"{context}{recent_history}\n\nVendedor: \"{user_input}\"\n\nResponde con un comentario corto + el mensaje para enviar (separado con ---)."

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_context}
            ]

            if self.api_provider == "openai":
                response = self.client_api.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    max_tokens=1500,
                    temperature=0.7
                )
                return response.choices[0].message.content

            elif self.api_provider == "anthropic":
                response = self.client_api.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=1500,
                    system=system_prompt,
                    messages=[{"role": "user", "content": full_context}]
                )
                return response.content[0].text

            elif self.api_provider == "gemini":
                full_prompt = f"{system_prompt}\n\n{full_context}"
                response = self.client_api.generate_content(full_prompt)
                return response.text

            elif self.api_provider == "groq":
                response = self.client_api.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    max_tokens=1500,
                    temperature=0.85  # Más creativo y variado
                )
                return response.choices[0].message.content

        except Exception as e:
            return f"Error con la API: {e}\n\n" + self._generate_demo_response(user_input)

    def _build_system_prompt(self) -> str:
        """Construye el prompt del sistema para el copiloto."""
        return """Eres Marcos, el mejor vendedor de agentes de IA. Ayudas a otros vendedores dándoles el mensaje exacto para enviar a sus clientes.

## TU ÚNICA TAREA

El vendedor te cuenta qué dice el cliente. Tú respondes SOLO con:
1. Un comentario corto tuyo (máximo 1-2 líneas, opcional)
2. El mensaje listo para copiar y enviar al cliente

EJEMPLO DE CÓMO RESPONDES:

Vendedor: "El cliente es abogado y dice que recibe muchas consultas"

Tú:
Perfecto, enganchalo con esto:

---
Entiendo perfectamente. Manejar tantas consultas puede ser agotador, especialmente cuando cada una requiere atencion personalizada.

Cuantas consultas dirias que recibes al dia aproximadamente? Te pregunto porque dependiendo del volumen, hay diferentes formas en que podriamos ayudarte.
---

## PRODUCTOS QORAX (precios en pesos colombianos)

- Atención 24/7: $250,000/mes
- Agente Ventas: $499,000/mes
- Agente RRHH: $399,000/mes
- Tutor IA: $349,000/mes
- Asistente Legal: $599,000/mes
- Asistente Médico: $699,000/mes
- Setup único: $1,500,000
- Prueba gratis: 14 días

## OBJECIONES COMUNES

"Caro" → Comparar con empleado ($1.5-2.5M/mes). Trabaja 24/7. Se paga solo en 3 meses.
"Lo pienso" → No presionar. Ofrecer info por correo + fecha seguimiento.
"No funciona" → 14 días gratis para probar. Garantía satisfacción.
"No tengo tiempo" → Nosotros hacemos todo. 2 semanas implementación.

## REGLAS

1. NUNCA uses formato de [ANÁLISIS] o [ESTRATEGIA] a menos que te lo pidan
2. Ve DIRECTO al mensaje para enviar
3. El mensaje debe sonar natural, como WhatsApp
4. Varía tus respuestas, no repitas lo mismo
5. Tu comentario previo debe ser breve y útil
6. Separa el mensaje con --- para que sea fácil de copiar
7. Adapta el tono según la industria del cliente"""

    def _build_context_for_ai(self) -> str:
        """Construye contexto para la IA."""
        parts = []

        # Info del cliente de forma natural
        client_info = []

        if self.client.industry:
            industry_names = {
                "legal": "abogado/despacho legal",
                "salud": "sector salud/médico",
                "educacion": "educación/academia",
                "retail": "comercio/tienda",
                "inmobiliaria": "inmobiliaria",
                "tecnologia": "tecnología/software",
                "finanzas": "finanzas/contabilidad",
                "gastronomia": "restaurante/gastronomía",
                "recursos_humanos": "recursos humanos"
            }
            client_info.append(f"es {industry_names.get(self.client.industry, self.client.industry)}")

        if self.client.business_size:
            client_info.append(f"negocio {self.client.business_size}")

        if self.client.interests:
            interest_map = {
                "atencion_cliente": "atención al cliente",
                "ventas": "ventas",
                "automatizacion": "automatización",
                "documentos": "gestión de documentos",
                "citas": "agendamiento de citas"
            }
            interests_readable = [interest_map.get(i, i) for i in self.client.interests]
            client_info.append(f"interesado en: {', '.join(interests_readable)}")

        if client_info:
            parts.append(f"Cliente: {', '.join(client_info)}")

        if self.client.objections:
            objection_map = {
                "precio": "le parece caro",
                "tiempo": "preocupado por el tiempo",
                "confianza": "tiene dudas si funciona",
                "indecision": "dice que lo va a pensar"
            }
            objs = [objection_map.get(o, o) for o in self.client.objections]
            parts.append(f"⚠️ Objeciones: {', '.join(objs)}")

        if len(self.conversation_history) > 3:
            parts.append(f"(Llevan {len(self.conversation_history)} mensajes)")

        return "\n".join(parts) if parts else "Cliente nuevo, primera interacción."

    def reset(self) -> None:
        """Reinicia para un nuevo cliente."""
        self.current_phase = SalePhase.INICIO
        self.client = ClientInfo()
        self.conversation_history = []

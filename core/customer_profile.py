"""Sistema de perfilamiento de clientes."""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class CustomerType(Enum):
    """Tipos de cliente."""
    UNKNOWN = "desconocido"
    STARTUP = "startup"
    PYME = "pyme"
    ENTERPRISE = "enterprise"
    FREELANCER = "freelancer"
    INDIVIDUAL = "individual"


class BuyingStage(Enum):
    """Etapa del proceso de compra."""
    AWARENESS = "conocimiento"          # Recién descubriendo que tiene un problema
    CONSIDERATION = "consideracion"      # Evaluando opciones
    DECISION = "decision"               # Listo para comprar
    RETENTION = "retencion"             # Cliente existente


class BudgetLevel(Enum):
    """Nivel de presupuesto."""
    UNKNOWN = "desconocido"
    LOW = "bajo"           # < $300/mes
    MEDIUM = "medio"       # $300-$700/mes
    HIGH = "alto"          # > $700/mes
    FLEXIBLE = "flexible"  # Sin límite definido


class Urgency(Enum):
    """Nivel de urgencia."""
    UNKNOWN = "desconocido"
    LOW = "baja"           # Solo explorando
    MEDIUM = "media"       # Tiene interés pero no prisa
    HIGH = "alta"          # Necesita solución pronto
    CRITICAL = "critica"   # Necesita solución inmediata


@dataclass
class CustomerProfile:
    """Perfil del cliente durante la conversación."""

    # Información básica
    name: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    # Clasificación
    customer_type: CustomerType = CustomerType.UNKNOWN
    industry: Optional[str] = None
    company_size: Optional[str] = None

    # Estado de compra
    buying_stage: BuyingStage = BuyingStage.AWARENESS
    budget_level: BudgetLevel = BudgetLevel.UNKNOWN
    urgency: Urgency = Urgency.UNKNOWN

    # Necesidades detectadas
    pain_points: List[str] = field(default_factory=list)
    needs: List[str] = field(default_factory=list)
    interests: List[str] = field(default_factory=list)

    # Objeciones y preocupaciones
    objections: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)

    # Productos de interés
    interested_products: List[str] = field(default_factory=list)

    # Historial de interacción
    questions_asked: List[str] = field(default_factory=list)
    topics_discussed: List[str] = field(default_factory=list)

    # Métricas
    engagement_score: float = 0.0  # 0-100
    qualification_score: float = 0.0  # 0-100

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el perfil a diccionario."""
        return {
            "name": self.name,
            "company": self.company,
            "role": self.role,
            "email": self.email,
            "phone": self.phone,
            "customer_type": self.customer_type.value,
            "industry": self.industry,
            "company_size": self.company_size,
            "buying_stage": self.buying_stage.value,
            "budget_level": self.budget_level.value,
            "urgency": self.urgency.value,
            "pain_points": self.pain_points,
            "needs": self.needs,
            "interests": self.interests,
            "objections": self.objections,
            "concerns": self.concerns,
            "interested_products": self.interested_products,
            "engagement_score": self.engagement_score,
            "qualification_score": self.qualification_score
        }

    def get_summary(self) -> str:
        """Obtiene un resumen del perfil."""
        parts = []

        if self.name:
            parts.append(f"Nombre: {self.name}")
        if self.company:
            parts.append(f"Empresa: {self.company}")
        if self.industry:
            parts.append(f"Industria: {self.industry}")
        if self.customer_type != CustomerType.UNKNOWN:
            parts.append(f"Tipo: {self.customer_type.value}")
        if self.buying_stage:
            parts.append(f"Etapa: {self.buying_stage.value}")
        if self.pain_points:
            parts.append(f"Problemas: {', '.join(self.pain_points[:3])}")
        if self.interested_products:
            parts.append(f"Intereses: {', '.join(self.interested_products[:3])}")

        return " | ".join(parts) if parts else "Perfil sin información"


class CustomerProfiler:
    """Analiza y actualiza el perfil del cliente basado en la conversación."""

    # Palabras clave para detectar tipo de cliente
    STARTUP_KEYWORDS = ["startup", "emprendimiento", "nueva empresa", "recién iniciando", "lanzamiento"]
    PYME_KEYWORDS = ["pyme", "pequeña empresa", "mediana empresa", "negocio familiar", "local"]
    ENTERPRISE_KEYWORDS = ["corporativo", "multinacional", "enterprise", "gran empresa", "corporación"]
    FREELANCER_KEYWORDS = ["freelance", "independiente", "consultor", "autónomo", "por cuenta propia"]

    # Palabras clave para detectar industria
    INDUSTRY_KEYWORDS = {
        "retail": ["tienda", "comercio", "retail", "ventas", "ecommerce", "e-commerce"],
        "salud": ["médico", "clínica", "hospital", "salud", "pacientes", "consultorio"],
        "educacion": ["educación", "escuela", "universidad", "cursos", "estudiantes", "academia"],
        "legal": ["abogado", "legal", "jurídico", "notaría", "despacho"],
        "tecnologia": ["software", "tecnología", "tech", "desarrollo", "app", "saas"],
        "finanzas": ["banco", "finanzas", "financiero", "crédito", "inversión"],
        "inmobiliaria": ["inmobiliaria", "bienes raíces", "propiedades", "rentas"],
        "recursos_humanos": ["rrhh", "recursos humanos", "empleados", "personal", "talento"],
        "gastronomia": ["restaurante", "comida", "cocina", "chef", "menú", "gastronomía", "food"],
        "cafeteria": ["cafetería", "cafeteria", "café", "cafe", "coffee", "panadería", "pastelería"]
    }

    # Palabras clave para detectar urgencia
    URGENCY_HIGH_KEYWORDS = ["urgente", "inmediato", "ahora", "lo antes posible", "cuanto antes", "rápido"]
    URGENCY_MEDIUM_KEYWORDS = ["pronto", "próximamente", "este mes", "en breve"]
    URGENCY_LOW_KEYWORDS = ["explorando", "investigando", "más adelante", "no hay prisa", "futuro"]

    # Palabras clave para detectar objeciones
    OBJECTION_KEYWORDS = {
        "precio": ["caro", "costoso", "presupuesto", "económico", "precio", "dinero", "inversión"],
        "tiempo": ["tiempo", "implementación", "demora", "rápido", "cuánto tarda"],
        "confianza": ["seguro", "garantía", "funciona", "resultados", "prueba"],
        "tecnico": ["técnico", "integración", "compatible", "complicado", "difícil"],
        "competencia": ["competencia", "otros", "alternativas", "diferencia"]
    }

    def __init__(self):
        self.profile = CustomerProfile()

    def analyze_message(self, message: str) -> CustomerProfile:
        """Analiza un mensaje y actualiza el perfil."""
        message_lower = message.lower()

        # Detectar tipo de cliente
        self._detect_customer_type(message_lower)

        # Detectar industria
        self._detect_industry(message_lower)

        # Detectar urgencia
        self._detect_urgency(message_lower)

        # Detectar objeciones
        self._detect_objections(message_lower)

        # Actualizar engagement
        self._update_engagement(message)

        # Actualizar qualification score
        self._update_qualification()

        return self.profile

    def _detect_customer_type(self, message: str):
        """Detecta el tipo de cliente."""
        if any(kw in message for kw in self.STARTUP_KEYWORDS):
            self.profile.customer_type = CustomerType.STARTUP
        elif any(kw in message for kw in self.ENTERPRISE_KEYWORDS):
            self.profile.customer_type = CustomerType.ENTERPRISE
        elif any(kw in message for kw in self.PYME_KEYWORDS):
            self.profile.customer_type = CustomerType.PYME
        elif any(kw in message for kw in self.FREELANCER_KEYWORDS):
            self.profile.customer_type = CustomerType.FREELANCER

    def _detect_industry(self, message: str):
        """Detecta la industria del cliente."""
        for industry, keywords in self.INDUSTRY_KEYWORDS.items():
            if any(kw in message for kw in keywords):
                self.profile.industry = industry
                break

    def _detect_urgency(self, message: str):
        """Detecta el nivel de urgencia."""
        if any(kw in message for kw in self.URGENCY_HIGH_KEYWORDS):
            self.profile.urgency = Urgency.HIGH
        elif any(kw in message for kw in self.URGENCY_MEDIUM_KEYWORDS):
            self.profile.urgency = Urgency.MEDIUM
        elif any(kw in message for kw in self.URGENCY_LOW_KEYWORDS):
            self.profile.urgency = Urgency.LOW

    def _detect_objections(self, message: str):
        """Detecta objeciones del cliente."""
        for objection_type, keywords in self.OBJECTION_KEYWORDS.items():
            if any(kw in message for kw in keywords):
                if objection_type not in self.profile.objections:
                    self.profile.objections.append(objection_type)

    def _update_engagement(self, message: str):
        """Actualiza el score de engagement."""
        # Más palabras = más engagement
        word_count = len(message.split())

        # Preguntas = más engagement
        question_count = message.count("?")

        # Calcular incremento
        increment = min(word_count * 0.5 + question_count * 5, 10)

        self.profile.engagement_score = min(
            self.profile.engagement_score + increment,
            100
        )

    def _update_qualification(self):
        """Actualiza el score de calificación."""
        score = 0

        # Tipo de cliente conocido
        if self.profile.customer_type != CustomerType.UNKNOWN:
            score += 15

        # Industria conocida
        if self.profile.industry:
            score += 15

        # Urgencia alta
        if self.profile.urgency in [Urgency.HIGH, Urgency.CRITICAL]:
            score += 20
        elif self.profile.urgency == Urgency.MEDIUM:
            score += 10

        # Datos de contacto
        if self.profile.name:
            score += 10
        if self.profile.email:
            score += 15
        if self.profile.phone:
            score += 10

        # Engagement alto
        if self.profile.engagement_score > 50:
            score += 15

        self.profile.qualification_score = min(score, 100)

    def update_profile(self, **kwargs):
        """Actualiza campos específicos del perfil."""
        for key, value in kwargs.items():
            if hasattr(self.profile, key):
                setattr(self.profile, key, value)

        self._update_qualification()

    def add_pain_point(self, pain_point: str):
        """Agrega un punto de dolor."""
        if pain_point not in self.profile.pain_points:
            self.profile.pain_points.append(pain_point)

    def add_interest(self, product_id: str):
        """Agrega un producto de interés."""
        if product_id not in self.profile.interested_products:
            self.profile.interested_products.append(product_id)

    def get_profile(self) -> CustomerProfile:
        """Obtiene el perfil actual."""
        return self.profile

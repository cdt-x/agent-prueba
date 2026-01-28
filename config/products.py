"""Catálogo de productos y servicios de agentes de IA."""

from typing import Dict, List, Any

PRODUCT_CATALOG: Dict[str, Dict[str, Any]] = {
    "asistente_atencion_cliente": {
        "nombre": "Agente de Atención al Cliente 24/7",
        "descripcion": "Agente de IA que atiende consultas de clientes las 24 horas, los 7 días de la semana",
        "beneficios": [
            "Disponibilidad total sin costos de personal nocturno",
            "Respuestas instantáneas a preguntas frecuentes",
            "Escalamiento inteligente a agentes humanos cuando es necesario",
            "Soporte multiidioma automático",
            "Reducción del 70% en tiempos de espera"
        ],
        "casos_uso": [
            "E-commerce y tiendas online",
            "Servicios financieros",
            "Telecomunicaciones",
            "Salud y bienestar",
            "Educación online"
        ],
        "precio_base": "Desde $299/mes",
        "tiempo_implementacion": "1-2 semanas"
    },

    "asistente_ventas": {
        "nombre": "Agente de Ventas Inteligente",
        "descripcion": "Agente especializado en calificar leads, presentar productos y cerrar ventas",
        "beneficios": [
            "Calificación automática de prospectos 24/7",
            "Seguimiento persistente sin ser invasivo",
            "Personalización de ofertas según el perfil del cliente",
            "Integración con CRM existente",
            "Aumento promedio del 40% en conversiones"
        ],
        "casos_uso": [
            "Inmobiliarias",
            "Concesionarios de autos",
            "Software y SaaS",
            "Servicios profesionales",
            "Retail y comercio"
        ],
        "precio_base": "Desde $499/mes",
        "tiempo_implementacion": "2-3 semanas"
    },

    "asistente_rrhh": {
        "nombre": "Agente de Recursos Humanos",
        "descripcion": "Agente para automatizar procesos de RRHH y atención a empleados",
        "beneficios": [
            "Respuestas automáticas sobre políticas y beneficios",
            "Gestión de solicitudes de vacaciones y permisos",
            "Onboarding automatizado de nuevos empleados",
            "Encuestas de clima laboral inteligentes",
            "Reducción del 60% en consultas repetitivas al área de RRHH"
        ],
        "casos_uso": [
            "Empresas medianas y grandes",
            "Startups en crecimiento",
            "Multinacionales",
            "Empresas con trabajo remoto"
        ],
        "precio_base": "Desde $399/mes",
        "tiempo_implementacion": "2-3 semanas"
    },

    "asistente_educativo": {
        "nombre": "Tutor IA Personalizado",
        "descripcion": "Agente educativo que adapta el aprendizaje al ritmo de cada estudiante",
        "beneficios": [
            "Aprendizaje adaptativo según el nivel del estudiante",
            "Disponibilidad 24/7 para resolver dudas",
            "Generación automática de ejercicios y evaluaciones",
            "Seguimiento del progreso en tiempo real",
            "Motivación y gamificación del aprendizaje"
        ],
        "casos_uso": [
            "Instituciones educativas",
            "Plataformas de e-learning",
            "Capacitación corporativa",
            "Academias y cursos online"
        ],
        "precio_base": "Desde $349/mes",
        "tiempo_implementacion": "2-4 semanas"
    },

    "asistente_legal": {
        "nombre": "Asistente Legal IA",
        "descripcion": "Agente especializado en consultas legales básicas y gestión documental",
        "beneficios": [
            "Respuestas rápidas a consultas legales frecuentes",
            "Generación de documentos legales básicos",
            "Organización y búsqueda inteligente de documentos",
            "Alertas de vencimientos y plazos",
            "Reducción de horas administrativas en un 50%"
        ],
        "casos_uso": [
            "Despachos de abogados",
            "Departamentos legales corporativos",
            "Notarías",
            "Consultoras legales"
        ],
        "precio_base": "Desde $599/mes",
        "tiempo_implementacion": "3-4 semanas"
    },

    "asistente_medico": {
        "nombre": "Asistente Médico IA",
        "descripcion": "Agente para triaje inicial, citas y seguimiento de pacientes",
        "beneficios": [
            "Triaje inicial automatizado 24/7",
            "Gestión inteligente de citas médicas",
            "Recordatorios de medicamentos y tratamientos",
            "Seguimiento post-consulta automatizado",
            "Reducción del 40% en llamadas a recepción"
        ],
        "casos_uso": [
            "Clínicas y consultorios",
            "Hospitales",
            "Farmacias",
            "Telemedicina"
        ],
        "precio_base": "Desde $699/mes",
        "tiempo_implementacion": "3-5 semanas"
    },

    "agente_personalizado": {
        "nombre": "Agente IA Personalizado",
        "descripcion": "Desarrollo a medida de un agente adaptado 100% a tus necesidades específicas",
        "beneficios": [
            "Diseño completamente personalizado",
            "Integración con cualquier sistema existente",
            "Entrenamiento con tus datos específicos",
            "Soporte y mantenimiento dedicado",
            "Escalabilidad según tu crecimiento"
        ],
        "casos_uso": [
            "Cualquier industria",
            "Procesos únicos de negocio",
            "Integraciones complejas",
            "Requerimientos especiales"
        ],
        "precio_base": "Cotización personalizada",
        "tiempo_implementacion": "4-8 semanas"
    }
}


INDUSTRY_SOLUTIONS: Dict[str, List[str]] = {
    "retail": ["asistente_atencion_cliente", "asistente_ventas"],
    "salud": ["asistente_medico", "asistente_atencion_cliente"],
    "educacion": ["asistente_educativo", "asistente_atencion_cliente"],
    "legal": ["asistente_legal", "asistente_atencion_cliente"],
    "tecnologia": ["asistente_ventas", "asistente_atencion_cliente", "asistente_rrhh"],
    "finanzas": ["asistente_atencion_cliente", "asistente_ventas"],
    "inmobiliaria": ["asistente_ventas", "asistente_atencion_cliente"],
    "recursos_humanos": ["asistente_rrhh"],
    "otro": ["agente_personalizado", "asistente_atencion_cliente"]
}


def get_product_by_id(product_id: str) -> Dict[str, Any]:
    """Obtiene un producto por su ID."""
    return PRODUCT_CATALOG.get(product_id, {})


def get_products_for_industry(industry: str) -> List[Dict[str, Any]]:
    """Obtiene productos recomendados para una industria."""
    product_ids = INDUSTRY_SOLUTIONS.get(industry.lower(), INDUSTRY_SOLUTIONS["otro"])
    return [PRODUCT_CATALOG[pid] for pid in product_ids if pid in PRODUCT_CATALOG]


def get_all_products() -> Dict[str, Dict[str, Any]]:
    """Obtiene todos los productos."""
    return PRODUCT_CATALOG

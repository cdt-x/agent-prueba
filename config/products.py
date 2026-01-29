"""Catálogo de productos y servicios de QORAX - Agentes de IA."""

from typing import Dict, List, Any

# Configuración de la empresa
EMPRESA = {
    "nombre": "Qorax",
    "slogan": "Agentes de IA que atienden tu negocio 24/7",
    "pais": "Colombia",
    "moneda": "COP",
    "setup_base": "$1,500,000 COP",
    "mensualidad_base": "$250,000 COP/mes"
}

PRODUCT_CATALOG: Dict[str, Dict[str, Any]] = {
    "agente_whatsapp": {
        "nombre": "Agente WhatsApp 24/7",
        "descripcion": "Agente de IA que responde tu WhatsApp automaticamente las 24 horas",
        "beneficios": [
            "Responde clientes en segundos, incluso a las 3am",
            "Agenda citas automaticamente",
            "Responde preguntas frecuentes sin cansarse",
            "Tu negocio nunca duerme",
            "Cuesta menos que un almuerzo diario"
        ],
        "casos_uso": [
            "Doctores y clinicas",
            "Abogados",
            "Restaurantes",
            "Tiendas",
            "Cualquier negocio"
        ],
        "precio_setup": "$1,500,000 COP",
        "precio_mensual": "$250,000 COP/mes",
        "precio_base": "$1,500,000 + $250,000/mes",
        "tiempo_implementacion": "5-7 dias"
    },

    "agente_basico": {
        "nombre": "Agente Basico",
        "descripcion": "Agente para responder preguntas frecuentes y dar informacion",
        "beneficios": [
            "Responde preguntas frecuentes 24/7",
            "Da informacion de precios y servicios",
            "Facil de configurar",
            "Ideal para empezar",
            "El mas economico"
        ],
        "casos_uso": [
            "Negocios pequenos",
            "Emprendedores",
            "Profesionales independientes"
        ],
        "precio_setup": "$997,000 COP",
        "precio_mensual": "$197,000 COP/mes",
        "precio_base": "$997,000 + $197,000/mes",
        "tiempo_implementacion": "3-5 dias"
    },

    "agente_ventas": {
        "nombre": "Agente de Ventas",
        "descripcion": "Agente especializado en calificar clientes y cerrar ventas",
        "beneficios": [
            "Califica clientes automaticamente",
            "Hace seguimiento sin ser invasivo",
            "Envia cotizaciones",
            "Agenda reuniones de cierre",
            "Aumenta tus ventas mientras duermes"
        ],
        "casos_uso": [
            "Inmobiliarias",
            "Concesionarios",
            "Servicios profesionales",
            "Cualquier negocio B2B"
        ],
        "precio_setup": "$1,800,000 COP",
        "precio_mensual": "$350,000 COP/mes",
        "precio_base": "$1,800,000 + $350,000/mes",
        "tiempo_implementacion": "7-10 dias"
    },

    "agente_citas": {
        "nombre": "Agente de Citas",
        "descripcion": "Agente especializado en agendar y gestionar citas",
        "beneficios": [
            "Agenda citas 24/7 sin errores",
            "Envia recordatorios automaticos",
            "Permite reagendar facilmente",
            "Se conecta con tu calendario",
            "Reduce las citas perdidas en 80%"
        ],
        "casos_uso": [
            "Doctores y clinicas",
            "Dentistas",
            "Abogados",
            "Salones de belleza",
            "Cualquier negocio con citas"
        ],
        "precio_setup": "$1,500,000 COP",
        "precio_mensual": "$280,000 COP/mes",
        "precio_base": "$1,500,000 + $280,000/mes",
        "tiempo_implementacion": "5-7 dias"
    },

    "agente_personalizado": {
        "nombre": "Agente Personalizado",
        "descripcion": "Desarrollo a medida para necesidades especificas",
        "beneficios": [
            "Disenado 100% para tu negocio",
            "Integraciones especiales",
            "Flujos personalizados",
            "Soporte dedicado",
            "Escalable segun crezcas"
        ],
        "casos_uso": [
            "Empresas medianas",
            "Necesidades especiales",
            "Integraciones complejas"
        ],
        "precio_setup": "Desde $2,500,000 COP",
        "precio_mensual": "Desde $400,000 COP/mes",
        "precio_base": "Cotizacion personalizada",
        "tiempo_implementacion": "10-15 dias"
    }
}


INDUSTRY_SOLUTIONS: Dict[str, List[str]] = {
    "retail": ["agente_whatsapp", "agente_ventas"],
    "salud": ["agente_citas", "agente_whatsapp"],
    "educacion": ["agente_whatsapp", "agente_basico"],
    "legal": ["agente_citas", "agente_whatsapp"],
    "tecnologia": ["agente_ventas", "agente_whatsapp"],
    "finanzas": ["agente_whatsapp", "agente_ventas"],
    "inmobiliaria": ["agente_ventas", "agente_whatsapp"],
    "recursos_humanos": ["agente_whatsapp", "agente_basico"],
    "gastronomia": ["agente_whatsapp", "agente_basico"],
    "otro": ["agente_whatsapp", "agente_personalizado"]
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

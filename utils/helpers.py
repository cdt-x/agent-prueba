"""Funciones de utilidad."""

import re
from typing import Optional


def clean_text(text: str) -> str:
    """Limpia y normaliza texto."""
    # Eliminar espacios múltiples
    text = re.sub(r'\s+', ' ', text)
    # Eliminar espacios al inicio y final
    text = text.strip()
    return text


def extract_email(text: str) -> Optional[str]:
    """Extrae un email del texto."""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(pattern, text)
    return match.group(0) if match else None


def extract_phone(text: str) -> Optional[str]:
    """Extrae un número de teléfono del texto."""
    # Patrón para números de teléfono (varios formatos)
    patterns = [
        r'\+?[\d\s\-\(\)]{10,}',  # Formato internacional
        r'\d{3}[\s\-]?\d{3}[\s\-]?\d{4}',  # Formato US/México
        r'\d{2}[\s\-]?\d{4}[\s\-]?\d{4}',  # Formato alternativo
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return clean_phone(match.group(0))

    return None


def clean_phone(phone: str) -> str:
    """Limpia un número de teléfono."""
    # Mantener solo dígitos y el signo +
    cleaned = re.sub(r'[^\d+]', '', phone)
    return cleaned


def extract_name(text: str) -> Optional[str]:
    """Intenta extraer un nombre del texto."""
    # Patrones comunes para nombres
    patterns = [
        r'(?:me llamo|soy|mi nombre es)\s+([A-Za-záéíóúñÁÉÍÓÚÑ]+(?:\s+[A-Za-záéíóúñÁÉÍÓÚÑ]+)?)',
        r'([A-Za-záéíóúñÁÉÍÓÚÑ]+(?:\s+[A-Za-záéíóúñÁÉÍÓÚÑ]+)?)\s+(?:aquí|aqui)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip().title()

    return None


def format_currency(amount: float, currency: str = "USD") -> str:
    """Formatea un monto como moneda."""
    symbols = {
        "USD": "$",
        "EUR": "€",
        "MXN": "$",
        "COP": "$",
    }
    symbol = symbols.get(currency, "$")
    return f"{symbol}{amount:,.2f}"


def calculate_roi(monthly_cost: float, equivalent_salary: float, months: int = 12) -> dict:
    """Calcula el ROI de la solución."""
    yearly_cost = monthly_cost * months
    yearly_salary = equivalent_salary * months
    savings = yearly_salary - yearly_cost
    roi_percentage = (savings / yearly_cost) * 100 if yearly_cost > 0 else 0

    return {
        "yearly_cost": yearly_cost,
        "yearly_salary_equivalent": yearly_salary,
        "annual_savings": savings,
        "roi_percentage": roi_percentage,
        "payback_months": monthly_cost / (equivalent_salary - monthly_cost) if equivalent_salary > monthly_cost else 0
    }


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Trunca texto a una longitud máxima."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

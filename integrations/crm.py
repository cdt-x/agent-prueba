"""Integración con sistemas CRM."""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import json
import os


class CRMIntegration(ABC):
    """Clase base para integraciones con CRM."""

    @abstractmethod
    def create_lead(self, data: Dict[str, Any]) -> str:
        """Crea un nuevo lead en el CRM."""
        pass

    @abstractmethod
    def update_lead(self, lead_id: str, data: Dict[str, Any]) -> bool:
        """Actualiza un lead existente."""
        pass

    @abstractmethod
    def add_note(self, lead_id: str, note: str) -> bool:
        """Agrega una nota a un lead."""
        pass


class LocalCRM(CRMIntegration):
    """CRM local basado en archivos JSON (para desarrollo/demo)."""

    def __init__(self, storage_path: str = "data/leads.json"):
        self.storage_path = storage_path
        self.leads: Dict[str, Dict[str, Any]] = {}
        self._load_data()

    def _load_data(self):
        """Carga datos existentes."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    self.leads = json.load(f)
            except Exception:
                self.leads = {}

    def _save_data(self):
        """Guarda datos."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.leads, f, indent=2, ensure_ascii=False)

    def create_lead(self, data: Dict[str, Any]) -> str:
        """Crea un nuevo lead."""
        import uuid
        lead_id = str(uuid.uuid4())[:8]

        self.leads[lead_id] = {
            "id": lead_id,
            "status": "new",
            "notes": [],
            **data
        }

        self._save_data()
        return lead_id

    def update_lead(self, lead_id: str, data: Dict[str, Any]) -> bool:
        """Actualiza un lead."""
        if lead_id not in self.leads:
            return False

        self.leads[lead_id].update(data)
        self._save_data()
        return True

    def add_note(self, lead_id: str, note: str) -> bool:
        """Agrega una nota."""
        if lead_id not in self.leads:
            return False

        from datetime import datetime
        self.leads[lead_id]["notes"].append({
            "timestamp": datetime.now().isoformat(),
            "content": note
        })
        self._save_data()
        return True

    def get_lead(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un lead por ID."""
        return self.leads.get(lead_id)

    def get_all_leads(self) -> Dict[str, Dict[str, Any]]:
        """Obtiene todos los leads."""
        return self.leads

    def search_leads(self, query: str) -> list:
        """Busca leads."""
        results = []
        query_lower = query.lower()

        for lead in self.leads.values():
            if (query_lower in str(lead.get("name", "")).lower() or
                query_lower in str(lead.get("email", "")).lower() or
                query_lower in str(lead.get("company", "")).lower()):
                results.append(lead)

        return results


class HubSpotCRM(CRMIntegration):
    """Integración con HubSpot CRM."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("HUBSPOT_API_KEY")
        self.base_url = "https://api.hubapi.com"

    def create_lead(self, data: Dict[str, Any]) -> str:
        """Crea un contacto en HubSpot."""
        if not self.api_key:
            raise ValueError("HubSpot API key not configured")

        # Mapear campos al formato de HubSpot
        properties = {
            "email": data.get("email"),
            "firstname": data.get("name", "").split()[0] if data.get("name") else "",
            "lastname": " ".join(data.get("name", "").split()[1:]) if data.get("name") else "",
            "company": data.get("company"),
            "phone": data.get("phone"),
            "hs_lead_status": "NEW"
        }

        # Aquí iría la llamada real a la API
        # response = requests.post(...)
        # return response.json()["id"]

        return "hubspot_placeholder_id"

    def update_lead(self, lead_id: str, data: Dict[str, Any]) -> bool:
        """Actualiza un contacto en HubSpot."""
        if not self.api_key:
            return False

        # Implementación real iría aquí
        return True

    def add_note(self, lead_id: str, note: str) -> bool:
        """Agrega una nota a un contacto en HubSpot."""
        if not self.api_key:
            return False

        # Implementación real iría aquí
        return True


class SalesforceCRM(CRMIntegration):
    """Integración con Salesforce."""

    def __init__(self, credentials: Optional[Dict[str, str]] = None):
        self.credentials = credentials or {
            "username": os.getenv("SALESFORCE_USERNAME"),
            "password": os.getenv("SALESFORCE_PASSWORD"),
            "security_token": os.getenv("SALESFORCE_TOKEN")
        }

    def create_lead(self, data: Dict[str, Any]) -> str:
        """Crea un lead en Salesforce."""
        # Implementación real iría aquí
        return "salesforce_placeholder_id"

    def update_lead(self, lead_id: str, data: Dict[str, Any]) -> bool:
        """Actualiza un lead en Salesforce."""
        return True

    def add_note(self, lead_id: str, note: str) -> bool:
        """Agrega una nota en Salesforce."""
        return True


def get_crm(crm_type: str = "local") -> CRMIntegration:
    """Factory para obtener la integración CRM correcta."""
    crm_map = {
        "local": LocalCRM,
        "hubspot": HubSpotCRM,
        "salesforce": SalesforceCRM
    }

    crm_class = crm_map.get(crm_type.lower(), LocalCRM)
    return crm_class()

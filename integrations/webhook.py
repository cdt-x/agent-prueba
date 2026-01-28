"""Sistema de webhooks para integraciones externas."""

from typing import Dict, Any, Callable, List, Optional
import json
import os
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class WebhookEvent:
    """Representa un evento de webhook."""
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }


class WebhookHandler:
    """Maneja webhooks entrantes y salientes."""

    # Tipos de eventos soportados
    EVENT_TYPES = [
        "conversation.started",
        "conversation.ended",
        "lead.created",
        "lead.qualified",
        "message.received",
        "message.sent",
        "objection.detected",
        "demo.requested"
    ]

    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {event: [] for event in self.EVENT_TYPES}
        self.webhook_urls: Dict[str, List[str]] = {event: [] for event in self.EVENT_TYPES}
        self.event_log: List[WebhookEvent] = []

    def subscribe(self, event_type: str, callback: Callable):
        """Suscribe una función a un tipo de evento."""
        if event_type not in self.EVENT_TYPES:
            raise ValueError(f"Tipo de evento no soportado: {event_type}")

        self.subscribers[event_type].append(callback)

    def register_webhook_url(self, event_type: str, url: str):
        """Registra una URL para recibir webhooks."""
        if event_type not in self.EVENT_TYPES:
            raise ValueError(f"Tipo de evento no soportado: {event_type}")

        if url not in self.webhook_urls[event_type]:
            self.webhook_urls[event_type].append(url)

    def emit(self, event_type: str, data: Dict[str, Any]):
        """Emite un evento."""
        if event_type not in self.EVENT_TYPES:
            return

        event = WebhookEvent(event_type=event_type, data=data)
        self.event_log.append(event)

        # Llamar suscriptores locales
        for callback in self.subscribers[event_type]:
            try:
                callback(event)
            except Exception as e:
                print(f"[WEBHOOK ERROR] Callback error: {e}")

        # Enviar a URLs registradas
        self._send_to_urls(event_type, event)

    def _send_to_urls(self, event_type: str, event: WebhookEvent):
        """Envía el evento a las URLs registradas."""
        urls = self.webhook_urls.get(event_type, [])

        for url in urls:
            try:
                # En producción, esto usaría requests
                # response = requests.post(url, json=event.to_dict(), timeout=5)
                print(f"[WEBHOOK] Enviando {event_type} a {url}")
            except Exception as e:
                print(f"[WEBHOOK ERROR] Error enviando a {url}: {e}")

    def get_event_log(self, event_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtiene el log de eventos."""
        events = self.event_log

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        return [e.to_dict() for e in events[-limit:]]


# Instancia global
webhook_handler = WebhookHandler()


# Funciones de conveniencia para emitir eventos comunes
def emit_conversation_started(session_id: str, metadata: Dict[str, Any] = None):
    """Emite evento de conversación iniciada."""
    webhook_handler.emit("conversation.started", {
        "session_id": session_id,
        "metadata": metadata or {}
    })


def emit_conversation_ended(session_id: str, summary: Dict[str, Any]):
    """Emite evento de conversación finalizada."""
    webhook_handler.emit("conversation.ended", {
        "session_id": session_id,
        "summary": summary
    })


def emit_lead_created(lead_data: Dict[str, Any]):
    """Emite evento de lead creado."""
    webhook_handler.emit("lead.created", lead_data)


def emit_lead_qualified(lead_id: str, qualification_score: float, profile: Dict[str, Any]):
    """Emite evento de lead calificado."""
    webhook_handler.emit("lead.qualified", {
        "lead_id": lead_id,
        "qualification_score": qualification_score,
        "profile": profile
    })


def emit_objection_detected(objection_type: str, context: str):
    """Emite evento de objeción detectada."""
    webhook_handler.emit("objection.detected", {
        "objection_type": objection_type,
        "context": context
    })


def emit_demo_requested(lead_data: Dict[str, Any]):
    """Emite evento de demo solicitada."""
    webhook_handler.emit("demo.requested", lead_data)

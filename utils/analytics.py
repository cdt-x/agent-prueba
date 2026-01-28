"""Sistema de analytics para conversaciones."""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import os


@dataclass
class ConversationMetrics:
    """Métricas de una conversación."""
    conversation_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_turns: int = 0
    final_phase: str = "greeting"
    customer_type: str = "unknown"
    industry: str = "unknown"
    engagement_score: float = 0.0
    qualification_score: float = 0.0
    outcome: str = "unknown"  # converted, follow_up, lost, unknown
    products_discussed: List[str] = field(default_factory=list)
    objections_raised: List[str] = field(default_factory=list)
    contact_captured: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario."""
        return {
            "conversation_id": self.conversation_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": (self.end_time - self.start_time).seconds if self.end_time else 0,
            "total_turns": self.total_turns,
            "final_phase": self.final_phase,
            "customer_type": self.customer_type,
            "industry": self.industry,
            "engagement_score": self.engagement_score,
            "qualification_score": self.qualification_score,
            "outcome": self.outcome,
            "products_discussed": self.products_discussed,
            "objections_raised": self.objections_raised,
            "contact_captured": self.contact_captured
        }


class ConversationAnalytics:
    """Gestiona analytics de conversaciones."""

    def __init__(self, storage_path: str = "data/analytics.json"):
        self.storage_path = storage_path
        self.conversations: List[ConversationMetrics] = []
        self.current_session: Optional[ConversationMetrics] = None
        self._load_data()

    def _load_data(self):
        """Carga datos históricos."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convertir a objetos (simplificado, no reconstituye objetos completos)
                    self.conversations = []
            except Exception:
                self.conversations = []

    def _save_data(self):
        """Guarda datos."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            data = [c.to_dict() for c in self.conversations]
            json.dump(data, f, indent=2, ensure_ascii=False)

    def start_session(self, conversation_id: str) -> ConversationMetrics:
        """Inicia una nueva sesión de analytics."""
        self.current_session = ConversationMetrics(
            conversation_id=conversation_id,
            start_time=datetime.now()
        )
        return self.current_session

    def end_session(self, outcome: str = "unknown"):
        """Finaliza la sesión actual."""
        if self.current_session:
            self.current_session.end_time = datetime.now()
            self.current_session.outcome = outcome
            self.conversations.append(self.current_session)
            self._save_data()
            self.current_session = None

    def update_session(self, **kwargs):
        """Actualiza métricas de la sesión actual."""
        if self.current_session:
            for key, value in kwargs.items():
                if hasattr(self.current_session, key):
                    setattr(self.current_session, key, value)

    def record_turn(self):
        """Registra un turno de conversación."""
        if self.current_session:
            self.current_session.total_turns += 1

    def record_product_discussed(self, product_id: str):
        """Registra un producto discutido."""
        if self.current_session and product_id not in self.current_session.products_discussed:
            self.current_session.products_discussed.append(product_id)

    def record_objection(self, objection_type: str):
        """Registra una objeción."""
        if self.current_session and objection_type not in self.current_session.objections_raised:
            self.current_session.objections_raised.append(objection_type)

    def get_summary_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas resumen."""
        if not self.conversations:
            return {"message": "No hay datos de conversaciones"}

        total = len(self.conversations)
        converted = sum(1 for c in self.conversations if c.outcome == "converted")
        follow_ups = sum(1 for c in self.conversations if c.outcome == "follow_up")

        avg_turns = sum(c.total_turns for c in self.conversations) / total
        avg_engagement = sum(c.engagement_score for c in self.conversations) / total
        avg_qualification = sum(c.qualification_score for c in self.conversations) / total

        # Industrias más comunes
        industries = {}
        for c in self.conversations:
            industries[c.industry] = industries.get(c.industry, 0) + 1

        # Objeciones más comunes
        objections = {}
        for c in self.conversations:
            for obj in c.objections_raised:
                objections[obj] = objections.get(obj, 0) + 1

        return {
            "total_conversations": total,
            "conversion_rate": (converted / total) * 100 if total > 0 else 0,
            "follow_up_rate": (follow_ups / total) * 100 if total > 0 else 0,
            "avg_turns_per_conversation": avg_turns,
            "avg_engagement_score": avg_engagement,
            "avg_qualification_score": avg_qualification,
            "top_industries": sorted(industries.items(), key=lambda x: x[1], reverse=True)[:5],
            "common_objections": sorted(objections.items(), key=lambda x: x[1], reverse=True)[:5],
            "contacts_captured": sum(1 for c in self.conversations if c.contact_captured)
        }

    def get_conversion_funnel(self) -> Dict[str, int]:
        """Obtiene el embudo de conversión."""
        phases = {
            "saludo": 0,
            "descubrimiento": 0,
            "calificacion": 0,
            "presentacion": 0,
            "objeciones": 0,
            "cierre": 0,
            "seguimiento": 0
        }

        for c in self.conversations:
            phase = c.final_phase
            if phase in phases:
                # Incrementar esta fase y todas las anteriores
                phase_order = list(phases.keys())
                phase_index = phase_order.index(phase)
                for i in range(phase_index + 1):
                    phases[phase_order[i]] += 1

        return phases

import os
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseModel):
    """Configuración del agente vendedor."""

    # APIs
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None

    # Configuración del agente
    agent_name: str = "FUTURE"
    company_name: str = "IAgentic Solutions"
    agent_language: str = "es"

    # Configuración de ventas
    max_conversation_turns: int = 50
    enable_analytics: bool = True

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    """Obtiene la configuración desde variables de entorno."""
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        groq_api_key=os.getenv("GROQ_API_KEY"),
        agent_name=os.getenv("AGENT_NAME", "FUTURE"),
        company_name=os.getenv("COMPANY_NAME", "IAgentic Solutions"),
        agent_language=os.getenv("AGENT_LANGUAGE", "es"),
    )

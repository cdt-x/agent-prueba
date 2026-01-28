"""Sistema de notificaciones por email."""

from typing import Dict, Any, Optional, List
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass


@dataclass
class EmailConfig:
    """Configuración de email."""
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    username: str = ""
    password: str = ""
    from_email: str = ""
    from_name: str = "IAgentic Solutions"


class EmailNotifier:
    """Envía notificaciones por email."""

    def __init__(self, config: Optional[EmailConfig] = None):
        self.config = config or self._load_config()

    def _load_config(self) -> EmailConfig:
        """Carga configuración desde variables de entorno."""
        return EmailConfig(
            smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            username=os.getenv("SMTP_USERNAME", ""),
            password=os.getenv("SMTP_PASSWORD", ""),
            from_email=os.getenv("SMTP_FROM_EMAIL", ""),
            from_name=os.getenv("SMTP_FROM_NAME", "IAgentic Solutions")
        )

    def send_lead_notification(self, lead_data: Dict[str, Any], to_email: str) -> bool:
        """Envía notificación de nuevo lead al equipo de ventas."""
        subject = f"Nuevo Lead: {lead_data.get('name', 'Sin nombre')} - {lead_data.get('company', 'Sin empresa')}"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #667eea;">Nuevo Lead Capturado</h2>

            <div style="background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h3>Información del Cliente</h3>
                <p><strong>Nombre:</strong> {lead_data.get('name', 'No especificado')}</p>
                <p><strong>Empresa:</strong> {lead_data.get('company', 'No especificada')}</p>
                <p><strong>Email:</strong> {lead_data.get('email', 'No especificado')}</p>
                <p><strong>Teléfono:</strong> {lead_data.get('phone', 'No especificado')}</p>
                <p><strong>Industria:</strong> {lead_data.get('industry', 'No detectada')}</p>
            </div>

            <div style="background: #e8f4f8; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h3>Calificación</h3>
                <p><strong>Tipo de Cliente:</strong> {lead_data.get('customer_type', 'Desconocido')}</p>
                <p><strong>Urgencia:</strong> {lead_data.get('urgency', 'Desconocida')}</p>
                <p><strong>Score de Engagement:</strong> {lead_data.get('engagement_score', 0):.0f}%</p>
                <p><strong>Score de Calificación:</strong> {lead_data.get('qualification_score', 0):.0f}%</p>
            </div>

            <div style="background: #fff3e0; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h3>Intereses</h3>
                <p><strong>Productos de interés:</strong> {', '.join(lead_data.get('interested_products', ['No especificados']))}</p>
                <p><strong>Problemas mencionados:</strong> {', '.join(lead_data.get('pain_points', ['No especificados']))}</p>
            </div>

            <p style="color: #888; font-size: 12px; margin-top: 30px;">
                Este email fue generado automáticamente por el Agente Vendedor de IA.
            </p>
        </body>
        </html>
        """

        return self._send_email(to_email, subject, html_content)

    def send_follow_up_reminder(self, lead_data: Dict[str, Any], to_email: str) -> bool:
        """Envía recordatorio de seguimiento."""
        subject = f"Recordatorio: Seguimiento con {lead_data.get('name', 'Cliente')}"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #667eea;">Recordatorio de Seguimiento</h2>

            <p>Es momento de dar seguimiento al siguiente lead:</p>

            <div style="background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <p><strong>Nombre:</strong> {lead_data.get('name', 'No especificado')}</p>
                <p><strong>Empresa:</strong> {lead_data.get('company', 'No especificada')}</p>
                <p><strong>Contacto:</strong> {lead_data.get('email', lead_data.get('phone', 'No especificado'))}</p>
            </div>

            <p style="color: #888; font-size: 12px; margin-top: 30px;">
                Este email fue generado automáticamente por el Agente Vendedor de IA.
            </p>
        </body>
        </html>
        """

        return self._send_email(to_email, subject, html_content)

    def send_welcome_email(self, customer_email: str, customer_name: str) -> bool:
        """Envía email de bienvenida al cliente."""
        subject = f"¡Bienvenido a {self.config.from_name}!"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #667eea;">¡Hola {customer_name}!</h2>

            <p>Gracias por tu interés en nuestras soluciones de Inteligencia Artificial.</p>

            <p>Hemos recibido tu información y nuestro equipo se pondrá en contacto contigo muy pronto
            para agendar una demostración personalizada.</p>

            <div style="background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h3>Mientras tanto, te invitamos a:</h3>
                <ul>
                    <li>Explorar nuestro catálogo de soluciones</li>
                    <li>Leer casos de éxito de clientes</li>
                    <li>Agendar una llamada directamente</li>
                </ul>
            </div>

            <p>Si tienes alguna pregunta, no dudes en responder a este correo.</p>

            <p>¡Saludos cordiales!</p>
            <p><strong>El equipo de {self.config.from_name}</strong></p>
        </body>
        </html>
        """

        return self._send_email(customer_email, subject, html_content)

    def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Envía un email."""
        if not self.config.username or not self.config.password:
            print(f"[EMAIL] Simulando envío a {to_email}: {subject}")
            return True

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.config.from_name} <{self.config.from_email}>"
            msg['To'] = to_email

            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.username, self.config.password)
                server.send_message(msg)

            return True

        except Exception as e:
            print(f"[EMAIL ERROR] {str(e)}")
            return False

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QORAX VENTAS - Agente de Ventas con Panel de Control
"""

from flask import Flask, render_template_string, request, jsonify, redirect, send_from_directory
from dotenv import load_dotenv
from groq import Groq
from datetime import datetime
import os
import json
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading

load_dotenv()

# Configuracion de correo
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

def send_email_async(to_email, subject, body_html):
    """Envia correo en un hilo separado para no bloquear"""
    def send():
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"QORAX AI <{GMAIL_USER}>"
            msg['To'] = to_email

            html_part = MIMEText(body_html, 'html')
            msg.attach(html_part)

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(GMAIL_USER, GMAIL_PASSWORD)
                server.sendmail(GMAIL_USER, to_email, msg.as_string())
            print(f"[EMAIL] Correo enviado a {to_email}")
        except Exception as e:
            print(f"[EMAIL ERROR] {e}")

    thread = threading.Thread(target=send)
    thread.start()

def send_lead_notification(lead_data):
    """Envia notificacion al vendedor de nuevo lead"""
    subject = f"Nuevo Lead QORAX - {lead_data.get('email', 'Sin email')}"
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #667eea;">Nuevo Lead Capturado</h2>
        <table style="border-collapse: collapse; width: 100%; max-width: 400px;">
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Email:</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{lead_data.get('email', 'No proporcionado')}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Telefono:</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{lead_data.get('telefono', 'No proporcionado')}</td>
            </tr>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">Fecha:</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{datetime.now().strftime('%Y-%m-%d %H:%M')}</td>
            </tr>
        </table>
        <p style="margin-top: 20px;">
            <a href="http://localhost:5003/panel" style="background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Ver en Panel</a>
        </p>
    </body>
    </html>
    """
    send_email_async(GMAIL_USER, subject, body)

def detect_business_type(conversation):
    """Detecta el tipo de negocio del cliente basado SOLO en mensajes del usuario"""
    # Solo analizar mensajes del usuario, no del bot
    user_messages = [msg.get("content", "") for msg in conversation if msg.get("role") == "user"]
    text = " ".join(user_messages).lower()

    business_types = {
        "abogado": {
            "keywords": ["abogado", "legal", "juridico", "demanda", "caso", "bufete", "derecho", "despacho", "firma legal", "leyes"],
            "title": "Soluciones IA para Firmas Legales",
            "intro": "Optimiza la gestion de tu firma mientras te enfocas en lo que mejor haces: defender a tus clientes.",
            "benefits": [
                ("Atencion a Clientes 24/7", "Captura consultas legales y agenda citas aunque no estes disponible"),
                ("Seguimiento de Casos", "Mantiene a tus clientes informados sobre el estado de sus casos"),
                ("Filtro de Consultas", "Califica prospectos y filtra casos que no son de tu especialidad")
            ]
        },
        "doctor": {
            "keywords": ["doctor", "medico", "clinica", "hospital", "paciente", "consultorio", "salud", "medicina", "cita medica"],
            "title": "Soluciones IA para Profesionales de la Salud",
            "intro": "Entendemos que tu tiempo debe estar enfocado en tus pacientes, no en tareas administrativas.",
            "benefits": [
                ("Agendamiento Inteligente", "Tus pacientes reservan citas 24/7 sin saturar tu recepcion"),
                ("Recordatorios de Citas", "Reduce las inasistencias con confirmaciones automaticas"),
                ("Triaje Preliminar", "El agente recopila sintomas antes de la consulta para optimizar tu tiempo")
            ]
        },
        "mecanico": {
            "keywords": ["mecanico", "taller", "vehiculo", "motor", "frenos", "aceite", "llantas", "repuestos", "taller mecanico", "carros", "autos"],
            "title": "Soluciones IA para Talleres Mecanicos",
            "intro": "Sabemos lo importante que es optimizar cada minuto en tu taller.",
            "benefits": [
                ("Agente de Citas 24/7", "Tus clientes agendan servicios, cambios de aceite y revisiones sin que tengas que contestar llamadas"),
                ("Recordatorios Automaticos", "Notifica a tus clientes sobre mantenimientos pendientes y aumenta la retencion"),
                ("Cotizador Inteligente", "Responde consultas sobre precios de servicios comunes al instante")
            ]
        },
        "restaurante": {
            "keywords": ["restaurante", "comida", "menu", "reservacion", "cocina", "chef", "pedido", "delivery"],
            "title": "Soluciones IA para Restaurantes",
            "intro": "Lleva tu restaurante al siguiente nivel con atencion automatizada.",
            "benefits": [
                ("Reservaciones 24/7", "Acepta reservaciones por WhatsApp o web sin perder clientes"),
                ("Menu Digital Inteligente", "Responde preguntas sobre ingredientes, alergenos y recomendaciones"),
                ("Pedidos Automatizados", "Gestiona pedidos para delivery o pickup sin errores")
            ]
        },
        "inmobiliaria": {
            "keywords": ["inmobiliaria", "propiedad", "casa", "apartamento", "arriendo", "venta", "bienes raices", "inmueble"],
            "title": "Soluciones IA para Inmobiliarias",
            "intro": "Captura mas leads y cierra mas negocios con atencion inmediata.",
            "benefits": [
                ("Atencion Inmediata a Leads", "Responde consultas sobre propiedades 24/7 cuando el cliente esta interesado"),
                ("Calificacion de Prospectos", "Filtra compradores serios de curiosos automaticamente"),
                ("Agendamiento de Visitas", "Coordina visitas a propiedades sin ir y venir de mensajes")
            ]
        },
        "default": {
            "keywords": [],
            "title": "Soluciones IA para tu Negocio",
            "intro": "Estamos listos para ayudarte a transformar tu negocio con inteligencia artificial.",
            "benefits": [
                ("Atencion 24/7", "Tus clientes reciben respuestas inmediatas a cualquier hora"),
                ("Automatizacion de Ventas", "Captura leads y agenda reuniones mientras duermes"),
                ("Asistentes Especializados", "Soluciones adaptadas a tu industria especifica")
            ]
        }
    }

    for biz_type, data in business_types.items():
        if biz_type == "default":
            continue
        for keyword in data["keywords"]:
            if keyword in text:
                return data

    return business_types["default"]

def send_welcome_email(to_email, nombre_empresa, conversation=None):
    """Envia correo de bienvenida personalizado al cliente"""

    # Detectar tipo de negocio
    biz_info = detect_business_type(conversation or [])

    subject = f"{biz_info['title']} - {nombre_empresa}"

    # Generar beneficios HTML
    benefits_html = ""
    for title, desc in biz_info["benefits"]:
        benefits_html += f"""
                                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin-bottom: 18px;">
                                                <tr>
                                                    <td width="50" style="vertical-align: top;">
                                                        <div style="width: 40px; height: 40px; background: linear-gradient(135deg, rgba(212,175,55,0.2) 0%, rgba(212,175,55,0.1) 100%); border-radius: 10px; text-align: center; line-height: 40px; font-size: 18px;">&#10003;</div>
                                                    </td>
                                                    <td style="vertical-align: middle; padding-left: 15px;">
                                                        <p style="margin: 0; color: #ffffff; font-size: 15px; font-weight: 500;">{title}</p>
                                                        <p style="margin: 4px 0 0 0; color: #888; font-size: 13px;">{desc}</p>
                                                    </td>
                                                </tr>
                                            </table>"""

    body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%); min-height: 100vh;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);">
            <tr>
                <td align="center" style="padding: 40px 20px;">
                    <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="background: linear-gradient(145deg, #141428 0%, #1a1a2e 100%); border-radius: 24px; border: 1px solid rgba(212, 175, 55, 0.3); box-shadow: 0 20px 60px rgba(0,0,0,0.5);">

                        <!-- Header con Logo -->
                        <tr>
                            <td style="padding: 40px 40px 20px 40px; text-align: center; border-bottom: 1px solid rgba(212, 175, 55, 0.2);">
                                <h1 style="margin: 0; font-size: 32px; font-weight: 700; letter-spacing: 6px; background: linear-gradient(135deg, #f4d03f 0%, #d4af37 50%, #b8960c 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">QORAX</h1>
                                <p style="margin: 8px 0 0 0; color: #888; font-size: 12px; letter-spacing: 2px; text-transform: uppercase;">Inteligencia Artificial para tu Negocio</p>
                            </td>
                        </tr>

                        <!-- Contenido Principal -->
                        <tr>
                            <td style="padding: 40px;">
                                <h2 style="margin: 0 0 20px 0; color: #ffffff; font-size: 28px; font-weight: 600;">Hola!</h2>
                                <p style="margin: 0 0 15px 0; color: #c0c0c0; font-size: 16px; line-height: 1.7;">
                                    Gracias por tu interes en <strong style="color: #d4af37;">{nombre_empresa}</strong>.
                                </p>
                                <p style="margin: 0 0 30px 0; color: #c0c0c0; font-size: 16px; line-height: 1.7;">
                                    {biz_info["intro"]}
                                </p>

                                <!-- Servicios Personalizados -->
                                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background: rgba(255,255,255,0.03); border-radius: 16px; border: 1px solid rgba(212, 175, 55, 0.15); margin: 30px 0;">
                                    <tr>
                                        <td style="padding: 30px;">
                                            <h3 style="margin: 0 0 25px 0; color: #d4af37; font-size: 18px; font-weight: 600; letter-spacing: 1px;">Como podemos ayudarte</h3>
                                            {benefits_html}
                                        </td>
                                    </tr>
                                </table>

                                <!-- Mensaje final -->
                                <p style="margin: 30px 0 0 0; color: #c0c0c0; font-size: 15px; line-height: 1.7;">
                                    Mientras tanto, si tienes alguna pregunta, puedes responder directamente a este correo.
                                </p>

                                <!-- Boton CTA -->
                                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin-top: 35px;">
                                    <tr>
                                        <td align="center">
                                            <a href="https://qorax.ai" style="display: inline-block; padding: 16px 40px; background: linear-gradient(135deg, #d4af37 0%, #b8960c 100%); color: #0a0a0a; text-decoration: none; font-weight: 600; font-size: 15px; border-radius: 30px; letter-spacing: 1px; box-shadow: 0 8px 25px rgba(212,175,55,0.3);">Conoce mas sobre QORAX</a>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td style="padding: 30px 40px; border-top: 1px solid rgba(212, 175, 55, 0.15); text-align: center;">
                                <p style="margin: 0 0 10px 0; color: #666; font-size: 13px;">
                                    <span style="color: #d4af37;">QORAX AI</span> - Transformamos negocios con Inteligencia Artificial
                                </p>
                                <p style="margin: 0; color: #555; font-size: 11px;">
                                    Este es un mensaje automatico. Si no solicitaste informacion, puedes ignorar este correo.
                                </p>
                            </td>
                        </tr>

                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    send_email_async(to_email, subject, body)

app = Flask(__name__, static_folder='static', static_url_path='/static')
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Base de datos simple en memoria (se puede cambiar a archivo/DB)
DATABASE = {
    "leads": [],
    "conversations": {},
    "config": {
        "nombre_empresa": "QORAX",
        "tipo_negocio": "agentes de IA",
        "servicios": "automatizacion de atencion al cliente, ventas, soporte",
        "horario": "24/7"
    }
}

# Archivo para persistir datos
DATA_FILE = "qorax_leads.json"

def load_data():
    global DATABASE
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                DATABASE = json.load(f)
    except:
        pass

def save_data():
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(DATABASE, f, ensure_ascii=False, indent=2)
    except:
        pass

load_data()

def extract_contact_info(text, conversation_id):
    """Extrae email y telefono del texto"""
    # Buscar email
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)

    # Buscar telefono (varios formatos)
    phone_pattern = r'(?:\+?57)?[\s.-]?(?:\d{3}[\s.-]?\d{3}[\s.-]?\d{4}|\d{10}|\d{7})'
    phones = re.findall(phone_pattern, text.replace(' ', ''))

    # Si encontramos datos, actualizar el lead
    if emails or phones:
        for lead in DATABASE["leads"]:
            if lead["conversation_id"] == conversation_id:
                email_is_new = emails and not lead.get("email")
                phone_is_new = phones and not lead.get("telefono")

                if email_is_new:
                    lead["email"] = emails[0]
                    # Enviar correo de bienvenida personalizado al cliente
                    conv = DATABASE.get("conversations", {}).get(conversation_id, [])
                    send_welcome_email(emails[0], DATABASE["config"]["nombre_empresa"], conv)
                    # Notificar al vendedor
                    send_lead_notification(lead)
                    print(f"[LEAD] Nuevo email capturado: {emails[0]}")

                if phone_is_new:
                    lead["telefono"] = phones[0]
                    # Si solo hay telefono (sin email previo), notificar
                    if not lead.get("email"):
                        send_lead_notification(lead)
                    print(f"[LEAD] Nuevo telefono capturado: {phones[0]}")

                lead["updated_at"] = datetime.now().isoformat()
                save_data()
                break

def get_agent_prompt(config, mode="asistente"):
    return f"""Eres el asistente virtual de {config['nombre_empresa']}.

PERSONALIDAD: Amable, profesional, eficiente y servicial. Respuestas claras y naturales.

EMPRESA: {config['nombre_empresa']}
SERVICIOS: {config['servicios']}
HORARIO: {config['horario']}

NUESTROS AGENTES DE IA:
- Agente de Atencion 24/7: Atencion automatizada para clientes
- Agente de Ventas: Automatiza ventas y captura leads
- Agente RRHH: Gestion de recursos humanos
- Asistente Legal: Consultas legales y jurisprudencia
- Asistente Medico: Orientacion medica y citas

TU TRABAJO:
- Responder preguntas sobre la empresa y servicios
- Explicar como nuestros agentes de IA pueden ayudar al cliente
- Ser util y resolver dudas
- Cuando el cliente muestre interes, pedirle su correo y telefono de forma natural

IMPORTANTE:
- NUNCA menciones a "Carlos" ni a ningun vendedor
- Tu eres el unico asistente, no transfieras a nadie
- Si piden precios, di que un asesor los contactara con la info
- Para contactarlos, pide su correo: "Para enviarte mas informacion, me compartes tu correo?"
- Responde en espanol, maximo 2-3 oraciones"""


# ==================== PAGINAS HTML ====================

CLIENTE_PAGE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Orbitron:wght@400;500;600;700&display=swap" rel="stylesheet">
    <title>{{ empresa }} - Agentes de IA</title>
    <style>
        :root {
            --gold: #d4af37;
            --gold-light: #f4d03f;
            --gold-dark: #b8960c;
            --bg-dark: #0a0a0a;
            --glass: rgba(255, 255, 255, 0.05);
            --glass-border: rgba(255, 255, 255, 0.1);
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html, body {
            height: 100%;
            overflow: hidden;
        }
        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg-dark);
            background-image: url('/static/qorax_logo.jpg');
            background-size: cover;
            background-position: center;
            color: #fff;
        }
        body::before {
            content: '';
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: linear-gradient(135deg, rgba(0,0,0,0.92) 0%, rgba(10,10,10,0.95) 100%);
            z-index: 0;
        }

        .main-container {
            position: relative;
            z-index: 1;
            height: 100vh;
            display: grid;
            grid-template-columns: 1fr 420px;
            grid-template-rows: auto 1fr auto;
            gap: 0;
        }

        /* Header */
        .header {
            grid-column: 1 / -1;
            background: rgba(10, 10, 10, 0.9);
            backdrop-filter: blur(20px);
            padding: 12px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--glass-border);
        }
        .header h1 {
            font-family: 'Orbitron', sans-serif;
            font-size: 1.3rem;
            background: linear-gradient(135deg, var(--gold-light), var(--gold));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 3px;
        }
        .header-subtitle {
            color: #888;
            font-size: 0.85rem;
        }

        /* Left Panel - Services */
        .services-panel {
            padding: 25px 30px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
        }
        .services-panel::-webkit-scrollbar { width: 4px; }
        .services-panel::-webkit-scrollbar-thumb { background: var(--gold); border-radius: 2px; }

        .welcome-text {
            margin-bottom: 25px;
        }
        .welcome-text h2 {
            font-family: 'Orbitron', sans-serif;
            font-size: 1.6rem;
            background: linear-gradient(135deg, #fff 0%, var(--gold) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }
        .welcome-text p {
            color: #a0a0a0;
            font-size: 0.95rem;
            line-height: 1.5;
        }

        .services-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            flex: 1;
        }
        .service-card {
            background: var(--glass);
            backdrop-filter: blur(10px);
            padding: 20px 15px;
            border-radius: 16px;
            border: 1px solid var(--glass-border);
            text-align: center;
            transition: all 0.3s ease;
        }
        .service-card:hover {
            border-color: rgba(212, 175, 55, 0.4);
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }
        .service-icon { font-size: 2rem; margin-bottom: 10px; }
        .service-card h3 {
            font-family: 'Orbitron', sans-serif;
            color: var(--gold);
            font-size: 0.8rem;
            margin-bottom: 6px;
            letter-spacing: 1px;
        }
        .service-card p {
            color: #888;
            font-size: 0.75rem;
            line-height: 1.4;
        }

        /* Right Panel - Chat */
        .chat-panel {
            background: rgba(15, 15, 15, 0.95);
            border-left: 1px solid var(--glass-border);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            min-height: 0;
        }
        .chat-header {
            background: linear-gradient(135deg, rgba(212, 175, 55, 0.15), rgba(20, 20, 20, 0.9));
            padding: 18px 20px;
            text-align: center;
            border-bottom: 1px solid rgba(212, 175, 55, 0.2);
            flex-shrink: 0;
        }
        .chat-header h2 {
            font-family: 'Orbitron', sans-serif;
            color: var(--gold);
            font-size: 1rem;
            margin-bottom: 4px;
            letter-spacing: 2px;
        }
        .chat-header p { color: #888; font-size: 0.8rem; }
        .status-dot {
            display: inline-block;
            width: 8px; height: 8px;
            background: #22c55e;
            border-radius: 50%;
            margin-right: 6px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }

        .chat-messages {
            flex: 1;
            overflow-y: auto;
            overflow-x: hidden;
            padding: 15px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            background: rgba(10, 10, 10, 0.5);
            min-height: 0;
        }
        .chat-messages::-webkit-scrollbar { width: 4px; }
        .chat-messages::-webkit-scrollbar-thumb { background: var(--gold); border-radius: 2px; }

        .message {
            max-width: 85%;
            padding: 12px 15px;
            border-radius: 16px;
            font-size: 0.9rem;
            line-height: 1.4;
            animation: slideIn 0.3s ease;
        }
        @keyframes slideIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .message.bot {
            background: rgba(255, 255, 255, 0.1);
            color: #e0e0e0;
            align-self: flex-start;
            border-bottom-left-radius: 4px;
        }
        .message.user {
            background: linear-gradient(135deg, var(--gold), var(--gold-dark));
            color: var(--bg-dark);
            align-self: flex-end;
            border-bottom-right-radius: 4px;
            font-weight: 500;
        }
        .typing { display: flex; gap: 4px; padding: 12px 15px; background: rgba(255,255,255,0.1); border-radius: 16px; align-self: flex-start; }
        .typing span { width: 6px; height: 6px; background: var(--gold); border-radius: 50%; animation: bounce 1.4s infinite; }
        .typing span:nth-child(1) { animation-delay: -0.32s; }
        .typing span:nth-child(2) { animation-delay: -0.16s; }
        @keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }

        .chat-input {
            padding: 15px;
            background: rgba(20, 20, 20, 0.95);
            display: flex;
            gap: 10px;
            border-top: 1px solid var(--glass-border);
            flex-shrink: 0;
        }
        .chat-input input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid rgba(212, 175, 55, 0.3);
            border-radius: 20px;
            font-size: 0.9rem;
            outline: none;
            background: rgba(255, 255, 255, 0.05);
            color: #fff;
        }
        .chat-input input:focus { border-color: var(--gold); }
        .chat-input button {
            padding: 12px 24px;
            background: linear-gradient(135deg, var(--gold), var(--gold-dark));
            color: var(--bg-dark);
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.3s;
        }
        .chat-input button:hover { transform: scale(1.03); }

        /* Footer */
        .footer {
            grid-column: 1 / -1;
            text-align: center;
            padding: 10px;
            color: #555;
            font-size: 0.75rem;
            background: rgba(10, 10, 10, 0.9);
            border-top: 1px solid var(--glass-border);
        }
        .footer span { color: var(--gold); }

        /* Responsive */
        @media (max-width: 900px) {
            .main-container {
                grid-template-columns: 1fr;
                grid-template-rows: auto 1fr auto;
            }
            .services-panel { display: none; }
            .chat-panel { border-left: none; }
        }
    </style>
</head>
<body>
    <div class="main-container">
        <header class="header">
            <div>
                <h1>QORAX</h1>
            </div>
            <span class="header-subtitle">Inteligencia Artificial para tu Negocio</span>
        </header>

        <div class="services-panel">
            <div class="welcome-text">
                <h2>Bienvenido a {{ empresa }}</h2>
                <p>Transformamos tu negocio con agentes de IA que trabajan 24/7</p>
            </div>
            <div class="services-grid">
                <div class="service-card">
                    <div class="service-icon">🤖</div>
                    <h3>Atencion 24/7</h3>
                    <p>Atencion automatizada las 24 horas</p>
                </div>
                <div class="service-card">
                    <div class="service-icon">💼</div>
                    <h3>Agente Ventas</h3>
                    <p>Automatiza ventas y captura leads</p>
                </div>
                <div class="service-card">
                    <div class="service-icon">👥</div>
                    <h3>Agente RRHH</h3>
                    <p>Gestion de recursos humanos</p>
                </div>
                <div class="service-card">
                    <div class="service-icon">⚖️</div>
                    <h3>Asistente Legal</h3>
                    <p>Consultas y analisis juridico</p>
                </div>
                <div class="service-card">
                    <div class="service-icon">🏥</div>
                    <h3>Asistente Medico</h3>
                    <p>Orientacion y gestion de citas</p>
                </div>
                <div class="service-card">
                    <div class="service-icon">🔧</div>
                    <h3>Personalizado</h3>
                    <p>Agentes para tu industria</p>
                </div>
            </div>
        </div>

        <div class="chat-panel">
            <div class="chat-header">
                <h2>Asistente QORAX</h2>
                <p><span class="status-dot"></span>En linea</p>
            </div>
            <div class="chat-messages" id="messages">
                <div class="message bot">Hola! Soy el asistente de {{ empresa }}. Cuentame, ¿a que te dedicas y como puedo ayudarte?</div>
            </div>
            <div class="chat-input">
                <input type="text" id="userInput" placeholder="Escribe tu mensaje..." onkeypress="if(event.key==='Enter')sendMessage()">
                <button onclick="sendMessage()" id="sendBtn">Enviar</button>
            </div>
        </div>

        <footer class="footer">
            Powered by <span>QORAX AI</span>
        </footer>
    </div>

    <script>
        const convId = '{{ conv_id }}';
        let mode = 'asistente';

        function addMessage(text, type) {
            const div = document.createElement('div');
            div.className = 'message ' + type;
            div.textContent = text;
            document.getElementById('messages').appendChild(div);
            document.getElementById('messages').scrollTop = 99999;
        }

        function showTyping() {
            const div = document.createElement('div');
            div.className = 'typing';
            div.id = 'typing';
            div.innerHTML = '<span></span><span></span><span></span>';
            document.getElementById('messages').appendChild(div);
            document.getElementById('messages').scrollTop = 99999;
        }

        async function sendMessage() {
            const input = document.getElementById('userInput');
            const text = input.value.trim();
            if (!text) return;

            addMessage(text, 'user');
            input.value = '';
            document.getElementById('sendBtn').disabled = true;
            showTyping();

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: text, conversation_id: convId})
                });
                const data = await res.json();
                document.getElementById('typing')?.remove();

                if (data.mode !== mode) {
                    mode = data.mode;
                    if (mode === 'vendedor') {
                        document.getElementById('agentStatus').innerHTML =
                            '<span class="status-dot" style="background:#f59e0b"></span>Carlos - Ventas';
                    }
                }

                addMessage(data.response, 'bot');
            } catch(e) {
                document.getElementById('typing')?.remove();
                addMessage('Error de conexion. Intenta de nuevo.', 'bot');
            }
            document.getElementById('sendBtn').disabled = false;
        }
    </script>
</body>
</html>
"""

PANEL_PAGE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Orbitron:wght@400;500;600;700&display=swap" rel="stylesheet">
    <title>QORAX - Panel de Ventas</title>
    <style>
        :root {
            --gold: #d4af37;
            --gold-light: #f4d03f;
            --gold-dark: #b8960c;
            --bg-dark: #0a0a0a;
            --bg-card: rgba(20, 20, 20, 0.8);
            --glass: rgba(255, 255, 255, 0.05);
            --glass-border: rgba(255, 255, 255, 0.1);
            --text-primary: #ffffff;
            --text-secondary: #a0a0a0;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg-dark);
            background-image: url('/static/qorax_logo.jpg');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
        }
        body::before {
            content: '';
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: linear-gradient(135deg, rgba(0,0,0,0.9) 0%, rgba(10,10,10,0.95) 50%, rgba(0,0,0,0.9) 100%);
            z-index: 0;
        }
        body::after {
            content: '';
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background:
                radial-gradient(ellipse at 20% 20%, rgba(212, 175, 55, 0.1) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 80%, rgba(212, 175, 55, 0.05) 0%, transparent 50%);
            z-index: 0;
            pointer-events: none;
        }
        .navbar, .container { position: relative; z-index: 1; }

        /* Navbar Glassmorphism */
        .navbar {
            background: rgba(10, 10, 10, 0.8);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            padding: 20px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--glass-border);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .navbar h1 {
            font-family: 'Orbitron', sans-serif;
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--gold-light) 0%, var(--gold) 50%, var(--gold-dark) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 4px;
            text-transform: uppercase;
        }
        .nav-links { display: flex; gap: 10px; align-items: center; }
        .navbar a {
            color: var(--text-secondary);
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 12px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid transparent;
            font-weight: 500;
        }
        .navbar a:hover {
            background: rgba(212, 175, 55, 0.15);
            color: var(--gold);
            border-color: rgba(212, 175, 55, 0.3);
            transform: translateY(-2px);
        }
        .refresh-btn {
            background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dark) 100%);
            color: var(--bg-dark);
            border: none;
            padding: 12px 24px;
            border-radius: 12px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
        }
        .refresh-btn:hover {
            transform: translateY(-2px) scale(1.02);
            box-shadow: 0 8px 25px rgba(212, 175, 55, 0.4);
        }

        .container { max-width: 1400px; margin: 0 auto; padding: 40px; }

        /* Hero Banner */
        .hero-banner {
            background: linear-gradient(135deg, rgba(212, 175, 55, 0.1) 0%, rgba(20, 20, 20, 0.9) 100%);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(212, 175, 55, 0.2);
            border-radius: 24px;
            padding: 60px 40px;
            text-align: center;
            margin-bottom: 50px;
            position: relative;
            overflow: hidden;
        }
        .hero-banner::before {
            content: '';
            position: absolute;
            top: 0; left: -100%;
            width: 200%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.1), transparent);
            animation: heroShine 3s ease-in-out infinite;
        }
        @keyframes heroShine {
            0% { left: -100%; }
            100% { left: 100%; }
        }
        .hero-banner h2 {
            font-family: 'Orbitron', sans-serif;
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #fff 0%, var(--gold) 50%, var(--gold-light) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 15px;
            position: relative;
            letter-spacing: 2px;
        }
        .hero-banner p {
            font-size: 1.2rem;
            color: var(--text-secondary);
            position: relative;
            max-width: 600px;
            margin: 0 auto;
        }

        /* Stats Grid */
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 24px;
            margin-bottom: 50px;
        }
        .stat-card {
            background: var(--glass);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 20px;
            border: 1px solid var(--glass-border);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 3px;
            background: linear-gradient(90deg, var(--gold), var(--gold-light), var(--gold));
            opacity: 0;
            transition: opacity 0.3s;
        }
        .stat-card:hover {
            transform: translateY(-8px);
            border-color: rgba(212, 175, 55, 0.3);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3), 0 0 30px rgba(212, 175, 55, 0.1);
        }
        .stat-card:hover::before { opacity: 1; }
        .stat-card h3 {
            color: var(--text-secondary);
            font-size: 0.85rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 12px;
        }
        .stat-card .number {
            font-family: 'Orbitron', sans-serif;
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--gold-light), var(--gold));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* Section Title */
        .section-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 2px solid rgba(212, 175, 55, 0.2);
            color: var(--text-primary);
            letter-spacing: 2px;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .section-title::before {
            content: '';
            width: 4px;
            height: 24px;
            background: linear-gradient(180deg, var(--gold), var(--gold-dark));
            border-radius: 2px;
        }

        /* Services Grid */
        .services-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 20px;
            margin-bottom: 50px;
        }
        .service-card {
            background: var(--glass);
            backdrop-filter: blur(10px);
            padding: 35px 25px;
            border-radius: 20px;
            border: 1px solid var(--glass-border);
            text-align: center;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        .service-card::after {
            content: '';
            position: absolute;
            bottom: 0; left: 0;
            width: 100%; height: 0;
            background: linear-gradient(180deg, transparent, rgba(212, 175, 55, 0.1));
            transition: height 0.4s;
        }
        .service-card:hover {
            transform: translateY(-10px) scale(1.02);
            border-color: rgba(212, 175, 55, 0.4);
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4), 0 0 40px rgba(212, 175, 55, 0.15);
        }
        .service-card:hover::after { height: 100%; }
        .service-icon {
            font-size: 3rem;
            margin-bottom: 20px;
            display: block;
            position: relative;
            z-index: 1;
            filter: drop-shadow(0 0 10px rgba(212, 175, 55, 0.3));
        }
        .service-card h3 {
            font-family: 'Orbitron', sans-serif;
            color: var(--gold);
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 12px;
            position: relative;
            z-index: 1;
            letter-spacing: 1px;
        }
        .service-card p {
            color: var(--text-secondary);
            font-size: 0.9rem;
            line-height: 1.6;
            position: relative;
            z-index: 1;
        }

        /* Table */
        .leads-table {
            background: var(--glass);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            overflow: hidden;
            border: 1px solid var(--glass-border);
        }
        table { width: 100%; border-collapse: collapse; }
        th, td {
            padding: 18px 24px;
            text-align: left;
            border-bottom: 1px solid var(--glass-border);
        }
        th {
            background: rgba(212, 175, 55, 0.1);
            font-family: 'Orbitron', sans-serif;
            font-weight: 600;
            color: var(--gold);
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        tr { transition: all 0.3s; }
        tr:hover { background: rgba(212, 175, 55, 0.05); }

        /* Buttons */
        .btn {
            padding: 10px 18px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 0.85rem;
            font-weight: 500;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .btn-secondary {
            background: rgba(255, 255, 255, 0.1);
            color: var(--text-primary);
            border: 1px solid var(--glass-border);
        }
        .btn-secondary:hover {
            background: rgba(212, 175, 55, 0.2);
            color: var(--gold);
            transform: scale(1.05);
        }
        .btn-whatsapp {
            background: linear-gradient(135deg, #25d366 0%, #128c7e 100%);
            color: white;
            text-decoration: none;
            margin-left: 8px;
        }
        .btn-whatsapp:hover { transform: scale(1.05); box-shadow: 0 5px 15px rgba(37, 211, 102, 0.3); }
        .btn-email {
            background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dark) 100%);
            color: var(--bg-dark);
            text-decoration: none;
            margin-left: 8px;
            font-weight: 600;
        }
        .btn-email:hover { transform: scale(1.05); box-shadow: 0 5px 15px rgba(212, 175, 55, 0.3); }

        .conversation-preview {
            max-width: 280px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            color: var(--text-secondary);
            font-size: 0.85rem;
        }

        .empty-state {
            text-align: center;
            padding: 80px 20px;
            color: var(--text-secondary);
        }
        .empty-state h3 {
            font-family: 'Orbitron', sans-serif;
            margin-bottom: 15px;
            color: var(--text-primary);
            font-size: 1.3rem;
        }
        .chat-link {
            display: inline-block;
            margin-top: 25px;
            padding: 15px 35px;
            background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dark) 100%);
            color: var(--bg-dark);
            text-decoration: none;
            border-radius: 12px;
            font-weight: 600;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 5px 20px rgba(212, 175, 55, 0.3);
        }
        .chat-link:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(212, 175, 55, 0.4);
        }

        /* Animations */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .hero-banner { animation: fadeInUp 0.8s ease-out; }
        .stat-card { animation: fadeInUp 0.8s ease-out backwards; }
        .stat-card:nth-child(1) { animation-delay: 0.1s; }
        .stat-card:nth-child(2) { animation-delay: 0.2s; }
        .stat-card:nth-child(3) { animation-delay: 0.3s; }
        .stat-card:nth-child(4) { animation-delay: 0.4s; }
        .service-card { animation: fadeInUp 0.8s ease-out backwards; }
        .service-card:nth-child(1) { animation-delay: 0.2s; }
        .service-card:nth-child(2) { animation-delay: 0.3s; }
        .service-card:nth-child(3) { animation-delay: 0.4s; }
        .service-card:nth-child(4) { animation-delay: 0.5s; }
        .service-card:nth-child(5) { animation-delay: 0.6s; }
    </style>
</head>
<body>
    <nav class="navbar">
        <h1>QORAX</h1>
        <div class="nav-links">
            <a href="/chat" target="_blank">Abrir Chat</a>
            <button class="refresh-btn" onclick="location.reload()">Actualizar Panel</button>
        </div>
    </nav>

    <div class="container">
        <div class="stats">
            <div class="stat-card">
                <h3>Total Leads</h3>
                <div class="number">{{ total_leads }}</div>
            </div>
            <div class="stat-card">
                <h3>Con Email</h3>
                <div class="number">{{ leads_con_email }}</div>
            </div>
            <div class="stat-card">
                <h3>Con Telefono</h3>
                <div class="number">{{ leads_con_telefono }}</div>
            </div>
            <div class="stat-card">
                <h3>Hoy</h3>
                <div class="number">{{ leads_hoy }}</div>
            </div>
        </div>

        <!-- Banner Principal -->
        <div class="hero-banner">
            <h2>Todo lo que necesitas en Agentes de IA</h2>
            <p>Automatiza, escala y transforma tu negocio con inteligencia artificial</p>
        </div>

        <!-- Seccion de Servicios -->
        <h2 class="section-title">Nuestros Agentes</h2>
        <div class="services-grid">
            <div class="service-card">
                <div class="service-icon">🤖</div>
                <h3>Agente Atencion 24/7</h3>
                <p>Atencion automatizada para tus clientes las 24 horas, todos los dias</p>
            </div>
            <div class="service-card">
                <div class="service-icon">💼</div>
                <h3>Agente de Ventas</h3>
                <p>Automatiza tu proceso de ventas y captura leads calificados</p>
            </div>
            <div class="service-card">
                <div class="service-icon">👥</div>
                <h3>Agente RRHH</h3>
                <p>Gestion automatizada de recursos humanos y reclutamiento</p>
            </div>
            <div class="service-card">
                <div class="service-icon">⚖️</div>
                <h3>Asistente Legal</h3>
                <p>Consultas legales, contratos y analisis de jurisprudencia</p>
            </div>
            <div class="service-card">
                <div class="service-icon">🏥</div>
                <h3>Asistente Medico</h3>
                <p>Orientacion medica, triaje y gestion de citas</p>
            </div>
        </div>

        <h2 class="section-title" style="margin-top: 40px;">Leads Capturados</h2>

        <div class="leads-table">
            {% if leads %}
            <table>
                <thead>
                    <tr>
                        <th>Fecha</th>
                        <th>Nombre</th>
                        <th>Email</th>
                        <th>Telefono</th>
                        <th>Ultimo mensaje</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    {% for lead in leads %}
                    <tr>
                        <td>{{ lead.fecha }}</td>
                        <td>{{ lead.nombre or 'Sin nombre' }}</td>
                        <td>{{ lead.email or '-' }}</td>
                        <td>{{ lead.telefono or '-' }}</td>
                        <td class="conversation-preview">{{ lead.ultimo_mensaje or '-' }}</td>
                        <td>
                            <button class="btn btn-secondary" onclick="verConversacion('{{ lead.conversation_id }}')">Ver chat</button>
                            {% if lead.telefono and lead.telefono != '-' %}
                            <a href="https://wa.me/57{{ lead.telefono }}" target="_blank" class="btn btn-whatsapp" style="margin-left:5px;">WhatsApp</a>
                            {% endif %}
                            {% if lead.email and lead.email != '-' %}
                            <a href="mailto:{{ lead.email }}" class="btn btn-email" style="margin-left:5px;">Email</a>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <div class="empty-state">
                <h3>No hay leads aun</h3>
                <p>Cuando los clientes chateen con el agente, sus datos apareceran aqui.</p>
                <a href="/chat" target="_blank" class="chat-link">Abrir Chat del Cliente</a>
            </div>
            {% endif %}
        </div>
    </div>

    <script>
        function verConversacion(id) {
            window.open('/conversacion/' + id, '_blank', 'width=500,height=600');
        }

        // Auto-refresh cada 30 segundos
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>
"""

CONVERSACION_PAGE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Conversacion - {{ conv_id }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; padding: 20px; }
        h2 { margin-bottom: 20px; font-size: 1.1rem; color: #94a3b8; }
        .messages { display: flex; flex-direction: column; gap: 10px; }
        .msg { padding: 12px 16px; border-radius: 12px; max-width: 85%; font-size: 0.9rem; }
        .msg.user { background: #667eea; align-self: flex-end; }
        .msg.assistant { background: #334155; align-self: flex-start; }
        .info { background: #1e293b; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
        .info p { margin: 5px 0; font-size: 0.9rem; }
        .info strong { color: #667eea; }
    </style>
</head>
<body>
    <div class="info">
        <p><strong>Email:</strong> {{ lead.email or 'No proporcionado' }}</p>
        <p><strong>Telefono:</strong> {{ lead.telefono or 'No proporcionado' }}</p>
        <p><strong>Fecha:</strong> {{ lead.fecha }}</p>
    </div>
    <h2>Conversacion</h2>
    <div class="messages">
        {% for msg in messages %}
        <div class="msg {{ msg.role }}">{{ msg.content }}</div>
        {% endfor %}
    </div>
</body>
</html>
"""

# ==================== RUTAS ====================

@app.route('/')
def index():
    return redirect('/panel')

@app.route('/panel')
def panel():
    leads = DATABASE.get("leads", [])
    today = datetime.now().strftime("%Y-%m-%d")

    # Preparar datos para la vista
    leads_display = []
    for lead in reversed(leads):  # Mas recientes primero
        conv = DATABASE.get("conversations", {}).get(lead["conversation_id"], [])
        ultimo_msg = conv[-1]["content"][:50] + "..." if conv else ""
        leads_display.append({
            "conversation_id": lead["conversation_id"],
            "fecha": lead.get("created_at", "")[:10],
            "nombre": lead.get("nombre"),
            "email": lead.get("email"),
            "telefono": lead.get("telefono"),
            "ultimo_mensaje": ultimo_msg
        })

    return render_template_string(PANEL_PAGE,
        leads=leads_display,
        total_leads=len(leads),
        leads_con_email=len([l for l in leads if l.get("email")]),
        leads_con_telefono=len([l for l in leads if l.get("telefono")]),
        leads_hoy=len([l for l in leads if l.get("created_at", "").startswith(today)])
    )

@app.route('/chat')
def chat_cliente():
    import uuid
    conv_id = str(uuid.uuid4())[:8]

    # Crear nuevo lead
    DATABASE["leads"].append({
        "conversation_id": conv_id,
        "created_at": datetime.now().isoformat(),
        "email": None,
        "telefono": None,
        "nombre": None
    })
    DATABASE["conversations"][conv_id] = []
    save_data()

    return render_template_string(CLIENTE_PAGE,
        empresa=DATABASE["config"]["nombre_empresa"],
        conv_id=conv_id
    )

@app.route('/conversacion/<conv_id>')
def ver_conversacion(conv_id):
    messages = DATABASE.get("conversations", {}).get(conv_id, [])
    lead = next((l for l in DATABASE["leads"] if l["conversation_id"] == conv_id), {})
    return render_template_string(CONVERSACION_PAGE, conv_id=conv_id, messages=messages, lead=lead)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json()
    message = data.get('message', '')
    conv_id = data.get('conversation_id', '')

    if conv_id not in DATABASE["conversations"]:
        DATABASE["conversations"][conv_id] = []

    # Agregar mensaje del usuario
    DATABASE["conversations"][conv_id].append({"role": "user", "content": message})

    # Extraer datos de contacto si los hay
    extract_contact_info(message, conv_id)

    # Siempre usar el mismo asistente
    conv = DATABASE["conversations"][conv_id]
    mode = "asistente"

    try:
        messages = [{"role": "system", "content": get_agent_prompt(DATABASE["config"], mode)}]
        messages += conv[-10:]  # Ultimos 10 mensajes

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=400,
            temperature=0.75
        )

        assistant_msg = response.choices[0].message.content
        DATABASE["conversations"][conv_id].append({"role": "assistant", "content": assistant_msg})
        save_data()

        return jsonify({"response": assistant_msg, "mode": mode})

    except Exception as e:
        print(f"[ERROR API] {e}")
        # Mensaje de fallback mas amigable
        fallback = "Gracias por tu mensaje. En este momento estoy procesando muchas consultas. Por favor, dejame tu correo y te contactamos pronto."
        DATABASE["conversations"][conv_id].append({"role": "assistant", "content": fallback})
        save_data()
        return jsonify({"response": fallback, "mode": mode})

@app.route('/api/config', methods=['POST'])
def update_config():
    data = request.get_json()
    DATABASE["config"].update(data)
    save_data()
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print("\n" + "="*50)
    print("  QORAX VENTAS - Sistema Completo")
    print("="*50)
    print("\n  Panel del vendedor: http://localhost:5055/panel")
    print("  Chat del cliente:   http://localhost:5055/chat")
    print("\n  Presiona Ctrl+C para cerrar")
    print("="*50 + "\n")

    app.run(debug=False, host='0.0.0.0', port=5055)

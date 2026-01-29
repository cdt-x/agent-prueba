#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QORAX VENTAS - Agente de Ventas con Panel de Control
"""

from flask import Flask, render_template_string, request, jsonify, redirect
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

def send_welcome_email(to_email, nombre_empresa):
    """Envia correo de bienvenida al cliente"""
    subject = f"Gracias por contactar a {nombre_empresa}"
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5;">
        <div style="max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px;">
            <h2 style="color: #667eea; margin-bottom: 20px;">Hola!</h2>
            <p>Gracias por tu interes en {nombre_empresa}.</p>
            <p>Hemos recibido tu informacion y uno de nuestros asesores te contactara pronto.</p>

            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #333; margin-bottom: 10px;">Nuestros servicios:</h3>
                <ul style="color: #666; line-height: 1.8;">
                    <li>Agente de Atencion 24/7</li>
                    <li>Agente de Ventas Automatizado</li>
                    <li>Asistentes Especializados (Legal, Medico, RRHH)</li>
                </ul>
            </div>

            <p>Mientras tanto, si tienes alguna pregunta, puedes responder a este correo.</p>

            <p style="margin-top: 30px; color: #888; font-size: 12px;">
                Este es un mensaje automatico de QORAX AI.
            </p>
        </div>
    </body>
    </html>
    """
    send_email_async(to_email, subject, body)

app = Flask(__name__)
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
                    # Enviar correo de bienvenida al cliente
                    send_welcome_email(emails[0], DATABASE["config"]["nombre_empresa"])
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
    if mode == "vendedor":
        return f"""Eres Carlos, experto en ventas de {config['nombre_empresa']}.

PERSONALIDAD: Vendedor consultivo, persuasivo pero no agresivo. Calido y profesional.

OBJETIVO: Cerrar ventas o agendar demos. Conseguir datos de contacto.

EMPRESA: {config['nombre_empresa']}
SERVICIOS: {config['servicios']}

PRODUCTOS Y PRECIOS:
- Agente Atencion 24/7: $250,000 COP/mes
- Agente de Ventas: $499,000 COP/mes
- Agente RRHH: $399,000 COP/mes
- Asistente Legal: $599,000 COP/mes
- Asistente Medico: $699,000 COP/mes
- Setup unico: $1,500,000 COP
- Prueba gratis: 14 dias

TECNICAS:
1. Entiende la necesidad antes de vender
2. Vende beneficios, no caracteristicas
3. Maneja objeciones con empatia
4. Siempre busca el siguiente paso

IMPORTANTE:
- Cuando el cliente este listo, PIDE su correo y telefono para contactarlo
- Se natural al pedir los datos: "Para enviarte la info, me compartes tu correo?"
- Confirma los datos cuando te los den
- Responde en espanol, maximo 3-4 oraciones"""
    else:
        return f"""Eres el asistente virtual de {config['nombre_empresa']}.

PERSONALIDAD: Amable, profesional, eficiente. Respuestas cortas y naturales.

EMPRESA: {config['nombre_empresa']}
SERVICIOS: {config['servicios']}
HORARIO: {config['horario']}

TU TRABAJO:
- Responder preguntas sobre la empresa
- Detectar interes de compra
- Recopilar informacion del cliente

CUANDO EL CLIENTE MUESTRE INTERES EN COMPRAR O PIDA PRECIOS:
- Transfierelo al experto en ventas diciendo algo como:
  "Perfecto! Te paso con Carlos, nuestro experto en ventas, para darte toda la info..."

Responde en espanol, maximo 2-3 oraciones."""


# ==================== PAGINAS HTML ====================

CLIENTE_PAGE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ empresa }} - Chat</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .chat-widget {
            width: 100%;
            max-width: 420px;
            height: 600px;
            background: #fff;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .chat-header h1 { font-size: 1.2rem; margin-bottom: 5px; }
        .chat-header p { font-size: 0.85rem; opacity: 0.9; }
        .status-dot {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #4ade80;
            border-radius: 50%;
            margin-right: 5px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 15px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            background: #f8f9fa;
        }
        .message {
            max-width: 85%;
            padding: 12px 16px;
            border-radius: 18px;
            font-size: 0.9rem;
            line-height: 1.4;
            animation: slideIn 0.3s ease;
        }
        @keyframes slideIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .message.bot {
            background: white;
            align-self: flex-start;
            border-bottom-left-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .message.user {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            align-self: flex-end;
            border-bottom-right-radius: 5px;
        }
        .message.system {
            background: #fef3c7;
            color: #92400e;
            align-self: center;
            font-size: 0.8rem;
            padding: 8px 15px;
        }
        .chat-input {
            padding: 15px;
            background: white;
            border-top: 1px solid #eee;
            display: flex;
            gap: 10px;
        }
        .chat-input input {
            flex: 1;
            padding: 12px 18px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 0.9rem;
            outline: none;
        }
        .chat-input input:focus { border-color: #667eea; }
        .chat-input button {
            padding: 12px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
        }
        .chat-input button:disabled { opacity: 0.6; }
        .typing { display: flex; gap: 5px; padding: 12px 16px; background: white; border-radius: 18px; align-self: flex-start; }
        .typing span { width: 8px; height: 8px; background: #667eea; border-radius: 50%; animation: bounce 1.4s infinite; }
        .typing span:nth-child(1) { animation-delay: -0.32s; }
        .typing span:nth-child(2) { animation-delay: -0.16s; }
        @keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }
        .powered { text-align: center; padding: 8px; font-size: 0.7rem; color: #999; }
    </style>
</head>
<body>
    <div class="chat-widget">
        <div class="chat-header">
            <h1>{{ empresa }}</h1>
            <p id="agentStatus"><span class="status-dot"></span>Asistente virtual</p>
        </div>
        <div class="chat-messages" id="messages">
            <div class="message bot">Hola! Bienvenido a {{ empresa }}. ¿En que puedo ayudarte?</div>
        </div>
        <div class="chat-input">
            <input type="text" id="userInput" placeholder="Escribe tu mensaje..." onkeypress="if(event.key==='Enter')sendMessage()">
            <button onclick="sendMessage()" id="sendBtn">Enviar</button>
        </div>
        <div class="powered">Powered by QORAX AI</div>
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
    <title>QORAX - Panel de Ventas</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            min-height: 100vh;
        }
        .navbar {
            background: #1e293b;
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #334155;
        }
        .navbar h1 {
            font-size: 1.3rem;
            background: linear-gradient(90deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .navbar a {
            color: #94a3b8;
            text-decoration: none;
            padding: 8px 15px;
            border-radius: 8px;
            transition: all 0.2s;
        }
        .navbar a:hover { background: #334155; color: white; }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: #1e293b;
            padding: 25px;
            border-radius: 15px;
            border: 1px solid #334155;
        }
        .stat-card h3 { color: #94a3b8; font-size: 0.9rem; margin-bottom: 10px; }
        .stat-card .number { font-size: 2.5rem; font-weight: bold; color: #667eea; }
        .section-title {
            font-size: 1.2rem;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #334155;
        }
        .leads-table {
            background: #1e293b;
            border-radius: 15px;
            overflow: hidden;
            border: 1px solid #334155;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 15px 20px;
            text-align: left;
            border-bottom: 1px solid #334155;
        }
        th {
            background: #334155;
            font-weight: 600;
            color: #94a3b8;
            font-size: 0.85rem;
            text-transform: uppercase;
        }
        tr:hover { background: #334155; }
        .badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .badge.new { background: #22c55e20; color: #22c55e; }
        .badge.contacted { background: #f59e0b20; color: #f59e0b; }
        .badge.closed { background: #667eea20; color: #667eea; }
        .btn {
            padding: 8px 15px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.85rem;
            transition: all 0.2s;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }
        .btn-secondary {
            background: #334155;
            color: white;
        }
        .btn-whatsapp {
            background: #25d366;
            color: white;
            text-decoration: none;
            margin-left: 5px;
        }
        .btn-email {
            background: #667eea;
            color: white;
            text-decoration: none;
            margin-left: 5px;
        }
        .btn:hover { transform: scale(1.05); }
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #64748b;
        }
        .empty-state h3 { margin-bottom: 10px; }
        .chat-link {
            display: inline-block;
            margin-top: 20px;
            padding: 12px 25px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            text-decoration: none;
            border-radius: 10px;
        }
        .refresh-btn {
            background: #334155;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            margin-left: 15px;
        }
        .conversation-preview {
            max-width: 300px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            color: #94a3b8;
            font-size: 0.85rem;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <h1>QORAX Panel de Ventas</h1>
        <div>
            <a href="/chat" target="_blank">Ver Chat del Cliente</a>
            <button class="refresh-btn" onclick="location.reload()">Actualizar</button>
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

        <h2 class="section-title">Leads Capturados</h2>

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

    # Detectar modo
    conv = DATABASE["conversations"][conv_id]
    transfer_keywords = ["precio", "costo", "cuanto", "comprar", "contratar", "demo", "cotizacion", "interesa"]
    is_sales = any(kw in message.lower() for kw in transfer_keywords) or \
               any(kw in msg["content"].lower() for msg in conv[-5:] for kw in transfer_keywords if msg["role"] == "assistant")

    mode = "vendedor" if is_sales or len(conv) > 6 else "asistente"

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
        return jsonify({"response": "Disculpa, tuve un problema. Intenta de nuevo.", "mode": mode})

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
    print("\n  Panel del vendedor: http://localhost:5050/panel")
    print("  Chat del cliente:   http://localhost:5050/chat")
    print("\n  Presiona Ctrl+C para cerrar")
    print("="*50 + "\n")

    app.run(debug=False, host='0.0.0.0', port=5050)

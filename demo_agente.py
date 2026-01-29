#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEMO DE AGENTE DE IA - Para mostrar a clientes
"""

from flask import Flask, render_template_string, request, jsonify
from dotenv import load_dotenv
from groq import Groq
import os

load_dotenv()

app = Flask(__name__)

# Cliente de Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Configuracion del agente (se puede cambiar)
AGENT_CONFIG = {
    "nombre_empresa": "Tu Empresa",
    "tipo_negocio": "servicios profesionales",
    "productos_servicios": "consultoria y asesoria empresarial",
    "horario": "Lunes a Viernes 9am-6pm",
    "contacto": "contacto@tuempresa.com"
}

# Modo actual: "asistente" o "vendedor"
current_mode = "asistente"

def get_sales_expert_prompt(config):
    return f"""Eres Carlos, el experto en ventas de {config['nombre_empresa']}. Acabas de entrar a la conversacion porque el asistente virtual te transfirio un cliente interesado.

TU PERSONALIDAD:
- Eres un vendedor experto, persuasivo pero no agresivo
- Eres calido, confiable y profesional
- Sabes escuchar y entender las necesidades del cliente
- Eres directo y vas al grano
- Usas tecnicas de venta consultiva

TU OBJETIVO:
- Entender exactamente que necesita el cliente
- Mostrar como tus servicios resuelven su problema
- Cerrar la venta o agendar una cita/llamada
- Conseguir datos de contacto del cliente

INFORMACION DE LA EMPRESA:
- Nombre: {config['nombre_empresa']}
- Servicios: {config['productos_servicios']}
- Horario: {config['horario']}

TECNICAS QUE USAS:
1. Haces preguntas para entender la necesidad real
2. Presentas beneficios, no caracteristicas
3. Manejas objeciones con empatia
4. Creas urgencia sin presionar
5. Siempre propones el siguiente paso

COMO INICIAS:
Al entrar a la conversacion, preséntate brevemente y retoma lo que el cliente ya menciono. Por ejemplo:
"Hola! Soy Carlos del equipo de ventas. Me cuentan que estas interesado en [lo que menciono]. Cuentame un poco mas sobre lo que buscas..."

REGLAS:
1. Nunca seas agresivo o desesperado
2. Si el cliente no quiere comprar ahora, ofrece enviar info por correo
3. Siempre busca el siguiente paso concreto
4. Se honesto, no prometas lo que no puedes cumplir
5. Si el cliente tiene dudas, ofrece una llamada o reunion"""

def get_agent_prompt(config):
    return f"""Eres un asistente virtual de IA para {config['nombre_empresa']}, una empresa de {config['tipo_negocio']}.

TU PERSONALIDAD:
- Eres amable, profesional y eficiente
- Respondes de forma natural, como un humano
- Usas un tono cercano pero profesional
- Eres conciso (respuestas de 2-4 oraciones max)

LO QUE HACES:
- Respondes preguntas sobre la empresa y sus servicios
- Ayudas a agendar citas o reuniones
- Calificas si el cliente es un buen prospecto
- Recopilas informacion de contacto cuando es apropiado

INFORMACION DE LA EMPRESA:
- Nombre: {config['nombre_empresa']}
- Servicios: {config['productos_servicios']}
- Horario: {config['horario']}
- Contacto: {config['contacto']}

REGLAS:
1. Si no sabes algo especifico, ofrece conectar con un humano
2. Siempre busca el siguiente paso (agendar llamada, pedir datos, etc.)
3. Se breve y directo
4. No inventes informacion que no tengas
5. Si el cliente quiere comprar o agendar, pide sus datos de contacto"""

conversation_history = []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ empresa }} - Asistente Virtual</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .chat-widget {
            width: 100%;
            max-width: 450px;
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

        .chat-header h1 {
            font-size: 1.3rem;
            margin-bottom: 5px;
        }

        .chat-header p {
            font-size: 0.85rem;
            opacity: 0.9;
        }

        .status-dot {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #4ade80;
            border-radius: 50%;
            margin-right: 5px;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
            background: #f8f9fa;
        }

        .message {
            max-width: 85%;
            padding: 12px 16px;
            border-radius: 18px;
            font-size: 0.95rem;
            line-height: 1.4;
            animation: slideIn 0.3s ease;
        }

        @keyframes slideIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

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
            font-size: 0.95rem;
            outline: none;
            transition: border-color 0.3s;
        }

        .chat-input input:focus {
            border-color: #667eea;
        }

        .chat-input button {
            padding: 12px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 0.95rem;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .chat-input button:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .chat-input button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .typing-indicator {
            display: flex;
            gap: 5px;
            padding: 12px 16px;
            background: white;
            border-radius: 18px;
            align-self: flex-start;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }

        .typing-indicator span {
            width: 8px;
            height: 8px;
            background: #667eea;
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out;
        }

        .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
        .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }

        .powered-by {
            text-align: center;
            padding: 10px;
            font-size: 0.75rem;
            color: #999;
            background: white;
        }
    </style>
</head>
<body>
    <div class="chat-widget">
        <div class="chat-header">
            <h1>{{ empresa }}</h1>
            <p><span class="status-dot"></span>Asistente virtual disponible</p>
        </div>

        <div class="chat-messages" id="messages">
            <div class="message bot">Hola! Soy el asistente virtual de {{ empresa }}. ¿En que puedo ayudarte hoy?</div>
        </div>

        <div class="chat-input">
            <input type="text" id="userInput" placeholder="Escribe tu mensaje..." onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()" id="sendBtn">Enviar</button>
        </div>

        <div class="powered-by">
            Powered by QORAX AI
        </div>
    </div>

    <script>
        const messages = document.getElementById('messages');
        const userInput = document.getElementById('userInput');
        const sendBtn = document.getElementById('sendBtn');

        function addMessage(text, isUser) {
            const div = document.createElement('div');
            div.className = 'message ' + (isUser ? 'user' : 'bot');
            div.textContent = text;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }

        function showTyping() {
            const div = document.createElement('div');
            div.className = 'typing-indicator';
            div.id = 'typing';
            div.innerHTML = '<span></span><span></span><span></span>';
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }

        function removeTyping() {
            const typing = document.getElementById('typing');
            if (typing) typing.remove();
        }

        let currentMode = 'asistente';

        async function sendMessage() {
            const text = userInput.value.trim();
            if (!text) return;

            addMessage(text, true);
            userInput.value = '';
            sendBtn.disabled = true;
            showTyping();

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });

                const data = await response.json();
                removeTyping();

                // Detectar cambio a vendedor
                if (data.mode === 'vendedor' && currentMode === 'asistente') {
                    currentMode = 'vendedor';
                    const header = document.querySelector('.chat-header p');
                    header.innerHTML = '<span class="status-dot" style="background:#f59e0b"></span>Carlos - Experto en Ventas';
                }

                addMessage(data.response, false);
            } catch (error) {
                removeTyping();
                addMessage('Disculpa, tuve un problema. Puedes intentar de nuevo?', false);
            }

            sendBtn.disabled = false;
            userInput.focus();
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') sendMessage();
        }

        userInput.focus();
    </script>
</body>
</html>
"""

# Pagina de configuracion
CONFIG_PAGE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Configurar Demo - QORAX</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .config-card {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 500px;
            width: 100%;
        }
        h1 {
            color: #1a1a2e;
            margin-bottom: 10px;
            font-size: 1.8rem;
        }
        p.subtitle {
            color: #666;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }
        input, textarea, select {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        textarea { resize: vertical; min-height: 80px; }
        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover { transform: scale(1.02); }
        .preset-btns {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .preset-btn {
            padding: 8px 15px;
            background: #f0f0f0;
            border: 2px solid #e0e0e0;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.2s;
        }
        .preset-btn:hover {
            border-color: #667eea;
            background: #667eea20;
        }
    </style>
</head>
<body>
    <div class="config-card">
        <h1>Configurar Demo</h1>
        <p class="subtitle">Personaliza el agente para tu cliente</p>

        <div class="preset-btns">
            <span class="preset-btn" onclick="setPreset('abogado')">Abogado</span>
            <span class="preset-btn" onclick="setPreset('medico')">Medico</span>
            <span class="preset-btn" onclick="setPreset('restaurante')">Restaurante</span>
            <span class="preset-btn" onclick="setPreset('inmobiliaria')">Inmobiliaria</span>
            <span class="preset-btn" onclick="setPreset('ecommerce')">E-commerce</span>
        </div>

        <form action="/demo" method="GET">
            <div class="form-group">
                <label>Nombre de la empresa</label>
                <input type="text" name="empresa" id="empresa" placeholder="Ej: Bufete Garcia & Asociados" required>
            </div>

            <div class="form-group">
                <label>Tipo de negocio</label>
                <input type="text" name="tipo" id="tipo" placeholder="Ej: servicios legales" required>
            </div>

            <div class="form-group">
                <label>Productos/Servicios</label>
                <textarea name="servicios" id="servicios" placeholder="Ej: asesoria legal, contratos, divorcios, demandas civiles"></textarea>
            </div>

            <div class="form-group">
                <label>Horario de atencion</label>
                <input type="text" name="horario" id="horario" placeholder="Ej: Lunes a Viernes 9am-6pm">
            </div>

            <button type="submit">Iniciar Demo</button>
        </form>
    </div>

    <script>
        const presets = {
            abogado: {
                empresa: "Bufete Legal Ejemplo",
                tipo: "servicios legales",
                servicios: "asesoria legal, contratos, divorcios, demandas civiles, derecho corporativo",
                horario: "Lunes a Viernes 9am-7pm"
            },
            medico: {
                empresa: "Clinica Salud Integral",
                tipo: "servicios medicos",
                servicios: "consultas generales, pediatria, ginecologia, medicina interna, laboratorio",
                horario: "Lunes a Sabado 8am-8pm"
            },
            restaurante: {
                empresa: "Restaurante El Buen Sabor",
                tipo: "gastronomia",
                servicios: "comida colombiana, almuerzos ejecutivos, eventos privados, domicilios",
                horario: "Lunes a Domingo 11am-10pm"
            },
            inmobiliaria: {
                empresa: "Inmobiliaria Tu Hogar",
                tipo: "bienes raices",
                servicios: "venta de casas y apartamentos, arriendos, avaluos, asesoria de credito",
                horario: "Lunes a Sabado 8am-6pm"
            },
            ecommerce: {
                empresa: "TiendaOnline.com",
                tipo: "comercio electronico",
                servicios: "venta de productos, seguimiento de pedidos, cambios y devoluciones",
                horario: "24/7 - Soporte en horario de oficina"
            }
        };

        function setPreset(type) {
            const p = presets[type];
            document.getElementById('empresa').value = p.empresa;
            document.getElementById('tipo').value = p.tipo;
            document.getElementById('servicios').value = p.servicios;
            document.getElementById('horario').value = p.horario;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def config():
    return render_template_string(CONFIG_PAGE)

@app.route('/demo')
def demo():
    global AGENT_CONFIG, current_mode, conversation_history

    empresa = request.args.get('empresa', 'Mi Empresa')
    tipo = request.args.get('tipo', 'servicios')
    servicios = request.args.get('servicios', 'diversos servicios')
    horario = request.args.get('horario', 'Lunes a Viernes')

    AGENT_CONFIG = {
        "nombre_empresa": empresa,
        "tipo_negocio": tipo,
        "productos_servicios": servicios,
        "horario": horario,
        "contacto": "contacto@ejemplo.com"
    }

    # Limpiar historial y resetear modo
    conversation_history = []
    current_mode = "asistente"

    return render_template_string(HTML_TEMPLATE, empresa=empresa)

@app.route('/chat', methods=['POST'])
def chat():
    global conversation_history, current_mode

    data = request.get_json()
    user_message = data.get('message', '')

    # Agregar mensaje del usuario al historial
    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    # Limitar historial a ultimos 10 mensajes
    if len(conversation_history) > 10:
        conversation_history = conversation_history[-10:]

    try:
        # Detectar si debe transferir a vendedor
        transfer_keywords = ["experto", "vendedor", "asesor", "hablar con alguien", "persona real",
                           "quiero comprar", "me interesa comprar", "precios", "cotizacion",
                           "cuanto cuesta", "promocion", "descuento", "cerrar", "contratar"]

        should_transfer = any(kw in user_message.lower() for kw in transfer_keywords)

        # Si detectamos intencion de compra o pide experto, cambiar a modo vendedor
        if should_transfer and current_mode == "asistente":
            current_mode = "vendedor"
            # Agregar contexto de transferencia
            transfer_context = "\n\n[SISTEMA: El cliente ha sido transferido a ti. Revisa la conversacion anterior y continua desde donde quedo el asistente. Presentate brevemente como Carlos del equipo de ventas.]"
            system_prompt = get_sales_expert_prompt(AGENT_CONFIG) + transfer_context
        elif current_mode == "vendedor":
            system_prompt = get_sales_expert_prompt(AGENT_CONFIG)
        else:
            system_prompt = get_agent_prompt(AGENT_CONFIG)

        # Llamar a Groq
        messages = [
            {"role": "system", "content": system_prompt}
        ] + conversation_history

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=500,
            temperature=0.75
        )

        assistant_message = response.choices[0].message.content

        # Agregar respuesta al historial
        conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return jsonify({"response": assistant_message, "mode": current_mode})

    except Exception as e:
        return jsonify({"response": f"Disculpa, tuve un problema tecnico. Por favor intenta de nuevo."})

if __name__ == '__main__':
    print("\n" + "="*50)
    print("  DEMO DE AGENTE DE IA - QORAX")
    print("="*50)
    print("\n  Abre en tu navegador:")
    print("  http://localhost:5002")
    print("\n  Presiona Ctrl+C para cerrar")
    print("="*50 + "\n")

    app.run(debug=False, host='0.0.0.0', port=5002)

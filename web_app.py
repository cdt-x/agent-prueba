#!/usr/bin/env python3
"""
Versión web del agente vendedor usando Flask.
Incluye una interfaz de chat moderna.
"""

import sys
import os
import uuid
from flask import Flask, render_template_string, request, jsonify, session

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.agent import SalesAgent
from config.settings import get_settings

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Almacén de agentes por sesión
agents = {}

# Template HTML
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ company_name }} - Agente de Ventas IA</title>
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

        .chat-container {
            width: 100%;
            max-width: 600px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            height: 90vh;
            max-height: 800px;
        }

        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }

        .chat-header h1 {
            font-size: 1.5rem;
            margin-bottom: 5px;
        }

        .chat-header p {
            opacity: 0.9;
            font-size: 0.9rem;
        }

        .status-badge {
            display: inline-block;
            background: #4CAF50;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            margin-top: 10px;
        }

        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f5f5f5;
        }

        .message {
            margin-bottom: 15px;
            display: flex;
            flex-direction: column;
        }

        .message.user {
            align-items: flex-end;
        }

        .message.agent {
            align-items: flex-start;
        }

        .message-content {
            max-width: 80%;
            padding: 12px 18px;
            border-radius: 18px;
            line-height: 1.5;
        }

        .message.user .message-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-bottom-right-radius: 4px;
        }

        .message.agent .message-content {
            background: white;
            color: #333;
            border-bottom-left-radius: 4px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .message-sender {
            font-size: 0.75rem;
            color: #888;
            margin-bottom: 4px;
            padding: 0 10px;
        }

        .chat-input-container {
            padding: 20px;
            background: white;
            border-top: 1px solid #eee;
        }

        .chat-input-wrapper {
            display: flex;
            gap: 10px;
        }

        #messageInput {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #eee;
            border-radius: 25px;
            font-size: 1rem;
            outline: none;
            transition: border-color 0.3s;
        }

        #messageInput:focus {
            border-color: #667eea;
        }

        #sendButton {
            padding: 15px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 1rem;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        #sendButton:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }

        #sendButton:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .typing-indicator {
            display: none;
            padding: 10px;
            color: #888;
            font-style: italic;
        }

        .typing-indicator.active {
            display: block;
        }

        .quick-actions {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-top: 10px;
        }

        .quick-action {
            padding: 8px 16px;
            background: #f0f0f0;
            border: none;
            border-radius: 20px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: background 0.2s;
        }

        .quick-action:hover {
            background: #e0e0e0;
        }

        @media (max-width: 480px) {
            .chat-container {
                height: 100vh;
                border-radius: 0;
            }

            .message-content {
                max-width: 90%;
            }
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>{{ agent_name }}</h1>
            <p>{{ company_name }}</p>
            <span class="status-badge">En línea</span>
        </div>

        <div class="chat-messages" id="chatMessages">
            <!-- Messages will be added here -->
        </div>

        <div class="typing-indicator" id="typingIndicator">
            {{ agent_name }} está escribiendo...
        </div>

        <div class="chat-input-container">
            <div class="chat-input-wrapper">
                <input type="text" id="messageInput" placeholder="Escribe tu mensaje..." autocomplete="off">
                <button id="sendButton">Enviar</button>
            </div>
            <div class="quick-actions">
                <button class="quick-action" data-message="¿Qué soluciones ofrecen?">Soluciones</button>
                <button class="quick-action" data-message="¿Cuáles son los precios?">Precios</button>
                <button class="quick-action" data-message="Quiero una demostración">Demo</button>
            </div>
        </div>
    </div>

    <script>
        const chatMessages = document.getElementById('chatMessages');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const typingIndicator = document.getElementById('typingIndicator');

        // Load initial greeting
        window.addEventListener('load', () => {
            fetch('/api/greeting')
                .then(response => response.json())
                .then(data => {
                    addMessage(data.message, 'agent');
                });
        });

        function addMessage(text, sender) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;

            const senderName = sender === 'agent' ? '{{ agent_name }}' : 'Tú';

            messageDiv.innerHTML = `
                <span class="message-sender">${senderName}</span>
                <div class="message-content">${text.replace(/\\n/g, '<br>')}</div>
            `;

            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function sendMessage() {
            const message = messageInput.value.trim();
            if (!message) return;

            addMessage(message, 'user');
            messageInput.value = '';
            sendButton.disabled = true;
            typingIndicator.classList.add('active');

            fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message }),
            })
            .then(response => response.json())
            .then(data => {
                typingIndicator.classList.remove('active');
                addMessage(data.response, 'agent');
                sendButton.disabled = false;
            })
            .catch(error => {
                typingIndicator.classList.remove('active');
                addMessage('Lo siento, hubo un error. Por favor intenta de nuevo.', 'agent');
                sendButton.disabled = false;
            });
        }

        sendButton.addEventListener('click', sendMessage);

        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        // Quick actions
        document.querySelectorAll('.quick-action').forEach(button => {
            button.addEventListener('click', () => {
                messageInput.value = button.dataset.message;
                sendMessage();
            });
        });
    </script>
</body>
</html>
'''


def get_agent():
    """Obtiene o crea un agente para la sesión actual."""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())

    session_id = session['session_id']

    if session_id not in agents:
        settings = get_settings()
        # Usar Groq como prioridad (gratis y rápido), sino Gemini, sino Anthropic, sino OpenAI
        if settings.groq_api_key:
            agents[session_id] = SalesAgent(
                agent_name=settings.agent_name,
                company_name=settings.company_name,
                api_provider="groq",
                api_key=settings.groq_api_key
            )
        elif settings.gemini_api_key:
            agents[session_id] = SalesAgent(
                agent_name=settings.agent_name,
                company_name=settings.company_name,
                api_provider="gemini",
                api_key=settings.gemini_api_key
            )
        elif settings.anthropic_api_key:
            agents[session_id] = SalesAgent(
                agent_name=settings.agent_name,
                company_name=settings.company_name,
                api_provider="anthropic",
                api_key=settings.anthropic_api_key
            )
        elif settings.openai_api_key:
            agents[session_id] = SalesAgent(
                agent_name=settings.agent_name,
                company_name=settings.company_name,
                api_provider="openai",
                api_key=settings.openai_api_key
            )
        else:
            agents[session_id] = SalesAgent(
                agent_name=settings.agent_name,
                company_name=settings.company_name
            )

    return agents[session_id]


@app.route('/')
def index():
    """Página principal."""
    settings = get_settings()
    return render_template_string(
        HTML_TEMPLATE,
        agent_name=settings.agent_name,
        company_name=settings.company_name
    )


@app.route('/api/greeting')
def greeting():
    """Obtiene el saludo inicial."""
    agent = get_agent()
    message = agent.get_greeting()
    return jsonify({'message': message})


@app.route('/api/chat', methods=['POST'])
def chat():
    """Procesa un mensaje del usuario."""
    data = request.json
    message = data.get('message', '')

    if not message:
        return jsonify({'error': 'Mensaje vacío'}), 400

    agent = get_agent()
    response = agent.process_message(message)

    return jsonify({
        'response': response,
        'profile': agent.get_profile().to_dict()
    })


@app.route('/api/reset', methods=['POST'])
def reset():
    """Reinicia la conversación."""
    agent = get_agent()
    agent.reset()
    return jsonify({'status': 'ok', 'message': 'Conversación reiniciada'})


@app.route('/api/profile')
def profile():
    """Obtiene el perfil del cliente."""
    agent = get_agent()
    return jsonify(agent.get_profile().to_dict())


if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  Agente Vendedor de IA - Versión Web")
    print("=" * 50)
    print("\nIniciando servidor...")
    print("Abre tu navegador en: http://localhost:5000")
    print("\nPresiona Ctrl+C para detener el servidor\n")

    app.run(debug=True, port=5000)

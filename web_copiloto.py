#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COPILOTO DE VENTAS - Interfaz Web
"""

from flask import Flask, render_template_string, request, jsonify
from dotenv import load_dotenv
import os

load_dotenv()

from core.sales_copilot import SalesCopilot

app = Flask(__name__)

# Inicializar copiloto
copilot = SalesCopilot(api_provider='groq')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QORAX - Copiloto de Ventas</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }

        header {
            text-align: center;
            padding: 20px 0;
            border-bottom: 1px solid #ffffff20;
        }

        header h1 {
            font-size: 2rem;
            background: linear-gradient(90deg, #00d9ff, #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
        }

        header p {
            color: #888;
            font-size: 0.9rem;
        }

        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px 0;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .message {
            padding: 15px 20px;
            border-radius: 15px;
            max-width: 85%;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .message.user {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            align-self: flex-end;
            border-bottom-right-radius: 5px;
        }

        .message.bot {
            background: #2a2a4a;
            align-self: flex-start;
            border-bottom-left-radius: 5px;
            white-space: pre-wrap;
            font-family: 'Consolas', monospace;
            font-size: 0.9rem;
            line-height: 1.6;
        }

        .message.bot .section-title {
            color: #00d9ff;
            font-weight: bold;
            margin-top: 10px;
        }

        .input-container {
            display: flex;
            gap: 10px;
            padding: 20px 0;
            border-top: 1px solid #ffffff20;
        }

        input[type="text"] {
            flex: 1;
            padding: 15px 20px;
            border: none;
            border-radius: 25px;
            background: #2a2a4a;
            color: #fff;
            font-size: 1rem;
            outline: none;
            transition: box-shadow 0.3s;
        }

        input[type="text"]:focus {
            box-shadow: 0 0 0 2px #00d9ff;
        }

        input[type="text"]::placeholder {
            color: #666;
        }

        button {
            padding: 15px 30px;
            border: none;
            border-radius: 25px;
            background: linear-gradient(135deg, #00d9ff 0%, #00ff88 100%);
            color: #1a1a2e;
            font-size: 1rem;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        button:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(0, 217, 255, 0.4);
        }

        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        .commands {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
            flex-wrap: wrap;
        }

        .command-btn {
            padding: 8px 15px;
            background: #3a3a5a;
            border: 1px solid #00d9ff40;
            border-radius: 20px;
            color: #00d9ff;
            font-size: 0.8rem;
            cursor: pointer;
            transition: all 0.2s;
        }

        .command-btn:hover {
            background: #00d9ff20;
            border-color: #00d9ff;
        }

        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid #ffffff40;
            border-top-color: #00d9ff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .status {
            text-align: center;
            padding: 10px;
            font-size: 0.8rem;
            color: #00ff88;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>QORAX - Copiloto de Ventas</h1>
            <p>Tu asistente para cerrar ventas</p>
        </header>

        <div class="status">Conectado a Groq (Llama 3.3 70B)</div>

        <div class="commands">
            <button class="command-btn" onclick="sendCommand('/nuevo')">Nuevo Cliente</button>
            <button class="command-btn" onclick="sendCommand('/resumen')">Ver Resumen</button>
            <button class="command-btn" onclick="sendCommand('/productos')">Productos</button>
            <button class="command-btn" onclick="sendCommand('/ayuda')">Ayuda</button>
        </div>

        <div class="chat-container" id="chat">
            <div class="message bot">Hola! Soy tu copiloto de ventas.

Cuentame que te dice el cliente y te ayudo con:
  * Que preguntarle
  * Que producto ofrecerle
  * Como manejar objeciones
  * Texto listo para copiar y enviarle

Que te dijo el cliente?</div>
        </div>

        <div class="input-container">
            <input type="text" id="userInput" placeholder="Escribe lo que dice el cliente..." onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()" id="sendBtn">Enviar</button>
        </div>
    </div>

    <script>
        const chat = document.getElementById('chat');
        const userInput = document.getElementById('userInput');
        const sendBtn = document.getElementById('sendBtn');

        function addMessage(text, isUser) {
            const div = document.createElement('div');
            div.className = 'message ' + (isUser ? 'user' : 'bot');
            div.textContent = text;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }

        function showLoading() {
            const div = document.createElement('div');
            div.className = 'message bot';
            div.id = 'loading';
            div.innerHTML = '<div class="loading"></div> Pensando...';
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }

        function removeLoading() {
            const loading = document.getElementById('loading');
            if (loading) loading.remove();
        }

        async function sendMessage() {
            const text = userInput.value.trim();
            if (!text) return;

            addMessage(text, true);
            userInput.value = '';
            sendBtn.disabled = true;
            showLoading();

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });

                const data = await response.json();
                removeLoading();
                addMessage(data.response, false);
            } catch (error) {
                removeLoading();
                addMessage('Error de conexion. Intenta de nuevo.', false);
            }

            sendBtn.disabled = false;
            userInput.focus();
        }

        function sendCommand(cmd) {
            userInput.value = cmd;
            sendMessage();
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        userInput.focus();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')

    if message.lower() == '/nuevo':
        copilot.reset()

    response = copilot.process_input(message)
    return jsonify({'response': response})

@app.route('/reset', methods=['POST'])
def reset():
    copilot.reset()
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    print("\n" + "="*50)
    print("  COPILOTO DE VENTAS - Interfaz Web")
    print("="*50)
    print("\n  Abre en tu navegador:")
    print("  http://localhost:5001")
    print("\n  Presiona Ctrl+C para cerrar")
    print("="*50 + "\n")

    app.run(debug=False, host='0.0.0.0', port=5001)

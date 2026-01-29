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
        select {
            appearance: none;
            background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23666' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
            background-repeat: no-repeat;
            background-position: right 12px center;
            background-size: 16px;
            padding-right: 40px;
        }
        select optgroup {
            font-weight: bold;
            color: #667eea;
        }
        select option {
            font-weight: normal;
            color: #333;
            padding: 8px;
        }
    </style>
</head>
<body>
    <div class="config-card">
        <h1>Configurar Demo</h1>
        <p class="subtitle">Personaliza el agente para tu cliente</p>

        <div class="form-group">
            <label>Tipo de negocio (plantilla)</label>
            <select id="presetSelect" onchange="setPreset(this.value)">
                <option value="">-- Selecciona una industria --</option>
                <option value="personalizado">Otro / Personalizado</option>
                <optgroup label="Salud">
                    <option value="medico">Medico / Clinica</option>
                    <option value="odontologo">Odontologo</option>
                    <option value="psicologo">Psicologo</option>
                    <option value="veterinaria">Veterinaria</option>
                    <option value="farmacia">Farmacia</option>
                    <option value="optica">Optica</option>
                </optgroup>
                <optgroup label="Legal y Finanzas">
                    <option value="abogado">Abogado / Bufete</option>
                    <option value="notaria">Notaria</option>
                    <option value="contador">Contador</option>
                    <option value="aseguradora">Aseguradora</option>
                    <option value="banco">Banco / Finanzas</option>
                </optgroup>
                <optgroup label="Gastronomia">
                    <option value="restaurante">Restaurante</option>
                    <option value="cafeteria">Cafeteria</option>
                    <option value="bar">Bar / Discoteca</option>
                </optgroup>
                <optgroup label="Comercio">
                    <option value="ecommerce">E-commerce</option>
                    <option value="tienda">Tienda Fisica</option>
                    <option value="ferreteria">Ferreteria</option>
                    <option value="concesionario">Concesionario Autos</option>
                </optgroup>
                <optgroup label="Inmobiliario">
                    <option value="inmobiliaria">Inmobiliaria</option>
                    <option value="constructora">Constructora</option>
                    <option value="arquitecto">Arquitecto</option>
                </optgroup>
                <optgroup label="Belleza y Bienestar">
                    <option value="gimnasio">Gimnasio</option>
                    <option value="spa">Spa / Belleza</option>
                    <option value="peluqueria">Peluqueria</option>
                </optgroup>
                <optgroup label="Turismo">
                    <option value="hotel">Hotel</option>
                    <option value="agencia_viajes">Agencia de Viajes</option>
                </optgroup>
                <optgroup label="Educacion">
                    <option value="academia">Academia / Cursos</option>
                    <option value="colegio">Colegio</option>
                    <option value="universidad">Universidad</option>
                </optgroup>
                <optgroup label="Tecnologia y Marketing">
                    <option value="software">Software / Tech</option>
                    <option value="marketing">Agencia Marketing</option>
                    <option value="imprenta">Imprenta</option>
                </optgroup>
                <optgroup label="Servicios">
                    <option value="taller">Taller Mecanico</option>
                    <option value="fotografo">Fotografo</option>
                    <option value="eventos">Eventos / Bodas</option>
                    <option value="transporte">Transporte / Logistica</option>
                    <option value="limpieza">Servicios de Limpieza</option>
                    <option value="seguridad">Seguridad Privada</option>
                    <option value="funeraria">Funeraria</option>
                    <option value="coworking">Coworking</option>
                </optgroup>
            </select>
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
            personalizado: {
                empresa: "",
                tipo: "",
                servicios: "",
                horario: ""
            },
            abogado: {
                empresa: "Bufete Legal Ejemplo",
                tipo: "servicios legales",
                servicios: "asesoria legal, contratos, divorcios, demandas civiles, derecho corporativo, derecho laboral",
                horario: "Lunes a Viernes 9am-7pm"
            },
            medico: {
                empresa: "Clinica Salud Integral",
                tipo: "servicios medicos",
                servicios: "consultas generales, pediatria, ginecologia, medicina interna, laboratorio, urgencias",
                horario: "Lunes a Sabado 8am-8pm"
            },
            odontologo: {
                empresa: "Sonrisas Dental",
                tipo: "odontologia",
                servicios: "limpieza dental, ortodoncia, blanqueamiento, implantes, endodoncia, odontopediatria",
                horario: "Lunes a Sabado 8am-6pm"
            },
            psicologo: {
                empresa: "Centro de Bienestar Mental",
                tipo: "psicologia",
                servicios: "terapia individual, terapia de pareja, terapia familiar, ansiedad, depresion, coaching",
                horario: "Lunes a Viernes 8am-8pm, Sabados 9am-2pm"
            },
            veterinaria: {
                empresa: "Veterinaria Amigos Peludos",
                tipo: "veterinaria",
                servicios: "consultas, vacunacion, cirugia, peluqueria canina, hotel para mascotas, emergencias 24h",
                horario: "Lunes a Domingo 8am-8pm"
            },
            restaurante: {
                empresa: "Restaurante El Buen Sabor",
                tipo: "gastronomia",
                servicios: "comida colombiana, almuerzos ejecutivos, eventos privados, domicilios, catering",
                horario: "Lunes a Domingo 11am-10pm"
            },
            cafeteria: {
                empresa: "Cafe Aroma",
                tipo: "cafeteria",
                servicios: "cafe de especialidad, desayunos, postres, wifi gratis, espacio coworking",
                horario: "Lunes a Domingo 7am-9pm"
            },
            bar: {
                empresa: "Bar La Noche",
                tipo: "entretenimiento nocturno",
                servicios: "cocteleria, musica en vivo, reserva de mesas VIP, eventos privados, cumpleanos",
                horario: "Jueves a Sabado 8pm-3am"
            },
            inmobiliaria: {
                empresa: "Inmobiliaria Tu Hogar",
                tipo: "bienes raices",
                servicios: "venta de casas y apartamentos, arriendos, avaluos, asesoria de credito hipotecario",
                horario: "Lunes a Sabado 8am-6pm"
            },
            constructora: {
                empresa: "Constructora Solida",
                tipo: "construccion",
                servicios: "proyectos residenciales, remodelaciones, acabados, presupuestos, asesoria tecnica",
                horario: "Lunes a Viernes 8am-6pm, Sabados 8am-1pm"
            },
            ecommerce: {
                empresa: "TiendaOnline.com",
                tipo: "comercio electronico",
                servicios: "venta de productos, seguimiento de pedidos, cambios y devoluciones, garantias",
                horario: "24/7 - Soporte en horario de oficina"
            },
            tienda: {
                empresa: "Tienda La Esquina",
                tipo: "comercio minorista",
                servicios: "venta de productos, apartados, domicilios, pedidos por WhatsApp, promociones",
                horario: "Lunes a Sabado 8am-8pm, Domingos 9am-2pm"
            },
            gimnasio: {
                empresa: "Fitness Total Gym",
                tipo: "gimnasio",
                servicios: "musculacion, clases grupales, spinning, yoga, entrenador personal, nutricionista",
                horario: "Lunes a Viernes 5am-10pm, Sabados 6am-6pm, Domingos 7am-2pm"
            },
            spa: {
                empresa: "Spa Relax & Beauty",
                tipo: "spa y belleza",
                servicios: "masajes, tratamientos faciales, manicure, pedicure, depilacion, dia de spa",
                horario: "Lunes a Sabado 9am-8pm"
            },
            peluqueria: {
                empresa: "Estilo Hair Studio",
                tipo: "peluqueria",
                servicios: "corte, tintura, mechas, alisado, peinados, barberia, tratamientos capilares",
                horario: "Martes a Sabado 9am-7pm"
            },
            hotel: {
                empresa: "Hotel Plaza Colonial",
                tipo: "hoteleria",
                servicios: "habitaciones, suites, restaurante, eventos, piscina, spa, transporte aeropuerto",
                horario: "24/7 - Recepcion siempre disponible"
            },
            agencia_viajes: {
                empresa: "Viajes y Aventuras",
                tipo: "agencia de viajes",
                servicios: "paquetes turisticos, tiquetes aereos, hoteles, cruceros, visas, seguros de viaje",
                horario: "Lunes a Viernes 9am-6pm, Sabados 9am-1pm"
            },
            contador: {
                empresa: "Contadores Asociados",
                tipo: "contabilidad",
                servicios: "declaracion de renta, contabilidad empresarial, nomina, impuestos, asesoria tributaria",
                horario: "Lunes a Viernes 8am-6pm"
            },
            academia: {
                empresa: "Academia de Idiomas Global",
                tipo: "educacion",
                servicios: "cursos de ingles, frances, aleman, clases particulares, preparacion examenes internacionales",
                horario: "Lunes a Sabado 7am-9pm"
            },
            colegio: {
                empresa: "Colegio Nueva Generacion",
                tipo: "educacion escolar",
                servicios: "preescolar, primaria, bachillerato, actividades extracurriculares, transporte escolar",
                horario: "Lunes a Viernes 6:30am-4pm"
            },
            universidad: {
                empresa: "Universidad del Futuro",
                tipo: "educacion superior",
                servicios: "pregrados, posgrados, educacion virtual, becas, intercambios, extension universitaria",
                horario: "Lunes a Viernes 7am-9pm, Sabados 8am-5pm"
            },
            aseguradora: {
                empresa: "Seguros Confianza",
                tipo: "seguros",
                servicios: "seguro de vida, seguro vehicular, seguro de hogar, seguro de salud, SOAT",
                horario: "Lunes a Viernes 8am-5pm"
            },
            banco: {
                empresa: "Banco Digital Plus",
                tipo: "servicios financieros",
                servicios: "cuentas de ahorro, creditos, tarjetas, inversiones, pagos, transferencias",
                horario: "Lunes a Viernes 8am-4pm, App 24/7"
            },
            taller: {
                empresa: "Taller Mecanico AutoFix",
                tipo: "taller mecanico",
                servicios: "mantenimiento preventivo, reparaciones, frenos, suspension, electricidad automotriz",
                horario: "Lunes a Sabado 7am-6pm"
            },
            concesionario: {
                empresa: "Autos Premium",
                tipo: "concesionario",
                servicios: "venta de vehiculos nuevos y usados, financiacion, seguros, servicio tecnico, repuestos",
                horario: "Lunes a Sabado 8am-7pm, Domingos 10am-4pm"
            },
            ferreteria: {
                empresa: "Ferreteria El Constructor",
                tipo: "ferreteria",
                servicios: "materiales de construccion, herramientas, plomeria, electricidad, pinturas, domicilios",
                horario: "Lunes a Sabado 7am-7pm, Domingos 8am-2pm"
            },
            farmacia: {
                empresa: "Farmacia Salud Total",
                tipo: "farmacia",
                servicios: "medicamentos, formula medica, inyectologia, toma de presion, domicilios 24h",
                horario: "24 horas, 7 dias a la semana"
            },
            optica: {
                empresa: "Optica Vision Clara",
                tipo: "optica",
                servicios: "examen visual, lentes formulados, lentes de contacto, gafas de sol, monturas",
                horario: "Lunes a Sabado 9am-7pm"
            },
            funeraria: {
                empresa: "Funeraria La Paz",
                tipo: "servicios funerarios",
                servicios: "servicios exequiales, cremacion, traslados, planes de prevision, asesoria legal",
                horario: "24/7 - Siempre disponibles"
            },
            imprenta: {
                empresa: "Imprenta Grafica Express",
                tipo: "imprenta",
                servicios: "tarjetas, volantes, pendones, libros, papeleria corporativa, diseno grafico",
                horario: "Lunes a Viernes 8am-6pm, Sabados 8am-1pm"
            },
            software: {
                empresa: "Tech Solutions",
                tipo: "tecnologia",
                servicios: "desarrollo de software, apps moviles, paginas web, soporte IT, consultoria tecnologica",
                horario: "Lunes a Viernes 8am-6pm, Soporte 24/7"
            },
            marketing: {
                empresa: "Agencia Digital Creativa",
                tipo: "marketing digital",
                servicios: "redes sociales, publicidad digital, SEO, diseno web, branding, contenido audiovisual",
                horario: "Lunes a Viernes 9am-6pm"
            },
            arquitecto: {
                empresa: "Arquitectura & Diseno",
                tipo: "arquitectura",
                servicios: "diseno arquitectonico, planos, remodelaciones, diseno de interiores, tramites de construccion",
                horario: "Lunes a Viernes 8am-6pm"
            },
            fotografo: {
                empresa: "Foto Studio Pro",
                tipo: "fotografia",
                servicios: "bodas, eventos, retratos, fotografia de producto, video, edicion profesional",
                horario: "Lunes a Sabado 9am-7pm, eventos fines de semana"
            },
            eventos: {
                empresa: "Eventos & Celebraciones",
                tipo: "organizacion de eventos",
                servicios: "bodas, quince anos, eventos corporativos, decoracion, catering, animacion",
                horario: "Lunes a Viernes 9am-6pm, eventos fines de semana"
            },
            transporte: {
                empresa: "Transportes Rapidos",
                tipo: "transporte y logistica",
                servicios: "envios nacionales, mensajeria, mudanzas, carga pesada, rastreo en tiempo real",
                horario: "Lunes a Sabado 6am-8pm"
            },
            limpieza: {
                empresa: "Limpieza Total",
                tipo: "servicios de limpieza",
                servicios: "limpieza de hogares, oficinas, post-construccion, limpieza de vidrios, desinfeccion",
                horario: "Lunes a Sabado 7am-6pm"
            },
            seguridad: {
                empresa: "Seguridad Elite",
                tipo: "seguridad privada",
                servicios: "vigilancia, escoltas, monitoreo CCTV, alarmas, seguridad para eventos",
                horario: "24/7 - Central de monitoreo"
            },
            coworking: {
                empresa: "Espacio Cowork Hub",
                tipo: "coworking",
                servicios: "escritorios flexibles, oficinas privadas, salas de reunion, domicilio fiscal, networking",
                horario: "Lunes a Viernes 7am-10pm, Sabados 8am-6pm"
            },
            notaria: {
                empresa: "Notaria 45",
                tipo: "notaria",
                servicios: "escrituras, autenticaciones, poderes, matrimonios, declaraciones juramentadas, apostilla",
                horario: "Lunes a Viernes 8am-5pm"
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

    app.run(debug=False, host='0.0.0.0', port=8080)

# Agente Vendedor de IA

Un agente de inteligencia artificial especializado en ventas, diseñado para interactuar con clientes potenciales, entender sus necesidades y guiarlos hacia la solución perfecta.

## Características

- **Perfilamiento automático de clientes**: Detecta industria, tipo de empresa, urgencia y más
- **Metodología SPIN**: Implementa técnicas de venta consultiva probadas
- **Manejo inteligente de objeciones**: Responde a preocupaciones sobre precio, tiempo, confianza, etc.
- **Múltiples interfaces**: Consola rica, texto simple, o web
- **Modo demo**: Funciona sin API keys con respuestas predefinidas inteligentes
- **Integración con IA**: Soporte para OpenAI y Anthropic
- **Analytics**: Seguimiento de métricas y conversiones
- **Integraciones**: CRM, email, webhooks

## Instalación Rápida

```bash
# Clonar o descargar el proyecto
cd iagent

# Ejecutar setup
python setup.py

# Iniciar el agente
python main.py
```

## Requisitos

- Python 3.8+
- Dependencias listadas en `requirements.txt`

## Modos de Ejecución

### 1. Interfaz Rica (Recomendada)
```bash
python main.py
```
Interfaz de consola con colores, paneles y formato mejorado.

### 2. Interfaz Simple
```bash
python simple_chat.py
```
Versión básica que funciona en cualquier terminal.

### 3. Interfaz Web
```bash
pip install flask
python web_app.py
```
Abre http://localhost:5000 en tu navegador.

## Configuración

Edita el archivo `.env`:

```env
# Nombre del agente
AGENT_NAME=Luna

# Nombre de tu empresa
COMPANY_NAME=Mi Empresa

# API Keys (opcional, para respuestas con IA real)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

## Comandos Durante la Conversación

| Comando | Descripción |
|---------|-------------|
| `/ayuda` | Ver comandos disponibles |
| `/productos` | Ver catálogo de productos |
| `/perfil` | Ver perfil del cliente actual |
| `/resumen` | Ver resumen de la conversación |
| `/reiniciar` | Iniciar nueva conversación |
| `/salir` | Finalizar y salir |

## Estructura del Proyecto

```
iagent/
├── main.py              # Entrada principal (interfaz rica)
├── simple_chat.py       # Interfaz simple
├── web_app.py           # Interfaz web
├── setup.py             # Script de instalación
├── requirements.txt     # Dependencias
├── .env.example         # Ejemplo de configuración
│
├── config/              # Configuración
│   ├── settings.py      # Configuración general
│   └── products.py      # Catálogo de productos
│
├── core/                # Núcleo del agente
│   ├── agent.py         # Agente principal
│   ├── conversation.py  # Gestión de conversación
│   └── customer_profile.py  # Perfilamiento de clientes
│
├── ui/                  # Interfaces de usuario
│   └── console.py       # UI de consola
│
├── utils/               # Utilidades
│   ├── helpers.py       # Funciones auxiliares
│   └── analytics.py     # Sistema de analytics
│
├── integrations/        # Integraciones externas
│   ├── crm.py           # Integración CRM
│   ├── email.py         # Notificaciones email
│   └── webhook.py       # Sistema de webhooks
│
└── data/                # Datos (generado)
    ├── leads.json       # Leads capturados
    └── analytics.json   # Datos de analytics
```

## Productos Incluidos

El agente viene preconfigurado con estos productos:

1. **Agente de Atención al Cliente 24/7** - $299/mes
2. **Agente de Ventas Inteligente** - $499/mes
3. **Agente de Recursos Humanos** - $399/mes
4. **Tutor IA Personalizado** - $349/mes
5. **Asistente Legal IA** - $599/mes
6. **Asistente Médico IA** - $699/mes
7. **Agente Personalizado** - Cotización

## Personalización

### Cambiar Productos

Edita `config/products.py` para agregar, modificar o eliminar productos del catálogo.

### Modificar Comportamiento

Edita `core/conversation.py` para ajustar el prompt del sistema y la personalidad del agente.

### Agregar Integraciones

Usa los módulos en `integrations/` como base para conectar con tu CRM, email o webhooks.

## Ejemplo de Uso

```
╔══════════════════════════════════════════════════════════════╗
║       🤖  AGENTE VENDEDOR DE IA  🤖                          ║
║           IAgentic Solutions                                  ║
╚══════════════════════════════════════════════════════════════╝

┌─ Luna ──────────────────────────────────────────────────────┐
│ ¡Hola! Soy Luna, tu asesora de soluciones de IA.           │
│                                                              │
│ ¿Me cuentas un poco sobre ti y tu empresa?                  │
└─────────────────────────────────────────────────────────────┘

>>> Tengo una tienda online de ropa y necesito mejorar la atención

┌─ Luna ──────────────────────────────────────────────────────┐
│ ¡El retail es fascinante! Con el e-commerce, la atención   │
│ al cliente es clave para diferenciarse.                     │
│                                                              │
│ ¿Cuál es tu mayor desafío: responder consultas rápido,     │
│ manejar devoluciones, o dar seguimiento post-venta?        │
└─────────────────────────────────────────────────────────────┘
```

## Licencia

MIT License - Úsalo libremente para tu negocio.

## Soporte

Para soporte o personalización, contacta al desarrollador.

---

Desarrollado con Python y amor por la IA

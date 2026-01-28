"""Interpretador inteligente de mensajes del usuario."""

import re
from typing import Dict, List, Optional, Tuple
from enum import Enum


class UserIntent(Enum):
    """Intenciones detectables del usuario."""
    AFFIRMATIVE = "affirmative"  # Sí, acepto, me interesa
    NEGATIVE = "negative"  # No, después, no me interesa
    OPTION_SELECT = "option_select"  # Selecciona una opción específica
    PRICE_INQUIRY = "price_inquiry"  # Pregunta por precio
    TIME_INQUIRY = "time_inquiry"  # Pregunta por tiempo
    DOUBT = "doubt"  # Tiene dudas
    MORE_INFO = "more_info"  # Quiere más información
    PROBLEM = "problem"  # Describe un problema
    AUTOMATION = "automation"  # Interés en automatización
    UNKNOWN = "unknown"


class MessageInterpreter:
    """Interpreta mensajes del usuario de forma flexible y natural."""

    def __init__(self):
        # Mapeo de palabras con tildes y variaciones
        self._char_map = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'ü': 'u', 'ñ': 'n'
        }

        # Patrones de afirmación (más completos)
        self._affirmative_patterns = [
            # Palabras directas
            r'\bsi\b', r'\bsip\b', r'\bsep\b', r'\byes\b', r'\bsii+\b',
            r'\bok\b', r'\bokay\b', r'\bokey\b', r'\boka\b',
            r'\bdale\b', r'\bdale dale\b', r'\bdalee+\b',
            r'\bvamos\b', r'\bva\b', r'\bvenga\b',
            r'\bacepto\b', r'\baceptar\b', r'\baceptado\b',
            r'\bclaro\b', r'\bclaramente\b', r'\bpor supuesto\b',
            r'\bperfecto\b', r'\bexcelente\b', r'\bgenial\b', r'\bsuper\b',
            r'\bbueno\b', r'\bbien\b', r'\bmuy bien\b',
            r'\bde acuerdo\b', r'\bdeacuerdo\b', r'\bme parece\b',
            r'\bhecho\b', r'\blisto\b', r'\bva que va\b',
            r'\bme gusta\b', r'\bme encanta\b', r'\bme agrada\b',
            r'\bconfirmado\b', r'\bconfirmo\b',
            r'\bprocedamos\b', r'\badelante\b', r'\bhagamoslo\b',
            # Frases de interés
            r'\bme interesa\b', r'\binteresante\b', r'\bsuena bien\b',
            r'\bsuena interesante\b', r'\bme llama la atencion\b',
            r'\bquiero\b', r'\bquisiera\b', r'\bme gustaria\b',
            r'\bcuenta conmigo\b', r'\bestoy dentro\b',
            r'\bpor favor\b', r'\bporfavor\b',
        ]

        # Patrones de negación (más completos)
        self._negative_patterns = [
            r'\bno\b(?! me| te| se| hay| tengo)',  # "no" pero no "no me interesa"
            r'^no$', r'^no,', r'^no\.', r'\bno gracias\b',
            r'\bdespues\b', r'\bluego\b', r'\bmas tarde\b', r'\botra vez\b',
            r'\bpensare\b', r'\bpensar\b', r'\blo pienso\b', r'\bdejame pensar\b',
            r'\bpensarlo\b', r'\blo pensare\b', r'\bvoy a pensar\b',
            r'\bconsultar\b', r'\bconsultarlo\b', r'\bpreguntar\b', r'\btengo que ver\b',
            r'\btengo que consultar\b', r'\bdebo consultar\b', r'\bvoy a consultar\b',
            r'\bno estoy seguro\b', r'\bno se\b', r'\bni idea\b',
            r'\bquiza\b', r'\btal vez\b', r'\ba lo mejor\b',
            r'\bpor ahora no\b', r'\btodavia no\b', r'\baun no\b',
            r'\bno creo\b', r'\bno puedo\b', r'\bno me convence\b',
            r'\bno me interesa\b', r'\bno es para mi\b',
            r'\bno es lo que busco\b', r'\bno aplica\b',
            r'\bmmm\b', r'\bhmm\b', r'\behh\b',  # Expresiones de duda
            r'\bdejame\b.*\bpensar\b', r'\btengo que\b.*\bpensar\b',
        ]

        # Patrones para detectar selección de opciones
        self._option_patterns = {
            1: [
                r'\b(la |el |opcion |numero )?1\b', r'\buno\b', r'\buna\b',
                r'\b(la |el )?primer[ao]?\b', r'\bprimera opcion\b',
                r'\batencion\b', r'\b24.?7\b', r'\bsoporte\b',
                r'\bconsultas\b', r'\bresponder consultas\b'
            ],
            2: [
                r'\b(la |el |opcion |numero )?2\b', r'\bdos\b',
                r'\b(la |el )?segund[ao]?\b', r'\bsegunda opcion\b',
                r'\bventas\b', r'\bleads\b', r'\bconversiones\b',
                r'\bcalificar\b', r'\bvender\b'
            ],
            3: [
                r'\b(la |el |opcion |numero )?3\b', r'\btres\b',
                r'\b(la |el )?tercer[ao]?\b', r'\btercera opcion\b',
                r'\bpersonalizad[ao]\b', r'\ba medida\b', r'\bcustom\b',
                r'\bespecifico\b', r'\bunico\b'
            ]
        }

        # Patrones para precio
        self._price_patterns = [
            r'\bprecio\b', r'\bcosto\b', r'\bcuanto\b', r'\bvalor\b',
            r'\bpresupuesto\b', r'\binversion\b', r'\bdinero\b',
            r'\bcuanto cuesta\b', r'\bcuanto vale\b', r'\bque precio\b',
            r'\bcuanto sale\b', r'\bcuanto seria\b', r'\btarifa\b',
            r'\bpagaria\b', r'\bpagar\b', r'\bbarato\b', r'\bcaro\b',
            r'\beconomico\b', r'\bcostoso\b', r'\bprecio accesible\b'
        ]

        # Patrones para tiempo
        self._time_patterns = [
            r'\btiempo\b', r'\bcuanto tarda\b', r'\bdemora\b',
            r'\brapido\b', r'\bplazo\b', r'\bcuando\b',
            r'\bimplementar\b', r'\bimplementacion\b',
            r'\bcuanto tiempo\b', r'\ben cuanto tiempo\b',
            r'\bduracion\b', r'\bfecha\b', r'\burgente\b'
        ]

        # Patrones para dudas
        self._doubt_patterns = [
            r'\bfunciona\b', r'\bseguro\b', r'\bgarantia\b',
            r'\bprueba\b', r'\bdemostrar\b', r'\bconfiar\b',
            r'\bcomo se\b', r'\bcomo funciona\b', r'\bcomo es\b',
            r'\bque pasa si\b', r'\by si\b', r'\bduda\b',
            r'\bno entiendo\b', r'\bexplicar\b', r'\baclarar\b',
            r'\bpreocupa\b', r'\briesgo\b', r'\bmiedito\b'
        ]

        # Patrones para problemas/desafíos
        self._problem_patterns = [
            r'\bproblema\b', r'\bdificil\b', r'\bcomplicado\b',
            r'\breto\b', r'\bdesafio\b', r'\bdolor\b',
            r'\bfrustración\b', r'\bfrustrante\b', r'\bmolest\b',
            r'\bno funciona\b', r'\bfalla\b', r'\berror\b',
            r'\bperdemos\b', r'\bperdiendo\b', r'\bdesperdicio\b',
            r'\bmucho trabajo\b', r'\bsobrecargado\b', r'\bagotad\b'
        ]

        # Patrones para automatización
        self._automation_patterns = [
            r'\bautomatizar\b', r'\bautomatizacion\b', r'\bautomatic\b',
            r'\bia\b', r'\binteligencia artificial\b', r'\brobot\b',
            r'\bbot\b', r'\bchatbot\b', r'\bagente\b',
            r'\bproceso\b', r'\bsistema\b', r'\bherramienta\b'
        ]

    def normalize(self, text: str) -> str:
        """Normaliza el texto para comparación flexible."""
        if not text:
            return ""

        # Convertir a minúsculas
        text = text.lower().strip()

        # Reemplazar caracteres acentuados
        for accented, normal in self._char_map.items():
            text = text.replace(accented, normal)

        # Eliminar puntuación excesiva pero mantener estructura
        text = re.sub(r'[¿¡!?.,;:]+', ' ', text)

        # Normalizar espacios múltiples
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    def _matches_any(self, text: str, patterns: List[str]) -> bool:
        """Verifica si el texto coincide con algún patrón."""
        normalized = self.normalize(text)
        for pattern in patterns:
            if re.search(pattern, normalized, re.IGNORECASE):
                return True
        return False

    def detect_intent(self, message: str) -> Tuple[UserIntent, float]:
        """
        Detecta la intención principal del mensaje.
        Retorna (intención, confianza 0-1).
        """
        normalized = self.normalize(message)

        # Verificar negación primero (tiene prioridad)
        if self._matches_any(message, self._negative_patterns):
            # Pero verificar si hay afirmación más fuerte
            if not self._matches_any(message, self._affirmative_patterns):
                return (UserIntent.NEGATIVE, 0.9)

        # Verificar afirmación
        if self._matches_any(message, self._affirmative_patterns):
            return (UserIntent.AFFIRMATIVE, 0.9)

        # Verificar selección de opción
        for option_num, patterns in self._option_patterns.items():
            if self._matches_any(message, patterns):
                return (UserIntent.OPTION_SELECT, 0.85)

        # Verificar precio
        if self._matches_any(message, self._price_patterns):
            return (UserIntent.PRICE_INQUIRY, 0.85)

        # Verificar tiempo
        if self._matches_any(message, self._time_patterns):
            return (UserIntent.TIME_INQUIRY, 0.8)

        # Verificar dudas
        if self._matches_any(message, self._doubt_patterns):
            return (UserIntent.DOUBT, 0.75)

        # Verificar problemas
        if self._matches_any(message, self._problem_patterns):
            return (UserIntent.PROBLEM, 0.8)

        # Verificar automatización
        if self._matches_any(message, self._automation_patterns):
            return (UserIntent.AUTOMATION, 0.8)

        return (UserIntent.UNKNOWN, 0.0)

    def detect_selected_option(self, message: str) -> Optional[int]:
        """
        Detecta si el usuario seleccionó una opción específica (1, 2 o 3).
        Retorna el número de opción o None si no se detectó.
        """
        normalized = self.normalize(message)

        for option_num, patterns in self._option_patterns.items():
            for pattern in patterns:
                if re.search(pattern, normalized, re.IGNORECASE):
                    return option_num

        return None

    def is_affirmative(self, message: str) -> bool:
        """Determina si el mensaje es una respuesta afirmativa."""
        intent, confidence = self.detect_intent(message)
        return intent == UserIntent.AFFIRMATIVE and confidence > 0.5

    def is_negative(self, message: str) -> bool:
        """Determina si el mensaje es una respuesta negativa."""
        intent, confidence = self.detect_intent(message)
        return intent == UserIntent.NEGATIVE and confidence > 0.5

    def is_price_inquiry(self, message: str) -> bool:
        """Determina si el usuario pregunta por precio."""
        return self._matches_any(message, self._price_patterns)

    def is_time_inquiry(self, message: str) -> bool:
        """Determina si el usuario pregunta por tiempo."""
        return self._matches_any(message, self._time_patterns)

    def has_doubt(self, message: str) -> bool:
        """Determina si el usuario tiene dudas."""
        return self._matches_any(message, self._doubt_patterns)

    def mentions_problem(self, message: str) -> bool:
        """Determina si el usuario menciona un problema."""
        return self._matches_any(message, self._problem_patterns)

    def mentions_automation(self, message: str) -> bool:
        """Determina si el usuario menciona automatización/IA."""
        return self._matches_any(message, self._automation_patterns)

    def extract_keywords(self, message: str) -> List[str]:
        """Extrae palabras clave relevantes del mensaje."""
        normalized = self.normalize(message)

        # Palabras a ignorar
        stopwords = {
            'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
            'de', 'del', 'al', 'a', 'en', 'con', 'por', 'para',
            'que', 'se', 'es', 'son', 'esta', 'este', 'esto',
            'y', 'o', 'pero', 'si', 'no', 'me', 'te', 'mi', 'tu',
            'muy', 'mas', 'como', 'cuando', 'donde', 'porque',
            'hay', 'tiene', 'tengo', 'hacer', 'hago'
        }

        words = normalized.split()
        keywords = [w for w in words if len(w) > 2 and w not in stopwords]

        return keywords


# Instancia global para fácil acceso
interpreter = MessageInterpreter()

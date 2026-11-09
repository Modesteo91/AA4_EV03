"""Lógica del asistente virtual: interpreta el mensaje y construye la respuesta.

Estrategia (reglas simples, sin IA externa):
1. Si el mensaje contiene un código de pedido (GEN-0000) -> responde su estado.
2. Si no, busca la pregunta frecuente con más palabras clave coincidentes.
3. Si nada coincide -> respuesta por defecto invitando a reformular.
"""
import re
import unicodedata

PATRON_CODIGO = re.compile(r"\bGEN-\d{4}\b", re.IGNORECASE)

RESPUESTA_POR_DEFECTO = (
    "No estoy seguro de haber entendido. Puedes preguntarme por horarios, "
    "servicios, tiempos de entrega, precios o el estado de un pedido."
)


def normalizar(texto):
    """Pasa a minúsculas y quita tildes para comparar sin importar la escritura."""
    descompuesto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in descompuesto if unicodedata.category(c) != "Mn")


def extraer_codigo_pedido(mensaje):
    """Devuelve el código de pedido en mayúsculas, o None si no hay uno."""
    coincidencia = PATRON_CODIGO.search(mensaje)
    return coincidencia.group(0).upper() if coincidencia else None


def puntuar_faq(mensaje_normalizado, palabras_clave):
    """Cuenta cuántas palabras clave de la FAQ aparecen en el mensaje."""
    claves = [normalizar(k).strip() for k in palabras_clave.split(",")]
    return sum(1 for clave in claves if clave and clave in mensaje_normalizado)


def respuesta_pedido(pedido):
    """Arma el texto con el estado de un pedido."""
    return (
        f"Tu pedido {pedido['codigo']} ({pedido['tipo_trabajo']}) está en estado "
        f"«{pedido['estado']}». Fecha estimada de entrega: {pedido['fecha_entrega']}."
    )


def responder(conexion, mensaje):
    """Genera la respuesta del asistente para un mensaje del cliente."""
    codigo = extraer_codigo_pedido(mensaje)
    if codigo:
        pedido = conexion.execute(
            "SELECT * FROM pedidos WHERE codigo = ?", (codigo,)
        ).fetchone()
        if pedido is None:
            return f"No encontré ningún pedido con el código {codigo}. Verifica el número."
        return respuesta_pedido(pedido)

    texto = normalizar(mensaje)
    mejor_respuesta, mejor_puntaje = RESPUESTA_POR_DEFECTO, 0
    for faq in conexion.execute("SELECT * FROM faqs ORDER BY id"):
        puntaje = puntuar_faq(texto, faq["palabras_clave"])
        if puntaje > mejor_puntaje:
            mejor_respuesta, mejor_puntaje = faq["respuesta"], puntaje
    return mejor_respuesta

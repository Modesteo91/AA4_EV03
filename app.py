"""Módulo Asistente Virtual – Laboratorio Dental Genesis (AA4_EV03).

Servicios REST (prefijo /api/v1):
    POST   /chat                   Envía un mensaje y recibe la respuesta
    GET    /conversaciones         Historial de las últimas conversaciones
    GET    /pedidos/<codigo>       Estado de un pedido
    GET    /faqs                   Lista las preguntas frecuentes
    POST   /faqs                   Crea una pregunta frecuente
    PUT    /faqs/<id>              Actualiza una pregunta frecuente
    DELETE /faqs/<id>              Elimina una pregunta frecuente
"""
import os

from flask import Blueprint, Flask, jsonify, render_template, request

import chatbot
import db

LIMITE_MENSAJE = 300
LIMITE_CAMPO_FAQ = 500

api = Blueprint("api", __name__, url_prefix="/api/v1")


def error(mensaje, codigo):
    """Respuesta de error uniforme en JSON."""
    return jsonify({"ok": False, "mensaje": mensaje}), codigo


def leer_faq(datos):
    """Valida el cuerpo de una FAQ. Devuelve (campos, mensaje_de_error)."""
    campos = {}
    for nombre in ("palabras_clave", "pregunta", "respuesta"):
        valor = datos.get(nombre)
        if not isinstance(valor, str) or not valor.strip():
            return None, f"El campo '{nombre}' es obligatorio"
        if len(valor) > LIMITE_CAMPO_FAQ:
            return None, f"El campo '{nombre}' supera {LIMITE_CAMPO_FAQ} caracteres"
        campos[nombre] = valor.strip()
    return campos, None


# ---------------------------------------------------------------- Chat
@api.post("/chat")
def chat():
    """Recibe el mensaje del cliente, responde y guarda la conversación."""
    datos = request.get_json(silent=True) or {}
    mensaje = datos.get("mensaje")
    if not isinstance(mensaje, str) or not mensaje.strip():
        return error("El mensaje no puede estar vacío", 400)
    if len(mensaje) > LIMITE_MENSAJE:
        return error(f"El mensaje supera {LIMITE_MENSAJE} caracteres", 400)

    conexion = db.get_db()
    respuesta = chatbot.responder(conexion, mensaje.strip())
    conexion.execute(
        "INSERT INTO conversaciones (mensaje, respuesta) VALUES (?, ?)",
        (mensaje.strip(), respuesta),
    )
    conexion.commit()
    return jsonify({"ok": True, "respuesta": respuesta}), 200


@api.get("/conversaciones")
def conversaciones():
    """Devuelve las últimas 50 conversaciones (la más reciente primero)."""
    filas = db.get_db().execute(
        "SELECT id, mensaje, respuesta, fecha FROM conversaciones "
        "ORDER BY id DESC LIMIT 50"
    ).fetchall()
    return jsonify({"ok": True, "conversaciones": [dict(f) for f in filas]}), 200


# ------------------------------------------------------------- Pedidos
@api.get("/pedidos/<codigo>")
def pedido(codigo):
    """Consulta el estado de un pedido por su código."""
    fila = db.get_db().execute(
        "SELECT * FROM pedidos WHERE codigo = ?", (codigo.upper(),)
    ).fetchone()
    if fila is None:
        return error("Pedido no encontrado", 404)
    return jsonify({"ok": True, "pedido": dict(fila)}), 200


# ---------------------------------------------------------------- FAQs
@api.get("/faqs")
def listar_faqs():
    """Lista todas las preguntas frecuentes."""
    filas = db.get_db().execute("SELECT * FROM faqs ORDER BY id").fetchall()
    return jsonify({"ok": True, "faqs": [dict(f) for f in filas]}), 200


@api.post("/faqs")
def crear_faq():
    """Crea una pregunta frecuente nueva."""
    campos, mensaje = leer_faq(request.get_json(silent=True) or {})
    if mensaje:
        return error(mensaje, 400)
    conexion = db.get_db()
    cursor = conexion.execute(
        "INSERT INTO faqs (palabras_clave, pregunta, respuesta) VALUES (?, ?, ?)",
        (campos["palabras_clave"], campos["pregunta"], campos["respuesta"]),
    )
    conexion.commit()
    return jsonify({"ok": True, "id": cursor.lastrowid}), 201


@api.put("/faqs/<int:faq_id>")
def actualizar_faq(faq_id):
    """Actualiza una pregunta frecuente existente."""
    campos, mensaje = leer_faq(request.get_json(silent=True) or {})
    if mensaje:
        return error(mensaje, 400)
    conexion = db.get_db()
    cursor = conexion.execute(
        "UPDATE faqs SET palabras_clave = ?, pregunta = ?, respuesta = ? WHERE id = ?",
        (campos["palabras_clave"], campos["pregunta"], campos["respuesta"], faq_id),
    )
    conexion.commit()
    if cursor.rowcount == 0:
        return error("Pregunta frecuente no encontrada", 404)
    return jsonify({"ok": True, "mensaje": "Pregunta actualizada"}), 200


@api.delete("/faqs/<int:faq_id>")
def eliminar_faq(faq_id):
    """Elimina una pregunta frecuente."""
    conexion = db.get_db()
    cursor = conexion.execute("DELETE FROM faqs WHERE id = ?", (faq_id,))
    conexion.commit()
    if cursor.rowcount == 0:
        return error("Pregunta frecuente no encontrada", 404)
    return jsonify({"ok": True, "mensaje": "Pregunta eliminada"}), 200


# ------------------------------------------------------------- Fábrica
def create_app(config=None):
    """Crea y configura la aplicación (permite usar otra BD en las pruebas)."""
    app = Flask(__name__)
    app.config["DATABASE"] = os.environ.get("DATABASE", "genesis.db")
    app.json.ensure_ascii = False  # respuestas JSON con tildes y ñ
    if config:
        app.config.update(config)

    app.teardown_appcontext(db.close_db)
    app.register_blueprint(api)

    @app.get("/")
    def inicio():
        """Página principal con el chat y el panel de preguntas frecuentes."""
        return render_template("index.html")

    @app.errorhandler(404)
    def no_encontrado(_e):
        return error("Ruta no encontrada", 404)

    with app.app_context():
        db.init_db()
    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=True)

"""Acceso a datos del módulo Asistente Virtual (SQLite)."""
import os
import sqlite3

from flask import current_app, g

RUTA_ESQUEMA = os.path.join(os.path.dirname(__file__), "schema.sql")

# Datos iniciales para que el asistente funcione desde el primer arranque.
FAQS_INICIALES = [
    ("hola,buenas,buenos dias,buenas tardes", "Saludo",
     "¡Hola! Soy el asistente de Laboratorio Dental Genesis. Puedo ayudarte con "
     "horarios, servicios, tiempos de entrega o el estado de tu pedido "
     "(escribe tu código, por ejemplo GEN-1001)."),
    ("horario,atencion,abren,cierran,hora", "¿Cuál es el horario de atención?",
     "Atendemos de lunes a viernes de 8:00 a. m. a 6:00 p. m. y los sábados "
     "de 8:00 a. m. a 1:00 p. m."),
    ("servicio,servicios,trabajos,ofrecen,hacen", "¿Qué servicios ofrecen?",
     "Elaboramos coronas de zirconio y porcelana, carillas, prótesis removibles, "
     "puentes fijos y guardas oclusales."),
    ("entrega,demora,tiempo,tarda,dias", "¿Cuánto tarda un trabajo?",
     "El tiempo habitual es de 3 a 7 días hábiles según el tipo de trabajo."),
    ("precio,costo,cuanto cuesta,valor,tarifa", "¿Cuáles son los precios?",
     "Los valores dependen del material y del tipo de trabajo. Escríbenos con "
     "tu solicitud y un asesor te enviará la cotización."),
]

PEDIDOS_INICIALES = [
    ("GEN-1001", "Clínica Sonrisa", "Corona de zirconio", "En proceso", "2026-11-12"),
    ("GEN-1002", "Dr. Ramírez", "Prótesis removible", "Listo para recoger", "2026-11-09"),
    ("GEN-1003", "Odontología Andina", "Carillas de porcelana", "Recibido", "2026-11-18"),
]


def get_db():
    """Devuelve la conexión de la petición actual (se crea una sola vez)."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_error=None):
    """Cierra la conexión al terminar la petición."""
    conexion = g.pop("db", None)
    if conexion is not None:
        conexion.close()


def init_db():
    """Crea las tablas y carga los datos iniciales si están vacías."""
    conexion = get_db()
    with open(RUTA_ESQUEMA, encoding="utf-8") as archivo:
        conexion.executescript(archivo.read())

    if conexion.execute("SELECT COUNT(*) FROM faqs").fetchone()[0] == 0:
        conexion.executemany(
            "INSERT INTO faqs (palabras_clave, pregunta, respuesta) VALUES (?, ?, ?)",
            FAQS_INICIALES,
        )
    if conexion.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0] == 0:
        conexion.executemany(
            "INSERT INTO pedidos VALUES (?, ?, ?, ?, ?)", PEDIDOS_INICIALES
        )
    conexion.commit()

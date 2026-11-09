"""Pruebas automáticas del módulo. Ejecutar con: python -m pytest -v"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app  # noqa: E402

BASE = "/api/v1"


@pytest.fixture()
def cliente(tmp_path):
    """Cliente de pruebas con una base de datos temporal nueva."""
    app = create_app({"DATABASE": str(tmp_path / "prueba.db"), "TESTING": True})
    with app.test_client() as c:
        yield c


def preguntar(cliente, texto):
    return cliente.post(f"{BASE}/chat", json={"mensaje": texto})


def test_pagina_principal(cliente):
    assert cliente.get("/").status_code == 200


def test_chat_responde_faq_sin_importar_tildes(cliente):
    r = preguntar(cliente, "¿Cuál es el HORARIO de atención?")
    assert r.status_code == 200
    assert "lunes a viernes" in r.get_json()["respuesta"]


def test_chat_estado_de_pedido(cliente):
    r = preguntar(cliente, "quiero saber de gen-1001")
    assert "En proceso" in r.get_json()["respuesta"]


def test_chat_pedido_inexistente(cliente):
    r = preguntar(cliente, "GEN-9999")
    assert "No encontré" in r.get_json()["respuesta"]


def test_chat_respuesta_por_defecto(cliente):
    r = preguntar(cliente, "xyz qwerty")
    assert "No estoy seguro" in r.get_json()["respuesta"]


def test_chat_valida_mensaje(cliente):
    assert preguntar(cliente, "   ").status_code == 400
    assert preguntar(cliente, "a" * 301).status_code == 400


def test_historial_guarda_conversaciones(cliente):
    preguntar(cliente, "hola")
    datos = cliente.get(f"{BASE}/conversaciones").get_json()
    assert len(datos["conversaciones"]) == 1


def test_consultar_pedido(cliente):
    assert cliente.get(f"{BASE}/pedidos/GEN-1002").status_code == 200
    assert cliente.get(f"{BASE}/pedidos/GEN-0000").status_code == 404


def test_crud_faqs(cliente):
    nueva = {"palabras_clave": "garantia", "pregunta": "¿Tienen garantía?",
             "respuesta": "Sí, 1 año."}
    # Crear
    creada = cliente.post(f"{BASE}/faqs", json=nueva)
    assert creada.status_code == 201
    faq_id = creada.get_json()["id"]
    # Usarla en el chat
    assert "1 año" in preguntar(cliente, "tienen garantia?").get_json()["respuesta"]
    # Actualizar
    nueva["respuesta"] = "Sí, 2 años."
    assert cliente.put(f"{BASE}/faqs/{faq_id}", json=nueva).status_code == 200
    assert "2 años" in preguntar(cliente, "garantia").get_json()["respuesta"]
    # Eliminar
    assert cliente.delete(f"{BASE}/faqs/{faq_id}").status_code == 200
    assert cliente.delete(f"{BASE}/faqs/{faq_id}").status_code == 404


def test_faq_valida_campos(cliente):
    r = cliente.post(f"{BASE}/faqs", json={"pregunta": "solo pregunta"})
    assert r.status_code == 400

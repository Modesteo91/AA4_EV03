/**
 * Lógica del cliente (navegador) del módulo Asistente Virtual.
 * Estilo: Google JavaScript Style Guide (const/let, camelCase, comillas simples).
 */
'use strict';

const API = '/api/v1';

const contenedorMensajes = document.getElementById('mensajes');
const formularioChat = document.getElementById('formulario-chat');
const entradaMensaje = document.getElementById('entrada-mensaje');
const formularioFaq = document.getElementById('formulario-faq');
const listaFaq = document.getElementById('lista-faq');
const estadoFaq = document.getElementById('estado-faq');

/**
 * Envía una petición JSON a la API y devuelve el cuerpo ya convertido.
 * @param {string} ruta Ruta relativa a /api/v1.
 * @param {string=} metodo Método HTTP (por defecto GET).
 * @param {Object=} cuerpo Datos a enviar como JSON.
 * @return {Promise<Object>} Respuesta de la API.
 */
async function pedirApi(ruta, metodo = 'GET', cuerpo = undefined) {
  const respuesta = await fetch(API + ruta, {
    method: metodo,
    headers: {'Content-Type': 'application/json'},
    body: cuerpo ? JSON.stringify(cuerpo) : undefined,
  });
  return respuesta.json();
}

/**
 * Agrega una burbuja de texto al chat.
 * Se usa textContent (no innerHTML) para evitar inyección de HTML (XSS).
 * @param {string} texto Contenido del mensaje.
 * @param {string} autor 'usuario' o 'asistente'.
 */
function agregarMensaje(texto, autor) {
  const burbuja = document.createElement('div');
  burbuja.className = 'burbuja ' + autor;
  burbuja.textContent = texto;
  contenedorMensajes.appendChild(burbuja);
  contenedorMensajes.scrollTop = contenedorMensajes.scrollHeight;
}

/** Envía el mensaje escrito y muestra la respuesta del asistente. */
async function enviarMensaje(evento) {
  evento.preventDefault();
  const texto = entradaMensaje.value.trim();
  if (!texto) {
    return;
  }
  agregarMensaje(texto, 'usuario');
  entradaMensaje.value = '';

  try {
    const datos = await pedirApi('/chat', 'POST', {mensaje: texto});
    agregarMensaje(datos.respuesta || datos.mensaje, 'asistente');
  } catch (error) {
    agregarMensaje('No pude conectarme con el servidor. Intenta de nuevo.', 'asistente');
  }
}

/** Dibuja la lista de preguntas frecuentes con su botón de eliminar. */
async function cargarFaqs() {
  const datos = await pedirApi('/faqs');
  listaFaq.innerHTML = '';
  for (const faq of datos.faqs) {
    const item = document.createElement('li');
    const texto = document.createElement('span');
    texto.textContent = faq.pregunta;

    const botonEliminar = document.createElement('button');
    botonEliminar.type = 'button';
    botonEliminar.textContent = 'Eliminar';
    botonEliminar.addEventListener('click', () => eliminarFaq(faq.id));

    item.append(texto, botonEliminar);
    listaFaq.appendChild(item);
  }
}

/** Crea una pregunta frecuente con los datos del formulario. */
async function crearFaq(evento) {
  evento.preventDefault();
  const datos = await pedirApi('/faqs', 'POST', {
    palabras_clave: document.getElementById('faq-clave').value,
    pregunta: document.getElementById('faq-pregunta').value,
    respuesta: document.getElementById('faq-respuesta').value,
  });
  estadoFaq.textContent = datos.ok ? 'Pregunta agregada.' : datos.mensaje;
  if (datos.ok) {
    formularioFaq.reset();
    cargarFaqs();
  }
}

/**
 * Elimina una pregunta frecuente.
 * @param {number} id Identificador de la pregunta.
 */
async function eliminarFaq(id) {
  const datos = await pedirApi('/faqs/' + id, 'DELETE');
  estadoFaq.textContent = datos.mensaje;
  cargarFaqs();
}

// Inicio: eventos y carga inicial.
formularioChat.addEventListener('submit', enviarMensaje);
formularioFaq.addEventListener('submit', crearFaq);
agregarMensaje('¡Hola! Soy el asistente de Genesis. ¿En qué puedo ayudarte?', 'asistente');
cargarFaqs();

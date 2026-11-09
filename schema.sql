-- Esquema de base de datos del módulo Asistente Virtual (Genesis)
-- Convención: tablas en plural y snake_case, claves primarias "id".

-- Preguntas frecuentes que el asistente sabe responder.
CREATE TABLE IF NOT EXISTS faqs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    palabras_clave TEXT NOT NULL,   -- separadas por coma: "horario,atencion,abren"
    pregunta TEXT NOT NULL,
    respuesta TEXT NOT NULL
);

-- Pedidos de trabajos del laboratorio dental (consultables por código).
CREATE TABLE IF NOT EXISTS pedidos (
    codigo TEXT PRIMARY KEY,        -- formato GEN-0000
    cliente TEXT NOT NULL,
    tipo_trabajo TEXT NOT NULL,
    estado TEXT NOT NULL,           -- Recibido | En proceso | Listo para recoger
    fecha_entrega TEXT NOT NULL     -- AAAA-MM-DD
);

-- Historial de las conversaciones atendidas por el asistente.
CREATE TABLE IF NOT EXISTS conversaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mensaje TEXT NOT NULL,
    respuesta TEXT NOT NULL,
    fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

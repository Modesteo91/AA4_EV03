# Módulo Asistente Virtual – Laboratorio Dental Genesis (AA4_EV03)

**Aprendiz:** Alejandro Sepúlveda Ardila
**Programa:** Análisis y desarrollo de software – Ficha 3336915

Módulo web del chatbot de atención al cliente de Genesis, desarrollado con **Python + Flask + SQLite** y una interfaz en **HTML/CSS/JavaScript**.

## Qué hace el módulo

- **Chat:** responde preguntas sobre horarios, servicios, tiempos de entrega y precios.
- **Estado de pedidos:** si el cliente escribe un código (ej. `GEN-1001`), responde el estado y la fecha de entrega.
- **Preguntas frecuentes (CRUD):** el administrador crea, consulta, actualiza y elimina las respuestas del asistente.
- **Historial:** guarda cada conversación.

## Estructura

```
├── app.py                 # Rutas REST y fábrica de la aplicación
├── chatbot.py             # Lógica de interpretación y respuesta
├── db.py                  # Conexión y datos iniciales (SQLite)
├── schema.sql             # Tablas: faqs, pedidos, conversaciones
├── templates/index.html   # Vista (chat + panel de FAQ)
├── static/css/styles.css  # Estilos
├── static/js/chat.js      # Lógica del navegador
├── tests/test_modulo.py   # 10 pruebas automáticas
├── docs/ARTEFACTOS.md     # Trazabilidad con historias de usuario, casos de uso y clases
└── ENLACE_REPOSITORIO.txt
```

## Ejecución

```bash
pip install -r requirements.txt
python app.py
```

Abrir en el navegador: http://127.0.0.1:5000

## Servicios (prefijo `/api/v1`)

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/chat` | Envía `{"mensaje": "..."}` y recibe la respuesta |
| GET | `/conversaciones` | Últimas 50 conversaciones |
| GET | `/pedidos/<codigo>` | Estado de un pedido |
| GET | `/faqs` | Lista las preguntas frecuentes |
| POST | `/faqs` | Crea una (`palabras_clave`, `pregunta`, `respuesta`) |
| PUT | `/faqs/<id>` | Actualiza una |
| DELETE | `/faqs/<id>` | Elimina una |

Códigos de pedido de ejemplo: `GEN-1001`, `GEN-1002`, `GEN-1003`.

## Pruebas

```bash
python -m pytest -v
```

## Versionamiento

Proyecto gestionado con Git (commits por componente). Enlace del repositorio en `ENLACE_REPOSITORIO.txt`.

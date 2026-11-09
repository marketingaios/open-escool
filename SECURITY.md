# Seguridad

Open Escool funciona en tu ordenador: el servidor escucha solo en `127.0.0.1`. El acceso desde el teléfono, si lo activas,
abre la red de casa con un código. Las claves están en `.env` y nunca salen de tu ordenador, salvo hacia el servicio al que
pertenecen (YouTube, Gemini, Tavily, ElevenLabs).

## Cómo avisar de un problema de seguridad
**No abras una incidencia pública.** Usa el aviso privado de GitHub: pestaña **Security** → **Report a vulnerability**.
Describe qué has encontrado, cómo reproducirlo y qué puede hacer quien lo aproveche. No incluyas claves reales.

No hay compromiso de tiempos de respuesta. Los avisos serios (alguien de fuera puede leer notas o claves, o ejecutar
órdenes en tu ordenador) se miran primero.

## Qué está dentro del alcance
- El servidor local (`accademia.py`): rutas de archivos, órdenes que abren el terminal, acceso desde el teléfono.
- Las herramientas de `strumenti/` que manejan claves (`chiavi.py`) o archivos descargados.

Fuera del alcance: Claude Code, Codex, Gemini, YouTube y las demás herramientas de terceros. Avisa a quien las hace.

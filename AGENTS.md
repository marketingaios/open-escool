# Open Escool · instrucciones para el asistente (Claude Code, Codex)

Open Escool es una plataforma **local y personal** de rutas de aprendizaje hechas con vídeos gratuitos (YouTube), comprobados
con las fuentes oficiales. Funciona en el ordenador de quien la usa: un pequeño servidor Python (`accademia.py`, solo biblioteca
estándar) y una página web que se instala como app (PWA). Tú, el asistente, eres el motor: creas y actualizas las rutas, respondes
a las preguntas sobre los vídeos desde el chat de la plataforma, personalizas e instalas.

## Idioma
Habla con quien usa Open Escool en el idioma de `config.json` → `lingua` (por defecto, el de `config.esempio.json`: italiano). Los
textos de los archivos internos (herramientas, guías) están en español; los nombres del código (funciones, variables, claves de los
JSON, subcomandos, opciones) y los prompts para los modelos siguen en italiano: no los traduzcas.

## Comandos (skill)
Un solo comando, **`/escool`** (en Codex `$escool`). Solo, sin palabras, muestra el estado de los cursos y el menú. Las palabras van
en inglés y valen también en italiano y en español: `create "tema"` (crea, crear) · `update <ruta> [etapa]` (aggiorna, actualizar) ·
`reinforce <ruta> <etapa>` (rinforza, reforzar) · `lesson <ruta> <etapa>` (lezione, lección) · `language <ruta> <it|es|en>`
(lingua, idioma) · `install` (installa, instalar) · `customize` (personalizza, personalizar) · `start` (avvia, iniciar) ·
`diagnose` (diagnosi, diagnóstico). Procedimiento en `.claude/skills/escool/SKILL.md` (copia idéntica en `.agents/skills/escool/SKILL.md`).

## Reglas que no se rompen
1. **Claves nunca en el chat.** Se usan `python strumenti/chiavi.py prepara|leggi NOME` (archivo temporal que solo lee el código y
   que luego se borra). No leas el archivo temporal, no imprimas `.env`, no pidas pegar claves en los mensajes.
2. **Nada de scraping de YouTube** ni descargas (yt-dlp y similares): las condiciones de uso lo prohíben. Solo la API oficial
   (`strumenti/video.py`) y el reproductor integrado. Los datos de la API (título, canal, fecha, duración, descripción) duran como mucho **30 días**
   (normas para desarrolladores III.E.4): solo están en `lavoro/youtube/metadati.json`, los renuevan la plataforma y
   `strumenti/metadati.py`; en `percorso.json` y en las fichas solo van el ID del vídeo y los textos nuestros.
3. **A Gemini solo datos públicos**: el enlace del vídeo y el mapa. Nunca las preguntas, las notas, el perfil ni el chat del usuario
   (plan gratuito: Google puede usar los contenidos). Las notas y el chat se quedan en `utente/` y solo los ves tú.
4. **Fuentes antes que vídeos.** El mapa nace de las fuentes oficiales (documentación, centros de ayuda, organismos), con la frase
   copiada para cada concepto, y el usuario lo aprueba **antes** de buscar los vídeos. Busca en la web: lo que sabes de memoria está anticuado.
5. **Di lo que no sabes.** Si las fuentes no aclaran un punto, va en las «Dudas» del mapa. Si un vídeo dice algo superado,
   la ficha lo señala y la plataforma lo muestra en «Atención».
6. **Costes.** Todo está pensado para ser gratis (API gratuitas, suscripción del asistente). Si un paso costara dinero de verdad,
   pregunta antes. Los créditos de ElevenLabs (voz de las lecciones) cuentan como gasto: primero `voce --verifica`, luego los créditos
   al usuario, luego su sí. Con el plan gratuito de ElevenLabs las lecciones son solo para uso no comercial.
7. **Mac y Windows.** Archivos siempre en UTF-8 (`encoding="utf-8"` explícito), rutas de archivo con `pathlib`, nada de comandos
   solo para Mac en las herramientas, nada de enlaces simbólicos obligatorios (Windows sin «modo de desarrollador» no los crea: copia). En Windows
   Python se llama a menudo `py`. Las lecciones funcionan también en Windows: voz gratuita en el procesador, Supertonic 3 en italiano y Kokoro en español
   e inglés (Chatterbox solo en Mac con Apple Silicon); Remotion y ffmpeg los instala `installa.ps1`.

## Dónde está cada cosa
| Qué | Dónde |
|---|---|
| servidor y páginas | `accademia.py`, `web/` |
| herramientas (claves, fuentes, vídeos, fichas, construir, diagnóstico) | `strumenti/` |
| una ruta | `percorsi/<ruta>/percorso.json`, `schede/`, `lavoro/` (mapa, fuentes, búsquedas, llamadas) |
| datos personales (notas, progreso, chat, repasos) | `utente/` (nunca en el repositorio, nunca a Gemini) |
| personalización | `config.json` (se crea a partir de `config.esempio.json`) |
| guías | `docs/chiavi.md`, `docs/mappa.md`, `docs/lezioni.md` |

Arranque: `python accademia.py --apri` → <http://127.0.0.1:8765>. Diagnóstico: `python strumenti/diagnosi.py` (para una incidencia
pública, `--condividi`). Estado de los cursos: `python strumenti/stato.py`.

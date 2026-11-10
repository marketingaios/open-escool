---
name: escool
description: Open Escool - crea, actualiza o refuerza una ruta de aprendizaje con vídeos gratuitos de YouTube verificados con las fuentes oficiales, la misma ruta en otro idioma o una lección generada para una etapa; instala, personaliza, inicia o hace el diagnóstico. Sin palabras muestra el estado de las rutas y el menú. Palabras en inglés, válidas también en italiano y español (create crea crear, update aggiorna actualizar, reinforce rinforza reforzar, lesson lezione lección, language lingua idioma, install installa instalar, customize personalizza personalizar, start avvia iniciar, diagnose diagnosi diagnóstico). Úsalo cuando la persona quiere aprender un tema, actualizar o reforzar una ruta, hacer una lección, instalar, cambiar el aspecto, abrir o revisar Open Escool.
---

# /escool — Open Escool (en Codex `$escool`)

Trabajas en la carpeta de Open Escool (la que tiene `accademia.py`). Lee antes `AGENTS.md`: sus reglas valen aquí
(claves nunca en el chat, nada de scraping de YouTube, a Gemini solo datos públicos, fuentes antes que vídeos).
Habla en el idioma de `config.json` → `lingua` (si no hay `config.json`, el de `config.esempio.json`; en el primer arranque pregúntalo).
En Windows usa `py` si `python` no responde. El nombre de un curso (`<ruta>`) va en minúsculas con guiones (p. ej. `seo-on-page`):
es su carpeta en `percorsi/`.

## Las palabras

La primera palabra después de `/escool` dice qué hacer. Mayúsculas y tildes no cuentan.

| Palabra | También vale | Qué hace |
|---|---|---|
| *(nada)* | | estado de los cursos y menú |
| `create "tema"` | crea, crear | un curso nuevo: preguntas, fuentes, mapa para aprobar, vídeos, fichas |
| `update <ruta> [etapa]` | aggiorna, actualizar | vuelve a leer las fuentes y actualiza las etapas que han cambiado |
| `reinforce <ruta> <etapa>` | rinforza, reforzar | cierra un hueco en una etapa donde quien aprende ha tenido dudas |
| `lesson <ruta> <etapa> [lingue]` | lezione, lección | una lección generada (fichas animadas y voz) para una etapa |
| `language <ruta> <it\|es\|en>` | lingua, idioma | el mismo curso con los vídeos en otro idioma |
| `install [link o cartella]` | installa, instalar | instala Open Escool |
| `customize` | personalizza, personalizar | nombre, logo, colores, idioma, disposición, asistente, perfil |
| `start` | avvia, iniciar | abre la plataforma |
| `diagnose` | diagnosi, diagnóstico | el informe para enviar a quien mantiene Open Escool |

Con `create` el tema es el resto de la línea, con o sin comillas. Si la primera palabra no es ninguna de estas pero la petición
se entiende («quiero aprender SEO on page»), es `create` con ese tema: dilo en una línea y empieza por las preguntas. Si no se
entiende, haz lo mismo que con *nada*.

## nada → estado y menú
1. `python strumenti/stato.py` y resúmelo en 3-6 líneas: los cursos, las etapas hechas y lo que queda por hacer (fuentes por
   revisar, etapas por repasar, dudas abiertas, fichas que faltan). El estado cuenta las dudas sin mostrarlas: no leas `utente/` para esto.
   Si dice que falta `config.json`, la primera propuesta es `install`.
2. Una pregunta de opción múltiple (en Codex, numerada en el texto): primero el consejo del estado, marcado como recomendado, luego
   `create`, `lesson`, `customize` u otras que sean más útiles en ese momento.
3. Ejecuta la opción elegida como si el usuario la hubiera escrito.

## create "tema"

**0. Comprobaciones** (en silencio si todo va bien)
- `python strumenti/chiavi.py stato`. Si falta `YOUTUBE_API_KEY` o `GEMINI_API_KEY`: explica en 2 líneas para qué sirve, abre la
  guía `docs/chiavi.md` en el punto adecuado, lanza `python strumenti/chiavi.py prepara NOME`, espera el «listo» y luego `leggi NOME`.
  No pidas nunca que pegue la clave en los mensajes.
- Lee `config.json` → `profilo` (nivel, objetivo, cómo quiere las explicaciones).

**1. Preguntas** (2 rondas como mucho, de opción múltiple con una opción recomendada; en Codex, numeradas en el texto)
- Meta concreta (lo que sabe hacer al final: «una campaña lista», «una web que pasa el control X»).
- **Idioma de los vídeos: uno solo por ruta**, siempre preguntado: italiano, español o inglés (recomendado el idioma de quien
  aprende; el inglés cuando sobre el tema hay pocos vídeos en su idioma). Va en `lingua_video` del mapa. Etapas, resúmenes y chat se
  quedan en el idioma de quien aprende (`lingua`, por defecto el de la interfaz). Para tener el mismo curso en otro idioma: `language`.
- Nivel de partida, tiempo total (p. ej. 1-2 h, 3-5 h), país (por normas, precios, disponibilidad), qué dejar fuera.
- Las respuestas libres a menudo contienen el requisito de verdad: reléelas antes de seguir.

**2. Fuentes oficiales** (busca en la web, no de memoria: el tema puede haber cambiado la semana pasada)
- Fuentes primarias: documentación y centro de ayuda de quien hace la herramienta, organismos y estándares, universidades. Blogs y
  vídeos solo para entender qué buscar, nunca como fuente de un concepto.
- Guárdalas en `percorsi/<ruta>/lavoro/fonti/`: con Tavily `python strumenti/fonti.py salva <ruta> URL...`; sin él, lee tú las páginas
  y guarda un `.md` por página (primera línea `URL: ...`, segunda `Letta: AAAA-MM-GG`, línea vacía, texto).
- Apunta las fechas de los cambios importantes (funciones nuevas, normas, precios, nombres cambiados): sirven para `valido_da`.

**3. Mapa** — `percorsi/<ruta>/lavoro/mappa.json` según `docs/mappa.md`, más `mappa.md` para leer.
- 4-8 etapas en el orden en que la cosa se hace de verdad; cada concepto con fuente y frase copiada; por etapa `valido_da` con el
  porqué, 3 búsquedas de YouTube en `lingua_video` (si quieres facilitar `language` después, también en los otros dos), qué debe mostrar el vídeo, errores típicos, lecturas oficiales.
- `python strumenti/fonti.py controlla <ruta>`: todas las citas deben salir encontradas; corrige las que no.
- En `mappa.md` una sección **Dudas** honesta: lo que las fuentes no aclaran o en lo que se contradicen.

**4. Aprobación** — enseña `mappa.md` (tabla de las etapas, avisos, cambios, dudas) y pregunta: apruebo / cambia algo.
Sin un sí explícito no se sigue. Con el sí, escribe `"approvata": "AAAA-MM-GG"` en el mapa.

**5. Vídeos** — `python strumenti/video.py cerca <ruta>` (gasta ~3 búsquedas por idioma y por etapa de las 100 diarias), luego
`python strumenti/video.py lista <ruta>` (propuesta de ~7 h 30 de vídeo; mantenla por debajo de ~20 vídeos: mira el límite de
Gemini en el paso 6). **Revisa la lista**: quita los vídeos que no son del tema (títulos que hablan de otra cosa), los repetidos del
mismo autor, los canales que venden cursos sin enseñar; añade a mano desde `lavoro/youtube/pertinenti.json` si una etapa se
queda sin cubrir. Guarda `lavoro/youtube/lista.json` y apunta los vídeos quitados en `lavoro/youtube/tolti_a_mano.json`
(`[{"id", "titolo", "perche"}]`): así un nuevo `lista` no los vuelve a poner.

**6. Fichas** — `python strumenti/schede.py <ruta>` (Gemini ve cada vídeo desde el enlace: 1-10 minutos por vídeo, más cuando
está sobrecargado; lánzalo en segundo plano y da una línea de estado de vez en cuando). Se puede interrumpir y volver a lanzar: se
salta las fichas hechas. Plan gratuito: **20 peticiones al día por modelo** (3.8 Flash y 3.5 Flash, ~40 en total), y **también
cuentan los errores** (los 503 de sobrecarga): con Gemini sobrecargado salen 10-15 fichas al día. Cuando la herramienta diga que
los modelos han agotado las peticiones, díselo al usuario con la hora en que se reanuda (medianoche del Pacífico: las 9:00 en Italia
y en España; para otras zonas horarias, calcúlala) y vuelve a lanzar el mismo comando después de esa hora. Para una lista que
necesita varios días está `--aspetta`: con la cuota agotada espera solo a que se reinicie y sigue (hay que dejar el ordenador
encendido: en Mac `caffeinate -i -s python3 strumenti/schede.py <ruta> --aspetta`, enchufado; en Windows el PC no debe entrar en
suspensión).

**7. Ruta** — `python strumenti/costruisci.py <ruta>`, luego lee `lavoro/scelta.md`. Revisa con ojo crítico:
empieza por «Por revisar» (fragmentos principales de menos de 3 minutos, vídeos descartados por el idioma hablado que dice
la ficha). ¿El fragmento principal de cada etapa habla de verdad de esa etapa? ¿es demasiado largo? Si no, elige a mano en
`lavoro/scelta.json` (`{"3": {"principale": "ID@1:20-9:40", "alternativi": ["ID"]}}`) y reconstruye. Las etapas sin vídeo
se quedan con «Hueco declarado» y las lecturas oficiales: dilo, no lo escondas.

**8. Entrega** — una pantalla: etapas, minutos, idiomas, huecos, qué revisar y cuándo. Abre
`http://127.0.0.1:8765/p/<ruta>` (si el servidor no está en marcha: `python accademia.py --apri`).

## update <ruta> [etapa]
1. Vuelve a leer las fuentes guardadas (mismas URL, nueva fecha de lectura) y compáralas con las antiguas: qué ha cambiado, con la fecha.
2. Actualiza el mapa: `cambi_recenti`, conceptos, `valido_da` de las etapas afectadas. Enseña al usuario **solo los cambios** y pide el ok.
3. Para las etapas cambiadas (o la indicada): `python strumenti/video.py cerca <ruta> --tappe 3,5`, revisa los nuevos
   pertinentes, añade los mejores a `lista.json`, `python strumenti/schede.py <ruta>`, `python strumenti/costruisci.py <ruta>`.
4. Las etapas no afectadas se quedan como están. `costruisci.py` actualiza la fecha de revisión (el aviso de los 30 días desaparece).

## language <ruta> <it|es|en>
La misma ruta con los vídeos en otro idioma: una ruta nueva `<ruta>-<idioma>` con el mismo mapa, ya aprobado.
1. `python strumenti/lingua.py <ruta> <idioma>`: copia mapa, fuentes y resultados de YouTube y reutiliza las fichas ya hechas de los vídeos
   hablados en ese idioma (no gastan cuota de Gemini).
   **¿Para quién es la ruta nueva?** Si es para otro país (la ruta en español, para España y América Latina), cambia `paese`
   en el mapa y reescribe los avisos y conceptos ligados al país (moneda, disponibilidad, leyes) antes de las fichas: las
   fichas escriben «para ti» para ese país, y en las reutilizadas revisa `per_chi_impara`.
2. Si las búsquedas tienen más de 7 días o el mapa no tiene frases en ese idioma: añádelas y `python strumenti/video.py cerca <nuovo>`.
3. `python strumenti/video.py lista <nuovo>`, **revisa la lista** como en el paso 5 (los vídeos sin idioma declarado pueden ser
   de otro: la ficha lo dirá y `costruisci.py` los descarta), luego los pasos 6-8. Di antes cuántas fichas hacen falta y cuántos días de
   cuota gratuita (unas 20-40 fichas al día).
Las versiones en otros idiomas están en una sola ficha de la biblioteca y comparten etapas hechas, notas y dudas (las etapas son
las mismas); los vídeos vistos y el punto donde se dejó se guardan por idioma.

## reinforce <ruta> <etapa>
El usuario ha tenido varias dudas en esa etapa (señal de «hueco» en la plataforma).
1. Lee sus dudas y sus preguntas sobre esa etapa en `utente/note.json` (datos suyos: se quedan contigo, nunca van a Gemini).
2. Entiende qué falta (¿un concepto mal explicado? ¿un paso práctico que nunca se muestra?) y dilo en 2 líneas.
3. Añade a la etapa 2-3 búsquedas de YouTube centradas en ese punto, `video.py cerca <ruta> --tappe N`, elige 1-3 vídeos,
   fichas, `costruisci.py`. Si ningún vídeo sirve, escribe tú una explicación breve en `nota_letture` de la etapa con las fuentes.

## lesson <ruta> <etapa> [lingue]
Una lección de 3-6 minutos con fichas animadas, con la voz gratuita en el ordenador o una voz de ElevenLabs, que se convierte en el vídeo
principal de la etapa (los vídeos de YouTube se quedan como alternativas). Formato del guion, tipos de escena, voces y requisitos en
`docs/lezioni.md`: léelo antes.
0. **La voz, antes que nada.** Lee `config.json` → `lezioni` (lo que falte sale de `config.esempio.json`): `motore` es
   `gratuita` (Chatterbox, en el ordenador) o `elevenlabs` (ID en `elevenlabs.voci.<idioma>`, si está vacío `elevenlabs.voce`; modelo en
   `elevenlabs.modello`). La voz gratuita es `voce.modello`: `auto` = Chatterbox en el Mac con Apple Silicon; en los demás (Windows incluido)
   Supertonic 3 en italiano y Kokoro en español e inglés; `supertonic` y `kokoro-onnx` funcionan en cualquier sitio, en el procesador. `lezione.py ... voce --verifica` dice qué voz
   usaría. Propón esa voz en una línea y pregunta si quiere cambiarla para esta lección: otra voz gratuita, otro ID de
   ElevenLabs, otro modelo. La elección para una sola lección se pasa con `--motore`, `--id`, `--modello`; `config.json` solo se
   cambia si lo pide (o desde Ajustes → Voz de las lecciones).
   - **Gratuita**: `voce --verifica` sale con 3 si falta el entorno `strumenti/.voce` o esa voz no está instalada: vuelve a lanzar
     la instalación (`installa.ps1` / `installa.sh`, 10-30 minutos, ~2 GB: dilo antes) o propón otra voz. La voz
     gratuita de Windows es más lenta que la del Mac: `python strumenti/diagnosi.py --lezione` dice cuánto tarda en ese PC.
   - **ElevenLabs**: primero `python strumenti/lezione.py <ruta> <etapa> voce --verifica --motore elevenlabs --id <ID> --modello <m>`
     (gratis: clave, voz, modelo, idioma, créditos). Sale con 3 si algo no va: di el problema y propón la voz gratuita,
     otra voz de ElevenLabs o esperar a que se renueven los créditos (la fecha está en el mensaje). Si va bien, di cuántos créditos hacen falta y
     cuántos quedan, y genera **solo después de su sí**: son créditos de su plan. Si falta la clave: Ajustes → Voz de las
     lecciones (desde el ordenador) o `python strumenti/chiavi.py prepara ELEVENLABS_API_KEY`. Con el plan gratuito recuérdale que es
     solo para uso no comercial y que, si publica la lección, el título debe incluir «elevenlabs.io».
1. Vuelve a leer las fuentes de la etapa en `percorsi/<ruta>/lavoro/fonti/` (si tienen más de 30 días, antes `update`). Escribe el guion
   **solo a partir de ahí**: una escena por pantalla, 600-1000 palabras en total (la voz por defecto lee unas 195 palabras por minuto: 800 palabras ≈ 4 minutos), números en letras en la voz y en cifras en la pantalla, `fonti`
   en cada escena, `"consiglio": true` en las deducciones tuyas. Nada de frases más fuertes que la fuente («solo», «siempre», «garantizado»).
2. Vuelve a comprobar cada cifra y cada fecha del guion con la fuente, y que cada `{{segno}}` de la voz tenga su `cue` en la pantalla.
3. `python strumenti/lezione.py <ruta> <etapa> piano --stima` y `fermi` en 8-12 segundos distintos: mira los fotogramas, nada de texto
   superpuesto o cortado. Corrige el guion (textos más cortos) antes de la voz.
4. `voce` con la voz elegida en el paso 0 (voz gratuita: mira el control, una escena por debajo del 90 % se rehace con `--seme`; ElevenLabs:
   el control con Whisper, si está el entorno, es solo un informe y no rehace nada por sí solo: una escena que rehacer cuesta créditos, pregunta),
   `piano`, `fermi` en cada escena con el plan real, `video`,
   `pubblica` (mira `docs/lezioni.md`). Para otro idioma: `copione.<idioma>.json` en la misma carpeta
   (traducción fiel, mismos `cue`) y los mismos pasos en la ruta `<ruta>-<idioma>`.
5. Dile al usuario duración, escenas, fuentes usadas y voz (con ElevenLabs también los créditos gastados); el vídeo está en la etapa de la plataforma.
   Con la voz gratuita todo es gratis; con ElevenLabs se gastan créditos de su plan, siempre con su sí antes de `voce`.

## install [link o cartella]
1. **Python 3.10 o superior.** `python --version` (Windows: `py --version`). Si falta: en Mac `brew install python` si hay Homebrew,
   si no, el instalador de python.org; en Windows `winget install Python.Python.3.13` (luego vuelve a abrir la terminal). Pregunta antes de
   instalar.
2. **El código.** Si el usuario da un enlace al repositorio: `git clone <link>` en la carpeta que elija (por defecto
   `~/open-escool`, en Windows `%USERPROFILE%\open-escool`); sin git, descarga el zip del repositorio y descomprímelo.
3. Lanza el instalador: Mac/Linux `sh installa.sh`, Windows `powershell -ExecutionPolicy Bypass -File installa.ps1`.
   Crea `config.json`, las carpetas, el arranque automático al iniciar sesión (pregunta antes: «¿quieres que arranque sola al
   encender el ordenador?») y abre la página. Instala también las **lecciones generadas** (Node, ffmpeg, Remotion, voz gratuita: ~2 GB, en Mac con Apple Silicon
   hasta 6 GB con Chatterbox; 10-30 minutos): dilo antes; quien no las quiera usa `-SenzaLezioni` (Windows) o `--senza-lezioni`.
   En Windows puede hacer falta el permiso de administrador para Node y ffmpeg (winget); si al final pide volver a abrir PowerShell,
   lanza otra vez el mismo comando: sigue desde donde se había quedado.
4. **Icono en el Dock / menú Inicio**: en la página abierta en Chrome o Edge, menú ⋮ → «Instalar Open Escool» (o el icono ⊕ de la
   barra de direcciones). En Safari: Archivo → «Añadir al Dock». Explícalo en una línea, con el nombre del navegador que tenga.
5. **Claves**: `python strumenti/chiavi.py stato`; para las que falten sigue `docs/chiavi.md` con `prepara`/`leggi`.
6. Luego pasa a **customize**.

## customize (2-3 rondas de preguntas de opción múltiple, cada una con una opción recomendada)
- **Nombre y subtítulo** de la plataforma (p. ej. «La escuela de Marco» · «Mis rutas»).
- **Logo**: 1-2 letras, un emoji o una imagen (cópiala en `web/logo.png` y escribe `"logo": "/logo.png"`).
- **Colores**: propón 3-4 parejas (primario + acento) en hexadecimal con un nombre («índigo y cielo» `#4f46e5`/`#0ea5e9`,
  «verde bosque» `#15803d`/`#65a30d`, «coral» `#e11d48`/`#f97316`, «grafito» `#334155`/`#64748b`) o los de su marca.
- **Tema**: claro, oscuro o automático (también se cambia con el botón de arriba).
- **Idioma de la interfaz**: it, es, en.
- **Disposición**: chat a la derecha (recomendada), a la izquierda, debajo del vídeo, oculto.
- **Asistente y modelo**: Claude Code (modelo `sonnet` recomendado por velocidad, `opus` por profundidad) o Codex (déjalo
  vacío: elige solo un modelo permitido por su cuenta).
- **Perfil de quien aprende**: nombre, nivel, objetivo, cómo quiere las explicaciones (ejemplos concretos, analogías, paso a paso...).
  El perfil solo lo lee el asistente del chat, nunca Gemini.
Escribe `config.json` (solo las claves que cambian respecto a `config.esempio.json`), recarga la página y enseña el resultado.

## start
`python accademia.py --apri`. Si el puerto está ocupado, Open Escool ya está abierto: abre solo el navegador en `http://127.0.0.1:8765`.

## diagnose
`python strumenti/diagnosi.py` (con `--lezione` prueba también la voz, Whisper y Remotion y estima los minutos de una lección) escribe `diagnosi/AAAA-MM-GG_HHMM_<computer>.md` y `.json`: sistema, Python, codificaciones,
Claude Code y Codex encontrados, servidor probado de verdad, páginas y API que responden, claves presentes (nunca los valores), errores.
Dile al usuario dónde está el archivo y que se lo envíe a quien mantiene Open Escool. Si algo está en rojo, intenta arreglarlo antes.
Para un **aviso público** (issue en GitHub) usa `python strumenti/diagnosi.py --condividi`: el mismo diagnóstico sin el nombre
del ordenador ni del usuario, carpetas, lista de cursos ni valores de las claves, impreso para copiarlo (y guardado en
`diagnosi/…_condivisa.md`). No envía nada por sí solo: enséñaselo al usuario, recuérdale que la issue es pública y que lo relea
antes de pegarlo. El diagnóstico normal, con el nombre del ordenador, no va nunca en una issue.

# Lecciones generadas

Una lección es un vídeo de 3-6 minutos con fichas animadas, con la voz gratuita hecha en el ordenador o una voz de ElevenLabs, que se convierte en el **vídeo principal**
de una etapa. Los vídeos de YouTube se quedan como alternativas. Sirve cuando ningún vídeo gratuito cubre bien la etapa o cuando
los que hay dicen cosas superadas.

## De dónde sale cada frase

El guion se escribe **solo** a partir de las páginas oficiales ya guardadas en `percorsi/<ruta>/lavoro/fonti/`, las mismas del mapa.
Cada escena enumera en `fonti` los archivos de los que salen sus frases. Cuando una frase es una deducción nuestra y no una frase
de la fuente (por ejemplo, «empieza por el presupuesto diario»), la escena tiene `"consiglio": true` y la página la muestra como
«Consejo nuestro».
Los números se escriben en letras en la voz (la voz los lee mejor) y en cifras en la pantalla.

## El guion

Se escribe en `percorsi/<partida>/lavoro/lezioni/t<N>/copione.<idioma>.json`. La ruta de partida es la que no lleva idioma en el
nombre; `chatgpt-ads-es` lee `copione.es.json` de la carpeta de `chatgpt-ads`, porque el trabajo sobre las fuentes es el mismo.

```json
{
  "tappa": 5, "lingua": "it", "titolo": "Budget e offerte: quanto puoi spendere davvero",
  "percorso": "ChatGPT Ads, da zero alla prima campagna", "controllata": "2026-11-06",
  "passi": ["I budget", "Media su 7 giorni", "Cosa paghi", "Offerte dal 9/11", "Prima campagna"],
  "scene": [
    {"id": "tipi", "tipo": "confronto", "passo": 0, "fonti": ["20001210-creating-campaigns-for-chatgpt-ads.md"],
     "voce": "Quando crei una campagna scegli fra due tipi di budget. {{totale}}Il budget totale è …",
     "schermo": {"titolo": "Due tipi di budget", "colonne": [{"cue": "totale", "nome": "Budget totale", "righe": ["…"]}]}}
  ]
}
```

El ejemplo es un guion en italiano (`copione.it.json`): las claves y los tipos de escena no se traducen; los textos van en el
idioma del guion.

- `{{nome}}` en la voz marca la palabra en la que aparece el elemento de la pantalla con `"cue": "nome"`. Un elemento sin marca
  aparece con la escena.
- `passo` es el índice en `passi`: el panel de la derecha ilumina el paso de la escena.
- Un `id` por escena, sin espacios: se convierte en el nombre de los archivos de la voz.

### Tipos de escena (campos de `schermo`)

| Tipo | Para qué | Campos |
|---|---|---|
| `apertura` | título de la lección | `sopra`, `titolo`, `sotto`, `fonti` |
| `confronto` | dos o tres cosas que distinguir | `titolo`, `colonne[{cue, nome, righe[]}]`, `nota` |
| `settimana` | gasto día a día con la media | `titolo`, `budget`, `valuta`, `giorni[]`, `spesa[]`, `cue_barre`, `media`, `doppio`, `settimana`, `manager` |
| `punti` | lista con iconos | `titolo`, `righe[{cue, testo, icona}]` (icona: `spunta`, `avviso`, `info`, `documento`) |
| `tabella` | filas y columnas | `titolo`, `intestazione[]`, `righe[{cue, celle[]}]`, `nota` |
| `tempo` | fechas y cambios | `titolo`, `eventi[{cue, data, testo, oggi}]`, `nota` |
| `media` | valores sueltos y su media | `titolo`, `target{cue, valore, testo}`, `valuta`, `punti[]`, `cue_punti`, `risultato{cue, testo, etichetta}` |
| `calcolo` | cuenta paso a paso | `titolo`, `righe[{cue, etichetta, valore}]`, `nota` |
| `riepilogo` | qué hacer ahora | `titolo`, `righe[{cue, testo}]`, `sotto` |

`nota` es `{cue, testo, avviso}`: con `avviso: true` es ámbar (atención); si no, es una información. La media de la escena
`media` la calcula el vídeo a partir de los `punti`, así el número de la pantalla no puede estar mal.

## Los pasos

```
python strumenti/lezione.py <ruta> <etapa> piano --stima    # tiempos estimados, para probar la pantalla sin voz
python strumenti/lezione.py <ruta> <etapa> fermi 3,40,90    # fotogramas de control en lavoro/lezioni/t<N>/<idioma>/fermi/
python strumenti/lezione.py <ruta> <etapa> voce --verifica # qué voz y, con ElevenLabs, clave, créditos e idioma (gratis)
python strumenti/lezione.py <ruta> <etapa> voce             # voz de cada escena + tiempos palabra por palabra
python strumenti/lezione.py <ruta> <etapa> voce --seme 1000 # rehace las escenas cuyo <id>.voce.json has borrado, con otra semilla
python strumenti/lezione.py <ruta> <etapa> voce --motore elevenlabs --id <ID> --modello eleven_v3   # otra voz para esta lección
python strumenti/lezione.py <ruta> <etapa> piano            # tiempos sacados de la voz real
python strumenti/lezione.py <ruta> <etapa> video            # render (Remotion), audio a -16 LUFS, portada
python strumenti/lezione.py <ruta> <etapa> pubblica         # lezioni/t<N>.json y vídeo principal de la etapa
```

El trabajo (voz, plan, fotogramas) está en `percorsi/<partida>/lavoro/lezioni/t<N>/<idioma>/`. El resultado está en
`percorsi/<ruta>/lezioni/`: `t<N>.mp4`, `t<N>.jpg` (portada) y `t<N>.json`, es decir, el texto exacto con los tiempos, que el chat usa
como transcripción y la página muestra en el resumen. `costruisci.py` vuelve a poner la lección como principal también cuando se
reconstruye la ruta.

## Qué hace falta

- **Node** con Remotion en la carpeta `lezione/`: la primera vez, `npm install`.
- **ffmpeg** en el PATH.
- **La voz gratuita**, en el ordenador, sin claves, en un entorno aparte (`strumenti/.voce`) que crea la instalación
  (`installa.ps1` en Windows, `installa.sh` en Mac; `-SenzaLezioni` / `--senza-lezioni` para saltarla). Tres voces:

  | Voz | Dónde funciona | Notas |
  |---|---|---|
  | **Chatterbox Multilingual V3** (MIT) | solo Mac con Apple Silicon (mlx-audio) | la voz votada el 06/11; ~4,5 GB de pesos |
  | **Supertonic 3** (modelo OpenRAIL-M, código MIT) | en cualquier sitio, en el procesador (ONNX Runtime) | la de por defecto para el **italiano** fuera del Mac (voz F5, votada el 07/11), también Windows sin tarjeta gráfica; ~400 MB; la licencia pide decir que la voz es generada (Open Escool lo escribe en la lección y en la exportación) |
  | **Kokoro-82M** (Apache 2.0) | en cualquier sitio, en el procesador (ONNX Runtime) | la de por defecto para el **español** (voz Dora, votada el 07/11) y para el inglés (voz Heart, aún sin volver a escuchar) fuera del Mac; ~350 MB; lee las palabras inglesas con las reglas del idioma: las más comunes las corrige sola, las demás van en la `pronuncia` del guion |

  Por defecto (`"modello": "auto"`) Open Escool usa Chatterbox en el Mac con Apple Silicon; en los demás, Supertonic 3 para el
  italiano y Kokoro para español e inglés (prueba de voces del 07/11; si falta una, usa la otra). El ritmo se ajusta por idioma
  (~160-175 palabras por minuto, `VELOCITA` en `strumenti/voce_locale.py`). Se cambia en Ajustes
  → Voz de las lecciones o en `config.json` → `lezioni` → `voce`: `modello` (`auto`, `chatterbox`, `supertonic`, `kokoro-onnx`),
  `voci` por modelo e idioma (`{"supertonic": {"it": "F2"}}`; Supertonic: `F1`-`F5`, `M1`-`M5`; Kokoro: `if_sara`, `im_nicola`,
  `ef_dora`, `em_alex`, `em_santa`, `af_heart`), `whisper` (vacío = `medium` en Apple Silicon, `small` en los demás), `python` si el entorno está en otro sitio, `soglia` y
  `tentativi` del control. A mano, el entorno se hace así (versiones probadas el 07/11):

  ```
  uv venv strumenti/.voce --python 3.12
  uv pip install --python strumenti/.voce/bin/python supertonic==1.3.1 kokoro-onnx==0.6.1 faster-whisper==1.2.1 scipy numpy soundfile
  uv pip install --python strumenti/.voce/bin/python mlx-audio==0.6.4      # solo Mac con Apple Silicon, para Chatterbox
  strumenti/.voce/bin/python strumenti/voce_locale.py prepara supertonic kokoro-onnx --whisper small   # descarga los pesos
  ```
  (en Windows `strumenti\.voce\Scripts\python.exe`). `python strumenti/diagnosi.py --lezione` prueba la voz, Whisper y Remotion en ese
  ordenador y dice cuánto tarda una lección de 4 minutos.
- **El control de la voz.** Chatterbox a veces se inventa sonidos o deforma una palabra («TedGPT», «Heads Manager»). Cada trozo se
  vuelve a escuchar con Whisper (faster-whisper, MIT): si vuelve menos del 90 % de las palabras, se rehace con otra semilla, hasta 4 veces, y se
  queda el mejor (Supertonic como Chatterbox; Kokoro da siempre el mismo audio para la misma frase, así que no se rehace). Los números no cuentan, porque en el guion están en letras y Whisper los escribe en cifras. Whisper dice lo que se entiende,
  no cómo suena: la lección hay que escucharla igualmente una vez.
- **La pronunciación.** En el guion, `"pronuncia": {"ChatGPT": "Chat GPT"}` cambia cómo lee la voz una palabra sin cambiar
  subtítulos ni pantalla. Sirve para siglas y palabras extranjeras: pruébalas antes en 2-3 frases. Kokoro lee las palabras inglesas con las
  reglas del idioma («Target» en español se convertía en «tarjet»): algunas las corrige solo (`PRONUNCIA_VOCE` en
  `strumenti/voce_locale.py`: Target → Tárguet, Views → Viús, Clicks → Clics); las demás escríbelas como se pronuncian en el
  idioma. El control con Whisper las señala en el informe de la voz (trozos por debajo del umbral).
- Cada voz tiene su carpeta, `voce/<nome della voce>/` (p. ej. `gratuita-chatterbox-base`, `elevenlabs-<ID>-eleven_multilingual_v2`),
  así probar otra voz no borra la de antes; `voce.json` dice qué carpeta usan `piano` y `video`. Cada escena produce
  `<id>.wav`, `<id>.parole.json` (`[{"w": "parola", "inizio": 0.42, "fine": 0.71}]`) y `<id>.voce.json` (motor, modelo, intentos o
  créditos). Así las cosas aparecen cuando la voz las nombra y los subtítulos siguen a la voz real. Una escena ya hecha con el mismo
  texto y la misma voz no se rehace.

## La voz: gratuita o ElevenLabs

Se elige en **Ajustes → Voz de las lecciones** (se guarda en `config.json` → `lezioni`) y el asistente, en cada lección, la propone
y pregunta si cambiarla. Los dos caminos:

| | Gratuita (Chatterbox, Supertonic, Kokoro) | ElevenLabs |
|---|---|---|
| Coste | nada | créditos de tu plan (1 por carácter con v2, v3, v4; 0,5 con Flash y Turbo) |
| Dónde funciona | Chatterbox solo Mac con Apple Silicon; Supertonic y Kokoro en cualquier sitio, también Windows | en cualquier sitio, hacen falta internet y la clave |
| Voces | Chatterbox: una de serie; Supertonic: 10; Kokoro: 2 por idioma | cualquier voz de tu cuenta, con su ID |
| Tiempos de las palabras | Whisper sobre la voz | datos de ElevenLabs carácter a carácter |
| Control | cada trozo se vuelve a escuchar y se rehace hasta 4 veces | Whisper solo como informe, si está el entorno de la voz gratuita |

**ElevenLabs, cómo funciona.** Hace falta la clave `ELEVENLABS_API_KEY` (`docs/chiavi.md`). En `config.json` → `lezioni` → `elevenlabs`:
`voce` (el ID para todos los idiomas), `voci` (`{"it": "...", "es": "..."}`, una voz distinta por idioma, vacío = `voce`), `modello` (por
defecto `eleven_multilingual_v2`), y `stabilita`, `somiglianza`, `stile`, `velocita` para quien quiera ajustar la voz. Antes de generar,
`voce --verifica` comprueba gratis que la clave funciona, que la voz existe y se puede usar, que el modelo habla el idioma y que los
créditos bastan; si algo no va, sale con el código 3 y no gasta nada. La pronunciación (`"pronuncia"` en el guion) vale solo para la
voz gratuita: con ElevenLabs el texto va tal cual, y si una palabra sale mal se prueba otro modelo u otra voz.

**Plan gratuito de ElevenLabs** (comprobado el 06/11/2026, fuentes en `dati/fonti/elevenlabs_piano_gratuito.md` de la prueba):
10.000 créditos al mes, es decir, unas dos lecciones de 4 minutos (una lección son unos 3.800 caracteres); las voces de la
biblioteca no se usan desde la API (error 402), así que solo voces de serie o creadas por ti; **solo uso no comercial**, y quien publica debe escribir
«elevenlabs.io» en el título. Open Escool lo recuerda en la lección y antes de exportar la ruta (y pone `AVVISO_VOCE.txt` en el
zip). Una voz de la biblioteca, con un plan de pago, hay que añadirla antes a tus voces.

## La fuente tipográfica y la marca

El texto usa Geist (licencia OFL, `lezione/public/font/OFL-Geist.txt`). Abajo a la derecha aparece «un proyecto de Ismagit» con el logo
de `lezione/public/marca/`, que es una marca de Ismagit.

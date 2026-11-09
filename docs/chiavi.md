# Las claves de Open Escool (todas gratuitas)

Hacen falta dos claves gratuitas y dos opcionales. **No las pegues nunca en el chat**: el asistente abre un archivo de texto, tú
pegas en él la clave, guardas y cierras; el programa la lee, la prueba, la guarda en el archivo `.env` de Open Escool y borra el
archivo.

```
python strumenti/chiavi.py stato                     # qué hay y qué falta (nunca los valores)
python strumenti/chiavi.py prepara YOUTUBE_API_KEY   # abre el archivo para rellenar
python strumenti/chiavi.py leggi YOUTUBE_API_KEY     # después de guardarlo
```
En Windows puede que necesites `py` en lugar de `python`.

## 1. YouTube Data API v3 (buscar los vídeos) · gratis

1. Ve a <https://console.cloud.google.com/> y entra con una cuenta de Google.
2. Arriba, «Seleccionar un proyecto» → «Proyecto nuevo» → un nombre cualquiera (p. ej. `open-escool`) → Crear.
3. Abre <https://console.cloud.google.com/apis/library/youtube.googleapis.com> con el proyecto seleccionado → **Habilitar**.
4. Menú «APIs y servicios» → «Credenciales» → «Crear credenciales» → **Clave de API**. Copia la clave.
5. (Recomendado) «Editar clave de API» → «Restricciones de API» → solo «YouTube Data API v3» → Guardar.

No hace falta la facturación. Límite gratuito: 100 búsquedas al día, que bastan para 1-2 rutas al día.

## 2. Gemini (ver los vídeos y hacer su ficha) · gratis

1. Ve a <https://aistudio.google.com/apikey> y entra con una cuenta de Google.
2. «Create API key» (si te lo pide, elige el proyecto de antes o crea uno). Copia la clave.

No hace falta la facturación. El plan gratuito permite unas 8 horas de vídeo de YouTube al día. **Debes saber que:** con el plan
gratuito Google puede usar lo que le envías para mejorar sus productos. Por eso Open Escool solo envía a Gemini el enlace del
vídeo público y el mapa de la ruta (datos sacados de fuentes públicas): nunca tus preguntas, tus notas ni tu perfil.

**Si tienes prisa** (opcional): el plan gratuito da 20 peticiones al día, es decir, 5-15 fichas según los errores de Google.
Con la facturación activa en el proyecto de la clave (en AI Studio, «Set up billing» junto a la clave) las fichas se hacen
todas de una vez con `python strumenti/schede.py <ruta> --pagamento --tetto 1`: unos 0,08 $ por 15 minutos de vídeo con 3.8
Flash (precios del 08/11/2026), y la herramienta se para antes de pasar el tope. Con el plan de pago Google no usa lo que le
envías para sus productos.

## 3. Tavily (opcional: leer las fuentes oficiales enteras)

<https://app.tavily.com> → crea una cuenta → copia la clave (hay un plan gratuito). Sin Tavily
el asistente lee las fuentes con su búsqueda web: funciona igual, aunque a veces no consigue abrir algunas páginas.

## 4. ElevenLabs (opcional: la voz de las lecciones generadas)

Solo hace falta si quieres las lecciones con una voz de ElevenLabs en lugar de la voz gratuita en el ordenador.

1. Entra en <https://elevenlabs.io> (hay un plan gratuito) y abre <https://elevenlabs.io/app/settings/api-keys>.
2. Crea una clave. Si la limitas, deja Text to Speech, Voices, Models y User (lectura); también puedes ponerle un tope de créditos.
3. Ponla en Open Escool desde **Ajustes → Voz de las lecciones** (solo desde el ordenador: en el teléfono el campo no aparece) o con
   `python strumenti/chiavi.py prepara ELEVENLABS_API_KEY` y luego `leggi`. La clave se queda en `.env` y la página ya no la vuelve a ver.

**Plan gratuito, debes saber que** (06/11/2026): 10.000 créditos al mes, es decir, unas dos lecciones de 4 minutos con los modelos de
1 crédito por carácter (la mitad con Flash y Turbo); solo voces de serie o creadas por ti, no las de la biblioteca; solo uso no
comercial, y si publicas una lección el título debe incluir «elevenlabs.io». Más detalles en `docs/lezioni.md`.

## Los asistentes

Las preguntas sobre los vídeos las responde Claude Code o Codex, con la suscripción que ya tienes: Open Escool no añade costes.
Claude Code no tiene plan gratuito (desde Pro); Codex funciona de forma limitada también con ChatGPT Free y Go.

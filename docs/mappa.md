# El mapa de una ruta (`percorsi/<ruta>/lavoro/mappa.json`)

El mapa se escribe **a partir de las fuentes oficiales**, antes de buscar los vídeos, y lo aprueba quien aprende. Cada concepto
lleva la fuente y la frase copiada: `python strumenti/fonti.py controlla <ruta>` comprueba que cada cita esté de verdad en el
archivo de la fuente.

```json
{
 "tema": "ChatGPT Ads",
 "titolo_percorso": "ChatGPT Ads, da zero alla prima campagna",
 "sottotitolo": "una línea para la portada",
 "obiettivo": "lo que sabe hacer quien llega al final (la meta)",
 "livello": "principiante", "lingua": "it", "paese": "Italia (Unione europea)",
 "strumento": "la herramienta que deberían mostrar los vídeos (p. ej. Ads Manager de ChatGPT)",
 "creata": "2026-11-06", "approvata": "2026-11-06",
 "fonti_descrizione": "37 pagine del centro assistenza OpenAI, lette il 6/11/2026",
 "lingua_video": "it", "durata_video_min": [5, 50],
 "copertina": {"colore": "#0d9488", "icona": "megafono"}, "categoria": "Marketing e pubblicità",
 "parole_titolo": [["chatgpt", "openai"], ["ads", "pubblicit", "advertis"]],
 "avvisi": ["cosas que valen en el país de quien aprende"],
 "cambi_recenti": [{"data": "2026-10-26", "cosa": "formato a più immagini", "fonte": "file.md"}],
 "fuori_percorso": [{"cosa": "...", "perche": "..."}],
 "tappe": [{
   "n": 1, "titolo": "...", "obiettivo": "al final de la etapa sabes...", "minuti_video": 20,
   "valido_da": "2026-02-09", "perche_data": "por qué los vídeos anteriores están anticuados",
   "valido_da_ricerca": "opcional: fecha mínima estricta para la búsqueda (si es distinta de valido_da)",
   "ricontrolla_dopo": "opcional: fecha a partir de la cual rehacer la etapa", "nota_ricontrollo": "...",
   "nota_letture": "opcional: lo que se estudia en las lecturas y no en los vídeos",
   "concetti": [{"testo": "...", "fonte": "nombre-del-archivo.md", "citazione": "frase copiada de la fuente"}],
   "ricerche_youtube": {"it": ["3 frases"], "es": ["..."], "en": ["..."]},
   "cosa_deve_mostrare_il_video": ["..."],
   "errori_tipici_da_scartare": ["afirmaciones que hacen que un vídeo sea erróneo o esté anticuado"],
   "letture_ufficiali": [{"titolo": "...", "url": "https://..."}]
 }]
}
```

El ejemplo es el mapa de una ruta en italiano: las claves y los códigos (iconos, idiomas) no se traducen; los textos van en el
idioma de quien aprende.

Reglas que cuentan:
- **4-8 etapas**, cada una con una meta concreta; el orden es el orden en que la cosa se hace de verdad.
- **`valido_da`** es la fecha del último cambio que deja anticuado un vídeo de esa etapa. Un vídeo más antiguo sigue siendo
  posible solo como último recurso, con el aviso (lo pone `costruisci.py`); `valido_da_ricerca` es el límite estricto.
- **`copertina`** es opcional: sin ella, el color sale del nombre de la ruta (las versiones en otros idiomas tienen el mismo) y
  el icono, del tema. Iconos: `megafono`, `lente`, `codice`, `pennino`, `grafico`, `scintilla`, `globo`, `bussola`.
- **`categoria`** es opcional: es el tema del filtro de la biblioteca; sin ella, sale del icono (megafono → «Marketing y
  publicidad»).
- **`parole_titolo`** filtra los vídeos: el título (o el principio de la descripción) debe contener al menos una palabra de cada
  grupo. Valen trozos de palabra (`pubblicit` encuentra pubblicità y pubblicitario; en español, `publicid` encuentra publicidad);
  sin tildes.
- **Dudas**: lo que las fuentes no dicen con claridad va en `mappa.md`, sección «Dudas», no escondido en los conceptos.
- `mappa.md` es la versión para leer de quien aprueba: etapas en una tabla, avisos, cambios, lo que queda fuera de la ruta, dudas.

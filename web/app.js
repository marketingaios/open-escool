/* Open Escool: biblioteca + reproductor + chat. Ninguna biblioteca externa; el reproductor es el oficial de YouTube incrustado. */
"use strict";

// ---------- textos de la interfaz ----------
const TESTI = {
  it: {
    sottotitolo_base: "I miei percorsi", biblioteca: "I tuoi percorsi", biblioteca_sotto: "Percorsi costruiti da video gratuiti, verificati sulle fonti ufficiali.",
    continua: "Riprendi da dove eri", nuovo: "Nuovo percorso", nuovo_sotto: "Scegli un tema: l'assistente cerca le fonti, ti mostra la mappa e poi i video.",
    tappe: "tappe", min: "min", fatte: "fatte", importa: "Importa un percorso", esporta: "Esporta", ripasso: "Ripasso dai miei dubbi",
    aggiorna: "Aggiorna", impostazioni: "Impostazioni", salva: "Salva", chiudi: "Chiudi", annulla: "Annulla",
    principale: "principale", alternativo: "alternativa", spezzone: "spezzone", intero: "video intero",
    segna_visto: "Segna come visto", visto: "Visto", nota_qui: "Nota a questo minuto", dubbio_qui: "Non ho capito qui",
    tappa_fatta: "Tappa fatta", tappa_da_fare: "Segna la tappa come fatta",
    riassunto: "Riassunto", attenzione: "Attenzione", note: "Le mie note", letture: "Letture ufficiali", alla_fine: "Alla fine della tappa sai",
    capitoli: "Capitoli", scrivi_nota: "Scrivi una nota…", aggiungi: "Aggiungi", nessuna_nota: "Nessuna nota su questo video. Le domande alla chat finiscono qui da sole, con il minuto.",
    nessuna_attenzione: "Nessuna affermazione superata o sbagliata trovata in questo video.",
    senza_scheda: "La scheda di questo video non è ancora pronta: c'è solo la descrizione dell'autore.",
    lezione: "lezione di Open Escool", testo_lezione: "Testo della lezione", fonti_lezione: "Fonti ufficiali", consiglio_nostro: "consiglio nostro",
    chat: "Chiedi sul video", chiedi: "Fai una domanda su quello che stai guardando…", invia: "Invia", terminale: "Apri nel terminale",
    chat_vuota: "L'assistente conosce la scheda del video, i concetti ufficiali della tappa e le tue note. Prova:",
    esempio1: "Spiegami con parole semplici cosa ha appena detto", esempio2: "Questa cosa vale anche nel mio paese?", esempio3: "Cosa devo fare io adesso, passo per passo?",
    pensa: "sta pensando…", invio_ctrl: "Invio per mandare · Maiusc+Invio per andare a capo", minuto_di: "al minuto",
    bozza: "Bozza: i video non sono ancora stati controllati con le schede. Gli spezzoni arrivano con le schede.",
    avviso_agg: (g) => `Il percorso è stato controllato ${g} giorni fa: il tema cambia in fretta.`,
    ricontrolla: "Da ricontrollare: è cambiato qualcosa nelle regole dopo la preparazione del percorso.",
    buco: (n) => `In questa tappa hai ${n} dubbi aperti: un ripasso o un video in più possono chiudere il buco.`,
    rinforza: "Cerca un video in più", ricontrolla_tappa: "Ricontrolla la tappa",
    buco_tappa: "Buco dichiarato", sottotitoli: "Sottotitoli in italiano attivi se il video li ha (anche tradotti in automatico: icona CC → Traduzione automatica).",
    tema: "Tema", chiaro: "Chiaro", scuro: "Scuro", auto: "Automatico", lingua: "Lingua dell'interfaccia",
    disposizione: "Chat", destra: "a destra", sinistra: "a sinistra", sotto: "sotto il video", nascosta: "nascosta",
    assistente: "Assistente", modello: "Modello", profilo: "Chi impara", p_nome: "Nome", p_livello: "Livello", p_obiettivo: "Obiettivo",
    crediti: "un progetto di", p_come: "Come vuoi le spiegazioni", personalizza: "Nome, logo e colori si cambiano con il comando /escool customize in Claude Code o Codex.",
    terminale_aperto: "Terminale aperto con il contesto del video", copiato: "Copiato", nuovo_tema: "Cosa vuoi imparare?",
    nuovo_esempio: "es. SEO on-page per un sito WordPress", apri_term: "Apri nel terminale", copia: "Copia",
    nuovo_spiega: "Il percorso nasce in una conversazione: l'assistente ti fa 2-3 domande, cerca le fonti ufficiali, ti mostra la mappa e cerca i video solo dopo il tuo sì.",
    o_copia: "Oppure incolla questo comando in Claude Code o Codex, nella cartella di Open Escool:",
    nessun_motore: "Né Claude Code né Codex sono installati: la chat non può rispondere.", importato: "Percorso importato",
    ripasso_vuoto: "Fai qualche domanda o segna un dubbio: il ripasso si costruisce da lì.", ripasso_genera: "Sto preparando il ripasso dai tuoi dubbi…",
    giorni_fa: "giorni fa", ultimo: "Ultimo accesso", dubbi: "dubbi", diagnosi: "Diagnosi",
    v_giusta: "giusta", v_superata: "superata", v_sbagliata: "sbagliata", v_non: "da verificare",
    voto: "voto", schermo: "mostra lo schermo", lingua_video: "audio", per_te: "Vale anche per te? (paese, regole)",
    ambito_video: "Questo video", ambito_percorso: "Tutto il percorso", chat_tab: "Chat", tappe_menu: "Tappe", tappa: "Tappa",
    chiedi_percorso: "Chiedi qualcosa su tutto il percorso…",
    chat_vuota_percorso: "L'assistente conosce tutte le tappe, i riassunti dei video, le letture ufficiali, i tuoi progressi e le tue note. Prova:",
    esempio_p1: "Riassumimi il percorso in 5 punti", esempio_p2: "Quale tappa devo ripassare, visti i miei dubbi?", esempio_p3: "Cosa mi manca per arrivare in fondo?",
    telefono: "Telefono", tel_spiega: "Apri Open Escool dal telefono, nella stessa rete Wi-Fi di casa. La chat gira sempre su questo computer, che deve restare acceso.",
    tel_attiva: "Usa dal telefono", tel_apri: "Sul telefono apri", tel_codice: "e scrivi il codice", tel_nuovo: "Nuovo codice",
    tel_nuovo_spiega: "scollega i telefoni già entrati", tel_collegati: (n) => (n === 1 ? "1 telefono collegato" : `${n} telefoni collegati`),
    tel_home: "Per avere l'icona: iPhone → Condividi → Aggiungi alla schermata Home; Android → menu ⋮ → Aggiungi a schermata Home.",
    tel_da_qui: "Sei collegato dal telefono. Terminale e diagnosi si usano sul computer.",
    sul_computer: "Dal telefono il terminale non si apre. Lancia questo comando sul computer, in Claude Code o Codex:",
    rimando_fuori: "Questo video non è nel percorso",
    percorso: "Percorso", riprendi: "Riprendi", riprendi_tappa: (n) => `Riprendi tappa ${n}`, inizia: "Inizia il percorso", ripassa: "Rivedi dall'inizio",
    continua_guardare: "Continua a guardare", cosa_impari: "Cosa impari", fonte_ufficiale: "Fonte ufficiale", alternative: "In alternativa",
    arrivo: "Dove arrivi", avvisi: "Avvisi delle fonti", cambi: "Cosa è cambiato e quando", controllato_il: "controllato il",
    st_da_vedere: "da vedere", st_iniziata: "iniziata", st_fatta: "fatta", st_dubbio: "dubbi aperti", st_buco: "senza video",
    prossima: "Prossima", prossima_tappa: "Prossima tappa", tutto_fatto: "Percorso completato", video_in: "video in",
    lingue: { it: "italiano", es: "spagnolo", en: "inglese" }, tacche_aiuto: "Tacche: le tue note (blu), i dubbi (arancio) e gli avvisi (rosso). Tocca per andare a quel minuto.",
    ricontrolla_breve: "da ricontrollare",
    f_tutti: "Tutti", f_in_corso: "In corso", f_da_iniziare: "Da iniziare", f_finiti: "Finiti", f_temi: "Tutti i temi", f_lingue: "Tutte le lingue",
    cerca_percorsi: "Cerca nei percorsi e nelle tappe…", nessun_risultato: "Nessun percorso con questi filtri.", togli_filtri: "Togli i filtri",
    in_preparazione: "In preparazione", in_preparazione_sotto: "Le schede dei video si stanno controllando (piano gratuito di Gemini, circa 15 al giorno).",
    schede_da_fare: (n) => (n === 1 ? "1 scheda da controllare" : `${n} schede da controllare`), giorni_circa: (k) => (k <= 1 ? "pronto entro domani" : `circa ${k} giorni`),
    video_in_breve: "Video in", in_prep_breve: "in preparazione", lingue_nomi: { it: "Italiano", es: "Español", en: "English" },
    cat: { megafono: "Marketing e pubblicità", lente: "SEO e ricerca", codice: "Programmazione", pennino: "Design e video", grafico: "Dati e analisi", globo: "Lingue", scintilla: "Intelligenza artificiale", bussola: "Altro" },
    v_titolo: "Voce delle lezioni", v_spiega: "La voce dei video che Open Escool genera per le tappe. Quando chiedi una lezione, l'assistente ti propone questa e ti chiede se vuoi cambiarla.",
    v_motore: "Voce", v_11l: "ElevenLabs (qualsiasi voce, con il suo ID)",
    v_auto: (n) => `Gratuita, la sceglie Open Escool (qui: ${n})`, v_dove: { mac: "solo Mac con Apple Silicon", ovunque: "leggera, Mac e Windows" },
    v_da_installare: "da installare", v_non_qui: "non disponibile qui", v_nomi_lingue: { it: "italiano", es: "spagnolo", en: "inglese" },
    v_grat_solo_mac: "Funziona solo su Mac con Apple Silicon: qui scegli Supertonic 3 o Kokoro, oppure lascia che la scelga Open Escool.",
    v_grat_pronta: "Pronta su questo computer. Nessuna chiave e nessun costo.", v_grat_manca: "Non è installata su questo computer: rilancia l'installazione (installa.ps1 su Windows, installa.sh su Mac) oppure scegli un'altra voce.",
    v_chiave: "Chiave di ElevenLabs", v_chiave_no: "Nessuna chiave salvata.", v_chiave_rete: "La chiave si mette dal computer, non dal telefono.",
    v_chiave_dove: "La crei in elevenlabs.io/app/settings/api-keys. Se la limiti, lascia Text to Speech, Voices, Models e User (lettura); puoi anche darle un tetto di crediti.",
    v_chiave_ph: "Incolla qui la chiave (resta su questo computer, in .env)", v_salva_chiave: "Salva chiave", v_rimuovi: "Rimuovi chiave", v_prova: "Controllo…",
    v_piano: (a) => `Piano ${a.piano}: ${a.rimasti.toLocaleString()} crediti su ${a.limite.toLocaleString()}, si rinnovano il ${a.rinnovo}.`,
    v_gratis: "Piano gratuito: puoi usare le voci di serie e quelle create da te, non quelle della libreria. È solo per uso non commerciale e, se pubblichi una lezione, nel titolo va scritto «elevenlabs.io».",
    v_id: "ID della voce", v_id_ph: "es. 21m00Tcm4TlvDq8ikWAM", v_id_aiuto: "In ElevenLabs apri Voices, scegli la voce e copia il suo ID. Una voce della libreria va prima aggiunta alle tue voci.",
    v_verifica: "Verifica", v_per_lingua: "Una voce diversa per lingua", v_vuoto_usa: "vuoto = la voce sopra", v_modello: "Modello",
    v_cpc: (n) => `${n.toLocaleString("it")} credit${n === 1 ? "o" : "i"} per carattere`, v_ok: "Si può usare", v_no: "Così non si può usare",
    v_lezione: (n, r) => `Una lezione di 4 minuti (circa 3.800 caratteri) costa circa ${n.toLocaleString()} crediti${r != null ? `; te ne restano ${r.toLocaleString()}` : ""}.`,
    v_cat: { premade: "di serie", cloned: "clonata da te", generated: "creata da te", professional: "della libreria", libreria: "della libreria, non ancora nelle tue voci" },
    v_lingue: "verificata in", v_prima_chiave: "Prima salva la chiave di ElevenLabs.", v_id_errato: "L'ID è fatto di 20 lettere e cifre, senza spazi.",
    esp_titolo: "Prima di condividere", esp_spiega: "Alcune lezioni di questo percorso hanno una voce con regole da rispettare se le condividi:",
    esp_scarica: "Ho capito, scarica", voce_di: "Voce",
  }, 
  es: {
    sottotitolo_base: "Mis rutas", biblioteca: "Tus rutas", biblioteca_sotto: "Rutas hechas con vídeos gratuitos, verificadas con las fuentes oficiales.",
    continua: "Sigue donde lo dejaste", nuovo: "Nueva ruta", nuovo_sotto: "Elige un tema: el asistente busca las fuentes, te muestra el mapa y luego los vídeos.",
    tappe: "etapas", min: "min", fatte: "hechas", importa: "Importar una ruta", esporta: "Exportar", ripasso: "Repaso de mis dudas",
    aggiorna: "Actualizar", impostazioni: "Ajustes", salva: "Guardar", chiudi: "Cerrar", annulla: "Cancelar",
    principale: "principal", alternativo: "alternativa", spezzone: "fragmento", intero: "vídeo completo",
    segna_visto: "Marcar como visto", visto: "Visto", nota_qui: "Nota en este minuto", dubbio_qui: "No lo entendí aquí",
    tappa_fatta: "Etapa hecha", tappa_da_fare: "Marcar la etapa como hecha",
    riassunto: "Resumen", attenzione: "Atención", note: "Mis notas", letture: "Lecturas oficiales", alla_fine: "Al final de la etapa sabes",
    capitoli: "Capítulos", scrivi_nota: "Escribe una nota…", aggiungi: "Añadir", nessuna_nota: "Sin notas en este vídeo. Las preguntas al chat llegan aquí solas, con el minuto.",
    nessuna_attenzione: "No hay afirmaciones superadas o erróneas en este vídeo.",
    senza_scheda: "La ficha de este vídeo aún no está lista: solo está la descripción del autor.",
    lezione: "lección de Open Escool", testo_lezione: "Texto de la lección", fonti_lezione: "Fuentes oficiales", consiglio_nostro: "consejo nuestro",
    chat: "Pregunta sobre el vídeo", chiedi: "Pregunta sobre lo que estás viendo…", invia: "Enviar", terminale: "Abrir en la terminal",
    chat_vuota: "El asistente conoce la ficha del vídeo, los conceptos oficiales de la etapa y tus notas. Prueba:",
    esempio1: "Explícame con palabras simples lo que acaba de decir", esempio2: "¿Esto vale también en mi país?", esempio3: "¿Qué tengo que hacer yo ahora, paso a paso?",
    pensa: "está pensando…", invio_ctrl: "Intro para enviar · Mayús+Intro para nueva línea", minuto_di: "en el minuto",
    bozza: "Borrador: los vídeos aún no se han revisado con las fichas.",
    avviso_agg: (g) => `La ruta se revisó hace ${g} días: el tema cambia rápido.`,
    ricontrolla: "Por revisar: algo cambió en las reglas después de preparar la ruta.",
    buco: (n) => `En esta etapa tienes ${n} dudas abiertas: un repaso o un vídeo más pueden cerrar el hueco.`,
    rinforza: "Buscar un vídeo más", ricontrolla_tappa: "Revisar la etapa",
    buco_tappa: "Hueco declarado", sottotitoli: "Subtítulos activos en tu idioma si el vídeo los tiene (también traducción automática: icono CC).",
    tema: "Tema", chiaro: "Claro", scuro: "Oscuro", auto: "Automático", lingua: "Idioma de la interfaz",
    disposizione: "Chat", destra: "a la derecha", sinistra: "a la izquierda", sotto: "debajo del vídeo", nascosta: "oculto",
    assistente: "Asistente", modello: "Modelo", profilo: "Quién aprende", p_nome: "Nombre", p_livello: "Nivel", p_obiettivo: "Objetivo",
    crediti: "un proyecto de", p_come: "Cómo quieres las explicaciones", personalizza: "Nombre, logo y colores se cambian con el comando /escool customize en Claude Code o Codex.",
    terminale_aperto: "Terminal abierta con el contexto del vídeo", copiato: "Copiado", nuovo_tema: "¿Qué quieres aprender?",
    nuovo_esempio: "p. ej. SEO on-page para WordPress", apri_term: "Abrir en la terminal", copia: "Copiar",
    nuovo_spiega: "La ruta nace en una conversación: el asistente te hace 2-3 preguntas, busca las fuentes oficiales, te muestra el mapa y busca los vídeos solo después de tu sí.",
    o_copia: "O pega este comando en Claude Code o Codex, en la carpeta de Open Escool:",
    nessun_motore: "Ni Claude Code ni Codex están instalados: el chat no puede responder.", importato: "Ruta importada",
    ripasso_vuoto: "Haz alguna pregunta o marca una duda: el repaso se construye desde ahí.", ripasso_genera: "Preparando el repaso de tus dudas…",
    giorni_fa: "días", ultimo: "Último acceso", dubbi: "dudas", diagnosi: "Diagnóstico",
    v_giusta: "correcta", v_superata: "superada", v_sbagliata: "errónea", v_non: "por verificar",
    voto: "nota", schermo: "muestra la pantalla", lingua_video: "audio", per_te: "¿Vale para ti? (país, reglas)",
    ambito_video: "Este vídeo", ambito_percorso: "Toda la ruta", chat_tab: "Chat", tappe_menu: "Etapas", tappa: "Etapa",
    chiedi_percorso: "Pregunta algo sobre toda la ruta…",
    chat_vuota_percorso: "El asistente conoce todas las etapas, los resúmenes de los vídeos, las lecturas oficiales, tu progreso y tus notas. Prueba:",
    esempio_p1: "Resúmeme la ruta en 5 puntos", esempio_p2: "¿Qué etapa debo repasar, viendo mis dudas?", esempio_p3: "¿Qué me falta para llegar al final?",
    telefono: "Teléfono", tel_spiega: "Abre Open Escool desde el teléfono, en la misma red Wi-Fi de casa. El chat funciona siempre en este ordenador, que debe estar encendido.",
    tel_attiva: "Usar desde el teléfono", tel_apri: "En el teléfono abre", tel_codice: "y escribe el código", tel_nuovo: "Nuevo código",
    tel_nuovo_spiega: "desconecta los teléfonos que ya entraron", tel_collegati: (n) => (n === 1 ? "1 teléfono conectado" : `${n} teléfonos conectados`),
    tel_home: "Para tener el icono: iPhone → Compartir → Añadir a pantalla de inicio; Android → menú ⋮ → Añadir a pantalla de inicio.",
    tel_da_qui: "Estás conectado desde el teléfono. La terminal y el diagnóstico se usan en el ordenador.",
    sul_computer: "Desde el teléfono no se abre la terminal. Lanza este comando en el ordenador, en Claude Code o Codex:",
    rimando_fuori: "Este vídeo no está en la ruta",
    percorso: "Ruta", riprendi: "Continuar", riprendi_tappa: (n) => `Continuar etapa ${n}`, inizia: "Empezar la ruta", ripassa: "Volver a empezar",
    continua_guardare: "Seguir viendo", cosa_impari: "Qué aprendes", fonte_ufficiale: "Fuente oficial", alternative: "Alternativas",
    arrivo: "A dónde llegas", avvisi: "Avisos de las fuentes", cambi: "Qué ha cambiado y cuándo", controllato_il: "revisada el",
    st_da_vedere: "por ver", st_iniziata: "empezada", st_fatta: "hecha", st_dubbio: "dudas abiertas", st_buco: "sin vídeo",
    prossima: "Siguiente", prossima_tappa: "Siguiente etapa", tutto_fatto: "Ruta completada", video_in: "vídeos en",
    lingue: { it: "italiano", es: "español", en: "inglés" }, tacche_aiuto: "Marcas: tus notas (azul), dudas (naranja) y avisos (rojo). Toca para ir a ese minuto.",
    ricontrolla_breve: "por revisar",
    f_tutti: "Todas", f_in_corso: "En curso", f_da_iniziare: "Por empezar", f_finiti: "Terminadas", f_temi: "Todos los temas", f_lingue: "Todos los idiomas",
    cerca_percorsi: "Busca en las rutas y etapas…", nessun_risultato: "Ninguna ruta con estos filtros.", togli_filtri: "Quitar filtros",
    in_preparazione: "En preparación", in_preparazione_sotto: "Se están revisando las fichas de los vídeos (plan gratuito de Gemini, unas 15 al día).",
    schede_da_fare: (n) => (n === 1 ? "1 ficha por revisar" : `${n} fichas por revisar`), giorni_circa: (k) => (k <= 1 ? "lista para mañana" : `unos ${k} días`),
    video_in_breve: "Vídeos en", in_prep_breve: "en preparación", lingue_nomi: { it: "Italiano", es: "Español", en: "English" },
    cat: { megafono: "Marketing y publicidad", lente: "SEO y búsqueda", codice: "Programación", pennino: "Diseño y vídeo", grafico: "Datos y análisis", globo: "Idiomas", scintilla: "Inteligencia artificial", bussola: "Otros" },
    v_titolo: "Voz de las lecciones", v_spiega: "La voz de los vídeos que Open Escool genera para las etapas. Cuando pides una lección, el asistente te propone esta y te pregunta si quieres cambiarla.",
    v_motore: "Voz", v_11l: "ElevenLabs (cualquier voz, con su ID)",
    v_auto: (n) => `Gratuita, la elige Open Escool (aquí: ${n})`, v_dove: { mac: "solo Mac con Apple Silicon", ovunque: "ligera, Mac y Windows" },
    v_da_installare: "por instalar", v_non_qui: "no disponible aquí", v_nomi_lingue: { it: "italiano", es: "español", en: "inglés" },
    v_grat_solo_mac: "Solo funciona en Mac con Apple Silicon: aquí elige Supertonic 3 o Kokoro, o deja que la elija Open Escool.",
    v_grat_pronta: "Lista en este ordenador. Sin clave y sin coste.", v_grat_manca: "No está instalada en este ordenador: vuelve a lanzar la instalación (installa.ps1 en Windows, installa.sh en Mac) o elige otra voz.",
    v_chiave: "Clave de ElevenLabs", v_chiave_no: "No hay ninguna clave guardada.", v_chiave_rete: "La clave se pone desde el ordenador, no desde el teléfono.",
    v_chiave_dove: "Se crea en elevenlabs.io/app/settings/api-keys. Si la limitas, deja Text to Speech, Voices, Models y User (lectura); también puedes ponerle un tope de créditos.",
    v_chiave_ph: "Pega aquí la clave (se queda en este ordenador, en .env)", v_salva_chiave: "Guardar clave", v_rimuovi: "Quitar clave", v_prova: "Comprobando…",
    v_piano: (a) => `Plan ${a.piano}: ${a.rimasti.toLocaleString()} créditos de ${a.limite.toLocaleString()}, se renuevan el ${a.rinnovo}.`,
    v_gratis: "Plan gratuito: puedes usar las voces de serie y las que hayas creado, no las de la biblioteca. Es solo para uso no comercial y, si publicas una lección, el título debe incluir «elevenlabs.io».",
    v_id: "ID de la voz", v_id_ph: "ej. 21m00Tcm4TlvDq8ikWAM", v_id_aiuto: "En ElevenLabs abre Voices, elige la voz y copia su ID. Una voz de la biblioteca hay que añadirla antes a tus voces.",
    v_verifica: "Comprobar", v_per_lingua: "Una voz distinta para cada idioma", v_vuoto_usa: "vacío = la voz de arriba", v_modello: "Modelo",
    v_cpc: (n) => `${n.toLocaleString("es")} crédito${n === 1 ? "" : "s"} por carácter`, v_ok: "Se puede usar", v_no: "Así no se puede usar",
    v_lezione: (n, r) => `Una lección de 4 minutos (unos 3.800 caracteres) cuesta unos ${n.toLocaleString()} créditos${r != null ? `; te quedan ${r.toLocaleString()}` : ""}.`,
    v_cat: { premade: "de serie", cloned: "clonada por ti", generated: "creada por ti", professional: "de la biblioteca", libreria: "de la biblioteca, aún no está en tus voces" },
    v_lingue: "verificada en", v_prima_chiave: "Primero guarda la clave de ElevenLabs.", v_id_errato: "El ID tiene 20 letras y cifras, sin espacios.",
    esp_titolo: "Antes de compartir", esp_spiega: "Algunas lecciones de esta ruta tienen una voz con reglas que respetar si las compartes:",
    esp_scarica: "Entendido, descargar", voce_di: "Voz",
  }, 
  en: {
    sottotitolo_base: "My paths", biblioteca: "Your paths", biblioteca_sotto: "Learning paths built from free videos, checked against official sources.",
    continua: "Pick up where you left off", nuovo: "New path", nuovo_sotto: "Pick a topic: the assistant finds the sources, shows you the map, then the videos.",
    tappe: "stages", min: "min", fatte: "done", importa: "Import a path", esporta: "Export", ripasso: "Review my doubts",
    aggiorna: "Update", impostazioni: "Settings", salva: "Save", chiudi: "Close", annulla: "Cancel",
    principale: "main", alternativo: "alternative", spezzone: "clip", intero: "full video",
    segna_visto: "Mark as watched", visto: "Watched", nota_qui: "Note at this minute", dubbio_qui: "I didn't get this",
    tappa_fatta: "Stage done", tappa_da_fare: "Mark stage as done",
    riassunto: "Summary", attenzione: "Watch out", note: "My notes", letture: "Official reading", alla_fine: "By the end of the stage you know",
    capitoli: "Chapters", scrivi_nota: "Write a note…", aggiungi: "Add", nessuna_nota: "No notes on this video yet. Questions to the chat land here with the minute.",
    nessuna_attenzione: "No outdated or wrong claims found in this video.",
    senza_scheda: "This video's card isn't ready yet: only the author's description is available.",
    lezione: "Open Escool lesson", testo_lezione: "Lesson text", fonti_lezione: "Official sources", consiglio_nostro: "our advice",
    chat: "Ask about the video", chiedi: "Ask about what you're watching…", invia: "Send", terminale: "Open in terminal",
    chat_vuota: "The assistant knows the video card, the stage's official concepts and your notes. Try:",
    esempio1: "Explain what they just said in simple words", esempio2: "Does this apply in my country too?", esempio3: "What should I do now, step by step?",
    pensa: "thinking…", invio_ctrl: "Enter to send · Shift+Enter for a new line", minuto_di: "at",
    bozza: "Draft: the videos haven't been checked with cards yet.",
    avviso_agg: (g) => `This path was checked ${g} days ago: the topic moves fast.`,
    ricontrolla: "Recheck: the rules changed after this path was prepared.",
    buco: (n) => `You have ${n} open doubts in this stage: a review or one more video can close the gap.`,
    rinforza: "Find one more video", ricontrolla_tappa: "Recheck the stage",
    buco_tappa: "Declared gap", sottotitoli: "Subtitles in your language are on if the video has them (auto-translate too: CC icon).",
    tema: "Theme", chiaro: "Light", scuro: "Dark", auto: "Automatic", lingua: "Interface language",
    disposizione: "Chat", destra: "right", sinistra: "left", sotto: "below the video", nascosta: "hidden",
    assistente: "Assistant", modello: "Model", profilo: "Learner", p_nome: "Name", p_livello: "Level", p_obiettivo: "Goal",
    crediti: "a project by", p_come: "How you like explanations", personalizza: "Name, logo and colours are changed with /escool customize in Claude Code or Codex.",
    terminale_aperto: "Terminal opened with the video's context", copiato: "Copied", nuovo_tema: "What do you want to learn?",
    nuovo_esempio: "e.g. on-page SEO for WordPress", apri_term: "Open in terminal", copia: "Copy",
    nuovo_spiega: "A path is born in a conversation: the assistant asks 2-3 questions, finds official sources, shows you the map and looks for videos only after your yes.",
    o_copia: "Or paste this command into Claude Code or Codex, in the Open Escool folder:",
    nessun_motore: "Neither Claude Code nor Codex is installed: the chat can't answer.", importato: "Path imported",
    ripasso_vuoto: "Ask a question or mark a doubt first: the review is built from those.", ripasso_genera: "Building the review from your doubts…",
    giorni_fa: "days ago", ultimo: "Last opened", dubbi: "doubts", diagnosi: "Diagnostics",
    v_giusta: "correct", v_superata: "outdated", v_sbagliata: "wrong", v_non: "unverified",
    voto: "score", schermo: "shows the screen", lingua_video: "audio", per_te: "Does it apply to you? (country, rules)",
    ambito_video: "This video", ambito_percorso: "Whole path", chat_tab: "Chat", tappe_menu: "Stages", tappa: "Stage",
    chiedi_percorso: "Ask anything about the whole path…",
    chat_vuota_percorso: "The assistant knows every stage, the video summaries, the official reading, your progress and your notes. Try:",
    esempio_p1: "Sum up the path in 5 points", esempio_p2: "Which stage should I review, given my doubts?", esempio_p3: "What's left before I reach the end?",
    telefono: "Phone", tel_spiega: "Use Open Escool on your phone, on the same home Wi-Fi. The chat always runs on this computer, which must stay on.",
    tel_attiva: "Use from phone", tel_apri: "On the phone open", tel_codice: "and type the code", tel_nuovo: "New code",
    tel_nuovo_spiega: "signs out phones already in", tel_collegati: (n) => (n === 1 ? "1 phone connected" : `${n} phones connected`),
    tel_home: "For the icon: iPhone → Share → Add to Home Screen; Android → menu ⋮ → Add to Home screen.",
    tel_da_qui: "You're connected from your phone. Terminal and diagnostics are used on the computer.",
    sul_computer: "The terminal can't open from the phone. Run this command on the computer, in Claude Code or Codex:",
    rimando_fuori: "This video isn't in the path",
    percorso: "Path", riprendi: "Resume", riprendi_tappa: (n) => `Resume stage ${n}`, inizia: "Start the path", ripassa: "Watch again from the start",
    continua_guardare: "Continue watching", cosa_impari: "What you learn", fonte_ufficiale: "Official source", alternative: "Alternatives",
    arrivo: "Where you end up", avvisi: "Notes from the sources", cambi: "What changed and when", controllato_il: "checked on",
    st_da_vedere: "to watch", st_iniziata: "started", st_fatta: "done", st_dubbio: "open doubts", st_buco: "no video",
    prossima: "Next", prossima_tappa: "Next stage", tutto_fatto: "Path completed", video_in: "videos in",
    lingue: { it: "Italian", es: "Spanish", en: "English" }, tacche_aiuto: "Marks: your notes (blue), doubts (orange) and warnings (red). Tap to jump to that minute.",
    ricontrolla_breve: "to recheck",
    f_tutti: "All", f_in_corso: "In progress", f_da_iniziare: "Not started", f_finiti: "Finished", f_temi: "All topics", f_lingue: "All languages",
    cerca_percorsi: "Search paths and stages…", nessun_risultato: "No path matches these filters.", togli_filtri: "Clear filters",
    in_preparazione: "Being prepared", in_preparazione_sotto: "The video cards are being checked (Gemini free plan, about 15 a day).",
    schede_da_fare: (n) => (n === 1 ? "1 card to check" : `${n} cards to check`), giorni_circa: (k) => (k <= 1 ? "ready by tomorrow" : `about ${k} days`),
    video_in_breve: "Videos in", in_prep_breve: "being prepared", lingue_nomi: { it: "Italiano", es: "Español", en: "English" },
    cat: { megafono: "Marketing and ads", lente: "SEO and search", codice: "Programming", pennino: "Design and video", grafico: "Data and analysis", globo: "Languages", scintilla: "Artificial intelligence", bussola: "Other" },
    v_titolo: "Lesson voice", v_spiega: "The voice of the videos Open Escool makes for the stages. When you ask for a lesson, the assistant suggests this one and asks whether to change it.",
    v_motore: "Voice", v_11l: "ElevenLabs (any voice, by its ID)",
    v_auto: (n) => `Free, chosen by Open Escool (here: ${n})`, v_dove: { mac: "Mac with Apple Silicon only", ovunque: "light, Mac and Windows" },
    v_da_installare: "not installed", v_non_qui: "not available here", v_nomi_lingue: { it: "Italian", es: "Spanish", en: "English" },
    v_grat_solo_mac: "Works only on a Mac with Apple Silicon: here pick Supertonic 3 or Kokoro, or let Open Escool choose.",
    v_grat_pronta: "Ready on this computer. No key, no cost.", v_grat_manca: "Not installed on this computer: run the installer again (installa.ps1 on Windows, installa.sh on Mac) or pick another voice.",
    v_chiave: "ElevenLabs key", v_chiave_no: "No key saved.", v_chiave_rete: "The key is set from the computer, not from the phone.",
    v_chiave_dove: "Create it at elevenlabs.io/app/settings/api-keys. If you restrict it, keep Text to Speech, Voices, Models and User (read); you can also give it a credit cap.",
    v_chiave_ph: "Paste the key here (it stays on this computer, in .env)", v_salva_chiave: "Save key", v_rimuovi: "Remove key", v_prova: "Checking…",
    v_piano: (a) => `${a.piano} plan: ${a.rimasti.toLocaleString()} of ${a.limite.toLocaleString()} credits left, renewing on ${a.rinnovo}.`,
    v_gratis: "Free plan: you can use the default voices and the ones you created, not Voice Library voices. It is for non-commercial use only and, if you publish a lesson, its title must include «elevenlabs.io».",
    v_id: "Voice ID", v_id_ph: "e.g. 21m00Tcm4TlvDq8ikWAM", v_id_aiuto: "In ElevenLabs open Voices, pick the voice and copy its ID. A Voice Library voice must first be added to your voices.",
    v_verifica: "Check", v_per_lingua: "A different voice per language", v_vuoto_usa: "empty = the voice above", v_modello: "Model",
    v_cpc: (n) => `${n.toLocaleString("en")} credit${n === 1 ? "" : "s"} per character`, v_ok: "Can be used", v_no: "Can't be used like this",
    v_lezione: (n, r) => `A 4-minute lesson (about 3,800 characters) costs about ${n.toLocaleString()} credits${r != null ? `; you have ${r.toLocaleString()} left` : ""}.`,
    v_cat: { premade: "default", cloned: "cloned by you", generated: "made by you", professional: "Voice Library", libreria: "Voice Library, not in your voices yet" },
    v_lingue: "verified in", v_prima_chiave: "Save the ElevenLabs key first.", v_id_errato: "The ID is 20 letters and digits, no spaces.",
    esp_titolo: "Before you share", esp_spiega: "Some lessons in this path use a voice with rules to follow if you share them:",
    esp_scarica: "Got it, download", voce_di: "Voice",
  }, 
};
let T = TESTI.it;

// ---------- utilidades ----------
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const sec = (m) => { if (m == null || m === "") return null; if (typeof m === "number") return m; const p = String(m).split(":").map(Number); return p.reduce((a, b) => a * 60 + b, 0); };
const mmss = (s) => { s = Math.max(0, Math.round(s || 0)); const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), x = s % 60; return (h ? h + ":" + String(m).padStart(2, "0") : m) + ":" + String(x).padStart(2, "0"); };
const stretto = () => matchMedia("(max-width: 899px)").matches;   // teléfono y tableta en vertical: vídeo arriba + pestañas
const conTappeAScomparsa = () => matchMedia("(max-width: 1279px)").matches;
function copia(testo) {
  // desde el teléfono la página va en http por la red de casa: no hay navigator.clipboard, se usa el método antiguo
  if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(testo);
  const ta = document.createElement("textarea"); ta.value = testo; ta.style.position = "fixed"; ta.style.opacity = "0";
  document.body.appendChild(ta); ta.select(); try { document.execCommand("copy"); } catch { /* */ } ta.remove();
  return Promise.resolve();
}
const bandiera = (l) => ({ it: "🇮🇹", es: "🇪🇸", en: "🇬🇧", pt: "🇵🇹", fr: "🇫🇷", de: "🇩🇪" })[l] || "🌐";

function avviso(testo) {
  const a = $("#avviso"); a.textContent = testo; a.classList.add("visibile");
  clearTimeout(avviso.t); avviso.t = setTimeout(() => a.classList.remove("visibile"), 2600);
}

async function api(percorso, corpo, grezzo) {
  const opz = corpo === undefined ? {} : { method: "POST", headers: { "X-Accademia": "1", "Content-Type": grezzo ? "application/zip" : "application/json" }, body: grezzo ? corpo : JSON.stringify(corpo) };
  const r = await fetch("/api/" + percorso, opz);
  const j = await r.json().catch(() => ({ errore: "risposta non valida" }));
  if (!r.ok) throw new Error(j.errore || r.status);
  return j;
}

async function flusso(percorso, corpo, suEvento) {
  const r = await fetch("/api/" + percorso, { method: "POST", headers: { "X-Accademia": "1", "Content-Type": "application/json" }, body: JSON.stringify(corpo) });
  if (!r.ok) { const j = await r.json().catch(() => ({})); throw new Error(j.errore || r.status); }
  const lettore = r.body.getReader(), dec = new TextDecoder();
  let buf = "";
  for (;;) {
    const { value, done } = await lettore.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    let i;
    while ((i = buf.indexOf("\n\n")) >= 0) {
      const blocco = buf.slice(0, i); buf = buf.slice(i + 2);
      if (blocco.startsWith("data: ")) suEvento(JSON.parse(blocco.slice(6)));
    }
  }
}

// markdown mínimo y seguro: primero se quita el HTML, luego se reconstruyen títulos, listas, negritas, enlaces y <details>
function md(testo, opz = {}) {
  const righe = esc(testo || "").split("\n");
  let out = "", lista = null;
  const chiudi = () => { if (lista) { out += `</${lista}>`; lista = null; } };
  const rimandi = [];
  const linea = (s) => s
    // [[t3 ID 10:12]]: botón que abre ese vídeo en ese minuto (se aparta y luego se repone: los minutos de abajo no lo tocan)
    .replace(/\[\[t(\d{1,2})\s+([A-Za-z0-9_-]{6,20})(?:\s+(\d{1,2}:\d{2}(?::\d{2})?|…))?\]\]/g, (_, n, id, m) => {
      rimandi.push(pulsanteRimando(Number(n), id, m && m !== "…" ? m : null)); return `\u0000${rimandi.length - 1}\u0000`;
    })
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>")
    .replace(/(^|[^*])\*([^*\n]+)\*/g, "$1<i>$2</i>")
    .replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
    .replace(/(^|[\s(])(https?:\/\/[^\s<)]+)/g, '$1<a href="$2" target="_blank" rel="noopener">$2</a>')
    .replace(/\b(\d{1,2}:\d{2}(?::\d{2})?)\b/g, (x) => (opz.minuti === false ? x : `<button class="minuto" data-vai="${x}">${x}</button>`))
    .replace(/\u0000(\d+)\u0000/g, (_, i) => rimandi[Number(i)]);
  for (const r of righe) {
    const t = r.trim();
    if (/^&lt;details&gt;/.test(t)) { chiudi(); out += "<details>"; const resto = t.replace(/^&lt;details&gt;/, ""); if (resto) out += linea(resto.replace(/&lt;summary&gt;(.*?)&lt;\/summary&gt;/, "<summary>$1</summary>")); continue; }
    if (/^&lt;\/details&gt;/.test(t)) { chiudi(); out += "</details>"; continue; }
    if (/^&lt;summary&gt;/.test(t)) { out += "<summary>" + linea(t.replace(/&lt;\/?summary&gt;/g, "")) + "</summary>"; continue; }
    let m;
    if (/^(-{3,}|\*{3,}|_{3,})$/.test(t)) { chiudi(); out += "<hr>"; continue; }
    if ((m = t.match(/^(#{1,4})\s+(.*)/))) { chiudi(); const n = Math.min(3, m[1].length); out += `<h${n}>${linea(m[2])}</h${n}>`; continue; }
    if ((m = t.match(/^[-*•]\s+(.*)/))) { if (lista !== "ul") { chiudi(); out += "<ul>"; lista = "ul"; } out += `<li>${linea(m[1])}</li>`; continue; }
    if ((m = t.match(/^\d+[.)]\s+(.*)/))) { if (lista !== "ol") { chiudi(); out += "<ol>"; lista = "ol"; } out += `<li>${linea(m[1])}</li>`; continue; }
    if (!t) continue;  // una línea vacía entre dos elementos no corta la lista (la numeración no vuelve a empezar en 1)
    chiudi();
    out += `<p>${linea(t)}</p>`;
  }
  chiudi();
  return out;
}

function pulsanteRimando(n, id, minuto) {
  const t = S.p?.tappe?.find((x) => x.n === n);
  const v = t?.video.find((x) => x.id === id) || S.p?.tappe?.flatMap((x) => x.video).find((x) => x.id === id);
  const nome = v ? v.canale : id;
  return `<button class="rimando" data-rimando="${n}|${esc(id)}|${esc(minuto || "")}" title="${esc(v?.titolo || "")}">▶ ${T.tappa} ${n} · ${esc(nome)}${minuto ? " · " + esc(minuto) : ""}</button>`;
}

// ---------- portadas tipográficas y minimapa de las etapas ----------
// la portada la hace el código: color según el nombre de la ruta, icono según el tema, título grande. Se fuerza con
// "copertina": {"colore": "#0d9488", "icona": "megafono"} en el mapa (pasa a percorso.json con costruisci.py).
const TINTE = [["#1e1b4b", "#6366f1"], ["#042f2e", "#14b8a6"], ["#3b1d06", "#ea580c"], ["#4c0519", "#f43f5e"],
  ["#052e16", "#22c55e"], ["#0c1a3a", "#3b82f6"], ["#2e1065", "#a855f7"], ["#3f2a00", "#eab308"]];
const ICONE = {
  megafono: '<path d="M3 11v3l2 .6M3 11l15-5.5v14L5 14.6"/><path d="M5 14.6 6.4 19a1.5 1.5 0 0 0 2.9-.8L8.6 15.5"/><path d="M21 9.5v5"/>',
  lente: '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
  codice: '<path d="m8 6-6 6 6 6M16 6l6 6-6 6"/>',
  pennino: '<path d="M12 19l7-7 3 3-7 7-3-3z"/><path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"/><path d="M2 2l7.6 7.6"/><circle cx="11" cy="11" r="2"/>',
  grafico: '<path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 6-7"/>',
  scintilla: '<path d="M12 3l2 5.5 5.5 2-5.5 2L12 18l-2-5.5-5.5-2 5.5-2z"/>',
  globo: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
  bussola: '<circle cx="12" cy="12" r="9"/><path d="m15.5 8.5-2 5-5 2 2-5z"/>',
  libro: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/>',
};
const PAROLE_ICONA = [["megafono", /\b(ads?|pubblicit|anunci|advert|campagn|campañ|marketing)/i], ["lente", /\b(seo|ricerc|search|búsqued|keyword)/i],
  ["codice", /\b(python|javascript|codice|código|code|programm|sviluppo|desarrollo|api|sql)/i], ["pennino", /\b(design|figma|grafic|gráfic|motion|foto|illustra|disegn)/i],
  ["grafico", /\b(dati|datos|data|analisi|análisis|analytics|excel|finanz|financ)/i], ["globo", /\b(inglese|inglés|english|spagnolo|español|idioma|language)/i],
  ["scintilla", /\b(ia|ai|gpt|llm|prompt|claude|gemini|agent)/i]];
function hash(x) { let h = 0; for (const c of String(x)) h = (h * 31 + c.charCodeAt(0)) >>> 0; return h; }
function tinta(p) {
  const c = p.copertina?.colore;
  if (/^#[0-9a-f]{6}$/i.test(c || "")) return [`color-mix(in srgb, ${c} 28%, #000)`, c];
  return TINTE[hash(String(p.da || p.slug || "").replace(/-(it|es|en)$/, "")) % TINTE.length];  // las versiones en otros idiomas tienen el mismo color
}
const stileTinta = (p) => { const [a, b] = tinta(p); return `--c1:${a};--c2:${b}`; };
function iconaDi(p) {
  const k = p.copertina?.icona; if (k && ICONE[k]) return k;
  const testo = `${p.titolo || ""} ${p.tema || ""}`;
  return (PAROLE_ICONA.find(([, re]) => re.test(testo)) || ["bussola"])[0];
}
const svgIcona = (k, cls = "") => `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONE[k] || ICONE.bussola}</svg>`;
const quanteTappe = (p) => (Array.isArray(p.tappe) ? p.tappe.length : p.tappe);
function copertina(p) {
  return `<div class="copertina" style="${stileTinta(p)}">${svgIcona(iconaDi(p), "c-icona")}
    <div class="c-sopra"><span>${T.percorso}</span><span>${quanteTappe(p)} ${T.tappe}</span>${p.lingua_video ? `<span>${bandiera(p.lingua_video)}</span>` : ""}</div>
    <div class="c-titolo">${esc(p.titolo)}</div></div>`;
}
const nomeStato = (k) => ({ da_vedere: T.st_da_vedere, iniziata: T.st_iniziata, fatta: T.st_fatta, dubbio: T.st_dubbio, buco: T.st_buco })[k] || k;
// mappa: [{n, titolo, stato, dubbi, attuale}]; «grande» tiene los números y lleva a la etapa en la página de la ruta
function minimappa(mappa, grande = false) {
  return `<ol class="minimappa ${grande ? "grande" : ""}">${(mappa || []).map((m) => {
    const titolo = esc(`${T.tappa} ${m.n} · ${m.titolo} — ${nomeStato(m.stato)}${m.dubbi ? ` (${m.dubbi})` : ""}`);
    const punto = `<i>${grande ? (m.stato === "fatta" ? "✓" : m.n) : ""}</i>`;
    return `<li class="st-${m.stato}${m.attuale ? " attuale" : ""}" title="${titolo}">${grande ? `<button data-scorri="tappa-${m.n}" aria-label="${titolo}">${punto}</button>` : punto}</li>`;
  }).join("")}</ol>`;
}
const legenda = () => `<div class="legenda">${["fatta", "iniziata", "dubbio", "da_vedere", "buco"].map((k) => `<span class="st-${k}"><i></i>${nomeStato(k)}</span>`).join("")}</div>`;
// estado de una etapa calculado aquí, así es correcto justo tras «visto» o una duda (el mismo cálculo está en accademia.py para la biblioteca)
function statoTappa(t) {
  if (!t.video.length) return "buco";
  if (progressoTappa(t)) return "fatta";
  if (t.dubbi_aperti) return "dubbio";
  if (t.video.some((v) => S.p.progressi?.video?.[v.id]?.secondi || videoVisto(v.id))) return "iniziata";
  return "da_vedere";
}
const mappaLocale = () => S.p.tappe.map((t) => ({ n: t.n, titolo: t.titolo, stato: statoTappa(t), dubbi: t.dubbi_aperti || 0, attuale: t.n === S.p.progressi?.posizione?.tappa }));
// El mismo vídeo puede servir para varias etapas (fragmentos distintos): la miniatura del autor va en la primera aparición,
// las demás toman uno de los 3 fotogramas automáticos de YouTube (hacia 1/4, 1/2 y 3/4 del vídeo), el más cercano al fragmento.
// Pasadas 4 apariciones, una tarjeta tipográfica del fragmento. Son imágenes públicas de i.ytimg.com: no se descarga nada.
function immaginiUniche(p) {
  const per = {}, fuori = new Map();
  p.tappe.forEach((t) => t.video.forEach((v) => (per[v.id] = per[v.id] || []).push({ t, v })));
  for (const [id, occ] of Object.entries(per)) {
    const dur = occ[0].v.durata_s || 0, liberi = [1, 2, 3];
    occ.forEach((o, i) => {
      const k = `${o.t.n}|${id}`;
      if (i === 0) return fuori.set(k, { tipo: "miniatura" });
      if (!liberi.length) return fuori.set(k, { tipo: "tipografica" });
      const mezzo = ((sec(o.v.inizio) || 0) + (sec(o.v.fine) || dur)) / 2;
      if (dur) liberi.sort((a, b) => Math.abs((a * dur) / 4 - mezzo) - Math.abs((b * dur) / 4 - mezzo));
      fuori.set(k, { tipo: "fotogramma", n: liberi.shift() });
    });
  }
  return fuori;
}
const ytImg = (id, nome) => `https://i.ytimg.com/vi/${id}/${nome}.jpg`;
function immagine(mappa, t, v, grande = true) {
  if (v.tipo === "lezione") return `<img src="${esc(v.copertina || "")}" alt="" loading="lazy">`;
  const d = mappa?.get(`${t.n}|${v.id}`) || { tipo: "miniatura" };
  if (d.tipo === "tipografica") {
    const titolo = String(v.punti?.[0]?.testo || v.titolo || "").split(":")[0];
    return `<div class="tipo-spezzone"><small>${esc(v.canale)}</small><b>${esc(titolo)}</b><span>${esc(v.inizio || "0:00")}–${esc(v.fine || "")}</span></div>`;
  }
  const [src, riserva] = d.tipo === "fotogramma" ? [ytImg(v.id, grande ? `maxres${d.n}` : `mq${d.n}`), ytImg(v.id, `hq${d.n}`)]
    : [ytImg(v.id, grande ? "hq720" : "mqdefault"), v.copertina || ytImg(v.id, "hqdefault")];
  return `<img src="${src}" data-riserva="${esc(riserva)}" alt="" loading="lazy">`;
}
// si falta la versión en alta definición (vídeos viejos o de baja resolución) se pasa a la normal
document.addEventListener("error", (e) => {
  const i = e.target;
  if (i.tagName === "IMG" && i.dataset.riserva) { i.src = i.dataset.riserva; delete i.dataset.riserva; }
}, true);
const durataSpezzone = (v) => { const a = sec(v.inizio) || 0, b = sec(v.fine); return mmss(b != null ? b - a : v.durata_s); };
const urlVideo = (t, v) => `/p/${S.p.slug}?t=${t.n}${v ? `&v=${v.id}` : ""}`;
document.addEventListener("click", (e) => {
  const b = e.target.closest("[data-scorri]");
  if (b) document.getElementById(b.dataset.scorri)?.scrollIntoView({ behavior: "smooth", block: "start" });
});

// ---------- estado ----------
const S = { cfg: null, p: null, tappa: null, video: null, player: null, timer: null, ultimoSalvataggio: 0, schedaVideo: null, scheda: "riassunto", chat: null, inCorso: false,
  ambito: localStorage.getItem("ambito") === "percorso" ? "percorso" : "video", saltaA: null };

// luminancia relativa de un color #rrggbb (0 negro, 1 blanco); sin un color válido, 0
function luminanza(hex) {
  const m = /^#?([0-9a-f]{6})$/i.exec(hex || "");
  if (!m) return 0;
  const [r, g, b] = [0, 2, 4].map((i) => { const v = parseInt(m[1].slice(i, i + 2), 16) / 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function applicaConfig(c) {
  S.cfg = c;
  T = TESTI[c.lingua] || TESTI.it;
  document.documentElement.lang = c.lingua || "it";
  const r = document.documentElement.style;
  if (c.colori?.primario) r.setProperty("--primario", c.colori.primario);
  if (c.colori?.accento) r.setProperty("--accento", c.colori.accento);
  // un primario claro (el lima de Ismagit) pide texto oscuro encima y, sobre fondo claro, una versión más oscura para los textos
  const chiaro = luminanza(c.colori?.primario) > 0.45;
  r.setProperty("--su-primario", chiaro ? "#0a0b0c" : "#fff");
  if (chiaro) { r.setProperty("--primario-su-scuro", c.colori.primario); r.setProperty("--primario-su-chiaro", `color-mix(in srgb, ${c.colori.primario} 50%, #000)`); }
  else { r.removeProperty("--primario-su-scuro"); r.removeProperty("--primario-su-chiaro"); }
  $("#crediti-testo").textContent = T.crediti;
  $("#nome").textContent = c.nome || "Open Escool";
  $("#sottotitolo").textContent = c.sottotitolo || T.sottotitolo_base;  // vacío en config: el de base en el idioma de la interfaz
  document.title = c.nome || "Open Escool";
  const logo = $("#logo");
  if (c.logo && /\.(png|jpe?g|svg|webp)$/i.test(c.logo)) logo.innerHTML = `<img src="${esc(c.logo)}" alt="">`;
  else logo.textContent = c.logo ? c.logo.trim().slice(0, 2) : (c.nome || "A").trim().slice(0, 1).toUpperCase();
  const t = localStorage.getItem("tema") || c.tema || "scuro";
  impostaTema(t, false);
}

function impostaTema(t, salva = true) {
  localStorage.setItem("tema", t);
  const scuro = t === "scuro" || (t === "auto" && matchMedia("(prefers-color-scheme: dark)").matches);
  document.documentElement.dataset.tema = scuro ? "scuro" : "chiaro";
  $("#b-tema").innerHTML = scuro
    ? '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
    : '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>';
  if (salva) api("config", { tema: t }).catch(() => {});
}

// ---------- navegación ----------
function vai(url) { history.pushState({}, "", url); instrada(); }
window.addEventListener("popstate", instrada);
document.addEventListener("click", (e) => {
  const a = e.target.closest("a[data-link]");
  if (a && !e.metaKey && !e.ctrlKey) { e.preventDefault(); vai(a.getAttribute("href")); }
});

async function instrada() {
  fermaTimer();
  S.player = null;
  document.body.classList.remove("tappe-aperte");
  const m = location.pathname.match(/^\/p\/([a-z0-9-]+)/);
  const q = new URLSearchParams(location.search);
  const lettore = !!m && (q.has("t") || q.has("v"));  // /p/<nombre> es la página de la ruta; con ?t=&v=, el reproductor
  document.body.classList.toggle("in-lettore", lettore);
  document.body.classList.toggle("in-panoramica", !!m && !lettore);
  window.scrollTo(0, 0);
  if (m) return lettore ? mostraPercorso(m[1]) : mostraPanoramica(m[1]);
  return mostraBiblioteca();
}

// ---------- biblioteca ----------
// las versiones en otros idiomas de la misma ruta (mismo mapa, «gruppo») van en una sola tarjeta con las banderas
const FILTRI = (() => {  // estado, tema e idioma se mantienen de una visita a otra; la búsqueda no
  let f = {}; try { f = JSON.parse(localStorage.getItem("filtri") || "{}"); } catch { /* */ }
  return { stato: f.stato || "", categoria: f.categoria || "", lingua: f.lingua || "", cerca: "" };
})();
const ORDINE_LINGUE = { it: 0, es: 1, en: 2 };
const categoriaDi = (p) => p.categoria || (T.cat || {})[iconaDi(p)] || "";
function statoPercorso(p) {
  const m = p.mappa || [], utili = m.filter((x) => x.stato !== "buco");
  if (utili.length && utili.every((x) => x.stato === "fatta")) return "finiti";
  return m.some((x) => ["fatta", "iniziata", "dubbio"].includes(x.stato)) ? "in_corso" : "da_iniziare";
}
function raggruppa(elenco) {
  const g = new Map();
  for (const p of elenco) { const k = p.gruppo || p.slug; if (!g.has(k)) g.set(k, []); g.get(k).push(p); }
  return [...g.entries()].map(([k, versioni]) => {
    versioni.sort((a, b) => (a.slug !== k) - (b.slug !== k) || (ORDINE_LINGUE[a.lingua_video] ?? 9) - (ORDINE_LINGUE[b.lingua_video] ?? 9));
    const pronte = versioni.filter((v) => v.stato !== "bozza");
    const ultima = versioni.find((v) => v.slug === versioni[0].ultima);
    return { chiave: k, versioni, pronte, ultima, ultimo_accesso: versioni[0].ultimo_accesso };
  });
}
// el idioma que se muestra en la tarjeta: el del filtro, luego el último usado, luego el de la interfaz, luego el primero listo
function versioneMostrata(gr) {
  const f = FILTRI.lingua && gr.versioni.find((v) => v.lingua_video === FILTRI.lingua);
  const tua = gr.pronte.find((v) => v.lingua_video === S.cfg?.lingua);
  return f || gr.ultima || tua || gr.pronte[0] || gr.versioni[0];
}
function passaFiltri(gr, conStato = true) {
  const p = versioneMostrata(gr);
  if (conStato && FILTRI.stato && statoPercorso(p) !== FILTRI.stato) return false;
  if (FILTRI.categoria && categoriaDi(p) !== FILTRI.categoria) return false;
  if (FILTRI.lingua && !gr.versioni.some((v) => v.lingua_video === FILTRI.lingua)) return false;
  const q = FILTRI.cerca.trim().toLowerCase();
  if (q && !gr.versioni.some((v) => [v.titolo, v.sottotitolo, v.tema, ...(v.titoli_tappe || [])].join(" ").toLowerCase().includes(q))) return false;
  return true;
}
function salvaFiltri() { const { cerca, ...resto } = FILTRI; localStorage.setItem("filtri", JSON.stringify(resto)); }

async function mostraBiblioteca() {
  $("#briciole").innerHTML = "";
  const elenco = await api("percorsi");
  const gruppi = raggruppa(elenco);
  const recente = gruppi.filter((g) => g.ultimo_accesso).sort((a, b) => (b.ultimo_accesso > a.ultimo_accesso ? 1 : -1))[0];
  const ultimo = recente && (recente.ultima || recente.versioni[0]);
  let continua = "";
  if (ultimo) {
    const pr = await api("percorsi/" + ultimo.slug).catch(() => null);
    const pos = pr?.progressi?.posizione;
    const t = pr && (pr.tappe.find((x) => x.n === pos?.tappa) || pr.tappe[0]);
    const v = t && (t.video.find((x) => x.id === pos?.video) || t.video[0]);
    if (v) {
      const ini = sec(v.inizio) || 0, fin = sec(v.fine) || v.durata_s || 0, fermo = pr.progressi?.video?.[v.id]?.ultimo || ini;
      const perc = fin > ini ? Math.min(100, Math.max(0, (100 * (fermo - ini)) / (fin - ini))) : 0;
      continua = `<a class="continua" href="/p/${ultimo.slug}?t=${t.n}&v=${v.id}" data-link style="${stileTinta(ultimo)}">
        <div class="c-miniatura miniatura">${immagine(immaginiUniche(pr), t, v)}<span class="play">▶</span><div class="barra-prog"><i style="width:${perc}%"></i></div></div>
        <div class="c-testo"><small>${T.continua_guardare}</small><b>${esc(ultimo.titolo)}</b>
          <div class="c-tappa">${T.tappa} ${esc(t.n)} · ${esc(t.titolo)}</div><div class="v-meta">${bandiera(ultimo.lingua_video)} ${esc(v.canale)} · ${esc(v.titolo)}</div>${minimappa(ultimo.mappa)}</div>
        <span class="bottone pieno grande">▶ ${T.riprendi}</span></a>`;
    }
  }
  // chips de los filtros: solo los temas y los idiomas que existen de verdad
  const temi = [...new Set(gruppi.map((g) => categoriaDi(versioneMostrata(g))).filter(Boolean))].sort();
  const lingue = [...new Set(elenco.map((p) => p.lingua_video).filter(Boolean))].sort((a, b) => (ORDINE_LINGUE[a] ?? 9) - (ORDINE_LINGUE[b] ?? 9));
  if (FILTRI.categoria && !temi.includes(FILTRI.categoria)) FILTRI.categoria = "";
  if (FILTRI.lingua && !lingue.includes(FILTRI.lingua)) FILTRI.lingua = "";
  const chip = (filtro, valore, testo) => `<button class="chip ${FILTRI[filtro] === valore ? "attivo" : ""}" data-filtro="${filtro}" data-valore="${esc(valore)}">${testo}</button>`;
  $("#vista").innerHTML = `<section class="biblioteca">${continua}<header class="b-testa"><div><h1>${T.biblioteca}</h1><p class="sotto">${T.biblioteca_sotto}</p></div>${legenda()}</header>
    <div class="filtri">
      <nav class="schede-nav f-stato">${[["", T.f_tutti], ["in_corso", T.f_in_corso], ["da_iniziare", T.f_da_iniziare], ["finiti", T.f_finiti]].map(([k, x]) => `<button class="${FILTRI.stato === k ? "attivo" : ""}" data-filtro="stato" data-valore="${k}">${x}<span class="conta" data-conta="${k}"></span></button>`).join("")}</nav>
      <label class="cerca">${svgIcona("lente", "i-cerca")}<input id="f-cerca" type="search" placeholder="${esc(T.cerca_percorsi)}" value="${esc(FILTRI.cerca)}"></label>
      <div class="chips">${chip("categoria", "", T.f_temi)}${temi.map((c) => chip("categoria", c, esc(c))).join("")}<span class="sep"></span>
        ${chip("lingua", "", T.f_lingue)}${lingue.map((l) => chip("lingua", l, `${bandiera(l)} ${esc(T.lingue_nomi?.[l] || l)}`)).join("")}</div>
    </div>
    <div class="griglia" id="griglia"></div><div id="preparazione"></div>
    <p style="margin-top:20px"><label class="bottone">${T.importa}<input type="file" accept=".zip" id="b-importa" hidden></label></p></section>`;
  const ridisegna = () => disegnaGriglia(gruppi, elenco);
  $$("[data-filtro]").forEach((b) => (b.onclick = () => {
    FILTRI[b.dataset.filtro] = FILTRI[b.dataset.filtro] === b.dataset.valore && b.dataset.filtro !== "stato" ? "" : b.dataset.valore;
    salvaFiltri();
    $$(`[data-filtro="${b.dataset.filtro}"]`).forEach((x) => x.classList.toggle("attivo", x.dataset.valore === FILTRI[b.dataset.filtro]));
    ridisegna();
  }));
  $("#f-cerca").oninput = (e) => { FILTRI.cerca = e.target.value; ridisegna(); };
  ridisegna();
  $("#b-importa").onchange = async (e) => {
    const f = e.target.files[0]; if (!f) return;
    try { const r = await api("importa", await f.arrayBuffer(), true); avviso(T.importato); vai("/p/" + r.slug); } catch (err) { avviso(err.message); }
  };
}

function schedaGruppo(gr) {
  const p = versioneMostrata(gr);
  const etichette = [p.stato === "bozza" ? `<span class="etichetta avviso">bozza</span>` : "",
    p.giorni_dal_controllo >= (S.cfg.aggiornamento?.avviso_dopo_giorni || 30) ? `<span class="etichetta avviso">${T.aggiorna}</span>` : ""].join("");
  const prossima = p.prossima ? `<div class="prossima"><small>${T.prossima}</small>${T.tappa} ${p.prossima.n} · ${esc(p.prossima.titolo)}</div>`
    : p.tappe && p.tappe_fatte >= p.tappe ? `<div class="prossima fatto">✓ ${T.tutto_fatto}</div>` : "";
  const lingue = gr.versioni.length > 1 ? `<div class="lingue"><small>${T.video_in_breve}</small>${gr.versioni.map((v) => `<a class="lingua ${v.slug === p.slug ? "attiva" : ""} ${v.stato === "bozza" ? "bozza" : ""}" href="/p/${v.slug}" data-link
      title="${esc(`${T.lingue_nomi?.[v.lingua_video] || v.lingua_video}${v.stato === "bozza" ? ` · ${T.in_prep_breve}` : ""}`)}">${bandiera(v.lingua_video)} ${esc((v.lingua_video || "").toUpperCase())}${v.stato === "bozza" ? `<i class="punto-prep"></i>` : ""}</a>`).join("")}</div>` : "";
  return `<article class="scheda"><a href="/p/${p.slug}" data-link class="s-link">${copertina(p)}</a><div class="corpo">${lingue}
    <a href="/p/${p.slug}" data-link class="s-link s-corpo">${p.sottotitolo ? `<p>${esc(p.sottotitolo)}</p>` : ""}${minimappa(p.mappa)}${prossima}
      <div class="riga">${p.lingua_video ? `<span title="${T.lingua_video} ${esc(p.lingua_video)}">${bandiera(p.lingua_video)}</span>·` : ""}<span>${p.tappe} ${T.tappe}</span>·<span>${p.durata_min || "?"} ${T.min}</span>·<span>${p.tappe_fatte}/${p.tappe} ${T.fatte}</span>${etichette}</div></a></div></article>`;
}

function disegnaGriglia(gruppi, elenco) {
  const pronti = gruppi.filter((g) => g.pronte.length);
  const visibili = pronti.filter((g) => passaFiltri(g));
  $$("[data-conta]").forEach((c) => { const k = c.dataset.conta; const n = pronti.filter((g) => passaFiltri(g, false) && (!k || statoPercorso(versioneMostrata(g)) === k)).length; c.textContent = n; });
  const filtrato = FILTRI.stato || FILTRI.categoria || FILTRI.lingua || FILTRI.cerca.trim();
  $("#griglia").innerHTML = visibili.map(schedaGruppo).join("")
    + (filtrato && !visibili.length ? `<div class="vuoto-filtri"><p>${T.nessun_risultato}</p><button class="bottone" id="f-togli">${T.togli_filtri}</button></div>` : "")
    + `<div class="scheda nuova" id="b-nuovo" role="button" tabindex="0"><div><div class="piu">+</div><b>${T.nuovo}</b><p>${T.nuovo_sotto}</p></div></div>`;
  if ($("#f-togli")) $("#f-togli").onclick = () => { Object.assign(FILTRI, { stato: "", categoria: "", lingua: "", cerca: "" }); salvaFiltri(); mostraBiblioteca(); };
  $("#b-nuovo").onclick = finestraNuovo;
  $("#b-nuovo").onkeydown = (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); finestraNuovo(); } };
  // las versiones aún en borrador (fichas de vídeos en curso): aparte, con las fichas que faltan; estimación ~15 fichas al día, en cola
  let somma = 0;
  const bozze = elenco.filter((p) => p.stato === "bozza").filter((p) => passaFiltri({ versioni: [p], pronte: [], ultima: p }, false))
    .sort((a, b) => (a.schede_mancanti || 0) - (b.schede_mancanti || 0));
  $("#preparazione").innerHTML = bozze.length ? `<section class="preparazione"><h2>${T.in_preparazione}</h2><p class="sotto">${T.in_preparazione_sotto}</p>
    <ul>${bozze.map((p) => { somma += p.schede_mancanti || 0; return `<li><a href="/p/${p.slug}" data-link style="${stileTinta(p)}"><span class="p-colore">${svgIcona(iconaDi(p))}</span>
      <span class="p-testo"><b>${esc(p.titolo)}</b><small>${bandiera(p.lingua_video)} ${T.video_in} ${esc(T.lingue?.[p.lingua_video] || p.lingua_video || "")}</small></span>
      <span class="p-stato">${p.schede_mancanti ? `${T.schede_da_fare(p.schede_mancanti)} · ${T.giorni_circa(Math.ceil(somma / 15))}` : ""}</span></a></li>`; }).join("")}</ul></section>` : "";
}

function finestraNuovo() {
  apriFinestra(`<h2>${T.nuovo}</h2><p class="sotto">${T.nuovo_spiega}</p>
    <div class="campo"><label>${T.nuovo_tema}</label><input id="n-tema" placeholder="${esc(T.nuovo_esempio)}"></div>
    <p class="sotto" style="margin:4px 0 0">${T.o_copia}</p><div class="comando"><code id="n-cmd">/escool create "…"</code><button class="bottone piccolo" id="n-copia">${T.copia}</button></div>
    <div class="piede"><button class="bottone" data-chiudi>${T.annulla}</button>${S.cfg.da_rete ? "" : `<button class="bottone pieno" id="n-apri">${T.apri_term}</button>`}</div>`);
  const segno = (localStorage.getItem("motore") || S.cfg.assistente?.motore) === "codex" ? "$" : "/";  // en Codex las skills se llaman con $
  const cmd = () => `/escool create "${$("#n-tema").value.replace(/["`$;&|<>\n]/g, "").trim() || "…"}"`;
  const mostra = () => cmd().replace(/^\//, segno);
  $("#n-cmd").textContent = mostra();
  $("#n-tema").oninput = () => ($("#n-cmd").textContent = mostra());
  $("#n-copia").onclick = () => copia(mostra()).then(() => avviso(T.copiato));
  if ($("#n-apri")) $("#n-apri").onclick = async () => {
    if (!$("#n-tema").value.trim()) return $("#n-tema").focus();
    // a la terminal el tema va sin comillas (el servidor no las acepta en los comandos); la skill toma el resto de la línea como tema
    try { await api("terminale", { comando: cmd().replace(/"/g, "") }); avviso(T.terminale_aperto); chiudiFinestra(); } catch (e) { avviso(e.message); }
  };
  setTimeout(() => $("#n-tema").focus(), 50);
}

// ---------- página de la ruta: cabecera de portada y línea vertical de las etapas ----------
async function mostraPanoramica(slug) {
  try { S.p = await api("percorsi/" + slug); } catch { return vai("/"); }
  const p = S.p, mappa = mappaLocale(), pos = p.progressi?.posizione || {};
  const prossima = mappa.find((m) => m.stato !== "fatta" && m.stato !== "buco");
  const tPos = p.tappe.find((t) => t.n === pos.tappa);
  const tRip = (tPos && !progressoTappa(tPos) && tPos.video.length ? tPos : p.tappe.find((t) => t.n === prossima?.n)) || p.tappe[0];
  const vRip = tRip.video.find((v) => v.id === pos.video) || tRip.video[0];
  const iniziato = mappa.some((m) => m.stato !== "da_vedere" && m.stato !== "buco");
  const etichetta = !prossima ? T.ripassa : iniziato ? T.riprendi_tappa(tRip.n) : T.inizia;
  const fatte = mappa.filter((m) => m.stato === "fatta").length;
  const avvisi = (Array.isArray(p.avvisi) ? p.avvisi : []).map((a) => (typeof a === "string" ? a : a.testo || a.cosa || JSON.stringify(a)));
  const cambi = Array.isArray(p.cambi_recenti) ? p.cambi_recenti : [];
  $("#briciole").innerHTML = `<span class="b-percorso"><a href="/" data-link>${T.biblioteca}</a> / <b>${esc(p.titolo)}</b></span>`;
  S.immagini = immaginiUniche(p);
  const versioni = (p.versioni || []).length > 1 ? `<div class="e-lingue"><small>${T.video_in_breve}</small>${p.versioni.map((v) => `<a class="lingua ${v.slug === p.slug ? "attiva" : ""} ${v.stato === "bozza" ? "bozza" : ""}" href="/p/${v.slug}" data-link>${bandiera(v.lingua_video)} ${esc(T.lingue_nomi?.[v.lingua_video] || v.lingua_video || "")}${v.stato === "bozza" ? `<i>${T.in_prep_breve}${v.schede_mancanti ? ` · ${v.schede_mancanti}` : ""}</i>` : ""}</a>`).join("")}</div>` : "";
  $("#vista").innerHTML = `<section class="panoramica" style="${stileTinta(p)}">
    <header class="eroe" style="${stileTinta(p)}">${svgIcona(iconaDi(p), "e-icona")}<div class="e-testo">
      <div class="c-sopra"><span>${T.percorso}</span><span>${p.tappe.length} ${T.tappe}</span><span>${p.durata_min || "?"} ${T.min}</span>${p.lingua_video ? `<span>${bandiera(p.lingua_video)} ${T.video_in} ${esc(T.lingue?.[p.lingua_video] || p.lingua_video)}</span>` : ""}</div>
      <h1>${esc(p.titolo)}</h1>${p.sottotitolo ? `<p class="e-sotto">${esc(p.sottotitolo)}</p>` : ""}
      ${versioni}${minimappa(mappa, true)}
      <div class="e-azioni"><a class="bottone pieno grande" href="${urlVideo(tRip, vRip)}" data-link>▶ ${etichetta}</a>
        <button class="bottone grande vetro" id="b-ripasso">${T.ripasso}</button><a class="bottone grande vetro" href="/api/esporta/${esc(p.slug)}">${T.esporta}</a></div>
      <small class="e-piede">${fatte}/${p.tappe.length} ${T.fatte} · ${T.controllato_il} ${esc(p.controllato || "?")}${p.fonti ? ` · ${esc(p.fonti)}` : ""}</small>
    </div></header>
    <div class="pan-fasce" id="fasce">${fascePercorso()}</div>
    <div class="pan-corpo"><ol class="linea">${p.tappe.map((t) => tappaInLinea(t, mappa.find((m) => m.n === t.n))).join("")}</ol>
      <aside class="pan-lato">${p.arrivo ? `<section><h3>${T.arrivo}</h3><p>${esc(p.arrivo)}</p></section>` : ""}
        ${cambi.length ? `<details class="fisarmonica"><summary>${T.cambi} (${cambi.length})</summary><ol class="cambi">${cambi.map((c) => `<li><time>${esc(c.data || "")}</time><span>${esc(c.cosa || "")}</span></li>`).join("")}</ol></details>` : ""}
        ${avvisi.length ? `<details class="fisarmonica"><summary>${T.avvisi} (${avvisi.length})</summary><ul class="avvisi">${avvisi.map((a) => `<li>${esc(a)}</li>`).join("")}</ul></details>` : ""}
      </aside></div></section>`;
  $("#b-ripasso").onclick = finestraRipasso;
  $$("#fasce [data-term]").forEach((b) => (b.onclick = () => comandoTerminale(b.dataset.term)));
}

function tappaInLinea(t, m) {
  const [pr, ...alt] = t.video;
  const visto = (v) => (videoVisto(v.id) ? `<span class="visto" title="${T.visto}">✓</span>` : "");
  const pezzo = (v) => (v.fine ? `${T.spezzone} ${esc(v.inizio || "0:00")}–${esc(v.fine)}` : T.intero);
  const nAtt = (pr?.attenzione || []).length;
  const badge = [m.dubbi ? `<span class="etichetta avviso">${m.dubbi} ${T.dubbi}</span>` : "", t.da_ricontrollare ? `<span class="etichetta avviso">↻ ${T.ricontrolla_breve}</span>` : "",
    nAtt ? `<span class="etichetta errore">⚠ ${nAtt} ${T.attenzione.toLowerCase()}</span>` : ""].join("");
  const fonte = t.letture?.length ? `<div class="fonte">${svgIcona("libro", "i-libro")}<span>${T.fonte_ufficiale}:</span><a href="${esc(t.letture[0].url)}" target="_blank" rel="noopener">${esc(t.letture[0].titolo)} ↗</a>${t.letture.length > 1 ? `<span class="piu">+${t.letture.length - 1}</span>` : ""}</div>` : "";
  const corpo = pr ? `<a class="v-grande" href="${urlVideo(t, pr)}" data-link><div class="miniatura">${immagine(S.immagini, t, pr)}<span class="durata">${durataSpezzone(pr)}</span><span class="play">▶</span>${visto(pr)}</div>
      <div class="v-dida"><b>${esc(pr.titolo)}</b><small>${esc(pr.canale)} · ${pezzo(pr)}</small></div></a>
    ${alt.length ? `<div class="alt"><small>${T.alternative}</small>${alt.map((v) => `<a class="v-piccolo" href="${urlVideo(t, v)}" data-link><div class="miniatura">${immagine(S.immagini, t, v, false)}<span class="durata">${durataSpezzone(v)}</span>${visto(v)}</div>
      <span>${esc(v.canale)}<small>${esc(v.titolo)}</small></span></a>`).join("")}</div>` : ""}`
    : `<div class="buco-box"><b>${T.buco_tappa}.</b> ${esc(t.buco || "")}</div>`;
  return `<li class="t-linea st-${m.stato}${m.attuale ? " attuale" : ""}" id="tappa-${t.n}"><span class="nodo">${m.stato === "fatta" ? "✓" : t.n}</span>
    <div class="t-card ${pr && alt.length ? "" : "solo"}"><div class="t-testa"><small>${T.tappa} ${t.n} · ${t.minuti_video || "?"} ${T.min}${m.stato !== "da_vedere" ? ` · ${nomeStato(m.stato)}` : ""}</small>
      <h2>${esc(t.titolo)}</h2>${badge ? `<div class="t-badge">${badge}</div>` : ""}</div>
      ${t.obiettivo ? `<p class="impari"><b>${T.cosa_impari}.</b> ${esc(t.obiettivo)}</p>` : ""}${corpo}${fonte}</div></li>`;
}

// ---------- reproductor ----------
async function mostraPercorso(slug) {
  try { S.p = await api("percorsi/" + slug); } catch { return vai("/"); }
  const q = new URLSearchParams(location.search);
  const pos = S.p.progressi?.posizione || {};
  S.tappa = S.p.tappe.find((t) => t.n === Number(q.get("t") || pos.tappa)) || S.p.tappe[0];
  S.video = S.tappa.video.find((v) => v.id === (q.get("v") || pos.video)) || S.tappa.video[0] || null;
  const disp = S.cfg.disposizione?.chat || "destra";
  $("#vista").innerHTML = `<div class="lettore chat-${esc(disp)}" id="lettore" style="${stileTinta(S.p)}"><aside class="tappe" id="tappe"></aside><div class="velo" id="velo"></div><section class="centro" id="centro"></section><aside class="chat" id="chat"></aside></div>`;
  $("#velo").onclick = () => document.body.classList.remove("tappe-aperte");
  disegnaTappe();
  await apriVideo(S.tappa, S.video, false);
}

function progressoTappa(t) { return S.p.progressi?.tappe?.[String(t.n)]?.fatta; }
function videoVisto(id) { return S.p.progressi?.video?.[id]?.visto; }

function disegnaBriciole() {
  // en el ordenador «Biblioteca / ruta»; con la pantalla estrecha «☰ Etapa 3 · título», que abre la lista de las etapas
  $("#briciole").innerHTML = `<span class="b-percorso"><a href="/" data-link>${T.biblioteca}</a> / <a href="/p/${S.p.slug}" data-link><b>${esc(S.p.titolo)}</b></a></span>
    <button class="b-tappa" id="b-briciola-tappe"><b>${T.tappa} ${S.tappa.n}</b> · ${esc(S.tappa.titolo)}</button>`;
  $("#b-briciola-tappe").onclick = () => document.body.classList.toggle("tappe-aperte");
}

function disegnaTappe() {
  const fatte = S.p.tappe.filter(progressoTappa).length;
  $("#tappe").innerHTML = `<div class="testa"><h2><a href="/p/${S.p.slug}" data-link>${esc(S.p.titolo)}</a></h2><div class="riga"><span>${fatte}/${S.p.tappe.length} ${T.fatte}</span><span>${S.p.durata_min || "?"} ${T.min}</span></div>
      <div class="barra-prog"><i style="width:${(100 * fatte) / S.p.tappe.length}%"></i></div>
      <div style="display:flex;gap:6px;margin-top:12px;flex-wrap:wrap"><button class="bottone piccolo" id="b-ripasso">${T.ripasso}</button><a class="bottone piccolo" href="/api/esporta/${S.p.slug}">${T.esporta}</a></div></div>` +
    S.p.tappe.map((t) => {
      const attiva = t.n === S.tappa.n;
      const meta = [`<span>${t.minuti_video || "?"} ${T.min}</span>`, t.segnale_buco ? `<span class="etichetta avviso"><i class="punto-buco"></i>${t.dubbi_aperti} ${T.dubbi}</span>` : "",
        t.da_ricontrollare ? `<span class="etichetta avviso">↻</span>` : "", t.buco ? `<span class="etichetta errore">${T.buco_tappa}</span>` : ""].join("");
      const video = t.video.map((v) => `<li><button data-video="${v.id}" data-tappa="${t.n}" class="${S.video?.id === v.id ? "attivo" : ""}">
          <span class="spunta">${videoVisto(v.id) ? "✓" : ""}</span><span class="v-titolo">${esc(v.canale)} · ${esc(v.titolo)}</span><span>${bandiera(v.lingua)}</span></button></li>`).join("");
      return `<div class="tappa st-${statoTappa(t)} ${progressoTappa(t) ? "fatta" : ""} ${attiva ? "attiva" : ""}"><button data-apri-tappa="${t.n}"><span class="num">${progressoTappa(t) ? "✓" : t.n}</span>
        <span><div class="t-titolo">${esc(t.titolo)}</div><div class="t-meta">${meta}</div></span></button>${attiva ? `<ul>${video}</ul>` : ""}</div>`;
    }).join("");
  // con las etapas plegables: abrir una etapa muestra sus vídeos (el panel sigue abierto), elegir un vídeo lo cierra
  $$("[data-apri-tappa]").forEach((b) => (b.onclick = () => { const t = S.p.tappe.find((x) => x.n === Number(b.dataset.apriTappa)); apriVideo(t, t.video[0], true, false); }));
  $$("[data-video]").forEach((b) => (b.onclick = () => { const t = S.p.tappe.find((x) => x.n === Number(b.dataset.tappa)); apriVideo(t, t.video.find((v) => v.id === b.dataset.video)); }));
  $("#b-ripasso").onclick = finestraRipasso;
}

async function apriVideo(tappa, video, aggiornaUrl = true, chiudiTappe = true) {
  const cambiaChat = S.ambito === "video" || !S.chat || !$("#messaggi");
  S.tappa = tappa; S.video = video;
  if (aggiornaUrl && video) history.replaceState({}, "", `/p/${S.p.slug}?t=${tappa.n}&v=${video.id}`);
  if (chiudiTappe) document.body.classList.remove("tappe-aperte");
  disegnaBriciole();
  disegnaTappe();
  S.schedaVideo = !video ? {} : video.tipo === "lezione" ? await fetch(video.src.replace(/\.mp4$/, ".json")).then((r) => r.json()).catch(() => ({}))
    : await api(`schede/${S.p.slug}/${video.id}`).catch(() => ({}));
  disegnaCentro();
  if (cambiaChat) disegnaChat(); else aggiornaTestaChat();  // el chat de la ruta se queda igual al pasar de un vídeo a otro
  if (video) api("progresso", { percorso: S.p.slug, posizione: { tappa: tappa.n, video: video.id } }).catch(() => {});
}

function comandoTerminale(cmd) {
  // desde el teléfono la terminal (que se abriría en el ordenador) no sirve: se muestra el comando para lanzarlo allí
  if (S.cfg.da_rete) {
    const c = S.cfg.assistente?.motore === "codex" ? cmd.replace(/^\//, "$") : cmd;
    apriFinestra(`<p>${T.sul_computer}</p><div class="comando"><code>${esc(c)}</code><button class="bottone piccolo" id="c-copia">${T.copia}</button></div><div class="piede"><button class="bottone" data-chiudi>${T.chiudi}</button></div>`);
    $("#c-copia").onclick = () => copia(c).then(() => avviso(T.copiato));
    return;
  }
  api("terminale", { comando: cmd }).then(() => avviso(T.terminale_aperto)).catch((e) => avviso(e.message));
}

function fascePercorso() {
  const f = [];
  if (S.p.stato === "bozza") f.push(`<div class="fascia avviso"><p>${T.bozza}</p></div>`);
  if (S.p.avviso_aggiornamento) f.push(`<div class="fascia avviso"><p>${T.avviso_agg(S.p.giorni_dal_controllo)}</p><button class="bottone piccolo" data-term="/escool update ${S.p.slug}">${T.aggiorna}</button></div>`);
  return f.join("");
}
function fasce() {
  const f = [fascePercorso()];
  const t = S.tappa;
  if (t.da_ricontrollare) f.push(`<div class="fascia avviso"><p>${T.ricontrolla}${t.nota_ricontrollo ? " " + esc(t.nota_ricontrollo) : ""}</p><button class="bottone piccolo" data-term="/escool update ${S.p.slug} ${t.n}">${T.ricontrolla_tappa}</button></div>`);
  // la nota habla de los vídeos de YouTube de la etapa: con la lección generada delante, solo queda en «Lecturas oficiales»
  if (t.nota_letture && S.video?.tipo !== "lezione") f.push(`<div class="fascia"><p>📖 ${esc(t.nota_letture)}</p><button class="bottone piccolo" data-apri-letture>${T.letture}</button></div>`);
  if (t.buco) f.push(`<div class="fascia avviso"><p><b>${T.buco_tappa}.</b> ${esc(t.buco)}</p></div>`);
  if (t.segnale_buco) f.push(`<div class="fascia avviso"><p>${T.buco(t.dubbi_aperti)}</p><button class="bottone piccolo" id="f-ripasso">${T.ripasso}</button><button class="bottone piccolo" data-term="/escool reinforce ${S.p.slug} ${t.n}">${T.rinforza}</button></div>`);
  return f.join("");
}

function disegnaCentro() {
  const v = S.video;
  $("#centro").innerHTML = v ? `<div id="fasce"></div><div class="cornice"><div id="player"></div></div><div class="tacche" id="tacche"></div><div id="info"></div>` : `<div id="fasce"></div><p class="vuoto">—</p>`;
  disegnaInfo();
  if (v) creaPlayer(v);
}

function disegnaInfo() {
  const t = S.tappa, v = S.video, sch = S.schedaVideo || {};
  $("#fasce").innerHTML = fasce();
  if (!v) return;
  const ini = sec(v.inizio), fin = sec(v.fine);
  const spezzone = v.tipo === "lezione" ? `<span class="etichetta lezione">${T.lezione}</span>`
    : ini != null || fin != null ? `<span class="etichetta">${T.spezzone} ${mmss(ini || 0)}–${fin ? mmss(fin) : "fine"}</span>` : `<span class="etichetta">${T.intero}</span>`;
  const voto = sch.qualita?.voto ? `<span class="etichetta">${T.voto} ${sch.qualita.voto}/5</span>` : "";
  const fatta = progressoTappa(t);
  $("#info").innerHTML = `<div class="v-testa"><h1>${esc(v.titolo)}</h1><div class="v-azioni">
      <button class="bottone" id="b-visto">${videoVisto(v.id) ? "✓ " + T.visto : T.segna_visto}</button>
      <button class="bottone ${fatta ? "" : "pieno"}" id="b-tappa">${fatta ? "✓ " + T.tappa_fatta : T.tappa_da_fare}</button>
      ${prossimaTappa() ? `<button class="bottone" id="b-prossima" title="${esc(`${T.tappa} ${prossimaTappa().n} · ${prossimaTappa().titolo}`)}">${T.prossima_tappa} ▶</button>` : ""}</div></div>
    <div class="v-meta"><b>${esc(v.canale)}</b>·<span>${esc(v.pubblicato || "")}</span>·<span>${bandiera(v.lingua)} ${T.lingua_video} ${esc(v.lingua || "?")}</span>·<span>${mmss(v.durata_s)}</span>
      <span class="etichetta ${v.ruolo === "principale" ? "ok" : ""}">${v.ruolo === "principale" ? T.principale : T.alternativo}</span>${spezzone}${voto}
      ${(sch.mostra_schermo || sch.mostra_ads_manager) ? `<span class="etichetta">${T.schermo}</span>` : ""}</div>
    ${v.perche ? `<p style="margin:0;color:var(--testo-2)">${esc(v.perche)}</p>` : ""}
    <div class="v-azioni"><button class="bottone" id="b-nota">✎ ${T.nota_qui}</button><button class="bottone" id="b-dubbio">? ${T.dubbio_qui}</button></div>
    <nav class="schede-nav">${["riassunto", "chat", "note", "attenzione", "letture"].map((k) => `<button data-scheda="${k}" class="${schedaAttiva() === k ? "attivo" : ""} ${k === "chat" ? "solo-stretto" : ""}">${k === "chat" ? T.chat_tab : T[k]}${contaScheda(k)}</button>`).join("")}</nav>
    <div class="pannello-scheda" id="pannello"></div>`;
  $$("[data-scheda]").forEach((b) => (b.onclick = () => { S.scheda = b.dataset.scheda; disegnaInfo(); if (S.scheda === "chat") scorriChat(); }));
  $$("[data-term]").forEach((b) => (b.onclick = () => comandoTerminale(b.dataset.term)));
  if ($("#f-ripasso")) $("#f-ripasso").onclick = finestraRipasso;
  $$("[data-apri-letture]").forEach((b) => (b.onclick = () => { S.scheda = "letture"; disegnaInfo(); }));
  $("#b-visto").onclick = () => segnaVisto(!videoVisto(v.id));
  $("#b-tappa").onclick = () => segnaTappa(!progressoTappa(t));
  if ($("#b-prossima")) $("#b-prossima").onclick = () => { const n = prossimaTappa(); apriVideo(n, n.video[0] || null); if (stretto()) window.scrollTo({ top: 0, behavior: "smooth" }); };
  $("#b-nota").onclick = () => { S.scheda = "note"; pausa(); disegnaInfo(); $("#nota-input")?.focus(); };
  $("#b-dubbio").onclick = async () => {
    pausa(); const m = mmss(adesso());
    await aggiungiNota("dubbio", `${T.dubbio_qui} (${m})`);
    if (S.ambito !== "video") { S.ambito = "video"; localStorage.setItem("ambito", "video"); await disegnaChat(); }
    if (stretto()) { S.scheda = "chat"; disegnaInfo(); }
    const ta = $("#domanda"); if (ta) { ta.value = `${T.minuto_di} ${m}: `; ta.focus(); }
  };
  $("#lettore")?.classList.toggle("in-chat", schedaAttiva() === "chat");
  disegnaPannello();
  disegnaTacche();
}

function prossimaTappa() { return S.p.tappe[S.p.tappe.indexOf(S.tappa) + 1] || null; }

// marcas bajo el vídeo: toda la duración, el fragmento elegido resaltado, las notas (azul), las dudas y las preguntas (naranja),
// los avisos de la ficha (rojo). Un toque en la marca va a ese minuto, un toque en la barra va a ese punto.
function disegnaTacche() {
  const el = $("#tacche"), v = S.video; if (!el || !v) return;
  const dur = v.durata_s || sec(v.fine) || 0;
  if (!dur) { el.innerHTML = ""; return; }
  const ini = sec(v.inizio) || 0, fin = Math.min(dur, sec(v.fine) || dur);
  const pct = (x) => `${Math.max(0, Math.min(100, (100 * x) / dur)).toFixed(2)}%`;
  const att = (Array.isArray(v.attenzione) ? v.attenzione : []).map((a) => ({ s: sec(a.minuto), a })).filter((x) => x.s != null && !isNaN(x.s));
  const note = noteVideo().filter((n) => n.secondi != null);
  el.innerHTML = `<div class="binario" id="binario" title="${esc(T.tacche_aiuto)}"><i class="tratto" style="left:${pct(ini)};width:${pct(fin - ini)}"></i><i class="testina" id="testina"></i>
    ${att.map(({ s, a }) => `<button class="tacca attenzione" style="left:${pct(s)}" data-vai="${s}" title="${esc(`${mmss(s)} · ${a.dice || ""}`)}" aria-label="${esc(mmss(s))}"></button>`).join("")}
    ${note.map((n) => `<button class="tacca ${n.tipo === "nota" ? "nota" : "dubbio"}${n.risolto ? " risolto" : ""}" style="left:${pct(n.secondi)}" data-vai="${n.secondi}" title="${esc(`${n.minuto || mmss(n.secondi)} · ${n.testo}`)}" aria-label="${esc(n.minuto || mmss(n.secondi))}"></button>`).join("")}</div>`;
  $("#binario").onclick = (e) => {
    if (e.target.closest(".tacca") || !S.player?.seekTo) return;
    const r = e.currentTarget.getBoundingClientRect();
    S.player.seekTo(Math.max(0, ((e.clientX - r.left) / r.width) * dur), true); S.player.playVideo();
  };
  muoviTestina();
}
function muoviTestina() {
  const t = $("#testina"), v = S.video, dur = v?.durata_s || sec(v?.fine);
  if (t && dur) t.style.left = `${Math.min(100, (100 * adesso()) / dur).toFixed(2)}%`;
}

// en el ordenador el chat está siempre al lado: la pestaña «Chat» solo existe con la pantalla estrecha
function schedaAttiva() { return S.scheda === "chat" && !stretto() ? "riassunto" : S.scheda; }

function contaScheda(k) {
  const sch = S.schedaVideo || {};
  if (k === "attenzione") { const v = S.video || {}; const n = Array.isArray(v.attenzione) ? v.attenzione.length : (sch.affermazioni || []).filter((a) => a.verdetto === "superata" || a.verdetto === "sbagliata").length; return n ? `<span class="conta">${n}</span>` : ""; }
  if (k === "note") { const n = noteVideo().length; return n ? `<span class="conta">${n}</span>` : ""; }
  return "";
}
const noteVideo = () => (S.p.note || []).filter((n) => n.video === S.video?.id);

function disegnaPannello() {
  const v = S.video, t = S.tappa, sch = S.schedaVideo || {}, el = $("#pannello");
  const k = schedaAttiva();
  if (k === "chat") { el.innerHTML = ""; return; }
  if (k === "riassunto") {
    if (!sch.riassunto && !v.riassunto) { el.innerHTML = `<p class="vuoto">${T.senza_scheda}</p><p style="white-space:pre-wrap;color:var(--testo-2)">${esc((v.descrizione || "").slice(0, 600))}</p>`; return; }
    const punti = v.punti || [];
    el.innerHTML = `<p>${esc(v.riassunto || sch.riassunto)}</p>` +
      (punti.length ? `<ul class="punti">${punti.map((p) => `<li><button class="minuto" data-vai="${esc(p.minuto)}">${esc(p.minuto)}</button><span>${esc(p.testo)}</span></li>`).join("")}</ul>` : "") +
      (sch.capitoli?.length ? `<details class="fisarmonica" ${punti.length ? "" : "open"}><summary>${T.capitoli} (${sch.capitoli.length})</summary>${sch.capitoli.map((c) => `<div class="capitolo"><h4><button class="minuto" data-vai="${esc(c.inizio)}">${esc(c.inizio)}</button>${esc(c.titolo)}</h4><ul>${(c.punti_chiave || []).map((x) => `<li>${esc(x)}</li>`).join("")}</ul></div>`).join("")}</details>` : "") +
      ((sch.per_chi_impara || sch.per_italia) ? `<details class="fisarmonica"><summary>${T.per_te}</summary><p>${esc(sch.per_chi_impara || sch.per_italia)}</p></details>` : "") +
      (v.tipo === "lezione" && sch.scene?.length
        ? `<details class="fisarmonica"><summary>${T.testo_lezione}</summary>${sch.scene.map((c) => `<div class="capitolo"><h4><button class="minuto" data-vai="${esc(mmss(c.inizio))}">${esc(mmss(c.inizio))}</button>${esc(c.titolo)}${c.consiglio ? ` <span class="etichetta">${T.consiglio_nostro}</span>` : ""}</h4><p>${esc(c.testo)}</p></div>`).join("")}</details>`
          + `<details class="fisarmonica"><summary>${T.fonti_lezione}</summary><ul>${[...new Set(sch.scene.flatMap((c) => c.fonti || []))].map((f) => { const id = (f.match(/^(\d+)-/) || [])[1]; return `<li>${id ? `<a href="https://help.openai.com/en/articles/${esc(f.replace(/\.md$/, ""))}" target="_blank" rel="noopener">${esc(f.replace(/^\d+-/, "").replace(/\.md$/, "").replaceAll("-", " "))}</a>` : esc(f)}</li>`; }).join("")}</ul></details>`
        : `<details class="fisarmonica"><summary>${T.sottotitoli.split(" (")[0]}</summary><p style="color:var(--testo-2)">${T.sottotitoli}</p></details>`) +
      (v.tipo === "lezione" && v.voce ? `<p class="sotto" style="margin-top:10px">${T.voce_di}: ${esc(v.voce)}</p>` : "") +
      (v.avviso_voce ? `<div class="esito-voce forse">${esc(v.avviso_voce)}</div>` : "");
  } else if (k === "attenzione") {
    // los avisos del fragmento elegido (de la ruta); si el vídeo no tiene fragmento, los de toda la ficha
    const aff = Array.isArray(v.attenzione) ? v.attenzione : (sch.affermazioni || []).filter((a) => a.verdetto === "superata" || a.verdetto === "sbagliata");
    const cls = { superata: "avviso", sbagliata: "errore", non_verificabile: "" };
    const nome = { superata: T.v_superata, sbagliata: T.v_sbagliata, non_verificabile: T.v_non };
    el.innerHTML = aff.length ? aff.map((a) => `<div class="affermazione"><button class="minuto" data-vai="${esc(a.minuto)}">${esc(a.minuto)}</button><div>
        <p>${esc(a.dice || a.testo)} ${a.verdetto ? `<span class="etichetta ${cls[a.verdetto] || ""}">${nome[a.verdetto] || esc(a.verdetto)}</span>` : ""}</p>${a.perche ? `<small>${esc(a.perche)}</small>` : ""}</div></div>`).join("")
      : `<p class="vuoto">${sch.affermazioni ? T.nessuna_attenzione : T.senza_scheda}</p>`;
  } else if (k === "note") {
    const note = noteVideo().sort((a, b) => (a.secondi || 0) - (b.secondi || 0));
    el.innerHTML = `<div class="scrivi-nota"><input id="nota-input" placeholder="${esc(T.scrivi_nota)}"><button class="bottone" id="nota-salva">${T.aggiungi}</button></div>` +
      (note.length ? note.map((n) => `<div class="nota ${n.risolto ? "risolto" : ""}"><button class="minuto" data-vai="${esc(n.minuto || "0:00")}">${esc(n.minuto || "—")}</button>
        <span class="etichetta ${n.tipo === "dubbio" ? "avviso" : ""}">${esc(n.tipo)}</span><span class="n-testo">${esc(n.testo)}</span>
        <span class="n-azioni">${n.tipo !== "nota" ? `<button class="bottone piccolo" data-risolvi="${n.id}" title="risolto">✓</button>` : ""}<button class="bottone piccolo" data-elimina="${n.id}">×</button></span></div>`).join("")
        : `<p class="vuoto">${T.nessuna_nota}</p>`);
    const salva = () => { const x = $("#nota-input").value.trim(); if (x) aggiungiNota("nota", x); };
    $("#nota-salva").onclick = salva;
    $("#nota-input").onkeydown = (e) => { if (e.key === "Enter") salva(); };
    $$("[data-elimina]").forEach((b) => (b.onclick = () => cambiaNota({ elimina: b.dataset.elimina })));
    $$("[data-risolvi]").forEach((b) => (b.onclick = () => { const n = S.p.note.find((x) => x.id === b.dataset.risolvi); cambiaNota({ id: n.id, risolto: !n.risolto }); }));
  } else {
    el.innerHTML = `<div class="letture">${(t.letture || []).map((l) => `<a href="${esc(l.url)}" target="_blank" rel="noopener">↗ ${esc(l.titolo)}</a>`).join("") || `<p class="vuoto">—</p>`}</div>
      ${t.nota_letture ? `<p>${esc(t.nota_letture)}</p>` : ""}
      <details class="fisarmonica"><summary>${T.alla_fine}</summary><p>${esc(t.obiettivo || "")}</p><ul class="concetti">${(t.concetti || []).map((c) => `<li>${esc(c)}</li>`).join("")}</ul></details>`;
  }
}

document.addEventListener("click", (e) => {
  const b = e.target.closest("[data-vai]");
  if (b && S.player?.seekTo) { const s = sec(b.dataset.vai); if (s != null) { S.player.seekTo(s, true); S.player.playVideo(); } }
  const r = e.target.closest("[data-rimando]");
  if (r && S.p) {
    const [n, id, m] = r.dataset.rimando.split("|");
    const t = S.p.tappe.find((x) => x.n === Number(n) && x.video.some((v) => v.id === id)) || S.p.tappe.find((x) => x.video.some((v) => v.id === id));
    if (!t) return avviso(T.rimando_fuori);
    const v = t.video.find((x) => x.id === id), s = sec(m);
    if (S.video?.id === v.id && S.player?.seekTo) { if (s != null) S.player.seekTo(s, true); S.player.playVideo(); }
    else { S.saltaA = s; apriVideo(t, v); }
    if (stretto()) window.scrollTo({ top: 0, behavior: "smooth" });
  }
});
// al pasar del ordenador a la pantalla estrecha (o al girar la tableta) la pestaña «Chat» aparece o desaparece
matchMedia("(max-width: 899px)").addEventListener("change", () => { if (S.p && $("#info")) disegnaInfo(); });

// ---------- notas y progreso ----------
async function aggiungiNota(tipo, testo) {
  const s = Math.round(adesso());
  const r = await api("note", { percorso: S.p.slug, tappa: S.tappa.n, video: S.video.id, secondi: s, minuto: mmss(s), testo, tipo });
  S.p.note = r.note; await ricaricaSegnali();
}
async function cambiaNota(d) { const r = await api("note", { percorso: S.p.slug, ...d }); S.p.note = r.note; await ricaricaSegnali(); }
async function ricaricaSegnali() {
  const p = await api("percorsi/" + S.p.slug);
  S.p.tappe.forEach((t) => { const n = p.tappe.find((x) => x.n === t.n); Object.assign(t, { dubbi_aperti: n.dubbi_aperti, segnale_buco: n.segnale_buco }); });
  S.p.note = p.note; S.p.progressi = p.progressi;
  disegnaTappe(); disegnaInfo();
}
async function segnaVisto(si) {
  S.p.progressi = await api("progresso", { percorso: S.p.slug, video: S.video.id, secondi: Math.round(adesso()), visto: si });
  if (si && S.video.ruolo === "principale" && !progressoTappa(S.tappa)) return segnaTappa(true);
  disegnaTappe(); disegnaInfo();
}
async function segnaTappa(si) {
  S.p.progressi = await api("progresso", { percorso: S.p.slug, tappa: S.tappa.n, fatta: si });
  disegnaTappe(); disegnaInfo();
}

// ---------- reproductor de YouTube ----------
function caricaApiYouTube() {
  if (window.YT?.Player) return Promise.resolve();
  if (!caricaApiYouTube.p) caricaApiYouTube.p = new Promise((ok) => {
    window.onYouTubeIframeAPIReady = ok;
    const s = document.createElement("script"); s.src = "https://www.youtube.com/iframe_api"; document.head.appendChild(s);
  });
  return caricaApiYouTube.p;
}
function adesso() { try { return S.player?.getCurrentTime?.() || 0; } catch { return 0; } }
function pausa() { try { S.player?.pauseVideo?.(); } catch { /* */ } }
function fermaTimer() { clearInterval(S.timer); S.timer = null; clearInterval(S.timerTestina); S.timerTestina = null; }

function creaPlayerLocale(v) {
  const box = $("#player"); if (!box) return;
  const ultimo = S.p.progressi?.video?.[v.id]?.ultimo, dur = v.durata_s || 0;
  const salto = S.saltaA; S.saltaA = null;
  const partenza = salto != null ? salto : ultimo && ultimo > 5 && (!dur || ultimo < dur - 10) ? ultimo : 0;
  box.outerHTML = `<video id="player" controls playsinline preload="metadata" poster="${esc(v.copertina || "")}" src="${esc(v.src)}"></video>`;
  const el = $("#player");
  el.addEventListener("loadedmetadata", () => { if (partenza) el.currentTime = partenza; if (salto != null) el.play().catch(() => {}); }, { once: true });
  el.addEventListener("play", () => { if (!S.timer) S.timer = setInterval(registraTempo, 5000); if (!S.timerTestina) S.timerTestina = setInterval(muoviTestina, 1000); });
  el.addEventListener("pause", muoviTestina);
  el.addEventListener("seeked", muoviTestina);
  el.addEventListener("ended", () => { registraTempo(); if (!videoVisto(v.id)) segnaVisto(true); });
  S.player = { getCurrentTime: () => el.currentTime, seekTo: (x) => { el.currentTime = x; }, playVideo: () => el.play().catch(() => {}), pauseVideo: () => el.pause() };
}

async function creaPlayer(v) {
  fermaTimer();
  if (v.tipo === "lezione") return creaPlayerLocale(v);
  await caricaApiYouTube();
  const lingua = S.cfg.sottotitoli?.lingua || S.cfg.lingua || "it";
  const ultimo = S.p.progressi?.video?.[v.id]?.ultimo;
  const ini = sec(v.inizio) || 0, fin = sec(v.fine);
  const salto = S.saltaA; S.saltaA = null;  // enlace desde el chat: se empieza en ese minuto, también fuera del fragmento
  const partenza = salto != null ? salto : ultimo && ultimo > ini + 5 && (!fin || ultimo < fin - 10) ? ultimo : ini;
  const vars = { rel: 0, playsinline: 1, hl: lingua, cc_lang_pref: lingua, cc_load_policy: S.cfg.sottotitoli?.sempre === false ? 0 : 1, origin: location.origin, start: Math.floor(partenza) };
  if (fin && !(salto != null && salto >= fin)) vars.end = fin;
  S.player = new YT.Player("player", {
    videoId: v.id, playerVars: vars,
    events: {
      onApiChange: () => { try { if (v.lingua !== lingua) S.player.setOption("captions", "track", { languageCode: lingua }); } catch { /* */ } },
      onStateChange: (e) => {
        if (e.data === YT.PlayerState.PLAYING && !S.timer) S.timer = setInterval(registraTempo, 5000);
        if (e.data === YT.PlayerState.PLAYING && !S.timerTestina) S.timerTestina = setInterval(muoviTestina, 1000);
        if (e.data === YT.PlayerState.PAUSED || e.data === YT.PlayerState.BUFFERING) muoviTestina();
        if (e.data === YT.PlayerState.CUED && salto != null) { try { S.player.playVideo(); } catch { /* */ } }
        if (e.data === YT.PlayerState.ENDED) { registraTempo(); if (!videoVisto(v.id)) segnaVisto(true); }
      },
    },
  });
}
function registraTempo() {
  const s = Math.round(adesso()); if (!S.video || !s) return;
  const fin = sec(S.video.fine) || S.video.durata_s;
  const visto = fin && s >= fin * 0.95;
  api("progresso", { percorso: S.p.slug, video: S.video.id, secondi: s, visto: visto || undefined }).then((p) => {
    const eraVisto = videoVisto(S.video.id); S.p.progressi = p;
    if (visto && !eraVisto) segnaVisto(true);
  }).catch(() => {});
}

// ---------- chat ----------
// dos conversaciones separadas: una por vídeo y otra para toda la ruta (cada una con su historial)
function chiaveChat() { return S.ambito === "percorso" ? `chat:${S.p.slug}:_percorso` : `chat:${S.p.slug}:${S.video?.id}`; }
function aggiornaTestaChat() {
  $$("[data-ambito]").forEach((b) => b.classList.toggle("attivo", b.dataset.ambito === S.ambito));
}
async function disegnaChat() {
  const el = $("#chat"); if (!el) return;
  const motori = S.cfg.motori || {};
  const motore = localStorage.getItem("motore") || S.cfg.assistente?.motore || "claude";
  const percorsoIntero = S.ambito === "percorso";
  el.innerHTML = `<div class="testa"><div class="ambito" role="tablist">${["video", "percorso"].map((a) => `<button data-ambito="${a}" role="tab" class="${S.ambito === a ? "attivo" : ""}">${a === "video" ? T.ambito_video : T.ambito_percorso}</button>`).join("")}</div>
      <select id="motore" title="${T.assistente}">${["claude", "codex"].map((m) => `<option value="${m}" ${m === motore ? "selected" : ""} ${motori[m] ? "" : "disabled"}>${m === "claude" ? "Claude" : "Codex"}</option>`).join("")}</select>
      ${S.cfg.da_rete ? "" : `<button class="icona" id="b-term" title="${T.terminale}">⌘</button>`}</div>
    <div class="messaggi" id="messaggi"></div>
    <div class="scrivi"><textarea id="domanda" placeholder="${esc(percorsoIntero ? T.chiedi_percorso : T.chiedi)}"></textarea><div class="riga"><small>${T.invio_ctrl}</small><button class="bottone pieno" id="b-invia">${T.invia}</button></div></div>`;
  $$("[data-ambito]").forEach((b) => (b.onclick = () => { if (S.inCorso || S.ambito === b.dataset.ambito) return; S.ambito = b.dataset.ambito; localStorage.setItem("ambito", S.ambito); disegnaChat(); }));
  $("#motore").onchange = (e) => { localStorage.setItem("motore", e.target.value); localStorage.removeItem(chiaveChat()); disegnaChat(); };
  if ($("#b-term")) $("#b-term").onclick = () => api("terminale", { percorso: S.p.slug, tappa: S.tappa.n, video: S.video?.id, secondi: Math.round(adesso()), motore: $("#motore").value })
    .then(() => avviso(T.terminale_aperto)).catch((e) => avviso(e.message));
  $("#b-invia").onclick = invia;
  $("#domanda").onkeydown = (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); invia(); } };
  const cid = localStorage.getItem(chiaveChat());
  S.chat = cid ? await api("chat/" + cid).catch(() => null) : null;
  disegnaMessaggi();
  if (!motori.claude && !motori.codex) $("#messaggi").innerHTML = `<div class="msg errore">${T.nessun_motore}</div>`;
}
function disegnaMessaggi() {
  const box = $("#messaggi"); if (!box) return;
  const msg = S.chat?.messaggi || [];
  const percorsoIntero = S.ambito === "percorso";
  if (!msg.length) {
    const esempi = percorsoIntero ? [T.esempio_p1, T.esempio_p2, T.esempio_p3] : [T.esempio1, T.esempio2, T.esempio3];
    box.innerHTML = `<div class="chat-vuota">${percorsoIntero ? T.chat_vuota_percorso : T.chat_vuota}${esempi.map((x) => `<button class="bottone" data-esempio="${esc(x)}">${esc(x)}</button>`).join("")}</div>`;
    $$("[data-esempio]").forEach((b) => (b.onclick = () => { $("#domanda").value = b.dataset.esempio; invia(); }));
    return;
  }
  // en el chat de la ruta un «4:12» suelto no dice de qué vídeo es: solo valen los enlaces [[t3 ID 4:12]]
  box.innerHTML = msg.map((m) => m.ruolo === "utente"
    ? `<div class="msg utente">${m.secondi != null && !percorsoIntero ? `<button class="minuto" data-vai="${mmss(m.secondi)}">${mmss(m.secondi)}</button>` : ""}${esc(m.testo)}</div>`
    : `<div class="msg assistente ${m.errore && !m.testo ? "errore" : ""}">${m.testo ? md(m.testo, { minuti: !percorsoIntero }) : esc(m.errore || "")}</div>`).join("");
  scorriChat();
}
function scorriChat() {
  const box = $("#messaggi"); if (!box) return;
  box.scrollTop = box.scrollHeight;
  // con la pantalla estrecha se desplaza la página, no el recuadro de los mensajes
  if (stretto() && schedaAttiva() === "chat") window.scrollTo(0, document.documentElement.scrollHeight);
}
async function invia() {
  const ta = $("#domanda"), testo = ta.value.trim();
  const percorsoIntero = S.ambito === "percorso";
  if (!testo || S.inCorso || (!S.video && !percorsoIntero)) return;
  S.inCorso = true; $("#b-invia").disabled = true; ta.value = "";
  const secondi = S.video ? Math.round(adesso()) : null, motore = $("#motore").value;
  S.chat = S.chat || { messaggi: [] };
  S.chat.messaggi.push({ ruolo: "utente", testo, secondi }, { ruolo: "assistente", testo: "" });
  disegnaMessaggi();
  const ultimo = () => $$("#messaggi .msg.assistente").pop();
  ultimo().innerHTML = `<span class="pensa">${motore === "codex" ? "Codex" : "Claude"} ${T.pensa}</span>`;
  const chiave = chiaveChat();
  const risposta = S.chat.messaggi[S.chat.messaggi.length - 1];
  try {
    await flusso("chiedi", { percorso: S.p.slug, tappa: S.tappa.n, video: S.video?.id, secondi, domanda: testo, chat: localStorage.getItem(chiave), motore, ambito: S.ambito }, (e) => {
      if (e.t === "inizio") localStorage.setItem(chiave, e.chat);
      if (e.t === "pezzo") { risposta.testo += e.testo; if (chiave === chiaveChat() && ultimo()) { ultimo().innerHTML = md(risposta.testo, { minuti: !percorsoIntero }); scorriChat(); } }
      if (e.t === "fine" && e.errore && !risposta.testo) { risposta.errore = e.errore; disegnaMessaggi(); }
    });
    // la pregunta se convierte en nota: bajo el vídeo con el minuto, o de la ruta (acaba en el repaso, no marca «buco» en la etapa)
    const r = await api("note", percorsoIntero ? { percorso: S.p.slug, tappa: S.tappa.n, video: null, testo, tipo: "domanda", ambito: "percorso" }
      : { percorso: S.p.slug, tappa: S.tappa.n, video: S.video.id, secondi, minuto: mmss(secondi), testo, tipo: "domanda" });
    S.p.note = r.note; await ricaricaSegnali();
  } catch (err) { risposta.errore = err.message; disegnaMessaggi(); }
  S.inCorso = false; const b = $("#b-invia"); if (b) b.disabled = false;
}

// ---------- repaso ----------
async function finestraRipasso() {
  const dubbi = (S.p.note || []).filter((n) => n.tipo !== "nota");
  if (!dubbi.length) return apriFinestra(`<h2>${T.ripasso}</h2><p class="sotto">${T.ripasso_vuoto}</p><div class="piede"><button class="bottone" data-chiudi>${T.chiudi}</button></div>`);
  apriFinestra(`<h2>${T.ripasso}</h2><p class="sotto">${dubbi.length} ${T.dubbi}</p><div class="md" id="ripasso"><p class="pensa">${T.ripasso_genera}</p></div><div class="piede"><button class="bottone" data-chiudi>${T.chiudi}</button></div>`);
  let testo = "";
  try {
    await flusso("ripasso", { percorso: S.p.slug }, (e) => {
      if (e.t === "pezzo") { testo += e.testo; $("#ripasso").innerHTML = md(testo); }
      if (e.t === "fine" && e.errore && !testo) $("#ripasso").innerHTML = `<p class="msg errore">${esc(e.errore)}</p>`;
    });
  } catch (err) { $("#ripasso").innerHTML = `<p class="msg errore">${esc(err.message)}</p>`; }
}

// ---------- ajustes ----------
function finestraImpostazioni() {
  const c = S.cfg, p = c.profilo || {}, a = c.assistente || {};
  const opz = (val, scelte) => scelte.map(([k, n]) => `<option value="${k}" ${val === k ? "selected" : ""}>${n}</option>`).join("");
  apriFinestra(`<h2>${T.impostazioni}</h2><p class="sotto">${T.personalizza}</p>
    <div class="due"><div class="campo"><label>${T.tema}</label><select id="i-tema">${opz(localStorage.getItem("tema") || c.tema, [["auto", T.auto], ["chiaro", T.chiaro], ["scuro", T.scuro]])}</select></div>
    <div class="campo"><label>${T.lingua}</label><select id="i-lingua">${opz(c.lingua, [["it", "Italiano"], ["es", "Español"], ["en", "English"]])}</select></div>
    <div class="campo"><label>${T.disposizione}</label><select id="i-chat">${opz(c.disposizione?.chat, [["destra", T.destra], ["sinistra", T.sinistra], ["sotto", T.sotto], ["nascosta", T.nascosta]])}</select></div>
    <div class="campo"><label>${T.assistente}</label><select id="i-motore">${opz(a.motore, [["claude", "Claude Code"], ["codex", "Codex"]])}</select></div>
    <div class="campo"><label>${T.modello} Claude</label><input id="i-mc" value="${esc(a.modello_claude || "")}" placeholder="sonnet, opus, haiku"></div>
    <div class="campo"><label>${T.modello} Codex</label><input id="i-mx" value="${esc(a.modello_codex || "")}" placeholder="auto"></div></div>
    <h3 style="font-size:14px;margin:8px 0 10px">${T.profilo}</h3>
    <div class="due"><div class="campo"><label>${T.p_nome}</label><input id="i-nome" value="${esc(p.nome || "")}"></div>
    <div class="campo"><label>${T.p_livello}</label><select id="i-livello">${opz(p.livello, [["principiante", "principiante"], ["intermedio", "intermedio"], ["esperto", "esperto"]])}</select></div></div>
    <div class="campo"><label>${T.p_obiettivo}</label><input id="i-obiettivo" value="${esc(p.obiettivo || "")}"></div>
    <div class="campo"><label>${T.p_come}</label><input id="i-come" value="${esc(p.come_spiegare || "")}"></div>
    <h3 style="font-size:14px;margin:8px 0 6px">${T.v_titolo}</h3><div id="i-voce"></div>
    <h3 style="font-size:14px;margin:8px 0 6px">${T.telefono}</h3><div id="i-tel"></div>
    ${c.da_rete ? "" : `<details class="fisarmonica" id="i-diag"><summary>${T.diagnosi}</summary><pre id="i-diagnosi" style="font-size:11.5px;white-space:pre-wrap;color:var(--testo-2)">…</pre></details>`}
    <div class="piede"><button class="bottone" data-chiudi>${T.annulla}</button><button class="bottone pieno" id="i-salva">${T.salva}</button></div>`);
  if ($("#i-diag")) $("#i-diag").ontoggle = async (e) => { if (e.target.open) $("#i-diagnosi").textContent = JSON.stringify(await api("diagnosi"), null, 1); };
  disegnaTelefono();
  disegnaVoce(opz);
  $("#i-salva").onclick = async () => {
    const sbagliato = $$("#i-voce input[id^='i-v-id']").find((i) => i.value.trim() && !ID_VOCE.test(i.value.trim()));
    if (sbagliato) { $("#i-v-esito").innerHTML = `<div class="esito-voce no">${T.v_id_errato}</div>`; sbagliato.focus(); return; }
    impostaTema($("#i-tema").value);
    const c2 = await api("config", {
      tema: $("#i-tema").value, lingua: $("#i-lingua").value, disposizione: { chat: $("#i-chat").value },
      assistente: { motore: $("#i-motore").value, modello_claude: $("#i-mc").value.trim(), modello_codex: $("#i-mx").value.trim() },
      profilo: { nome: $("#i-nome").value.trim(), livello: $("#i-livello").value, obiettivo: $("#i-obiettivo").value.trim(), come_spiegare: $("#i-come").value.trim() },
      ...($("#i-v-motore") ? { lezioni: {
        motore: $("#i-v-motore").value === "elevenlabs" ? "elevenlabs" : "gratuita",
        ...($("#i-v-motore").value.startsWith("gratuita:") ? { voce: { modello: $("#i-v-motore").value.split(":")[1] } } : {}),
        elevenlabs: { voce: $("#i-v-id").value.trim(), modello: $("#i-v-modello").value,
          voci: Object.fromEntries(["it", "es", "en"].map((l) => [l, $("#i-v-id-" + l).value.trim()])) },
      } } : {}),
    });
    localStorage.removeItem("motore");
    applicaConfig({ ...S.cfg, ...c2 }); chiudiFinestra(); instrada();
  };
}

// ---------- voz de las lecciones (gratuita o ElevenLabs) ----------
// La clave va al servidor solo desde este ordenador y nunca vuelve: la página solo sabe si está.
const ID_VOCE = /^[A-Za-z0-9]{10,40}$/;
const VOCI_GRATUITE = [["chatterbox", "Chatterbox", "mac"], ["supertonic", "Supertonic 3", "ovunque"], ["kokoro-onnx", "Kokoro", "ovunque"]];
async function disegnaVoce(opz) {
  const el = $("#i-voce"); if (!el) return;
  const L = S.cfg.lezioni || {}, E = L.elevenlabs || {}, modello = E.modello || "eleven_multilingual_v2";
  const scelta = L.motore === "elevenlabs" ? "elevenlabs" : "gratuita:" + (L.voce?.modello || "auto");
  const riga = (id, val, ph) => `<div class="riga-campo"><input id="${id}" value="${esc(val || "")}" placeholder="${esc(ph)}" autocomplete="off" spellcheck="false"><button class="bottone" data-verifica="${id}">${T.v_verifica}</button></div>`;
  el.innerHTML = `<p class="sotto" style="margin:0 0 8px">${T.v_spiega}</p>
    <div class="campo"><label>${T.v_motore}</label><select id="i-v-motore">${opz(scelta, [["gratuita:auto", T.v_auto("…")],
      ...VOCI_GRATUITE.map(([id, nome, dove]) => ["gratuita:" + id, `${nome} · ${T.v_dove[dove]}`]), ["elevenlabs", T.v_11l]])}</select></div>
    <p class="sotto" id="i-v-grat" style="margin:-4px 0 12px"></p>
    <div id="i-v-11l">
      <div class="campo"><label>${T.v_chiave}</label><div id="i-v-chiave" class="sotto">…</div></div>
      <div class="campo"><label>${T.v_id}</label>${riga("i-v-id", E.voce, T.v_id_ph)}</div>
      <p class="sotto" style="margin:-6px 0 12px">${T.v_id_aiuto}</p>
      <div class="campo"><label>${T.v_modello}</label><select id="i-v-modello"><option value="${esc(modello)}">${esc(modello)}</option></select></div>
      <div id="i-v-esito"></div>
      <details class="fisarmonica" ${Object.values(E.voci || {}).some(Boolean) ? "open" : ""}><summary>${T.v_per_lingua}</summary>
        ${["it", "es", "en"].map((l) => `<div class="campo"><label>${T.lingue_nomi[l]}</label>${riga("i-v-id-" + l, E.voci?.[l], T.v_vuoto_usa)}</div>`).join("")}
      </details>
    </div>`;
  const mostra = () => {
    const val = $("#i-v-motore").value, e = val === "elevenlabs", g = S.el?.gratuite;
    $("#i-v-11l").hidden = !e; $("#i-v-grat").hidden = e;
    if (g && !e) {
      const scelta = val.split(":")[1], ids = scelta === "auto" ? [...new Set(Object.values(g.auto))] : [scelta];
      const v = g.voci.find((x) => x.id === ids[0]);
      // «auto» con voces distintas por idioma: se dice cuál lee qué (p. ej. italiano Supertonic 3, español Kokoro)
      const perLingua = ids.length > 1 ? Object.entries(g.auto).map(([l, id]) => `${T.v_nomi_lingue[l]}: ${g.voci.find((x) => x.id === id)?.nome || id}`).join(" · ") + ". " : "";
      $("#i-v-grat").textContent = v?.dove === "mac" && !g.mac_apple ? T.v_grat_solo_mac
        : perLingua + (ids.every((id) => g.installate.includes(id)) ? T.v_grat_pronta : T.v_grat_manca);
    }
  };
  $("#i-v-motore").onchange = mostra; mostra();
  $$("[data-verifica]", el).forEach((b) => (b.onclick = () => verificaVoce(b.dataset.verifica)));
  let st;
  try { st = await api("elevenlabs"); } catch (e) { $("#i-v-chiave").innerHTML = `<span class="msg errore">${esc(e.message)}</span>`; return; }
  S.el = st;
  // nombres de las voces gratuitas con lo que hay de verdad en este ordenador
  const g = st.gratuite, nomi = Object.fromEntries(VOCI_GRATUITE.map(([id, n]) => [id, n]));
  for (const o of $("#i-v-motore").options) {
    const id = o.value.split(":")[1];
    if (id === "auto") o.textContent = T.v_auto([...new Set(Object.values(g.auto))].map((x) => nomi[x] || x).join(" / "));
    else if (id) {
      const v = g.voci.find((x) => x.id === id), altrove = v.dove === "mac" && !g.mac_apple;  // Chatterbox en Windows: no se instala
      o.disabled = altrove;
      o.textContent = `${v.nome} · ${T.v_dove[v.dove]}${altrove ? " · " + T.v_non_qui : v.installata ? "" : " · " + T.v_da_installare}`;
    }
  }
  mostra();
  disegnaChiave(st);
  caricaModelli();
}

async function caricaModelli() {
  const sel = $("#i-v-modello"); if (!sel || !S.el?.chiave || S.el.errore) return;
  const scelto = sel.value;
  try {
    const mm = await api("elevenlabs/modelli");
    sel.innerHTML = mm.map((m) => `<option value="${esc(m.id)}" ${m.id === scelto ? "selected" : ""}>${esc(m.nome)} · ${T.v_cpc(m.crediti_per_carattere)}</option>`).join("");
  } catch (e) { /* se queda el modelo guardado */ }
}

function disegnaChiave(st) {
  const box = $("#i-v-chiave"), ab = st.abbonamento;
  const stato = !st.chiave ? T.v_chiave_no : st.errore ? `<span class="msg errore">${esc(st.errore)}</span>` : ab ? T.v_piano(ab) : "✓";
  const gratis = ab?.gratuito ? `<div class="esito-voce forse" style="margin-top:8px">${T.v_gratis}</div>` : "";
  if (st.da_rete) { box.innerHTML = `${stato}${gratis}<div style="margin-top:6px">${T.v_chiave_rete}</div>`; return; }
  box.innerHTML = `<div>${stato}</div>${gratis}
    <div class="riga-campo" style="margin-top:8px"><input id="i-v-k" type="password" placeholder="${esc(T.v_chiave_ph)}" autocomplete="off" spellcheck="false">
    <button class="bottone" id="i-v-k-salva">${T.v_salva_chiave}</button></div>
    <div style="margin-top:6px">${T.v_chiave_dove}${st.chiave ? ` · <button class="link" id="i-v-k-togli">${T.v_rimuovi}</button>` : ""}</div>
    <div id="i-v-k-msg"></div>`;
  const invia = async (corpo) => {
    $("#i-v-k-msg").innerHTML = `<p class="sotto">${T.v_prova}</p>`;
    let r;
    try { r = await api("elevenlabs/chiave", corpo); } catch (e) { r = { ok: false, messaggio: e.message }; }
    const nuovo = await api("elevenlabs").catch(() => st);
    S.el = nuovo; disegnaChiave(nuovo);
    $("#i-v-k-msg").innerHTML = `<p class="${r.ok ? "sotto" : "msg errore"}" style="margin-top:6px">${esc(r.messaggio || "")}</p>`;
    if (r.ok && corpo.chiave) caricaModelli();
  };
  $("#i-v-k-salva").onclick = () => { const v = $("#i-v-k").value.trim(); if (v) invia({ chiave: v }); };
  if ($("#i-v-k-togli")) $("#i-v-k-togli").onclick = () => invia({ rimuovi: true });
}

async function verificaVoce(campo) {
  const out = $("#i-v-esito"), id = $("#" + campo).value.trim(), lingua = $("#" + campo).id.match(/-(it|es|en)$/)?.[1] || S.cfg.lingua || "it";
  if (!S.el?.chiave) { out.innerHTML = `<div class="esito-voce no">${T.v_prima_chiave}</div>`; return; }
  if (!ID_VOCE.test(id)) { out.innerHTML = `<div class="esito-voce no">${T.v_id_errato}</div>`; return; }
  out.innerHTML = `<div class="esito-voce">${T.v_prova}</div>`;
  let r;
  try { r = await api(`elevenlabs/voce/${id}?lingua=${lingua}&modello=${encodeURIComponent($("#i-v-modello").value)}&caratteri=3800`); }
  catch (e) { out.innerHTML = `<div class="esito-voce no">${esc(e.message)}</div>`; return; }
  const v = r.voce, li = (a) => a.map((x) => `<li>${esc(x)}</li>`).join("");
  out.innerHTML = `<div class="esito-voce">
    ${v ? `<div><b>${esc(v.nome)}</b> · ${esc(T.v_cat[v.categoria] || v.categoria || "")}${v.lingue?.length ? ` · ${T.v_lingue} ${v.lingue.join(", ")}` : ""} · ${T.lingue_nomi[lingua]}</div>` : ""}
    <div class="${r.ok ? "si" : "no"}" style="margin-top:4px"><b>${r.ok ? "✓ " + T.v_ok : "✗ " + T.v_no}</b></div>
    ${r.problemi?.length ? `<ul class="no">${li(r.problemi)}</ul>` : ""}${r.avvisi?.length ? `<ul class="forse">${li(r.avvisi)}</ul>` : ""}
    ${r.servono != null && v ? `<div>${T.v_lezione(r.servono, r.abbonamento?.rimasti)}</div>` : ""}
    ${v?.anteprima ? `<audio controls preload="none" src="${esc(v.anteprima)}"></audio>` : ""}</div>`;
}

async function disegnaTelefono(azione) {
  const el = $("#i-tel"); if (!el) return;
  if (S.cfg.da_rete) { el.innerHTML = `<p class="sotto">${T.tel_da_qui}</p>`; return; }
  let r;
  try { r = await api("rete", azione); } catch (e) { el.innerHTML = `<p class="msg errore">${esc(e.message)}</p>`; return; }
  el.innerHTML = `<p class="sotto" style="margin:0 0 8px">${T.tel_spiega}</p>
    <label class="interruttore"><input type="checkbox" id="i-tel-on" ${r.voluta ? "checked" : ""}> ${T.tel_attiva}</label>
    ${r.attiva ? `<div class="tel"><div>${T.tel_apri}</div><div class="url">${esc(r.url)}</div><div>${T.tel_codice}</div><div class="codice">${esc(r.codice)}</div>
      <small>${T.tel_collegati(r.telefoni)} · <button class="link" id="i-tel-nuovo">${T.tel_nuovo}</button> (${T.tel_nuovo_spiega})</small>
      <p class="sotto" style="margin:8px 0 0">${T.tel_home}</p></div>` : r.voluta && r.errore ? `<p class="msg errore">${esc(r.errore)}</p>` : ""}`;
  $("#i-tel-on").onchange = (e) => disegnaTelefono({ attiva: e.target.checked });
  if ($("#i-tel-nuovo")) $("#i-tel-nuovo").onclick = () => disegnaTelefono({ nuovo_codice: true });
}

// ---------- exportar: primero el aviso sobre las voces ElevenLabs del plan gratuito ----------
document.addEventListener("click", async (e) => {
  const a = e.target.closest('a[href^="/api/esporta/"]'); if (!a) return;
  e.preventDefault();
  const avvisi = await api(a.getAttribute("href").replace("/api/", "") + "/avvisi").catch(() => []);
  if (!avvisi.length) { location.href = a.href; return; }
  apriFinestra(`<h2>${T.esp_titolo}</h2><p class="sotto">${T.esp_spiega}</p>
    <ul>${avvisi.map((x) => `<li>${T.tappa} ${x.tappa} · ${esc(x.voce)}</li>`).join("")}</ul>
    ${[...new Set(avvisi.map((x) => x.avviso))].map((t) => `<div class="esito-voce forse">${esc(t)}</div>`).join("")}
    <div class="piede"><button class="bottone" data-chiudi>${T.annulla}</button><a class="bottone pieno" href="${esc(a.href)}" id="esp-vai">${T.esp_scarica}</a></div>`);
  $("#esp-vai").onclick = () => setTimeout(chiudiFinestra, 300);
});

// ---------- ventanas ----------
function apriFinestra(html) { $("#finestra-corpo").innerHTML = html; const d = $("#finestra"); if (!d.open) d.showModal(); $$("[data-chiudi]", d).forEach((b) => (b.onclick = chiudiFinestra)); }
function chiudiFinestra() { $("#finestra").close(); }
$("#finestra").addEventListener("click", (e) => { if (e.target.id === "finestra") chiudiFinestra(); });

// ---------- arranque ----------
(async function avvio() {
  applicaConfig(await api("config"));
  $("#b-tema").onclick = () => impostaTema(document.documentElement.dataset.tema === "scuro" ? "chiaro" : "scuro");
  $("#b-impostazioni").onclick = finestraImpostazioni;
  $("#b-tappe").onclick = () => document.body.classList.toggle("tappe-aperte");
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") document.body.classList.remove("tappe-aperte"); });
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => { if ((localStorage.getItem("tema") || "auto") === "auto") impostaTema("auto", false); });
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => {});
  instrada();
})();

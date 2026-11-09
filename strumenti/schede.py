"""Ficha de cada vídeo hecha por Gemini viéndolo desde el enlace público (sin descargarlo), comparada con el mapa.

  python strumenti/schede.py <ruta>                   los vídeos de lavoro/youtube/lista.json que aún no tienen ficha
  python strumenti/schede.py <ruta> ID [ID ...]       solo estos
  opciones: --modello gemini-3.8-flash
            --aspetta   agotada la cuota del día, espera al reinicio (las 9:00 en Italia) y sigue hasta terminar la lista:
                        para listas largas, para dejarlo encendido (en Mac con `caffeinate -i -s`, ordenador enchufado)
            --pagamento [--tetto 1]   con el plan de pago (facturación activa en el proyecto de Google de la clave): sin el
                        límite de 20 peticiones ni el de 8 horas de vídeo, el coste de cada ficha a partir de los tokens en
                        lavoro/chiamate.jsonl, y se detiene antes de superar el tope en dólares de esta ejecución (1 $ si no
                        lo indicas)

A Gemini solo van el enlace del vídeo público y el mapa (datos tomados de las fuentes oficiales): nunca chats, notas ni perfil.
Plan gratuito (medido el 6/11/2026): **20 peticiones al día por modelo y por proyecto de Google** y 8 horas de vídeo al
día; se reinician a medianoche del Pacífico (las 9:00 en Italia). **También cuentan las respuestas de error** (503 «sobrecarga»,
400): el 6/11 la cuota de 3.8 Flash se agotó tras 5 fichas correctas y 15 errores. 3.7 Flash usa la cuota de 3.8 (su 429
dice «model: gemini-3.8-flash»): como reserva no sirve. Por eso se reintenta poco y despacio, un modelo agotado se salta hasta
el día siguiente, y la cuenta se hace sobre todas las rutas (la cuota es del proyecto, no de la ruta).
Con el plan gratuito, Google puede usar los contenidos para mejorar sus productos: solo se envían datos públicos.
Plan de pago (precios leídos el 08/11/2026 en ai.google.dev/gemini-api/docs/pricing): 3.8 Flash 0,75 $ por millón de
tokens de entrada (vídeo incluido) y 3,75 $ de salida, razonamiento incluido, hasta el 31/12/2026. Un vídeo cuesta ~95 tokens
por segundo (resolución baja): 15 minutos son unos 0,08 $. La cuenta real la hace Google; aquí está la estimación, para el tope.
Cada llamada queda en lavoro/chiamate.jsonl.
"""
import http.client
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

import metadati
from comune import PERCORSI, cartella, chiave, leggi, registra, scrivi, secondi, aiuto

MODELLO = "gemini-3.8-flash"
RISERVE = ["gemini-3.5-flash"]                    # 3.7 Flash no: usa la cuota de 3.8
RIPROVA = ("HTTP 503", "HTTP 500", "RETE")        # sobrecarga o red: se reintenta más tarde
ATTESE = (0, 60, 180)                            # rondas de intentos en todos los modelos: cada intento gasta cuota
TETTO_GIORNO_S = 8 * 3600
RICHIESTE_GIORNO = 20                            # por modelo, plan gratuito
QUOTA_DI = {"gemini-3.7-flash": "gemini-3.8-flash"}   # modelos que gastan la cuota de otro (visto en los 429)
ESAURITI = set()                                 # modelos con el límite diario alcanzado en esta ejecución
PREZZI = {"gemini-3.8-flash": (0.75, 3.75)}      # $ por millón de tokens, entrada y salida, plan de pago (08/11/2026)
PREZZO_ALTRI = PREZZI["gemini-3.8-flash"]        # los modelos sin precio leído: para el tope cuentan como 3.8 Flash
TOKEN_AL_SECONDO = 100                           # para la estimación antes de la llamada (medidos ~95 con MEDIA_RESOLUTION_LOW)
SPESA = [0.0]                                    # dólares gastados en esta ejecución, con el plan de pago
INIZIO = datetime.now(timezone.utc).isoformat(timespec="seconds")

# el prompt queda en italiano: es el que se ha probado
PROMPT = """Sei il revisore di un percorso di apprendimento. Chi impara: {livello}, lingua {lingua}. Guarda tutto il video (immagini e audio).
Qui sotto c'è la MAPPA del percorso, scritta dalle fonti ufficiali il {creata}: è la verità di riferimento. Il video è del {pubblicato}.

MAPPA:
{mappa}

Rispondi SOLO con un JSON con questa forma (testi in {lingua_nome}, minuti come "m:ss" o "h:mm:ss"):
{{"lingua_parlata": "it|es|en|...",
 "riassunto": "3-4 frasi: cosa insegna e a chi serve",
 "mostra_schermo": true/false,                 // si vede davvero lo schermo di {strumento}
 "da_zero": true/false,
 "capitoli": [{{"inizio": "m:ss", "fine": "m:ss", "titolo": "...", "tappe": [n], "schermo": true/false, "punti_chiave": ["..."]}}],
 "affermazioni": [{{"minuto": "m:ss", "dice": "...", "verdetto": "giusta|superata|sbagliata|non_verificabile",
                   "perche": "confronto con la mappa: cita il concetto o il cambio con la data"}}],
 "per_chi_impara": "cosa vale o non vale nel paese di chi impara ({paese})",
 "qualita": {{"voto": 1-5, "perche": "chiarezza, pratica, ritmo, aggiornamento"}},
 "consiglio": "principale|alternativo|scarta", "consiglio_perche": "...",
 "tappa_migliore": n, "spezzone_migliore": {{"inizio": "m:ss", "fine": "m:ss"}}}}
Regole: le affermazioni sono tutte quelle su numeri, regole, prezzi, limiti, formati, paesi, date. Non inventare minuti.
«giusta» solo se la mappa la conferma; se la mappa non ne parla scrivi «non_verificabile». Una cosa giusta prima di un cambio
della lista CAMBI e diversa dopo è «superata», non «sbagliata»."""


def contesto(m):
    return {"tema": m["tema"], "avvisi": m.get("avvisi_italia") or m.get("avvisi", []), "cambi_recenti": m.get("cambi_recenti", []),
            "tappe": [{"n": t["n"], "titolo": t["titolo"], "obiettivo": t["obiettivo"], "concetti": [c["testo"] for c in t["concetti"]],
                       "errori_tipici": t.get("errori_tipici_da_scartare", [])} for t in m["tappe"]]}


def chiama(vid, testo, modello):
    corpo = {"contents": [{"parts": [{"file_data": {"file_uri": f"https://www.youtube.com/watch?v={vid}"}}, {"text": testo}]}],
             "generationConfig": {"responseMimeType": "application/json", "mediaResolution": "MEDIA_RESOLUTION_LOW", "temperature": 0.2}}
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{modello}:generateContent",
                                 data=json.dumps(corpo).encode(), method="POST",
                                 headers={"x-goog-api-key": chiave("GEMINI_API_KEY"), "Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=900) as r:
            return json.load(r), None, time.time() - t0
    except urllib.error.HTTPError as e:
        return None, {"errore": f"HTTP {e.code}", "dettaglio": e.read().decode("utf-8", "replace")[:400]}, time.time() - t0
    except (urllib.error.URLError, http.client.HTTPException, TimeoutError, ConnectionError, OSError) as e:
        return None, {"errore": "RETE", "dettaglio": f"{type(e).__name__}: {e}"[:300]}, time.time() - t0


def giorno_pacifico(ts):
    """Día en California (donde Google reinicia las cuotas), sin zoneinfo: en Windows faltan los datos de los husos horarios.
    Horario de verano de EE. UU.: del segundo domingo de marzo al primero de noviembre, a las 2:00 locales (10:00 UTC aprox.)."""
    t = datetime.fromisoformat(ts).astimezone(timezone.utc)
    return (t - timedelta(hours=scarto_pacifico(t))).date().isoformat()


def scarto_pacifico(t):
    def domenica(mese, n):
        d = datetime(t.year, mese, 1, 10, tzinfo=timezone.utc)
        return d + timedelta(days=(6 - d.weekday()) % 7 + 7 * (n - 1))
    return 7 if domenica(3, 2) <= t < domenica(11, 1) else 8


def prossimo_azzeramento():
    """Instante (UTC) de la próxima medianoche del Pacífico, más 10 minutos de margen."""
    ora = datetime.now(timezone.utc)
    ore = scarto_pacifico(ora)
    mezzanotte = datetime.combine((ora - timedelta(hours=ore)).date() + timedelta(days=1), datetime.min.time(), timezone.utc)
    return mezzanotte + timedelta(hours=ore, minutes=10)


def uso_oggi(slug=None):
    """Segundos de vídeo correctos y peticiones por modelo de hoy (día del Pacífico) en todas las rutas:
    la cuota es del proyecto de Google. También cuentan los errores, salvo los 429 (rechazos tras el límite)."""
    oggi = giorno_pacifico(datetime.now(timezone.utc).isoformat())
    secondi_video, richieste = 0, {}
    for f in PERCORSI.glob("*/lavoro/chiamate.jsonl"):
        for r in f.read_text(encoding="utf-8").splitlines():
            e = json.loads(r)
            if e.get("servizio") != "gemini" or giorno_pacifico(e["ts"]) != oggi:
                continue
            if e.get("errore") != "HTTP 429":
                q = QUOTA_DI.get(e["modello"], e["modello"])
                richieste[q] = richieste.get(q, 0) + 1
            if not e.get("errore"):
                secondi_video += e.get("durata_video_s") or 0
    return secondi_video, richieste


def annulla_costi(slug):
    """Un 429 «free_tier» con el plan de pago significa que la facturación no está activa: las fichas de esta ejecución
    han pasado con el plan gratuito (probado el 08/11/2026: 3 fichas correctas, luego el 429 «free_tier_requests, limit: 20»).
    Sus líneas vuelven a 0 $, así el registro no cuenta dinero que nunca se gastó."""
    f = PERCORSI / slug / "lavoro" / "chiamate.jsonl"
    righe, n = [], 0
    for r in f.read_text(encoding="utf-8").splitlines():
        e = json.loads(r)
        if e.get("servizio") == "gemini" and e.get("piano") == "pagamento" and e.get("ts", "") >= INIZIO:
            e.update(costo_usd=0.0, piano="gratuito", nota="fatturazione non attiva: passata col piano gratuito")
            n += 1
        righe.append(json.dumps(e, ensure_ascii=False))
    f.write_text("\n".join(righe) + "\n", encoding="utf-8")
    SPESA[0] = 0.0
    return n


def costo(modello, u):
    p_in, p_out = PREZZI.get(modello, PREZZO_ALTRI)
    uscita = (u.get("candidatesTokenCount") or 0) + (u.get("thoughtsTokenCount") or 0)
    return round(((u.get("promptTokenCount") or 0) * p_in + uscita * p_out) / 1e6, 5)


def una(slug, vid, m, meta, modello, tetto=None):
    """tetto: dólares con el plan de pago (None = plan gratuito)."""
    d = cartella(slug)
    lingua = m.get("lingua", "it")
    testo = PROMPT.format(livello=m.get("livello", "principiante"), lingua=lingua,
                          lingua_nome={"it": "italiano", "es": "spagnolo", "en": "inglese"}.get(lingua, lingua),
                          creata=m.get("creata", "?"), pubblicato=meta.get("pubblicato", "?"), strumento=m.get("strumento", "lo strumento del tema"),
                          paese=m.get("paese", "Italia"), mappa=json.dumps(contesto(m), ensure_ascii=False))
    modelli = [modello] + [r for r in RISERVE if r != modello]
    for attesa in ATTESE:
        vivi = [x for x in modelli if x not in ESAURITI
                and (tetto is not None or uso_oggi()[1].get(QUOTA_DI.get(x, x), 0) < RICHIESTE_GIORNO)]
        ESAURITI.update(x for x in modelli if x not in vivi)
        if not vivi:
            break
        if attesa:
            print(f"{vid}: Gemini sobrecargado ({', '.join(vivi)}), reintento dentro de {attesa} s")
            time.sleep(attesa)
        for mod in vivi:  # con el 503 se pasa enseguida al modelo siguiente: solo se espera cuando todos están sobrecargados
            ris, err, sec = chiama(vid, testo, mod)
            riga = {"servizio": "gemini", "modello": mod, "video": vid, "latenza_ms": int(sec * 1000), "costo_usd": 0.0}
            if err:
                registra(slug, {**riga, **err})
                if err["errore"] == "HTTP 429" and tetto is not None and "free_tier" in err["dettaglio"]:
                    n = annulla_costi(slug)
                    print("Google sigue respondiendo con el límite gratuito: la facturación no está activa en el proyecto de la clave"
                          + (f"; las {n} fichas anteriores han pasado gratis (coste devuelto a 0 $)" if n else ""))
                    return None
                if err["errore"] == "HTTP 429":
                    ESAURITI.add(mod)
                    if tetto is None:
                        print(f"{vid}: {mod} ha agotado las peticiones gratuitas de hoy")
                    else:
                        print(f"{vid}: {mod} responde 429 también con el plan de pago: {err['dettaglio'][:160]}")
                elif err["errore"] not in RIPROVA:
                    print(f"{vid}: {err['errore']} {err['dettaglio'][:160]}")
                    return False
                continue
            u = ris.get("usageMetadata", {})
            testo_r = "".join(p.get("text", "") for p in ris["candidates"][0]["content"]["parts"])
            try:
                sch = json.loads(testo_r)
            except json.JSONDecodeError:
                sch = {"errore_json": True, "grezzo": testo_r}
            if isinstance(sch, list):  # a veces Gemini responde con una lista de un solo objeto
                sch = sch[0] if len(sch) == 1 and isinstance(sch[0], dict) else {"errore_json": True, "grezzo": testo_r}
            sch.update(video=vid, modello=mod,  # la fecha del vídeo está en lavoro/youtube/metadati.json (dato de YouTube)
                       creata=datetime.now(timezone.utc).isoformat(timespec="seconds"))
            scrivi(d / "schede" / f"{vid}.json", sch)
            spesa = costo(mod, u) if tetto is not None else 0.0
            SPESA[0] += spesa
            registra(slug, {**riga, "costo_usd": spesa, "token_in": u.get("promptTokenCount"), "token_out": u.get("candidatesTokenCount"),
                            "token_pensiero": u.get("thoughtsTokenCount"), "durata_video_s": meta.get("durata_s"),
                            "piano": "pagamento" if tetto is not None else "gratuito"})
            print(f"{vid}: ok en {sec:.0f} s con {mod}, {u.get('promptTokenCount')} tokens, consejo {sch.get('consiglio')}"
                  + (f", {spesa:.3f} $ (en total {SPESA[0]:.3f} $ de {tetto:g} $)" if tetto is not None else ""))
            return True
    if all(x in ESAURITI for x in [modello] + RISERVE):
        print("todos los modelos han agotado las peticiones gratuitas de hoy: se vuelve a empezar después de las 9:00 (medianoche del Pacífico)")
        return None
    print(f"{vid}: Gemini sobrecargado también en los modelos de reserva, lo salto: vuelve a lanzarlo más tarde")
    return False


def main(a):
    modello = MODELLO
    if "--modello" in a:
        i = a.index("--modello")
        modello = a[i + 1]
        a = a[:i] + a[i + 2:]
    aspetta = "--aspetta" in a
    tetto = None
    if "--tetto" in a:
        i = a.index("--tetto")
        tetto = float(a[i + 1].replace(",", "."))
        a = a[:i] + a[i + 2:]
    if "--pagamento" in a:
        tetto = 1.0 if tetto is None else tetto
    elif tetto is not None:
        sys.exit("--tetto solo vale con --pagamento")
    a = [x for x in a if x not in ("--aspetta", "--pagamento")]
    if not a:
        sys.exit("falta el nombre de la ruta\n" + __doc__)
    slug, scelti = a[0], a[1:]
    d = cartella(slug)
    m = leggi(d / "lavoro" / "mappa.json") or sys.exit("falta lavoro/mappa.json")
    lista = {v["id"]: v for v in (leggi(d / "lavoro" / "youtube" / "lista.json") or [])}
    pert = {v["id"]: v for v in (leggi(d / "lavoro" / "youtube" / "pertinenti.json") or [])}
    meta_yt = metadati.validi(d)
    fatte, falliti = 0, {}
    while True:
        ids = [i for i in (scelti or lista) if not (d / "schede" / f"{i}.json").exists() and falliti.get(i, 0) < 2]
        finita = False
        for vid in ids:
            meta = lista.get(vid) or pert.get(vid) or meta_yt.get(vid) or {}
            if tetto is None and uso_oggi(slug)[0] + (meta.get("durata_s") or 0) > TETTO_GIORNO_S:
                print("alcanzado el tope del plan gratuito (8 h de vídeo al día): vuelve a lanzar mañana el mismo comando")
                finita = True
                break
            if tetto is not None:
                p_in, p_out = PREZZI.get(modello, PREZZO_ALTRI)
                stima = ((meta.get("durata_s") or 900) * TOKEN_AL_SECONDO + 12000) * p_in / 1e6 + 6000 * p_out / 1e6
                if SPESA[0] + stima > tetto:
                    print(f"{vid}: con esta ficha (~{stima:.2f} $) se superaría el tope de {tetto:g} $ "
                          f"(gastados {SPESA[0]:.3f} $): me detengo")
                    finita = True
                    break
            esito = una(slug, vid, m, meta, modello, tetto)
            if esito is None:
                finita = True
                break
            fatte += bool(esito)
            if not esito:
                falliti[vid] = falliti.get(vid, 0) + 1
        restano = [i for i in (scelti or lista) if not (d / "schede" / f"{i}.json").exists() and falliti.get(i, 0) < 2]
        if not aspetta or not restano:
            break
        quando = prossimo_azzeramento() if finita else datetime.now(timezone.utc) + timedelta(minutes=30)
        print(f"{len(restano)} fichas aún por hacer: vuelvo a empezar a las {quando.astimezone().strftime('%H:%M del %d/%m')}", flush=True)
        # a pasos cortos mirando el reloj: un solo sleep largo se retrasa todo el tiempo en que el ordenador está en reposo (07/11)
        while (resta := (quando - datetime.now(timezone.utc)).total_seconds()) > 0:
            time.sleep(min(300, max(1, resta)))
        ESAURITI.clear()
    if tetto is not None:
        print(f"gasto estimado con el plan de pago: {SPESA[0]:.3f} $ (tope {tetto:g} $)")
    print(f"fichas nuevas: {fatte}; en total {len(list((d / 'schede').glob('*.json'))) if (d / 'schede').exists() else 0}"
          + (f"; saltadas tras 2 errores: {', '.join(i for i, n in falliti.items() if n >= 2)}" if any(n >= 2 for n in falliti.values()) else ""))


if __name__ == "__main__":
    aiuto(__doc__)
    main(sys.argv[1:]) if len(sys.argv) > 1 else sys.exit(__doc__)

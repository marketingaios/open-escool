"""ElevenLabs para la voz de las lecciones: solo la biblioteca estándar de Python, así que funciona también en Windows (no hace falta
el entorno de la voz).

    python strumenti/elevenlabs.py stato                         plan, créditos que quedan, renovación (llamadas gratuitas)
    python strumenti/elevenlabs.py voce <ID> [it|es|en]          cómo es la voz y si se puede usar con tu plan
    python strumenti/elevenlabs.py modelli                       los modelos de voz, con lo que cuestan en créditos

La clave es ELEVENLABS_API_KEY en el .env de Open Escool: Ajustes → Voz de las lecciones (solo desde el ordenador) o
`python strumenti/chiavi.py prepara ELEVENLABS_API_KEY`. Nunca se imprime.

Para saber (06/11/2026, fuentes en docs/lezioni.md):
- plan gratuito: 10.000 créditos al mes; Multilingual v2, v3 y v4 cuestan 1 crédito por carácter, Flash y Turbo 0,5;
- con el plan gratuito las voces de la **biblioteca** de ElevenLabs no se pueden usar desde la API (error 402): funcionan las voces
  de serie y las creadas en tu propia cuenta;
- plan gratuito = uso no comercial; quien publica o comparte debe escribir «elevenlabs.io» en el título.
"""
from __future__ import annotations

import base64
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from comune import tr  # también solo biblioteca estándar (strumenti/ está en sys.path: script, lezione.py, accademia.py)

API = "https://api.elevenlabs.io"
NOME_CHIAVE = "ELEVENLABS_API_KEY"
MODELLO_BASE = "eleven_multilingual_v2"
IMPOSTAZIONI_BASE = {"stability": 0.5, "similarity_boost": 0.75, "style": 0.0, "use_speaker_boost": True, "speed": 1.0}
# voces del usuario o de ElevenLabs: funcionan también con el plan gratuito. «professional» = de la biblioteca (o clonación profesional)
CATEGORIE_PROPRIE = {"premade", "generated", "cloned"}
FORMATO = "mp3_44100_128"  # el mejor que funciona con todos los planes (192 kbps desde Creator, PCM 44,1 kHz desde Pro)


class Errore(Exception):
    def __init__(self, codice, messaggio, dettaglio=""):
        super().__init__(messaggio)
        self.codice, self.messaggio, self.dettaglio = codice, messaggio, dettaglio


def chiave(obbligatoria=False):
    from comune import chiave as c

    return c(NOME_CHIAVE, obbligatoria=obbligatoria)


def chiama(k, metodo, percorso, corpo=None, timeout=60, tentativi=3):
    """Una llamada a la API. Errores en español; 429 y 5xx se reintentan con una espera creciente."""
    dati = json.dumps(corpo).encode("utf-8") if corpo is not None else None
    for i in range(tentativi):
        r = urllib.request.Request(API + percorso, data=dati, method=metodo,
                                   headers={"xi-api-key": k, "Content-Type": "application/json", "Accept": "application/json",
                                            "User-Agent": "OpenEscool/0.3"})
        try:
            with urllib.request.urlopen(r, timeout=timeout) as risp:
                return json.load(risp)
        except urllib.error.HTTPError as e:
            testo = e.read().decode("utf-8", errors="replace")
            try:
                det = json.loads(testo).get("detail")
            except json.JSONDecodeError:
                det = testo[:200]
            stato = det.get("status") if isinstance(det, dict) else ""
            msg = det.get("message") if isinstance(det, dict) else str(det)
            if (e.code == 429 or e.code >= 500) and i < tentativi - 1:
                time.sleep(4 * (i + 1))
                continue
            if e.code == 401:
                raise Errore(401, tr("la chiave di ElevenLabs non funziona o non ha il permesso per questa operazione",
                                     "la clave de ElevenLabs no funciona o no tiene permiso para esta operación",
                                     "the ElevenLabs key does not work or lacks permission for this operation"), msg) from None
            raise Errore(e.code, msg or tr(f"errore {e.code}", f"error {e.code}", f"error {e.code}"), stato) from None
        except (urllib.error.URLError, OSError) as e:
            if i < tentativi - 1:
                time.sleep(3)
                continue
            tipo = type(e).__name__
            raise Errore(0, tr(f"non riesco a raggiungere ElevenLabs ({tipo}): controlla la rete",
                               f"no consigo conectar con ElevenLabs ({tipo}): revisa la red",
                               f"cannot reach ElevenLabs ({tipo}): check the network")) from None


def abbonamento(k):
    s = chiama(k, "GET", "/v1/user/subscription")
    usati, limite = int(s.get("character_count") or 0), int(s.get("character_limit") or 0)
    rinnovo = s.get("next_character_count_reset_unix")
    return {"piano": s.get("tier") or "?", "gratuito": (s.get("tier") or "").lower() == "free", "usati": usati, "limite": limite,
            "rimasti": max(0, limite - usati),
            "rinnovo": datetime.fromtimestamp(rinnovo, timezone.utc).date().isoformat() if rinnovo else None}


def modelli(k):
    """Los modelos que hacen voz a partir de texto, con el coste en créditos por carácter y los idiomas."""
    out = []
    for m in chiama(k, "GET", "/v1/models"):
        if not m.get("can_do_text_to_speech"):
            continue
        out.append({"id": m["model_id"], "nome": m.get("name") or m["model_id"],
                    "crediti_per_carattere": float((m.get("model_rates") or {}).get("character_cost_multiplier") or 1.0),
                    "lingue": sorted({(x.get("language_id") or "")[:2] for x in m.get("languages") or [] if x.get("language_id")}),
                    "max_caratteri": m.get("maximum_text_length_per_request")})
    return out


def voce(k, voice_id):
    """La voz a partir del ID: de la cuenta; si no está, de la biblioteca. None si no existe."""
    if not voice_id or not voice_id.replace("_", "").isalnum() or len(voice_id) > 40:
        return None
    try:
        v = chiama(k, "GET", f"/v1/voices/{voice_id}")
        sh = v.get("sharing") or {}
        libreria = v.get("category") == "professional" and not v.get("is_owner") or sh.get("status") == "copied"
        lingue = sorted({(x.get("language") or "")[:2] for x in v.get("verified_languages") or [] if x.get("language")})
        return {"id": voice_id, "nome": v.get("name") or voice_id, "categoria": v.get("category"), "nel_conto": True,
                "libreria": bool(libreria), "anteprima": v.get("preview_url"), "lingue": lingue,
                "moltiplicatore": float(sh.get("rate") or 1.0), "etichette": v.get("labels") or {}}
    except Errore as e:
        if e.codice not in (400, 404):
            raise
    r = chiama(k, "GET", "/v1/shared-voices?" + urllib.parse.urlencode({"page_size": 5, "search": voice_id}))
    v = next((x for x in r.get("voices", []) if x.get("voice_id") == voice_id), None)
    if not v:
        return None
    lingue = sorted({(x.get("language") or "")[:2] for x in v.get("verified_languages") or [] if x.get("language")} | ({v["language"][:2]} if v.get("language") else set()))
    return {"id": voice_id, "nome": v.get("name") or voice_id, "categoria": "libreria", "nel_conto": False, "libreria": True,
            "anteprima": v.get("preview_url"), "lingue": lingue, "moltiplicatore": float(v.get("rate") or 1.0),
            "solo_a_pagamento": v.get("free_users_allowed") is False, "etichette": {}}


def verifica(k, voice_id, lingua, modello, caratteri):
    """Todo lo que se puede saber sin gastar créditos. Los `problemi` detienen la lección (se pregunta al usuario), los `avvisi` no."""
    problemi, avvisi, ab, v, costo = [], [], None, None, 1.0
    if not k:
        manca = tr("manca la chiave di ElevenLabs (Impostazioni → Voce delle lezioni, dal computer)",
                   "falta la clave de ElevenLabs (Ajustes → Voz de las lecciones, desde el ordenador)",
                   "the ElevenLabs key is missing (Settings → Lesson voice, from the computer)")
        return {"ok": False, "problemi": [manca], "avvisi": []}
    try:
        ab = abbonamento(k)
    except Errore as e:
        if e.codice == 401 and "permission" not in (e.dettaglio or "").lower():
            return {"ok": False, "problemi": [e.messaggio], "avvisi": []}
        avvisi.append(tr("non riesco a leggere il piano e i crediti (la chiave non ha il permesso «User: read»?): "
                         "controllali su elevenlabs.io",
                         "no consigo leer el plan y los créditos (¿la clave no tiene el permiso «User: read»?): "
                         "revísalos en elevenlabs.io",
                         "cannot read the plan and credits (does the key lack the «User: read» permission?): "
                         "check them on elevenlabs.io"))
    try:
        mm = {m["id"]: m for m in modelli(k)}
        if modello not in mm:
            elenco = ", ".join(mm)
            problemi.append(tr(f"il modello «{modello}» non c'è (modelli: {elenco})",
                               f"el modelo «{modello}» no existe (modelos: {elenco})",
                               f"the model «{modello}» does not exist (models: {elenco})"))
        else:
            costo = mm[modello]["crediti_per_carattere"]
            if mm[modello]["lingue"] and lingua not in mm[modello]["lingue"]:
                nome = mm[modello]["nome"]
                problemi.append(tr(f"il modello {nome} non parla «{lingua}»", f"el modelo {nome} no habla «{lingua}»",
                                   f"the model {nome} does not speak «{lingua}»"))
    except Errore as e:
        avvisi.append(tr(f"non riesco a leggere i modelli: {e.messaggio}", f"no consigo leer los modelos: {e.messaggio}",
                         f"cannot read the models: {e.messaggio}"))
    v = voce(k, voice_id)
    if not v:
        problemi.append(tr(f"la voce con ID «{voice_id}» non esiste (in elevenlabs.io apri Voices, scegli la voce e copia "
                           "il suo ID)",
                           f"la voz con ID «{voice_id}» no existe (en elevenlabs.io abre Voices, elige la voz y copia su ID)",
                           f"the voice with ID «{voice_id}» does not exist (on elevenlabs.io open Voices, pick the voice "
                           "and copy its ID)"))
    else:
        nome = v["nome"]
        if v["libreria"] and ab and ab["gratuito"]:
            problemi.append(tr(f"«{nome}» è una voce della libreria di ElevenLabs: col piano gratuito non si può usare "
                               "dall'API. Scegli una voce di base o creata da te, oppure la voce gratuita di Open Escool",
                               f"«{nome}» es una voz de la biblioteca de ElevenLabs: con el plan gratuito no se puede usar "
                               "desde la API. Elige una voz de serie o creada por ti, o la voz gratuita de Open Escool",
                               f"«{nome}» is an ElevenLabs library voice: on the free plan it cannot be used from the API. "
                               "Choose a default voice or one you created, or the free Open Escool voice"))
        elif v["libreria"] and not v["nel_conto"]:
            problemi.append(tr(f"«{nome}» è nella libreria ma non fra le tue voci: aggiungila alle tue voci su elevenlabs.io "
                               "(Voice Library) e riprova",
                               f"«{nome}» está en la biblioteca pero no entre tus voces: añádela a tus voces en elevenlabs.io "
                               "(Voice Library) y vuelve a probar",
                               f"«{nome}» is in the library but not among your voices: add it to your voices on elevenlabs.io "
                               "(Voice Library) and try again"))
        if v["lingue"] and lingua not in v["lingue"]:
            verificate = ", ".join(v["lingue"])
            avvisi.append(tr(f"«{nome}» è verificata in {verificate}, non in «{lingua}»: può avere un accento straniero",
                             f"«{nome}» está verificada en {verificate}, no en «{lingua}»: puede tener acento extranjero",
                             f"«{nome}» is verified in {verificate}, not in «{lingua}»: it may have a foreign accent"))
        costo *= v["moltiplicatore"]
    servono = round(caratteri * costo)
    if ab and servono > ab["rimasti"]:
        problemi.append(tr(f"servono circa {servono} crediti e ne restano {ab['rimasti']} (si rinnovano il {ab['rinnovo']})",
                           f"hacen falta unos {servono} créditos y quedan {ab['rimasti']} (se renuevan el {ab['rinnovo']})",
                           f"about {servono} credits are needed and {ab['rimasti']} are left (renewed on {ab['rinnovo']})"))
    if ab and ab["gratuito"]:
        avvisi.append(tr("piano gratuito: uso non commerciale; se pubblichi o condividi la lezione scrivi «elevenlabs.io» "
                         "nel titolo",
                         "plan gratuito: uso no comercial; si publicas o compartes la lección, escribe «elevenlabs.io» en el título",
                         "free plan: non-commercial use; if you publish or share the lesson, put “elevenlabs.io” in the title"))
    return {"ok": not problemi, "problemi": problemi, "avvisi": avvisi, "abbonamento": ab, "voce": v, "modello": modello,
            "caratteri": caratteri, "servono": servono}


def parla(k, voice_id, testo, modello, impostazioni=None, seme=None, prima="", dopo="", lingua=None):
    """Voz y tiempos de cada palabra (a partir de los tiempos de los caracteres que da la API). Devuelve (mp3, parole, richiesta)."""
    corpo = {"text": testo, "model_id": modello, "voice_settings": {**IMPOSTAZIONI_BASE, **(impostazioni or {})}}
    extra = {}
    if seme is not None:
        extra["seed"] = int(seme) % 4294967295
    if prima:
        extra["previous_text"] = prima[-400:]
    if dopo:
        extra["next_text"] = dopo[:400]
    if lingua and modello != MODELLO_BASE:
        extra["language_code"] = lingua
    percorso = f"/v1/text-to-speech/{voice_id}/with-timestamps?output_format={FORMATO}"
    try:
        r = chiama(k, "POST", percorso, {**corpo, **extra}, timeout=180)
    except Errore as e:
        if e.codice not in (400, 422) or not extra:
            raise
        r = chiama(k, "POST", percorso, corpo, timeout=180)  # un modelo que no acepta semilla, contexto o idioma: sin ellos
    al = r.get("alignment") or r.get("normalized_alignment") or {}
    return base64.b64decode(r["audio_base64"]), parole_da_caratteri(al), r.get("request_id")


def parole_da_caratteri(al):
    car, ini, fin = al.get("characters") or [], al.get("character_start_times_seconds") or [], al.get("character_end_times_seconds") or []
    parole, cur = [], None
    for c, a, b in zip(car, ini, fin):
        if c.isspace():
            if cur:
                parole.append(cur)
            cur = None
        elif cur is None:
            cur = {"w": c, "inizio": round(a, 3), "fine": round(b, 3)}
        else:
            cur["w"] += c
            cur["fine"] = round(b, 3)
    if cur:
        parole.append(cur)
    return parole


def prova_chiave(k):
    """Para chiavi.py y los Ajustes: ¿funciona la clave? No gasta créditos."""
    try:
        n = len(modelli(k))
    except Errore as e:
        return False, e.messaggio
    try:
        ab = abbonamento(k)
        return True, tr(f"chiave ElevenLabs valida: piano {ab['piano']}, {ab['rimasti']} crediti rimasti fino al {ab['rinnovo']}",
                        f"clave de ElevenLabs válida: plan {ab['piano']}, quedan {ab['rimasti']} créditos hasta el {ab['rinnovo']}",
                        f"ElevenLabs key valid: plan {ab['piano']}, {ab['rimasti']} credits left until {ab['rinnovo']}")
    except Errore:
        return True, tr(f"chiave ElevenLabs valida ({n} modelli); non vedo i crediti (manca il permesso «User: read»)",
                        f"clave de ElevenLabs válida ({n} modelos); no veo los créditos (falta el permiso «User: read»)",
                        f"ElevenLabs key valid ({n} models); credits not visible (the «User: read» permission is missing)")


def main():
    a = sys.argv[1:]
    k = chiave(obbligatoria=True)
    try:
        if a[:1] == ["stato"]:
            print(json.dumps(abbonamento(k), ensure_ascii=False, indent=1))
        elif a[:1] == ["modelli"]:
            for m in modelli(k):
                mid, cc, nl, nome = m["id"], m["crediti_per_carattere"], len(m["lingue"]), m["nome"]
                print(tr(f"{mid:<28} {cc:>4} crediti/carattere · {nl} lingue · {nome}",
                         f"{mid:<28} {cc:>4} créditos/carácter · {nl} idiomas · {nome}",
                         f"{mid:<28} {cc:>4} credits/character · {nl} languages · {nome}"))
        elif a[:1] == ["voce"] and len(a) >= 2:
            print(json.dumps(verifica(k, a[1], a[2] if len(a) > 2 else "it", MODELLO_BASE, 0), ensure_ascii=False, indent=1))
        else:
            sys.exit(__doc__)
    except Errore as e:
        sys.exit(f"ElevenLabs: {e.messaggio}")


if __name__ == "__main__":
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from comune import aiuto

    aiuto(__doc__)  # antes de pedir la clave
    main()

"""Open Escool: plataforma local de rutas de aprendizaje (servidor solo con la biblioteca estándar).

  python accademia.py                 arranca en http://127.0.0.1:<puerto> (config.json, por defecto 8765)
  python accademia.py --apri          arranca y abre el navegador
  python accademia.py --diagnosi      imprime el diagnóstico en JSON y sale

Desde el teléfono (opcional, Ajustes → Teléfono): un segundo servidor en la dirección privada del ordenador en la red de casa,
nunca en 0.0.0.0 ni en direcciones públicas; se entra con un código de 6 cifras (luego una cookie), la terminal no se abre desde ahí.

Todo se queda en el ordenador: rutas en percorsi/, notas, progreso y chats en utente/. Las preguntas van al asistente
elegido (Claude Code o Codex, con la suscripción de quien lo usa); a Gemini nunca le llega nada desde aquí.
"""
import hashlib
import hmac
import io
import ipaddress
import json
import os
import platform
import re
import secrets
import shutil
import socket
import subprocess
import sys
import threading
import time
import uuid
import webbrowser
import zipfile
from datetime import date, datetime
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

QUI = Path(__file__).resolve().parent
WEB = QUI / "web"
PERCORSI = QUI / "percorsi"
UTENTE = QUI / "utente"
CONFIG = QUI / "config.json"
CONFIG_ESEMPIO = QUI / "config.esempio.json"
VERSIONE = "0.4.0"
FILE_RETE = UTENTE / "rete.json"  # código para el teléfono y huellas de las cookies entregadas (nunca las cookies reales)
RETE = {"server": None, "ip": None, "porta": None, "falliti": {}, "falliti_ora": []}
WIN = os.name == "nt"
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,60}$")
VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{6,20}$")
TIPI = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8",
        ".json": "application/json; charset=utf-8", ".webmanifest": "application/manifest+json",
        ".svg": "image/svg+xml", ".png": "image/png", ".ico": "image/x-icon", ".md": "text/markdown; charset=utf-8",
        ".mp4": "video/mp4", ".jpg": "image/jpeg", ".webp": "image/webp"}
LEZIONE_FILE = re.compile(r"^t\d{1,2}\.(mp4|jpg|json)$")
blocco = threading.Lock()


# ---------- archivos JSON en UTF-8 (en Windows cp1252 lo rompe todo: siempre encoding explícito) ----------
def leggi_json(p, base=None):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return base


def scrivi_json(p, dati):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(dati, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, p)


def unisci(a, b):
    """b encima de a, también dentro de los diccionarios anidados (los ajustes de las lecciones tienen dos niveles)."""
    out = dict(a)
    for k, v in (b or {}).items():
        out[k] = unisci(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def config():
    return unisci(leggi_json(CONFIG_ESEMPIO, {}), leggi_json(CONFIG, {}))


def el():
    """strumenti/elevenlabs.py (solo biblioteca estándar): la voz ElevenLabs de las lecciones."""
    if str(QUI / "strumenti") not in sys.path:
        sys.path.insert(0, str(QUI / "strumenti"))
    import elevenlabs

    return elevenlabs


VOCI_GRATUITE = [("chatterbox", "Chatterbox", "mac"), ("supertonic", "Supertonic 3", "ovunque"), ("kokoro-onnx", "Kokoro", "ovunque")]


def voci_gratuite():
    """Las voces gratuitas y cuáles están instaladas en el entorno de la voz (strumenti/.voce, lo crea la instalación)."""
    el()
    import comune

    v = (config().get("lezioni") or {}).get("voce") or {}
    installati = comune.moduli_voce(comune.python_voce(v.get("python") or ""))
    return {"installate": sorted(installati - {"whisper"}), "whisper": "whisper" in installati, "mac_apple": comune.mac_apple(),
            "auto": {l: comune.modello_gratuito("auto", installati, l) for l in ("it", "es", "en")}, "scelta": v.get("modello") or "auto",
            "voci": [{"id": i, "nome": n, "dove": d, "installata": i in installati} for i, n, d in VOCI_GRATUITE]}


VOCE_ID = re.compile(r"^[A-Za-z0-9]{10,40}$")


def lezioni_pulite(d):
    """Solo los campos de las lecciones que se pueden cambiar desde Ajustes, ya validados."""
    out = {}
    if d.get("motore") in ("gratuita", "elevenlabs"):
        out["motore"] = d["motore"]
    g = d.get("voce") or {}
    if isinstance(g, dict) and g.get("modello") in ("auto", *(i for i, _, _ in VOCI_GRATUITE)):
        out["voce"] = {"modello": g["modello"]}
    e = d.get("elevenlabs") or {}
    if isinstance(e, dict):
        ee = {}
        if "voce" in e:
            ee["voce"] = e["voce"].strip() if VOCE_ID.match((e["voce"] or "").strip()) else ""
        if isinstance(e.get("voci"), dict):
            ee["voci"] = {l: (v or "").strip() if VOCE_ID.match((v or "").strip()) else "" for l, v in e["voci"].items() if l in ("it", "es", "en")}
        if re.match(r"^[a-z0-9_]{3,40}$", e.get("modello") or ""):
            ee["modello"] = e["modello"]
        for k, (lo, hi) in {"stabilita": (0, 1), "somiglianza": (0, 1), "stile": (0, 1), "velocita": (0.7, 1.2)}.items():
            if isinstance(e.get(k), (int, float)):
                ee[k] = min(hi, max(lo, float(e[k])))
        if ee:
            out["elevenlabs"] = ee
    return out


def oggi():
    return date.today().isoformat()


def giorni_da(iso):
    try:
        return (date.today() - date.fromisoformat(iso[:10])).days
    except (TypeError, ValueError):
        return None


# ---------- rutas y datos del usuario ----------
def elenco_percorsi():
    if not PERCORSI.exists():
        return []
    fuori, note = [], tutte_le_note()
    for d in sorted(PERCORSI.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        p = leggi_json(d / "percorso.json")
        if not p:
            continue
        prog = progressi(d.name)
        con_url(d.name, p)
        video_principali = [v for t in p["tappe"] for v in t.get("video", []) if v.get("ruolo") == "principale"]
        fatte = sum(1 for t in p["tappe"] if prog.get("tappe", {}).get(str(t["n"]), {}).get("fatta"))
        stessi = del_gruppo(d.name)
        mappa = stati_tappe(p, prog, [n for n in note if n["percorso"] in stessi])
        prossima = next((m for m in mappa if m["stato"] not in ("fatta", "buco")), None)
        fuori.append({"slug": d.name, "gruppo": p.get("da") or d.name, "ultima": prog.get("ultima"), "categoria": p.get("categoria"),
                      "titoli_tappe": [t["titolo"] for t in p["tappe"]], "schede_mancanti": p.get("schede_mancanti", 0),
                      "titolo": p["titolo"], "sottotitolo": p.get("sottotitolo", ""), "tema": p.get("tema", ""),
                      "copertina": p.get("copertina"), "mappa": mappa, "prossima": prossima, "arrivo": p.get("arrivo", ""),
                      "tappe": len(p["tappe"]), "tappe_fatte": fatte, "durata_min": p.get("durata_min"),
                      "copertine": list(dict.fromkeys(v["copertina"] for v in video_principali))[:4],
                      "stato": p.get("stato", "pronto"), "controllato": p.get("controllato"), "lingua_video": p.get("lingua_video"),
                      "giorni_dal_controllo": giorni_da(p.get("controllato")),
                      "ultimo_accesso": prog.get("ultimo_accesso")})
    fuori.sort(key=lambda x: x.get("ultimo_accesso") or "", reverse=True)
    return fuori


def stati_tappe(p, prog, note):
    """El minimapa de una ruta: para cada etapa fatta · dubbio (dudas abiertas) · iniziata · da_vedere · buco (sin vídeos),
    y «attuale» en la etapa donde se quedó la persona."""
    pos = (prog.get("posizione") or {}).get("tappa")
    fuori = []
    for t in p["tappe"]:
        ids = [v["id"] for v in t.get("video", [])]
        dubbi = sum(1 for n in note if n.get("tappa") == t["n"] and n["tipo"] in ("dubbio", "domanda") and not n.get("risolto")
                    and n.get("ambito") != "percorso")
        if not ids:
            stato = "buco"
        elif prog.get("tappe", {}).get(str(t["n"]), {}).get("fatta"):
            stato = "fatta"
        elif dubbi:
            stato = "dubbio"
        elif any(prog.get("video", {}).get(i, {}).get("secondi") or prog.get("video", {}).get(i, {}).get("visto") for i in ids):
            stato = "iniziata"
        else:
            stato = "da_vedere"
        fuori.append({"n": t["n"], "titolo": t["titolo"], "stato": stato, "dubbi": dubbi, "attuale": t["n"] == pos,
                      "minuti": t.get("minuti_video")})
    return fuori


def con_url(slug, p):
    """Las lecciones generadas están dentro de la ruta (lezioni/t5.mp4): la página las pide a /percorsi/<nombre>/lezioni/...
    A los vídeos de YouTube les añade título, canal, fecha y duración desde lavoro/youtube/metadati.json (ver dati_youtube)."""
    for t in p.get("tappe", []):
        for v in t.get("video", []):
            if v.get("tipo") == "lezione":
                v["src"] = f"/percorsi/{slug}/{v['file']}"
                if v.get("copertina") and not v["copertina"].startswith(("/", "http")):
                    v["copertina"] = f"/percorsi/{slug}/{v['copertina']}"
    dati_youtube(slug, p)
    return p


def leggi_percorso(slug):
    return con_url(slug, leggi_json(PERCORSI / slug / "percorso.json", {}))


def metadati():
    el()  # añade strumenti/ al sys.path de Python
    import metadati as m

    return m


RINNOVO = {"attivo": False}  # la renovación en segundo plano solo arranca desde el servidor (main), no desde quien importa este archivo


def dati_youtube(slug, p):
    """Las reglas para desarrolladores de YouTube (III.E.4) permiten guardar los datos de la API 30 días como máximo: por eso
    percorso.json solo tiene el ID y nuestros textos; título, canal, fecha y duración llegan aquí desde
    lavoro/youtube/metadati.json (solo los válidos). Si faltan o tienen 25 días o más y hay clave de YouTube, el servidor los
    renueva en segundo plano, como máximo un intento por hora y por ruta. Sin datos: portada a partir del ID y un título nuestro."""
    md = metadati()
    d = PERCORSI / slug
    dati = md.validi(d)
    if RINNOVO["attivo"] and not dati and slug not in RINNOVO and any(
            v.get("tipo") != "lezione" for t in p.get("tappe", []) for v in t.get("video", [])):
        RINNOVO[slug] = time.time()  # curso recién instalado o importado: la primera renovación enseguida, así se ven los títulos reales
        rinnova_youtube(slug, timeout=5)
        dati = md.validi(d)
    ids = []
    for t in p.get("tappe", []):
        for v in t.get("video", []):
            md.completa(v, dati)
            if v.get("tipo") != "lezione" and v.get("id"):
                ids.append(v["id"])
    if RINNOVO["attivo"] and ids and time.time() - RINNOVO.get(slug, 0) > 3600 and md.da_rinnovare(d, ids):
        RINNOVO[slug] = time.time()
        threading.Thread(target=rinnova_youtube, args=(slug,), daemon=True).start()


def rinnova_youtube(slug, timeout=20):
    md = metadati()
    import comune

    k = comune.chiave("YOUTUBE_API_KEY", obbligatoria=False)
    if not k:
        return
    try:
        r, sp = md.rinnova(PERCORSI / slug, k, timeout=timeout)
        md.pulisci(PERCORSI / slug)
        if "--silenzioso" not in sys.argv and sys.stderr:
            print(f"datos de YouTube renovados: {slug}, {r} vídeos" + (f", {sp} ya no disponibles" if sp else ""), file=sys.stderr)
    except (OSError, ValueError) as e:  # red, cuota o clave: se reintenta en una hora; mientras, se quedan los datos válidos
        if "--silenzioso" not in sys.argv and sys.stderr:
            print(f"datos de YouTube no renovados ({slug}): {e.__class__.__name__}", file=sys.stderr)


def avvisi_voce(slug):
    """Lecciones con una voz que tiene reglas para quien las comparte (ElevenLabs gratuito: uso no comercial y «elevenlabs.io»
    en el título; Supertonic 3: decir que se ha generado automáticamente). La página lo avisa antes de exportar; el zip lo
    lleva en AVVISO_VOCE.txt."""
    p = leggi_json(PERCORSI / slug / "percorso.json", {})
    return [{"tappa": t["n"], "voce": v.get("voce", ""), "avviso": v["avviso_voce"]}
            for t in p.get("tappe", []) for v in t.get("video", []) if v.get("tipo") == "lezione" and v.get("avviso_voce")]


def lezione_di(slug, video_id):
    """El texto exacto de una lección generada, con los tiempos (lezioni/t<N>.json): para el chat vale más que una ficha."""
    m = re.fullmatch(r"lezione-t(\d{1,2})", video_id or "")
    return leggi_json(PERCORSI / slug / "lezioni" / f"t{m.group(1)}.json", {}) if m else {}


def percorso(slug):
    p = leggi_json(PERCORSI / slug / "percorso.json")
    if not p:
        return None
    con_url(slug, p)
    soglia = config().get("aggiornamento", {}).get("avviso_dopo_giorni", 30)
    g = giorni_da(p.get("controllato"))
    p["avviso_aggiornamento"] = g is not None and g >= soglia
    p["giorni_dal_controllo"] = g
    for t in p["tappe"]:
        rd = t.get("ricontrolla_dopo")
        t["da_ricontrollare"] = bool(rd and oggi() >= rd)
    stessi = del_gruppo(slug)
    note = [n for n in tutte_le_note() if n["percorso"] in stessi]
    for t in p["tappe"]:
        dubbi = [n for n in note if n.get("tappa") == t["n"] and n["tipo"] in ("dubbio", "domanda") and not n.get("risolto")
                 and n.get("ambito") != "percorso"]
        t["dubbi_aperti"] = len(dubbi)
        t["segnale_buco"] = len(dubbi) >= config().get("buco", {}).get("dubbi_per_segnale", 2)
    p["progressi"] = progressi(slug)
    p["note"] = note
    versioni = []
    for v in sorted(stessi, key=lambda x: (x != gruppo(slug), x)):
        q = leggi_json(PERCORSI / v / "percorso.json", {})
        versioni.append({"slug": v, "lingua_video": q.get("lingua_video"), "stato": q.get("stato", "pronto"), "schede_mancanti": q.get("schede_mancanti", 0)})
    p["versioni"] = versioni  # los idiomas de los vídeos de la misma ruta (selector en la página de la ruta)
    return p


def gruppo(slug):
    """El nombre de partida: chatgpt-ads-es y chatgpt-ads-en están en el grupo chatgpt-ads (mismo mapa, vídeos en otros idiomas)."""
    return leggi_json(PERCORSI / slug / "percorso.json", {}).get("da") or slug


def del_gruppo(slug):
    """Todas las versiones de la misma ruta: comparten etapas hechas, notas y dudas (las etapas son las mismas)."""
    g = gruppo(slug)
    if not PERCORSI.exists():
        return {slug}
    return {g} | {d.name for d in PERCORSI.iterdir() if d.is_dir() and leggi_json(d / "percorso.json", {}).get("da") == g}


def file_progressi(slug):
    return UTENTE / "progressi" / f"{gruppo(slug)}.json"


def unisci_progressi_vecchi():
    """Antes cada idioma tenía su archivo de progreso: al arrancar se unen en el del grupo y el viejo se borra."""
    cartella = UTENTE / "progressi"
    for f in sorted(cartella.glob("*.json")) if cartella.exists() else []:
        slug = f.stem
        g = gruppo(slug) if (PERCORSI / slug / "percorso.json").exists() else slug
        if g == slug:
            continue
        vecchio, dest = leggi_json(f, {}), cartella / f"{g}.json"
        pr = leggi_json(dest, {"video": {}, "tappe": {}})
        for vid, v in (vecchio.get("video") or {}).items():
            cur = pr.setdefault("video", {}).setdefault(vid, {})
            cur["secondi"] = max(cur.get("secondi", 0), v.get("secondi", 0))
            cur.setdefault("ultimo", v.get("ultimo", 0))
            if v.get("visto"):
                cur["visto"] = True
        for n, t in (vecchio.get("tappe") or {}).items():
            if t.get("fatta"):
                pr.setdefault("tappe", {}).setdefault(n, {})["fatta"] = True
        pos = pr.setdefault("posizioni", {})
        if "posizione" in pr:
            pos.setdefault(g, pr.pop("posizione"))
        if vecchio.get("posizione"):
            pos.setdefault(slug, vecchio["posizione"])
        if (vecchio.get("ultimo_accesso") or "") > (pr.get("ultimo_accesso") or ""):
            pr["ultimo_accesso"], pr["ultima"] = vecchio["ultimo_accesso"], slug
        scrivi_json(dest, pr)
        f.unlink()


def progressi(slug):
    """Un archivo por grupo: etapas hechas en común, vídeos por id (cambian de un idioma a otro), posición por idioma."""
    pr = leggi_json(file_progressi(slug), {"video": {}, "tappe": {}})
    pos = (pr.get("posizioni") or {}).get(slug)
    if pos is None and slug == gruppo(slug):
        pos = pr.get("posizione")  # formato antiguo, un solo idioma
    return {**pr, "posizione": pos}


def tutte_le_note():
    return leggi_json(UTENTE / "note.json", [])


# ---------- asistente: Claude Code o Codex en local ----------
def trova(nome):
    p = shutil.which(nome)
    if p:
        return p
    candidati = [Path.home() / ".local" / "bin" / nome, Path("/opt/homebrew/bin") / nome, Path("/usr/local/bin") / nome]
    if WIN:
        appdata = Path(os.environ.get("APPDATA", ""))
        candidati += [appdata / "npm" / f"{nome}.cmd", Path.home() / ".local" / "bin" / f"{nome}.exe"]
    return next((str(c) for c in candidati if c.exists()), None)


def modello_codex(richiesto):
    """Puede que el modelo del config de Codex no esté permitido con la cuenta de ChatGPT: se elige de la caché de modelos."""
    if richiesto:
        return richiesto
    cache = leggi_json(Path.home() / ".codex" / "models_cache.json", {})
    elenco = [m.get("slug") for m in cache.get("models", []) if m.get("visibility") == "list"]
    return elenco[0] if elenco else None


def comando_assistente(motore, modello, sessione, nuova, cartella):
    if motore == "codex":
        exe = trova("codex")
        if not exe:
            return None
        m = modello_codex(modello)
        # «resume» no acepta -s ni -C: el sandbox de solo lectura se pasa como configuración, la carpeta es la del proceso
        opz = ["--json", "--skip-git-repo-check", "-c", 'sandbox_mode="read-only"', "-c", 'service_tier="default"'] + (["-m", m] if m else [])
        if nuova:
            return [exe, "exec", *opz, "-C", str(cartella), "-"]
        return [exe, "exec", "resume", *opz, sessione, "-"]
    exe = trova("claude")
    if not exe:
        return None
    cmd = [exe, "-p", "--output-format", "stream-json", "--verbose", "--include-partial-messages",
           "--tools", "WebSearch,WebFetch", "--allowedTools", "WebSearch,WebFetch",
           "--setting-sources", "", "--strict-mcp-config"]
    if modello:
        cmd += ["--model", modello]
    cmd += (["--session-id", sessione] if nuova else ["--resume", sessione])
    return cmd


def scheda_video(slug, video_id):
    return leggi_json(PERCORSI / slug / "schede" / f"{video_id}.json", {})


# el prompt queda en italiano: es el que se ha probado
RIMANDI = ("Quando rimandi a un punto preciso di un video del percorso scrivi il rimando così: [[t3 IDVIDEO 10:12]]"
           " (numero della tappa, identificativo del video come scritto qui sotto, minuto): la piattaforma lo trasforma in un"
           " pulsante che apre il video a quel minuto. Mai l'identificativo da solo nel testo.")


def contesto(slug, n_tappa, video_id, secondi):
    """Texto que recibe el asistente con la primera pregunta: perfil, etapa, vídeo, ficha, notas. Nada de esto va a Gemini."""
    cfg = config()
    p = leggi_percorso(slug)
    t = next((t for t in p.get("tappe", []) if t["n"] == n_tappa), {})
    v = next((v for v in t.get("video", []) if v["id"] == video_id), {})
    sch = scheda_video(slug, video_id)
    note = [n for n in tutte_le_note() if n["percorso"] in del_gruppo(slug) and n.get("video") == video_id]
    # el prompt queda en italiano: es el que se ha probado
    lingua = {"it": "italiano", "es": "spagnolo", "en": "inglese"}.get(cfg.get("lingua", "it"), "italiano")
    parti = [
        f"Sei il tutor di {cfg.get('profilo', {}).get('nome') or 'chi impara'} dentro Open Escool, una piattaforma locale di percorsi"
        f" fatti di video gratuiti. Rispondi in {lingua}, breve e concreto (massimo 8 frasi se non ti chiedono di più).",
        "Regole: usa i minuti del video quando servono (es. «al 4:12»); se il video dice una cosa superata o sbagliata rispetto ai"
        " concetti della tappa (presi dalla documentazione ufficiale), dillo; se non lo sai, dillo e proponi dove controllare."
        " Puoi cercare sul web solo per verificare un fatto recente; cita la pagina. Non inventare cosa si vede nel video:"
        " sai solo quello che c'è nella scheda qui sotto.",
        RIMANDI + f" Il video aperto è [[t{t.get('n')} {video_id} …]].",
        f"PROFILO: {json.dumps(cfg.get('profilo', {}), ensure_ascii=False)}",
        f"PERCORSO: {p.get('titolo')} · arrivo: {p.get('arrivo', '')}",
        f"TAPPA {t.get('n')}: {t.get('titolo')} · obiettivo: {t.get('obiettivo')}",
        "CONCETTI DELLA TAPPA (fonte ufficiale):\n" + "\n".join(f"- {c}" for c in t.get("concetti", [])),
        f"VIDEO: «{v.get('titolo')}» di {v.get('canale')} ({v.get('lingua')}, pubblicato {v.get('pubblicato')})"
        f" · spezzone del percorso {v.get('inizio', '0:00')}-{v.get('fine', 'fine')}",
    ]
    lez = lezione_di(slug, video_id)
    if lez:
        parti.append("LEZIONE GENERATA DA OPEN ESCOOL dalle pagine ufficiali (testo esatto della voce, con l'inizio di ogni scena in"
                     " secondi e le fonti; ciò che segue «consiglio» è una deduzione, non una frase ufficiale):\n" + json.dumps(
                         [{k: sc.get(k) for k in ("inizio", "titolo", "testo", "fonti", "consiglio")} for sc in lez.get("scene", [])], ensure_ascii=False))
    elif sch and not sch.get("errore_json"):
        parti.append("SCHEDA DEL VIDEO (fatta guardandolo, con i minuti):\n" + json.dumps(
            {k: sch.get(k) for k in ("riassunto", "capitoli", "affermazioni", "per_chi_impara", "per_italia") if sch.get(k)}, ensure_ascii=False))
    else:
        parti.append("SCHEDA DEL VIDEO: non ancora disponibile; conosci solo titolo e descrizione: "
                     + (v.get("riassunto") or v.get("descrizione", ""))[:600])
    if secondi is not None:
        parti.append(f"La persona ha fermato il video al minuto {secondi // 60}:{secondi % 60:02d}.")
    if note:
        parti.append("SUE NOTE E DUBBI SU QUESTO VIDEO:\n" + "\n".join(f"- [{n.get('minuto', '')}] {n['tipo']}: {n['testo']}" for n in note[-12:]))
    return "\n\n".join(parti)


def contesto_percorso(slug, n_tappa, video_id, secondi):
    """Contexto del chat «Toda la ruta»: todas las etapas, los vídeos elegidos con resumen y puntos, lecturas, notas y progreso."""
    cfg = config()
    p = leggi_percorso(slug)
    prog = progressi(slug)
    # el prompt queda en italiano: es el que se ha probado
    lingua = {"it": "italiano", "es": "spagnolo", "en": "inglese"}.get(cfg.get("lingua", "it"), "italiano")
    nomi = {v["id"]: f"«{v.get('titolo')}» di {v.get('canale')}" for t in p.get("tappe", []) for v in t.get("video", [])}
    parti = [
        f"Sei il tutor di {cfg.get('profilo', {}).get('nome') or 'chi impara'} dentro Open Escool, una piattaforma locale di percorsi"
        f" fatti di video gratuiti. Qui rispondi su TUTTO il percorso, non su un solo video. Rispondi in {lingua}, breve e concreto"
        " (massimo 10 frasi se non ti chiedono di più).",
        "Regole: i concetti delle tappe vengono dalla documentazione ufficiale e valgono più di quello che dicono i video; se un"
        " video dice una cosa superata, dillo. Per «dove si spiega X?» indica tappa, video e minuto. Sai solo quello che c'è qui"
        " sotto (riassunti e punti fatti guardando i video): non inventare cosa si vede. Puoi cercare sul web solo per verificare"
        " un fatto recente; cita la pagina. " + RIMANDI,
        f"PROFILO: {json.dumps(cfg.get('profilo', {}), ensure_ascii=False)}",
        f"PERCORSO: {p.get('titolo')} · arrivo: {p.get('arrivo', '')} · controllato il {p.get('controllato')}",
    ]
    if p.get("avvisi"):
        parti.append("AVVISI PER IL PAESE DI CHI IMPARA:\n" + "\n".join(f"- {a}" for a in p["avvisi"][:10]))
    if p.get("cambi_recenti"):
        parti.append("CAMBI RECENTI:\n" + "\n".join(f"- {c.get('data')}: {c.get('cosa')}" for c in p["cambi_recenti"][:10]))
    for t in p.get("tappe", []):
        fatta = " (fatta)" if prog.get("tappe", {}).get(str(t["n"]), {}).get("fatta") else ""
        righe = [f"TAPPA {t['n']}{fatta}: {t['titolo']} · obiettivo: {t.get('obiettivo', '')}",
                 "Concetti ufficiali: " + " | ".join(t.get("concetti", [])[:14])]
        if t.get("nota_letture"):
            righe.append("Da studiare sulle letture: " + t["nota_letture"])
        if t.get("letture"):
            righe.append("Letture ufficiali: " + " · ".join(f"{l.get('titolo')} {l.get('url')}" for l in t["letture"][:6]))
        if t.get("buco"):
            righe.append("Buco dichiarato: " + t["buco"])
        for v in t.get("video", []):
            visto = " (visto)" if prog.get("video", {}).get(v["id"], {}).get("visto") else ""
            righe.append(f"- video {v['id']} ({v.get('ruolo')}){visto}: «{v.get('titolo')}» di {v.get('canale')} ({v.get('lingua')},"
                         f" {v.get('pubblicato')}), spezzone {v.get('inizio', '0:00')}-{v.get('fine', 'fine')}."
                         f" Riassunto: {(v.get('riassunto') or '')[:500]}")
            for pt in (v.get("punti") or [])[:8]:
                righe.append(f"    {pt.get('minuto')} {pt.get('testo', '')[:200]}")
            for a in (v.get("attenzione") or [])[:4]:
                righe.append(f"    ATTENZIONE {a.get('minuto')}: dice «{a.get('dice')}» → {a.get('verdetto')}: {a.get('perche') or ''}")
        parti.append("\n".join(righe))
    note = [n for n in tutte_le_note() if n["percorso"] in del_gruppo(slug)]
    if note:
        parti.append("SUE NOTE, DUBBI E DOMANDE (le più recenti):\n" + "\n".join(
            f"- tappa {n.get('tappa')}, {nomi.get(n.get('video'), 'sul percorso')} {n.get('minuto') or ''}: {n['tipo']}"
            f"{' (risolto)' if n.get('risolto') else ''}: {n['testo'][:300]}" for n in note[-30:]))
    dove = f"La persona è alla tappa {n_tappa}"
    if video_id:
        dove += f", video {nomi.get(video_id, video_id)} [[t{n_tappa} {video_id} …]]"
    if secondi is not None:
        dove += f", minuto {secondi // 60}:{secondi % 60:02d}"
    parti.append(dove + ".")
    return "\n\n".join(parti)


def salva_chat(cid, voce):
    with blocco:
        f = UTENTE / "chat" / f"{cid}.json"
        c = leggi_json(f, {"id": cid, "messaggi": []})
        c.update({k: v for k, v in voce.items() if k != "messaggio"})
        if voce.get("messaggio"):
            c["messaggi"].append(voce["messaggio"])
        scrivi_json(f, c)
        return c


# ---------- red de casa (teléfono) ----------
def ip_locale():
    """La dirección del ordenador en la red de casa (solo direcciones privadas: nunca públicas). No sale ningún paquete de verdad."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("192.0.2.1", 9))
        ip = s.getsockname()[0]
    except OSError:
        return None
    finally:
        s.close()
    try:
        a = ipaddress.ip_address(ip)
    except ValueError:
        return None
    return ip if a.is_private and not (a.is_loopback or a.is_link_local) else None


def codice_rete(nuovo=False):
    """Código de 6 cifras para entrar desde el teléfono; un código nuevo desconecta todos los teléfonos. Llamar fuera de `blocco`."""
    with blocco:
        r = leggi_json(FILE_RETE, {})
        if nuovo or not r.get("codice"):
            r = {"codice": f"{secrets.randbelow(10 ** 6):06d}", "sessioni": []}
            scrivi_json(FILE_RETE, r)
        return r


def stato_rete():
    r = leggi_json(FILE_RETE, {})
    attiva = bool(RETE["server"])
    return {"attiva": attiva, "voluta": bool(config().get("rete", {}).get("telefono")), "ip": RETE["ip"],
            "url": f"http://{RETE['ip']}:{RETE['porta']}" if attiva else None, "codice": r.get("codice") if attiva else None,
            "telefoni": len(r.get("sessioni", [])), "errore": RETE.get("errore")}


def avvia_rete(porta):
    ip = ip_locale()
    RETE["errore"] = None
    if not ip:
        RETE["errore"] = "no hay red privada: Wi-Fi apagado o red que no es de casa"
        ferma_rete()
        return False
    if RETE["server"] and RETE["ip"] == ip:
        return True
    ferma_rete()
    try:
        srv = ThreadingHTTPServer((ip, porta), GestoreRete)
    except OSError as e:
        RETE["errore"] = f"no puedo abrir {ip}:{porta}: {e}"
        return False
    RETE.update(server=srv, ip=ip, porta=porta)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    codice_rete()
    return True


def ferma_rete():
    srv = RETE["server"]
    RETE.update(server=None, ip=None)
    if srv:
        threading.Thread(target=lambda: (srv.shutdown(), srv.server_close()), daemon=True).start()


def sorveglia_rete(porta):
    """Si el ordenador cambia de red o de dirección (DHCP), el servidor para el teléfono se vuelve a abrir en la nueva dirección."""
    while True:
        time.sleep(60)
        if config().get("rete", {}).get("telefono") and ip_locale() != RETE["ip"]:
            avvia_rete(porta)


PAGINA_ACCESSO = """<!DOCTYPE html><html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><title>Open Escool</title>
<style>body{margin:0;min-height:100vh;display:grid;place-items:center;font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif;
background:#f7f7f8;color:#17171c}@media(prefers-color-scheme:dark){body{background:#0b0c0d;color:#f2f2f0}form{background:#111315!important;
border-color:#26272e!important}input{background:#0b0c0d!important;color:#ececf0;border-color:#26272e!important}}
form{box-sizing:border-box;background:#fff;border:1px solid #e6e6ea;border-radius:16px;padding:28px 24px;width:min(360px,90vw);text-align:center}
.logo{width:44px;height:44px;border-radius:12px;margin:0 auto 12px;background:#AFF320;color:#0a0b0c;
display:grid;place-items:center;font-weight:700;font-size:20px}h1{font-size:19px;margin:0 0 6px}p{margin:0 0 18px;color:#8a8a96;font-size:14px}
input{width:100%;box-sizing:border-box;font-size:28px;letter-spacing:.35em;text-align:center;padding:10px;border:1px solid #e6e6ea;
border-radius:10px;margin-bottom:12px;font-variant-numeric:tabular-nums}input:focus{outline:2px solid #AFF320;outline-offset:1px}button{width:100%;height:44px;border:0;border-radius:10px;
background:#AFF320;color:#0a0b0c;font:inherit;font-weight:600}#e{color:#dc2626;min-height:22px;margin:10px 0 0}</style></head><body>
<form id="f"><div class="logo">O</div><h1>Open Escool</h1><p id="s">Scrivi il codice che vedi sul computer, in Impostazioni → Telefono.</p>
<input id="c" inputmode="numeric" autocomplete="one-time-code" maxlength="6" pattern="[0-9]{6}" required autofocus>
<button>Entra</button><div id="e"></div></form>
<script>
var L=(navigator.language||"it").slice(0,2);
if(L==="es"){document.getElementById("s").textContent="Escribe el código que ves en el ordenador, en Ajustes → Teléfono.";document.querySelector("button").textContent="Entrar";}
if(L==="en"){document.getElementById("s").textContent="Type the code shown on the computer, in Settings → Phone.";document.querySelector("button").textContent="Enter";}
document.getElementById("f").onsubmit=async function(ev){ev.preventDefault();
var r=await fetch("/api/accesso",{method:"POST",headers:{"X-Accademia":"1","Content-Type":"application/json"},body:JSON.stringify({codice:document.getElementById("c").value})});
if(r.ok){location.reload();}else{var j=await r.json().catch(function(){return{}});document.getElementById("e").textContent=j.errore||r.status;}};
</script></body></html>"""


# ---------- servidor ----------
class Gestore(BaseHTTPRequestHandler):
    server_version = "Accademia/" + VERSIONE
    da_rete = False  # peticiones desde este ordenador (127.0.0.1)

    def log_message(self, fmt, *args):
        if "--silenzioso" not in sys.argv and sys.stderr:  # con pythonw (Windows) no hay stderr
            sys.stderr.write("%s %s\n" % (datetime.now().strftime("%H:%M:%S"), fmt % args))

    # seguridad: solo desde este ordenador y solo desde la página de Open Escool (ningún sitio externo que llame al servidor)
    def host_ok(self):
        host = (self.headers.get("Host") or "").split(":")[0]
        return host in ("127.0.0.1", "localhost")

    def origine_ok(self):
        o = self.headers.get("Origin")
        if o and urlparse(o).hostname not in ("127.0.0.1", "localhost"):
            return False
        return self.headers.get("X-Accademia") == "1"

    def intestazioni(self, codice, tipo, lung=None, extra=None):
        self.send_response(codice)
        self.send_header("Content-Type", tipo)
        if lung is not None:
            self.send_header("Content-Length", str(lung))
        # el reproductor de YouTube incrustado necesita el referrer (sin él, error 153)
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-cache")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()

    def file_a_pezzi(self, f):
        """Un archivo servido también por partes (Range): el vídeo se abre en un minuto concreto sin descargarlo entero."""
        if not f.is_file():
            return self.errore(404, "no encontrado")
        tot = f.stat().st_size
        da, a, codice = 0, tot - 1, 200
        m = re.match(r"bytes=(\d*)-(\d*)$", self.headers.get("Range") or "")
        if m and (m.group(1) or m.group(2)):
            if m.group(1):
                da, a = int(m.group(1)), min(int(m.group(2) or tot - 1), tot - 1)
            else:
                da = max(0, tot - int(m.group(2)))
            if da > a:
                self.intestazioni(416, "text/plain", 0, {"Content-Range": f"bytes */{tot}"})
                return
            codice = 206
        extra = {"Accept-Ranges": "bytes"}
        if codice == 206:
            extra["Content-Range"] = f"bytes {da}-{a}/{tot}"
        self.intestazioni(codice, TIPI.get(f.suffix, "application/octet-stream"), a - da + 1, extra)
        try:
            with open(f, "rb") as h:
                h.seek(da)
                resta = a - da + 1
                while resta > 0:
                    b = h.read(min(256 * 1024, resta))
                    if not b:
                        break
                    self.wfile.write(b)
                    resta -= len(b)
        except (BrokenPipeError, ConnectionResetError):
            pass  # el navegador cierra la petición cuando salta a otro punto

    def json(self, dati, codice=200):
        b = json.dumps(dati, ensure_ascii=False).encode("utf-8")
        self.intestazioni(codice, "application/json; charset=utf-8", len(b))
        self.wfile.write(b)

    def errore(self, codice, msg):
        self.json({"errore": msg}, codice)

    def corpo(self, grezzo=False):
        n = int(self.headers.get("Content-Length") or 0)
        if n > 50 * 1024 * 1024:
            raise ValueError("demasiado grande")
        b = self.rfile.read(n) if n else b""
        return b if grezzo else (json.loads(b.decode("utf-8")) if b else {})

    def autorizzato(self):
        return True

    def do_GET(self):
        if not self.host_ok():
            return self.errore(403, "host no permitido")
        u = urlparse(self.path)
        parti = [unquote(x) for x in u.path.strip("/").split("/") if x]
        # el manifest y los iconos se piden sin cookie (los necesita el teléfono para «Añadir a pantalla de inicio»): no dicen nada personal
        pubblico = parti in (["manifest.webmanifest"],) or (len(parti) == 2 and parti[0] == "icone")
        if not self.autorizzato() and not pubblico:
            if parti[:1] == ["api"]:
                return self.errore(401, "hace falta el código")
            b = PAGINA_ACCESSO.encode("utf-8")
            self.intestazioni(200, "text/html; charset=utf-8", len(b))
            return self.wfile.write(b)
        if parti[:1] == ["api"]:
            return self.api_get(parti[1:])
        if len(parti) == 4 and parti[0] == "percorsi" and parti[2] == "lezioni" and SLUG.match(parti[1]) and LEZIONE_FILE.match(parti[3]):
            return self.file_a_pezzi(PERCORSI / parti[1] / "lezioni" / parti[3])
        rel = "/".join(parti) or "index.html"
        f = (WEB / rel).resolve()
        if not f.is_relative_to(WEB.resolve()) or not f.is_file():  # solo archivos dentro de web/ (no carpetas vecinas «web…»)
            f = WEB / "index.html"  # páginas de la app (p. ej. /percorso/x): las gestiona app.js
        b = f.read_bytes()
        self.intestazioni(200, TIPI.get(f.suffix, "application/octet-stream"), len(b),
                          {"Service-Worker-Allowed": "/"} if f.name == "sw.js" else None)
        self.wfile.write(b)

    def do_POST(self):
        if not self.host_ok() or not self.origine_ok():
            return self.errore(403, "petición no permitida")
        parti = [unquote(x) for x in urlparse(self.path).path.strip("/").split("/") if x]
        if self.da_rete and parti == ["api", "accesso"]:
            return self.accesso()
        if not self.autorizzato():
            return self.errore(401, "hace falta el código")
        try:
            return self.api_post(parti[1:] if parti[:1] == ["api"] else [])
        except (ValueError, KeyError, json.JSONDecodeError) as e:
            return self.errore(400, f"petición no válida: {e}")

    # ----- lectura -----
    def api_get(self, p):
        if p == ["config"]:
            return self.json({**config(), "versione": VERSIONE, "motori": {m: bool(trova(m)) for m in ("claude", "codex")},
                              "da_rete": self.da_rete})
        if p == ["rete"]:
            return self.errore(403, "solo desde el ordenador") if self.da_rete else self.json(stato_rete())
        if p == ["percorsi"]:
            return self.json(elenco_percorsi())
        if len(p) == 2 and p[0] == "percorsi" and SLUG.match(p[1]):
            dati = percorso(p[1])
            return self.json(dati) if dati else self.errore(404, "ruta no encontrada")
        if len(p) == 3 and p[0] == "schede" and SLUG.match(p[1]) and VIDEO_ID.match(p[2]):
            return self.json(scheda_video(p[1], p[2]))
        if len(p) == 2 and p[0] == "chat" and re.match(r"^[A-Za-z0-9_-]{1,120}$", p[1]):
            return self.json(leggi_json(UTENTE / "chat" / f"{p[1]}.json", {"id": p[1], "messaggi": []}))
        if len(p) == 2 and p[0] == "esporta" and SLUG.match(p[1]):
            return self.esporta(p[1])
        if len(p) == 3 and p[0] == "esporta" and p[2] == "avvisi" and SLUG.match(p[1]):
            return self.json(avvisi_voce(p[1]))
        if p == ["diagnosi"]:
            return self.errore(403, "solo desde el ordenador") if self.da_rete else self.json(diagnosi())
        if p[:1] == ["elevenlabs"]:
            return self.elevenlabs_get(p[1:], parse_qs(urlparse(self.path).query))
        return self.errore(404, "no encontrado")

    def elevenlabs_get(self, p, q):
        """Estado de la clave y del plan, modelos, verificación de una voz: llamadas de solo lectura, no gastan créditos.
        La clave nunca sale del servidor."""
        e = el()
        k = e.chiave()
        if p == []:
            base = {"chiave": bool(k), "da_rete": self.da_rete, "gratuite": voci_gratuite()}
            if not k:
                return self.json(base)
            try:
                return self.json({**base, "abbonamento": e.abbonamento(k)})
            except e.Errore as x:
                return self.json({**base, "errore": x.messaggio})
        if not k:
            return self.errore(400, "falta la clave de ElevenLabs")
        try:
            if p == ["modelli"]:
                return self.json(e.modelli(k))
            if len(p) == 2 and p[0] == "voce" and VOCE_ID.match(p[1]):
                lingua = (q.get("lingua") or ["it"])[0][:2]
                modello = (q.get("modello") or [e.MODELLO_BASE])[0]
                caratteri = min(100000, max(0, int((q.get("caratteri") or ["0"])[0] or 0)))  # la página pregunta por una lección típica
                return self.json(e.verifica(k, p[1], lingua, modello, caratteri))
        except e.Errore as x:
            return self.errore(502, f"ElevenLabs: {x.messaggio}")
        return self.errore(404, "no encontrado")

    def esporta(self, slug):
        d = PERCORSI / slug
        if not (d / "percorso.json").exists():
            return self.errore(404, "ruta no encontrada")
        # se comparten la ruta, las fichas y el mapa; no las páginas de las fuentes (son de otros: va la lista con URL y fecha)
        # ni los datos en bruto de YouTube ni el registro de llamadas
        fuori = ("lavoro/fonti/", "lavoro/youtube/", "lavoro/chiamate.jsonl")
        elenco = []
        for f in sorted((d / "lavoro" / "fonti").glob("*.md")) if (d / "lavoro" / "fonti").exists() else []:
            testa = f.read_text(encoding="utf-8", errors="replace").splitlines()[:4]
            trovato = re.search(r"https?://\S+", "\n".join(testa))
            elenco.append({"file": f.name, "url": trovato.group(0) if trovato else ""})
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            for f in d.rglob("*"):
                rel = f.relative_to(d).as_posix()
                # de las lecciones se comparten el vídeo (lezioni/) y el guion; voz, fotogramas y render de trabajo no (decenas de MB)
                lavoro_lezione = rel.startswith("lavoro/lezioni/") and not rel.endswith(".json") or re.match(r"lavoro/lezioni/t\d+/[a-z]{2}/", rel)
                if f.is_file() and not any(x.startswith(".") for x in f.relative_to(d).parts) and not rel.startswith(fuori) and not lavoro_lezione:
                    z.write(f, f"{slug}/{rel}")
            if elenco:
                z.writestr(f"{slug}/lavoro/fonti_elenco.json", json.dumps(elenco, ensure_ascii=False, indent=1))
            avvisi = avvisi_voce(slug)
            if avvisi:
                z.writestr(f"{slug}/AVVISO_VOCE.txt", "\n".join(f"Etapa {a['tappa']} · {a['voce']}: {a['avviso']}" for a in avvisi) + "\n")
        b = buf.getvalue()
        self.intestazioni(200, "application/zip", len(b), {"Content-Disposition": f'attachment; filename="{slug}.open-escool.zip"'})
        self.wfile.write(b)

    # ----- escritura -----
    def api_post(self, p):
        if p == ["progresso"]:
            d = self.corpo()
            slug = d["percorso"]
            if not SLUG.match(slug):
                raise ValueError("percorso")
            with blocco:
                f = file_progressi(slug)
                pr = leggi_json(f, {"video": {}, "tappe": {}})
                if d.get("video"):
                    v = pr["video"].setdefault(d["video"], {})
                    v["secondi"] = max(int(d.get("secondi", 0)), v.get("secondi", 0))
                    v["ultimo"] = int(d.get("secondi", 0))
                    if d.get("visto"):
                        v["visto"] = True
                if d.get("tappa") is not None and "fatta" in d:
                    pr["tappe"].setdefault(str(d["tappa"]), {})["fatta"] = bool(d["fatta"])
                if d.get("posizione"):
                    pos = pr.setdefault("posizioni", {})
                    if "posizione" in pr:  # formato antiguo (un solo idioma): pasa a ser la posición de la ruta de partida
                        pos.setdefault(gruppo(slug), pr.pop("posizione"))
                    pos[slug] = d["posizione"]
                pr["ultima"] = slug  # el último idioma usado: la tarjeta de la biblioteca abre este
                pr["ultimo_accesso"] = datetime.now().isoformat(timespec="seconds")
                scrivi_json(f, pr)
            return self.json(progressi(slug))
        if p == ["note"]:
            d = self.corpo()
            with blocco:
                note = tutte_le_note()
                if d.get("elimina"):
                    note = [n for n in note if n["id"] != d["elimina"]]
                elif d.get("id"):
                    for n in note:
                        if n["id"] == d["id"]:
                            n.update({k: d[k] for k in ("testo", "risolto") if k in d})
                else:
                    if d.get("tipo") not in ("nota", "dubbio", "domanda") or not SLUG.match(d.get("percorso", "")):
                        raise ValueError("nota")
                    note.append({"id": uuid.uuid4().hex[:12], "ts": datetime.now().isoformat(timespec="seconds"),
                                 **{k: d.get(k) for k in ("percorso", "tappa", "video", "secondi", "minuto", "testo", "tipo")},
                                 **({"ambito": "percorso"} if d.get("ambito") == "percorso" else {})})
                scrivi_json(UTENTE / "note.json", note)
            stessi = del_gruppo(d["percorso"]) if SLUG.match(d.get("percorso") or "") else None
            return self.json({"ok": True, "note": [n for n in note if stessi is None or n["percorso"] in stessi]})
        if p == ["chiedi"]:
            return self.chiedi(self.corpo())
        if p == ["ripasso"]:
            return self.ripasso(self.corpo())
        if p == ["terminale"]:
            if self.da_rete:
                return self.errore(403, "desde el teléfono la terminal no se abre: lanza el comando en el ordenador")
            return self.terminale(self.corpo())
        if p == ["rete"]:
            if self.da_rete:
                return self.errore(403, "solo desde el ordenador")
            d = self.corpo()
            if "attiva" in d:
                with blocco:
                    c = leggi_json(CONFIG, {})
                    c["rete"] = {**c.get("rete", {}), "telefono": bool(d["attiva"])}
                    scrivi_json(CONFIG, c)
                if d["attiva"]:
                    avvia_rete(int(config().get("porta", 8765)))
                else:
                    ferma_rete()
            if d.get("nuovo_codice"):
                codice_rete(nuovo=True)
            return self.json(stato_rete())
        if p == ["config"]:
            d = self.corpo()
            ammessi = {"tema", "lingua", "disposizione", "assistente", "profilo"}
            with blocco:
                c = leggi_json(CONFIG, {})
                for k in ammessi & d.keys():
                    c[k] = {**c.get(k, {}), **d[k]} if isinstance(d[k], dict) else d[k]
                if isinstance(d.get("lezioni"), dict):
                    c["lezioni"] = unisci(c.get("lezioni") or {}, lezioni_pulite(d["lezioni"]))
                scrivi_json(CONFIG, c)
            return self.json(config())
        if p == ["elevenlabs", "chiave"]:
            # la clave solo se pone desde el ordenador: desde el teléfono pasaría en claro por la red de casa (http)
            if self.da_rete:
                return self.errore(403, "la clave se pone desde el ordenador")
            d, e = self.corpo(), el()
            if d.get("rimuovi"):
                from comune import togli_chiave

                with blocco:
                    togli_chiave(e.NOME_CHIAVE)
                if os.environ.get(e.NOME_CHIAVE):
                    return self.json({"ok": False, "messaggio": "quitada de .env, pero el servidor también la recibe del entorno (variable ELEVENLABS_API_KEY): quítala de ahí y reinicia"})
                return self.json({"ok": True, "messaggio": "clave quitada"})
            v = (d.get("chiave") or "").strip().strip('"').strip("'")
            if not re.fullmatch(r"[A-Za-z0-9_\-\.]{20,200}", v):
                return self.json({"ok": False, "messaggio": "no parece una clave: vuelve a copiarla entera, en una sola línea"})
            ok, msg = e.prova_chiave(v)
            if ok:
                from comune import scrivi_chiave

                with blocco:
                    scrivi_chiave(e.NOME_CHIAVE, v)
            return self.json({"ok": ok, "messaggio": msg})
        if p == ["importa"]:
            return self.importa(self.corpo(grezzo=True))
        return self.errore(404, "no encontrado")

    def flusso(self, evento):
        self.wfile.write(("data: " + json.dumps(evento, ensure_ascii=False) + "\n\n").encode("utf-8"))
        self.wfile.flush()

    def esegui_assistente(self, cmd, prompt, motore, cartella):
        """Lanza Claude Code o Codex y envía el texto por partes (Server-Sent Events). Devuelve (testo, id_sessione, errore)."""
        testo, sessione, err = "", None, None
        env = {**os.environ, "PYTHONIOENCODING": "utf-8", "NO_COLOR": "1"}
        try:
            pr = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(cartella),
                                  env=env, encoding="utf-8", errors="replace", bufsize=1,
                                  creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        except OSError as e:
            return "", None, f"no puedo arrancar {motore}: {e}"
        # stderr se lee aparte: si se llenara su tubería (~64 KB) el asistente se pararía y la chat se quedaría colgada
        errores = []
        lector = threading.Thread(target=lambda: errores.append(pr.stderr.read()), daemon=True)
        lector.start()
        pr.stdin.write(prompt)
        pr.stdin.close()
        for riga in pr.stdout:
            try:
                e = json.loads(riga)
            except json.JSONDecodeError:
                continue
            if motore == "claude":
                if e.get("type") == "stream_event":
                    d = e["event"].get("delta", {})
                    if d.get("type") == "text_delta":
                        testo += d["text"]
                        self.flusso({"t": "pezzo", "testo": d["text"]})
                elif e.get("type") == "system" and e.get("session_id"):
                    sessione = e["session_id"]
                elif e.get("type") == "result":
                    sessione = e.get("session_id", sessione)
                    if e.get("is_error"):
                        err = e.get("result") or "error de Claude Code"
            else:
                if e.get("type") == "thread.started":
                    sessione = e.get("thread_id")
                elif e.get("type") == "item.completed" and e["item"].get("type") == "agent_message":
                    pezzo = ("\n\n" if testo else "") + e["item"]["text"]
                    testo += pezzo
                    self.flusso({"t": "pezzo", "testo": pezzo})
                elif e.get("type") in ("turn.failed", "error"):
                    m = (e.get("error") or {}).get("message") or e.get("message", "")
                    err = m[:400]
        pr.wait(timeout=600)
        lector.join(timeout=5)
        if pr.returncode and not err and not testo:
            err = ("".join(errores) or f"{motore} ha salido con el código {pr.returncode}")[-400:]
        return testo, sessione, err

    def inizia_flusso(self):
        self.intestazioni(200, "text/event-stream; charset=utf-8", None, {"X-Accel-Buffering": "no"})

    def chiedi(self, d):
        slug, n, vid = d["percorso"], int(d["tappa"]), d.get("video") or ""
        percorso_intero = d.get("ambito") == "percorso"
        if not SLUG.match(slug) or (vid and not VIDEO_ID.match(vid)) or (not vid and not percorso_intero):
            raise ValueError("percorso o video")
        cfg = config()
        motore = d.get("motore") or cfg["assistente"]["motore"]
        modello = cfg["assistente"].get("modello_" + motore) or None
        cid = d.get("chat") or f"{slug}-{'percorso' if percorso_intero else vid}-{uuid.uuid4().hex[:6]}"
        if not re.match(r"^[A-Za-z0-9_-]{1,120}$", cid):
            raise ValueError("chat")
        chat = leggi_json(UTENTE / "chat" / f"{cid}.json", {})
        nuova = not chat.get("sessione") or chat.get("motore") != motore
        sessione = str(uuid.uuid4()) if (nuova and motore == "claude") else chat.get("sessione")
        secondi = d.get("secondi")
        domanda = d["domanda"].strip()[:4000]
        # el prompt queda en italiano: es el que se ha probado
        if percorso_intero:
            dove = f"(Ora sono alla tappa {n}" + (f", video {vid}" if vid else "") + (f", minuto {secondi // 60}:{secondi % 60:02d}" if secondi is not None else "") + ") "
            prompt = (contesto_percorso(slug, n, vid, secondi) + "\n\nDOMANDA: " + domanda) if nuova else dove + domanda
        else:
            prompt = (contesto(slug, n, vid, secondi) + "\n\nDOMANDA: " + domanda) if nuova else (
                (f"(Video al minuto {secondi // 60}:{secondi % 60:02d}) " if secondi is not None else "") + domanda)
        cmd = comando_assistente(motore, modello, sessione, nuova, PERCORSI / slug)
        if not cmd:
            return self.errore(424, f"{motore} no está instalado: abre los ajustes o instálalo")
        self.inizia_flusso()
        self.flusso({"t": "inizio", "chat": cid, "motore": motore})
        salva_chat(cid, {"percorso": slug, "tappa": n, "video": vid, "motore": motore, "ambito": "percorso" if percorso_intero else "video",
                         "messaggio": {"ruolo": "utente", "testo": domanda, "secondi": secondi, "ts": datetime.now().isoformat(timespec="seconds")}})
        testo, s, err = self.esegui_assistente(cmd, prompt, motore, PERCORSI / slug)
        salva_chat(cid, {"sessione": s or sessione, "motore": motore,
                         "messaggio": {"ruolo": "assistente", "testo": testo, "errore": err, "ts": datetime.now().isoformat(timespec="seconds")}})
        self.flusso({"t": "fine", "chat": cid, "errore": err})

    def ripasso(self, d):
        slug = d["percorso"]
        if not SLUG.match(slug):
            raise ValueError("percorso")
        p = leggi_percorso(slug)
        note = [x for x in tutte_le_note() if x["percorso"] in del_gruppo(slug) and x["tipo"] in ("dubbio", "domanda")]
        if not note:
            return self.errore(409, "todavía no hay dudas ni preguntas en esta ruta")
        cfg = config()
        motore = cfg["assistente"]["motore"]
        # el prompt queda en italiano: es el que se ha probado
        titoli = {t["n"]: t["titolo"] for t in p["tappe"]}
        nomi = {v["id"]: f"«{v.get('titolo')}» di {v.get('canale')}" for t in p["tappe"] for v in t.get("video", [])}
        righe = "\n".join(f"- tappa {x.get('tappa')} ({titoli.get(x.get('tappa'), '')}), "
                          + (f"video {nomi.get(x.get('video'), x.get('video'))} al {x.get('minuto') or '?'}:" if x.get("video") else "domanda su tutto il percorso:")
                          + f" {x['tipo']} «{x['testo']}»" + (" [risolto]" if x.get("risolto") else "") for x in note)
        concetti = "\n".join(f"Tappa {t['n']} {t['titolo']}: " + "; ".join(t.get("concetti", [])[:12]) for t in p["tappe"])
        prompt = (f"Prepara un ripasso in markdown, in {cfg.get('lingua', 'it')}, per chi segue il percorso «{p['titolo']}»,"
                  " costruito SOLO sui suoi dubbi e sulle sue domande. Per ogni dubbio (raggruppa quelli simili): 1) la spiegazione"
                  " corretta in 2-4 frasi, basata sui concetti ufficiali qui sotto; 2) una domanda di controllo con la risposta"
                  " nascosta in un <details>; 3) quale tappa, video (con il titolo, mai l'identificativo) e minuto rivedere."
                  " Chiudi con le 3 cose da ricordare."
                  f"\n\nDUBBI E DOMANDE:\n{righe}\n\nCONCETTI UFFICIALI:\n{concetti}")
        cmd = comando_assistente(motore, cfg["assistente"].get("modello_" + motore), str(uuid.uuid4()), True, PERCORSI / slug)
        if not cmd:
            return self.errore(424, f"{motore} no está instalado")
        self.inizia_flusso()
        self.flusso({"t": "inizio", "motore": motore})
        testo, _, err = self.esegui_assistente(cmd, prompt, motore, PERCORSI / slug)
        if testo:
            f = UTENTE / "ripassi" / f"{slug}-{datetime.now():%Y%m%d-%H%M}.md"
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(testo, encoding="utf-8")
        self.flusso({"t": "fine", "errore": err})

    def terminale(self, d):
        """Abre una terminal con Claude Code o Codex ya en la carpeta de la ruta (o de Open Escool) y el contexto listo."""
        cfg = config()
        motore = d.get("motore") or cfg["assistente"]["motore"]
        slug = d.get("percorso")
        if d.get("comando"):  # p. ej. /escool create "tema" (botón «Nueva ruta»)
            if not re.match(r"^/escool\b[^\n\"`$;&|<>]{0,200}$", d["comando"]):
                raise ValueError("comando")
            cartella, iniziale = QUI, d["comando"]
        else:
            if not SLUG.match(slug or "") or not VIDEO_ID.match(d.get("video", "")):
                raise ValueError("percorso o video")
            cartella = PERCORSI / slug
            f = cartella / ".contesto" / f"{d['video']}.md"
            f.parent.mkdir(exist_ok=True)
            f.write_text(contesto(slug, int(d["tappa"]), d["video"], d.get("secondi")), encoding="utf-8")
            # el prompt queda en italiano: es el que se ha probado
            iniziale = f"Leggi .contesto/{d['video']}.md: è il contesto del video che sto guardando. Dimmi in una riga che sei pronto e aspetta la mia domanda."
        exe = trova(motore)
        if not exe:
            return self.errore(424, f"{motore} no está instalado")
        if motore == "codex" and iniziale.startswith("/"):
            iniziale = "$" + iniziale[1:]  # en Codex las skills se llaman con $nombre
        if d.get("prova"):  # para las pruebas y el diagnóstico: dice qué abriría, sin abrir nada
            return self.json({"ok": True, "cartella": str(cartella), "argv": [exe, iniziale]})
        ok, msg = apri_terminale(cartella, [exe, iniziale])
        return self.json({"ok": ok, "messaggio": msg}, 200 if ok else 500)

    def importa(self, b):
        try:
            z = zipfile.ZipFile(io.BytesIO(b))
        except zipfile.BadZipFile:
            return self.errore(400, "no es un zip de Open Escool")
        nomi = [n for n in z.namelist() if not n.endswith("/")]
        radici = {n.split("/")[0] for n in nomi}
        if len(radici) != 1 or not SLUG.match(next(iter(radici))) or f"{next(iter(radici))}/percorso.json" not in nomi:
            return self.errore(400, "el zip debe contener una carpeta con percorso.json")
        slug = next(iter(radici))
        dest = PERCORSI / slug
        if dest.exists():
            slug = f"{slug}-{datetime.now():%m%d%H%M}"
            dest = PERCORSI / slug
        for n in nomi:
            rel = Path(*n.split("/")[1:])
            if rel.is_absolute() or ".." in rel.parts or rel.suffix not in (".json", ".md", ".png", ".jpg", ".svg"):
                continue
            out = dest / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(z.read(n))
        if not leggi_json(dest / "percorso.json"):
            shutil.rmtree(dest, ignore_errors=True)
            return self.errore(400, "percorso.json no válido")
        return self.json({"ok": True, "slug": slug})


class GestoreRete(Gestore):
    """Peticiones desde el teléfono, en la red de casa: hace falta la cookie que da el código; terminal, diagnóstico y red no."""
    da_rete = True

    def host_ok(self):
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0]
        return bool(RETE["ip"]) and host == RETE["ip"]

    def origine_ok(self):
        o = self.headers.get("Origin")
        if o and urlparse(o).netloc != self.headers.get("Host"):
            return False
        return self.headers.get("X-Accademia") == "1"

    def autorizzato(self):
        c = SimpleCookie()
        try:
            c.load(self.headers.get("Cookie") or "")
        except Exception:  # cookies mal formadas de otros sitios en la misma dirección
            return False
        tok = c["accademia"].value if "accademia" in c else ""
        if not tok:
            return False
        impronta = hashlib.sha256(tok.encode()).hexdigest()
        return any(hmac.compare_digest(impronta, s) for s in leggi_json(FILE_RETE, {}).get("sessioni", []))

    def accesso(self):
        """Código correcto → cookie para un año. 5 errores por minuto por teléfono, 20 por hora en total: luego hay que esperar."""
        ip, ora = self.client_address[0], time.time()
        try:
            d = self.corpo()
        except (ValueError, json.JSONDecodeError):
            d = {}
        with blocco:
            falliti = [x for x in RETE["falliti"].get(ip, []) if ora - x < 60]
            tutti = [x for x in RETE["falliti_ora"] if ora - x < 3600]
            bloccato = len(falliti) >= 5 or len(tutti) >= 20
            r = leggi_json(FILE_RETE, {})
            giusto = not bloccato and r.get("codice") and hmac.compare_digest(str(d.get("codice", "")).strip().encode("utf-8"), r["codice"].encode("utf-8"))
            tok = None
            if giusto:
                tok = secrets.token_urlsafe(32)
                r["sessioni"] = (r.get("sessioni", []) + [hashlib.sha256(tok.encode()).hexdigest()])[-20:]
                scrivi_json(FILE_RETE, r)
            elif not bloccato:
                RETE["falliti"][ip] = falliti + [ora]
                RETE["falliti_ora"] = tutti + [ora]
        if bloccato:
            return self.errore(429, "demasiados intentos: espera un minuto")
        if not giusto:
            return self.errore(403, "código incorrecto")
        b = json.dumps({"ok": True}).encode("utf-8")
        self.intestazioni(200, "application/json; charset=utf-8", len(b),
                          {"Set-Cookie": f"accademia={tok}; Path=/; Max-Age=31536000; HttpOnly; SameSite=Strict"})
        self.wfile.write(b)


def apri_terminale(cartella, argv):
    cartella = str(cartella)
    try:
        if sys.platform == "darwin":
            riga = "cd " + sh_q(cartella) + " && " + " ".join(sh_q(a) for a in argv)
            script = f'tell application "Terminal"\nactivate\ndo script "{riga.replace(chr(92), chr(92) * 2).replace(chr(34), chr(92) + chr(34))}"\nend tell'
            subprocess.run(["osascript", "-e", script], check=True, capture_output=True, timeout=20)
        elif WIN:
            wt = shutil.which("wt")
            if wt:
                subprocess.Popen([wt, "-d", cartella, *argv])
            else:
                subprocess.Popen(["cmd", "/c", "start", "", "cmd", "/k", subprocess.list2cmdline(argv)], cwd=cartella)
        else:
            term = shutil.which("x-terminal-emulator") or shutil.which("gnome-terminal")
            if not term:
                return False, "no se ha encontrado ninguna terminal"
            subprocess.Popen([term, "--", *argv], cwd=cartella)
        return True, "terminal abierta"
    except (OSError, subprocess.SubprocessError) as e:
        return False, f"no puedo abrir la terminal: {e}"


def sh_q(s):
    return "'" + str(s).replace("'", "'\\''") + "'"


def diagnosi():
    def versione(nome):
        exe = trova(nome)
        if not exe:
            return None
        try:
            r = subprocess.run([exe, "--version"], capture_output=True, encoding="utf-8", errors="replace", timeout=30,
                               creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            return {"percorso": exe, "versione": (r.stdout or r.stderr).strip()[:80]}
        except (OSError, subprocess.SubprocessError) as e:
            return {"percorso": exe, "errore": str(e)[:200]}
    scrivibile = True
    try:
        UTENTE.mkdir(exist_ok=True)
        (UTENTE / ".prova").write_text("ok", encoding="utf-8")
        (UTENTE / ".prova").unlink()
    except OSError:
        scrivibile = False
    return {"versione": VERSIONE, "data": datetime.now().isoformat(timespec="seconds"), "sistema": platform.platform(),
            "python": sys.version.split()[0], "codifica_predefinita": sys.getfilesystemencoding(),
            "cartella": str(QUI), "scrivibile": scrivibile, "claude": versione("claude"), "codex": versione("codex"),
            "modello_codex": modello_codex(config().get("assistente", {}).get("modello_codex")),
            "percorsi": [p["slug"] for p in elenco_percorsi()], "porta": config().get("porta", 8765),
            "rete": {k: v for k, v in stato_rete().items() if k != "codice"}}


def e_accademia(porta):
    import urllib.request
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{porta}/api/config", timeout=3) as r:
            return (r.headers.get("Server") or "").startswith("Accademia/")
    except (OSError, ValueError):
        return False


def main():
    if "--diagnosi" in sys.argv:
        print(json.dumps(diagnosi(), ensure_ascii=False, indent=1))
        return
    for d in (PERCORSI, UTENTE):
        d.mkdir(exist_ok=True)
    unisci_progressi_vecchi()
    RINNOVO["attivo"] = True
    porta = int(config().get("porta", 8765))
    try:
        srv = ThreadingHTTPServer(("127.0.0.1", porta), Gestore)
    except OSError:
        if e_accademia(porta):
            print(f"Open Escool ya está abierta en http://127.0.0.1:{porta}")
            if "--apri" in sys.argv:
                webbrowser.open(f"http://127.0.0.1:{porta}")
            return
        print(f"El puerto {porta} lo usa otro programa: elige otro puerto en config.json (\"porta\": 8766) y reinicia")
        sys.exit(2)
    url = f"http://127.0.0.1:{porta}"
    print(f"Open Escool {VERSIONE} en {url} (Ctrl+C para detenerla)")
    if config().get("rete", {}).get("telefono"):
        if avvia_rete(porta):
            print(f"Desde el teléfono (misma red Wi-Fi): http://{RETE['ip']}:{porta} · código en Ajustes → Teléfono")
        else:
            print(f"Teléfono: {RETE['errore']}")
    threading.Thread(target=sorveglia_rete, args=(porta,), daemon=True).start()
    if "--apri" in sys.argv:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()

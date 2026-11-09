"""Diagnóstico de Open Escool en este ordenador: un informe para enviar a quien lo mantiene (como ADS para Windows).

  python strumenti/diagnosi.py               -> diagnosi/AAAA-MM-GG_HHMM_<computer>.md y .json
  python strumenti/diagnosi.py --assistente  prueba también una pregunta real a Claude Code y Codex (usa la suscripción, ~10-30 s)
  python strumenti/diagnosi.py --lezione     prueba también las lecciones: voz gratuita en una escena (tiempo real en este
                                             ordenador), Whisper y un fotograma con Remotion (1-5 minutos, gratis)
  python strumenti/diagnosi.py --condividi   el «diagnóstico para compartir» para una incidencia pública (issue en GitHub):
                                             -> diagnosi/AAAA-MM-GG_HHMM_condivisa.md, también impreso aquí para copiarlo. Sin el
                                             nombre del ordenador ni del usuario, las carpetas, la lista de rutas ni las claves (solo
                                             presente/falta); quedan sistema, versiones, qué pruebas pasan y los errores.
                                             Se combina con --lezione y --assistente. No envía nada por sí solo: lo pega quien informa.

Prueba de verdad el servidor en un puerto libre (páginas, API, escritura de una nota de prueba que luego se borra), las
codificaciones (acentos y caracteres no latinos en archivos), las claves presentes (solo los nombres) y los asistentes. No contiene
valores de claves, notas, chats ni perfil.
"""
import getpass
import json
import locale
import os
import platform
import re
import socket
import subprocess
import sys
import tempfile
import threading
import traceback
import urllib.request
from datetime import datetime
from pathlib import Path

QUI = Path(__file__).resolve().parent
RADICE = QUI.parent
sys.path.insert(0, str(RADICE))
sys.path.insert(0, str(QUI))
from comune import chiave, aiuto, tr  # noqa: E402

risultati = []


def voce(nome, ok, dettaglio=""):
    risultati.append({"prova": nome, "ok": bool(ok), "dettaglio": str(dettaglio)[:600]})
    print(f"{'OK ' if ok else 'NO '} {nome}: {str(dettaglio)[:160]}")


def prova(nome):
    def deco(f):
        try:
            r = f()
            voce(nome, True if r is None else r[0], "" if r is None else r[1])
        except Exception as e:  # el diagnóstico no debe detenerse nunca
            voce(nome, False, f"{type(e).__name__}: {e} · {traceback.format_exc(limit=2)[-300:]}")
        return f
    return deco


def main():
    import accademia  # el propio servidor, así se prueba el código real

    info = {"data": datetime.now().isoformat(timespec="seconds"), "versione": accademia.VERSIONE, "sistema": platform.platform(),
            "macchina": platform.machine(), "python": sys.version.split()[0], "eseguibile": sys.executable,
            "codifica_preferita": locale.getpreferredencoding(False), "codifica_file": sys.getfilesystemencoding(),
            "codifica_console": getattr(sys.stdout, "encoding", None), "cartella": str(RADICE),
            "percorsi": [p.name for p in accademia.PERCORSI.iterdir() if (p / "percorso.json").exists()] if accademia.PERCORSI.exists() else []}
    print(json.dumps(info, ensure_ascii=False, indent=1))

    @prova(tr("Python 3.10 o più", "Python 3.10 o superior", "Python 3.10 or later"))
    def _():
        return sys.version_info >= (3, 10), sys.version.split()[0]

    @prova(tr("file UTF-8 con accenti e caratteri non latini", "archivos UTF-8 con acentos y caracteres no latinos",
              "UTF-8 files with accents and non-Latin characters"))
    def _():
        testo = "àèéìòù ñ ü ç — «» 日本語 😀"
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "prova àè.json"
            f.write_text(json.dumps({"t": testo}, ensure_ascii=False), encoding="utf-8")
            letto = json.loads(f.read_text(encoding="utf-8"))["t"]
        return letto == testo, (tr("uguale", "igual", "same") if letto == testo
                                else tr(f"diverso: {letto!r}", f"distinto: {letto!r}", f"different: {letto!r}"))

    @prova(tr("cartella scrivibile", "carpeta con permiso de escritura", "writable folder"))
    def _():
        accademia.UTENTE.mkdir(exist_ok=True)
        f = accademia.UTENTE / ".prova-diagnosi"
        f.write_text("ok", encoding="utf-8")
        f.unlink()

    for nome in ("YOUTUBE_API_KEY", "GEMINI_API_KEY", "TAVILY_API_KEY"):
        v = chiave(nome, obbligatoria=False)
        stato = (tr("presente", "presente", "present") if v
                 else tr("manca (facoltativa)", "falta (opcional)", "missing (optional)") if nome == "TAVILY_API_KEY"
                 else tr("manca", "falta", "missing"))
        voce(tr(f"chiave {nome}", f"clave {nome}", f"key {nome}"), bool(v) or nome == "TAVILY_API_KEY", stato)

    for m in ("claude", "codex"):
        exe = accademia.trova(m)
        if not exe:
            voce(tr(f"{m} installato", f"{m} instalado", f"{m} installed"),
                 m == "codex" and bool(accademia.trova("claude")) or m == "claude" and bool(accademia.trova("codex")),
                 tr("non trovato", "no encontrado", "not found")
                 + (tr(" (basta uno dei due)", " (basta con uno de los dos)", " (one of the two is enough)")
                    if accademia.trova("claude") or accademia.trova("codex") else ""))
            continue
        r = subprocess.run([exe, "--version"], capture_output=True, encoding="utf-8", errors="replace", timeout=60,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        voce(tr(f"{m} installato", f"{m} instalado", f"{m} installed"), r.returncode == 0,
             f"{exe} · {(r.stdout or r.stderr).strip()[:80]}")
    voce(tr("modello Codex scelto", "modelo de Codex elegido", "Codex model chosen"), True,
         accademia.modello_codex(accademia.config().get("assistente", {}).get("modello_codex")) or tr("nessuno", "ninguno", "none"))

    # servidor real en un puerto libre
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    porta = s.getsockname()[1]
    s.close()
    srv = accademia.ThreadingHTTPServer(("127.0.0.1", porta), accademia.Gestore)
    sys.argv.append("--silenzioso")
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{porta}"

    def get(p):
        with urllib.request.urlopen(base + p, timeout=20) as r:
            return r.status, r.headers.get("Content-Type", ""), r.read()

    def post(p, dati, intestazione=True):
        h = {"Content-Type": "application/json"}
        if intestazione:
            h["X-Accademia"] = "1"
        req = urllib.request.Request(base + p, data=json.dumps(dati).encode("utf-8"), headers=h, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.status, json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            return e.code, {}

    for p, tipo in (("/", "text/html"), ("/app.js", "javascript"), ("/stile.css", "text/css"), ("/manifest.webmanifest", "manifest"),
                    ("/sw.js", "javascript"), ("/icone/icona-192.png", "image/png"), ("/api/config", "json"), ("/api/percorsi", "json")):
        @prova(tr(f"server {p}", f"servidor {p}", f"server {p}"))
        def _(p=p, tipo=tipo):
            st, ct, b = get(p)
            return st == 200 and tipo in ct, tr(f"{st} {ct} {len(b)} byte", f"{st} {ct} {len(b)} bytes", f"{st} {ct} {len(b)} bytes")

    @prova(tr("server: note con accenti (scrive e cancella)", "servidor: notas con acentos (escribe y borra)",
              "server: notes with accents (writes and deletes)"))
    def _():
        slug = info["percorsi"][0] if info["percorsi"] else "prova-diagnosi"
        st, r = post("/api/note", {"percorso": slug, "tappa": 1, "video": "diagnosi00", "secondi": 1, "minuto": "0:01",
                                   "testo": "nota di prova àèì ñ 日本", "tipo": "nota"})
        nuova = next((n for n in r.get("note", []) if n.get("video") == "diagnosi00"), None)
        if nuova:
            post("/api/note", {"percorso": slug, "elimina": nuova["id"]})
        return st == 200 and nuova and nuova["testo"].endswith("日本"), f"{st}"

    @prova(tr("server rifiuta richieste da altri siti", "el servidor rechaza peticiones de otros sitios",
              "the server refuses requests from other sites"))
    def _():
        st, _ = post("/api/note", {"percorso": "x", "testo": "x", "tipo": "nota"}, intestazione=False)
        return st == 403, f"{st}"

    if "--assistente" in sys.argv:
        for m in ("claude", "codex"):
            if not accademia.trova(m):
                continue

            @prova(tr(f"domanda vera a {m}", f"pregunta real a {m}", f"real question to {m}"))
            def _(m=m):
                import uuid
                cmd = accademia.comando_assistente(m, accademia.config()["assistente"].get("modello_" + m), str(uuid.uuid4()), True, RADICE)
                # el prompt queda en italiano: es el que se ha probado
                r = subprocess.run(cmd, input="Rispondi solo con la parola: pronto", capture_output=True, encoding="utf-8",
                                   errors="replace", timeout=180, cwd=str(RADICE), creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                return "pronto" in r.stdout.lower(), (r.stdout[-200:] or r.stderr[-300:])
    srv.shutdown()
    lezioni(info)

    ok = sum(r["ok"] for r in risultati)
    out = RADICE / "diagnosi"
    out.mkdir(exist_ok=True)
    if "--condividi" in sys.argv:
        return condivisa(info, ok, out)
    nome = f"{datetime.now():%Y-%m-%d_%H%M}_{platform.node().split('.')[0] or 'pc'}"
    rapporto = {"info": info, "prove": risultati, "riassunto": f"{ok}/{len(risultati)} ok"}
    (out / f"{nome}.json").write_text(json.dumps(rapporto, ensure_ascii=False, indent=1), encoding="utf-8")
    data, n, sistema, py = info["data"], len(risultati), info["sistema"], info["python"]
    righe = [tr(f"# Diagnosi Open Escool · {data}", f"# Diagnóstico de Open Escool · {data}",
                f"# Open Escool diagnostics · {data}"), "",
             tr(f"**{ok}/{n} prove ok** · {sistema} · Python {py}", f"**{ok}/{n} pruebas ok** · {sistema} · Python {py}",
                f"**{ok}/{n} tests ok** · {sistema} · Python {py}"), "",
             tr("| | Prova | Dettaglio |", "| | Prueba | Detalle |", "| | Test | Detail |"), "|---|---|---|"] + \
        [f"| {'✅' if r['ok'] else '❌'} | {r['prova']} | {' '.join(r['dettaglio'][:140].split()).replace('|', '/')} |" for r in risultati] + \
        ["", "```json", json.dumps(info, ensure_ascii=False, indent=1), "```"]
    (out / f"{nome}.md").write_text("\n".join(righe) + "\n", encoding="utf-8")
    f_md = out / (nome + ".md")
    print(tr(f"\n{ok}/{n} ok · rapporto: {f_md}", f"\n{ok}/{n} ok · informe: {f_md}", f"\n{ok}/{n} ok · report: {f_md}"))


def lezioni(info):
    """Lo que necesitan las lecciones generadas: Node y Remotion, ffmpeg, el entorno de la voz. Con --lezione, también una prueba real."""
    import shutil

    import comune

    lez = RADICE / "lezione"

    @prova(tr("lezioni: Node 18 o più", "lecciones: Node 18 o superior", "lessons: Node 18 or later"))
    def _():
        exe = shutil.which("node")
        if not exe:
            return False, tr("manca Node (Windows: winget install OpenJS.NodeJS.LTS; Mac: brew install node)",
                             "falta Node (Windows: winget install OpenJS.NodeJS.LTS; Mac: brew install node)",
                             "Node is missing (Windows: winget install OpenJS.NodeJS.LTS; Mac: brew install node)")
        v = subprocess.run([exe, "-v"], capture_output=True, encoding="utf-8", errors="replace", timeout=30).stdout.strip()
        return int(v.lstrip("v").split(".")[0]) >= 18, f"{v} · {exe}"

    @prova(tr("lezioni: ffmpeg", "lecciones: ffmpeg", "lessons: ffmpeg"))
    def _():
        exe = shutil.which("ffmpeg")
        if not exe:
            return False, tr("manca ffmpeg (Windows: winget install Gyan.FFmpeg; Mac: brew install ffmpeg)",
                             "falta ffmpeg (Windows: winget install Gyan.FFmpeg; Mac: brew install ffmpeg)",
                             "ffmpeg is missing (Windows: winget install Gyan.FFmpeg; Mac: brew install ffmpeg)")
        r = subprocess.run([exe, "-version"], capture_output=True, encoding="utf-8", errors="replace", timeout=30)
        return r.returncode == 0, r.stdout.splitlines()[0][:80] if r.stdout else r.stderr[:200]

    @prova(tr("lezioni: Remotion e il suo Chrome", "lecciones: Remotion y su Chrome", "lessons: Remotion and its Chrome"))
    def _():
        cli = lez / "node_modules" / "@remotion" / "cli" / "remotion-cli.js"
        base = lez / "node_modules" / ".remotion" / "chrome-headless-shell"
        chrome = list(base.glob("*/*/chrome-headless-shell")) + list(base.glob("*/*/chrome-headless-shell.exe"))
        if not cli.exists():
            return False, tr("manca Remotion: nella cartella lezione/ lancia «npm install» (lo fa l'installazione)",
                             "falta Remotion: en la carpeta lezione/ lanza «npm install» (lo hace la instalación)",
                             "Remotion is missing: run «npm install» in the lezione/ folder (the installer does it)")
        stato = "ok: " + chrome[0].parent.name if chrome else tr("non ancora scaricato (lo scarica il primo render)",
                                                                   "aún no descargado (lo descarga el primer render)",
                                                                   "not downloaded yet (the first render downloads it)")
        return True, f"Remotion ok · Chrome {stato}"

    py = comune.python_voce(((accademia_config().get("lezioni") or {}).get("voce") or {}).get("python") or "")
    mod = comune.moduli_voce(py)
    info["voce"] = {"python": str(py), "installate": sorted(mod), "mac_apple": comune.mac_apple(),
                    "auto": {l: comune.modello_gratuito("auto", mod, l) for l in ("it", "es", "en")}}

    @prova(tr("lezioni: voce gratuita installata", "lecciones: voz gratuita instalada", "lessons: free voice installed"))
    def _():
        if not py.exists():
            return False, tr(f"manca l'ambiente della voce ({py}): rilancia l'installazione",
                             f"falta el entorno de la voz ({py}): vuelve a lanzar la instalación",
                             f"the voice environment is missing ({py}): run the installer again")
        voci = sorted(mod - {"whisper"})
        elenco = ", ".join(voci) or tr("nessuna", "ninguna", "none")
        whisper = tr("sì", "sí", "yes") if "whisper" in mod else "no"
        base = ", ".join(f"{l} {m}" for l, m in info["voce"]["auto"].items())
        return bool(voci) and "whisper" in mod, tr(f"voci: {elenco} · Whisper: {whisper} · di base: {base}",
                                                   f"voces: {elenco} · Whisper: {whisper} · por defecto: {base}",
                                                   f"voices: {elenco} · Whisper: {whisper} · default: {base}")

    @prova(tr("lezioni: collegamenti nella cartella (se no, copia)", "lecciones: enlaces en la carpeta (si no, copia)",
              "lessons: links in the folder (otherwise, copy)"))
    def _():
        with tempfile.TemporaryDirectory() as d:
            try:
                (Path(d) / "l").symlink_to(Path(d), target_is_directory=True)
                return True, tr("si possono creare", "se pueden crear", "they can be created")
            except OSError as e:
                errore = e.__class__.__name__
                return True, tr(f"non si possono creare ({errore}): lezione.py copia i file, va bene",
                                f"no se pueden crear ({errore}): lezione.py copia los archivos, está bien",
                                f"they cannot be created ({errore}): lezione.py copies the files, that's fine")

    @prova(tr("lezioni: chiave ElevenLabs (facoltativa)", "lecciones: clave de ElevenLabs (opcional)",
              "lessons: ElevenLabs key (optional)"))
    def _():
        return True, (tr("presente", "presente", "present") if chiave("ELEVENLABS_API_KEY", obbligatoria=False)
                      else tr("assente (si usa la voce gratuita)", "ausente (se usa la voz gratuita)",
                              "absent (the free voice is used)"))

    if "--lezione" not in sys.argv or not py.exists():
        return
    testi = {"it": "Il budget giornaliero non è un tetto del giorno: è una media su sette giorni. Se imposti quindici euro al giorno, "
                   "in un giorno buono la campagna può spenderne fino a trenta.",
             "es": "El presupuesto diario no es un tope del día: es una media de siete días. Con Target CPC pagas cada clic, "
                   "y en un día bueno la campaña puede gastar hasta el doble."}
    provate = set()
    for lingua, testo in testi.items():  # una prueba por motor: el italiano y, si usa otra voz, el español
        modello = info["voce"]["auto"][lingua]
        if modello in provate:
            continue
        provate.add(modello)
        prova_voce(info, py, modello, lingua, testo)

    @prova(tr("lezioni: un fotogramma con Remotion", "lecciones: un fotograma con Remotion", "lessons: one frame with Remotion"))
    def _():
        import time

        cli = lez / "node_modules" / "@remotion" / "cli" / "remotion-cli.js"
        piano = {"fps": 30, "durata_f": 90, "stimato": True, "lingua": "it", "voce": "", "voce_info": {}, "marchio": "Open Escool",
                 "percorso": "Diagnosi", "titolo": "Prova àèì ñ", "tappa": 1, "etichetta_passi": "Passi", "crediti": "", "passi": ["Uno"],
                 "tema": {}, "sottotitoli": [{"da_f": 5, "a_f": 85, "testo": "Prova dei sottotitoli àèì ñ"}],
                 "scene": [{"id": "a", "tipo": "apertura", "passo": 0, "da_f": 0, "durata_f": 90, "m": {"titolo": 5, "fonti": 20},
                            "schermo": {"sopra": "Diagnosi", "titolo": "Prova àèì ñ 日本", "sotto": "Open Escool", "fonti": "Fonti: prova"},
                            "voce_s": 0.2, "voce_dur": 2.5}]}
        with tempfile.TemporaryDirectory() as d:
            pub = Path(d) / "public"
            pub.mkdir()
            for nome in ("font", "marca"):
                shutil.copytree(lez / "public" / nome, pub / nome)
            (pub / "piano.json").write_text(json.dumps(piano, ensure_ascii=False), encoding="utf-8")
            t = time.time()
            r = subprocess.run([shutil.which("node") or "node", str(cli), "still", "src/index.ts", "Lezione", str(Path(d) / "f.jpg"), "--frame=45",
                                f"--public-dir={pub}", "--bundle-cache=false", "--log=error"], cwd=str(lez), capture_output=True,
                               encoding="utf-8", errors="replace", timeout=900, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            ok = r.returncode == 0 and (Path(d) / "f.jpg").exists()
            secondi_ = f"{time.time() - t:.0f}"
            return ok, tr(f"in {secondi_} s", f"en {secondi_} s", f"in {secondi_} s") if ok else (r.stderr or r.stdout)[-400:]


def prova_voce(info, py, modello, lingua, testo):
    import comune

    @prova(tr(f"lezioni: voce vera ({modello}, {lingua}) e Whisper su questo computer",
              f"lecciones: voz real ({modello}, {lingua}) y Whisper en este ordenador",
              f"lessons: real voice ({modello}, {lingua}) and Whisper on this computer"))
    def _():
        import time

        with tempfile.TemporaryDirectory() as d:
            lavoro = {"modello": modello, "voce": comune.VOCI_BASE.get(modello, {}).get(lingua, "base"), "lingua": lingua,
                      "whisper": "medium" if comune.mac_apple() else "small", "soglia": 0.9, "tentativi": 2, "seme": 7,
                      "scene": [{"id": "prova", "testo": testo, "wav": str(Path(d) / "prova.wav"), "parole": str(Path(d) / "prova.parole.json")}]}
            f = Path(d) / "lavoro.json"
            f.write_text(json.dumps(lavoro, ensure_ascii=False), encoding="utf-8")
            t = time.time()
            r = subprocess.run([str(py), str(QUI / "voce_locale.py"), str(f)], capture_output=True, encoding="utf-8", errors="replace",
                               timeout=1800, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            meta = json.loads((Path(d) / "prova.voce.json").read_text(encoding="utf-8")) if (Path(d) / "prova.voce.json").exists() else {}
            info["voce"].setdefault("prove", {})[f"{modello}_{lingua}"] = {"secondi_totali": round(time.time() - t, 1),
                                                                           **{k: meta.get(k) for k in ("durata_s", "tempo_s", "voto_scena", "giri")}}
            if r.returncode != 0 or not meta:
                return False, (r.stderr or r.stdout)[-400:]
            per_lezione = meta["tempo_s"] / max(meta["durata_s"], 0.1) * 240 / 60
            ds, ts, vs = meta["durata_s"], meta["tempo_s"], meta.get("voto_scena")
            return meta.get("voto_scena", 0) >= 0.8, tr(
                f"{ds} s di voce in {ts} s con il controllo (voto {vs}) · una lezione di 4 minuti ≈ {per_lezione:.0f} minuti",
                f"{ds} s de voz en {ts} s con el control (nota {vs}) · una lección de 4 minutos ≈ {per_lezione:.0f} minutos",
                f"{ds} s of voice in {ts} s with the check (score {vs}) · a 4-minute lesson ≈ {per_lezione:.0f} minutes")


def pulito(testo, sostituzioni):
    """Quita de un texto las carpetas, el nombre del ordenador, el del usuario y los nombres de los cursos (también con las barras de
    Windows)."""
    t = str(testo)
    for vero, finto in sorted(sostituzioni, key=lambda x: -len(x[0] or "")):  # primero los más largos: el ordenador antes que el usuario
        if vero and len(vero) >= 3:
            for forma in {vero, vero.replace("\\", "/"), vero.replace("/", "\\")}:
                t = re.sub(r"(?<![A-Za-z0-9])" + re.escape(forma) + r"(?![A-Za-z0-9])", finto, t, flags=re.IGNORECASE)
    # carpetas personales que quedan (otros discos, otros usuarios): /Users/x, /home/x, C:\Users\x
    t = re.sub(r"(/Users/|/home/|[A-Za-z]:[\\/]+Users[\\/]+)[^\\/\s\"']+", lambda m: m.group(1) + "<usuario>", t, flags=re.IGNORECASE)
    return t


def condivisa(info, ok, out):
    """El diagnóstico para pegar en una incidencia pública: nada que diga quién es ni qué estudia quien lo envía."""
    casa = str(Path.home())
    sost = [(str(RADICE), "<carpeta de Open Escool>"), (casa, "~")]
    try:
        sost.append((getpass.getuser(), "<usuario>"))
    except Exception:  # noqa: BLE001 (en algunos sistemas no hay nombre de usuario)
        pass
    nodo = platform.node()
    sost += [(nodo, "<computer>"), (nodo.split(".")[0], "<computer>")]
    sost += [(c, "<ruta>") for c in sorted(info.get("percorsi", []), key=len, reverse=True)]
    tenuti = {k: info.get(k) for k in ("versione", "sistema", "macchina", "python", "codifica_preferita", "codifica_file",
                                       "codifica_console")}
    tenuti["corsi"] = len(info.get("percorsi", []))
    versione, giorno, n = info.get("versione", ""), info["data"][:10], len(risultati)
    righe = [tr(f"### Diagnosi da condividere · Open Escool {versione} · {giorno}",
                f"### Diagnóstico para compartir · Open Escool {versione} · {giorno}",
                f"### Diagnostics to share · Open Escool {versione} · {giorno}"), "",
             tr("Contiene: sistema, versioni, quali prove passano e gli errori. Tolti: nome del computer e dell'utente, "
                "cartelle, elenco dei corsi, chiavi (solo presente/manca), note, chat e profilo. "
                "È pubblica: rileggila prima di incollarla.",
                "Contiene: sistema, versiones, qué pruebas pasan y los errores. Quitados: nombre del ordenador y del usuario, "
                "carpetas, lista de rutas, claves (solo presente/falta), notas, chat y perfil. "
                "Es público: reléelo antes de pegarlo.",
                "Contains: system, versions, which tests pass and the errors. Removed: computer and user name, folders, "
                "list of paths, keys (only present/missing), notes, chat and profile. "
                "It is public: read it again before pasting it."), "",
             tr(f"**{ok}/{n} prove ok**", f"**{ok}/{n} pruebas ok**", f"**{ok}/{n} tests ok**"), "",
             tr("| | Prova | Dettaglio |", "| | Prueba | Detalle |", "| | Test | Detail |"), "|---|---|---|"]
    righe += [f"| {'✅' if r['ok'] else '❌'} | {pulito(r['prova'], sost)} | {' '.join(pulito(r['dettaglio'][:200], sost).split()).replace('|', '/')} |"
              for r in risultati]
    righe += ["", "```json", pulito(json.dumps(tenuti, ensure_ascii=False, indent=1), sost), "```"]
    testo = "\n".join(righe) + "\n"
    f = out / f"{datetime.now():%Y-%m-%d_%H%M}_condivisa.md"
    f.write_text(testo, encoding="utf-8")
    print(tr("\n----- da qui: copia e incolla nella segnalazione -----\n",
             "\n----- desde aquí: copia y pega en la incidencia -----\n",
             "\n----- from here: copy and paste into the issue -----\n") + testo
          + tr("----- fin qui -----", "----- hasta aquí -----", "----- up to here -----"))
    print(tr(f"{ok}/{n} ok · salvata anche in diagnosi/{f.name}", f"{ok}/{n} ok · guardado también en diagnosi/{f.name}",
             f"{ok}/{n} ok · also saved in diagnosi/{f.name}"))


def accademia_config():
    import accademia

    return accademia.config()


if __name__ == "__main__":
    aiuto(__doc__)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()

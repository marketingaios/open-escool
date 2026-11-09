"""Claves desde el bloc de notas: el valor solo lo lee este programa, nunca el chat del asistente.

  python strumenti/chiavi.py stato                    qué claves hay (sin valores)
  python strumenti/chiavi.py prepara GEMINI_API_KEY   crea el archivo temporal y lo abre en el editor de texto
  python strumenti/chiavi.py leggi GEMINI_API_KEY     lo lee, prueba la clave, la guarda en el .env de Open Escool, borra el archivo

Claves: GEMINI_API_KEY (fichas de los vídeos, gratis), YOUTUBE_API_KEY (búsqueda de vídeos, gratis), TAVILY_API_KEY (opcional),
ELEVENLABS_API_KEY (voz de las lecciones, opcional: también se puede poner desde Ajustes → Voz de las lecciones).
El valor no se imprime nunca. Guía para crearlas: docs/chiavi.md.
"""
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

from comune import RADICE, chiave, scrivi_chiave, aiuto, tr

NOMI = {
    "GEMINI_API_KEY": ("Gemini (Google AI Studio)", "https://aistudio.google.com/apikey"),
    "YOUTUBE_API_KEY": ("YouTube Data API v3 (Google Cloud)", "https://console.cloud.google.com/apis/library/youtube.googleapis.com"),
    "TAVILY_API_KEY": ("Tavily", "https://app.tavily.com"),
    "ELEVENLABS_API_KEY": (tr("ElevenLabs (voce delle lezioni, facoltativa)", "ElevenLabs (voz de las lecciones, opcional)",
                              "ElevenLabs (lesson voice, optional)"), "https://elevenlabs.io/app/settings/api-keys"),
}


def file_tmp(nome):
    return RADICE / f"incolla-{nome.split('_')[0].lower()}.txt"


def apri(f):
    if sys.platform == "darwin":
        subprocess.run(["open", "-e", str(f)], check=False)
    elif os.name == "nt":
        subprocess.Popen(["notepad.exe", str(f)])
    else:
        subprocess.run(["xdg-open", str(f)], check=False)


def prova(nome, v):
    try:
        if nome == "GEMINI_API_KEY":
            r = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models?pageSize=100", headers={"x-goog-api-key": v})
            n = len(json.load(urllib.request.urlopen(r, timeout=30)).get("models", []))
            return True, tr(f"chiave Gemini valida ({n} modelli)", f"clave de Gemini válida ({n} modelos)",
                            f"Gemini key is valid ({n} models)")
        if nome == "YOUTUBE_API_KEY":
            u = "https://www.googleapis.com/youtube/v3/videos?" + urllib.parse.urlencode({"part": "id", "id": "dQw4w9WgXcQ", "key": v})
            json.load(urllib.request.urlopen(u, timeout=30))
            return True, tr("chiave YouTube valida", "clave de YouTube válida", "YouTube key is valid")
        if nome == "TAVILY_API_KEY":
            r = urllib.request.Request("https://api.tavily.com/search", data=json.dumps({"query": "test", "max_results": 1}).encode(),
                                       headers={"Authorization": f"Bearer {v}", "Content-Type": "application/json"})
            urllib.request.urlopen(r, timeout=30).read()
            return True, tr("chiave Tavily valida", "clave de Tavily válida", "Tavily key is valid")
        if nome == "ELEVENLABS_API_KEY":
            from elevenlabs import prova_chiave

            return prova_chiave(v)
    except urllib.error.HTTPError as e:
        return False, tr(f"la chiave non funziona (HTTP {e.code})", f"la clave no funciona (HTTP {e.code})",
                         f"the key doesn't work (HTTP {e.code})")
    except (urllib.error.URLError, OSError) as e:
        return False, tr(f"non riesco a provarla, controlla la rete ({type(e).__name__})",
                         f"no consigo probarla, revisa la conexión ({type(e).__name__})",
                         f"can't test it, check the connection ({type(e).__name__})")
    return False, tr("chiave sconosciuta", "clave desconocida", "unknown key")


def prepara(nome):
    titolo, url = NOMI[nome]
    f = file_tmp(nome)
    eol = "\r\n" if os.name == "nt" else "\n"
    istruzioni = [tr(f"# Incolla qui sotto la chiave {titolo}, su una riga sola. Si crea su {url}",
                     f"# Pega aquí debajo la clave de {titolo}, en una sola línea. Se crea en {url}",
                     f"# Paste the {titolo} key below, on a single line. You can create it at {url}"),
                  tr("# Poi salva (Mac: Cmd+S, Windows: Ctrl+S) e chiudi. Non incollarla mai in chat:",
                     "# Luego guarda (Mac: Cmd+S, Windows: Ctrl+S) y cierra. No la pegues nunca en el chat:",
                     "# Then save (Mac: Cmd+S, Windows: Ctrl+S) and close. Never paste it in the chat:"),
                  tr("# questo file lo legge solo il programma, che poi lo cancella.",
                     "# este archivo solo lo lee el programa, que luego lo borra.",
                     "# only the program reads this file, and then it deletes it.")]
    f.write_text(eol.join(istruzioni + ["", ""]), encoding="utf-8")
    try:
        os.chmod(f, 0o600)
    except OSError:
        pass
    apri(f)
    print(tr(f"aperto {f.name}: incolla la chiave, salva e chiudi; poi `leggi {nome}`",
             f"abierto {f.name}: pega la clave, guarda y cierra; luego `leggi {nome}`",
             f"opened {f.name}: paste the key, save and close; then `leggi {nome}`"))


def cancella(f):
    n = f.stat().st_size
    with open(f, "r+b") as h:
        h.write(b"\0" * n)
        h.flush()
        os.fsync(h.fileno())
    f.unlink()


def leggi(nome):
    f = file_tmp(nome)
    if not f.exists():
        sys.exit(tr(f"il file non c'è: prima `prepara {nome}`", f"el archivo no está: primero `prepara {nome}`",
                    f"the file is not there: first `prepara {nome}`"))
    b = f.read_bytes()
    testo = b.decode("utf-16") if b[:2] in (b"\xff\xfe", b"\xfe\xff") else b.decode("utf-8-sig", errors="replace")
    righe = [r.strip() for r in testo.splitlines() if r.strip() and not r.lstrip().startswith("#")]
    if len(righe) != 1:
        sys.exit(tr(f"nel file ci sono {len(righe)} righe oltre alle istruzioni: lascia solo la chiave, salva e riprova",
                    f"en el archivo hay {len(righe)} líneas además de las instrucciones: "
                    "deja solo la clave, guarda y vuelve a probar",
                    f"the file has {len(righe)} lines besides the instructions: leave only the key, save and try again"))
    v = righe[0].strip().strip('"').strip("'")
    if not re.fullmatch(r"[A-Za-z0-9_\-\.]{20,200}", v):
        sys.exit(tr("non sembra una chiave (una riga senza spazi): ricopiala intera, salva e riprova",
                    "no parece una clave (una línea sin espacios): cópiala entera otra vez, guarda y vuelve a probar",
                    "this doesn't look like a key (one line, no spaces): copy it again in full, save and try again"))
    ok, msg = prova(nome, v)
    if not ok:
        sys.exit(msg + tr(": il file resta, ricontrolla la chiave", ": el archivo se queda, revisa la clave",
                          ": the file stays, check the key"))
    scrivi_chiave(nome, v)
    cancella(f)
    print(msg + tr(f"; salvata come {nome} nel .env di Open Escool, file temporaneo cancellato",
                   f"; guardada como {nome} en el .env de Open Escool, archivo temporal borrado",
                   f"; saved as {nome} in the Open Escool .env, temporary file deleted"))


def stato():
    for n, (titolo, url) in NOMI.items():
        c = tr("presente", "presente", "present") if chiave(n, obbligatoria=False) else tr("manca", "falta", "missing")
        print(f"{n}: {c} · {titolo} · {url}")


if __name__ == "__main__":
    aiuto(__doc__)
    a = sys.argv[1:]
    if a[:1] == ["stato"]:
        stato()
    elif len(a) == 2 and a[0] in ("prepara", "leggi") and a[1] in NOMI:
        (prepara if a[0] == "prepara" else leggi)(a[1])
    else:
        sys.exit(__doc__)

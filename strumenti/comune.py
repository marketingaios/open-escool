"""Lo común a las herramientas de Open Escool: carpetas, claves en el .env, JSON en UTF-8, registro de las llamadas."""
import json
import re
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

RADICE = Path(__file__).resolve().parents[1]
PERCORSI = RADICE / "percorsi"
ENV = RADICE / ".env"

if hasattr(sys.stdout, "reconfigure"):  # en Windows la consola no es UTF-8 de serie
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)


def chiave(nome, obbligatoria=True):
    if os.environ.get(nome):
        return os.environ[nome].strip().strip('"').strip("'")
    if ENV.exists():
        for r in ENV.read_text(encoding="utf-8-sig").splitlines():
            if r.startswith(nome + "="):
                v = r.split("=", 1)[1].strip().strip('"').strip("'")
                if v:
                    return v
    if obbligatoria:
        sys.exit(tr(f"Manca {nome}: python strumenti/chiavi.py prepara {nome} (la guida è in docs/chiavi.md)",
                    f"Falta {nome}: python strumenti/chiavi.py prepara {nome} (la guía está en docs/chiavi.md)",
                    f"{nome} is missing: python strumenti/chiavi.py prepara {nome} (the guide is in docs/chiavi.md)"))
    return None


def scrivi_chiave(nome, valore):
    righe = ENV.read_text(encoding="utf-8-sig").splitlines() if ENV.exists() else []
    righe = [r for r in righe if not r.startswith(nome + "=")] + [f"{nome}={valore}"]
    ENV.write_text("\n".join(righe) + "\n", encoding="utf-8")
    try:
        os.chmod(ENV, 0o600)
    except OSError:
        pass


def togli_chiave(nome):
    if ENV.exists():
        righe = [r for r in ENV.read_text(encoding="utf-8-sig").splitlines() if not r.startswith(nome + "=")]
        ENV.write_text("\n".join(righe) + ("\n" if righe else ""), encoding="utf-8")


def lingue_video(m):
    """Un idioma por ruta (`lingua_video`, se pregunta al crearla); los mapas antiguos tenían la lista `lingue_video`."""
    return [m["lingua_video"]] if m.get("lingua_video") else (m.get("lingue_video") or [])


NOME_PERCORSO = re.compile(r"^[a-z0-9][a-z0-9-]{0,60}$")  # como SLUG en accademia.py


def aiuto(doc):
    """-h o --help: imprime el uso de la herramienta y sale, antes de tocar ninguna carpeta."""
    if any(a in ("-h", "--help") for a in sys.argv[1:]):
        print(doc)
        sys.exit(0)


def lingua_messaggi():
    """Idioma de los mensajes de las herramientas (it, es o en): OPEN_ESCOOL_LINGUA si está, si no `lingua` de config.json
    y, si falta, la de config.esempio.json. Se lee en cada mensaje: un cambio en Ajustes vale enseguida, también en el servidor."""
    l = os.environ.get("OPEN_ESCOOL_LINGUA", "")
    for f in () if l else (RADICE / "config.json", RADICE / "config.esempio.json"):
        try:
            l = json.loads(f.read_text(encoding="utf-8-sig")).get("lingua") or ""
        except (OSError, ValueError, AttributeError):
            l = ""
        if l:
            break
    return l[:2] if l[:2] in ("it", "es", "en") else "es"


def tr(it, es, en):
    """Un mensaje para quien usa Open Escool en su idioma: tr(f"…italiano…", f"…español…", f"…english…").
    La ayuda (--help) y los comentarios quedan en español; los prompts para los modelos, en italiano."""
    return {"it": it, "es": es, "en": en}[lingua_messaggi()]


def cartella(slug):
    if not slug or not NOME_PERCORSO.match(slug):
        sys.exit(tr(f"nome di percorso non valido: {slug!r} (minuscole, cifre e trattini, inizia con una lettera o una cifra)",
                    f"nombre de ruta no válido: {slug!r} (minúsculas, cifras y guiones; empieza por una letra o una cifra)",
                    f"invalid path name: {slug!r} (lowercase letters, digits and hyphens; starts with a letter or a digit)"))
    d = PERCORSI / slug
    (d / "lavoro").mkdir(parents=True, exist_ok=True)
    return d


def leggi(p, base=None):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return base


def scrivi(p, dati):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(dati, ensure_ascii=False, indent=1), encoding="utf-8")


def registra(slug, riga):
    riga = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), **riga}
    with open(PERCORSI / slug / "lavoro" / "chiamate.jsonl", "a", encoding="utf-8") as h:
        h.write(json.dumps(riga, ensure_ascii=False) + "\n")


def secondi(m):
    """'1:02:03', '4:05' o ISO 8601 (PT1H2M3S) en segundos."""
    if m in (None, ""):
        return None
    m = str(m)
    if m.startswith("P"):
        import re
        g = re.match(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", m)
        d, h, mi, s = (int(x or 0) for x in g.groups())
        return d * 86400 + h * 3600 + mi * 60 + s
    t = 0
    for x in m.split(":"):
        t = t * 60 + int(x)
    return t


def mmss(x):
    x = int(x)
    return f"{x // 3600}:{x % 3600 // 60:02d}:{x % 60:02d}" if x >= 3600 else f"{x // 60}:{x % 60:02d}"


# --- voz gratuita de las lecciones ---------------------------------------------------------------------------------------------
# Dos familias: Chatterbox con mlx-audio (solo Mac con Apple Silicon, la voz votada el 06/11) y las voces ligeras con ONNX Runtime
# (Supertonic 3, Kokoro-82M: en el procesador, también en Windows sin tarjeta gráfica; prueba de voces del 07/11).
# voz ligera por defecto de cada idioma: votada por el usuario el 07/11 (it Supertonic F5, es Kokoro Dora). El inglés no se votó:
# Kokoro (idioma de origen del modelo, voz Heart), por volver a escuchar en la primera lección en inglés
LEGGERA = {"it": "supertonic", "es": "kokoro-onnx", "en": "kokoro-onnx"}
VOCI_BASE = {"chatterbox": {"it": "base", "es": "base", "en": "base"},
             "supertonic": {"it": "F5", "es": "F4", "en": "F5"},
             "kokoro-onnx": {"it": "if_sara", "es": "ef_dora", "en": "af_heart"}}
MODULO = {"chatterbox": "mlx_audio", "supertonic": "supertonic", "kokoro-onnx": "kokoro_onnx"}


def mac_apple():
    import platform

    return sys.platform == "darwin" and platform.machine() == "arm64"


def python_voce(py=""):
    """El Python del entorno de la voz: el de config.json; si no, strumenti/.voce (Scripts\\python.exe en Windows)."""
    if py:
        return Path(py)
    base = RADICE / "strumenti" / ".voce"
    return base / "Scripts" / "python.exe" if os.name == "nt" else base / "bin" / "python"


def moduli_voce(py):
    """Qué voces están instaladas en el entorno (mira las carpetas, sin arrancar Python): {"chatterbox", "supertonic", ...}."""
    py = Path(py)
    if not py.exists():
        return set()
    venv = py.parent.parent
    siti = list(venv.glob("lib/python3*/site-packages")) + list(venv.glob("Lib/site-packages"))
    trovati = {m for m, modulo in MODULO.items() if any((s / modulo).is_dir() for s in siti)}
    if any((s / "faster_whisper").is_dir() for s in siti):
        trovati.add("whisper")
    return trovati


def modello_gratuito(scelto, moduli, lingua="it"):
    """«auto» (o vacío): Chatterbox en el Mac con Apple Silicon si está; si no, la voz ligera del idioma (si falta, la otra)."""
    if scelto and scelto != "auto":
        return scelto
    if mac_apple() and "chatterbox" in moduli:
        return "chatterbox"
    preferita = LEGGERA.get(lingua, "supertonic")
    altre = [m for m in ("supertonic", "kokoro-onnx") if m in moduli and m != preferita]
    return preferita if preferita in moduli or not altre else altre[0]

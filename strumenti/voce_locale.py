"""Voz gratuita en el ordenador para las lecciones de Open Escool: un wav por escena y los tiempos de cada palabra.

No se lanza a mano: lo llama `lezione.py <ruta> <etapa> voce` con el Python del entorno de la voz
(config.json → lezioni → voce → python). Dos familias de voces:
- en Mac con Apple Silicon, con mlx-audio: Chatterbox (la voz por defecto en el Mac), Kokoro y Qwen3-TTS;
- en cualquier sitio, también en Windows sin tarjeta gráfica, con ONNX Runtime en el procesador: las voces ligeras `supertonic`
  (Supertonic 3) y `kokoro-onnx` (Kokoro-82M). Pesos en strumenti/.modelli/ la primera vez.
En los dos casos, faster-whisper para el control y los tiempos de las palabras.

    <python de la voz> strumenti/voce_locale.py lavoro.json
    <python de la voz> strumenti/voce_locale.py controlla lavoro.json    solo la nueva escucha con Whisper (voces de ElevenLabs)
    <python de la voz> strumenti/voce_locale.py prepara supertonic --whisper small    descarga los pesos (lo hace la instalación)

lavoro.json: {"modello": "chatterbox|kokoro|qwen|supertonic|kokoro-onnx", "voce": "im_nicola", "lingua": "it", "whisper": "medium", "soglia": 0.9,
              "tentativi": 4, "seme": 7, "pronuncia": {"ChatGPT": "Chat GPT"},
              "scene": [{"id": "apertura", "testo": "...", "wav": ".../voce/apertura.wav", "parole": ".../voce/apertura.parole.json"}]}

Para cada escena: el texto se divide en frases agrupadas; cada trozo se genera, se recorta el silencio de los bordes y se vuelve a
escuchar con Whisper: si las palabras no cuadran (voz que inventa sonidos o deforma palabras, le pasa a Chatterbox) se rehace con
otra semilla y se queda el mejor. `pronuncia` cambia cómo se escribe una palabra solo para la voz (siglas, palabras extranjeras).
Los trozos se unen con una pausa fija; luego -16 LUFS con loudnorm lineal (sin compresión). Whisper vuelve a transcribir el wav con
los tiempos de cada palabra: `lezione.py` los alinea con el guion, así las cosas aparecen cuando la voz las nombra. Una escena ya
hecha con el mismo texto y la misma voz no se rehace. Modelos: Kokoro-82M (Apache 2.0), Qwen3-TTS (Apache 2.0), Chatterbox
Multilingual (MIT), Supertonic 3 (modelo OpenRAIL-M, código MIT); pesos descargados la primera vez.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
import subprocess
import sys
import tempfile
import time
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np
from scipy.io import wavfile

QUI = Path(__file__).resolve().parent
if hasattr(sys.stdout, "reconfigure"):  # en Windows, si el asistente lee la salida, la consola no es UTF-8 por defecto
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
REPO = {
    "kokoro": "mlx-community/Kokoro-82M-bf16",
    "qwen": "mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16",
    "chatterbox": "mlx-community/chatterbox-multilingual-v3",
}
CONDS_CHATTERBOX = "mlx-community/chatterbox-fp16"  # la v3 multilingüe no tiene la voz por defecto: la toma de la v2 (la misma voz)
LINGUA = {"kokoro": {"it": "i", "es": "e", "en": "a"}, "qwen": {"it": "italian", "es": "spanish", "en": "english"},
          "chatterbox": {"it": "it", "es": "es", "en": "en"}}
PEZZO = {"kokoro": 200, "qwen": 700, "chatterbox": 220, "supertonic": 280, "kokoro-onnx": 200}  # caracteres máximos por trozo
# voces ligeras (ONNX, solo procesador: Mac y Windows)
ONNX = {"supertonic", "kokoro-onnx"}
LINGUA_ONNX = {"kokoro-onnx": {"it": "it", "es": "es", "en": "en-us"}, "supertonic": {"it": "it", "es": "es", "en": "en"}}
KOKORO_ONNX = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/"
KOKORO_FILE = {"kokoro-v1.0.onnx": "model-files-v1.1/kokoro-v1.0.onnx", "voices-v1.0.bin": "model-files-v1.1/voices-v1.0.bin"}
SUPERTONIC = {"modello": "supertonic-3", "passi": 8}  # 8 pasos = calidad completa del paquete
# ritmo cercano al de Chatterbox (~165-180 palabras por minuto). Medido el 07/11 en la lección t5 a velocidad 1,0: Supertonic it 130,
# es 152-167; Kokoro it 144-161, es 166-170 (Chatterbox it 183, es 176)
VELOCITA = {"supertonic": {"it": 1.25, "es": 1.05, "en": 1.05}, "kokoro-onnx": {"it": 1.08, "es": 1.0, "en": 1.0}}
# palabras inglesas que una voz lee con las reglas de su idioma: Kokoro en español decía «tarjet», «bios», «clix» (07/11, Whisper
# en la lección t5: con estas grafías, 100 %). El guion puede añadir o cambiar alguna con su "pronuncia", que tiene prioridad.
PRONUNCIA_VOCE = {"kokoro-onnx": {"es": {"Target": "Tárguet", "target": "tárguet", "Views": "Viús", "views": "viús",
                                         "Clicks": "Clics", "clicks": "clics"}}}
DETERMINISTICI = {"kokoro", "kokoro-onnx"}  # misma frase = mismo audio: rehacer con otra semilla no sirve
PAUSA_FRASI, PAUSA_PARAGRAFI, BORDO, SEME = 0.30, 0.65, 0.20, 7
GIRI_SCENA = 3  # cuántas veces se rehace una escena entera que no cuadra
RISCALDA = {"it": "Una frase breve per scaldare il modello.", "es": "Una frase corta para calentar el modelo.", "en": "A short sentence to warm up."}
# Chatterbox: 0,4 de énfasis para sonar sobrio; cfg 0,3 (a 0 el italiano inventaba sonidos, prueba del 06/11)
PARAMETRI_CHATTERBOX = {"exaggeration": 0.4, "cfg_weight": 0.3}
ISTRUZIONE_QWEN = ("An adult male voice, calm, clear and warm, like a teacher explaining a topic to adult students. "
                   "Medium pace, steady and even intonation, neutral and sober delivery, no dramatic emphasis, no excitement.")
LOUDNORM = "loudnorm=I=-16:TP=-1.5:LRA=20"


def cartella_chatterbox() -> Path:
    from huggingface_hub import snapshot_download

    v3 = Path(snapshot_download(REPO["chatterbox"]))
    conds = Path(snapshot_download(CONDS_CHATTERBOX, allow_patterns=["conds.safetensors"])) / "conds.safetensors"
    dove = QUI / ".modelli" / "chatterbox-v3-voce-base"
    dove.mkdir(parents=True, exist_ok=True)
    for f in [*v3.iterdir(), conds]:
        if f.name.startswith("."):
            continue
        link = dove / f.name
        if link.is_symlink() or link.exists():
            link.unlink()
        link.symlink_to(f.resolve())
    return dove


MODELLI = QUI / ".modelli"


class VoceOnnx:
    """Supertonic 3 o Kokoro-82M con ONNX Runtime: funcionan en el procesador, también en un portátil Windows sin tarjeta gráfica."""

    def __init__(self, modello: str):
        self.modello = modello
        if modello == "supertonic":
            import os

            os.environ.setdefault("SUPERTONIC_CACHE_DIR", str(MODELLI / "supertonic"))
            from supertonic import TTS

            self.m = TTS(model=SUPERTONIC["modello"], auto_download=True)
            self.sample_rate = int(self.m.sample_rate)
            self.stili = {}
        else:
            from kokoro_onnx import Kokoro

            d = MODELLI / "kokoro-onnx"
            d.mkdir(parents=True, exist_ok=True)
            for nome, rel in KOKORO_FILE.items():
                if not (d / nome).exists():
                    import urllib.request

                    print(f"descargando {nome} (Kokoro-82M, Apache 2.0)…", flush=True)
                    urllib.request.urlretrieve(KOKORO_ONNX + rel, d / (nome + ".parziale"))
                    (d / (nome + ".parziale")).replace(d / nome)
            self.m = Kokoro(str(d / "kokoro-v1.0.onnx"), str(d / "voices-v1.0.bin"))
            self.sample_rate = 24000

    def parla(self, testo: str, voce: str, lingua: str) -> np.ndarray:
        if self.modello == "supertonic":
            if voce not in self.stili:
                self.stili[voce] = self.m.get_voice_style(voice_name=voce)
            wav, _ = self.m.synthesize(testo, voice_style=self.stili[voce], lang=LINGUA_ONNX["supertonic"][lingua],
                                       total_steps=SUPERTONIC["passi"], speed=VELOCITA["supertonic"][lingua])
            return np.asarray(wav, dtype=np.float32).reshape(-1)
        audio, sr = self.m.create(testo, voice=voce, speed=VELOCITA["kokoro-onnx"][lingua], lang=LINGUA_ONNX["kokoro-onnx"][lingua])
        self.sample_rate = int(sr)
        return np.asarray(audio, dtype=np.float32).reshape(-1)


def carica(modello: str):
    if modello in ONNX:
        return VoceOnnx(modello)
    from mlx_audio.tts.utils import load_model

    return load_model(cartella_chatterbox() if modello == "chatterbox" else REPO[modello])


def pezzi(testo: str, massimo: int) -> list[tuple[str, float]]:
    uscita: list[tuple[str, float]] = []
    for paragrafo in [p.strip() for p in re.split(r"\n\s*\n", testo.strip()) if p.strip()]:
        corrente = ""
        for frase in re.split(r"(?<=[.!?…])\s+", re.sub(r"\s+", " ", paragrafo)):
            if corrente and len(corrente) + 1 + len(frase) > massimo:
                uscita.append((corrente, PAUSA_FRASI))
                corrente = frase
            else:
                corrente = f"{corrente} {frase}".strip()
        if corrente:
            uscita.append((corrente, PAUSA_PARAGRAFI))
    if uscita:
        uscita[-1] = (uscita[-1][0], 0.0)
    return uscita


def rifila(audio: np.ndarray, sr: int, soglia_db: float = -45.0, margine: float = 0.08) -> np.ndarray:
    finestra = int(0.02 * sr)
    if len(audio) < finestra * 3:
        return audio
    rms = np.sqrt(np.convolve(audio**2, np.ones(finestra) / finestra, mode="same") + 1e-12)
    sopra = np.where(20 * np.log10(rms) > soglia_db)[0]
    if len(sopra) == 0:
        return audio
    m = int(margine * sr)
    return audio[max(0, sopra[0] - m): min(len(audio), sopra[-1] + m)]


def genera_pezzo(modello: str, m, voce: str, lingua: str, testo: str, seme: int) -> np.ndarray:
    np.random.seed(seme)
    if modello in ONNX:
        return rifila(m.parla(testo, voce, lingua), int(m.sample_rate))
    import mlx.core as mx

    mx.random.seed(seme)
    if modello == "kokoro":
        r = m.generate(text=testo, voice=voce, speed=1.0, lang_code=LINGUA["kokoro"][lingua])
    elif modello == "qwen":
        r = m.generate_voice_design(text=testo, instruct=ISTRUZIONE_QWEN, language=LINGUA["qwen"][lingua])
    else:
        r = m.generate(text=testo, lang_code=LINGUA["chatterbox"][lingua], verbose=False, **PARAMETRI_CHATTERBOX)
    return rifila(np.concatenate([np.array(x.audio, dtype=np.float32).reshape(-1) for x in r]), int(m.sample_rate))


# --- control de cada trozo con Whisper ---------------------------------------------------------------------------------------------
# Los números están en letras en el guion y Whisper los escribe en cifras: no cuentan ni en un lado ni en el otro.
MORFEMI = {
    "it": "zero un uno una due tre quattro cinque sei sette otto nove dieci undici dodici tredici quattordici quindici sedici diciassette "
          "diciotto diciannove vent venti trent trenta quarant quaranta cinquant cinquanta sessant sessanta settant settanta ottant ottanta "
          "novant novanta cent cento mille mila",
    "es": "cero un uno una dos tres cuatro cinco seis siete ocho nueve diez once doce trece catorce quince dieciseis diecisiete dieciocho "
          "diecinueve veinte veinti treinta cuarenta cincuenta sesenta setenta ochenta noventa cien ciento cientos doscientos trescientos "
          "cuatrocientos quinientos mil",
}


def norma(p: str) -> str:
    p = unicodedata.normalize("NFKD", p.lower())
    return "".join(c for c in p if c.isalnum())


def e_numero(p: str, lingua: str) -> bool:
    if not p or p.isdigit():
        return bool(p)
    m = MORFEMI.get(lingua, "").split()
    ok = [True] + [False] * len(p)
    for i in range(len(p)):
        if ok[i]:
            for x in m:
                if p.startswith(x, i):
                    ok[i + len(x)] = True
    return ok[-1]


def unisci(parole: list[str], altre: set) -> list[str]:
    """Une dos palabras seguidas cuando en el otro lado están escritas juntas (grafía de Whisper, no error de la voz)."""
    out, i = [], 0
    while i < len(parole):
        if i + 1 < len(parole) and parole[i] not in altre and parole[i] + parole[i + 1] in altre:
            out.append(parole[i] + parole[i + 1])
            i += 2
        else:
            out.append(parole[i])
            i += 1
    return out


def voto(atteso: str, sentito: list[str], lingua: str) -> tuple[float, list[str]]:
    """Cuánto cuadra el trozo escuchado con el texto: palabras iguales sobre el más largo de los dos (así cuentan también los sonidos
    inventados)."""
    a = [x for x in (norma(w) for w in atteso.split()) if x and not e_numero(x, lingua)]
    b = [x for x in (norma(w) for w in sentito) if x and not e_numero(x, lingua)]
    b = unisci(b, set(a))  # «chat GPT» escuchado en dos palabras vale como el «ChatGPT» del guion
    a = unisci(a, set(b))  # y «maxbid» escuchado en una, como «Max Bid»
    sm = SequenceMatcher(None, a, b, autojunk=False)
    uguali = sum(k.size for k in sm.get_matching_blocks())
    diversi = [f"{' '.join(a[i1:i2])} → {' '.join(b[j1:j2])}" for op, i1, i2, j1, j2 in sm.get_opcodes() if op != "equal"]
    return uguali / max(1, len(a), len(b)), diversi


def ascolta(w, audio: np.ndarray, sr: int, lingua: str) -> list[str]:
    from math import gcd

    from scipy.signal import resample_poly

    g = gcd(sr, 16000)
    a16 = audio if sr == 16000 else resample_poly(audio, 16000 // g, sr // g).astype(np.float32)
    segmenti, _ = w.transcribe(a16, language=lingua, beam_size=5, vad_filter=False, condition_on_previous_text=False)
    return " ".join(x.text for x in segmenti).split()


def mappa_pronuncia(lavoro: dict) -> dict:
    """La de la voz (PRONUNCIA_VOCE) más la del guion, que tiene prioridad."""
    return {**PRONUNCIA_VOCE.get(lavoro["modello"], {}).get(lavoro["lingua"], {}), **(lavoro.get("pronuncia") or {})}


def pronuncia(testo: str, mappa: dict) -> str:
    for parola, come in (mappa or {}).items():
        testo = re.sub(rf"(?<!\w){re.escape(parola)}(?!\w)", come, testo)
    return testo


def genera(modello: str, m, w, voce: str, lingua: str, testo: str, mappa: dict, soglia: float, tentativi: int, seme: int = SEME) -> tuple[np.ndarray, int, list]:
    """La escena trozo a trozo. Cada trozo se vuelve a escuchar con Whisper: por debajo del umbral se rehace con otra semilla (hasta
    `tentativi`) y se queda el mejor. El texto con la pronuncia va a la voz; el control se hace sobre el texto del guion."""
    sr = int(m.sample_rate)
    parti, rapporto = [np.zeros(int(BORDO * sr), dtype=np.float32)], []
    for i, (pezzo, pausa) in enumerate(pezzi(testo, PEZZO[modello])):
        migliore = None
        for k in range(1 if modello in DETERMINISTICI else tentativi):
            audio = genera_pezzo(modello, m, voce, lingua, pronuncia(pezzo, mappa), seme + 101 * k + i)
            v, diversi = voto(pezzo, ascolta(w, audio, sr, lingua), lingua) if w else (1.0, [])
            # demasiado largo para las palabras que tiene (sonidos inventados, pausas raras): cuenta como error
            if len(audio) / sr > 1.0 + len(pezzo.split()) / 1.6:
                v, diversi = v - 0.2, diversi + [f"demasiado largo: {len(audio) / sr:.1f} s"]
            if migliore is None or v > migliore[1]:
                migliore = (audio, v, diversi, k + 1)
            if v >= soglia:
                break
        audio, v, diversi, n = migliore
        rapporto.append({"pezzo": i, "voto": round(v, 3), "tentativi": n, "diversi": diversi})
        parti += [audio, np.zeros(int((pausa or BORDO) * sr), dtype=np.float32)]
    return np.concatenate(parti), sr, rapporto


def _ffmpeg(*a: str) -> str:
    return subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *a], capture_output=True, text=True, check=True).stderr


def _misura(stderr: str) -> dict:
    return json.loads(stderr[stderr.rfind("{"): stderr.rfind("}") + 1])


# Rotación de fase (4 pasa-todo): no cambia volumen ni timbre en una voz mono, pero baja la cresta 2-4 dB (prueba del 06/11)
FASE = "allpass=f=100:t=q:w=0.5,allpass=f=200:t=q:w=0.5,allpass=f=400:t=q:w=0.5,allpass=f=800:t=q:w=0.5"


def _misura_file(f: Path) -> dict:
    return _misura(_ffmpeg("-i", str(f), "-af", f"{LOUDNORM}:print_format=json", "-f", "null", "-"))


def normalizza(grezzo: Path, wav: Path, sr: int) -> str:
    """-16 LUFS de forma lineal (solo ganancia). Estas voces tienen picos altos respecto al volumen medio: primero la rotación de fase,
    luego, si aún hace falta, un limitador suave que quita solo los dB de más; nunca el modo «dynamic» de loudnorm, que comprime."""
    fase = grezzo.with_name("fase.wav")
    _ffmpeg("-y", "-i", str(grezzo), "-af", FASE, "-c:a", "pcm_f32le", str(fase))
    mis0, misf = _misura_file(grezzo), _misura_file(fase)
    cresta = lambda m: float(m["input_tp"]) - float(m["input_i"])  # noqa: E731
    if cresta(misf) >= cresta(mis0):
        fase, misf = grezzo, mis0
    riduzione, sorgente, mis = 0.0, fase, misf
    for _ in range(8):
        e = float(mis["input_tp"]) + (-16 - float(mis["input_i"])) + 1.5
        if e <= 0:
            break
        riduzione += e + 0.2
        limite = 10 ** ((float(misf["input_tp"]) - riduzione) / 20)
        sorgente = grezzo.with_name("limitato.wav")
        _ffmpeg("-y", "-i", str(fase), "-af", f"alimiter=limit={max(limite, 0.0625):.4f}:attack=5:release=80:level=0:latency=1",
                "-c:a", "pcm_f32le", str(sorgente))
        mis = _misura_file(sorgente)
    filtro = (f"{LOUDNORM}:measured_I={mis['input_i']}:measured_TP={mis['input_tp']}:measured_LRA={mis['input_lra']}"
              f":measured_thresh={mis['input_thresh']}:offset={mis['target_offset']}:linear=true:print_format=json")
    return _misura(_ffmpeg("-y", "-i", str(sorgente), "-af", filtro, "-ar", str(sr), "-c:a", "pcm_s16le", str(wav))).get("normalization_type", "")


def audio_16k(f: Path) -> np.ndarray:
    grezzo = subprocess.run(["ffmpeg", "-v", "error", "-i", str(f), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(grezzo, dtype=np.float32)


def impronta(lavoro: dict, testo: str) -> str:
    chiave = [lavoro["modello"], lavoro.get("voce"), lavoro["lingua"], pronuncia(testo, mappa_pronuncia(lavoro))]
    if lavoro["modello"] in VELOCITA:  # las voces ligeras se rehacen si cambia el ritmo (Chatterbox: huella de antes)
        chiave.append(VELOCITA[lavoro["modello"]].get(lavoro["lingua"], 1.0))
    chiave = json.dumps(chiave, ensure_ascii=False)
    return hashlib.sha1(chiave.encode("utf-8")).hexdigest()[:16]


def controlla(f: Path) -> None:
    """Solo la nueva escucha, para las voces hechas en otro sitio (ElevenLabs): nota de cada escena en voce/<id>.voce.json, sin rehacer nada."""
    from faster_whisper import WhisperModel

    lavoro = json.loads(f.read_text(encoding="utf-8"))
    lingua = lavoro["lingua"]
    w = WhisperModel(lavoro.get("whisper") or "medium", device="cpu", compute_type="int8")
    print("nueva escucha con Whisper (solo informe: no rehace nada):", flush=True)
    for s in lavoro["scene"]:
        segmenti, _ = w.transcribe(audio_16k(Path(s["wav"])), language=lingua, beam_size=5, vad_filter=False)
        v, diversi = voto(s["testo"], " ".join(x.text for x in segmenti).split(), lingua)
        meta_f = Path(s["wav"]).with_suffix(".voce.json")
        meta = json.loads(meta_f.read_text(encoding="utf-8")) if meta_f.exists() else {}
        meta.update({"voto_scena": round(v, 3), "diversi_scena": diversi})
        meta_f.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  {s['id']}: {v:.0%}" + (f" · {diversi[:3]}" if v < 0.9 else ""), flush=True)


def prepara(modelli: list[str], whisper: str) -> None:
    """Para la instalación: descarga los pesos de las voces y de Whisper y genera una frase de prueba, así la primera lección arranca enseguida."""
    from faster_whisper import WhisperModel

    t = time.time()
    WhisperModel(whisper, device="cpu", compute_type="int8")
    print(f"Whisper {whisper}: listo ({time.time() - t:.0f} s)", flush=True)
    for modello in modelli:
        t = time.time()
        m = carica(modello)
        voce = {"supertonic": "F1", "kokoro-onnx": "if_sara"}.get(modello, "base")
        audio = genera_pezzo(modello, m, voce, "it", RISCALDA["it"], SEME)
        print(f"{modello}: listo, frase de prueba de {len(audio) / m.sample_rate:.1f} s ({time.time() - t:.0f} s)", flush=True)


def main() -> None:
    if len(sys.argv) == 3 and sys.argv[1] == "controlla":
        return controlla(Path(sys.argv[2]))
    if len(sys.argv) >= 3 and sys.argv[1] == "prepara":  # prepara supertonic [kokoro-onnx] [--whisper small]
        args = sys.argv[2:]
        w = args[args.index("--whisper") + 1] if "--whisper" in args else "small"
        return prepara([a for a in args if a != "--whisper" and a != w], w)
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0 if sys.argv[1:] in (["-h"], ["--help"]) else 2)
    lavoro = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    modello, voce, lingua = lavoro["modello"], lavoro.get("voce") or "base", lavoro["lingua"]
    mappa, soglia, tentativi = mappa_pronuncia(lavoro), float(lavoro.get("soglia", 0.9)), int(lavoro.get("tentativi", 4))
    da_fare = []
    for s in lavoro["scene"]:
        meta = Path(s["wav"]).with_suffix(".voce.json")
        fatto = json.loads(meta.read_text(encoding="utf-8")) if meta.exists() else {}
        if fatto.get("impronta") == impronta(lavoro, s["testo"]) and Path(s["wav"]).exists() and Path(s["parole"]).exists():
            continue
        da_fare.append(s)
    print(f"voz: {modello} {voce} ({lingua}), {len(da_fare)} escenas por hacer de {len(lavoro['scene'])}", flush=True)
    if not da_fare:
        return
    from faster_whisper import WhisperModel

    w = WhisperModel(lavoro.get("whisper") or "medium", device="cpu", compute_type="int8")
    m = carica(modello)
    genera_pezzo(modello, m, voce, lingua, RISCALDA.get(lingua, RISCALDA["en"]), SEME)
    for s in da_fare:
        t = time.time()
        wav = Path(s["wav"])
        wav.parent.mkdir(parents=True, exist_ok=True)
        migliore = None
        for giro in range(1 if modello in DETERMINISTICI else GIRI_SCENA):
            # la escena entera se vuelve a escuchar: a veces los trozos pasan y la escena no (Whisper pierde el final, cambia una palabra)
            audio, sr, rapporto = genera(modello, m, w, voce, lingua, s["testo"], mappa, soglia, tentativi, int(lavoro.get("seme", SEME)) + 5000 * giro)
            with tempfile.TemporaryDirectory() as d:
                grezzo, uscita = Path(d) / "grezzo.wav", Path(d) / "voce.wav"
                wavfile.write(grezzo, sr, audio.astype(np.float32))
                tipo = normalizza(grezzo, uscita, sr)
                segmenti, _ = w.transcribe(audio_16k(uscita), language=lingua, beam_size=5, word_timestamps=True, vad_filter=False)
                parole = [{"w": p.word.strip(), "inizio": round(p.start, 3), "fine": round(p.end, 3)} for seg in segmenti for p in (seg.words or [])]
                v_scena, diversi = voto(s["testo"], [p["w"] for p in parole], lingua)
                if migliore is None or v_scena > migliore[0]:
                    migliore = (v_scena, diversi, uscita.read_bytes(), parole, audio, sr, rapporto, tipo, giro + 1)
            if v_scena >= soglia:
                break
            print(f"  {s['id']}: escena entera al {v_scena:.0%} ({diversi[:3]}), la rehago", flush=True)
        v_scena, diversi, dati, parole, audio, sr, rapporto, tipo, giri = migliore
        wav.write_bytes(dati)
        Path(s["parole"]).write_text(json.dumps(parole, ensure_ascii=False), encoding="utf-8")
        deboli = [r for r in rapporto if r["voto"] < soglia]
        wav.with_suffix(".voce.json").write_text(json.dumps(
            {"impronta": impronta(lavoro, s["testo"]), "modello": modello, "repo": REPO.get(modello, modello), "voce": voce, "lingua": lingua,
             "parametri": PARAMETRI_CHATTERBOX if modello == "chatterbox" else {**(SUPERTONIC if modello == "supertonic" else {}),
                                                                                   "velocita": VELOCITA[modello][lingua]} if modello in VELOCITA else {},
             "pronuncia": mappa, "soglia": soglia,
             "durata_s": round(len(audio) / sr, 1), "tempo_s": round(time.time() - t, 1), "loudnorm": tipo, "voto_scena": round(v_scena, 3),
             "diversi_scena": diversi, "giri": giri, "pezzi": rapporto}, ensure_ascii=False, indent=1), encoding="utf-8")
        rifatti = sum(r["tentativi"] - 1 for r in rapporto)
        print(f"  {s['id']}: {len(audio) / sr:.1f} s en {time.time() - t:.0f} s · escena {v_scena:.0%} · {len(rapporto)} trozos, {rifatti} rehechos"
              + (f" · bajo el umbral: {[(r['pezzo'], r['voto'], r['diversi'][:3]) for r in deboli]}" if deboli else ""), flush=True)


if __name__ == "__main__":
    main()

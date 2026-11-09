"""El estado de los cursos de Open Escool, para `/escool` sin palabras: qué hay, por dónde vas, qué queda por hacer.

    python strumenti/stato.py            texto para leer (el asistente lo resume en el idioma de quien usa Open Escool)
    python strumenti/stato.py --json     los mismos datos para un programa

Para cada curso: los idiomas de los vídeos, las etapas hechas, los días desde la última revisión de las fuentes (aviso pasado el
umbral de config.json → aggiornamento), las etapas por revisar, las etapas con dudas abiertas (señal de hueco: config.json →
buco) y las fichas que faltan. De las dudas solo cuenta cuántas hay: el texto de las notas se queda en utente/.
"""
import json
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RADICE))
sys.path.insert(0, str(RADICE / "strumenti"))
import accademia  # noqa: E402  (solo funciones: el servidor arranca solo con `python accademia.py`)
import comune  # noqa: E402
from comune import tr  # noqa: E402


def stato():
    corsi, gruppi = [], {}
    for c in accademia.elenco_percorsi():
        gruppi.setdefault(c["gruppo"], []).append(c)
    for g, versioni in gruppi.items():
        principale = next((v for v in versioni if v["slug"] == g), versioni[0])
        p = accademia.percorso(principale["slug"]) or {}
        tappe = p.get("tappe", [])
        corsi.append({
            "nome": g, "titolo": principale["titolo"],
            "lingue": sorted({v["slug"]: v.get("lingua_video") for v in versioni}.items()),
            "tappe": principale["tappe"], "tappe_fatte": principale["tappe_fatte"],
            "prossima": (principale.get("prossima") or {}).get("n"),
            "giorni_dal_controllo": p.get("giorni_dal_controllo"), "da_aggiornare": bool(p.get("avviso_aggiornamento")),
            "da_ricontrollare": [t["n"] for t in tappe if t.get("da_ricontrollare")],
            "dubbi": {t["n"]: t["dubbi_aperti"] for t in tappe if t.get("dubbi_aperti")},
            "da_rinforzare": [t["n"] for t in tappe if t.get("segnale_buco")],
            "schede_mancanti": {v["slug"]: v["schede_mancanti"] for v in versioni if v.get("schede_mancanti")},
            "ultimo_accesso": principale.get("ultimo_accesso"),
        })
    return {"config": (RADICE / "config.json").exists(), "corsi": corsi}


def testo(s):
    righe = [] if s["config"] else [tr("config.json manca: prima /escool install (poi customize).",
                                        "Falta config.json: primero /escool install (luego customize).",
                                        "config.json is missing: first /escool install (then customize).")]
    if not s["corsi"]:
        return "\n".join(righe + [tr("Nessun corso ancora. Consiglio: /escool create \"tema\".",
                                     "Aún no hay ningún curso. Consejo: /escool create \"tema\".",
                                     "No courses yet. Tip: /escool create \"topic\".")])
    consigli = []
    for c in s["corsi"]:
        lingue = ", ".join(f"{l or '?'} ({slug})" for slug, l in c["lingue"])
        r = [tr(f"- {c['titolo']} [{c['nome']}] · video in {lingue} · tappe fatte {c['tappe_fatte']}/{c['tappe']}",
                f"- {c['titolo']} [{c['nome']}] · vídeos en {lingue} · etapas hechas {c['tappe_fatte']}/{c['tappe']}",
                f"- {c['titolo']} [{c['nome']}] · videos in {lingue} · stages done {c['tappe_fatte']}/{c['tappe']}")]
        if c["prossima"]:
            r.append(tr(f"  prossima tappa da fare: la {c['prossima']}", f"  siguiente etapa por hacer: la {c['prossima']}",
                        f"  next stage to do: {c['prossima']}"))
        if c["giorni_dal_controllo"] is not None:
            g = c["giorni_dal_controllo"]
            oggi = tr("  fonti controllate oggi", "  fuentes revisadas hoy", "  sources checked today")
            fa = tr(f"  fonti controllate {g} giorn{'o' if g == 1 else 'i'} fa",
                    f"  fuentes revisadas hace {g} día{'' if g == 1 else 's'}",
                    f"  sources checked {g} day{'' if g == 1 else 's'} ago")
            aggiorna = tr(" → da aggiornare", " → por actualizar", " → needs updating")
            r.append((oggi if g == 0 else fa) + (aggiorna if c["da_aggiornare"] else ""))
        if c["da_ricontrollare"]:
            n = c["da_ricontrollare"]
            r.append(tr(f"  da ricontrollare: {'tappa' if len(n) == 1 else 'tappe'} {', '.join(map(str, n))}",
                        f"  por revisar: {'etapa' if len(n) == 1 else 'etapas'} {', '.join(map(str, n))}",
                        f"  to recheck: {'stage' if len(n) == 1 else 'stages'} {', '.join(map(str, n))}"))
        if c["dubbi"]:
            tappa = tr("tappa", "etapa", "stage")
            r.append(tr("  dubbi aperti: ", "  dudas abiertas: ", "  open doubts: ")
                     + ", ".join(f"{tappa} {n} ({k})" for n, k in c["dubbi"].items()))
        if c["schede_mancanti"]:
            r.append(tr("  schede ancora da fare: ", "  fichas que faltan: ", "  cards still to do: ")
                     + ", ".join(f"{k} ({v})" for k, v in c["schede_mancanti"].items()))
        righe += r
        if c["da_aggiornare"]:
            consigli.append(f"/escool update {c['nome']}")
        for n in c["da_rinforzare"]:
            consigli.append(f"/escool reinforce {c['nome']} {n}")
        for n in c["da_ricontrollare"]:
            consigli.append(f"/escool update {c['nome']} {n}")
    resto = tr("/escool create \"tema\" per un corso nuovo, o continua la prossima tappa",
               "/escool create \"tema\" para un curso nuevo, o sigue con la siguiente etapa",
               "/escool create \"topic\" for a new course, or go on with the next stage")
    righe.append(tr("Consiglio: ", "Consejo: ", "Tip: ") + (consigli[0] if consigli else resto))
    return "\n".join(righe)


if __name__ == "__main__":
    comune.aiuto(__doc__)
    s = stato()
    print(json.dumps(s, ensure_ascii=False, indent=1) if "--json" in sys.argv else testo(s))

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
    righe = [] if s["config"] else ["Falta config.json: primero /escool install (luego customize)."]
    if not s["corsi"]:
        return "\n".join(righe + ["Aún no hay ningún curso. Consejo: /escool create \"tema\"."])
    consigli = []
    for c in s["corsi"]:
        lingue = ", ".join(f"{l or '?'} ({slug})" for slug, l in c["lingue"])
        r = [f"- {c['titolo']} [{c['nome']}] · vídeos en {lingue} · etapas hechas {c['tappe_fatte']}/{c['tappe']}"]
        if c["prossima"]:
            r.append(f"  siguiente etapa por hacer: la {c['prossima']}")
        if c["giorni_dal_controllo"] is not None:
            g = c["giorni_dal_controllo"]
            r.append(("  fuentes revisadas hoy" if g == 0 else f"  fuentes revisadas hace {g} día{'' if g == 1 else 's'}") + (" → por actualizar" if c["da_aggiornare"] else ""))
        if c["da_ricontrollare"]:
            n = c["da_ricontrollare"]
            r.append(f"  por revisar: {'etapa' if len(n) == 1 else 'etapas'} {', '.join(map(str, n))}")
        if c["dubbi"]:
            r.append("  dudas abiertas: " + ", ".join(f"etapa {n} ({k})" for n, k in c["dubbi"].items()))
        if c["schede_mancanti"]:
            r.append("  fichas que faltan: " + ", ".join(f"{k} ({v})" for k, v in c["schede_mancanti"].items()))
        righe += r
        if c["da_aggiornare"]:
            consigli.append(f"/escool update {c['nome']}")
        for n in c["da_rinforzare"]:
            consigli.append(f"/escool reinforce {c['nome']} {n}")
        for n in c["da_ricontrollare"]:
            consigli.append(f"/escool update {c['nome']} {n}")
    righe.append("Consejo: " + (consigli[0] if consigli else "/escool create \"tema\" para un curso nuevo, o sigue con la siguiente etapa"))
    return "\n".join(righe)


if __name__ == "__main__":
    comune.aiuto(__doc__)
    s = stato()
    print(json.dumps(s, ensure_ascii=False, indent=1) if "--json" in sys.argv else testo(s))

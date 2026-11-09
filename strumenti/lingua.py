"""La misma ruta con los vídeos en otro idioma: una ruta nueva con el mismo mapa (ya aprobado).

  python strumenti/lingua.py <ruta> <it|es|en>    -> percorsi/<ruta>-<idioma>/

Copia el mapa (con la nueva `lingua_video`), las fuentes y los resultados de YouTube ya encontrados, y las fichas de los vídeos
hablados en ese idioma: las fichas dependen solo del vídeo y del mapa, así que también valen aquí y no gastan cuota de Gemini.
Etapas, resúmenes y chat se quedan en el idioma de quien aprende (`lingua` del mapa). Después: `video.py lista` (o `cerca`, si
las búsquedas son antiguas o hay pocos vídeos en ese idioma), `schede.py`, `costruisci.py`.
"""
import shutil
import sys
from datetime import date

from comune import PERCORSI, cartella, leggi, scrivi, aiuto

NOMI = {"it": "italiano", "es": "español", "en": "inglés"}


def main(slug, lingua):
    if lingua not in NOMI:
        sys.exit("idioma: it, es o en")
    da = cartella(slug)
    m = leggi(da / "lavoro" / "mappa.json") or sys.exit(f"falta percorsi/{slug}/lavoro/mappa.json")
    if not m.get("approvata"):
        sys.exit("el mapa de partida no está aprobado: primero la aprobación")
    base = m.get("da") or slug  # desde chatgpt-ads-es se vuelve siempre al nombre de partida: chatgpt-ads-en, no chatgpt-ads-es-en
    mb = leggi(PERCORSI / base / "lavoro" / "mappa.json", {})
    if (mb.get("lingua_video") or mb.get("lingua")) == lingua:
        sys.exit(f"percorsi/{base} ya tiene los vídeos en {NOMI[lingua]}")
    nuovo = f"{base}-{lingua}"
    a = PERCORSI / nuovo
    if (a / "lavoro" / "mappa.json").exists():
        sys.exit(f"ya existe percorsi/{nuovo}: actualízala con video.py / schede.py / costruisci.py")
    cartella(nuovo)
    if not any(lingua in (t.get("ricerche_youtube") or {}) for t in m["tappe"]):
        print(f"atención: el mapa no tiene búsquedas de YouTube en {NOMI[lingua]}: añádelas a las etapas antes de `video.py cerca`")
    scrivi(a / "lavoro" / "mappa.json", {**m, "lingua_video": lingua, "da": base, "copiata": date.today().isoformat()})
    for sotto in ("fonti",):
        if (da / "lavoro" / sotto).exists():
            shutil.copytree(da / "lavoro" / sotto, a / "lavoro" / sotto, dirs_exist_ok=True)
    yt_da, yt_a = da / "lavoro" / "youtube", a / "lavoro" / "youtube"
    pert = []
    if yt_da.exists():
        yt_a.mkdir(parents=True, exist_ok=True)
        for nome in ("grezzo_video.json", "grezzo_canali.json", "candidati.json", "metadati.json"):  # copy2 conserva la fecha
            if (yt_da / nome).exists():
                shutil.copy2(yt_da / nome, yt_a / nome)
        pert = [r for r in leggi(yt_da / "pertinenti.json", []) if not r.get("lingua_audio") or r["lingua_audio"] == lingua]
        scrivi(yt_a / "pertinenti.json", pert)
    schede = 0
    for f in sorted((da / "schede").glob("*.json")) if (da / "schede").exists() else []:
        s = leggi(f, {})
        if (s.get("lingua_parlata") or "")[:2] == lingua and not s.get("errore_json"):
            (a / "schede").mkdir(exist_ok=True)
            shutil.copy2(f, a / "schede" / f.name)
            schede += 1
    print(f"percorsi/{nuovo}: mapa copiado (vídeos en {NOMI[lingua]}), {len(pert)} vídeos pertinentes ya encontrados, "
          f"{schede} fichas ya hechas reutilizadas")
    print(f"después: python strumenti/video.py lista {nuovo} · python strumenti/schede.py {nuovo} · python strumenti/costruisci.py {nuovo}")


if __name__ == "__main__":
    aiuto(__doc__)
    main(sys.argv[1], sys.argv[2]) if len(sys.argv) == 3 else sys.exit(__doc__)

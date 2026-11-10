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

from comune import PERCORSI, cartella, leggi, scrivi, aiuto, tr

NOMI = {"it": "italiano", "es": "español", "en": "inglés"}
NOMI_IT = {"it": "italiano", "es": "spagnolo", "en": "inglese"}  # el nombre del idioma en los mensajes en italiano e inglés
NOMI_EN = {"it": "Italian", "es": "Spanish", "en": "English"}


def main(slug, lingua):
    if lingua not in NOMI:
        sys.exit(tr("lingua: it, es o en", "idioma: it, es o en", "language: it, es or en"))
    nl = tr(NOMI_IT[lingua], NOMI[lingua], NOMI_EN[lingua])
    da = cartella(slug)
    m = leggi(da / "lavoro" / "mappa.json") or sys.exit(tr(f"manca percorsi/{slug}/lavoro/mappa.json",
                                                           f"falta percorsi/{slug}/lavoro/mappa.json",
                                                           f"percorsi/{slug}/lavoro/mappa.json is missing"))
    if not m.get("approvata"):
        sys.exit(tr("la mappa di partenza non è approvata: prima l'approvazione",
                    "el mapa de partida no está aprobado: primero la aprobación",
                    "the starting map is not approved: approve it first"))
    base = m.get("da") or slug  # desde chatgpt-ads-es se vuelve siempre al nombre de partida: chatgpt-ads-en, no chatgpt-ads-es-en
    mb = leggi(PERCORSI / base / "lavoro" / "mappa.json", {})
    if (mb.get("lingua_video") or mb.get("lingua")) == lingua:
        sys.exit(tr(f"percorsi/{base} ha già i video in {nl}", f"percorsi/{base} ya tiene los vídeos en {nl}",
                    f"percorsi/{base} already has the videos in {nl}"))
    nuovo = f"{base}-{lingua}"
    a = PERCORSI / nuovo
    if (a / "lavoro" / "mappa.json").exists():
        sys.exit(tr(f"esiste già percorsi/{nuovo}: aggiornalo con video.py / schede.py / costruisci.py",
                    f"ya existe percorsi/{nuovo}: actualízala con video.py / schede.py / costruisci.py",
                    f"percorsi/{nuovo} already exists: update it with video.py / schede.py / costruisci.py"))
    cartella(nuovo)
    if not any(lingua in (t.get("ricerche_youtube") or {}) for t in m["tappe"]):
        print(tr(f"attenzione: la mappa non ha ricerche YouTube in {nl}: aggiungile alle tappe prima di `video.py cerca`",
                 f"atención: el mapa no tiene búsquedas de YouTube en {nl}: añádelas a las etapas antes de `video.py cerca`",
                 f"warning: the map has no YouTube searches in {nl}: add them to the stages before `video.py cerca`"))
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
    print(tr(f"percorsi/{nuovo}: mappa copiata (video in {nl}), {len(pert)} video pertinenti già trovati, "
             f"{schede} schede già fatte riusate",
             f"percorsi/{nuovo}: mapa copiado (vídeos en {nl}), {len(pert)} vídeos pertinentes ya encontrados, "
             f"{schede} fichas ya hechas reutilizadas",
             f"percorsi/{nuovo}: map copied (videos in {nl}), {len(pert)} relevant videos already found, "
             f"{schede} cards already done reused"))
    paese = m.get("paese") or "Italia"  # las fichas escriben «per_chi_impara» para este país (10/11: el curso español hablaba a Italia)
    print(tr(f"paese di chi impara: {paese}. Se il percorso in {nl} è per un altro pubblico, cambia «paese» nella mappa e "
             f"riscrivi avvisi e concetti legati al paese (valuta, disponibilità, leggi) prima delle schede nuove; le schede "
             f"riusate parlano ancora a chi impara da {paese}",
             f"país de quien aprende: {paese}. Si la ruta en {nl} es para otro público, cambia «paese» en el mapa y reescribe "
             f"los avisos y conceptos ligados al país (moneda, disponibilidad, leyes) antes de las fichas nuevas; las fichas "
             f"reutilizadas siguen hablando a quien aprende desde {paese}",
             f"learner's country: {paese}. If the path in {nl} is for another audience, change «paese» in the map and rewrite "
             f"the country-bound warnings and concepts (currency, availability, laws) before the new cards; the reused cards "
             f"still speak to learners in {paese}"))
    comandi = (f"python strumenti/video.py lista {nuovo} · python strumenti/schede.py {nuovo} · "
               f"python strumenti/costruisci.py {nuovo}")
    print(tr(f"poi: {comandi}", f"después: {comandi}", f"next: {comandi}"))


if __name__ == "__main__":
    aiuto(__doc__)
    main(sys.argv[1], sys.argv[2]) if len(sys.argv) == 3 else sys.exit(__doc__)

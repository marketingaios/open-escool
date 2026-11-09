"""Vídeos candidatos para las etapas de un mapa, solo con la API oficial de YouTube (Data API v3, gratuita).

  python strumenti/video.py cerca <ruta> [--tappe 3,5]  búsquedas del mapa -> lavoro/youtube/candidati.json y pertinenti.json
                                                       (con --tappe rehace solo esas y mantiene el resto)
  python strumenti/video.py lista <ruta> [--minuti 450]  propone los vídeos que verá Gemini -> lavoro/youtube/lista.json

Nada de acceso a youtube.com ni descargas (las condiciones de uso de YouTube lo prohíben): solo la API y el reproductor integrado.
Cuota: search.list 100 llamadas al día (cupo propio); videos.list y channels.list 1 unidad cada 50 vídeos.
El mapa (lavoro/mappa.json) da para cada etapa `ricerche_youtube` {idioma: [frases]} y `valido_da_ricerca` o `valido_da`;
arriba `parole_titolo` (grupos de palabras: el título debe contener al menos una de cada grupo), `lingua_video` (uno por ruta:
it, es o en; solo se buscan las frases de ese idioma), `durata_video_min`.
"""
import json
import math
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

import metadati
from comune import cartella, chiave, leggi, lingue_video, scrivi, secondi, aiuto, tr

API = "https://www.googleapis.com/youtube/v3/"


def chiama(metodo, **p):
    p["key"] = chiave("YOUTUBE_API_KEY")
    try:
        with urllib.request.urlopen(API + metodo + "?" + urllib.parse.urlencode(p), timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        corpo = e.read().decode("utf-8", "replace")
        try:
            msg = json.loads(corpo)["error"]["message"]
        except (ValueError, KeyError):
            msg = corpo[:300]
        sys.exit(f"YouTube {metodo}: HTTP {e.code}: {msg}")


def cerca_ids(q, lingua, dopo=None, n=25):
    p = dict(part="snippet", q=q, type="video", maxResults=n, relevanceLanguage=lingua, safeSearch="none")
    if dopo:
        p["publishedAfter"] = f"{dopo}T00:00:00Z"
    return [i["id"]["videoId"] for i in chiama("search", **p).get("items", [])]


def dettagli(ids):
    video, canali = {}, {}
    for i in range(0, len(ids), 50):
        for v in chiama("videos", part="snippet,contentDetails,statistics,status", id=",".join(ids[i:i + 50])).get("items", []):
            video[v["id"]] = v
    cids = sorted({v["snippet"]["channelId"] for v in video.values()})
    for i in range(0, len(cids), 50):
        for c in chiama("channels", part="snippet,statistics", id=",".join(cids[i:i + 50])).get("items", []):
            canali[c["id"]] = c
    return video, canali


def riga(v, canali):
    s, st, cd = v["snippet"], v.get("statistics", {}), v["contentDetails"]
    c = canali.get(s["channelId"], {})
    giorni = (datetime.now(timezone.utc) - datetime.fromisoformat(s["publishedAt"].replace("Z", "+00:00"))).days
    viste, like = int(st.get("viewCount", 0)), int(st.get("likeCount", 0))
    return {"id": v["id"], "url": f"https://www.youtube.com/watch?v={v['id']}", "titolo": s["title"], "canale": s["channelTitle"],
            "canale_id": s["channelId"], "iscritti": int(c.get("statistics", {}).get("subscriberCount", 0) or 0),
            "pubblicato": s["publishedAt"][:10], "giorni": giorni, "durata_s": secondi(cd.get("duration")) or 0,
            "viste": viste, "like": like, "viste_al_giorno": round(viste / max(giorni, 1), 1),
            "lingua_audio": (s.get("defaultAudioLanguage") or s.get("defaultLanguage") or "")[:2],
            "sottotitoli_caricati": cd.get("caption") == "true", "incorporabile": v.get("status", {}).get("embeddable", False),
            "copertina": f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg", "descrizione": s.get("description", "")[:600]}


def punteggio(c):
    """Solo un filtro previo con los números públicos: la elección de verdad la hace la ficha de Gemini."""
    if c["durata_s"] < 180 or c["durata_s"] > 3 * 3600 or not c["incorporabile"]:
        return -1
    return round(math.log10(c["viste"] + 10) + 0.5 * math.log10(c["iscritti"] + 10) + 0.3 * math.log10(c["viste_al_giorno"] + 1)
                 + (0.5 if c["like"] and c["viste"] and c["like"] / c["viste"] > 0.02 else 0), 2)


def piano(s):
    return "".join(ch for ch in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(ch) != "Mn")


def pertinente(c, m):
    gruppi = m.get("parole_titolo") or []
    titolo = piano(c["titolo"] + " " + c["descrizione"][:200])
    if any(not any(piano(p) in titolo for p in g) for g in gruppi):
        return False
    lingue = lingue_video(m)
    lingua = c.get("lingua_audio") or ""
    if lingue and lingua and lingua not in lingue:
        return False
    lo, hi = m.get("durata_video_min", [5, 60])
    return lo * 60 <= c["durata_s"] <= hi * 60


def cerca(slug, solo=None):
    d = cartella(slug)
    m = leggi(d / "lavoro" / "mappa.json") or sys.exit(tr("manca lavoro/mappa.json: prima la mappa, approvata",
                                                           "falta lavoro/mappa.json: primero el mapa, aprobado",
                                                           "lavoro/mappa.json is missing: first the map, approved"))
    if not m.get("approvata"):
        sys.exit(tr("la mappa non è ancora approvata: mostrala e chiedi il sì prima di cercare i video",
                    "el mapa aún no está aprobado: enséñalo y pide el sí antes de buscar los vídeos",
                    "the map is not approved yet: show it and ask for a yes before searching for videos"))
    out = d / "lavoro" / "youtube"
    lingue = lingue_video(m)
    per_tappa, n_ricerche = {}, 0
    for t in m["tappe"]:
        if solo and t["n"] not in solo:
            continue
        ids_t = []
        for lingua, frasi in t["ricerche_youtube"].items():
            if lingue and lingua not in lingue:
                continue
            for q in frasi:
                ids = cerca_ids(q, lingua, dopo=t.get("valido_da_ricerca") or t.get("valido_da"))
                n_ricerche += 1
                ids_t += [i for i in ids if i not in ids_t]
        per_tappa[t["n"]] = ids_t
    tutti = sorted({i for v in per_tappa.values() for i in v})
    video, canali = dettagli(tutti)
    metadati.salva(out.parents[1], video.values())  # título, canal, fecha y duración: duran 30 días (strumenti/metadati.py)
    vecchi_c = leggi(out / "candidati.json", {}) if solo else {}
    vecchi_p = leggi(out / "pertinenti.json", []) if solo else []
    video = {**(leggi(out / "grezzo_video.json", {}) if solo else {}), **video}
    canali = {**(leggi(out / "grezzo_canali.json", {}) if solo else {}), **canali}
    scrivi(out / "grezzo_video.json", video)
    scrivi(out / "grezzo_canali.json", canali)
    cand = {"creato": datetime.now(timezone.utc).isoformat(timespec="seconds"), "ricerche": n_ricerche,
            "tappe": {k: v for k, v in vecchi_c.get("tappe", {}).items() if int(k) not in (solo or [])}}
    pert = {}
    for r in vecchi_p:  # las etapas que no se rehacen se quedan como estaban
        resto = [n for n in r["tappe"] if n not in (solo or [])]
        if resto:
            pert[r["id"]] = {**r, "tappe": resto}
    for n, ids in per_tappa.items():
        righe = [riga(video[i], canali) for i in ids if i in video]
        for r in righe:
            r["punteggio"] = punteggio(r)
        righe = sorted([r for r in righe if r["punteggio"] >= 0], key=lambda r: -r["punteggio"])
        cand["tappe"][str(n)] = righe
        for r in righe:
            if pertinente(r, m):
                voce = pert.setdefault(r["id"], {**r, "tappe": []})
                if n not in voce["tappe"]:
                    voce["tappe"].append(n)
    scrivi(out / "candidati.json", cand)
    scrivi(out / "pertinenti.json", sorted(pert.values(), key=lambda r: -r["punteggio"]))
    n_tutti, n_pert = len(tutti), len(pert)
    print(tr(f"{n_ricerche} ricerche, {n_tutti} video unici, {n_pert} pertinenti (titolo, lingua, durata)",
             f"{n_ricerche} búsquedas, {n_tutti} vídeos únicos, {n_pert} pertinentes (título, idioma, duración)",
             f"{n_ricerche} searches, {n_tutti} unique videos, {n_pert} relevant (title, language, length)"))
    for n in per_tappa:
        top = [r for r in pert.values() if n in r["tappe"]][:5]
        print(tr(f"tappa {n}: ", f"etapa {n}: ", f"stage {n}: ")
              + " | ".join(f"{r['canale'][:18]} {r['durata_s'] // 60}′ {r['lingua_audio'] or '?'}" for r in top))


def lista(slug, minuti=450):
    """Para cada etapa los mejores por puntuación (+1 si están en el idioma de quien aprende), sin repetidos, hasta el tope
    de minutos. Es solo una propuesta con los números públicos: el asistente la revisa y quita los vídeos que no son del tema
    antes de las fichas, apuntándolos en lavoro/youtube/tolti_a_mano.json ([{"id", "titolo", "perche"}]): así no vuelven en
    la vuelta siguiente."""
    d = cartella(slug)
    m = leggi(d / "lavoro" / "mappa.json") or sys.exit(tr("manca lavoro/mappa.json: prima la mappa, approvata",
                                                           "falta lavoro/mappa.json: primero el mapa, aprobado",
                                                           "lavoro/mappa.json is missing: first the map, approved"))
    pert = leggi(d / "lavoro" / "youtube" / "pertinenti.json") or sys.exit(tr("prima `cerca`", "primero `cerca`",
                                                                              "run `cerca` first"))
    lingua = m.get("lingua_video") or m.get("lingua", "it")
    if m.get("lingua_video"):  # audio en otro idioma: fuera (si YouTube no lo dice, se queda: lo dirá la ficha)
        pert = [r for r in pert if not r.get("lingua_audio") or r["lingua_audio"] == lingua]
    tolti = {v["id"] for v in leggi(d / "lavoro" / "youtube" / "tolti_a_mano.json", [])}  # fuera del tema, quitados al revisar
    pert = [r for r in pert if r["id"] not in tolti]
    scelti, tot, giro = [], 0, 0
    while tot < minuti * 60 and giro < 6:
        aggiunti = 0
        for t in m["tappe"]:
            cand = [r for r in pert if t["n"] in r["tappe"] and r["id"] not in {s["id"] for s in scelti}]
            cand.sort(key=lambda r: -(r["punteggio"] + (1.0 if r["lingua_audio"] == lingua else 0)))
            if cand and tot + cand[0]["durata_s"] <= minuti * 60:
                scelti.append({k: cand[0][k] for k in ("id", "titolo", "canale", "pubblicato", "durata_s", "lingua_audio", "tappe")})
                tot += cand[0]["durata_s"]
                aggiunti += 1
        giro += 1
        if not aggiunti:
            break
    scrivi(d / "lavoro" / "youtube" / "lista.json", scelti)
    n_sc, min_tot = len(scelti), tot // 60
    print(tr(f"{n_sc} video, {min_tot} minuti (tetto {minuti}): lavoro/youtube/lista.json, modificabile a mano",
             f"{n_sc} vídeos, {min_tot} minutos (tope {minuti}): lavoro/youtube/lista.json, se puede cambiar a mano",
             f"{n_sc} videos, {min_tot} minutes (cap {minuti}): lavoro/youtube/lista.json, can be edited by hand"))
    parola_tappe = tr("tappe", "etapas", "stages")
    for s in scelti:
        print(f"  {s['id']}  {s['canale'][:20]:20} {s['durata_s'] // 60:>3}′ {s['lingua_audio'] or '?':>2} "
              f"{parola_tappe} {s['tappe']} · {s['titolo'][:60]}")


if __name__ == "__main__":
    aiuto(__doc__)
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == "cerca":
        cerca(a[1], [int(x) for x in a[a.index("--tappe") + 1].split(",")] if "--tappe" in a else None)
    elif len(a) >= 2 and a[0] == "lista":
        lista(a[1], int(a[a.index("--minuti") + 1]) if "--minuti" in a else 450)
    else:
        sys.exit(__doc__)

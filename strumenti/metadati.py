"""Los datos de YouTube de los vídeos (título, canal, fecha, duración, descripción): están aquí, no en los cursos.

Las normas para desarrolladores de YouTube (III.E.4.d, leídas el 09/11/2026: developers.google.com/youtube/terms/developer-policies)
permiten guardar los datos sacados de la API como mucho 30 días: después hay que actualizarlos o borrarlos. Por eso `percorso.json`
y las fichas solo tienen el ID del vídeo y los textos nuestros (fragmento elegido, resumen, puntos, avisos): un curso se comparte
o se publica tal cual. Los datos de la API están en `percorsi/<ruta>/lavoro/youtube/metadati.json`, con la fecha de lectura de
cada vídeo. La plataforma los renueva sola a los 25 días con la clave de quien la usa (videos.list: 1 unidad cada 50 vídeos) y no
usa los que pasan de 30. Sin clave se ven la miniatura (sacada del ID) y un título nuestro; el reproductor integrado muestra los
reales.

    python strumenti/metadati.py <ruta>            separa los datos de YouTube de un curso antiguo, renueva los que
                                                   tienen 25 días o más (hace falta YOUTUBE_API_KEY) y limpia los archivos
                                                   de trabajo con datos de la API de más de 30 días
    python strumenti/metadati.py <ruta> --forza    los renueva todos ahora

`lavoro/youtube/` se queda en el ordenador: no entra en los zip de los cursos ni en el repositorio.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime
from pathlib import Path

from comune import chiave, leggi, secondi

CAMPI = ("titolo", "canale", "pubblicato", "durata_s", "lingua_audio", "descrizione")
VALIDI = 30   # días: pasado este plazo, los datos de la API ya no se usan y se borran
RINNOVA = 25  # días: desde aquí se renuevan, con unos días de margen
API = "https://www.googleapis.com/youtube/v3/videos"
# archivos de trabajo hechos solo de datos de la API: pasados 30 días se borran (`video.py cerca` los rehace cuando hacen falta)
SOLO_API = ("grezzo_video.json", "grezzo_canali.json", "candidati.json", "pertinenti.json")
# listas elegidas por nosotros pero con títulos y números de la API: pasados 30 días solo quedan las claves nuestras
RIDUCI = {"lista.json": ("id", "tappe"), "tolti_a_mano.json": ("id", "perche")}
NOTA = ("Datos de la API de YouTube, leídos con la clave de quien usa Open Escool. Duran como mucho 30 días (normas para "
        "desarrolladores de YouTube III.E.4): la plataforma los renueva sola. No se comparten ni se publican.")


def file(d):
    return Path(d) / "lavoro" / "youtube" / "metadati.json"


def eta(x, oggi=None):
    try:
        return ((oggi or date.today()) - date.fromisoformat(x["letto"][:10])).days
    except (KeyError, TypeError, ValueError):
        return None


def tutti(d):
    return (leggi(file(d), {}) or {}).get("video", {})


def validi(d, oggi=None):
    """id → datos, solo los leídos hace menos de 30 días."""
    return {k: v for k, v in tutti(d).items() if (e := eta(v, oggi)) is not None and e < VALIDI}


def da_api(v):
    """Un elemento de videos.list (part snippet y contentDetails) → los campos que usa Open Escool."""
    sn = v.get("snippet", {})
    return {"titolo": sn.get("title", ""), "canale": sn.get("channelTitle", ""), "pubblicato": (sn.get("publishedAt") or "")[:10],
            "durata_s": secondi(v.get("contentDetails", {}).get("duration")),
            "lingua_audio": (sn.get("defaultAudioLanguage") or "")[:2], "descrizione": (sn.get("description") or "")[:600]}


def scrivi_tutti(d, video, oggi=None):
    """Escribe quitando los datos caducados. Escritura atómica: el servidor puede leer mientras otro proceso renueva."""
    video = {k: v for k, v in video.items() if (e := eta(v, oggi)) is not None and e < VALIDI}
    f = file(d)
    f.parent.mkdir(parents=True, exist_ok=True)
    tmp = f.with_name(f".{f.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps({"nota": NOTA, "video": video}, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, f)
    return video


def salva(d, elementi, oggi=None):
    """Añade o renueva los vídeos leídos ahora de la API (elementos de videos.list)."""
    oggi = oggi or date.today()
    video = tutti(d)
    for v in elementi:
        video[v["id"]] = {**da_api(v), "letto": oggi.isoformat()}
    return scrivi_tutti(d, video, oggi)


def ids_usati(d):
    """Los vídeos de YouTube del curso: los de percorso.json, los que tienen ficha y los de la lista."""
    d = Path(d)
    p = leggi(d / "percorso.json", {}) or {}
    ids = [v["id"] for t in p.get("tappe", []) for v in t.get("video", []) if v.get("tipo") != "lezione" and v.get("id")]
    ids += sorted(f.stem for f in (d / "schede").glob("*.json")) if (d / "schede").exists() else []
    ids += [v["id"] for v in leggi(d / "lavoro" / "youtube" / "lista.json", []) or [] if v.get("id")]
    return list(dict.fromkeys(ids))


def da_rinnovare(d, ids=None, forza=False, oggi=None):
    v = tutti(d)
    ids = ids_usati(d) if ids is None else ids
    def vecchio(i):
        e = eta(v[i], oggi) if i in v else None
        return e is None or e >= RINNOVA
    return [i for i in ids if forza or vecchio(i)]


def rinnova(d, chiave_api, ids=None, forza=False, timeout=20):
    """Vuelve a leer de la API los vídeos sin datos o con 25 días o más. Los vídeos que la API ya no devuelve (borrados o privados)
    quedan marcados como «sparito», así la página puede decirlo. Devuelve (renovados, desaparecidos); errores de red o de cuota:
    excepción."""
    oggi = date.today()
    fare = da_rinnovare(d, ids, forza, oggi)
    video, presi = tutti(d), []
    for i in range(0, len(fare), 50):
        pezzo = fare[i:i + 50]
        q = urllib.parse.urlencode({"part": "snippet,contentDetails", "id": ",".join(pezzo), "key": chiave_api, "maxResults": 50})
        with urllib.request.urlopen(f"{API}?{q}", timeout=timeout) as r:
            presi += json.load(r).get("items", [])
    trovati = {v["id"] for v in presi}
    for v in presi:
        video[v["id"]] = {**da_api(v), "letto": oggi.isoformat()}
    spariti = [i for i in fare if i not in trovati]
    for i in spariti:
        video[i] = {"sparito": True, "letto": oggi.isoformat()}
    scrivi_tutti(d, video, oggi)
    return len(trovati), len(spariti)


def separa(d):
    """Cursos hechos antes del 09/11/2026: quita título, canal, fecha, duración, descripción y miniatura de percorso.json y la fecha
    de las fichas, y los pone en metadati.json con la fecha en que se leyeron (la de los archivos en bruto). Devuelve los vídeos
    movidos."""
    d = Path(d)
    fp = d / "percorso.json"
    p = leggi(fp, {}) or {}
    grezzo = d / "lavoro" / "youtube" / "grezzo_video.json"
    letto = (date.fromtimestamp(grezzo.stat().st_mtime) if grezzo.exists()
             else date.fromisoformat((p.get("controllato") or date.today().isoformat())[:10]))
    video, spostati = tutti(d), 0
    if grezzo.exists():  # los datos completos de la API (con el idioma del audio), con su fecha real
        for vid, g in (leggi(grezzo, {}) or {}).items():
            if vid not in video and isinstance(g, dict) and g.get("snippet"):
                video[vid] = {**da_api({"id": vid, **g}), "letto": letto.isoformat()}
    for t in p.get("tappe", []):
        for v in t.get("video", []):
            if v.get("tipo") == "lezione" or not any(k in v for k in (*CAMPI, "copertina")):
                continue
            if v["id"] not in video and v.get("titolo") and v.get("titolo") != v["id"]:
                video[v["id"]] = {**{k: v.get(k) for k in CAMPI if k != "lingua_audio"}, "lingua_audio": "", "letto": letto.isoformat()}
            for k in (*CAMPI, "copertina"):
                if k != "lingua_audio":
                    v.pop(k, None)
            spostati += 1
    for f in sorted((d / "schede").glob("*.json")) if (d / "schede").exists() else []:
        s = leggi(f)
        if isinstance(s, dict) and "pubblicato" in s:
            vid = s.get("video") or f.stem
            if s.get("pubblicato") and vid in video and not video[vid].get("pubblicato"):
                video[vid]["pubblicato"] = s["pubblicato"]
            elif s.get("pubblicato") and vid not in video:
                video[vid] = {"pubblicato": s["pubblicato"], "letto": date.fromtimestamp(f.stat().st_mtime).isoformat()}
            s.pop("pubblicato")
            f.write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")
    if spostati:
        fp.write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8")
    scrivi_tutti(d, video)
    return spostati


def pulisci(d, oggi=None):
    """Borra los archivos de trabajo hechos solo de datos de la API con más de 30 días y reduce las listas a las claves nuestras."""
    oggi = oggi or date.today()
    yt, fatti = Path(d) / "lavoro" / "youtube", []
    for nome in SOLO_API:
        f = yt / nome
        if f.exists() and (oggi - date.fromtimestamp(f.stat().st_mtime)).days >= VALIDI:
            f.unlink()
            fatti.append(nome)
    for nome, chiavi in RIDUCI.items():
        f = yt / nome
        if f.exists() and (oggi - date.fromtimestamp(f.stat().st_mtime)).days >= VALIDI:
            righe = leggi(f, []) or []
            if any(set(r) - set(chiavi) for r in righe if isinstance(r, dict)):
                f.write_text(json.dumps([{k: r[k] for k in chiavi if k in r} for r in righe if isinstance(r, dict)],
                                        ensure_ascii=False, indent=1), encoding="utf-8")
                fatti.append(nome + " (ridotto)")
    scelta = Path(d) / "lavoro" / "scelta.md"  # tabla con los títulos: la rehace costruisci.py
    if scelta.exists() and (oggi - date.fromtimestamp(scelta.stat().st_mtime)).days >= VALIDI:
        scelta.unlink()
        fatti.append("scelta.md")
    return fatti


def etichetta(v):
    """Un título nuestro para cuando faltan los datos de YouTube: el primer capítulo del fragmento o el principio del resumen."""
    t = ((v.get("punti") or [{}])[0].get("testo") or "").split(":")[0].strip()
    if not t:
        t = (v.get("riassunto") or "").split(". ")[0].strip()
    vuoto = {"es": "Vídeo de YouTube", "en": "YouTube video"}.get((v.get("lingua") or "")[:2], "Video di YouTube")  # idioma del vídeo
    return (t[:90] + "…") if len(t) > 90 else (t or vuoto)


def completa(v, dati):
    """Pone en el vídeo de un curso los datos de YouTube válidos (o el título nuestro) y la miniatura del ID. Solo en memoria."""
    if v.get("tipo") == "lezione" or not v.get("id"):
        return v
    x = dati.get(v["id"])
    if x and not x.get("sparito"):
        for k in ("titolo", "canale", "pubblicato", "durata_s", "descrizione"):
            if x.get(k) not in (None, ""):
                v[k] = x[k]
        if not v.get("lingua") and x.get("lingua_audio"):
            v["lingua"] = x["lingua_audio"]
    elif x and x.get("sparito"):
        v["sparito"] = True
    if not v.get("titolo"):
        v["titolo"] = etichetta(v)
    if not v.get("canale"):
        v["canale"] = "YouTube"
    v.setdefault("copertina", f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg")
    return v


def main(a):
    from comune import aiuto, cartella
    aiuto(__doc__)
    if not a:
        sys.exit(__doc__)
    d = cartella(a[0])
    n = separa(d)
    if n:
        print(f"separados los datos de YouTube de {n} vídeos de percorso.json (ahora en lavoro/youtube/metadati.json)")
    k = chiave("YOUTUBE_API_KEY", obbligatoria=False)
    if k:
        try:
            r, s = rinnova(d, k, forza="--forza" in a)
            print(f"renovados {r} vídeos" + (f", {s} ya no disponibles en YouTube" if s else ""))
        except (urllib.error.URLError, OSError, ValueError) as e:
            print(f"YouTube no responde ({e.__class__.__name__}): se quedan los datos válidos, se vuelve a probar la próxima vez")
    else:
        print("falta YOUTUBE_API_KEY: no se renueva nada (python strumenti/chiavi.py prepara YOUTUBE_API_KEY)")
    for f in pulisci(d):
        print(f"más de 30 días: {f}")
    v = tutti(d)
    vecchi = [e for x in v.values() if (e := eta(x)) is not None]
    print(f"{len(v)} vídeos en metadati.json" + (f", el más antiguo leído hace {max(vecchi)} día{'' if max(vecchi) == 1 else 's'}" if vecchi else "")
          + f" · {datetime.now():%H:%M}")


if __name__ == "__main__":
    main(sys.argv[1:])

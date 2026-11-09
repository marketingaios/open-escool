"""Construye percorso.json a partir del mapa aprobado y de las fichas de los vídeos.

  python strumenti/costruisci.py <ruta>      -> percorsi/<ruta>/percorso.json y lavoro/scelta.md (el porqué de cada fragmento)

Fragmentos = capítulos seguidos de una ficha que cubren la etapa. Puntuación = nota de la ficha + 1 si muestra la pantalla
de la herramienta + 0,5 si está en el idioma de quien aprende + 0,5 si Gemini lo recomienda como «principale» + 1 si es el
mejor fragmento para la etapa + lo específico que es (hasta 1) − 1 por afirmación errónea − 0,5 por superada − 1,5 si es
anterior a la fecha de la etapa (se queda, con el aviso) − 1,5 si ya es el fragmento principal de otra etapa − 0,5 si dura más
de 15 minutos. Excluidos: vídeos «scarta», anteriores a `valido_da_ricerca`, fragmentos de menos de 1 minuto, vídeos hablados
en un idioma distinto de `lingua_video` del mapa, fragmentos ya usados en otra etapa (solapados en más de la mitad: el mismo
vídeo con otro trozo sí vale). Se quedan hasta 3 vídeos por etapa.
Las elecciones a mano en lavoro/scelta.json mandan: {"3": {"principale": "ID@1:20-9:40", "alternativi": ["ID"]}}.
Una lección generada (lezioni/t<N>.json, strumenti/lezione.py) sigue siendo el vídeo principal de su etapa también después.
De los vídeos de YouTube, percorso.json guarda solo el ID y los textos nuestros: título, canal, fecha y duración están en
lavoro/youtube/metadati.json (duran 30 días, ver strumenti/metadati.py) y los añade la plataforma cuando lee el curso.
"""
import sys
from datetime import date

import metadati
from comune import cartella, chiave, leggi, mmss, scrivi, secondi as s, aiuto, tr

MALE = {"sbagliata": 1.0, "superata": 0.5}


def meta_video(vid, meta, grezzo, pert):
    """Los datos de YouTube de un vídeo (solo para elegir y para scelta.md: en percorso.json no van)."""
    if vid in meta and not meta[vid].get("sparito") and meta[vid].get("titolo"):
        return {"id": vid, **meta[vid]}
    if vid in pert:
        return pert[vid]
    if grezzo.get(vid):
        return {"id": vid, **metadati.da_api({"id": vid, **grezzo[vid]})}
    return {"id": vid, "titolo": vid, "canale": "", "pubblicato": (meta.get(vid) or {}).get("pubblicato", "")}


def spezzoni(sch, n):
    out, cur = [], None
    for c in sch.get("capitoli", []):
        try:
            a, b = s(c["inizio"]), s(c["fine"])
        except (KeyError, ValueError, TypeError):
            cur = None
            continue
        if n in (c.get("tappe") or []):
            if cur and abs(a - cur["fine"]) <= 5:
                cur["fine"] = b
                cur["capitoli"].append(c)
            else:
                cur = {"inizio": a, "fine": b, "capitoli": [c]}
                out.append(cur)
        else:
            cur = None
    return out


def minuto(x):
    try:
        return s(x)
    except (ValueError, TypeError):
        return None


# textos que ve quien aprende, en su idioma (`lingua` de la ruta, no la de los vídeos)
TESTI = {
    "it": {"vecchio": "Video del {pub}, prima del cambio del {morbido}",
           "buco": "Nessun video controllato copre questa tappa: si studia sulle letture ufficiali finché non se ne trova uno."},
    "es": {"vecchio": "Vídeo del {pub}, anterior al cambio del {morbido}",
           "buco": "Ningún vídeo revisado cubre esta etapa: se estudia con las lecturas oficiales hasta que se encuentre uno."},
    "en": {"vecchio": "Video from {pub}, before the change of {morbido}",
           "buco": "No checked video covers this stage: study the official readings until one is found."},
}


MINUTI_POCHI = 3  # fragmento principal más corto: la etapa se avisa (09/11, GEO italiano: un fragmento genérico de pocos minutos)


def testo(chiave, lingua, **campi):
    return TESTI.get(lingua, TESTI["it"])[chiave].format(**campi)


def candidati(t, schede, lingua, principali, pavimento, solo_lingua=None, usati=(), date_video=None, lingua_testi="it"):
    n, duro, morbido = t["n"], t.get("valido_da_ricerca") or pavimento, t.get("valido_da")
    out = []
    for vid, sch in schede.items():
        pub = (date_video or {}).get(vid) or sch.get("pubblicato")  # sin fecha (datos de YouTube caducados) no se descarta por fecha
        if sch.get("consiglio") == "scarta" or (pub and pub < duro):
            continue
        if solo_lingua and (sch.get("lingua_parlata") or solo_lingua)[:2] != solo_lingua:
            continue
        for sp in spezzoni(sch, n):
            lung = sp["fine"] - sp["inizio"]
            if lung < 60:
                continue
            if any(v == vid and min(b, sp["fine"]) - max(a, sp["inizio"]) > 0.5 * min(b - a, lung) for v, a, b in usati):
                continue  # este trozo ya está en otra etapa (capítulo que Gemini une a varias etapas): no se repite
            aff = [a for a in sch.get("affermazioni", []) if sp["inizio"] - 2 <= (minuto(a.get("minuto")) or -99) <= sp["fine"] + 2]
            vecchio = bool(morbido and pub and pub < morbido)
            gia = any(v == vid and a < sp["fine"] and sp["inizio"] < b for v, a, b in principali)
            schermo = (sch.get("mostra_schermo") or sch.get("mostra_ads_manager")) and any(c.get("schermo") for c in sp["capitoli"])
            punti = ((sch.get("qualita") or {}).get("voto") or 3) + (1 if schermo else 0) \
                + (0.5 if sch.get("lingua_parlata") == lingua else 0) + (0.5 if sch.get("consiglio") == "principale" else 0) \
                + (1 if sch.get("tappa_migliore") == n else 0) \
                + sum(1 / max(1, len(c.get("tappe") or [])) for c in sp["capitoli"]) / len(sp["capitoli"]) \
                - sum(MALE.get(a.get("verdetto"), 0) for a in aff) - (1.5 if vecchio else 0) - (1.5 if gia else 0) \
                - (0.5 if lung > 15 * 60 else 0)
            if vecchio:
                aff = aff + [{"minuto": mmss(sp["inizio"]), "verdetto": "superata", "dice": testo("vecchio", lingua_testi, pub=pub, morbido=morbido),
                              "perche": (t.get("perche_data") or "").split(". ")[0]}]
            out.append({"vid": vid, "sch": sch, "sp": sp, "aff": aff, "punti": round(punti, 2)})
    out.sort(key=lambda c: (-c["punti"], c["sp"]["fine"] - c["sp"]["inizio"]))
    return out


def a_mano(voci, cand, schede, t=None, date_video=None, lingua_testi="it"):
    out = []
    morbido = (t or {}).get("valido_da")
    for voce in voci:
        vid, _, tempi = (voce or "").partition("@")
        if vid not in schede:
            continue
        c = next((c for c in cand if c["vid"] == vid), None)
        if tempi:
            a, b = (s(x) for x in tempi.split("-"))
            sch = schede[vid]
            c = {"vid": vid, "sch": sch, "sp": {"inizio": a, "fine": b, "capitoli": [ch for ch in sch.get("capitoli", []) if a <= (minuto(ch.get("inizio")) or -1) < b]},
                 "aff": [x for x in sch.get("affermazioni", []) if a <= (minuto(x.get("minuto")) or -1) <= b], "punti": "a mano"}
            pub = (date_video or {}).get(vid) or sch.get("pubblicato")
            if morbido and pub and pub < morbido:  # como con los fragmentos elegidos automáticamente
                c["aff"] = c["aff"] + [{"minuto": mmss(a), "verdetto": "superata", "dice": testo("vecchio", lingua_testi, pub=pub, morbido=morbido),
                                        "perche": (t.get("perche_data") or "").split(". ")[0]}]
        if c:
            out.append(c)
    return out


def main(slug):
    d = cartella(slug)
    m = leggi(d / "lavoro" / "mappa.json") or sys.exit(tr("manca lavoro/mappa.json", "falta lavoro/mappa.json",
                                                           "lavoro/mappa.json is missing"))
    metadati.separa(d)  # cursos anteriores al 09/11/2026: los datos de YouTube salen de percorso.json y de las fichas
    grezzo = leggi(d / "lavoro" / "youtube" / "grezzo_video.json", {})
    pert = {v["id"]: v for v in leggi(d / "lavoro" / "youtube" / "pertinenti.json", [])}
    schede = {f.stem: leggi(f) for f in (d / "schede").glob("*.json")} if (d / "schede").exists() else {}
    schede = {k: v for k, v in schede.items() if v and not v.get("errore_json")}
    if k := chiave("YOUTUBE_API_KEY", obbligatoria=False):
        try:
            metadati.rinnova(d, k, ids=list(schede))
        except (OSError, ValueError) as e:  # red o cuota: se construye con los datos válidos que hay
            nome = e.__class__.__name__
            print(tr(f"dati di YouTube non rinnovati ({nome}): le date dei video senza dati non si controllano",
                     f"datos de YouTube no renovados ({nome}): las fechas de los vídeos sin datos no se comprueban",
                     f"YouTube data not renewed ({nome}): the dates of videos without data are not checked"))
    meta = metadati.validi(d)
    date_video = {vid: meta_video(vid, meta, grezzo, pert).get("pubblicato") for vid in schede}
    mano = leggi(d / "lavoro" / "scelta.json", {})
    lingua = m.get("lingua", "it")
    lingua_v = m.get("lingua_video")  # un idioma por ruta: los vídeos hablados en otros idiomas se quedan fuera
    pavimento = min(t.get("valido_da") or "0" for t in m["tappe"])
    tappe, righe, principali, usati, deboli = [], [], [], [], []
    # papel del vídeo y elección a mano como se leen en scelta.md y en pantalla (en percorso.json quedan "principale", "a mano")
    nomi_ruolo = {"principale": tr("principale", "principal", "main"),
                  "alternativo": tr("alternativo", "alternativo", "alternative")}
    a_mano_txt = tr("a mano", "a mano", "by hand")
    for t in m["tappe"]:
        cand = candidati(t, schede, lingua_v or lingua, principali, pavimento, lingua_v, usati, date_video, lingua)
        fuori_lingua = []  # los que quedan fuera solo por el idioma hablado (el de la ficha de Gemini, no el que declara YouTube)
        if lingua_v:
            dentro = {c["vid"] for c in cand}
            fuori_lingua = [c for c in candidati(t, schede, lingua_v, principali, pavimento, None, usati, date_video, lingua)
                            if c["vid"] not in dentro]
        scelti, visti = [], set()
        for c in cand:
            if c["vid"] not in visti:
                scelti.append(c)
                visti.add(c["vid"])
            if len(scelti) == 3:
                break
        if str(t["n"]) in mano:
            x = mano[str(t["n"])]
            scelti = a_mano([x.get("principale")] + x.get("alternativi", []), cand, schede, t, date_video, lingua)
        if scelti:
            principali.append((scelti[0]["vid"], scelti[0]["sp"]["inizio"], scelti[0]["sp"]["fine"]))
        usati += [(c["vid"], c["sp"]["inizio"], c["sp"]["fine"]) for c in scelti]
        video = []
        for i, c in enumerate(scelti):
            mv, sch, sp = meta_video(c["vid"], meta, grezzo, pert), c["sch"], c["sp"]
            punti = [{"minuto": ch["inizio"], "testo": ch.get("titolo", "") + (": " + "; ".join(ch["punti_chiave"][:3]) if ch.get("punti_chiave") else "")}
                     for ch in sp["capitoli"]]
            attenzione = [{k: a.get(k) for k in ("minuto", "dice", "verdetto", "perche")} for a in c["aff"] if a.get("verdetto") in MALE]
            ruolo = "principale" if i == 0 else "alternativo"
            video.append({"id": c["vid"], "ruolo": ruolo, "lingua": sch.get("lingua_parlata") or mv.get("lingua_audio"),
                          "inizio": mmss(sp["inizio"]), "fine": mmss(sp["fine"]), "riassunto": sch.get("riassunto"), "punti": punti,
                          "attenzione": attenzione, "perche": sch.get("consiglio_perche"), "punteggio": c["punti"]})
            punti_txt = a_mano_txt if c["punti"] == "a mano" else c["punti"]
            video_txt = f"{mv.get('canale', '')} · {(mv.get('titolo') or c['vid'])[:60]}".replace("|", "/")  # «|» rompería la tabla
            righe.append(f"| {t['n']} | {nomi_ruolo[ruolo]} | {video_txt} "
                         f"| {mmss(sp['inizio'])}-{mmss(sp['fine'])} | {punti_txt} |")
        n_tappa = t["n"]
        durata_p = (s(video[0]["fine"]) - s(video[0]["inizio"])) / 60 if video else 0.0
        if video and durata_p < MINUTI_POCHI:
            deboli.append((n_tappa, tr(f"tappa {n_tappa}: lo spezzone principale dura solo {durata_p:.1f} min: controlla che copra davvero la "
                             f"tappa (se no, buco dichiarato o lezione generata)",
                             f"etapa {n_tappa}: el fragmento principal dura solo {durata_p:.1f} min: comprueba que cubra de verdad "
                             f"la etapa (si no, hueco declarado o lección generada)",
                             f"stage {n_tappa}: the main clip is only {durata_p:.1f} min long: check that it really covers the stage "
                             f"(if not, a declared gap or a generated lesson)")))
        punti_p = scelti[0]["punti"] if scelti and isinstance(scelti[0]["punti"], (int, float)) else None
        migliori = {c["vid"] for c in fuori_lingua if punti_p is None or c["punti"] > punti_p}
        if fuori_lingua and (not video or durata_p < MINUTI_POCHI):  # solo si la etapa queda débil: el idioma elegido manda
            k = len({c["vid"] for c in fuori_lingua})
            parlate = ", ".join(sorted({(c["sch"].get("lingua_parlata") or "?")[:2] for c in fuori_lingua}))
            n_m = len(migliori)
            piu = (tr(f", {n_m} con punteggio più alto del principale", f", {n_m} con más puntuación que el principal",
                      f", {n_m} scoring higher than the main one") if video else "")
            deboli.append((n_tappa, tr(f"tappa {n_tappa}: {k} video esclusi perché parlati in {parlate} (lingua letta dalla scheda di Gemini, non "
                             f"quella dichiarata da YouTube){piu}",
                             f"etapa {n_tappa}: {k} vídeos excluidos por estar hablados en {parlate} (idioma leído de la ficha de Gemini, "
                             f"no el que declara YouTube){piu}",
                             f"stage {n_tappa}: {k} videos left out because they are spoken in {parlate} (language read from the Gemini "
                             f"card, not the one YouTube declares){piu}")))
        tappe.append({"n": t["n"], "titolo": t["titolo"], "obiettivo": t["obiettivo"],
                      "minuti_video": round((s(video[0]["fine"]) - s(video[0]["inizio"])) / 60) if video else t.get("minuti_video"),
                      "valido_da": t.get("valido_da"), "ricontrolla_dopo": t.get("ricontrolla_dopo"), "nota_ricontrollo": t.get("nota_ricontrollo"),
                      "concetti": [c["testo"] for c in t["concetti"]], "letture": t.get("letture_ufficiali", []),
                      "nota_letture": t.get("nota_letture") or t.get("nota_offerte"),
                      "buco": None if video else testo("buco", lingua),
                      "video": video})
    # borrador mientras falte la ficha de algún vídeo de la lista (los fragmentos aún pueden cambiar)
    mancano = [v["id"] for v in leggi(d / "lavoro" / "youtube" / "lista.json", []) if v["id"] not in schede]
    vecchio = leggi(d / "percorso.json", {})
    percorso = {"slug": slug, "titolo": m.get("titolo_percorso") or m["tema"], "sottotitolo": m.get("sottotitolo", ""),
                "arrivo": m.get("obiettivo", ""), "lingua": lingua, "lingua_video": lingua_v, "da": m.get("da"), "tema": m["tema"], "copertina": m.get("copertina"), "categoria": m.get("categoria"), "creato": vecchio.get("creato") or date.today().isoformat(),
                "controllato": date.today().isoformat(), "stato": "pronto" if schede and not mancano else "bozza", "schede_mancanti": len(mancano), "fonti": m.get("fonti_descrizione", ""),
                "avvisi": m.get("avvisi_italia") or m.get("avvisi", []), "cambi_recenti": m.get("cambi_recenti", []),
                "durata_min": sum(t["minuti_video"] or 0 for t in tappe), "tappe": tappe}
    scrivi(d / "percorso.json", percorso)
    from lezione import metti_lezioni  # las lecciones generadas (lezioni/t<N>.json) siguen siendo el vídeo principal de su etapa
    if n_lez := metti_lezioni(slug):
        print(tr(f"lezioni generate rimesse: {n_lez}", f"lecciones generadas repuestas: {n_lez}",
                 f"generated lessons put back: {n_lez}"))
        percorso = leggi(d / "percorso.json", percorso)  # el resumen cuenta también las lecciones
        tappe = percorso["tappe"]
    con_lezione = {(leggi(f, {}) or {}).get("tappa") for f in (d / "lezioni").glob("t*.json")}
    deboli = [x for n_tappa, x in deboli if n_tappa not in con_lezione]  # una lección generada ya cubre la etapa
    testata = tr("# Spezzoni scelti\n\n| Tappa | Ruolo | Video | Spezzone | Punti |\n",
                 "# Fragmentos elegidos\n\n| Etapa | Rol | Vídeo | Fragmento | Puntos |\n",
                 "# Chosen clips\n\n| Stage | Role | Video | Clip | Points |\n")
    da_guardare = (tr("## Da controllare\n\n", "## Por revisar\n\n", "## To check\n\n") + "".join(f"- {x}\n" for x in deboli) + "\n"
                   if deboli else "")
    testata = testata.replace("\n\n", "\n\n" + da_guardare, 1)
    (d / "lavoro" / "scelta.md").write_text(testata + "|---|---|---|---|---|\n" + "\n".join(righe) + "\n", encoding="utf-8")
    metadati.pulisci(d)
    n_sch, n_sp, n_t, durata = len(schede), sum(len(t["video"]) for t in tappe), len(tappe), percorso["durata_min"]
    senza = [t["n"] for t in tappe if not t["video"]]
    print(tr(f"{n_sch} schede, {n_sp} spezzoni in {n_t} tappe, {durata} min; tappe senza video: {senza or 'nessuna'}",
             f"{n_sch} fichas, {n_sp} fragmentos en {n_t} etapas, {durata} min; etapas sin vídeo: {senza or 'ninguna'}",
             f"{n_sch} cards, {n_sp} clips in {n_t} stages, {durata} min; stages without video: {senza or 'none'}"))
    print("\n".join(righe))
    for x in deboli:
        print(tr("ATTENZIONE ", "ATENCIÓN ", "WARNING ") + x)


if __name__ == "__main__":
    aiuto(__doc__)
    main(sys.argv[1]) if len(sys.argv) == 2 else sys.exit(__doc__)

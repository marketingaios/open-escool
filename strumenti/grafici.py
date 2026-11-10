"""Los gráficos del README (SVG claro y oscuro), a partir de las rutas listas.

    python strumenti/grafici.py      -> docs/img/filtros-{claro,oscuro}.svg, rutas-{claro,oscuro}.svg y datos.json

Solo datos propios: cuántos vídeos pasan cada filtro al hacer una ruta y cuántos minutos dura cada ruta lista. Los números de
la búsqueda salen de percorsi/<ruta>/lavoro/youtube/ cuando existe; esos archivos duran 30 días (strumenti/metadati.py), así
que se guardan en docs/img/datos.json y la próxima vez se reutilizan. Colores de la paleta de referencia (azul), validados
contra el fondo de GitHub en modo claro (#ffffff) y oscuro (#0d1117).
"""
import json
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RADICE / "strumenti"))
from comune import PERCORSI, aiuto, leggi, tr  # noqa: E402

OUT = RADICE / "docs" / "img"
RUTA_FILTROS = "chatgpt-ads-es"  # la ruta en español: el README principal es en español
RUTAS = [("chatgpt-ads", "ChatGPT Ads · italiano"), ("chatgpt-ads-es", "ChatGPT Ads · español"),
         ("chatgpt-ads-en", "ChatGPT Ads · inglés"), ("geo", "GEO · español")]
TEMAS = {
    "claro": {"fondo": "#ffffff", "texto": "#0b0b0b", "texto2": "#52514e", "base": "#c3c2b7",
              "serie": "#2a78d6", "escala": ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab"]},
    "oscuro": {"fondo": "#0d1117", "texto": "#f0efec", "texto2": "#c3c2b7", "base": "#383835",
               "serie": "#3987e5", "escala": ["#184f95", "#256abf", "#3987e5", "#6da7ec"]},
}
FUENTE = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def barra(x, y, w, h, color):
    """Barra horizontal: base recta, extremo de los datos redondeado 4 px."""
    w = max(w, 4)
    r = min(4, w / 2, h / 2)
    return (f'<path d="M{x:.1f},{y:.1f} h{w - r:.1f} a{r},{r} 0 0 1 {r},{r} v{h - 2 * r:.1f} a{r},{r} 0 0 1 -{r},{r} '
            f'h-{w - r:.1f} z" fill="{color}"/>')


def grafico(titulo, subtitulo, filas, colores, tema, unidad=""):
    """filas: [(etiqueta, valor, texto del valor)]. Una etiqueta encima de cada barra, el valor en la punta."""
    t = TEMAS[tema]
    ancho, izq, ancho_barras, alto_fila, grosor = 720, 24, 560, 54, 20
    alto = 92 + alto_fila * len(filas) + 12
    maximo = max((v for _, v, _ in filas), default=0) or 1  # sin rutas listas: gráfico vacío, sin error
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" viewBox="0 0 {ancho} {alto}" role="img" '
         f'aria-label="{esc(titulo)}. ' + esc("; ".join(f"{e}: {tx}" for e, _, tx in filas)) + '">',
         f'<rect width="{ancho}" height="{alto}" rx="8" fill="{t["fondo"]}"/>',
         f'<text x="{izq}" y="34" font-family="{FUENTE}" font-size="18" font-weight="600" fill="{t["texto"]}">{esc(titulo)}</text>',
         f'<text x="{izq}" y="58" font-family="{FUENTE}" font-size="13" fill="{t["texto2"]}">{esc(subtitulo)}</text>']
    y = 92
    for i, (etiqueta, valor, texto) in enumerate(filas):
        w = ancho_barras * valor / maximo
        p.append(f'<text x="{izq}" y="{y}" font-family="{FUENTE}" font-size="13" fill="{t["texto2"]}">{esc(etiqueta)}</text>')
        p.append(f'<line x1="{izq}" y1="{y + 8}" x2="{izq}" y2="{y + 8 + grosor}" stroke="{t["base"]}" stroke-width="1"/>')
        p.append(barra(izq, y + 8, w, grosor, colores[i]))
        p.append(f'<text x="{izq + max(w, 4) + 8:.1f}" y="{y + 8 + grosor - 5}" font-family="{FUENTE}" font-size="14" '
                 f'font-weight="600" fill="{t["texto"]}">{esc(texto)}</text>')
        y += alto_fila
    p.append("</svg>")
    return "\n".join(p) + "\n"


IDIOMAS = {"it": "italiano", "es": "español", "en": "inglés"}


def datos():
    guardados = leggi(OUT / "datos.json", {}) or {}
    d = PERCORSI / RUTA_FILTROS
    yt = d / "lavoro" / "youtube"
    p = leggi(d / "percorso.json", {}) or {}
    filtros = guardados.get("filtros", {})
    if (yt / "grezzo_video.json").exists() and (yt / "pertinenti.json").exists():
        filtros = {"busquedas": (leggi(yt / "candidati.json", {}) or {}).get("ricerche"),
                   "encontrados": len(leggi(yt / "grezzo_video.json", {}) or {}),
                   "pertinentes": len(leggi(yt / "pertinenti.json", []) or []),
                   "vistos": len(list((d / "schede").glob("*.json"))),
                   "en_la_ruta": sum(1 for t in p.get("tappe", []) for v in t.get("video", []) if v.get("tipo") != "lezione"),
                   "minutos": p.get("durata_min"), "ruta": RUTA_FILTROS, "titulo": p.get("titolo"),
                   "idioma": p.get("lingua_video") or p.get("lingua")}
    rutas = []
    for slug, nombre in RUTAS:
        q = leggi(PERCORSI / slug / "percorso.json", {}) or {}
        if q:
            rutas.append({"ruta": slug, "nombre": nombre, "etapas": len(q.get("tappe", [])), "minutos": q.get("durata_min") or 0})
    return {"filtros": filtros, "rutas": rutas}


def main():
    aiuto(__doc__)
    OUT.mkdir(parents=True, exist_ok=True)
    d = datos()
    f = d["filtros"]
    for tema, t in TEMAS.items():
        if f:
            busquedas = f" ({f['busquedas']} búsquedas)" if f.get("busquedas") else ""
            filas = [("Encontrados con la API de YouTube" + busquedas, f["encontrados"], f"{f['encontrados']} vídeos"),
                     ("Pertinentes por título, duración e idioma", f["pertinentes"], f"{f['pertinentes']} vídeos"),
                     ("Vistos por Gemini y comparados con las fuentes", f["vistos"], f"{f['vistos']} vídeos"),
                     ("Fragmentos en la ruta", f["en_la_ruta"], f"{f['en_la_ruta']} fragmentos · {f['minutos']} min")]
            (OUT / f"filtros-{tema}.svg").write_text(grafico(
                f"De {f['encontrados']} vídeos a {f['en_la_ruta']} fragmentos",
                f"Ruta «{f.get('titulo') or RUTA_FILTROS}», vídeos en {IDIOMAS.get(f.get('idioma'), 'varios idiomas')}: "
                "lo que pasa cada filtro",
                filas, t["escala"], tema), encoding="utf-8")
        filas = [(r["nombre"] + f" · {r['etapas']} etapas", r["minutos"], f"{r['minutos']} min") for r in d["rutas"]]
        (OUT / f"rutas-{tema}.svg").write_text(grafico(
            "Minutos de vídeo de cada ruta lista", "Solo los fragmentos que hay que ver, sin las lecturas oficiales",
            filas, [t["serie"]] * len(filas), tema), encoding="utf-8")
    (OUT / "datos.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    dove, n = OUT.relative_to(RADICE), len(d["rutas"])
    print(tr(f"grafici in {dove}: filtri {'sì' if f else 'no (mancano i dati della ricerca)'}, {n} percorsi",
             f"gráficos en {dove}: filtros {'sí' if f else 'no (faltan los datos de la búsqueda)'}, {n} rutas",
             f"charts in {dove}: filters {'yes' if f else 'no (the search data is missing)'}, {n} paths"))


if __name__ == "__main__":
    main()

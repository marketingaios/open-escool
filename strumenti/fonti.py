"""Fuentes oficiales guardadas en lavoro/fonti/ (una página = un archivo .md con la URL y la fecha arriba).

  python strumenti/fonti.py salva <ruta> URL [URL ...]   con Tavily (TAVILY_API_KEY, opcional) descarga y guarda las páginas
  python strumenti/fonti.py controlla <ruta>             cada cita del mapa debe estar de verdad en su fuente

Sin Tavily el asistente lee las páginas con su búsqueda web y las guarda él con el mismo formato (las etiquetas no se traducen):
  primera línea «URL: ...», segunda «Letta: AAAA-MM-GG» (año-mes-día), línea vacía y luego el texto de la página.
"""
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.request
from datetime import date

from comune import cartella, chiave, leggi, aiuto


def nome_file(url):
    s = re.sub(r"^https?://", "", url).rstrip("/")
    s = re.sub(r"[^A-Za-z0-9]+", "-", s.split("?")[0])[-90:].strip("-").lower()
    return s + ".md"


def salva(slug, urls):
    k = chiave("TAVILY_API_KEY", obbligatoria=False)
    if not k:
        sys.exit("no hay TAVILY_API_KEY: lee las páginas con la búsqueda web del asistente y guárdalas en lavoro/fonti/ (formato arriba)")
    out = cartella(slug) / "lavoro" / "fonti"
    out.mkdir(parents=True, exist_ok=True)
    for i in range(0, len(urls), 10):
        req = urllib.request.Request("https://api.tavily.com/extract", method="POST",
                                     data=json.dumps({"urls": urls[i:i + 10], "extract_depth": "advanced"}).encode(),
                                     headers={"Authorization": f"Bearer {k}", "Content-Type": "application/json"})
        try:
            ris = json.load(urllib.request.urlopen(req, timeout=120))
        except urllib.error.HTTPError as e:
            sys.exit(f"Tavily: HTTP {e.code}")
        for r in ris.get("results", []):
            f = out / nome_file(r["url"])
            f.write_text(f"URL: {r['url']}\nLetta: {date.today().isoformat()}\n\n{r.get('raw_content', '')}", encoding="utf-8")
            print(f"ok {f.name} ({len(r.get('raw_content', '').split())} palabras)")
        for r in ris.get("failed_results", []):
            print(f"NO leída: {r.get('url')} ({r.get('error', '')})")


def piano(s):
    s = unicodedata.normalize("NFKD", s).replace("’", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"[*_`#>|\[\]]", "", s)  # negritas, enlaces y tablas del markdown
    return re.sub(r"\s+", " ", s).strip().lower()


def controlla(slug):
    d = cartella(slug)
    m = leggi(d / "lavoro" / "mappa.json") or sys.exit("falta lavoro/mappa.json")
    fonti = {f.name: piano(f.read_text(encoding="utf-8")) for f in (d / "lavoro" / "fonti").glob("*.md")}
    ok, male = 0, []
    for t in m["tappe"]:
        for c in t["concetti"]:
            testo = fonti.get(c.get("fonte", ""))
            cit = piano(c.get("citazione", ""))
            if testo is None:
                male.append(f"etapa {t['n']}: fuente «{c.get('fonte')}» no guardada · {c['testo'][:70]}")
            elif cit and cit in testo:
                ok += 1
            else:
                male.append(f"etapa {t['n']}: cita no encontrada en {c.get('fonte')} · «{c.get('citazione', '')[:80]}»")
    print(f"citas encontradas: {ok}; por arreglar: {len(male)}")
    for x in male:
        print("  " + x)
    sys.exit(1 if male else 0)


if __name__ == "__main__":
    aiuto(__doc__)
    a = sys.argv[1:]
    if len(a) >= 3 and a[0] == "salva":
        salva(a[1], a[2:])
    elif len(a) == 2 and a[0] == "controlla":
        controlla(a[1])
    else:
        sys.exit(__doc__)

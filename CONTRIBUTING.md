# Cómo contribuir a Open Escool

Open Escool es un proyecto personal de [Ismagit](https://ismagit.com) que se comparte tal cual. Se aceptan **correcciones
pequeñas**; no hay compromiso de tiempos de respuesta.

## Qué se acepta
- **Errores**: algo que no funciona como dice la documentación, en Mac, Windows o Linux.
- **Compatibilidad**: rutas, codificaciones o instaladores que fallan en un sistema concreto.
- **Textos**: erratas y traducciones de la interfaz (italiano, español, inglés).
- **Rutas listas**: un vídeo que ya no existe o un dato que ha cambiado en las fuentes oficiales.

Funciones nuevas, cambios de diseño o de estructura: abre antes una discusión. Lo más probable es que la respuesta sea «no por
ahora»: el proyecto se mantiene pequeño a propósito.

## Antes de abrir una incidencia
1. Ejecuta el diagnóstico para compartir: `python strumenti/diagnosi.py --condividi` (en Windows `py` en lugar de
   `python`). Quita el nombre del ordenador y del usuario, las carpetas, la lista de rutas y las claves.
2. **Léelo antes de pegarlo**: la incidencia es pública. Nunca pegues el diagnóstico completo de la carpeta `diagnosi/`, el
   archivo `.env`, tus notas ni tu chat.
3. Usa la plantilla «Problema» y escribe los pasos para reproducirlo.

## Pull requests
- Un cambio pequeño por pull request, con una línea que diga qué arregla y cómo lo has probado.
- Python solo con la biblioteca estándar en el servidor (`accademia.py`) y en las herramientas comunes; archivos en UTF-8,
  rutas con `pathlib`, nada que funcione solo en Mac.
- Nunca datos de la API de YouTube dentro de las rutas (`percorso.json`, fichas): solo el ID del vídeo y textos propios (ver
  `strumenti/metadati.py`).
- Activa el control previo de los commits: `git config core.hooksPath .githooks` (bloquea claves, datos personales y correos
  visibles; con `gitleaks` instalado revisa más a fondo).

## Acuerdo de contribución
Al enviar una pull request confirmas que:
1. el trabajo es tuyo, o tienes derecho a enviarlo;
2. lo publicas bajo la licencia del proyecto (PolyForm Noncommercial 1.0.0);
3. concedes a Ismagit una licencia mundial, gratuita, perpetua e irrevocable para usar, modificar, sublicenciar y
   volver a licenciar tu contribución, también con otra licencia.

El punto 3 permite a Ismagit cambiar la licencia del proyecto en el futuro sin pedir permiso a cada persona. Si no estás de
acuerdo, no envíes la pull request: abre una incidencia describiendo el arreglo.

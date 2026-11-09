#!/bin/sh
# Open Escool · instalación en Mac (y Linux). Uso: sh installa.sh [--senza-avvio] [--senza-lezioni]
#   --senza-avvio    no añade el arranque automático al iniciar sesión (el servidor se arranca a mano: python3 accademia.py --apri)
#   --senza-lezioni  se salta lo que necesitan las lecciones generadas (Node, ffmpeg, Remotion, voz gratuita: 2-6 GB, 10-30 minutos)
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

PY="$(command -v python3 || command -v python || true)"
if [ -z "$PY" ]; then echo "Hace falta Python 3.10 o más: https://www.python.org/downloads/ (o brew install python)"; exit 1; fi
"$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' || { echo "Python demasiado antiguo: hace falta 3.10 o más"; exit 1; }
PY="$("$PY" -c 'import sys; print(sys.executable)')"
echo "Python: $PY"

mkdir -p percorsi utente
[ -f config.json ] || printf '{}\n' > config.json
# las skills valen para Claude Code (.claude/skills) y Codex (.agents/skills): la misma copia
mkdir -p .agents/skills && cp -R .claude/skills/. .agents/skills/

case "$DIR" in
  "$HOME/Documents"*|"$HOME/Desktop"*|"$HOME/Downloads"*)
    echo "Atención: en Documentos, Escritorio o Descargas macOS no deja leer los archivos a un programa que arranca solo."
    echo "Mejor mover la carpeta a $HOME/open-escool y volver a lanzarlo. Sigo sin arranque automático."
    SENZA=1 ;;
esac

PORTA="$("$PY" -c "import json; c=json.load(open('config.esempio.json', encoding='utf-8')); c.update(json.load(open('config.json', encoding='utf-8'))); print(c.get('porta', 8765))")"

case " $* " in *" --senza-avvio "*) SENZA=1 ;; esac

# ---------- lecciones generadas: Node + Remotion, ffmpeg, voz gratuita ----------
# Mac con Apple Silicon: Chatterbox (mlx-audio) y las voces ligeras; en el resto, solo las ligeras
# (Supertonic 3, Kokoro: ONNX en el procesador)
LEZ="no instaladas (--senza-lezioni)"
case " $* " in *" --senza-lezioni "*) SENZA_LEZ=1 ;; esac
if [ -z "$SENZA_LEZ" ]; then
  echo ""
  echo "Lecciones generadas: Node, ffmpeg, Remotion y la voz gratuita (2-6 GB, 10-30 minutos la primera vez)."
  OK=1
  for prog in node ffmpeg uv; do
    if ! command -v "$prog" >/dev/null 2>&1; then
      if command -v brew >/dev/null 2>&1; then brew install "$prog" || OK=0
      else echo "Falta $prog: instala Homebrew (https://brew.sh) y vuelve a lanzarlo, o instálalo a mano"; OK=0; fi
    fi
  done
  if [ "$OK" = 1 ]; then
    (cd lezione && npm install --no-audit --no-fund && node node_modules/@remotion/cli/remotion-cli.js browser ensure) || OK=0
  fi
  if [ "$OK" = 1 ]; then
    VPY="$DIR/strumenti/.voce/bin/python"
    PAC="supertonic==1.3.1 kokoro-onnx==0.6.1 faster-whisper==1.2.1 scipy==1.18.1 numpy==2.5.4 soundfile==0.14.0"
    VOCI="supertonic kokoro-onnx"; W=small
    if [ "$(uname)" = "Darwin" ] && [ "$(uname -m)" = "arm64" ]; then PAC="$PAC mlx-audio==0.6.4"; VOCI="chatterbox $VOCI"; W=medium; fi
    [ -x "$VPY" ] || uv venv strumenti/.voce --python 3.12 || OK=0
    # shellcheck disable=SC2086
    [ "$OK" = 1 ] && { uv pip install --python "$VPY" $PAC || OK=0; }
    [ "$OK" = 1 ] && { "$VPY" strumenti/voce_locale.py prepara $VOCI --whisper $W || OK=0; }
  fi
  if [ "$OK" = 1 ]; then LEZ="listas"; else LEZ="NO listas: mira los mensajes de arriba (python3 strumenti/diagnosi.py)"; fi
fi

if [ -z "$SENZA" ] && [ "$(uname)" = "Darwin" ]; then
  PLIST="$HOME/Library/LaunchAgents/it.accademia.server.plist"
  mkdir -p "$HOME/Library/LaunchAgents"
  cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
 <key>Label</key><string>it.accademia.server</string>
 <key>ProgramArguments</key><array><string>$PY</string><string>$DIR/accademia.py</string><string>--silenzioso</string></array>
 <key>WorkingDirectory</key><string>$DIR</string>
 <key>EnvironmentVariables</key><dict><key>PATH</key><string>$PATH</string><key>LANG</key><string>it_IT.UTF-8</string></dict>
 <key>RunAtLoad</key><true/>
 <key>KeepAlive</key><dict><key>SuccessfulExit</key><false/></dict>
 <key>StandardErrorPath</key><string>$DIR/utente/server.log</string>
</dict></plist>
EOF
  launchctl bootout "gui/$(id -u)/it.accademia.server" 2>/dev/null || true
  launchctl bootstrap "gui/$(id -u)" "$PLIST"
  echo "Arranque automático: activo (para quitarlo: launchctl bootout gui/$(id -u)/it.accademia.server && rm \"$PLIST\")"
  sleep 1
else
  nohup "$PY" accademia.py --silenzioso > utente/server.log 2>&1 &
  echo "Servidor arrancado a mano (se para al reiniciar el ordenador)"
  sleep 1
fi

"$PY" strumenti/chiavi.py stato || true
URL="http://127.0.0.1:$PORTA"
if ! "$PY" -c "import sys, accademia; sys.exit(0 if accademia.e_accademia($PORTA) else 1)"; then
  echo "Open Escool no responde en $URL: mira utente/server.log (¿puerto ocupado? cambia \"porta\" en config.json)"; exit 1
fi
echo "Open Escool está en $URL"
echo "Lecciones generadas: $LEZ"
echo "Para el icono en el Dock: en Chrome o Edge menú ⋮ → «Instalar Open Escool»; en Safari Archivo → «Añadir al Dock»."
if [ -n "$ACCADEMIA_SENZA_BROWSER" ]; then :; elif command -v open >/dev/null 2>&1; then open "$URL"; elif command -v xdg-open >/dev/null 2>&1; then xdg-open "$URL"; fi

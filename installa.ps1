# Open Escool · instalación en Windows. Uso (desde PowerShell, en la carpeta de Open Escool):
#   powershell -ExecutionPolicy Bypass -File installa.ps1 [-SenzaAvvio] [-SenzaLezioni]
#   -SenzaAvvio    no añade el arranque automático al iniciar sesión (el servidor se arranca a mano: py accademia.py --apri)
#   -SenzaLezioni  se salta lo que necesitan las lecciones generadas (Node, ffmpeg, Remotion, voz gratuita: ~2 GB, 10-30 minutos)
param([switch]$SenzaAvvio, [switch]$SenzaLezioni)
$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$utf8 = New-Object Text.UTF8Encoding $false

# Python: primero el lanzador «py» (el de python.org); «python» puede ser el falso acceso directo a Microsoft Store
$py = $null; $pyArgs = @()
if (Get-Command py -ErrorAction SilentlyContinue) { $py = "py"; $pyArgs = @("-3") }
elseif (Get-Command python -ErrorAction SilentlyContinue) { $py = "python" }
if (-not $py) {
  Write-Host "Hace falta Python 3.10 o superior: winget install Python.Python.3.13 (luego cierra y vuelve a abrir PowerShell)"; exit 1
}
& $py @pyArgs -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)"
if ($LASTEXITCODE -ne 0) { Write-Host "Python demasiado antiguo o que no funciona: hace falta 3.10 o superior (winget install Python.Python.3.13)"; exit 1 }
$exe = (& $py @pyArgs -c "import sys; print(sys.executable)").Trim()
$pyw = Join-Path (Split-Path $exe) "pythonw.exe"
if (-not (Test-Path $pyw)) { $pyw = $exe }
Write-Host "Python: $exe"

New-Item -ItemType Directory -Force -Path percorsi, utente, ".agents\skills" | Out-Null
if (-not (Test-Path config.json)) { [IO.File]::WriteAllText((Join-Path $PSScriptRoot "config.json"), "{}`n", $utf8) }
# las skills valen para Claude Code (.claude\skills) y Codex (.agents\skills): la misma copia
Copy-Item -Recurse -Force ".claude\skills\*" ".agents\skills\"

# ---------- lecciones generadas: Node + Remotion, ffmpeg, voz gratuita ligera (Supertonic 3 / Kokoro con ONNX, solo procesador) ----------
function Aggiorna-Path {
  $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
}
function Con-Winget($id, $nome) {
  if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "Falta winget (App Installer de Microsoft Store): instala $nome a mano y vuelve a lanzar el instalador."; return $false
  }
  Write-Host "Instalo $nome con winget (si Windows pide permiso, permite el cambio)..."
  winget install --id $id -e --silent --accept-package-agreements --accept-source-agreements | Out-Host
  Aggiorna-Path
  return $true
}
$lezioni = "no instaladas (-SenzaLezioni)"
if (-not $SenzaLezioni) {
  Write-Host ""
  Write-Host "Lecciones generadas: Node, ffmpeg, Remotion y la voz gratuita (unos 2 GB, 10-30 minutos la primera vez)."
  $ok = $true
  $nodeOk = $false
  if (Get-Command node -ErrorAction SilentlyContinue) { $nodeOk = ([int]((node -v).TrimStart("v").Split(".")[0]) -ge 18) }
  if (-not $nodeOk) { $null = Con-Winget "OpenJS.NodeJS.LTS" "Node.js" }
  if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) { $null = Con-Winget "Gyan.FFmpeg" "ffmpeg" }
  # ONNX Runtime (la voz) y Whisper usan las bibliotecas Visual C++ de Microsoft: en un PC recién instalado pueden faltar
  if (-not (Test-Path (Join-Path $env:SystemRoot "System32\msvcp140.dll"))) { $null = Con-Winget "Microsoft.VCRedist.2015+.x64" "Visual C++ Redistributable" }
  if (-not (Get-Command node -ErrorAction SilentlyContinue)) { Write-Host "Node no encontrado: cierra y vuelve a abrir PowerShell y lanza otra vez installa.ps1."; $ok = $false }
  if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) { Write-Host "ffmpeg no encontrado: cierra y vuelve a abrir PowerShell y lanza otra vez installa.ps1."; $ok = $false }
  if ($ok) {
    Push-Location lezione
    Write-Host "Remotion (fichas animadas)..."
    npm install --no-audit --no-fund | Out-Host
    if ($LASTEXITCODE -ne 0) { $ok = $false; Write-Host "npm install no ha funcionado: mira los mensajes de arriba." }
    else { node node_modules/@remotion/cli/remotion-cli.js browser ensure | Out-Host }
    Pop-Location
  }
  if ($ok) {
    # uv descarga por su cuenta Python 3.12, para el que hay listos para Windows todos los paquetes de la voz
    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) { $null = Con-Winget "astral-sh.uv" "uv" }
    $vpy = Join-Path $PSScriptRoot "strumenti\.voce\Scripts\python.exe"
    $pacchetti = @("supertonic==1.3.1", "kokoro-onnx==0.6.1", "faster-whisper==1.2.1", "scipy==1.18.1", "numpy==2.5.4", "soundfile==0.14.0")  # versiones probadas (07/11/2026)
    if (Get-Command uv -ErrorAction SilentlyContinue) {
      if (-not (Test-Path $vpy)) { uv venv strumenti\.voce --python 3.12 | Out-Host }
      uv pip install --python $vpy @pacchetti | Out-Host
    } else {
      Write-Host "No hay uv: uso el Python que tienes ($exe). Si los paquetes no se instalan, instala Python 3.12."
      if (-not (Test-Path $vpy)) { & $exe -m venv strumenti\.voce }
      & $vpy -m pip install --upgrade pip | Out-Host
      & $vpy -m pip install @pacchetti | Out-Host
    }
    if (Test-Path $vpy) {
      Write-Host "Descargo los pesos de la voz y de Whisper (una sola vez)..."
      & $vpy strumenti\voce_locale.py prepara supertonic kokoro-onnx --whisper small | Out-Host
      if ($LASTEXITCODE -ne 0) { $ok = $false }
    } else { $ok = $false }
  }
  $lezioni = if ($ok) { "listas (voz gratuita Supertonic 3 / Kokoro)" } else { "NO listas: mira los mensajes de arriba (python strumenti\diagnosi.py)" }
}

$porta = (& $exe -c "import json; c=json.load(open('config.esempio.json',encoding='utf-8')); c.update(json.load(open('config.json',encoding='utf-8'))); print(c.get('porta',8765))").Trim()
$script = Join-Path $PSScriptRoot "accademia.py"

if (-not $SenzaAvvio) {
  # acceso directo en la carpeta Inicio: arranca al iniciar sesión, sin ventanas (pythonw)
  $avvio = [Environment]::GetFolderPath("Startup")
  $lnk = Join-Path $avvio "Open Escool.lnk"
  $sh = New-Object -ComObject WScript.Shell
  $c = $sh.CreateShortcut($lnk)
  $c.TargetPath = $pyw
  $c.Arguments = "`"$script`" --silenzioso"
  $c.WorkingDirectory = $PSScriptRoot
  $c.WindowStyle = 7
  $c.Description = "Servidor local de Open Escool"
  $c.Save()
  Write-Host "Inicio con Windows: activo (para quitarlo borra $lnk)"
}
Start-Process -FilePath $pyw -ArgumentList "`"$script`"", "--silenzioso" -WorkingDirectory $PSScriptRoot -WindowStyle Hidden
Start-Sleep -Seconds 2

& $exe strumenti\chiavi.py stato
$url = "http://127.0.0.1:$porta"
& $exe -c "import sys, accademia; sys.exit(0 if accademia.e_accademia($porta) else 1)"
if ($LASTEXITCODE -ne 0) { Write-Host "Open Escool no responde en $url (si el puerto ya lo usa otro programa, cambia 'porta' en config.json)"; exit 1 }
Write-Host "Open Escool ya funciona en $url"
Write-Host "Lecciones generadas: $lezioni"
Write-Host "Icono en Inicio: en Edge o Chrome, tres puntos ... -> Aplicaciones -> 'Instalar Open Escool' (o el icono + de la barra de direcciones)."
if (-not $env:ACCADEMIA_SENZA_BROWSER) { Start-Process $url }

@echo off
setlocal

cd /d "%~dp0.."
echo [SOVEREIGN] Requesting local process stop...
powershell -NoProfile -Command "Get-Process ollama -ErrorAction SilentlyContinue | Stop-Process -Force"
powershell -NoProfile -Command "Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force"

if exist "%ProgramFiles%\NVIDIA Corporation\NVSMI\nvidia-smi.exe" (
  echo [SOVEREIGN] Attempting VRAM flush via nvidia-smi --gpu-reset
  "%ProgramFiles%\NVIDIA Corporation\NVSMI\nvidia-smi.exe" --gpu-reset >nul 2>&1
)

echo [SOVEREIGN] Setting dashboard state to offline...
python -c "import json, pathlib; p=pathlib.Path('public/state.json'); d=json.loads(p.read_text(encoding='utf-8')); d['status']='offline'; p.write_text(json.dumps(d, indent=2), encoding='utf-8')"

echo [SOVEREIGN] Committing consensus logs snapshot...
git add memory/shared_context.json public/state.json
git commit -m "chore: persist sovereign consensus logs" >nul 2>&1

echo [SOVEREIGN] Stop sequence complete.
endlocal

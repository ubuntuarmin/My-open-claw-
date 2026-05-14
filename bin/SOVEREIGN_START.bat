@echo off
setlocal

cd /d "%~dp0.."
echo [SOVEREIGN] Pulling latest repository state...
git pull

echo [SOVEREIGN] Initializing shared memory blackboard...
python -c "from orchestrator.shared_memory import SharedMemoryEngine; SharedMemoryEngine().initialize()"

echo [SOVEREIGN] Opening dashboard at http://localhost:4173/dashboard/
start "Sovereign Dashboard" "http://localhost:4173/dashboard/"
start "Sovereign Dashboard Server" cmd /k python -m http.server 4173

endlocal

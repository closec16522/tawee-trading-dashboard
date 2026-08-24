import subprocess
import sys
with open('backend.log', 'w', encoding='utf8') as f:
    subprocess.Popen([sys.executable, 'mt5_backend/agent_orchestrator.py'], stdout=f, stderr=f)

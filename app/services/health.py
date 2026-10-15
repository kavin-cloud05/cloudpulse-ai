import re
import subprocess
from pathlib import Path

# Path to the Bash script from Phase 1
SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "server-health.sh"

# Script exit code -> overall status
STATUS = {0: "ok", 1: "warning", 2: "critical"}

# Matches lines like: CPU:     0%  [OK]
LINE = re.compile(r"^(CPU|Memory|Disk /):\s+(\d+)%\s+\[(\w+)\]", re.MULTILINE)


def run_health_check():
    """Run the health script and return its result as a dictionary."""
    result = subprocess.run(
        [str(SCRIPT)], capture_output=True, text=True, timeout=15
    )
    metrics = {}
    for name, value, level in LINE.findall(result.stdout):
        metrics[name.split()[0].lower()] = {
            "percent": int(value),
            "level": level.lower(),
        }
    return {
        "overall": STATUS.get(result.returncode, "unknown"),
        "metrics": metrics,
        "report": result.stdout,
    }

import os
import sys
from pathlib import Path

# Add backend directory to sys.path so app modules are always found
root_dir = Path(__file__).resolve().parent
backend_dir = root_dir / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import uvicorn

if __name__ == "__main__":
    raw_port = os.environ.get("PORT", "10000")
    try:
        port = int(raw_port)
    except (ValueError, TypeError):
        port = 10000

    print(f"--> CourseGuide AI launching on 0.0.0.0:{port}...", flush=True)
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="info")

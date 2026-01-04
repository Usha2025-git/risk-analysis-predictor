#!/usr/bin/env python3
"""Run the FastAPI backend server."""
import sys
import os

# Ensure imports work from any CWD.
# We add the repo root to sys.path so `backend.app.*` is importable and does not
# conflict with the repo-root `app.py`.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from backend.app.main import app
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)

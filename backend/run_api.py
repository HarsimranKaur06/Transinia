"""
Start the Transinia API server
"""
import os
import sys

# Add the project root to the path (allows `python run_api.py` from backend/ or repo root)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.src.api import run_api


if __name__ == "__main__":
    run_api(port=8001)

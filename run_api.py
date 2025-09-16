"""
Start the Transinia API server
"""

from src.api import run_api

if __name__ == "__main__":
    run_api(port=8001)

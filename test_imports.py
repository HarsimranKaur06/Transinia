"""
Test imports for the API server
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import fastapi
    print(f"FastAPI import successful! Version: {fastapi.__version__}")
except ImportError as e:
    print(f"FastAPI import failed: {e}")

try:
    from src.api import run_api
    print("API import successful!")
except ImportError as e:
    print(f"API import failed: {e}")
    import traceback
    traceback.print_exc()
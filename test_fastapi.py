"""
Test if FastAPI can be imported
"""

try:
    import fastapi
    print(f"FastAPI version: {fastapi.__version__}")
    print("FastAPI import successful!")
except ImportError as e:
    print(f"Failed to import FastAPI: {e}")
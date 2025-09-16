"""
Module entry point to support 'python -m src' execution.
Using this approach avoids conflicts with other Python packages.
"""

from src.app import main

if __name__ == "__main__":
    main()

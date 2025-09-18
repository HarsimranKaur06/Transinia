#!/usr/bin/env python
"""
Transinia - Meeting Transcript Analyzer
--------------------------------------
Wrapper script to run the application from the project root.
"""

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from src.app
from backend.src.app import main

if __name__ == "__main__":
    main()

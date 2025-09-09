"""
FILE PATH MANAGEMENT UTILITY
--------------------------
This file defines all file and directory paths used by the application.
It provides:

1. ROOT - The absolute path to the project root directory
2. SAMPLES_DIR - Location where transcript samples are stored
3. OUTPUTS_DIR - Directory where generated outputs are saved
4. TRANSCRIPT_TXT - Path to the default transcript file
5. MINUTES_MD - Path where meeting minutes will be saved
6. ACTIONS_JSON - Path where action items will be saved

Using Path objects from the pathlib library ensures cross-platform
compatibility for all file operations, regardless of operating system.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SAMPLES_DIR = ROOT / "samples"
OUTPUTS_DIR = ROOT / "outputs"

TRANSCRIPT_TXT = SAMPLES_DIR / "transcript.txt"
MINUTES_MD = OUTPUTS_DIR / "minutes.md"
ACTIONS_JSON = OUTPUTS_DIR / "actions.json"

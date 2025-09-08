from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SAMPLES_DIR = ROOT / "samples"
OUTPUTS_DIR = ROOT / "outputs"

TRANSCRIPT_TXT = SAMPLES_DIR / "transcript.txt"
MINUTES_MD = OUTPUTS_DIR / "minutes.md"
ACTIONS_JSON = OUTPUTS_DIR / "actions.json"

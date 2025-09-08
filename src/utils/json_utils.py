import json
import re
from typing import Any, Dict

def robust_json_parse(text: str) -> Dict[str, Any]:
    """Try strict JSON, else extract first {...} block."""
    try:
        return json.loads(text)
    except Exception:
        pass
    m = re.search(r"\{.*\}", text, flags=re.S)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            return {}
    return {}

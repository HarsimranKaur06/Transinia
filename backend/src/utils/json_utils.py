"""
JSON PARSING UTILITY FUNCTIONS
----------------------------
This file provides specialized JSON handling functionality.
It contains:

1. The robust_json_parse() function which:
   - Attempts to parse standard JSON text
   - Falls back to regex extraction if standard parsing fails
   - Handles common formatting issues in AI-generated JSON
   - Returns empty objects rather than raising errors
   
This utility makes the application more resilient when working with
JSON data that might be imperfectly formatted, especially important
when processing AI outputs that don't always produce perfect JSON.
"""

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

import json
import re

SUGGESTION_KEY_PHRASES = [
    "would you like",
    "should i",
    "do you want",
    "want me to",
    "shall i",
    "do you want me to",
    "would you like me to",
]
SUGGESTION_RE = re.compile(
    r"(?i)\b(?:" + "|".join(re.escape(p) for p in SUGGESTION_KEY_PHRASES) + r")\b.*\?$"
)


def extract_text(node):
    """
    Robustly return the most plausible textual content from a message node.
    node can be:
      - mapping entry value: {"message": {...}, ...}
      - message dict itself: {"id": "...", "author": {...}, "content": {...}, ...}
      - None or other unexpected shapes

    Strategy:
      - normalize to message dict if wrapped in {"message": ...}
      - get content = message.get("content") (must be dict) or fallback to message.get("parts")
      - find last non-empty part (string preferred). If a part is dict, try common keys
        ('text','content','replacement','message') or nested 'parts'.
      - fallback: json.dumps(part) or str(part)
    """
    if node is None:
        return ""

    # If the wrapper contains "message", use that; otherwise assume node is message
    if (
        isinstance(node, dict)
        and "message" in node
        and isinstance(node["message"], dict)
    ):
        msg = node["message"]
    elif isinstance(node, dict):
        msg = node
    else:
        # Unexpected type (e.g., string) — return its string form
        return str(node).strip()

    # Safe get content (may be None or non-dict)
    content = msg.get("content") if isinstance(msg, dict) else None

    # Try several places where parts could live
    parts = None
    if isinstance(content, dict):
        parts = content.get("parts")
    # Older/alternate layouts may put parts on the message itself
    if not parts:
        parts = msg.get("parts") if isinstance(msg, dict) else None
    if not parts:
        return ""

    # Ensure parts is a list
    if not isinstance(parts, list):
        # sometimes it's a single string
        if isinstance(parts, str):
            return parts.strip()
        return ""

    # Iterate parts in reverse (take most recent / last part)
    for part in reversed(parts):
        if part is None:
            continue
        if isinstance(part, str):
            if part.strip():
                return part.strip()
            continue
        if isinstance(part, dict):
            # try common text-like keys inside this dict
            for key in ("text", "content", "replacement", "message"):
                val = part.get(key)
                if isinstance(val, str) and val.strip():
                    return val.strip()
                # if val is list, consider last element
                if isinstance(val, list) and val:
                    last = val[-1]
                    if isinstance(last, str) and last.strip():
                        return last.strip()
            # nested 'parts' in the dict
            nested = part.get("parts")
            if isinstance(nested, list):
                for p in reversed(nested):
                    if isinstance(p, str) and p.strip():
                        return p.strip()
            # fallback: try to stringify compactly
            try:
                return json.dumps(part, ensure_ascii=False)
            except Exception:
                return str(part)
        # other types: convert to string
        try:
            s = str(part)
            if s.strip():
                return s.strip()
        except Exception:
            continue

    # nothing found
    return ""


def extract_suggestion(node):
    """
    Return suggestion string if node (message) contains assistant suggestion in last line,
    otherwise return empty string.
    Uses extract_text() and a heuristic regex.
    """
    text = extract_text(node)
    if not text:
        return ""
    # examine last non-empty line
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return ""
    last = lines[-1]
    # match heuristic: contains key phrase and ends with a question mark
    if SUGGESTION_RE.search(last):
        return last
    # also accept polite offers with no question mark (optional; comment/uncomment)
    # if any(k in last.lower() for k in SUGGESTION_KEY_PHRASES):
    #     return last
    return ""

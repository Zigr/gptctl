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
    "let me know",
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
    if any(k in last.lower() for k in SUGGESTION_KEY_PHRASES):
        return last
    return ""


def analyze_conversations(data):
    rows = []
    for conv in data:
        title = conv.get("title", "Untitled")
        # print(f"Analyzing conversation: {title}")
        mapping = conv.get("mapping", {})

        if not isinstance(mapping, dict):
            continue

        # print(f"Total messages in mapping: {len(mapping)}")
        sorted_msgs = sorted(mapping.values(), key=lambda x: x.get("create_time", 0))
        # print(f"Total sorted messages: {len(sorted_msgs)}")
        previous_user_msg = None

        for msg in sorted_msgs:
            m_obj = msg.get("message", {})
            message_id = msg.get("id", "unknown")
            # print(f"Message object: {m_obj}")

            if m_obj is None:
                print(f"Skipping message ID {message_id} with no content.")
                continue

            role = m_obj.get("author", {}).get("role")
            text = extract_text(m_obj)
            if not text:
                continue

            # print(
            #     f"Processing message ID {message_id} with role {role} created at {m_obj.get('create_time', 0)} text: {text[:30]}..."
            # )

            if role == "user":
                previous_user_msg = text
                rows.append(
                    {
                        "conversation_title": title,
                        "message_id": message_id,
                        "role": "user",
                        "message_text": text,
                        "paired_user_message": text,
                        "paired_assistant_suggestion": "",
                    }
                )
                # print(rows)
                # break

            elif role == "assistant":
                suggestion = extract_suggestion(msg)
                if suggestion:
                    rows.append(
                        {
                            "conversation_title": title,
                            "message_id": message_id,
                            "role": "assistant",
                            "message_text": suggestion,
                            "paired_user_message": previous_user_msg or "",
                            "paired_assistant_suggestion": suggestion,
                        }
                    )
    return rows


def export_markdown(rows):
    md_lines = ["### 🧩 User ↔ Assistant Suggestion Pairs\n"]
    md_lines.append(
        "| Conversation | Role | Message ID | Message Text | Paired User Message | Assistant Suggestion |"
    )
    md_lines.append(
        "|--------------|------|-------------|---------------|----------------------|----------------------|"
    )
    for r in rows[:50]:  # limit output
        md_lines.append(
            f"| {r['conversation_title']} | {r['role']} | {r['message_id']} | {r['message_text'][:40]} | {r['paired_user_message'][:40]} | {r['paired_assistant_suggestion'][:40]} |"
        )
    return "\n".join(md_lines)

from datetime import datetime
import os
from pathlib import Path
import re
import textwrap
import time
from typing import Any, Dict, List, Optional
import json
from rich.console import Console
from rich.table import Table
import typer
from gptctl.definitions import Conversation, SortFields, SortOrder


FENCED_CODE_RE = re.compile(r"```[\s\S]*?```", re.MULTILINE)
ELIPSIS = "..."


def sanitize_filename(name: str) -> str:
    name = re.sub(r"[^\w\-_]+", "_", name)
    return name.strip("_") or "untitled"


def make_filename(
    title: str, created: str, index: int, prefix_with_date: bool = False
) -> str:
    safe_title = sanitize_filename(title[:50]) or f"untitled-{index}"
    if prefix_with_date and created:
        dt = parse_timestamp(created)
        if isinstance(dt, datetime):
            date_prefix = dt.strftime("%Y-%m-%d")
            return f"{date_prefix}_{safe_title}.md"
    return f"{safe_title}.md"


def windows_to_unix_eol(content: str) -> str:
    old_newline_var: str = "\x0d\x0a"
    new_content = content.replace(old_newline_var, "\n")
    return new_content.strip()


def format_timestamp(ts) -> str:
    if not ts:
        return ""
    try:
        dt = datetime.fromtimestamp(float(ts))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        try:
            dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return str(ts)


def parse_timestamp(ts) -> datetime | str:
    if not ts:
        return ""
    try:
        return datetime.fromtimestamp(float(ts))
    except Exception:
        try:
            return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        except Exception:
            return ""


def get_created_date(conv: dict) -> str:
    created = conv.get("create_time") or conv.get("created") or ""
    dt = parse_timestamp(created)
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d")
    return ""


def find_by_title(conversations: List[dict], title: str) -> Any:
    for conv in conversations:
        if conv.get("title") == title:
            return conv
    return None

def find_msg_by_title(mapping: Dict[str, Any], title: str) -> Optional[str]:
    """finds message by title in one thread

    Args:
        mapping (Dict[str, Any]): Message thread mapping given
        title (str): message title

    Returns:
        Optional[str]: message id or None
    """
    for mid, obj in mapping.items():
        msg = obj.get("message", {})
        msg_title = msg.get("metadata", {}).get("title")
        if msg_title and title.lower() in msg_title.lower():
            return mid
    return None

def md_anchor(title: str,truncate_length:Optional[int] =80) -> str:
    """Sanitize text suitable for a Markdown anchor link.

    Args:
        title (str): text part of the anchor

    Returns:
        str: sanitized anchor text suitable for markdown links
    """
    anchor = title.strip().lower()
    anchor = re.sub(r"[^\w\s-]", "", anchor)
    anchor = re.sub(r"\s+", "-", anchor)
    return anchor.strip("-").strip(ELIPSIS) or "untitled"


def looks_like_json(s: str) -> bool:
    """Heuristic: check if a string looks like JSON."""
    s = s.strip()
    return (s.startswith("{") and s.endswith("}")) or (
        s.startswith("[") and s.endswith("]")
    )


def try_load_json(s: str):
    try:
        return json.loads(s)
    except Exception:
        return None


def handle_code_content(type_: str, content: str) -> str:
    """Handle code/JSON content properly."""
    lang = type_.split("/", 1)[1] if "/" in type_ else ""

    # Auto-detect JSON strings
    if lang in ("json", "javascript"):  # extendable
        try:
            parsed = json.loads(content)
            pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
            return f"```{lang}\n{pretty}\n```"
        except Exception:
            pass

    return f"```{lang}\n{content.strip()}\n```"


def extract_strings(obj: Any) -> List[str]:
    if isinstance(obj, str):
        return [obj]

    if isinstance(obj, dict):
        for k in ("text", "description", "title", "body"):
            v = obj.get(k)
            if isinstance(v, str) and v.strip():
                return [v]
        if "content" in obj:
            return extract_strings(obj["content"])
        if "parts" in obj:
            return extract_strings(obj["parts"])
        if "updates" in obj:
            out: List[str] = []
            for upd in obj["updates"]:
                out.extend(extract_strings(upd.get("replacement")))
            return out
        out: List[str] = []
        for v in obj.values():
            if isinstance(v, (dict, list)):
                out.extend(extract_strings(v))
        return out

    if isinstance(obj, list):
        out: List[str] = []
        for item in obj:
            out.extend(extract_strings(item))
        return out

    return []


def extract_json_fragments(text: str):
    """
    Scan text and yield (start, end, snippet) for balanced {...} or [...] fragments.
    """
    results = []
    stack = []
    start_idx = None

    for i, ch in enumerate(text):
        if ch in "{[":
            if not stack:  # new fragment starts
                start_idx = i
            stack.append(ch)
        elif ch in "}]":
            if stack:
                opening = stack.pop()
                # simple validation of match
                if (opening == "{" and ch != "}") or (opening == "[" and ch != "]"):
                    # mismatched brackets → reset
                    stack = []
                    start_idx = None
                elif not stack and start_idx is not None:
                    snippet = text[start_idx : i + 1]
                    results.append((start_idx, i + 1, snippet))
                    start_idx = None
    return results


def replace_inline_json(text: str) -> str:
    """
    Replace balanced inline JSON fragments with fenced ```json blocks.
    """
    fragments = extract_json_fragments(text)
    if not fragments:
        return text

    out = []
    last = 0
    for start, end, snippet in fragments:
        # add preceding text
        out.append(text[last:start])

        obj = None
        try:
            obj = json.loads(snippet)
        except Exception:
            pass

        if obj is not None:
            pretty = json.dumps(obj, indent=2, ensure_ascii=False)
            out.append("\n```json\n" + pretty + "\n```\n")
        else:
            out.append(snippet)  # leave as-is if not valid JSON

        last = end

    out.append(text[last:])
    return "".join(out)


def truncate_string_with_ellipsis(text, length, placeholder="..."):
    """
    Truncates a string to a specified length, respecting word boundaries
    and adding an ellipsis if truncated.

    Args:
        text (str): The input string to truncate.
        length (int): The maximum desired length of the truncated string.

    Returns:
        str: The truncated string with ellipsis if necessary.
    """
    return textwrap.shorten(text, width=length, placeholder=placeholder)


def get_messages_iter(conv: dict):
    # Support messages in different structures
    for key in ("mapping", "messages", "items", "chat", "message_list", "updates"):
        if key in conv and conv[key] is not None:
            val = conv[key]
            if isinstance(val, dict):
                for entry in val.values():
                    if isinstance(entry, dict):
                        if "message" in entry and isinstance(entry["message"], dict):
                            # HERE we process messages
                            yield entry["message"]
                        elif "author" in entry and "content" in entry:
                            yield entry
                        else:
                            for v in entry.values():
                                if (
                                    isinstance(v, dict)
                                    and "author" in v
                                    and "content" in v
                                ):
                                    yield v
                                    break
                return
            elif isinstance(val, list):
                for item in val:
                    if isinstance(item, dict):
                        if "message" in item and isinstance(item["message"], dict):
                            yield item["message"]
                        elif "author" in item and "content" in item:
                            yield item
                        else:
                            for v in item.values():
                                if (
                                    isinstance(v, dict)
                                    and "author" in v
                                    and "content" in v
                                ):
                                    yield v
                                    break
                return
    # Fallback: scan all dict values
    for v in conv.values():
        if isinstance(v, dict) and "author" in v and "content" in v:
            yield v


def stringify_part(part, collapse_threshold=40) -> str:
    # 1) dict-like part
    if isinstance(part, dict):
        # code blocks
        t = part.get("type") or part.get("content_type", "")
        content = part.get("content") or part.get("text") or ""
        if t and t.startswith("code/"):
            lang = t.split("/", 1)[1] or "text"
            code = content.strip()
            lines = code.splitlines()
            fenced = f"```{lang}\n{code}\n```"
            if len(lines) > collapse_threshold:
                return f"<details><summary>Show {lang} code ({len(lines)} lines)</summary>\n\n{fenced}\n\n</details>"
            return fenced
        # images / urls
        if part.get("image_url") or part.get("url"):
            url = part.get("image_url") or part.get("url")
            alt = part.get("alt_text", "")
            return f"![{alt}]({url})"
        # updates => recurse replacements
        if "updates" in part and isinstance(part["updates"], list):
            out = []
            for upd in part["updates"]:
                rep = upd.get("replacement")
                pattern = upd.get("pattern", "N/A")
                lang = "text"
                if rep:
                    out.append(
                        f"**Updated Pattern:** `{pattern}`\n\n```{lang}\n{rep}\n```"
                    )
            return "\n\n".join(out)
        # nested parts
        if "parts" in part and isinstance(part["parts"], list):
            return "\n\n".join(
                [stringify_part(p, collapse_threshold) for p in part["parts"]]
            )
        # fallback prefer text/content
        if content:
            return replace_inline_json(content)
        return json.dumps(part, ensure_ascii=False, indent=2)  # last resort

    # 2) string-like part
    if isinstance(part, str):
        s = part.strip()
        # if full JSON string
        if looks_like_json(s):
            obj = try_load_json(s)
            if isinstance(obj, dict):
                return stringify_part(obj, collapse_threshold)
            # pretty print data
            return (
                "```json\n" + json.dumps(obj, indent=2, ensure_ascii=False) + "\n```"
                if obj is not None
                else s
            )
        # preserve fenced code blocks if present
        if FENCED_CODE_RE.search(s):
            # preserve as-is, but still replace inline JSON inside non-code regions
            pieces = []
            last = 0
            for m in FENCED_CODE_RE.finditer(s):
                pre = s[last : m.start()]
                if pre.strip():
                    pieces.append(replace_inline_json(pre))
                pieces.append(m.group(0))  # keep code block verbatim
                last = m.end()
            tail = s[last:]
            if tail.strip():
                pieces.append(replace_inline_json(tail))
            return "\n\n".join(pieces)
        # otherwise replace inline JSON fragments (if any)
        return replace_inline_json(s)

    # fallback
    return str(part)


def make_bookmark(
    title: str = "",
    created: str = "",
    url: str = "https://www.example.com",
    tags: Optional[list] = None,
    keywords: Optional[list] = None,
) -> str:
    bookmark = {
        "title": title,
        "url": url,
        "tags": tags,
        "keywords": keywords,
        "created": created,
    }
    bkm = ""
    for key, value in bookmark.items():
        if isinstance(value, list):
            bkm += f"**{key}**: {', '.join(value)}\n\n"
        else:
            bkm += f"**{key}**: {value}\n\n"
    return bkm


def conversation_to_md(
    conv: dict, anchor: str = "", skip_system: bool = True, truncate_length: int = 80
) -> tuple[list, str]:
    title = conv.get("title") or conv.get("name") or "Untitled"
    created = conv.get("create_time") or conv.get("created") or ""

    thread_toc: List[Dict[str,str]] = []
    lines: List[str] = []

    for msg in get_messages_iter(conv):
        metadata = msg.get("metadata", {})
        is_visually_hidden_from_conversation = metadata.get(
            "is_visually_hidden_from_conversation", False
        )

        role = (
            (msg.get("author") or {}).get("role", "unknown")
            if isinstance(msg.get("author"), dict)
            else msg.get("author", "unknown")
        )

        if skip_system and (
            role == "system"
            or role == "error_reporting_system"
            or role == "tool"
            or is_visually_hidden_from_conversation
        ):
            # Skip system messages
            continue

        content = msg.get("content", msg)
        parts = []
        if isinstance(content, dict):
            parts = content.get("parts") or [content]
        elif isinstance(content, list):
            parts = content
        elif isinstance(content, str):
            parts = [content]

        text = "\n\n".join([stringify_part(p) for p in parts if p])
        if not text.strip():
            continue

        if role == "user":
            msg_text = text.replace("\n", " ").strip()
            # TODO: -> to structure in order to be sorted
            msg_created = format_timestamp(msg.get("create_time", "")) or ""
            thread_toc.append({"content":msg_text,"created":msg_created, "link":md_anchor(msg_text,truncate_length)})
            lines.append(f'<a id="{md_anchor(msg_text)}"></a>\n**You:**\n{text}\n')
        elif role == "assistant":
            lines.append(f"**Assistant:**\n{text}\n")
        else:
            lines.append(f"**{str(role).capitalize()}:**\n{text}\n")

    lines = ["## Conversation TOC"] + lines

    # Make bookmark text
    bkm = make_bookmark(
        title=title,
        created=format_timestamp(created),
        url=f"#{anchor}",
        tags=["to be implemented", "another-tag"],
        keywords=["keyword1", "keyword2"],
    )
    lines = [bkm] + lines

    # Title / H1
    lines = [f"# {title}\n"] + lines
    if anchor:
        lines = [f'<a id="{anchor}"></a>\n'] + lines

    # Whole Content
    thread_content = "\n".join(lines).strip() + "\n"

    return (thread_toc, thread_content)


def thread_msg_count(conv: dict, anchor: str = "", skip_system: bool = True) -> int:
    msg_count = 0

    for msg in get_messages_iter(conv):
        metadata = msg.get("metadata", {})
        is_visually_hidden_from_conversation = metadata.get(
            "is_visually_hidden_from_conversation", False
        )

        role = (
            (msg.get("author") or {}).get("role", "unknown")
            if isinstance(msg.get("author"), dict)
            else msg.get("author", "unknown")
        )

        if skip_system and (
            role == "system"
            or role == "error_reporting_system"
            or role == "tool"
            or is_visually_hidden_from_conversation
        ):
            # Skip system messages
            continue

        content = msg.get("content", msg)
        parts = []
        if isinstance(content, dict):
            parts = content.get("parts") or [content]
        elif isinstance(content, list):
            parts = content
        elif isinstance(content, str):
            parts = [content]

        text = "\n\n".join([stringify_part(p) for p in parts if p])
        if not text.strip():
            continue

        if role == "user":
            msg_count += 1

    return msg_count


def collect_conv(
    conversations: List[dict[Any, Any]],
    titles: list = [],
    skip_system: bool = True,
    console: Optional[Console] = None,
) -> List[Conversation]:
    conv_coll = []
    if len(titles):
        for t in titles:
            verified = find_by_title(conversations, t)
            if not verified:
                if console:
                    console.print(
                        f"[red]The title [bold]'{t}'[/bold] not found in conversations file[/red]"
                    )
                continue
            conv_coll.append(verified)
    else:
        conv_coll = conversations

    conv_objs = []
    for conv in conv_coll:
        msg_count = thread_msg_count(conv, "", skip_system=skip_system)
        conv_obj = Conversation(
            title=conv.get("title") or conv.get("name", "Untitled"),
            created=get_created_date(conv),
            count=msg_count,
            conversation=conv,
        )
        conv_objs.append(conv_obj)
    return conv_objs


def sort_conv(
    data: List[Conversation] = [],
    sort: SortFields = SortFields.NO_SORT,
    order: SortOrder = SortOrder.ASC,
) -> list:
    if sort and sort != SortFields.NO_SORT:
        key_cbk = (
            (lambda c: c[sort])
            if sort != SortFields.CREATED
            else (lambda c: parse_timestamp(c[sort]) or datetime.min)
        )
        conv_sorted = sorted(
            data,
            key=key_cbk,
            reverse=(order == SortOrder.DESC),
        )
        return conv_sorted
    else:
        return data

def is_jinja_template_string(s: str) -> bool:
    """
    Checks if a string contains common Jinja2 template syntax.
    This function looks for variable delimiters ({{...}}) and
    statement/tag delimiters ({%...%}).
    """
    # Search for variable delimiters
    if re.search(r'\{\{.*?\}\}', s):
        return True
    # Search for statement/tag delimiters
    if re.search(r'\{%.*?%\}', s):
        return True
    return False


def create_rich_table(
    input_file: str = "",
    sort: SortFields = SortFields.NO_SORT,
    order: SortOrder = SortOrder.ASC,
) -> Table:
    table = Table(
        title=f"File: [bold green]{input_file}[/bold green] ({'Not sorted' if sort == SortFields.NO_SORT else 'Sorted by' + ' [bold green]' + sort.value + '[/bold green]' + ' [bold green]' + order.value.upper() + '[/bold green]'})"
    )
    table.add_column("#", justify="center")
    table.add_column("Title")
    table.add_column("Created")
    table.add_column("Message Count", justify="right")

    return table


def get_batch_filepath(
    output_dir: str = "./",
    with_date_prefix: bool = False,
    number: int = 1,
    sort: SortFields = SortFields.NO_SORT,
    order: SortOrder = SortOrder.ASC,
    rec_count: int = 0,
    format: str = "json",
):
    cur_ts = time.time()
    date_prefix = format_timestamp(cur_ts)
    filename_tpl = """{date_prefix}-batch_{number}-{sort}-{order}-{rec_count}_items"""
    filename = (
        sanitize_filename(
            filename_tpl.format(
                date_prefix=date_prefix,
                number=number,
                sort=sort,
                order=order,
                rec_count=rec_count,
            )
        ).lower()
        + f".{format}"
    )
    filepath = os.path.join(output_dir, filename)
    return filepath


def get_batch_list(lst: list = [], chunk_size: int = 0):
    """
    Chunks a list into sublists of size chunk_size using a generator.
    If the list length is not a multiple of chunk_size, the last sublist will contain the remaining elements.

    # Example usage:
        my_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        chunk_size = 3
        for chunk in get_batch_list(lst=my_list, chunk_size=chunk_size):
        print(chunk)

    # To get a list of all chunks:
        chunked_list = list(get_batch_list(my_list, chunk_size))
        print(chunked_list)
    """
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]


def get_filepath(
    conv: dict,
    output_dir: str = "./",
    number: int = 1,
    with_date_prefix: bool = False,
    format: str = "json",
) -> str:
    if with_date_prefix:
        format_str = "%Y-%m-%d"
        dt = parse_timestamp(get_created_date(conv))
        if dt and isinstance(dt, datetime):
            date_prefix = dt.strftime(format_str) + "_"
        elif dt and isinstance(dt, str):
            dt_obj = datetime.strptime(dt, format_str)
            date_prefix = dt_obj.strftime(format_str) + "_"
        else:
            date_prefix = ""
    else:
        date_prefix = ""

    if isinstance(conv, dict):
        title = conv.get("title", "untitled")
    elif isinstance(conv, Conversation):
        title = conv.conversation.get("title", "untitled")
    else:
        "untitled"

    filename = sanitize_filename(f"{date_prefix}{title}-{number}") + f".{format}"
    filepath = os.path.join(output_dir, filename)
    return filepath


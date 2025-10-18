import json
from pathlib import Path
import typer

app = typer.Typer(help="ChatGPT conversation export CLI")


@app.command("partial")
def thread_partial (
    thread: str = typer.Option(None, help="Thread ID (optional, auto-detected)"),
    start: str = typer.Option(..., help="Start message title or ID"),
    end: str = typer.Option(None, help="End message title or ID (optional)"),
    include_children: bool = typer.Option(
        False, "--include-children", help="Include children recursively"
    ),
    depth: int = typer.Option(None, "--depth", help="Limit child recursion depth"),
    context_limit: int = typer.Option(
        None, "--context-limit", help="Limit number of ancestors to include"
    ),
    output_format: str = typer.Option(
        "markdown", "--format", help="Output format: markdown or text"
    ),
    data_file: Path = typer.Option(
        Path("conversations.json"), help="Path to ChatGPT export JSON file"
    ),
):
    """
    Export a range or subtree of messages, preserving parent-child structure and chronology.
    Example Usage:
    chatgptctl export --start "AI Agentic Workflows" --end "Dust / Pydust" --include-children --depth 2 --context-limit 3 --format markdown
    """
    data = json.loads(data_file.read_text())
    messages = {
        m["id"]: m for t in data for m in t["mapping"].values() if "message" in m
    }

    def find_by_key(key):
        for msg in messages.values():
            if msg["message"].get("id") == key or msg["message"].get("title") == key:
                return msg
        return None

    start_msg = find_by_key(start)
    if not start_msg:
        typer.echo(f"Start message '{start}' not found")
        raise typer.Exit(1)

    # Auto-detect thread root
    if not thread:
        root = start_msg
        while root.get("parent") and root["parent"] in messages:
            root = messages[root["parent"]]
        thread = root["message"]["id"]
        typer.echo(f"Auto-detected thread ID: {thread}")

    # Helper: get parent chain (context)
    def get_parents(msg):
        parents = []
        current = msg
        while current.get("parent") and current["parent"] in messages:
            parent = messages[current["parent"]]
            parents.append(parent)
            current = parent
        return (
            list(reversed(parents))[:context_limit]
            if context_limit
            else list(reversed(parents))
        )

    # Helper: get children recursively (with depth)
    def get_children(msg, level=0):
        if depth is not None and level >= depth:
            return []
        children = [
            messages[cid]
            for cid in messages
            if messages[cid].get("parent") == msg["id"]
        ]
        children.sort(key=lambda x: x["message"]["create_time"])
        result = []
        for child in children:
            result.append(child)
            result.extend(get_children(child, level + 1))
        return result

    # Collect messages
    exported = get_parents(start_msg) + [start_msg]
    if end:
        end_msg = find_by_key(end)
        if not end_msg:
            typer.echo(f"End message '{end}' not found")
            raise typer.Exit(1)
        # Include all messages between start and end (inclusive)
        all_sorted = sorted(
            messages.values(), key=lambda x: x["message"]["create_time"]
        )
        start_idx = all_sorted.index(start_msg)
        end_idx = all_sorted.index(end_msg)
        exported += all_sorted[start_idx + 1 : end_idx + 1]

    if include_children:
        exported += get_children(start_msg)

    # Deduplicate + sort chronologically
    exported = sorted(set(exported), key=lambda x: x["message"]["create_time"])

    # Format output
    if output_format == "markdown":
        lines = ["# Exported Conversation\n"]
        for msg in exported:
            role = msg["message"]["author"]["role"]
            content = msg["message"]["content"].get("parts", [""])[0]
            lines.append(f"**{role.capitalize()}:** {content}\n")
        typer.echo("\n".join(lines))
    else:
        for msg in exported:
            content = msg["message"]["content"].get("parts", [""])[0]
            typer.echo(f"{msg['message']['author']['role']}: {content}")


if __name__ == "__main__":
    app()

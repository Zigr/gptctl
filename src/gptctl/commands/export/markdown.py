import os
import typer
from typing import Annotated, List, Optional
import json
from rich.console import Console

from gptctl.definitions import SortFields, SortOrder
from gptctl.utils.utils import (
    collect_conv,
    format_timestamp,
    conversation_to_md,
    make_filename,
    md_anchor,
    sort_conv,
)


app = typer.Typer(
    no_args_is_help=True,
    rich_markup_mode="markdown",
    help="Export conversation(s) from the input conversations.json file to MARKDOWN.",
)


@app.command(name="markdown")
def export_markdown(
    ctx: typer.Context,
    title: Annotated[
        Optional[List[str]],
        typer.Option(
            "--title",
            "-t",
            help="**Title** of the conversation to export. May be used multiple times. Use asterisk('*') to export all titles",
        ),
    ] = None,
    combined: Annotated[
        bool,
        typer.Option(
            "--combined",
            help="Also write ***selected*** or ***all*** conversations in one ***output*** file. Check that you ***output*** OPTION is set correctly.",
        ),
    ] = False,
    combined_index: Annotated[
        bool,
        typer.Option(
            "--combined-index",
            help="Also write ***selected*** or ***all*** conversations in one ***output*** index file with TOC but without content, Check that you ***output*** OPTION is set correctly.",
        ),
    ] = False,
    prefix_with_date: Annotated[
        Optional[bool],
        typer.Option(
            "--prefix-with-date",
            "-p",
            help="Prefix output message(s) *.json files with their creation date.",
            rich_help_panel="Formatting Options",
        ),
    ] = None,
    sort: Annotated[
        SortFields,
        typer.Option("--sort", "-s", case_sensitive=False, help="Sort by field"),
    ] = SortFields.NO_SORT,
    order: Annotated[
        SortOrder,
        typer.Option("--order", "-o", case_sensitive=False, help="Sort order"),
    ] = SortOrder.DESC,
    skip_system: Annotated[
        bool,
        typer.Option("--skip-system / --no-skip-system", help="Skip system messages"),
    ] = True,
):
    """Export one or ___more___ (in a batch) conversations to a ___markdown (\\*.md)___ file(s). :rocket:

    Example Usage:

    ```bash
    # Sort all conversations by created date with **asc**(ending) order
    # and export all conversations from input file **./data/conversations.json** into **./data/conversations-md** directory
    # with file names prefixed by **creation date**
    # and also export these conversations into single combined file **./data/conversations-all.md**

    $ chatgptctl --input ./data/conversations.json --output-dir ./data/conversations-md --output ./data/conversations-all.md .data/conversations-md/ -t * --sort created --order asc --combined --prefix-with-date

    ```
    """
    cfg = ctx.obj["config"]
    input_file = cfg["input_file"]
    output_file = cfg["output_file"]
    output_dir = cfg["output_dir"]
    console: Console = ctx.obj["console"]

    if not title:
        console.print(f"No title(s) provided (raw input = {title})")
        raise typer.Abort()

    os.makedirs(output_dir, exist_ok=True)

    with open(input_file, "r", encoding="utf-8") as f:
        conversations = json.load(f)

        titles = []
    if len(title) and title[0] == "*":
        titles = []
    else:
        titles = title

    conv_objs = collect_conv(
        conversations = conversations,
        titles=titles,
        skip_system=skip_system,
        console=console,
    )
    if not len(conv_objs):
        console.print(f"No title(s) found (raw input = {title})")
        raise typer.Abort()

    conv_sorted = sort_conv(data=conv_objs, sort=sort, order=order)

    combined_lines: List[str] = []
    chronological = " (Chronological)" if sort == SortFields.CREATED else ""
    toc_lines: List[str] = [f"# Table of Contents{chronological}\n"]

    for i, conversation in enumerate(conv_sorted, start=1):
        conv = conversation.get("conversation", {})
        c_title = conv.get("title") or conv.get("name") or f"Untitled-{i}"
        created = conv.get("create_time") or conv.get("created") or ""
        filename = make_filename(c_title, created, i)
        filepath = os.path.join(output_dir, filename)

        anchor = f"{md_anchor(c_title)}-{i}"
        _, md_content = conversation_to_md(conv, anchor=anchor)

        # Export individual file
        with open(filepath, "w", encoding="utf-8", newline="\n") as md:
            md.write(md_content)

        # TOC entry (internal anchor)
        date_str = format_timestamp(created) if created else "Unknown date"
        toc_lines.append(f"- {date_str} — [{title}](#{anchor})")

        if combined:
            # Add content to combined file
            combined_lines.append(md_content)
            combined_lines.append("\n---\n")

    if combined:
        # Write combined Markdown file
        with open(output_file, "w", encoding="utf-8", newline="\n") as big:
            big.write("\n".join(toc_lines) + "\n\n")
            big.write("\n".join(combined_lines))

    console.print(f"✅ Exported {len(conv_sorted)} conversation(s).")
    console.print(f"- Individual files: {output_dir}/")
    if combined:
        console.print(f"- Combined Markdown with TOC: {output_file}")


def main():
    app()


if __name__ == "__main__":
    main()

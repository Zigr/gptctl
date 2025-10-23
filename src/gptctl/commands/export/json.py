import json
import os
from typing import Annotated, Any, List, Optional
from rich.console import Console

import typer
from gptctl.definitions import Conversation, SortFields, SortOrder
from gptctl.utils.utils import (
    collect_conv,
    get_batch_filepath,
    get_batch_list,
    get_filepath,
    sort_conv,
)

app = typer.Typer()


def write_json(data: Any = {}, path: str = "", ensure_linux_lines: bool = True):
    try:
        dirname = os.path.dirname(path)
        os.makedirs(dirname, exist_ok=True)

        if isinstance(data, dict):
            j = data
        elif isinstance(data, Conversation):
            j = data.to_dict()
        elif isinstance(data, list):
            j = []
            for it in data:
                if isinstance(it, dict):
                    j.append(it)
                elif isinstance(it, Conversation):
                    j.append(it.to_dict())
                else:
                    continue
        else:
            return

        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(j, ensure_ascii=False, indent=2))
            f.write("\n")
    except FileNotFoundError:
        print(f"Error: The file '{path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


def write_console(console: Console, data: dict = {}, path: str = "./"):
    dry_run_tpl = """[yellow]Would process conversation: [bold]"{title}[/bold]"
and write to a file: [bold]"{filename}"[/bold][/yellow]
"""
    console.print(
        dry_run_tpl.format(title=data.get("title", "untitled"), filename=path)
    )


def write_console_batch(
    console: Console,
    data: list = [],
    path: str = "./",
    batch_size: int = 0,
    number: int = 0,
):
    dry_run_batch_tpl = """[yellow]Would process in the batch No [bold]{number}[/bold] of {batch_size} conversations per batch 
    and write to a file [bold]"{filename}"[/bold] {qty} records"""
    console.print(
        dry_run_batch_tpl.format(
            number=number, filename=path, batch_size=batch_size, qty=len(data)
        )
    )


@app.command("json")
def export_json(
    ctx: typer.Context,
    title: Annotated[
        Optional[List[str]],
        typer.Option(
            "--title",
            "-t",
            help="**Title** of the conversation to export. May be used multiple times. Use asterisk('*') to export all titles",
        ),
    ] = None,
    batch_size: Annotated[
        int,
        Optional[int],
        typer.Option(
            "--batch",
            "-b",
            help="Export number of ***batch*** conversations in one ***output-file***",
        ),
    ] = 0,
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
    """
    Export one or ___more___ (in a batch) conversations to a ___\\*.json___ file(s). :rocket:

    Example Usage:

    ```bash
    # Export one title
    $ gptctl export json --title My\\ conversation\\ title\\ 10
    # Export several titles
    $ gptctl --output-dir export json -t 'My conversation title 5' -t 'My conversation title 2' -t 'My conversation title 15'
    # Export all titles
    $ gptctl export json --title "*"
    ```
    """
    cfg = ctx.obj["config"]
    input_file = cfg["input_file"]
    output_dir = cfg["output_dir"]
    dry_run = ctx.obj.get("dry_run", False)
    console: Console = ctx.obj["console"]

    if not title:
        console.print(f"[red]No title(s) provided (raw input = {title})[/red]")
        raise typer.Abort()

    with open(input_file, "r", encoding="utf-8") as f:
        conversations = json.load(f)

    titles = []
    if len(title) and title[0] == "*":
        titles = []
    else:
        titles = title

    conv_objs = collect_conv(
        conversations=conversations,
        titles=titles,
        skip_system=skip_system,
        console=console,
    )
    if not len(conv_objs):
        console.print(f"No title(s) found (raw input = {title})")
        raise typer.Abort()
    conv_sorted = sort_conv(data=conv_objs, sort=sort, order=order)

    if batch_size:
        counter = 1
        for chunk in get_batch_list(lst=conv_sorted, chunk_size=batch_size):
            filepath = get_batch_filepath(
                output_dir=output_dir,
                with_date_prefix=True,
                number=counter,
                sort=sort,
                order=order,
                rec_count=len(chunk),
            )
            if dry_run:
                write_console_batch(
                    console=console,
                    data=chunk,
                    path=filepath,
                    batch_size=batch_size,
                    number=counter,
                )
            else:
                write_json(data=chunk, path=filepath)
            counter += 1

        raise typer.Exit(0)

    # Single file
    for i, conv in enumerate(conv_sorted, start=1):
        filepath = get_filepath(
            conv=conv,
            output_dir=output_dir,
            number=i,
            with_date_prefix=prefix_with_date if prefix_with_date else False,
        )
        if dry_run:
            write_console(console=console, data=conv, path=filepath)
        else:
            write_json(data=conv, path=filepath)

    if dry_run:
        write_console(console=console, data=conv, path=filepath)
    else:
        write_json(data=conv, path=filepath)
        console.print(f"✅ Exported to {filepath}")


def main():
    app()


if __name__ == "__main__":
    main()

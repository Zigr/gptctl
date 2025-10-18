import json
from typing import Annotated
import typer
from rich.console import Console

from gptctl.definitions import SortFields, SortOrder
from gptctl.utils.utils import (
    collect_conv,
    format_timestamp,
    create_rich_table,
    sort_conv,
)

app = typer.Typer()


@app.command(
    "list",
    help="List conversations from the ***input OPTION*** conversations.json file. :sparkles:",
)
def list_conversations(
    ctx: typer.Context,
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
    show_table: Annotated[
        bool,
        typer.Option(
            "--table /--no-table",
            "-t /-T",
            help="Show as a table. Otherwise as a comma-separated titles",
        ),
    ] = True,
):
    cfg = ctx.obj["config"]
    verbose = ctx.obj["verbose"]
    input_file = cfg["input_file"]
    console: Console = ctx.obj["console"]

    with open(input_file, "r", encoding="utf-8") as f:
        conversations = json.load(f)
    conv_objs = collect_conv(
        conversations=conversations, skip_system=skip_system, console=console
    )
    conv_sorted = sort_conv(data=conv_objs, sort=sort, order=order)

    if show_table:
        table = create_rich_table(input_file=input_file, sort=sort, order=order)
        for i, cs in enumerate(conv_sorted, start=1):
            msg_count = f"{cs.count} w/o system" if skip_system else f"{cs.count}"
            table.add_row(str(i), cs.title, format_timestamp(cs.created), msg_count)
        console.print(table)
    else:
        separated = []
        for cs in conv_sorted:
            separated.append(cs.title)
        console.print("Conversations:" if verbose >= 1 else "")
        console.print("|".join(separated))

    console.print(f"Total conversations: {len(conversations)}" if verbose >= 1 else "")


def main():
    app()


if __name__ == "__main__":
    main()

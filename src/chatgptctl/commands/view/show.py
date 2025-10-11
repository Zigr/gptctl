import json
from typing import Annotated, Dict, List
import typer
from rich.console import Console
from rich.table import Table

from chatgptctl.utils.utils import conversation_to_md, truncate_string_with_ellipsis

app = typer.Typer()


def create_rich_table(
    title: str, columns: Dict[str, str], rows: List[Dict] = []
) -> Table:
    """
    TODO: -> generalize with templting
    """
    table = Table(title=title)
    for column in columns.keys():
        table.add_column(column)

    # for row in rows:
    #     table.add_row(*[str(lookup(row, key)) for key in columns.values()])

    return table


@app.command(
    "show",
    help="Show conversation details from the ***input OPTION*** conversations.json file. :sparkles:",
)
def show_conversation(
    ctx: typer.Context,
    title: Annotated[str, typer.Argument(help="Title of the conversation to show")],
    toc_only: Annotated[
        bool,
        typer.Option(
            "--toc-only",
            "-toc",
            help="Show user questions of the given converstation only",
        ),
    ] = False,
    skip_system: Annotated[
        bool,
        typer.Option("--skip-system / --no-skip-system", help="Skip system messages"),
    ] = True,
):
    try:
        cfg = ctx.obj["config"]
        input_file = cfg["input_file"]
        line_len = cfg["truncate_len"]
        console: Console = ctx.obj["console"]

        with open(input_file, "r", encoding="utf-8") as f:
            conversations = json.load(f)
        for conv in conversations:
            c_title = conv.get("title") or conv.get("name") or "Untitled"
            found = c_title == title
            if found:
                if toc_only:
                    md_toc_lines = []
                    md_quests, _ = conversation_to_md(conv, "", skip_system)
                    toc_table = create_rich_table(
                        title=f"{c_title} TOC",
                        columns={"#": "No", "Type": "❓", "Content": "", "Created": ""},
                    )
                    for i, md_quest in enumerate(md_quests, start=1):
                        # md_toc_lines.append(
                        #     f"{i}❓" + truncate_string_with_ellipsis(md_quest, line_len)
                        # )
                        toc_table.add_row(
                            str(i),
                            "❓",
                            truncate_string_with_ellipsis(
                                md_quest.get("content", ""), line_len
                            ),
                            md_quest["created"],
                        )
                    console.print(toc_table, markup=True)
                    break
                else:
                    console.print_json(data=conv)
                    break
            else:
                continue

        if not found:
            console.print(f"[red]{title} not found[/red]")
    except FileNotFoundError as e:
        console.print(f"[red]File or directory {e.filename} is not found[/red]")
    # except Exception as e:
    #     console.print(f"[red]{e}[/red]")


def main():
    app()


if __name__ == "__main__":
    main()

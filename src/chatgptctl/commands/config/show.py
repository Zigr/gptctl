import json
from pathlib import Path
from typing import Annotated
import typer
from rich.console import Console

from chatgptctl.utils.utils import check_config_exists, default_config_path

app = typer.Typer()


@app.command(
    "show",
    help="Show configuration",
)
def show_config(
    ctx: typer.Context,
    config_path: Annotated[
        Path, typer.Argument(help="Path to config file to show")
    ] = default_config_path(),
):
    console: Console = ctx.obj["console"]
    exists = check_config_exists(config=config_path, console=console)
    if exists:
        with open(str(config_path), "r", encoding="utf-8") as f:
            cfg = json.load(f)
        console.print(f"Configuration file: [bold]{config_path}[/bold]")
        console.print_json(json.dumps(cfg, ensure_ascii=False, indent=2))
    else:
        dflt_cfg_path=default_config_path()
        console.print_json(json.dumps(ctx.obj["config"], ensure_ascii=False, indent=2))
        console.print(f"Configuration file does not exist.\n\nYou may create default configuration file in: [bold green]{dflt_cfg_path}[/bold green]")

def main():
    app()


if __name__ == "__main__":
    main()
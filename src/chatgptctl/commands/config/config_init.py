import json
from pathlib import Path
from typing import Annotated, Optional
import typer
from rich.console import Console
from rich.prompt import Prompt

from chatgptctl.utils.utils import default_config_path
from chatgptctl.config import AppConfig

app = typer.Typer()

cmd_help = """
**Initialize/create** configuration file with defaults in a default location.
But you can init as many config files as you want. 
Just pass the configuration file in ***config_file*** argument.
NOTE: config files do not support inherited configuration values overrides.You simply create a new configuration.
"""


@app.command(help=cmd_help)
def init(
    ctx: typer.Context,
    config_file: Annotated[
        Path, typer.Argument(help="Path to config file to init")
    ] = default_config_path(),
    force: bool = typer.Option(False, "--force", help="Overwrite existing config."),
) -> None:
    console: Console = ctx.obj["console"]
    command_name = "chatgptctl"
    config_path = config_file or default_config_path()

    if config_path.exists() and not force:
        console.print(f"[yellow]Configuration already exists at {config_path}[/yellow]")
        console.print("Use [bold]--force[/bold] to overwrite")
        console.print(
            f"Run [bold]{command_name} config show[/bold] to view current settings"
        )
        return

    try:
        config_name = Prompt.ask(
            prompt=f"Default {str(config_path)} [Enter] or provide your own config path",
            default=config_path,
            case_sensitive=False,
        )
        if config_name:
            # ensure dirs
            config_dir = Path(config_path.parent)
            config_dir.mkdir(parents=True, exist_ok=True)

            config_content = json.dumps(
                AppConfig().to_dict(), ensure_ascii=False, indent=4
            )
            config_path.write_text(config_content, encoding="utf-8", newline="\n")
            console.print(
                f"[green]✓[/green] Created configuration file [bold green]{config_path}[/bold green]"
            )
            console.print("\nNext steps:")
            console.print(
                f"  • Edit the config file [bold green]{config_path}[/bold green] to fit your needs"
            )
            console.print(
                f"  • Run [bold]{command_name} config show[/bold] to view your current settings"
            )
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to create config: {e}")
        raise typer.Exit(1) from e


def main():
    app()


if __name__ == "__main__":
    main()

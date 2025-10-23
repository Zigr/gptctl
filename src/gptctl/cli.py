from pathlib import Path
from typing import Annotated, Optional
import logging

from gptctl.config import check_config_exists, default_config_path

from gptctl import __version__

from rich.console import Console
from rich.logging import RichHandler

import typer
from .commands.view import app as view_app
from .commands.export import app as export_app
from .commands.config import app as config_app
from .config import AppConfig

APP_NAME = "gptctl"
DEFAULT_CONFIG = AppConfig().to_dict()
logger = logging.getLogger("rich")
console = Console()


def setup_logging(verbose: int = 0, debug: bool = False) -> None:
    """Set up logging configuration."""
    level = (
        logging.DEBUG
        if debug or verbose in [2, 3]
        else (logging.INFO if verbose > 0 and verbose < 2 else logging.WARNING)
    )

    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )


app_help = """

![Manage your ChatGPT exports](./docs/header.png 'Manage your ChatGPT exports')

CLI manager to organize(show,list,export,explore) ChatGPT user ***conversations.json***.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](#)
[![Build](https://img.shields.io/github/actions/workflow/status/Zigr/gptctl/ci.yml)](#)
[![Stars](https://img.shields.io/github/stars/Zigr/gptctl.svg?style=social&label=Star)](https://github.com/Zigr/gptctl/stargazers)

## [INTRODUCTION(more details)](./INTRODUCTION.md)

## [INSTALLATION(examples)](./INSTALL.md)
"""

app = typer.Typer(
    name=APP_NAME,
    no_args_is_help=True,
    rich_markup_mode="markdown",
    help=app_help,
)
app.add_typer(view_app)
app.add_typer(
    export_app,
    name="export",
    help="Export conversations from the ***input*** conversations.json file to JSON or MARKDOWN format. See gptctl **export command --help** for details.",
)
app.add_typer(
    config_app, name="config", help="Configuration file(s) operations: show, create"
)


def check_exclusive_options(
    ctx: typer.Context, value: Optional[str], other_option_value: Optional[str]
) -> Optional[str]:
    # """
    # Callback to check that only one of the mutually exclusive options is provided.

    # Parameters
    # ----------
    #     ctx (typer.Context): The Typer context.
    #     value (Optional[str]): The value of the current option.
    #     other_option_value (Optional[str]): The value of the other mutually exclusive option.
    # Returns
    # -------
    #     Optional[str]: The value of the current option if valid.
    # Raises
    # ------
    #     typer.BadParameter: If both options are provided.

    # Example usage
    # -------------
    #     @app.command()
    #     def my_command(
    #         ctx: typer.Context,
    #         by_name: Optional[str] = typer.Option(None, "--by-name", callback=lambda ctx, value: Optional[str]: check_exclusive_options(ctx, value, ctx.params.get("by_id"))),
    #         by_id: Optional[str] = typer.Option(None, "--by-id", callback=lambda ctx, value: Optional[str]: check_exclusive_options(ctx, value, ctx.params.get("by_name"))),
    #     ):
    #         ...
    # """

    # This check is important for features like autocompletion,
    # where the program may not have all parameters yet.
    if ctx.resilient_parsing:
        return value

    if value is not None and other_option_value is not None:
        if "by_name" in ctx.params and "by_id" in ctx.params:
            raise typer.BadParameter("Cannot use --by-name and --by-id together.")
    return value


def version_callback(value: bool):
    if value:
        console.print(f"{APP_NAME}, version v[bold]{__version__}[/bold]")
        raise typer.Exit()


# global options
@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    input: Annotated[
        str,
        typer.Option(
            "--input",
            "-i",
            help="Path to input conversations.json file",
            rich_help_panel="Path OPTIONS",
        ),
    ] = "",
    output_dir: Annotated[
        str,
        typer.Option(help="Path to output directory", rich_help_panel="Path OPTIONS"),
    ] = DEFAULT_CONFIG["output_dir"],
    output: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Path to output file. Depends on the command used.",
            rich_help_panel="Path OPTIONS",
        ),
    ] = DEFAULT_CONFIG["output_file"],
    config: Annotated[
        Path,
        typer.Option(
            "--config",
            "-c",
            help="Path to config.json file with overrides internal defaults",
            rich_help_panel="Path OPTIONS",
        ),
    ] = default_config_path(),
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Perform a trial run with no changes made. Output is printed to console.",
            rich_help_panel="Miscellaneous OPTIONS",
        ),
    ] = False,
    truncate_len: Annotated[
        int,
        typer.Option(
            "--truncate-len",
            "-tl",
            help="Shorten long strings (for ***dry-run*** preview)",
            rich_help_panel="Miscellaneous OPTIONS",
        ),
    ] = DEFAULT_CONFIG["truncate_len"],
    verbose: Annotated[
        int,
        typer.Option(
            "--verbose",
            "-v",
            count=True,
            help="Enable verbose output. Increase verbosity (-v, -vv(very verbose) -vvv(very very verbose, i.e. debug)) for more details.",
            rich_help_panel="Miscellaneous OPTIONS",
        ),
    ] = 0,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-V",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit.",
            rich_help_panel="Miscellaneous OPTIONS",
        ),
    ] = False,
):
    """
    Global  [OPTIONS] for ChatGpt Conversation Control. Use --help on subcommands for more details of another COMMAND [ARGS]..."""

    if verbose >= 1:
        console.print(f"Verbose level set to [bold green]{verbose}[/bold green]")
        console.print(f"Reading conversations from {input}...")

    if verbose == 2:
        console.print("Debug output enabled.")

    if verbose >= 3:
        # Set to the lowest level for maximum verbosity
        console.log("Maximum verbosity enabled.")
        console.print(f"Invoked command: {ctx.command.name}")
        console.print(f"Invoked subcommand: {ctx.invoked_subcommand}")
        console.print(f"Args: {ctx.args}")
        console.print(f"Params: {ctx.params}")
    if dry_run:
        console.print(
            "[bold yellow]Dry run enabled - no files will be written.[/bold yellow]"
        )
    ctx.obj = {"verbose": verbose, "dry_run": dry_run}

    # Adjust the logging level based on the number of `-v` flags
    setup_logging(verbose=verbose)

    # file_config = load_config(config, verbose)
    # cfg = resolve_config(ctx.params, file_config, verbose)
    config_path = default_config_path()
    g_config_exists = check_config_exists(config=config_path, console=console)
    if g_config_exists:
        cfg_result = AppConfig().get_config(
            config_path=str(config_path), args=ctx.params
        )
    else:
        cfg_result = AppConfig().get_config(args=ctx.params)
    if isinstance(cfg_result, dict):
        try:
            cfg = AppConfig(**cfg_result)
        except TypeError:
            # Fallback: populate a new AppConfig with known attributes if direct construction fails
            cfg = AppConfig()
            for k, v in cfg_result.items():
                if hasattr(cfg, k):
                    setattr(cfg, k, v)
    elif isinstance(cfg_result, AppConfig):
        # cfg_result is already the expected type
        cfg = cfg_result
    else:
        # Fallback to a default AppConfig when cfg_result is None or an unexpected type
        cfg = AppConfig()
    ctx.obj["config"] = cfg.to_dict()
    ctx.obj["console"] = console


def main():
    app()


if __name__ == "__main__":
    main()

import typer
from .list import app as list_app
from .show import app as show_app

app = typer.Typer(
    help="See individual command --help for details", no_args_is_help=True
)
app.add_typer(list_app)
app.add_typer(show_app)

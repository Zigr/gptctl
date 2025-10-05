import typer
from typer.core import TyperGroup
from click.core import Command
from .show import app as config_show_app
from .config_init import app as config_init_app


class CustomTyperGroup(TyperGroup):
    def get_command(self, ctx: typer.Context, name: str) -> Command | None:
        if name == "":
            return self.get_command(
                ctx, "show"
            )  # Replace with your default command's name
        return super().get_command(ctx, name)


app = typer.Typer(
    help="See individual command --help for details", no_args_is_help=True
)
app.add_typer(config_show_app)
app.add_typer(config_init_app)

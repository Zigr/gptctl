from typer.testing import CliRunner
from chatgptctl.cli import app

runner = CliRunner()


def test_cli_app():
    result = runner.invoke(app, [""])
    assert "Try 'chatgptctl --help' for help." in result.output


def test_root_help():
    """Test that the main app's help message shows all subcommands."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert (
        "List conversations from the input OPTION conversations.json file."
        in result.stdout
    )
    assert (
        "Show conversation details from the input OPTION conversations.json file."
        in result.stdout
    )
    assert (
        "Export conversations from the input conversations.json file to JSON or MARKDOWN format."
        in result.stdout
    )


def test_cli_app_list():
    result = runner.invoke(app, ["list"], input="")
    assert result.exit_code == 0
    assert "Message Count" in result.stdout


def test_cli_app_show():
    # Without parameters
    result = runner.invoke(app, ["show"])
    assert result.exit_code == 2
    assert "Missing argument 'TITLE'" in result.stderr


def test_app_export_json():
    # Without parameters
    result = runner.invoke(app, ["export", "json"])
    assert result.exit_code == 1, "The exit_code is not 1"
    assert "Aborted" in result.stderr
    # Not existing title(s)
    result = runner.invoke(app, ["export", "json", "-t 1", "-t 2"])
    assert result.exit_code == 1
    assert "Aborted" in result.stderr


def test_app_export_md():
    # Without parameters
    result = runner.invoke(app, ["export", "markdown"])
    assert result.exit_code == 1, "The exit_code is not 1"
    assert "Aborted" in result.stderr
    # Not existing title(s)
    result = runner.invoke(app, ["export", "markdown", "-t 1", "-t 2"])
    assert result.exit_code == 1
    assert "Aborted" in result.stderr

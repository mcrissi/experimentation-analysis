import typer

from xpa import __version__

app = typer.Typer(help="Hillstrom e-mail experiment analysis.", no_args_is_help=True)


def _version(value: bool) -> None:
    if value:
        typer.echo(f"xpa {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", callback=_version, is_eager=True, help="Show version and exit."
    ),
) -> None:
    """Hillstrom e-mail experiment analysis."""

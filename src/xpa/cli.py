import typer

from xpa import __version__
from xpa.config import Settings
from xpa.data.clean import build_silver
from xpa.data.download import download

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


@app.command("download")
def download_cmd() -> None:
    """Fetch the Hillstrom CSV into data/raw/ and write MANIFEST.json."""
    settings = Settings()
    manifest = download(settings.raw_dir)
    typer.echo(f"source:  {manifest['source_name']}")
    typer.echo(f"sha256:  {manifest['sha256']}")
    typer.echo(f"n_rows:  {manifest['n_rows']}")
    typer.echo(f"written: {settings.raw_dir}")


@app.command("clean")
def clean_cmd() -> None:
    """Build the typed silver Parquet in data/processed/ (prints arm sizes only)."""
    settings = Settings()
    counts = build_silver(settings.raw_dir, settings.processed_dir)
    for arm, n in counts.items():
        typer.echo(f"{arm:<8} {n:>6}")
    typer.echo(f"total    {sum(counts.values()):>6}")
    typer.echo(f"written: {settings.processed_dir}")

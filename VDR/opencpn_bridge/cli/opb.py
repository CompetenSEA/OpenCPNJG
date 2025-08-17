from __future__ import annotations

from pathlib import Path

import typer

from opencpn_bridge.tools import stage_s52_assets
from opencpn_bridge.py import ingest

app = typer.Typer(help="OpenCPN bridge utilities")


@app.command("stage-s52")
def stage_s52() -> None:
    """Stage S-52 assets."""
    try:
        stage_s52_assets.stage()
        typer.echo("S-52 assets staged")
    except Exception as exc:  # pragma: no cover - defensive
        typer.echo(f"stage-s52 failed: {exc}", err=True)
        raise typer.Exit(1)


@app.command()
def ingest(
    dataset_id: str,
    src_root: Path,
    dataset_type: str = typer.Option(..., "--type", "-t", help="Dataset type", metavar="enc|cm93"),
) -> None:
    """Ingest a dataset into the SENC cache and registry."""
    if dataset_type not in {"enc", "cm93"}:
        raise typer.BadParameter("type must be 'enc' or 'cm93'")
    try:
        ingest.ingest_dataset(dataset_id, str(src_root), dataset_type)
        typer.echo(f"Ingested dataset {dataset_id}")
    except Exception as exc:  # pragma: no cover - defensive
        typer.echo(f"ingest failed: {exc}", err=True)
        raise typer.Exit(1)


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="Bind address"),
    port: int = typer.Option(8000, help="Listen port"),
) -> None:
    """Run the FastAPI tile server."""
    try:
        import uvicorn
        uvicorn.run("opencpn_bridge.tileserver.app:app", host=host, port=port)
    except Exception as exc:  # pragma: no cover - defensive
        typer.echo(f"serve failed: {exc}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    app()

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import typer

app = typer.Typer(help="OpenCPN bridge utilities")

BASE_DIR = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = BASE_DIR / "scripts"
ASSETS_DIR = BASE_DIR / "chart-tiler" / "assets" / "senc"


@app.command("stage-s52")
def stage_s52() -> None:
    """Stage S-52 assets."""
    script = SCRIPTS_DIR / "stage_s52_assets.sh"
    try:
        subprocess.run([str(script)], check=True)
        typer.echo("S-52 assets staged")
    except subprocess.CalledProcessError as exc:
        typer.echo(f"stage-s52 failed: {exc}", err=True)
        raise typer.Exit(exc.returncode)


@app.command()
def ingest(
    dataset_id: str,
    src_root: Path,
    type: str = typer.Option(..., "--type", "-t", help="Dataset type", metavar="enc|cm93"),
) -> None:
    """Build a SENC cache and register it."""
    if type not in {"enc", "cm93"}:
        raise typer.BadParameter("type must be 'enc' or 'cm93'")
    chart_tiler = BASE_DIR / "chart-tiler"
    sys.path.insert(0, str(chart_tiler))
    from registry import get_registry  # type: ignore
    from opencpn_bridge import build_senc, query_features

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    senc_path = ASSETS_DIR / f"{dataset_id}.senc"
    try:
        build_senc(str(src_root), str(senc_path))
        info = query_features(str(senc_path))
        meta = {
            "id": dataset_id,
            "kind": type,
            "bbox": info.get("bbox", [0, 0, 0, 0]),
            "scale_min": int(info.get("scale_min", 0)),
            "scale_max": int(info.get("scale_max", 0)),
        }
        meta_path = senc_path.with_name(f"{senc_path.stem}.senc.json")
        meta_path.write_text(json.dumps(meta))
        registry = get_registry()
        registry.register_senc(meta_path, senc_path)
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
    chart_tiler = BASE_DIR / "chart-tiler"
    sys.path.insert(0, str(chart_tiler))
    try:
        import uvicorn
        uvicorn.run("tileserver:app", host=host, port=port)
    except Exception as exc:  # pragma: no cover - defensive
        typer.echo(f"serve failed: {exc}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    app()

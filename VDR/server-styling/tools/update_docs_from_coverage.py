import argparse
import json
from pathlib import Path

BEGIN = "<!-- BEGIN:S52_COVERAGE -->"
END = "<!-- END:S52_COVERAGE -->"


def render(coverage_path: Path, symbols_path: Path, limit: int = 25) -> str:
    coverage = json.loads(coverage_path.read_text())
    total = coverage.get("totalLookups", 0)
    covered = coverage.get("coveredByStyle", 0)
    missing = coverage.get("missingObjL", [])
    symbols = symbols_path.read_text().splitlines() if symbols_path.exists() else []
    missing_block = "\n".join(f"- {m}" for m in missing[:limit]) or "(none)"
    symbols_block = "\n".join(f"- {s}" for s in sorted(symbols)[:limit]) or "(none)"
    lines = [
        "| metric | value |",
        "| --- | ---: |",
        f"| total lookups | {total} |",
        f"| covered by style | {covered} |",
        f"| missing | {len(missing)} |",
    ]
    prev_path = coverage_path.with_name("style_coverage.prev.json")
    if prev_path.exists():
        prev = json.loads(prev_path.read_text())
        prev_missing = set(prev.get("missingObjL", []))
        newly = sorted(prev_missing - set(missing))
        delta = covered - prev.get("coveredByStyle", 0)
        lines.extend(
            [
                "",
                "### Delta",
                f"covered change: {delta:+d}",
                *(f"- {n}" for n in newly[:limit]),
            ]
        )
    lines.extend(
        [
            "",
            "### Missing OBJL",
            missing_block,
            "",
            "### Symbols seen",
            symbols_block,
        ]
    )
    return "\n".join(lines)


def update_docs(doc_path: Path, block: str) -> bool:
    text = doc_path.read_text()
    start = text.find(BEGIN)
    end = text.find(END)
    if start == -1 or end == -1 or end < start:
        raise RuntimeError("Coverage markers not found in docs")
    before = text[: start + len(BEGIN)]
    after = text[end:]
    new_text = before + "\n" + block + "\n" + after
    if new_text == text:
        return False
    doc_path.write_text(new_text)
    return True


def main() -> None:
    p = argparse.ArgumentParser(description="Update docs with coverage data")
    p.add_argument("--docs", type=Path, required=True)
    p.add_argument("--coverage", type=Path, required=True)
    p.add_argument("--symbols", type=Path, required=True)
    args = p.parse_args()
    block = render(args.coverage, args.symbols)
    updated = update_docs(args.docs, block)
    if updated:
        print("Documentation updated")
    else:
        print("Documentation already up to date")


if __name__ == "__main__":
    main()

import argparse
import json
from pathlib import Path

BEGIN = "<!-- BEGIN:S52_COVERAGE -->"
END = "<!-- END:S52_COVERAGE -->"


def render(
    coverage_path: Path,
    portrayal_path: Path,
    symbols_path: Path,
    s57_path: Path | None = None,
    limit: int = 25,
) -> str:
    coverage = json.loads(coverage_path.read_text())
    portrayal = json.loads(portrayal_path.read_text()) if portrayal_path.exists() else {}
    total = coverage.get("totalLookups", 0)
    covered = coverage.get("coveredByStyle", 0)
    missing = coverage.get("missingObjL", [])
    symbols = symbols_path.read_text().splitlines() if symbols_path.exists() else []
    presence_pct = coverage.get("presence", 0.0) * 100
    portrayal_pct = portrayal.get("coverage", 0.0) * 100
    portrayal_missing = portrayal.get("portrayalMissing", [])
    _sample = portrayal.get("sample", [])  # unused but reserved for future use
    by_type = portrayal.get("byType", {})
    by_bucket = portrayal.get("byBucket", {})
    missing_block = "\n".join(f"- {m}" for m in missing[:limit]) or "(none)"
    symbols_block = "\n".join(f"- {s}" for s in sorted(symbols)[:limit]) or "(none)"
    lines = [
        "| metric | value |",
        "| --- | ---: |",
        f"| total lookups | {total} |",
        f"| presence coverage | {presence_pct:.1f}% |",
        f"| portrayal coverage | {portrayal_pct:.1f}% |",
    ]
    for key, val in by_type.items():
        lines.append(f"| {key.lower()} portrayal | {val*100:.1f}% |")
    for key, val in by_bucket.items():
        lines.append(f"| {key.lower()} portrayal | {val*100:.1f}% |")
    lines.append(
        f"| missing | {len(missing)} |",
    )
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
            "### Portrayal gaps",
            ("\n".join(f"- {m}" for m in portrayal_missing[:limit]) or "(none)"),
            "",
            "### Symbols seen",
            symbols_block,
        ]
    )

    if s57_path and s57_path.exists():
        s57 = json.loads(s57_path.read_text())
        missing_s57 = s57.get("missingClasses", [])
        lines.extend(
            [
                "",
                "### S-57 catalogue",
                "| metric | value |",
                "| --- | ---: |",
                f"| total classes | {s57.get('totalClasses', 0)} |",
                f"| have S-52 lookup | {s57.get('s52Lookups', 0)} |",
                f"| handled by styles | {s57.get('handledByStyles', 0)} |",
                f"| ignored | {len(s57.get('ignoredClasses', []))} |",
                f"| missing | {len(missing_s57)} |",
                "",
                "#### Missing S-57 classes",
                "\n".join(f"- {m}" for m in missing_s57[:limit]) or "(none)",
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
    p.add_argument("--portrayal", type=Path, required=True)
    p.add_argument("--symbols", type=Path, required=True)
    p.add_argument("--s57", type=Path)
    args = p.parse_args()
    block = render(args.coverage, args.portrayal, args.symbols, args.s57)
    updated = update_docs(args.docs, block)
    if updated:
        print("Documentation updated")
    else:
        print("Documentation already up to date")


if __name__ == "__main__":
    main()

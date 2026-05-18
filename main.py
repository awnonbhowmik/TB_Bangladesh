#!/usr/bin/env python3.13
"""Entry point: build the TB Bangladesh review Excel workbook."""

import sys
import time
from pathlib import Path

# Allow running from the TB_BD directory without installing the package
sys.path.insert(0, str(Path(__file__).parent))

from src.workbook import run


def main() -> None:
    start = time.perf_counter()
    output = run()
    elapsed = time.perf_counter() - start
    figs  = output.parent / "figures"
    mps   = output.parent / "maps"
    latex = output.parent / "latex"
    print(f"\nDone in {elapsed:.1f}s")
    print(f"  Excel   → {output}")
    print(f"  Figures → {figs}/ ({len(list(figs.glob('*.pdf')))} PDFs + PNGs)")
    print(f"  Maps    → {mps}/ ({len(list(mps.glob('*.pdf')))} PDFs + PNGs)")
    print(f"  LaTeX   → {latex}/ ({len(list(latex.glob('*.tex')))} .tex files)")


if __name__ == "__main__":
    main()

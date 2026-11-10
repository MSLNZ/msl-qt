"""Constants used by the `msl-qt` package."""

# cSpell: ignore qryzafpnum kMGTPEZYRQ
from __future__ import annotations

from pathlib import Path

HOME_DIR: Path = Path("~/.msl").expanduser()
"""The default `HOME` directory where all files used by the package are located."""

SI_PREFIX_MAP: dict[int, str] = dict(enumerate("qryzafpnum kMGTPEZYRQ", start=-10))
"""The SI prefixes used to form multiples of $10^{3n}$ (n=-10..10)."""

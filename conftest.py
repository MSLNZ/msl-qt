"""pytest configuration file."""

# cSpell: ignore addoption
from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register custom command-line options."""
    parser.addoption(
        "--binding",
        action="store",
        default="PySide6",
        choices=["PySide6", "PyQt6"],
        help="The Qt API binding to use.",
    )


def pytest_report_header(*_: object) -> str:
    """Displayed as header info for terminal reporting."""
    return f"QT_API: {binding.name}, version={binding.version}, qt_version={binding.qt_version}"


for i, arg in enumerate(sys.argv, start=1):
    if (arg == "--binding") and (i < len(sys.argv)):
        os.environ["QT_API"] = sys.argv[i]


from msl.qt import application, binding  # noqa: E402

# must be created before running the tests when using PyQt6 as the binding
app = application()

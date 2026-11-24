"""Example to show the `Logger` widget."""

from __future__ import annotations

import logging
import random

from msl.qt import Logger, application


def show() -> None:
    """Create the QApplication and show the `Logger`."""
    app = application()
    logger = Logger()  # fmt="%(message)s")
    logger.setWindowTitle("Logger Widget")

    # Configure the root logger
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # Create 100 log messages
    for i in range(1, 101):
        level = random.randint(10, 60)
        if level < logging.INFO:
            root.debug("DEBUG %d", i)
        elif level < logging.WARNING:
            root.info("INFO %d", i)
        elif level < logging.ERROR:
            root.warning("WARN %d", i)
        elif level < logging.CRITICAL:
            root.error("ERROR %d", i)
        else:
            root.critical("CRITICAL %d", i)

    logger.show()
    _ = app.exec()


if __name__ == "__main__":
    show()

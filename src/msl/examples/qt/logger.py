"""Example to show the [Logger][msl.qt.widgets.logger.Logger] widget."""

from __future__ import annotations

import logging
import random

from msl.qt import Logger, application


def show() -> None:
    """Uses the root logger."""
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    app = application()

    logger = Logger(fmt="%(message)s")
    logger.setWindowTitle("Logger Widget")

    for i in range(1, 101):
        level = random.randint(10, 60)
        if level < logging.INFO:
            log.debug("DEBUG %d", i)
        elif level < logging.WARNING:
            log.info("INFO %d", i)
        elif level < logging.ERROR:
            log.warning("WARN %d", i)
        elif level < logging.CRITICAL:
            log.error("ERROR %d", i)
        else:
            log.critical("CRITICAL %d", i)

    logger.resize(800, 400)
    logger.show()
    _ = app.exec()


if __name__ == "__main__":
    show()

"""
Example to show the :class:`~msl.qt.widgets.logger.Logger`.
"""
import random
import logging

from msl.qt import (
    application,
    Logger
)


def show():
    log = logging.getLogger()

    app = application()

    logger = Logger()
    logger.setWindowTitle('Logger Widget')

    for i in range(100):
        level = random.randint(10, 60)
        if level < logging.INFO:
            log.debug('debug message {}'.format(i+1))
        elif level < logging.WARNING:
            log.info('info message {}'.format(i+1))
        elif level < logging.ERROR:
            log.warning('warning message {}'.format(i+1))
        elif level < logging.CRITICAL:
            log.error('error message {}'.format(i+1))
        else:
            log.critical('critical message {}'.format(i+1))

    logger.resize(800, 400)
    logger.show()
    app.exec_()


if __name__ == '__main__':
    show()

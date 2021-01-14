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
    log.setLevel(logging.DEBUG)

    app = application()

    logger = Logger(fmt='%(message)s')
    logger.setWindowTitle('Logger Widget')

    for i in range(1, 101):
        level = random.randint(10, 60)
        if level < logging.INFO:
            log.debug('DEBUG {}'.format(i))
        elif level < logging.WARNING:
            log.info('INFO {}'.format(i))
        elif level < logging.ERROR:
            log.warning('WARN {}'.format(i))
        elif level < logging.CRITICAL:
            log.error('ERROR {}'.format(i))
        else:
            log.critical('CRITICAL {}'.format(i))

    logger.resize(800, 400)
    logger.show()
    app.exec()


if __name__ == '__main__':
    show()

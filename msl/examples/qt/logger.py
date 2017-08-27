"""
Example to show how to use the Logger QWidget.
"""
import sys
import random
import logging

from msl.qt import application, Logger


def main():
    logger = logging.getLogger()

    app = application()
    log = Logger()
    log.setWindowTitle('Logger Widget')

    for i in range(1000):
        level = random.randint(10, 60)
        if level < logging.INFO:
            logger.debug('debug message {}'.format(i+1))
        elif level < logging.WARNING:
            logger.info('info message {}'.format(i+1))
        elif level < logging.ERROR:
            logger.warning('warning message {}'.format(i+1))
        elif level < logging.CRITICAL:
            logger.error('error message {}'.format(i+1))
        else:
            logger.critical('critical message {}'.format(i+1))

    log.resize(800, 400)
    log.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

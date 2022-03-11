import os
import sys

if 'QT_API' not in os.environ and not os.getenv('GITHUB_ACTIONS'):
    os.environ['QT_API'] = 'PySide6' if sys.version_info.minor > 5 else 'PySide2'

sys.excepthook = print

from msl.qt import application
app = application()

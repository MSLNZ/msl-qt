import os
import sys

if 'QT_API' not in os.environ:
    os.environ['QT_API'] = 'PySide6' if sys.version_info.minor > 5 else 'PySide2'

sys.excepthook = print

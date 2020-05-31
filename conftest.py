import os
import sys

# the backend to use, either pyside or pyqt
os.environ['QT_API'] = 'pyside'

sys.excepthook = print

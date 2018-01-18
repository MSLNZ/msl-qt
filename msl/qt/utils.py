"""
General classes and functions.
"""
from . import QtCore


class Sleep(QtCore.QObject):

    _finished = QtCore.pyqtSignal()

    def __init__(self):
        """
        Suspends execution for a certain number of milliseconds without
        freezing the user interface.
        """
        QtCore.QObject.__init__(self)

        self._milliseconds = 0

        self._thread = QtCore.QThread()
        self.moveToThread(self._thread)
        self._thread.started.connect(self._start)
        self._finished.connect(self._thread.quit)

    def register_callback(self, callback):
        """Register a function or method to be called when sleeping is done.

        Parameters
        ----------
        callback : :obj:`callable`
            The function or method to be called when sleeping is done.
        """
        self._finished.connect(callback)

    def start(self, milliseconds):
        """Start sleeping.

        Parameters
        ----------
        milliseconds : :obj:`int`
            The number of milliseconds to sleep for.
        """
        self._milliseconds = int(milliseconds)
        self._thread.start()

    def _start(self):
        self._thread.msleep(self._milliseconds)
        self._finished.emit()

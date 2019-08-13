"""
Base classes for starting a process in a new :class:`QThread`.
"""
import logging
import traceback

from . import QtCore, prompt

logger = logging.getLogger(__name__)


class Worker(QtCore.QObject):
    """
    Processes an expensive or blocking operation in a thread that is separate from the main thread.

    Example
    -------
    See :class:`~msl.qt.sleep.SleepWorker` for an example subclass of a :class:`Worker`.
    """

    _finished = QtCore.pyqtSignal()
    _error = QtCore.pyqtSignal(str)

    def process(self):
        """The expensive or blocking operation to process.

        .. attention::
           You **MUST** override this method.
        """
        raise NotImplementedError("You must override the 'process' method.")

    def _process(self):
        try:
            self.process()
        except:
            self._error.emit(traceback.format_exc())
        else:
            self._finished.emit()


class Thread(QtCore.QObject):

    def __init__(self, worker):
        """Moves the `worker` to a new :class:`QtCore.QThread`.

        Parameters
        ----------
        worker : :class:`Worker`
            A :class:`Worker` subclass that has **NOT** been instantiated.

        Example
        -------
        See :class:`~msl.qt.sleep.Sleep` for an example subclass of a :class:`Thread`.
        """
        super(Thread, self).__init__()
        self._thread = None
        self._worker = None
        self._callbacks = []

        if not callable(worker):
            raise TypeError('The Worker for the QThread must not be instantiated')
        elif not issubclass(worker, Worker):
            raise TypeError('The Worker for the QThread is not a Worker subclass')
        else:
            self._worker_class = worker

    def __getattr__(self, item):
        return getattr(self._worker, item)

    def add_callback(self, callback):
        """Add a callable object as a callback.

        The `callback` is called when the :meth:`Worker.process` method is finished.
        The `callback` cannot have arguments nor keyword arguments.

        Parameters
        ----------
        callback : :obj:`callable`
            A function or method that will be called when the :class:`Worker`
            is finished processing the task.
        """
        self._callbacks.append(callback)

    def is_running(self):
        """:class:`bool`: Whether the thread is running."""
        return self._thread.isRunning()

    def quit(self):
        """Tells the thread's event loop to exit."""
        self._thread.quit()

    def remove_callback(self, callback):
        """Remove the callable object as a callback.

        Rather than raising a :exc:`ValueError` if the `callback` is not
        registered as a callback this method logs a warning that the
        `callback` could not be removed.

        Parameters
        ----------
        callback : :obj:`callable`
            The function or method that will no longer be called when the
            :class:`Worker` is finished processing the task.
        """
        try:
            self._callbacks.remove(callback)
        except ValueError:
            logger.warning('callback "{}" was not removed from "{}"'.format(
                callback.__name__, self.__class__.__name__))

    def start(self, *args, **kwargs):
        """Start processing the :class:`Worker` in the :class:`QtCore.QThread`.

        The ``*args`` and ``**kwargs`` values are passed to the constructor
        of the :class:`Worker` class.
        """
        self._thread = QtCore.QThread()
        self._worker = self._worker_class(*args, **kwargs)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker._process)
        self._worker._error.connect(lambda message: prompt.critical(message))
        self._worker._finished.connect(self._thread.quit)
        self._worker._finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)

        # connecting the callbacks last seems to have the best
        # performance and stability for the GUI
        for callback in self._callbacks:
            self._thread.finished.connect(callback)

        self._thread.start()

    def wait(self, milliseconds=None):
        """Wait for the thread to either finish or timeout.

        Parameters
        ----------
        milliseconds : :class:`int`, optional
            The number of milliseconds to wait before a timeout occurs.
            If :obj:`None` then :meth:`wait` will never timeout and the
            thread must return from its ``run`` method.

        Returns
        -------
        :class:`bool`
            :data:`True` if the thread finished otherwise :data:`False`
            if the thread timed out.
        """
        if milliseconds is None:
            return self._thread.wait()
        else:
            return self._thread.wait(int(milliseconds))

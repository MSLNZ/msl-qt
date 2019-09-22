"""
Base classes for starting a process in a new :class:`QThread`.
"""
import sys
import logging
import traceback as tb

from . import QtCore, Signal, prompt

logger = logging.getLogger(__name__)


class Worker(QtCore.QObject):
    """Process an expensive or blocking operation in a thread that is separate from the main thread.

    You can access to the attributes of the :class:`Worker` as though they are attributes of the
    :class:`Thread`.

    Example
    -------
    See :class:`~msl.qt.sleep.SleepWorker` for an example of a :class:`Worker`.
    """

    finished = Signal()
    error = Signal(object, object)  # (exception, traceback)

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
            self.error.emit(*sys.exc_info()[1:])
        else:
            self.finished.emit()


class Thread(QtCore.QObject):

    finished = Signal()
    """:class:`~msl.qt._qt.Signal`: This signal is emitted from the thread when it finishes executing."""

    def __init__(self, worker):
        """Moves the `worker` to a new :class:`QtCore.QThread`.

        Parameters
        ----------
        worker
            A :class:`Worker` subclass that has **NOT** been instantiated.

        Example
        -------
        See :class:`~msl.qt.sleep.Sleep` for an example of a :class:`Thread`.
        """
        super(Thread, self).__init__()
        self._thread = None
        self._worker = None
        self._callbacks = []
        self._finished = False

        if not callable(worker):
            raise TypeError('The Worker for the Thread must not be instantiated')
        elif not issubclass(worker, Worker):
            raise TypeError('The Worker for the Thread is not a Worker subclass')
        else:
            self._worker_class = worker

    def __getattr__(self, item):
        """All other attributes are assumed to be those of the :class:`Worker`."""
        if self._worker is not None:
            return getattr(self._worker, item)
        raise AttributeError('You must start the Thread before accessing an attribute of the Worker')

    def error_handler(self, exception, traceback):
        """If an exception is raised by the :class:`Worker` then the default behaviour is to
        show the error message in a :func:`~msl.qt.prompt.critical` dialog window.

        You can override this method to implement your own error handler.

        Parameters
        ----------
        exception
            The exception.
        traceback
            The traceback.
        """
        prompt.critical(''.join(tb.format_exception(type(exception), exception, traceback)))

    def is_finished(self):
        """Whether the thread successfully finished.

        Returns
        -------
        :class:`bool`
            :data:`True` if the thread finished otherwise :data:`False`.
        """
        if self._thread is None:
            return self._finished
        return bool(self._check(self._thread.isFinished))

    def is_running(self):
        """Whether the thread is running.

        Returns
        -------
        :class:`bool`
            :data:`True` if the thread is running otherwise :data:`False`.
        """
        if self._thread is None:
            return False
        return bool(self._check(self._thread.isRunning))

    def quit(self):
        """Tells the thread's event loop to exit."""
        if self._thread is not None:
            self._check(self._thread.quit)

    def start(self, *args, **kwargs):
        """Start processing the :class:`Worker` in a :class:`QtCore.QThread`.

        The ``*args`` and ``**kwargs`` are passed to the constructor of the
        :class:`Worker` class.
        """
        self._thread = QtCore.QThread()
        self._worker = self._worker_class(*args, **kwargs)
        self._worker.moveToThread(self._thread)
        self._worker.error.connect(lambda *ignore: self._thread.exit(-1))
        self._worker.error.connect(self.error_handler)
        self._worker.finished.connect(self._worker_finished)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.started.connect(self._worker._process)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.finished.connect(self.finished)
        self._thread.start()

    def stop(self, milliseconds=None):
        """Calls :meth:`.quit` then :meth:`.wait`."""
        self.quit()
        return self.wait(milliseconds=milliseconds)

    def wait(self, milliseconds=None):
        """Wait for the thread to either finish or timeout.

        Parameters
        ----------
        milliseconds : :class:`int`, optional
            The number of milliseconds to wait before a timeout occurs.
            If :data:`None` then this method will never timeout and the
            thread must return from its `run` method.

        Returns
        -------
        :class:`bool` or :data:`None`
            :data:`True` if the thread finished, :data:`False` if the
            thread timed out or :data:`None` if the thread is not running.
        """
        if self._thread is None:
            return None
        if milliseconds is None:
            return self._check(self._thread.wait)
        return self._check(self._thread.wait, int(milliseconds))

    def _check(self, method, *args):
        """Wrap all calls to the QThread in a try..except block to silently
        ignore the following error:

        RuntimeError: Internal C++ object (*.QtCore.QThread) already deleted.
        """
        try:
            return method(*args)
        except RuntimeError:
            self._thread = None

    def _worker_finished(self):
        """Slot -> Called when the :class:`Worker` finished successfully."""
        self._thread.quit()
        self._finished = True

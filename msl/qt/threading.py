"""
Base classes for starting a process in a new :class:`~QtCore.QThread`.
"""
import sys
import traceback as tb

from . import QtCore
from . import Signal
from . import prompt


class Worker(QtCore.QObject):

    finished = Signal()
    error = Signal(BaseException, object)  # (exception, traceback)

    def __init__(self, *args, **kwargs):
        """Process an expensive or blocking operation in a thread that is
        separate from the main thread.

        You can access to the attributes of the :class:`~msl.qt.threading.Worker`
        as though they are attributes of the :class:`~msl.qt.threading.Thread`.

        The ``*args`` and ``**kwargs`` parameters are passed to the constructor
        of the :class:`~msl.qt.threading.Worker` when the
        :meth:`~msl.qt.threading.Thread.start` method is called.

        Example
        -------
        See :class:`~msl.qt.sleep.SleepWorker` for an example of a
        :class:`~msl.qt.threading.Worker`.
        """
        super(Worker, self).__init__()

    def process(self):
        """The expensive or blocking operation to process.

        .. attention::
           You must override this method.
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
    """A :class:`~QtCore.Signal` that is emitted when the thread is finished 
    (i.e., when :meth:`~msl.qt.threading.Worker.process` finishes)."""

    def __init__(self, worker):
        """Moves a :class:`~msl.qt.threading.Worker` to a new :class:`~QtCore.QThread`.

        Parameters
        ----------
        worker
            A :class:`~msl.qt.threading.Worker` subclass that has *not* been instantiated.

        Example
        -------
        See :class:`~msl.qt.sleep.Sleep` for an example of a :class:`~msl.qt.threading.Thread`.
        """
        super(Thread, self).__init__()
        self._thread = None
        self._worker = None
        self._finished = False
        self._signals_slots = []

        if not callable(worker):
            raise TypeError('The Worker for the Thread must not be instantiated')
        elif not issubclass(worker, Worker):
            raise TypeError('The Worker for the Thread is not a Worker subclass')
        else:
            self._worker_class = worker

    def __getattr__(self, item):
        """All other attributes are assumed to be those of the :class:`~msl.qt.threading.Worker`."""
        if self._worker is not None:
            return getattr(self._worker, item)
        raise AttributeError('You must start the Thread before accessing an attribute of the Worker')

    def error_handler(self, exception, traceback):
        """If an exception is raised by the :class:`~msl.qt.threading.Worker` then the default
        behaviour is to show the error message in a :func:`~msl.qt.prompt.critical` dialog window.

        You can override this method to implement your own error handler.

        Parameters
        ----------
        exception : :exc:`BaseException`
            The exception instance
        traceback : :mod:`traceback`
            A traceback object.
        """
        prompt.critical(''.join(tb.format_exception(type(exception), exception, traceback)))

    def is_finished(self):
        """Whether the thread is finished.

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
        """Start processing the :class:`~msl.qt.threading.Worker` in a :class:`~QtCore.QThread`.

        The ``*args`` and ``**kwargs`` are passed to the constructor of the
        :class:`~msl.qt.threading.Worker` class.
        """
        self._thread = QtCore.QThread()
        self._worker = self._worker_class(*args, **kwargs)
        self._worker.moveToThread(self._thread)
        for signal, slot in self._signals_slots:
            getattr(self._worker, signal).connect(slot)
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
            If :data:`None` then this method will never time out and the
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

    def worker_connect(self, signal, slot):
        """Connect a :class:`~QtCore.Signal` from the :class:`~msl.qt.threading.Worker`
        to a :class:`~QtCore.Slot`.

        This method is intended to be called *before* a worker thread starts.
        Although, you can still call this method when a worker thread is running,
        it is easier (fewer characters to type) to access the attributes of a
        :class:`~msl.qt.threading.Worker` as though they are attributes of the
        :class:`~msl.qt.threading.Thread`.

        Parameters
        ----------
        signal : :class:`str`, :class:`~QtCore.Signal` or :class:`~PySide6.QtCore.SignalInstance`
            The `signal` to connect the `slot` to. If a :class:`str`, then either
            the name of a class attribute of the :class:`~msl.qt.threading.Worker` or the `name`
            parameter that was used in the :class:`~QtCore.Signal` constructor.
        slot
            A callable function to use as the :class:`~QtCore.Slot`.
        """
        signal, slot = Thread._check_signal_slot(signal, slot)
        if self.is_running():
            getattr(self._worker, signal).connect(slot)
        else:
            self._signals_slots.append((signal, slot))

    def worker_disconnect(self, signal, slot):
        """Disconnect a :class:`~QtCore.Slot` from a :class:`~QtCore.Signal` of the
        :class:`~msl.qt.threading.Worker`.

        This method is intended to be called *before* a worker thread is restarted.
        Although, you can still call this method when a worker thread is running,
        it is easier (fewer characters to type) to access the attributes of a
        :class:`~msl.qt.threading.Worker` as though they are attributes of the
        :class:`~msl.qt.threading.Thread`.

        Parameters
        ----------
        signal : :class:`str`, :class:`~QtCore.Signal` or :class:`~PySide6.QtCore.SignalInstance`
            The `signal` to disconnect the `slot` from. Must be the same
            value that was used in :meth:`worker_connect`.
        slot
            Must be the same callable that was used in :meth:`worker_connect`.
        """
        signal, slot = Thread._check_signal_slot(signal, slot)
        if self.is_running():
            getattr(self._worker, signal).disconnect(slot)
        else:
            try:
                self._signals_slots.remove((signal, slot))
            except ValueError:
                options = '\n'.join(f'  {a!r} {b}' for a, b in self._signals_slots)
                if not options:
                    raise ValueError(
                        'No Worker signals were connected to slots') from None
                raise ValueError(
                    f'The slot {slot} is not connected to the signal '
                    f'{signal!r}.\nOptions\n{options}') from None

    @staticmethod
    def _check_signal_slot(signal, slot):
        """Check the input types and returns the appropriate types."""
        if not callable(slot):
            raise TypeError('slot must be callable')

        if isinstance(signal, str):
            return signal, slot

        if isinstance(signal, Signal):
            if hasattr(signal, 'signatures'):  # PyQt
                signal = signal.signatures[0]
                if '(' not in signal:
                    raise TypeError(
                        'Cannot determine the Signal name. Either pass in '
                        'the Signal name as a string or define a name '
                        'parameter in the Signal constructor.')
            return str(signal).split('(')[0], slot

        raise TypeError('signal must be a QtCore.Signal or string')

    def _check(self, method, *args):
        """Wrap all calls to the QThread in a try-except block to silently
        ignore the following error:

        RuntimeError: Internal C++ object (*.QtCore.QThread) already deleted.
        """
        try:
            return method(*args)
        except RuntimeError:
            self._thread = None

    def _worker_finished(self):
        """Slot -> Called when the :class:`~msl.qt.threading.Worker` finished successfully."""
        self._thread.quit()
        self._finished = True

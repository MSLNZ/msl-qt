"""
Sleep without freezing the graphical user interface.
"""
import time

from .threading import Thread, Worker


class SleepWorker(Worker):

    def __init__(self, seconds):
        """The :class:`~msl.qt.threading.Worker` class for :class:`Sleep`.

        Delays execution for a certain number of seconds without
        freezing the graphical user interface.

        Parameters
        ----------
        seconds : :class:`float`
            The number of seconds to sleep for. This argument is passed in from
            the :obj:`start(*args, **kwargs) <msl.qt.threading.Thread.start>`
            method of the :class:`Sleep` class.
        """
        Worker.__init__(self)
        self.seconds = seconds

    def process(self):
        """Calls :func:`time.sleep`."""
        time.sleep(self.seconds)


class Sleep(Thread):

    def __init__(self):
        """Sleep without freezing the graphical user interface.

        The following example illustrates how one can use :class:`Sleep`
        and keep the GUI active:

        .. literalinclude:: ../../msl/examples/qt/loop_until_abort_sleep.py

        Example
        -------
        To run this example enter the following:

        >>> from msl.examples.qt import LoopExampleSleep
        >>> loop = LoopExampleSleep() # doctest: +SKIP
        >>> loop.start() # doctest: +SKIP
        """
        Thread.__init__(self, SleepWorker)

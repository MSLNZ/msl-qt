"""
Repeatedly perform a task until aborted by the user.
"""
import datetime
import traceback

from . import QtWidgets, QtCore, QtGui, application, prompt


class LoopUntilAbort(object):

    def __init__(self, loop_delay=0, max_iterations=None, single_shot=False,
                 title=None, bg_color='#DFDFDF', text_color='#20548B',
                 font_family='Helvetica', font_size=14, **kwargs):
        """Repeatedly perform a task until aborted by the user.

        This class provides an interface to show the status of a task (e.g., read
        a sensor value and write the value to a file) that you want to perform for
        an unknown period of time (e.g., during lunch or overnight) and you want to
        stop the task whenever you return. It can be regarded as a way to tell
        your program to *"get as much data as possible until I get back"*.

        The following example illustrates how to repeatedly write data to a
        file in a loop:

        .. literalinclude:: ../../msl/examples/qt/loop_until_abort.py

        Example
        -------
        To view this example run:

        >>> from msl.examples.qt import LoopExample
        >>> LoopExample() # doctest: +SKIP

        Parameters
        ----------
        loop_delay : :obj:`int`, optional
            The delay time, in milliseconds, to wait between successive calls
            to the :meth:`loop` method. For example, if `loop_delay` = ``0``
            then there is no time delay between successive calls to the
            :meth:`loop` method; if `loop_delay` = ``1000`` then wait 1 second
            between successive calls to the :meth:`loop` method. The time delay
            occurs *before* the :meth:`loop` method is executed.
        max_iterations : :obj:`int`, optional
            The maximum number of times to call the :meth:`loop` method. The
            default value is :obj:`None`, which means to loop until the user
            aborts the program.
        single_shot : :obj:`bool`, optional
            Whether to call the :meth:`loop` method once (and only once). If
            you specify the value to be :obj:`True` then you must call the
            :meth:`loop_once` method in the subclass whenever you want to
            run the :meth:`loop` one more time. This is useful if the
            :meth:`loop` depends on external factors (e.g., waiting for an
            oscilloscope to download a trace after a trigger event) and the
            amount of time that the :meth:`loop` requires to complete is not
            known.
        title : :obj:`str`, optional
            The text to display in the title bar of the dialog window.
            If :obj:`None` then uses the name of the subclass as the title.
        bg_color : :obj:`str` or :obj:`QColor`, optional
            The background color of the dialog window.
        text_color : :obj:`str` or :obj:`QColor`, optional
            The color of the **Elapsed time** and **Iterations** text.
        font_family : :obj:`str`, optional
            The font family to use for the text.
        font_size : :obj:`int`, optional
            The font size of the text.
        **kwargs : :obj:`dict`
            All additional keyword arguments will be passed to the
            :meth:`setup` method.
        """
        self._iteration = 0
        self._loop_error = False
        self._max_iterations = int(max_iterations) if max_iterations else None

        self._app = application()

        self._central_widget = QtWidgets.QWidget()
        bg_hex_color = QtGui.QColor(bg_color).name()
        self._central_widget.setStyleSheet('background:{};'.format(bg_hex_color))

        self._main_window = QtWidgets.QMainWindow()
        self._main_window.setCentralWidget(self._central_widget)
        self._main_window.closeEvent = self._shutdown
        if title is None:
            title = self.__class__.__name__
        self._main_window.setWindowTitle(title)
        self._main_window.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)

        font = QtGui.QFont(font_family, pointSize=font_size)
        text_hex_color = QtGui.QColor(text_color).name()

        self._runtime_label = QtWidgets.QLabel()
        self._runtime_label.setFont(font)
        self._runtime_label.setStyleSheet('color:{};'.format(text_hex_color))

        self._iteration_label = QtWidgets.QLabel()
        self._iteration_label.setFont(font)
        self._iteration_label.setStyleSheet('color:{};'.format(text_hex_color))

        self._user_label = QtWidgets.QLabel()
        self._user_label.setFont(font)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self._runtime_label)
        vbox.addWidget(self._iteration_label)
        vbox.addWidget(self._user_label)
        vbox.setStretchFactor(self._user_label, 1)
        self._central_widget.setLayout(vbox)

        self._runtime_timer = QtCore.QTimer()
        self._runtime_timer.timeout.connect(self._update_runtime_label)

        self._loop_timer = QtCore.QTimer()
        self._loop_timer.timeout.connect(self._call_loop)

        self._start_time = self.current_time
        s = self._start_time.strftime('%d %B %Y at %H:%M:%S')
        self._main_window.statusBar().showMessage('Started ' + s)
        self._update_runtime_label()
        self._update_iteration_label()

        try:
            self.setup(**kwargs)
        except:
            msg = 'The following exception occurred in the setup() method:\n\n'
            prompt.critical(msg + traceback.format_exc())
            self._stop_timers()

        if self._loop_timer:
            self._loop_delay = max(0, int(loop_delay)) if not single_shot else 0
            if self._loop_delay > 0:
                self._call_loop()
            self._loop_timer.setSingleShot(single_shot)
            self._loop_timer.start(self._loop_delay)
            self._runtime_timer.start(1000)
            self._main_window.show()
            self._app.exec_()

    @property
    def iteration(self):
        """:obj:`int`: The number of times that the :meth:`loop` method has been called."""
        return self._iteration

    @property
    def start_time(self):
        """:obj:`datetime.datetime`: The time when the :meth:`loop` started."""
        return self._start_time

    @property
    def current_time(self):
        """:obj:`datetime.datetime`: The current time."""
        return datetime.datetime.now()

    @property
    def elapsed_time(self):
        """:obj:`datetime.datetime`: The elapsed time since the :meth:`loop` started."""
        return datetime.datetime.now() - self._start_time

    @property
    def user_label(self):
        """:obj:`QLabel`: The reference to a label that the user can modify the text of.

        See Also
        --------
        :obj:`update_label`
        """
        return self._user_label

    @property
    def max_iterations(self):
        """:obj:`int` or :obj:`None`: The maximum number of times that the :meth:`loop` will be called."""
        return self._max_iterations

    @property
    def loop_delay(self):
        """:obj:`int`: The time delay, in milliseconds, between successive calls to the :meth:`loop`."""
        return self._loop_delay

    def setup(self, **kwargs):
        """This method gets called before the :meth:`loop` starts.

        You can override this method to properly set up the task that you
        want to perform. For example, to open a file.

        The ``**kwargs`` that this method can receive are the additional keyword
        arguments that were passed in to :class:`LoopUntilAbort` class.
        """
        pass

    def loop(self):
        """The task to perform in a repeated loop.

        .. attention::
            You **MUST** override this method.
        """
        raise NotImplementedError("You must override the 'loop' method.")

    def teardown(self):
        """This method gets called after the :meth:`loop` stops.

        You can override this method to properly tear down the task that you
        want to perform. For example, to close a file.
        """
        pass

    def loop_once(self):
        """Run the :meth:`loop` method once.

        This method should be called if the :class:`LoopUntilAbort` class
        was initialized with `single_shot` = :obj:`True`, in order to run the
        :meth:`loop` method one more time.
        """
        if not self._loop_timer:
            raise RuntimeError('The loop timer has stopped')

        if not self._loop_timer.isSingleShot():
            self._stop_timers()
            raise RuntimeError('Single shots are not enabled')

        self._loop_timer.start(0)

    def update_label(self, text):
        """Update the text of the label that the user has access to.

        Parameters
        ----------
        text : :obj:`str`
            The text to display in the user-accessible label.

        See Also
        --------
        :obj:`user_label`
        """
        self._user_label.setText(text)

    def _shutdown(self, event):
        """Abort the loop"""

        # check whether max_iterations was reached
        if self._is_max_reached():
            event.accept()
            return

        # check that it is okay to abort
        if not self._loop_error and not prompt.question('Are you sure that you want to abort the loop?'):
            # need to check again whether max_iterations was reached while the prompt window was displayed
            if self._is_max_reached():
                prompt.information('The maximum number of iterations was already reached.\nLoop already aborted.')
                event.accept()
            else:
                event.ignore()
            return

        # need to check again whether max_iterations was reached after the prompt window was displayed
        if self._is_max_reached():
            event.accept()
            return

        self._main_window.statusBar().showMessage('Stopping the loop...')
        self._stop_timers()
        self._teardown()
        event.accept()

    def _update_runtime_label(self):
        """update the 'Elapsed time' label"""
        dt = datetime.datetime.now() - self.start_time
        hours, remainder = divmod(dt.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        base = 'Elapsed time {:02d}:{:02d}:{:02d} '.format(hours, minutes, seconds)
        if dt.days == 0:
            self._runtime_label.setText(base)
        elif dt.days == 1:
            self._runtime_label.setText(base + '(+1 day)')
        else:
            self._runtime_label.setText(base + '(+{} days)'.format(dt.days))

    def _update_iteration_label(self):
        """update the `Iterations` label"""
        self._iteration_label.setText('Iteration: {}'.format(self._iteration))

    def _call_loop(self):
        """call the loop method once"""
        if self._is_max_reached():
            self._stop_timers()
            msg = 'Maximum number of iterations reached ({})'.format(self._iteration)
            self._main_window.statusBar().showMessage(msg)
            prompt.information(msg)
            self._teardown()
        else:
            try:
                self._iteration += 1
                self.loop()
                self._update_iteration_label()
            except:
                msg = 'The following exception occurred in the loop() method:\n\n'
                prompt.critical(msg + traceback.format_exc())
                self._loop_error = True
                self._stop_timers()
                err_time = self.current_time.strftime('%d %B %Y at %H:%M:%S')
                self._main_window.statusBar().showMessage('Error occurred on ' + err_time)

    def _is_max_reached(self):
        """Whether the maximum number of iterations was reached"""
        return self._max_iterations is not None and self._iteration == self._max_iterations

    def _teardown(self):
        """Wraps the teardown method in a try..except block."""
        try:
            self.teardown()
        except:
            msg = 'The following exception occurred in the teardown() method:\n\n'
            prompt.critical(msg + traceback.format_exc())
            self._stop_timers()

    def _stop_timers(self):
        if self._loop_timer:
            self._loop_timer.stop()
            self._loop_timer = None
        if self._runtime_timer:
            self._runtime_timer.stop()
            self._runtime_timer = None

"""
Repeatedly perform a task until aborted by the user.
"""
import datetime
import traceback

from . import QtWidgets, QtCore, QtGui, application, prompt


class LoopUntilAbort(object):

    def __init__(self, loop_delay=0, max_iterations=None, title=None,
                 bg_color='#DFDFDF', text_color='#20548B',
                 font_family='Helvetica', font_size=14):
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
        """
        self._counter = 0
        self._loop_error = False
        self._max_iterations = int(max_iterations) if max_iterations is not None else None

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

        self._counter_label = QtWidgets.QLabel()
        self._counter_label.setFont(font)
        self._counter_label.setStyleSheet('color:{};'.format(text_hex_color))

        self._user_label = QtWidgets.QLabel()
        self._user_label.setFont(font)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self._runtime_label)
        vbox.addWidget(self._counter_label)
        vbox.addWidget(self._user_label)
        vbox.setStretchFactor(self._user_label, 1)
        self._central_widget.setLayout(vbox)

        self._runtime_timer = QtCore.QTimer()
        self._runtime_timer.timeout.connect(self._update_runtime_label)

        self._loop_timer = QtCore.QTimer()
        self._loop_timer.timeout.connect(self._call_loop)

        self._start_time = datetime.datetime.now()
        s = self._start_time.strftime('%d %B %Y at %H:%M:%S')
        self._main_window.statusBar().showMessage('Started ' + s)
        self._update_runtime_label()
        self._update_iteration_label()

        try:
            self.setup()
            self._runtime_timer.start(1000)
            loop_delay = max(0, int(loop_delay))
            if loop_delay > 0:
                self._call_loop()
            self._loop_timer.start(loop_delay)
            self._main_window.show()
            self._app.exec_()
        except:
            msg = 'The following exception occurred in the setup() method:\n\n{}'.format(traceback.format_exc())
            prompt.critical(msg, title)

    @property
    def counter(self):
        """:obj:`int`: The number of times that the :meth:`loop` method has been called."""
        return self._counter

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
        """:obj:`int` or :obj:`None`: The maximum number of times to call the :meth:`loop` method."""
        return self._max_iterations

    @property
    def loop_delay(self):
        """:obj:`int`: The time delay, in milliseconds, between successive calls to the loop method."""
        return self._loop_timer.interval()

    def setup(self):
        """This method gets called before the :meth:`loop` starts.

        You can override this method to properly set up the task that you
        want to perform. For example, to open a file.
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
        """abort the loop"""

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
        self._loop_timer.stop()
        self._runtime_timer.stop()
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
        """update the 'Iterations' label"""
        self._counter_label.setText('Iterations: {}'.format(self._counter))

    def _call_loop(self):
        """call the loop method once"""
        if self._is_max_reached():
            self._loop_timer.stop()
            self._runtime_timer.stop()
            msg = 'Maximum number of iterations reached ({})'.format(self._counter)
            self._main_window.statusBar().showMessage(msg)
            self._teardown()
        else:
            try:
                self.loop()
                self._counter += 1
                self._update_iteration_label()
            except:
                msg = 'The following exception occurred in the loop() method:\n\n{}'.format(traceback.format_exc())
                prompt.critical(msg)
                self._loop_error = True
                self._main_window.close()

    def _is_max_reached(self):
        """Whether the maximum number of iterations was reached"""
        return self._max_iterations is not None and self._counter == self._max_iterations

    def _teardown(self):
        """Wraps the teardown method in a try..except block."""
        try:
            self.teardown()
        except:
            msg = 'The following exception occurred in the teardown() method:\n\n{}'.format(traceback.format_exc())
            prompt.critical(msg)

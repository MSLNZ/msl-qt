"""
Repeatedly perform a task until aborted by the user.
"""
import datetime
import traceback

from . import QtWidgets, QtCore, QtGui, application, prompt


class LoopUntilAbort(object):

    def __init__(self, loop_delay=0, max_iterations=None, single_shot=False,
                 title=None, bg_color='#DFDFDF', text_color='#20548B',
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

        Examples
        --------
        To run the above example enter the following:

        >>> from msl.examples.qt import LoopExample
        >>> loop = LoopExample() # doctest: +SKIP
        >>> loop.start() # doctest: +SKIP

        Another example which uses *single-shot* mode:

        >>> from msl.examples.qt import LoopExampleSleep
        >>> loop = LoopExampleSleep() # doctest: +SKIP
        >>> loop.start() # doctest: +SKIP

        Parameters
        ----------
        loop_delay : :class:`int`, optional
            The delay time, in milliseconds, to wait between successive calls
            to the :meth:`loop` method. For example, if `loop_delay` = ``0``
            then there is no time delay between successive calls to the
            :meth:`loop` method; if `loop_delay` = ``1000`` then wait 1 second
            between successive calls to the :meth:`loop` method.
        max_iterations : :class:`int`, optional
            The maximum number of times to call the :meth:`loop` method. The
            default value is :obj:`None`, which means to loop until the user
            aborts the program.
        single_shot : :class:`bool`, optional
            Whether to call the :meth:`loop` method once (and only once). If
            you specify the value to be :obj:`True` then you must call the
            :meth:`loop_once` method in the subclass whenever you want to
            run the :meth:`loop` one more time. This is useful if the
            :meth:`loop` depends on external factors (e.g., waiting for an
            oscilloscope to download a trace after a trigger event) and the
            amount of time that the :meth:`loop` requires to complete is not
            known.
        title : :class:`str`, optional
            The text to display in the title bar of the
            :class:`QtWidgets.QMainWindow`. If :obj:`None` then uses the name
            of the subclass as the title.
        bg_color : :class:`QtGui.QColor`, optional
            The background color of the :class:`QtWidgets.QMainWindow`. Can be
            any data type and value that the constructor of a :class:`QtGui.QColor`
            accepts.
        text_color : :class:`QtGui.QColor`, optional
            The color of the **Elapsed time** and **Iteration** text.Can be
            any data type and value that the constructor of a :class:`QtGui.QColor`
            accepts.
        font_family : :class:`QtGui.QFont`, optional
            The font family to use for the text. Can be any value that the
            constructor of a :class:`QtGui.QFont` accepts.
        font_size : :class:`int`, optional
            The font size of the text.
        """
        self._iteration = 0
        self._loop_error = False
        self._start_time = None
        self._loop_delay = loop_delay
        self._single_shot = single_shot

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

        self._elapsed_time_label = QtWidgets.QLabel()
        self._elapsed_time_label.setFont(font)
        self._elapsed_time_label.setStyleSheet('color:{};'.format(text_hex_color))

        self._iteration_label = QtWidgets.QLabel()
        self._iteration_label.setFont(font)
        self._iteration_label.setStyleSheet('color:{};'.format(text_hex_color))

        self._user_label = QtWidgets.QLabel()
        self._user_label.setFont(font)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self._elapsed_time_label)
        vbox.addWidget(self._iteration_label)
        vbox.addWidget(self._user_label)
        vbox.setStretchFactor(self._user_label, 1)
        self._central_widget.setLayout(vbox)

        self._elapsed_time_timer = QtCore.QTimer()
        self._elapsed_time_timer.timeout.connect(self._update_elapsed_time_label)

        self._loop_timer = QtCore.QTimer()
        self._loop_timer.timeout.connect(self._call_loop)

    @property
    def current_time(self):
        """:class:`datetime.datetime`: The current time."""
        return datetime.datetime.now()

    @property
    def elapsed_time(self):
        """:class:`datetime.datetime`: The elapsed time since the :meth:`loop` started."""
        return self.current_time - self._start_time

    @property
    def iteration(self):
        """:class:`int`: The number of times that the :meth:`loop` method has been called."""
        return self._iteration

    @property
    def loop_delay(self):
        """:class:`int`: The time delay, in milliseconds, between successive calls to the :meth:`loop`."""
        return self._loop_delay

    @property
    def loop_timer(self):
        """:class:`QtCore.QTimer`: The reference to the :meth:`loop`\'s timer."""
        return self._loop_timer

    @property
    def main_window(self):
        """:class:`QtWidgets.QMainWindow`: The reference to the main window."""
        return self._main_window

    @property
    def max_iterations(self):
        """:class:`int` or :obj:`None`: The maximum number of times that the :meth:`loop` will be called."""
        return self._max_iterations

    @property
    def start_time(self):
        """:class:`datetime.datetime`: The time when the :meth:`loop` started."""
        return self._start_time

    @property
    def user_label(self):
        """:class:`QtWidgets.QLabel`: The reference to the label object that the user can modify the text of.

        See Also
        --------
        :meth:`set_label_text`
            To set the text of the :class:`QtWidgets.QLabel`.
        """
        return self._user_label

    def cleanup(self):
        """This method gets called when the :class:`QtWidgets.QMainWindow` is closing.

        You can override this method to properly cleanup any tasks.
        For example, to close a file that is open.
        """
        pass

    def loop(self):
        """The task to perform in a loop.

        .. attention::
            You **MUST** override this method.
        """
        raise NotImplementedError("You must override the 'loop' method.")

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

    def set_label_text(self, text):
        """Update the text of the label that the user has access to.

        Parameters
        ----------
        text : :class:`str`
            The text to display in the user-accessible label.

        See Also
        --------
        :meth:`user_label`
            For the reference to the :class:`QtWidgets.QLabel` object.
        """
        self._user_label.setText(text)

    def set_status_bar_text(self, text):
        """Set the text to display in the status bar of the :class:`QtWidgets.QMainWindow`.

        Parameters
        ----------
        text : :class:`str`
            The text to display in the status bar of the :class:`QtWidgets.QMainWindow`.
        """
        self._main_window.statusBar().showMessage(text)

    def start(self):
        """Show the :class:`QtWidgets.QMainWindow` and start looping."""
        self._start_time = self.current_time
        s = self._start_time.strftime('%d %B %Y at %H:%M:%S')
        self.set_status_bar_text('Started ' + s)
        self._update_elapsed_time_label()
        self._update_iteration_label()
        self._loop_delay = max(0, int(self._loop_delay)) if not self._single_shot else 0
        if self._loop_delay > 0:
            self._call_loop()
        self._loop_timer.setSingleShot(self._single_shot)
        self._loop_timer.start(self._loop_delay)
        self._elapsed_time_timer.start(1000)
        self._main_window.show()
        self._app.exec_()

    def _call_loop(self):
        """Call the loop method once."""
        if self._is_max_reached():
            self._stop_timers()
            msg = 'Maximum number of iterations reached ({})'.format(self._iteration)
            self.set_status_bar_text(msg)
            prompt.information(msg)
        else:
            self._iteration += 1
            try:
                self.loop()
            except:
                msg = 'The following exception occurred in the loop() method:\n\n'
                prompt.critical(msg + traceback.format_exc())
                self._loop_error = True
                self._stop_timers()
                err_time = self.current_time.strftime('%d %B %Y at %H:%M:%S')
                self.set_status_bar_text('Error occurred on ' + err_time)
            else:
                self._update_iteration_label()

    def _cleanup(self):
        """Wraps the cleanup method in a try..except block."""
        try:
            self.cleanup()
        except:
            msg = 'The following exception occurred in the cleanup() method:\n\n'
            prompt.critical(msg + traceback.format_exc())
            self._stop_timers()

    def _is_max_reached(self):
        """Whether the maximum number of iterations was reached"""
        return self._max_iterations is not None and self._iteration == self._max_iterations

    def _shutdown(self, event):
        """Abort the loop"""

        # check that it is okay to abort
        if not self._is_max_reached() and not self._loop_error:
            if not prompt.yes_no('Are you sure that you want to abort the loop?'):
                # check again whether max_iterations was reached while the prompt window was displayed
                if self._is_max_reached():
                    prompt.information('The maximum number of iterations was already reached.\n'
                                       'Loop already aborted.')
                event.ignore()
                return

        self._stop_timers()
        self._cleanup()
        event.accept()

    def _stop_timers(self):
        """Stop and delete the timers."""
        if self._loop_timer:
            self._loop_timer.stop()
            self._loop_timer = None
        if self._elapsed_time_timer:
            self._elapsed_time_timer.stop()
            self._elapsed_time_timer = None

    def _update_elapsed_time_label(self):
        """update the 'Elapsed time' label"""
        dt = self.elapsed_time
        hours, remainder = divmod(dt.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        base = 'Elapsed time {:02d}:{:02d}:{:02d} '.format(hours, minutes, seconds)
        if dt.days == 0:
            self._elapsed_time_label.setText(base)
        elif dt.days == 1:
            self._elapsed_time_label.setText(base + '(+1 day)')
        else:
            self._elapsed_time_label.setText(base + '(+{} days)'.format(dt.days))

    def _update_iteration_label(self):
        """update the `Iteration` label"""
        self._iteration_label.setText('Iteration {}'.format(self._iteration))

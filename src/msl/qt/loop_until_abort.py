"""Repeatedly perform a task until aborted by the user."""

from __future__ import annotations

import traceback
from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING

from ._qt import Qt, QtCore, QtGui, QtWidgets, application
from .convert import to_qcolor, to_qfont
from .prompt import critical, information, yes_no

if TYPE_CHECKING:
    from datetime import timedelta

    from .typing import Color, Font


class LoopUntilAbort(ABC):
    """Repeatedly perform a task until aborted by the user."""

    def __init__(
        self,
        *,
        loop_delay: int = 0,
        max_iterations: int = -1,
        single_shot: bool = False,
        title: str | None = None,
        bg_color: Color | None = None,
        text_color: Color | None = None,
        font: Font | None = None,
    ) -> None:
        """Repeatedly perform a task until aborted by the user.

        This class provides an interface to show the status of a task (e.g., read
        a sensor value and write the value to a file) that you want to perform for
        an unknown period of time (e.g., during lunch or overnight) and you want to
        stop the task whenever you return. It can be regarded as a way to tell
        your program to *"get as much data as possible until I get back"*.

        The following example illustrates how to repeatedly write data to a file in a loop:

        ??? example
            <!-- fmt: off -->
            ```python
            --8<-- "src/msl/examples/qt/loop_until_abort.py"
            ```
            <!-- fmt: on -->

        !!! example
            ```python
            from msl.examples.qt import LoopExample
            loop = LoopExample()
            loop.start()
            ```

            Another example which uses *single-shot* mode
            ```python
            from msl.examples.qt import LoopExampleSleep
            loop = LoopExampleSleep()
            loop.start()
            ```

        Args:
            loop_delay: The delay time, in milliseconds, to wait between successive
                calls to the [loop][..loop] method.
            max_iterations: The maximum number of times to call the [loop][..loop] method.
                The default value is `-1`, which means to loop until the user aborts the program.
            single_shot: Whether to call the [loop][..loop] method once (and only once).
                If you specify the value to be `True` then you must call the [loop_once][..loop_once]
                method in the subclass whenever you want to run the [loop][..loop] one more time.
                This is useful if the [loop][..loop] depends on external factors (e.g., waiting for
                an oscilloscope to download a trace after a trigger event) and the amount of time
                that the [loop][..loop] requires to complete is not known.
            title: The text to display in the title bar of the window. If `None`, then uses the name
                of the subclass as the title.
            bg_color: The background color of the window. The default color is chosen based on
                the color scheme of the operating system.
            text_color: The color of the *Elapsed time* and *Iteration* text.
                The default color is chosen based on the color scheme of the operating system.
            font: The font to use for the text.
        """
        self._iteration: int = 0
        self._loop_error: bool = False
        self._start_time: datetime = datetime.fromtimestamp(0)  # noqa: DTZ006
        self._loop_delay: int = loop_delay
        self._single_shot: bool = single_shot

        self._max_iterations: int = int(max_iterations)

        self._app: QtWidgets.QApplication = application()

        if text_color is None:
            text_color = self._app.palette().color(QtGui.QPalette.ColorRole.Text)

        if bg_color is None:
            scheme = self._app.styleHints().colorScheme()
            bg = self._app.palette().color(QtGui.QPalette.ColorRole.Window)
            bg_color = bg.lighter(150) if scheme == Qt.ColorScheme.Dark else bg.darker(110)

        self._central_widget: QtWidgets.QWidget = QtWidgets.QWidget()
        bg_hex_color = to_qcolor(bg_color).name()
        self._central_widget.setStyleSheet(f"background:{bg_hex_color};")

        self._main_window: QtWidgets.QMainWindow = QtWidgets.QMainWindow()
        self._main_window.setCentralWidget(self._central_widget)
        self._main_window.closeEvent = self._shutdown  # type: ignore[method-assign]
        if title is None:
            title = self.__class__.__name__
        self._main_window.setWindowTitle(title)
        self._main_window.setWindowFlags(Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.WindowMinimizeButtonHint)

        font = to_qfont(font)
        text_hex_color = to_qcolor(text_color).name()

        self._elapsed_time_label: QtWidgets.QLabel = QtWidgets.QLabel()
        self._elapsed_time_label.setFont(font)
        self._elapsed_time_label.setStyleSheet(f"color:{text_hex_color};")

        self._iteration_label: QtWidgets.QLabel = QtWidgets.QLabel()
        self._iteration_label.setFont(font)
        self._iteration_label.setStyleSheet(f"color:{text_hex_color};")

        self._user_label: QtWidgets.QLabel = QtWidgets.QLabel()
        self._user_label.setFont(font)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self._elapsed_time_label)
        vbox.addWidget(self._iteration_label)
        vbox.addWidget(self._user_label)
        _ = vbox.setStretchFactor(self._user_label, 1)
        self._central_widget.setLayout(vbox)

        self._elapsed_time_timer: QtCore.QTimer = QtCore.QTimer()
        _ = self._elapsed_time_timer.timeout.connect(self._update_elapsed_time_label)

        self._loop_timer: QtCore.QTimer = QtCore.QTimer()
        _ = self._loop_timer.timeout.connect(self._call_loop)

    @property
    def current_time(self) -> datetime:
        """[datetime][] &mdash; The current date and time."""
        return datetime.now()  # noqa: DTZ005

    @property
    def elapsed_time(self) -> timedelta:
        """[timedelta][] &mdash; The elapsed time since the [loop][..loop] started."""
        return self.current_time - self._start_time

    @property
    def iteration(self) -> int:
        """[int][] &mdash; The number of times that the [loop][..loop] method has been called."""
        return self._iteration

    @property
    def loop_delay(self) -> int:
        """[int][] &mdash; The time delay, in milliseconds, between successive calls to the [loop][..loop]."""
        return self._loop_delay

    @property
    def loop_timer(self) -> QtCore.QTimer:
        """[QTimer][QtCore.QTimer] &mdash; The reference to the [loop][..loop]s timer."""
        return self._loop_timer

    @property
    def main_window(self) -> QtWidgets.QMainWindow:
        """[QMainWindow][QtWidgets.QMainWindow] &mdash; The reference to the main window."""
        return self._main_window

    @property
    def max_iterations(self) -> int:
        """[int][] &mdash; The maximum number of times that the [loop][..loop] will be called.

        A value &lt;0 means there is no limit.
        """
        return self._max_iterations

    @property
    def start_time(self) -> datetime:
        """[datetime][] &mdash; The time when the [loop][..loop] started."""
        return self._start_time

    @property
    def user_label(self) -> QtWidgets.QLabel:
        """[QLabel][QtWidgets.QLabel] &mdash; The reference to the label object that the user can modify the text of.

        !!! note "See Also"
            [set_label_text][..set_label_text] &mdash; To set the text of the [QLabel][QtWidgets.QLabel].
        """
        return self._user_label

    def cleanup(self) -> None:
        """This method gets called when the [QMainWindow][QtWidgets.QMainWindow] is closing.

        Override this method to properly clean up any tasks, e.g., to close a file that is open.
        """
        return

    @abstractmethod
    def loop(self) -> None:
        """The task to perform in a loop.

        !!! warning
            You must override this method.
        """

    def loop_once(self) -> None:
        """Run the [loop][..loop] method once.

        This method should be called if the class was initialized with `single_shot=True`,
        in order to run the [loop][..loop] method one more time.
        """
        if not self._loop_timer:
            msg = "The loop timer has stopped"
            raise RuntimeError(msg)

        if not self._loop_timer.isSingleShot():
            self._stop_timers()
            msg = "Single shots are not enabled"
            raise RuntimeError(msg)

        self._loop_timer.start(0)

    def set_label_text(self, text: str) -> None:
        """Update the text of the label that the user has access to.

        Args:
            text: The text to display in the user-accessible label.

        !!! note "See Also"
            [user_label][..user_label] &mdash; For the reference to the [QLabel][QtWidgets.QLabel] object.
        """
        self._user_label.setText(text)

    def set_status_bar_text(self, text: str) -> None:
        """Set the text to display in the status bar of the [QMainWindow][QtWidgets.QMainWindow].

        Args:
            text: The text to display in the status bar of the [QMainWindow][QtWidgets.QMainWindow].
        """
        self._main_window.statusBar().showMessage(text)

    def start(self) -> None:
        """Show the [QMainWindow][QtWidgets.QMainWindow] and start looping."""
        self._start_time = self.current_time
        s = self._start_time.strftime("%d %B %Y at %H:%M:%S")
        self.set_status_bar_text(f"Started {s}")
        self._update_elapsed_time_label()
        self._update_iteration_label()
        self._loop_delay = max(0, int(self._loop_delay)) if not self._single_shot else 0
        if self._loop_delay > 0:
            self._call_loop()
        self._loop_timer.setSingleShot(self._single_shot)
        self._loop_timer.start(self._loop_delay)
        self._elapsed_time_timer.start(1000)
        self._main_window.show()
        _ = self._app.exec()

    def _call_loop(self) -> None:
        """Call the loop method once."""
        if self._is_max_reached():
            self._stop_timers()
            msg = f"Maximum number of iterations reached ({self._iteration})"
            self.set_status_bar_text(msg)
            information(msg)
        else:
            self._iteration += 1
            try:
                self.loop()
            except:  # noqa: E722
                msg = "The following exception occurred in the loop() method:\n\n"
                critical(msg + traceback.format_exc())
                self._loop_error = True
                self._stop_timers()
                err_time = self.current_time.strftime("%d %B %Y at %H:%M:%S")
                self.set_status_bar_text("Error occurred on " + err_time)
            else:
                self._update_iteration_label()

    def _cleanup(self) -> None:
        """Wraps the cleanup method in a try-except block."""
        try:
            self.cleanup()
        except:  # noqa: E722
            msg = "The following exception occurred in the cleanup() method:\n\n"
            critical(msg + traceback.format_exc())
            self._stop_timers()

    def _is_max_reached(self) -> bool:
        """Whether the maximum number of iterations was reached."""
        return self._max_iterations > 0 and self._iteration == self._max_iterations

    def _shutdown(self, event: QtGui.QCloseEvent) -> None:
        """Abort the loop."""
        if (
            (not self._is_max_reached())
            and (not self._loop_error)
            and (not yes_no("Are you sure that you want to abort the loop?"))
        ):
            # check again whether max_iterations was reached while the prompt window was displayed
            if self._is_max_reached():
                information("The maximum number of iterations was already reached.\nLoop already aborted.")
            event.ignore()
            return

        self._stop_timers()
        self._cleanup()
        event.accept()

    def _stop_timers(self) -> None:
        """Stop the timers."""
        self._loop_timer.stop()
        self._elapsed_time_timer.stop()

    def _update_elapsed_time_label(self) -> None:
        """Update the 'Elapsed time' label."""
        dt = self.elapsed_time
        hours, remainder = divmod(dt.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        base = f"Elapsed time {hours:02d}:{minutes:02d}:{seconds:02d}"
        if dt.days == 0:
            self._elapsed_time_label.setText(base)
        elif dt.days == 1:
            self._elapsed_time_label.setText(f"{base} (+1 day)")
        else:
            self._elapsed_time_label.setText(f"{base} (+{dt.days} days)")

    def _update_iteration_label(self) -> None:
        """Update the `Iteration` label."""
        self._iteration_label.setText(f"Iteration {self._iteration}")

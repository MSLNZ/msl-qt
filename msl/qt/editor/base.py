import sys
import logging

from .. import (
    QtWidgets,
    QtGui,
    Qt,
    Signal,
)
from .modes.syntax_highlighter import ColorScheme
from .managers import (
    ModeManager,
    PanelManager,
)

logger = logging.getLogger(__name__)


class BaseEditor(QtWidgets.QPlainTextEdit):

    key_press_event = Signal(QtGui.QKeyEvent)
    key_release_event = Signal(QtGui.QKeyEvent)
    new_text_event = Signal()
    new_color_scheme_event = Signal(ColorScheme)
    paint_event = Signal(QtGui.QPaintEvent)
    resize_event = Signal(QtGui.QResizeEvent)
    mouse_release_event = Signal(QtGui.QMouseEvent)
    paste_event = Signal(str)  # the text from the clipboard

    # the QTextCursor has WordUnderCursor selected
    mouse_move_event = Signal(QtGui.QMouseEvent, QtGui.QTextCursor)

    # see http://doc.qt.io/qt-5/qt.html#KeyboardModifier-enum
    ControlModifier = Qt.MetaModifier if sys.platform == 'darwin' else Qt.ControlModifier

    def __init__(self, *, parent=None, font=None, cursor_width=2):
        super(BaseEditor, self).__init__(parent)

        logger.debug('initialized ' + str(self))

        self.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.setCursorWidth(cursor_width)
        self.setMouseTracking(True)

        # the self._inserted_length variable is required for LinterMode because
        # some modes (like IndentDedentMode, AutoCompleteMode) modify the text
        # in the BaseEditor and therefore the start and end position of the
        # cursor needs to be shifted by self._inserted_length when removing the
        # previous QTextCharFormat.WaveUnderline's
        self._inserted_length = 0

        if font is None:
            font = QtGui.QFont('Courier New', 10)
        elif isinstance(font, int):
            font = QtGui.QFont('Courier New', font)
        elif isinstance(font, str):
            font = QtGui.QFont(font, 10)
        elif isinstance(font, (list, tuple)):
            font = QtGui.QFont(*font)
        self.setFont(font)

        self._modes = ModeManager(self)
        self._panels = PanelManager(self)
        self._color_scheme = None
        self._is_code_completer_visible = False

    def __repr__(self):
        return '<{} id={:#x}>'.format(self.__class__.__name__, id(self))

    @property
    def color_scheme(self):
        """:class:`ColorScheme`: The current color scheme."""
        return self._color_scheme

    @color_scheme.setter
    def color_scheme(self, name):
        if self._color_scheme and name == self._color_scheme.name:
            return
        logger.debug('update color scheme to ' + name)
        self._color_scheme = ColorScheme(name)
        self.new_color_scheme_event.emit(self._color_scheme)

    @property
    def modes(self):
        """:class:`ModeManager`: The modes that are currently in use."""
        return self._modes

    @property
    def panels(self):
        """:class:`PanelManager`: The panels that are currently in use."""
        return self._panels

    def keyPressEvent(self, event):
        """Overrides `keyPressEvent <https://doc.qt.io/qt-5/qwidget.html#keyPressEvent>`_."""
        logger.debug('keyPressEvent: text={!r}, key={}, CTRL={}'.format(
            event.text(), event.key(), event.modifiers() == self.ControlModifier))

        self.key_press_event.emit(event)
        if event.isAccepted():
            QtWidgets.QPlainTextEdit.keyPressEvent(self, event)

    def keyReleaseEvent(self, event):
        """Overrides `keyReleaseEvent <https://doc.qt.io/qt-5/qwidget.html#keyReleaseEvent>`_."""
        logger.debug('keyReleaseEvent: text={!r}, key={}, CTRL={}'.format(
            event.text(), event.key(), event.key() == Qt.Key_Control))

        self.key_release_event.emit(event)
        if event.isAccepted():
            QtWidgets.QPlainTextEdit.keyReleaseEvent(self, event)

    def wheelEvent(self, event):
        """Overrides `wheelEvent <https://doc.qt.io/qt-5/qwidget.html#wheelEvent>`_."""
        if event.modifiers() == self.ControlModifier:
            if event.angleDelta().y() < 0:
                self.zoomOut()
            else:
                self.zoomIn()
        else:
            QtWidgets.QPlainTextEdit.wheelEvent(self, event)

    def resizeEvent(self, event):
        """Overrides `resizeEvent <https://doc.qt.io/qt-5/qwidget.html#resizeEvent>`_."""
        self.resize_event.emit(event)
        QtWidgets.QPlainTextEdit.resizeEvent(self, event)

    def paintEvent(self, event):
        """Overrides `paintEvent <https://doc.qt.io/qt-5/qwidget.html#paintEvent>`_."""
        self.paint_event.emit(event)
        QtWidgets.QPlainTextEdit.paintEvent(self, event)

    def mouseMoveEvent(self, event):
        """Overrides `mouseMoveEvent <https://doc.qt.io/qt-5/qwidget.html#mouseMoveEvent>`_."""
        cursor = self.cursorForPosition(event.pos())
        cursor.select(cursor.WordUnderCursor)
        self.mouse_move_event.emit(event, cursor)
        QtWidgets.QPlainTextEdit.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        """Overrides `mouseReleaseEvent <https://doc.qt.io/qt-5/qwidget.html#mouseReleaseEvent>`_."""
        self.mouse_release_event.emit(event)
        if event.isAccepted():
            QtWidgets.QPlainTextEdit.mouseReleaseEvent(self, event)

    def canInsertFromMimeData(self, source):
        """Overrides `canInsertFromMimeData <http://doc.qt.io/qt-5/qplaintextedit.html#canInsertFromMimeData>`_."""
        logger.debug('canInsertFromMimeData')
        if source.hasUrls():
            for url in source.urls():
                print(url)
        return False

    def insertFromMimeData(self, source):
        """Overrides `insertFromMimeData <http://doc.qt.io/qt-5/qplaintextedit.html#insertFromMimeData>`_."""
        if source.hasText():
            self.insertPlainText(source.text())
            self.paste_event.emit(source.text())

    def text(self):
        """Returns the text in the editor.

        Returns
        -------
        :class:`str`
            The text in the editor.
        """
        return self.toPlainText()

    def set_text(self, text):
        """Set the text of the editor.

        Emits the `new_text_event` signal.

        Parameters
        ----------
        text : class:`str`
            The text to set the editor to.
        """
        self.setPlainText(text)
        self.new_text_event.emit()

    @staticmethod
    def is_alphanumeric_or_underscore(text):
        """Is the text alphanumeric or an underscore?

        Parameters
        ----------
        text : :class:`str`
            The text to check.

        Returns
        -------
        :class:`bool`
            Whether the `text` is alphanumeric or an underscore.
        """
        if not text:
            return False
        if text.isalnum():
            return True
        for char in text:
            if not (char == '_' or char.isalnum()):
                return False
        return True

    @staticmethod
    def is_navigation(event):
        """Is the key event a navigation key?

        Parameters
        ----------
        event : :class:`QtGui.QKeyEvent`
            A key event.

        Returns
        -------
        :class:`bool`
            Whether the `event` is a navigation key.
        """
        key = event.key()
        return key == Qt.Key_Up or \
               key == Qt.Key_Down or \
               key == Qt.Key_Left or \
               key == Qt.Key_Right or \
               key == Qt.Key_Home or \
               key == Qt.Key_End or \
               key == Qt.Key_PageUp or \
               key == Qt.Key_PageDown

    def code_completer_popup_event(self, is_visible):
        """ slot """
        self._is_code_completer_visible = bool(is_visible)

    @property
    def is_code_completer_visible(self):
        """:class:`bool`: Returns whether the popup for the :class:`CodeCompleteMode` is currently visible."""
        return self._is_code_completer_visible

    def inserted_length_event(self, length):
        """ slot """
        self._inserted_length = int(length)

    @property
    def inserted_length(self):
        """:class:`int`: Returns the length of the text that was inserted by a :class:`Mode`."""
        return self._inserted_length

    def hyperlink_external_event(self, path, cursor_position):
        """ slot: hyperlink to an object that is located outside of the text in the editor."""
        with open(path) as fp:
            text = fp.read()

        name = self.color_scheme.name if self.color_scheme else None
        editor = self.__class__(font=self.font(), color_scheme_name=name)
        editor.set_text(text)
        editor.setWindowTitle(path)

        cursor = editor.textCursor()
        cursor.setPosition(cursor_position)
        editor.setTextCursor(cursor)

        desktop = QtWidgets.QDesktopWidget()
        n = desktop.screenNumber(QtGui.QCursor.pos())
        geo = desktop.availableGeometry(n)
        editor.resize(geo.width() * 2 // 3, geo.height() // 2)
        editor.show()

    def peek_left(self, n=1):
        """See what characters are to the left of the cursor.

        The position of the cursor remains unchanged upon return.

        Parameters
        ----------
        n : :class:`int`
            The number of characters to peek.

        Returns
        -------
        :class:`str`
            The character(s) to the left of the cursor.
        """
        return self._peek(QtGui.QTextCursor.Left, n)

    def peek_right(self, n=1):
        """See what characters are to the right of the cursor.

        The position of the cursor remains unchanged upon return.

        Parameters
        ----------
        n : :class:`int`
            The number of characters to peek.

        Returns
        -------
        :class:`str`
            The character(s) to the right of the cursor.
        """
        return self._peek(QtGui.QTextCursor.Right, n)

    def _peek(self, operation, n):
        if n < 1:
            return ''
        cursor = self.textCursor()
        cursor.movePosition(operation, cursor.KeepAnchor, n=n)
        return cursor.selectedText()

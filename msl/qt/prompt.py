"""
Convenience functions to prompt the user.

The following functions create a pop-up window to either notify the user of an
event that happened or to request information from the user.
"""
from PyQt5 import QtWidgets, QtCore

from msl.qt import application


def critical(message, title=None):
    """Displays the critical `message` in a pop-up window.

    Parameters
    ----------
    message : :obj:`str` or :obj:`Exception`
        The message to display.
    title : :obj:`str`, optional
        The text to display in the title bar of the pop-up window.
        If :obj:`None` then uses the text in the title bar of the active window.
    """
    app, title = _get_app_and_title(title)
    QtWidgets.QMessageBox.critical(app.activeWindow(), title, str(message))


def warning(message, title=None):
    """Displays the warning `message` in a pop-up window.

    Parameters
    ----------
    message : :obj:`str` or :obj:`Exception`
        The message to display.
    title : :obj:`str`, optional
        The text to display in the title bar of the pop-up window.
        If :obj:`None` then uses the text in the title bar of the active window.
    """
    app, title = _get_app_and_title(title)
    QtWidgets.QMessageBox.warning(app.activeWindow(), title, str(message))


def information(message, title=None):
    """Displays the information `message` in a pop-up window.

    Parameters
    ----------
    message : :obj:`str` or :obj:`Exception`
        The message to display.
    title : :obj:`str`, optional
        The text to display in the title bar of the pop-up window.
        If :obj:`None` then uses the text in the title bar of the active window.
    """
    app, title = _get_app_and_title(title)
    QtWidgets.QMessageBox.information(app.activeWindow(), title, str(message))


def question(message, default=True, title=None):
    """Ask the user a question to receive a ``Yes`` or ``No`` answer.

    Parameters
    ----------
    message : :obj:`str`
        The question to ask the user.
    default : :obj:`bool`, optional
        The answer to be selected by default. If :obj:`True` then ``Yes`` is
        the default answer, if :obj:`False` then ``No`` is the default answer.
    title : :obj:`str`, optional
        The text to display in the title bar of the pop-up window.
        If :obj:`None` then uses the text in the title bar of the active window.

    Returns
    -------
    :obj:`bool`
        :obj:`True` if the user answered ``Yes``, :obj:`False` otherwise.
    """
    app, title = _get_app_and_title(title)
    d = QtWidgets.QMessageBox.Yes if default else QtWidgets.QMessageBox.No
    answer = QtWidgets.QMessageBox.question(app.activeWindow(), title, message, defaultButton=d)
    return answer == QtWidgets.QMessageBox.Yes


def double(message, default=0, minimum=-2147483647, maximum=2147483647, precision=1, title=None):
    """Get a floating-point value from the user.

    Parameters
    ----------
    message : :obj:`str`
        The message that is shown to the user to describe what the value represents.
    default : :obj:`float`, optional
        The default floating-point value.
    minimum : :obj:`float`, optional
        The minimum value that the user can enter.
    maximum : :obj:`float`, optional
        The maximum value that the user can enter.
    precision : :obj:`int`, optional
        The number of digits that are displayed after the decimal point.
    title : :obj:`str`, optional
        The text to display in the title bar of the pop-up window.
        If :obj:`None` then uses the text in the title bar of the active window.

    Returns
    -------
    :obj:`float` or :obj:`None`
        The floating-point value or :obj:`None` if the user cancelled
        the request to enter a number.
    """
    app, title = _get_app_and_title(title)
    value, ok = QtWidgets.QInputDialog.getDouble(app.activeWindow(), title, message,
                                                 default, minimum, maximum, precision,
                                                 flags=QtCore.Qt.WindowCloseButtonHint)
    return value if ok else None


def integer(message, default=0, minimum=-2147483647, maximum=2147483647, step=1, title=None):
    """Get an integer value from the user.

    Parameters
    ----------
    message : :obj:`str`
        The message that is shown to the user to describe what the value represents.
    default : :obj:`float`, optional
        The default floating-point value.
    minimum : :obj:`float`, optional
        The minimum value that the user can enter.
    maximum : :obj:`float`, optional
        The maximum value that the user can enter.
    step : :obj:`int`, optional
        The amount by which the values change as the user presses the arrow
        buttons to increment or decrement the value.
    title : :obj:`str`, optional
        The text to display in the title bar of the pop-up window.
        If :obj:`None` then uses the text in the title bar of the active window.

    Returns
    -------
    :obj:`int` or :obj:`None`
        The integer value or :obj:`None` if the user cancelled the request to
        enter a number.
    """
    app, title = _get_app_and_title(title)
    value, ok = QtWidgets.QInputDialog.getInt(app.activeWindow(), title, message,
                                              default, minimum, maximum, step,
                                              flags=QtCore.Qt.WindowCloseButtonHint)
    return value if ok else None


def item(message, items, index=0, title=None):
    """Select an item from a list of items.

    Parameters
    ----------
    message : :obj:`str`
        The message that is shown to the user to describe what the list of items represent.
    items : :obj:`list` of :obj:`object`
        The list of items to choose from.
    index : :obj:`int`, optional
        The index of the default item that is selected.
    title : :obj:`str`, optional
        The text to display in the title bar of the pop-up window.
        If :obj:`None` then uses the text in the title bar of the active window.

    Returns
    -------
    :obj:`object`
        The selected item or :obj:`None` if the user cancelled the request to select an item.

        .. note::
            The data type of the selected item is preserved. For example, if
            `items` = ``[1, 2.0, 2+3j, 'hello', b'world', True, QtWidgets.QPushButton]``
            and the user selects the ``True`` item then :obj:`True` is returned.

    """
    app, title = _get_app_and_title(title)
    items_ = [str(i) for i in items]
    value, ok = QtWidgets.QInputDialog.getItem(app.activeWindow(), title, message, items_, index,
                                               editable=False,
                                               flags=QtCore.Qt.WindowCloseButtonHint,
                                               inputMethodHints=QtCore.Qt.ImhNone)
    return items[items_.index(value)] if ok else None


def text(message, default='', multi_line=False, title=None):
    """Get text from the user.

    Parameters
    ----------
    message : :obj:`str`
        The message that is shown to the user to describe what the text represents.
    default : :obj:`str`, optional
        The default text.
    multi_line : :obj:`bool`
        Whether the entered text can span multiple lines.
    title : :obj:`str`, optional
        The text to display in the title bar of the pop-up window.
        If :obj:`None` then uses the text in the title bar of the active window.

    Returns
    -------
    :obj:`str`
        The text that the user entered or :obj:`None` if the user cancelled the request
        to enter text.
    """
    app, title = _get_app_and_title(title)
    if multi_line:
        value, ok = QtWidgets.QInputDialog.getMultiLineText(app.activeWindow(), title, message, default,
                                                            flags=QtCore.Qt.WindowCloseButtonHint,
                                                            inputMethodHints=QtCore.Qt.ImhNone)
    else:
        value, ok = QtWidgets.QInputDialog.getText(app.activeWindow(), title, message, QtWidgets.QLineEdit.Normal,
                                                   default, flags=QtCore.Qt.WindowCloseButtonHint,
                                                   inputMethodHints=QtCore.Qt.ImhNone)
    return value.strip() if ok else None


def _get_app_and_title(title):
    """Returns a tuple of the QApplication instance and the title bar text."""
    app = application()
    if title is None:
        w = app.activeWindow()
        title = 'MSL' if w is None else w.windowTitle()
    return app, title

"""
Convenience functions to prompt the user.

The following functions create a pop-up window to either notify the user of an
event that happened or to request information from the user.
"""
from PyQt5 import QtWidgets

from . import application


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


def question(message, title=None, default_answer=True):
    """Ask the user a question to receive a ``Yes`` or ``No`` answer.

    Parameters
    ----------
    message : :obj:`str`
        The question to ask the user.
    title : :obj:`str`, optional
        The text to display in the title bar of the pop-up window.
        If :obj:`None` then uses the text in the title bar of the active window.
    default_answer : :obj:`bool`, optional
        The answer to be selected by default. If :obj:`True` then ``Yes`` is
        the default answer, if :obj:`False` then ``No`` is the default answer.

    Returns
    -------
    :obj:`bool`
        :obj:`True` if the user answered ``Yes``, :obj:`False` otherwise.
    """
    app, title = _get_app_and_title(title)
    d = QtWidgets.QMessageBox.Yes if default_answer else QtWidgets.QMessageBox.No
    answer = QtWidgets.QMessageBox.question(app.activeWindow(), title, message, defaultButton=d)
    return answer == QtWidgets.QMessageBox.Yes


def _get_app_and_title(title):
    """Returns a tuple of the QApplication instance and the title bar text."""
    app = application()
    if title is None:
        w = app.activeWindow()
        title = 'MSL' if w is None else w.windowTitle()
    return app, title

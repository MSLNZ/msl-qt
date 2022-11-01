"""
Convenience functions to prompt the user.

The following functions create a dialog window to either notify the user of an
event that happened or to request information from the user.
"""
import traceback

from . import (
    QtWidgets,
    Qt,
    application,
    binding,
)
from .convert import to_qfont


def critical(message, *, title=None, font=None):
    """Display a `critical` message in a dialog window.

    Parameters
    ----------
    message : :class:`str` or :class:`Exception`
        The message to display. The message can use HTML/CSS markup, for example,
        ``'<html>A <p style="color:red;font-size:18px"><i>critical</i></p> error occurred!</html>'``
    title : :class:`str`, optional
        The text to display in the title bar of the dialog window.
        If :data:`None` then uses the text in the title bar of the active window.
    font : :class:`int`, :class:`str`, :class:`tuple` or :class:`QtGui.QFont`, optional
        The font to use. If an :class:`int` then the point size, if a :class:`str` then
        the family name, if a :class:`tuple` then the (family name, point size).
    """
    if isinstance(message, Exception):
        message = traceback.format_exc()
    app, mb = _message_box(title=title, message=message, font=font)
    mb.setIcon(QtWidgets.QMessageBox.Critical)
    mb.exec()


def double(message, *, title=None, font=None, value=0, minimum=-2147483647, maximum=2147483647, step=1, decimals=2):
    """Request a double-precision value (a Python :class:`float` data type).

    Parameters
    ----------
    message : :class:`str`
        The message that is shown to the user to describe what the value represents.
        The message can use HTML/CSS markup, for example, ``'<html>Enter a mass, in &mu;g</html>'``
    title : :class:`str`, optional
        The text to display in the title bar of the dialog window.
        If :data:`None` then uses the text in the title bar of the active window.
    font : :class:`int`, :class:`str`, :class:`tuple` or :class:`QtGui.QFont`, optional
        The font to use. If an :class:`int` then the point size, if a :class:`str` then
        the family name, if a :class:`tuple` then the (family name, point size).
    value : :class:`float`, optional
        The initial value.
    minimum : :class:`float`, optional
        The minimum value that the user can enter.
    maximum : :class:`float`, optional
        The maximum value that the user can enter.
    step : :class:`float`, optional
        The step size by which the value is increased and decreased.
    decimals : :class:`int`, optional
        The number of digits that are displayed after the decimal point.

    Returns
    -------
    :class:`float` or :data:`None`
        The value or :data:`None` if the user cancelled the request.
    """
    app, dialog = _input_dialog(title=title, message=message, font=font)
    dialog.setInputMode(QtWidgets.QInputDialog.DoubleInput)
    dialog.setDoubleRange(minimum, maximum)
    dialog.setDoubleStep(step)
    dialog.setDoubleDecimals(decimals)
    dialog.setDoubleValue(value)
    ok = dialog.exec()
    return dialog.doubleValue() if ok else None


def filename(*, title='Select File', directory=None, filters=None, multiple=False):
    """Request to select the file(s) to open.

    Parameters
    ----------
    title : :class:`str`, optional
        The text to display in the title bar of the dialog window.
    directory : :class:`str`, optional
        The initial directory to start in.
    filters : :class:`str`, :class:`list` of :class:`str` or :class:`dict`, optional
        Only filenames that match the specified `filters` are shown.

        Examples::

            'Images (*.png *.xpm *.jpg)'
            'Images (*.png *.xpm *.jpg);;Text files (*.txt);;XML files (*.xml)'
            ['Images (*.png *.xpm *.jpg)', 'Text files (*.txt)', 'XML files (*.xml)']
            {'Images': ('*.png', '*.xpm', '*.jpg'), 'Text files': '*.txt'}

    multiple : :class:`bool`, optional
        Whether multiple files can be selected.

    Returns
    -------
    :class:`str`, :class:`list` of :class:`str` or :data:`None`
        The name(s) of the file(s) to open or :data:`None` if the user cancelled the request.
    """
    app, title = _get_app_and_title(title)
    filters = _get_file_filters(filters)
    if multiple:
        if title == 'Select File':
            title += 's'
        name, _ = QtWidgets.QFileDialog.getOpenFileNames(app.activeWindow(), title, directory, filters)
    else:
        name, _ = QtWidgets.QFileDialog.getOpenFileName(app.activeWindow(), title, directory, filters)
    return name if name else None


def folder(*, title='Select Folder', directory=None):
    """Request to select an existing folder or to create a new folder.

    Parameters
    ----------
    title : :class:`str`, optional
        The text to display in the title bar of the dialog window.
    directory : :class:`str`, optional
        The initial directory to start in.

    Returns
    -------
    :class:`str` or :data:`None`
        The name of the selected folder or :data:`None` if the user cancelled the request.
    """
    app, title = _get_app_and_title(title)
    name = QtWidgets.QFileDialog.getExistingDirectory(app.activeWindow(), title, directory)
    return name if name else None


def information(message, *, title=None, font=None):
    """Display an `information` message in a dialog window.

    Parameters
    ----------
    message : :class:`str` or :class:`Exception`
        The message to display. The message can use HTML/CSS markup, for example,
        ``'<html>The temperature is 21.3 &deg;C</html>'``
    title : :class:`str`, optional
        The text to display in the title bar of the dialog window.
        If :data:`None` then uses the text in the title bar of the active window.
    font : :class:`int`, :class:`str`, :class:`tuple` or :class:`QtGui.QFont`, optional
        The font to use. If an :class:`int` then the point size, if a :class:`str` then
        the family name, if a :class:`tuple` then the (family name, point size).
    """
    if isinstance(message, Exception):
        message = traceback.format_exc()
    app, mb = _message_box(title=title, message=message, font=font)
    mb.setIcon(QtWidgets.QMessageBox.Information)
    mb.exec()


def integer(message, *, title=None, font=None, value=0, minimum=-2147483647, maximum=2147483647, step=1):
    """Request an integer value.

    Parameters
    ----------
    message : :class:`str`
        The message that is shown to the user to describe what the value represents.
        The message can use HTML/CSS markup, for example, ``'<html>Enter a mass, in &mu;g</html>'``
    title : :class:`str`, optional
        The text to display in the title bar of the dialog window.
        If :data:`None` then uses the text in the title bar of the active window.
    font : :class:`int`, :class:`str`, :class:`tuple` or :class:`QtGui.QFont`, optional
        The font to use. If an :class:`int` then the point size, if a :class:`str` then
        the family name, if a :class:`tuple` then the (family name, point size).
    value : :class:`int`, optional
        The initial value.
    minimum : :class:`int`, optional
        The minimum value that the user can enter.
    maximum : :class:`int`, optional
        The maximum value that the user can enter.
    step : :class:`int`, optional
        The step size by which the value is increased and decreased.

    Returns
    -------
    :class:`int` or :data:`None`
        The value or :data:`None` if the user cancelled the request.
    """
    app, dialog = _input_dialog(title=title, message=message, font=font)
    dialog.setInputMode(QtWidgets.QInputDialog.IntInput)
    dialog.setIntRange(minimum, maximum)
    dialog.setIntStep(step)
    dialog.setIntValue(value)
    ok = dialog.exec()
    return dialog.intValue() if ok else None


def item(message, items, *, title=None, font=None, index=0):
    """Request an item from a list of items.

    Parameters
    ----------
    message : :class:`str`
        The message that is shown to the user to describe what the list of items represent.
        The message can use HTML/CSS markup.
    items : :class:`list` or :class:`tuple`
        The list of items to choose from. The items can be of any data type.
    title : :class:`str`, optional
        The text to display in the title bar of the dialog window.
        If :data:`None` then uses the text in the title bar of the active window.
    font : :class:`int`, :class:`str`, :class:`tuple` or :class:`QtGui.QFont`, optional
        The font to use. If an :class:`int` then the point size, if a :class:`str` then
        the family name, if a :class:`tuple` then the (family name, point size).
    index : :class:`int`, optional
        The index of the initial item that is selected.

    Returns
    -------
    The selected item or :data:`None` if the user cancelled the request.

    Notes
    -----
    The data type of the selected item is preserved. For example, if
    `items` = ``[1, 2.0, 2+3j, 'hello', b'world', True, QtWidgets.QPushButton]``
    and the user selects the ``2+3j`` item then a :class:`complex` data type is returned.
    """
    items_ = [str(i) for i in items]
    app, dialog = _input_dialog(title=title, message=message, font=font)
    dialog.setComboBoxItems(items_)
    dialog.setTextValue(items_[index])
    dialog.setComboBoxEditable(False)
    dialog.setInputMethodHints(Qt.ImhNone)
    ok = dialog.exec()
    return items[items_.index(dialog.textValue())] if ok else None


def comments(*, path=None, title=None, even_row_color='#FFFFFF', odd_row_color='#EAF2F8'):
    """Ask the user to enter comments.

    Opens a :class:`QtWidgets.QDialog` to allow for a user to enter comments about
    a task that they are performing. The dialog provides a table of all the previous
    comments that have been used. Comments that are in the table can be deleted by
    selecting the desired row(s) and pressing the ``Delete`` key or the comment in
    a row can be selected by double-clicking on a row.

    This function is useful when acquiring data and you want to include comments
    about how the data was acquired. Using a prompt to enter comments forces you
    to enter a new comment (or use a previous comment) every time you acquire data
    rather than having the comments in a, for example :class:`QtWidgets.QPlainTextEdit`,
    which you might forget to update before acquiring the next data set.

    .. _JSON: https://www.json.org/

    Parameters
    ----------
    path : :class:`str`, optional
        The path to a JSON_ file that contains the history of the comments that have
        been used. If :data:`None` then the default file is used. The file will
        automatically be created if it does not exist.
    title : :class:`str`, optional
        The text to display in the title bar of the dialog window.
    even_row_color
        The background color of the even-numbered rows in the history table.
        See :func:`~.convert.to_qcolor` for details about the different
        data types that are supported.
    odd_row_color
        The background color of the odd-numbered rows in the history table.
        See :func:`~.convert.to_qcolor` for details about the different
        data types that are supported.

    Returns
    -------
    :class:`str`
        The comment that was entered.
    """
    # import here since there are circular import errors if you import at the module level
    from .widgets.comments import Comments
    app, title = _get_app_and_title(title)
    nh = Comments(path, title, even_row_color, odd_row_color)
    nh.exec()
    return nh.text()


def save(*, title='Save As', directory=None, filters=None, options=None):
    """Request to enter the name of a file to save.

    Parameters
    ----------
    title : :class:`str`, optional
        The text to display in the title bar of the dialog window.
    directory : :class:`str`, optional
        The initial directory to start in.
    filters : :class:`str`, :class:`list` of :class:`str` or :class:`dict`, optional
        Only filenames that match the specified `filters` are shown.

        Examples::

            'Images (*.png *.xpm *.jpg)'
            'Images (*.png *.xpm *.jpg);;Text files (*.txt);;XML files (*.xml)'
            ['Images (*.png *.xpm *.jpg)', 'Text files (*.txt)', 'XML files (*.xml)']
            {'Images': ('*.png', '*.xpm', '*.jpg'), 'Text files': '*.txt'}

    options : `QtWidgets.QFileDialog.Option <https://doc.qt.io/qt-6/qfiledialog.html#Option-enum>`_, optional
        Specify additional options on how to run the dialog.

    Returns
    -------
    :class:`str` or :data:`None`
        The name of the file to save or :data:`None` if the user cancelled the request.
    """
    app, title = _get_app_and_title(title)
    filters = _get_file_filters(filters)
    if options is None:
        name, _ = QtWidgets.QFileDialog.getSaveFileName(app.activeWindow(), title, directory, filters)
    else:
        name, _ = QtWidgets.QFileDialog.getSaveFileName(app.activeWindow(), title, directory, filters, options=options)
    return name if name else None


def text(message, *, title=None, font=None, value='', multi_line=False, echo=QtWidgets.QLineEdit.Normal):
    """Request text.

    Parameters
    ----------
    message : :class:`str`
        The message that is shown to the user to describe what the list of items represent.
        The message can use HTML/CSS markup.
    title : :class:`str`, optional
        The text to display in the title bar of the dialog window.
        If :data:`None` then uses the text in the title bar of the active window.
    font : :class:`int`, :class:`str`, :class:`tuple` or :class:`QtGui.QFont`, optional
        The font to use. If an :class:`int` then the point size, if a :class:`str` then
        the family name, if a :class:`tuple` then the (family name, point size).
    value : :class:`str`, optional
        The initial value.
    multi_line : :class:`bool`, optional
        Whether the entered text can span multiple lines.
    echo : :class:`int` or `QLineEdit.EchoMode <https://doc.qt.io/qt-6/qlineedit.html#EchoMode-enum>`_, optional
        The echo mode for the text value. Useful if requesting a password.

    Returns
    -------
    :class:`str` or :data:`None`
        The text that the user entered or :data:`None` if the user cancelled the request.
    """
    app, dialog = _input_dialog(title=title, message=message, font=font)
    dialog.setTextValue(value)
    dialog.setInputMethodHints(Qt.ImhNone)
    if multi_line:
        dialog.setOption(QtWidgets.QInputDialog.UsePlainTextEditForTextInput)
    else:
        dialog.setTextEchoMode(QtWidgets.QLineEdit.EchoMode(echo))
    ok = dialog.exec()
    return dialog.textValue().strip() if ok else None


def password(message, *, title=None, font=None):
    """Request a password.

    Parameters
    ----------
    message : :class:`str`
        The message that is shown to the user to describe what the list of items represent.
        The message can use HTML/CSS markup.
    title : :class:`str`, optional
        The text to display in the title bar of the dialog window.
        If :data:`None` then uses the text in the title bar of the active window.
    font : :class:`int`, :class:`str`, :class:`tuple` or :class:`QtGui.QFont`, optional
        The font to use. If an :class:`int` then the point size, if a :class:`str` then
        the family name, if a :class:`tuple` then the (family name, point size).

    Returns
    -------
    :class:`str` or :data:`None`
        The password or :data:`None` if the user cancelled the request.
    """
    return text(message, title=title, font=font, echo=QtWidgets.QLineEdit.Password)


def warning(message, *, title=None, font=None):
    """Display a `warning` message in a dialog window.

    Parameters
    ----------
    message : :class:`str` or :class:`Exception`
        The message to display. The message can use HTML/CSS markup, for example,
        ``'<html>A <p style="color:yellow">warning</p>...</html>'``
    title : :class:`str`, optional
        The text to display in the title bar of the dialog window.
        If :data:`None` then uses the text in the title bar of the active window.
    font : :class:`int`, :class:`str`, :class:`tuple` or :class:`QtGui.QFont`, optional
        The font to use. If an :class:`int` then the point size, if a :class:`str` then
        the family name, if a :class:`tuple` then the (family name, point size).
    """
    if isinstance(message, Exception):
        message = traceback.format_exc()
    app, mb = _message_box(title=title, message=message, font=font)
    mb.setIcon(QtWidgets.QMessageBox.Warning)
    mb.exec()


def ok_cancel(message, *, title=None, font=None, default=True):
    """Ask for a response to a message where the logical options are ``Ok`` or ``Cancel``.

    Parameters
    ----------
    message : :class:`str`
        The message to ask the user. The message can use HTML/CSS markup.
    title : :class:`str`, optional
        The text to display in the title bar of the dialog window.
        If :data:`None` then uses the text in the title bar of the active window.
    font : :class:`int`, :class:`str`, :class:`tuple` or :class:`QtGui.QFont`, optional
        The font to use. If an :class:`int` then the point size, if a :class:`str` then
        the family name, if a :class:`tuple` then the (family name, point size).
    default : :class:`bool`, optional
        The answer to be selected by default. If :data:`True` then ``Ok`` is
        the default answer, otherwise ``Cancel`` is the default answer.

    Returns
    -------
    :class:`bool` or :data:`None`
        :data:`True` if the user answered ``Ok``, :data:`None` if the user answered ``Cancel``.
    """
    app, mb = _message_box(title=title, message=message, font=font)
    mb.setIcon(QtWidgets.QMessageBox.Question)
    mb.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
    mb.setDefaultButton(QtWidgets.QMessageBox.Ok if default else QtWidgets.QMessageBox.Cancel)
    response = mb.exec()
    if _equal(response, QtWidgets.QMessageBox.Ok):
        return True
    return None


def yes_no(message, *, title=None, font=None, default=True):
    """Ask for a response to a message where the logical options are ``Yes`` or ``No``.

    Parameters
    ----------
    message : :class:`str`
        The message to ask the user. The message can use HTML/CSS markup.
    title : :class:`str`, optional
        The text to display in the title bar of the dialog window.
        If :data:`None` then uses the text in the title bar of the active window.
    font : :class:`int`, :class:`str`, :class:`tuple` or :class:`QtGui.QFont`, optional
        The font to use. If an :class:`int` then the point size, if a :class:`str` then
        the family name, if a :class:`tuple` then the (family name, point size).
    default : :class:`bool`, optional
        The answer to be selected by default. If :data:`True` then ``Yes`` is
        the default answer, otherwise ``No`` is the default answer.

    Returns
    -------
    :class:`bool`
        :data:`True` if the user answered ``Yes``, :data:`False` if the user answered ``No``.
    """
    app, mb = _message_box(title=title, message=message, font=font)
    mb.setIcon(QtWidgets.QMessageBox.Question)
    mb.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    mb.setDefaultButton(QtWidgets.QMessageBox.Yes if default else QtWidgets.QMessageBox.No)
    response = mb.exec()
    return _equal(response, QtWidgets.QMessageBox.Yes)


def yes_no_cancel(message, *, title=None, font=None, default=True):
    """Ask for a response to a message where the logical options are ``Yes``, ``No`` or ``Cancel``.

    Parameters
    ----------
    message : :class:`str`
        The message to ask the user. The message can use HTML/CSS markup.
    title : :class:`str`, optional
        The text to display in the title bar of the dialog window.
        If :data:`None` then uses the text in the title bar of the active window.
    font : :class:`int`, :class:`str`, :class:`tuple` or :class:`QtGui.QFont`, optional
        The font to use. If an :class:`int` then the point size, if a :class:`str` then
        the family name, if a :class:`tuple` then the (family name, point size).
    default : :class:`bool`, optional
        The answer to be selected by default. If :data:`True` then ``Yes`` is
        the default answer, if :data:`False` then ``No`` is the default answer,
        else if :data:`None` then ``Cancel`` is the default answer.

    Returns
    -------
    :class:`bool` or :data:`None`
        :data:`True` if the user answered ``Yes``, :data:`False` if the user answered ``No``,
        or :data:`None` if the user answered ``Cancel``.
    """
    app, mb = _message_box(title=title, message=message, font=font)
    mb.setIcon(QtWidgets.QMessageBox.Question)
    mb.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
    if default is None:
        mb.setDefaultButton(QtWidgets.QMessageBox.Cancel)
    elif default:
        mb.setDefaultButton(QtWidgets.QMessageBox.Yes)
    else:
        mb.setDefaultButton(QtWidgets.QMessageBox.No)
    response = mb.exec()
    if _equal(response, QtWidgets.QMessageBox.Yes):
        return True
    elif _equal(response, QtWidgets.QMessageBox.No):
        return False
    return None


def _get_app_and_title(title):
    """Returns a tuple of the QApplication instance and the title bar text of the active window."""
    app = application()
    if title is None:
        w = app.activeWindow()
        title = 'MSL' if w is None else w.windowTitle()
    return app, title


def _input_dialog(*, title=None, message=None, font=None):
    app, title = _get_app_and_title(title)
    dialog = QtWidgets.QInputDialog(app.activeWindow(), flags=Qt.WindowCloseButtonHint)
    dialog.setWindowTitle(title)
    dialog.setLabelText(message)
    if font:
        dialog.setFont(to_qfont(font))
    return app, dialog


def _message_box(*, title=None, message=None, font=None, buttons=None, default=None):
    app, title = _get_app_and_title(title)
    mb = QtWidgets.QMessageBox(app.activeWindow())
    mb.setWindowTitle(title)
    mb.setText(message)
    if font:
        mb.setFont(to_qfont(font))
    if buttons:
        mb.setStandardButtons(buttons)
    if default:
        mb.setDefaultButton(default)
    return app, mb


def _get_file_filters(filters):
    """Make the `filters` value be in the appropriate syntax."""
    def _check_extn(ex):
        """Check the format of the file extension."""
        if ex is None:
            return all_files
        if '*' in ex:
            return ex
        if ex.startswith('.'):
            return f'*{ex}'
        return f'*.{ex}'

    all_files = 'All Files (*)'

    if filters is None:
        return all_files

    if isinstance(filters, dict):
        f = ''
        for name, extn in filters.items():
            if isinstance(extn, (list, tuple)):
                extn = ' '.join(_check_extn(e) for e in extn)
                f += f'{name} ({extn});;'
            else:
                f += f'{name} ({_check_extn(extn)});;'
        return f[:-2]

    if isinstance(filters, (list, tuple)):
        return ';;'.join(f if f is not None else all_files for f in filters)

    if filters.endswith(';;'):
        return filters[:-2]

    return filters


def _equal(response, enum):
    """In PyQt6 all enums are implemented as an enum.Enum not enum.IntEnum"""
    if binding.name == 'PyQt6':
        return response == enum.value
    return response == enum

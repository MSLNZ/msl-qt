"""
Convenience functions to prompt the user.

The following functions create a dialog window to either notify the user of an
event that happened or to request information from the user.
"""
import traceback

from . import QtWidgets, QtCore, application


def critical(message, title=None):
    """Display the critical `message` in a dialog window.

    Parameters
    ----------
    message : :class:`str` or :class:`Exception`
        The message to display.
    title : :class:`str`, optional
        The text to display in the title bar of the dialog window.
        If :obj:`None` then uses the text in the title bar of the active window.
    """
    app, title = _get_app_and_title(title)
    if isinstance(message, Exception):
        message = traceback.format_exc()
    QtWidgets.QMessageBox.critical(app.activeWindow(), title, str(message))


def double(message, default=0, minimum=-2147483647, maximum=2147483647, precision=1, title=None):
    """Request a floating-point value.

    Parameters
    ----------
    message : :class:`str`
        The message that is shown to the user to describe what the value represents.
    default : :class:`float`, optional
        The default floating-point value.
    minimum : :class:`float`, optional
        The minimum value that the user can enter.
    maximum : :class:`float`, optional
        The maximum value that the user can enter.
    precision : :class:`int`, optional
        The number of digits that are displayed after the decimal point.
    title : :class:`str`, optional
        The text to display in the title bar of the dialog window.
        If :obj:`None` then uses the text in the title bar of the active window.

    Returns
    -------
    :class:`float` or :obj:`None`
        The floating-point value or :obj:`None` if the user cancelled
        the request to enter a floating-point number.
    """
    app, title = _get_app_and_title(title)
    value, ok = QtWidgets.QInputDialog.getDouble(app.activeWindow(), title, message,
                                                 default, minimum, maximum, precision,
                                                 flags=QtCore.Qt.WindowCloseButtonHint)
    return value if ok else None


def filename(initial=None, filters=None, multiple=False, title='Select File'):
    """Request to select the file(s) to open.

    Parameters
    ----------
    initial : :class:`str`, optional
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
    title : :class:`str`, optional
        The text to display in the title bar of the dialog window.

    Returns
    -------
    :class:`str` or :class:`list` of :class:`str`
        The name(s) of the file(s) to open or :obj:`None` if the user cancelled
        the request to select a file.
    """
    app, title = _get_app_and_title(title)
    filters = _get_file_filters(filters)
    if multiple:
        if title == 'Select File':
            title += 's'
        name, _ = QtWidgets.QFileDialog.getOpenFileNames(app.activeWindow(), title, initial, filters)
    else:
        name, _ = QtWidgets.QFileDialog.getOpenFileName(app.activeWindow(), title, initial, filters)
    return name if len(name) > 0 else None


def folder(initial=None, title='Select Folder'):
    """Request to select an existing folder or to create a new folder.

    Parameters
    ----------
    initial : :class:`str`, optional
        The initial directory to start in.
    title : :class:`str`, optional
        The text to display in the title bar of the dialog window.

    Returns
    -------
    :class:`str`
        The name of the selected folder or :obj:`None` if the user cancelled
        the request to select a folder.
    """
    app, title = _get_app_and_title(title)
    name = QtWidgets.QFileDialog.getExistingDirectory(app.activeWindow(), title, initial)
    return name if len(name) > 0 else None


def information(message, title=None):
    """Display the information `message` in a dialog window.

    Parameters
    ----------
    message : :class:`str` or :class:`Exception`
        The message to display.
    title : :class:`str`, optional
        The text to display in the title bar of the dialog window.
        If :obj:`None` then uses the text in the title bar of the active window.
    """
    app, title = _get_app_and_title(title)
    if isinstance(message, Exception):
        message = traceback.format_exc()
    QtWidgets.QMessageBox.information(app.activeWindow(), title, str(message))


def integer(message, default=0, minimum=-2147483647, maximum=2147483647, step=1, title=None):
    """Request an integer value.

    Parameters
    ----------
    message : :class:`str`
        The message that is shown to the user to describe what the value represents.
    default : :class:`int`, optional
        The default integer value.
    minimum : :class:`int`, optional
        The minimum value that the user can enter.
    maximum : :class:`int`, optional
        The maximum value that the user can enter.
    step : :class:`int`, optional
        The amount by which the values change as the user presses the arrow
        buttons to increment or decrement the value.
    title : :class:`str`, optional
        The text to display in the title bar of the dialog window.
        If :obj:`None` then uses the text in the title bar of the active window.

    Returns
    -------
    :class:`int` or :obj:`None`
        The integer value or :obj:`None` if the user cancelled the request to
        enter a number.
    """
    app, title = _get_app_and_title(title)
    value, ok = QtWidgets.QInputDialog.getInt(app.activeWindow(), title, message,
                                              default, minimum, maximum, step,
                                              flags=QtCore.Qt.WindowCloseButtonHint)
    return value if ok else None


def item(message, items, index=0, title=None):
    """Request an item from a list of items.

    Parameters
    ----------
    message : :class:`str`
        The message that is shown to the user to describe what the list of items represent.
    items : :class:`list` of :class:`object`
        The list of items to choose from. The items can be of any data type.
    index : :class:`int`, optional
        The index of the default item that is selected.
    title : :class:`str`, optional
        The text to display in the title bar of the dialog window.
        If :obj:`None` then uses the text in the title bar of the active window.

    Returns
    -------
    :class:`object`
        The selected item or :obj:`None` if the user cancelled the request to
        select an item.

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


def notes(json_path=None, title=None, even_row_color='#FFFFFF', odd_row_color='#EAF2F8'):
    """Ask the user to enter notes.

    Opens a :class:`QtWidgets.QDialog` to allow for a user to enter a detailed
    description of a task that they are performing. The :class:`QtWidgets.QDialog`
    provides a table of all the previous notes that have been used. Notes that are
    in the table can be deleted by selecting the desired row(s) and pressing the
    ``delete`` key or the note in a row can be copied to the note editor by
    double-clicking on a row.

    This function is useful when acquiring data and you want to include notes
    about how the data was acquired. Using a prompt to enter notes forces you
    to manually enter the notes every time you acquire data rather than having
    the notes typed directly onto the graphical user interface, which you might
    forget to update before acquiring the next data set.

    .. _JSON: https://www.json.org/

    Parameters
    ----------
    json_path : :class:`str`, optional
        The path to a JSON_ file that contains the history of the notes that have
        been used. If :obj:`None` then the default file is used. The file will
        automatically be created if it does not exist.
    title : :class:`str`, optional
        The text to display in the title bar of the dialog window.
    even_row_color : :class:`QtGui.QColor`, optional
        The background color of the even-numbered rows in the history table.
        Can be any data type and value that the constructor of a
        :class:`QtGui.QColor` accepts.
    odd_row_color : :class:`QtGui.QColor`, optional
        The background color of the odd-numbered rows in the history table.
        Can be any data type and value that the constructor of a
        :class:`QtGui.QColor` accepts.

    Returns
    -------
    :class:`str`
        The note that was entered.
    """
    # import here since there are circular import errors if you import at the module level
    from .notes_history import NotesHistory
    app, title = _get_app_and_title(title)
    nh = NotesHistory(app.activeWindow(), json_path, title, even_row_color, odd_row_color)
    nh.exec_()
    return nh.text()


def question(message, default=True, title=None):
    """Ask a question to receive a ``Yes`` or ``No`` answer.

    Parameters
    ----------
    message : :class:`str`
        The question to ask the user.
    default : :class:`bool`, optional
        The answer to be selected by default. If :obj:`True` then ``Yes`` is
        the default answer, if :obj:`False` then ``No`` is the default answer.
    title : :class:`str`, optional
        The text to display in the title bar of the dialog window.
        If :obj:`None` then uses the text in the title bar of the active window.

    Returns
    -------
    :class:`bool`
        :obj:`True` if the user answered ``Yes``, :obj:`False` otherwise.
    """
    app, title = _get_app_and_title(title)
    d = QtWidgets.QMessageBox.Yes if default else QtWidgets.QMessageBox.No
    answer = QtWidgets.QMessageBox.question(app.activeWindow(), title, message, defaultButton=d)
    return answer == QtWidgets.QMessageBox.Yes


def save(initial=None, filters=None, title='Save As', options=None):
    """Request to select the name of a file to save.

    Parameters
    ----------
    initial : :class:`str`, optional
        The initial directory to start in.
    filters : :class:`str`, :class:`list` of :class:`str` or :class:`dict`, optional
        Only filenames that match the specified `filters` are shown.

        Examples::

            'Images (*.png *.xpm *.jpg)'
            'Images (*.png *.xpm *.jpg);;Text files (*.txt);;XML files (*.xml)'
            ['Images (*.png *.xpm *.jpg)', 'Text files (*.txt)', 'XML files (*.xml)']
            {'Images': ('*.png', '*.xpm', '*.jpg'), 'Text files': '*.txt'}

    title : :class:`str`, optional
        The text to display in the title bar of the dialog window.
    options : `QtWidgets.QFileDialog.Option <http://doc.qt.io/qt-5/qfiledialog.html#Option-enum>`_, optional
        Specify additional options on how to run the dialog.

    Returns
    -------
    :class:`str`
        The name of the file to save or :obj:`None` if the user cancelled the
        request to select a file.
    """
    app, title = _get_app_and_title(title)
    filters = _get_file_filters(filters)
    if options is None:
        name, _ = QtWidgets.QFileDialog.getSaveFileName(app.activeWindow(), title, initial, filters)
    else:
        name, _ = QtWidgets.QFileDialog.getSaveFileName(app.activeWindow(), title, initial, filters, options=options)
    return name if len(name) > 0 else None


def text(message, default='', multi_line=False, title=None):
    """Request text.

    Parameters
    ----------
    message : :class:`str`
        The message that is shown to the user to describe what the text represents.
    default : :class:`str`, optional
        The default text.
    multi_line : :class:`bool`, optional
        Whether the entered text can span multiple lines.
    title : :class:`str`, optional
        The text to display in the title bar of the dialog window.
        If :obj:`None` then uses the text in the title bar of the active window.

    Returns
    -------
    :class:`str`
        The text that the user entered or :obj:`None` if the user cancelled the
        request to enter text.
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


def warning(message, title=None):
    """Display the warning `message` in a dialog window.

    Parameters
    ----------
    message : :class:`str` or :class:`Exception`
        The message to display.
    title : :class:`str`, optional
        The text to display in the title bar of the dialog window.
        If :obj:`None` then uses the text in the title bar of the active window.
    """
    app, title = _get_app_and_title(title)
    if isinstance(message, Exception):
        message = traceback.format_exc()
    QtWidgets.QMessageBox.warning(app.activeWindow(), title, str(message))


def _get_app_and_title(title):
    """Returns a tuple of the QApplication instance and the title bar text of the active window."""
    app = application()
    if title is None:
        w = app.activeWindow()
        title = 'MSL' if w is None else w.windowTitle()
    return app, title


def _get_file_filters(filters):
    """Make the `filters` value be in the appropriate syntax."""
    def _check_extn(ex):
        """Check the format of the file extension."""
        if ex is None:
            return all_files
        if '*' in ex:
            return ex
        if ex.startswith('.'):
            return '*' + ex
        return '*.' + ex

    all_files = 'All Files (*)'

    if filters is None:
        return all_files

    if isinstance(filters, dict):
        f = ''
        for name, extn in filters.items():
            if isinstance(extn, (list, tuple)):
                f += '{} ({});;'.format(name, ' '.join(_check_extn(e) for e in extn))
            else:
                f += '{} ({});;'.format(name, _check_extn(extn))
        return f[:-2]

    if isinstance(filters, (list, tuple)):
        return ';;'.join(f if f is not None else all_files for f in filters)

    if filters.endswith(';;'):
        return filters[:-2]

    return filters

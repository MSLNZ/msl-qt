"""
A :class:`~QtWidgets.QComboBox` with more options in the constructor.
"""
from .. import QtGui
from .. import QtWidgets


class ComboBox(QtWidgets.QComboBox):

    def __init__(self, *, items=None, initial=None, index_changed=None,
                 text_changed=None, tooltip=None, parent=None):
        """A :class:`~QtWidgets.QComboBox` with more options in the constructor.

        Parameters
        ----------
        items : :class:`str`, :class:`list` of :class:`str`, :class:`dict`, optional
            The item(s) to add to the combobox. If a :class:`str`, then adds the
            single item. If a :class:`list`, then adds all items. If a :class:`dict`,
            then the keys are the text of each item and the values can either be a
            :class:`~QtGui.QIcon` to use as the icon or any other type to use as the
            `userData` parameter. To specify both an icon and `userData` for an item
            the values can be of type :class:`tuple`, e.g., (icon, `userData`).
        initial : :class:`int` or :class:`str`, optional
            The index or text of the item to initially display. This value is set
            before the slots are registered.
        index_changed
            A callable function to use as a slot for the
            :meth:`~QtWidgets.QComboBox.currentIndexChanged` signal.
        text_changed
            A callable function to use as a slot for the
            :meth:`~QtWidgets.QComboBox.currentTextChanged` signal.
        tooltip : :class:`str`, optional
            The tooltip to display for the combobox.
        parent : :class:`QtWidgets.QWidget`, optional
            The parent widget.
        """
        super(ComboBox, self).__init__(parent=parent)
        if items:
            if isinstance(items, str):
                self.addItem(items)
            elif isinstance(items, (list, tuple)):
                self.addItems(items)
            elif isinstance(items, dict):
                for key, value in items.items():
                    if isinstance(value, QtGui.QIcon):
                        self.addItem(value, key)
                    elif isinstance(value, (list, tuple)):
                        icon, data = None, None
                        for item in value:
                            if isinstance(item, QtGui.QIcon):
                                icon = item
                            else:
                                data = item
                        if icon:
                            self.addItem(icon, key, userData=data)
                        else:
                            self.addItem(key, userData=data)
                    else:
                        self.addItem(key, userData=value)
            else:
                raise TypeError(f"unsupported type {type(items)} for 'items' parameter")

        if initial:
            if isinstance(initial, int):
                self.setCurrentIndex(initial)
            else:
                self.setCurrentText(initial)

        if index_changed:
            self.currentIndexChanged.connect(index_changed)  # noqa: QComboBox.currentIndexChanged

        if text_changed:
            self.currentTextChanged.connect(text_changed)  # noqa: QComboBox.currentTextChanged

        if tooltip:
            self.setToolTip(tooltip)

"""
Custom :class:`~QtWidgets.QWidget`\'s for the `MSL Equipment <http://msl-equipment.readthedocs.io/en/latest>`_ package.
"""
from msl.qt import QtWidgets, QtCore


def show_record(record):
    """Create a :class:`~QtWidgets.QDialog` to display the information about a record.

    Parameters
    ----------
    record : :obj:`~msl.equipment.record_types.EquipmentRecord` or :obj:`~msl.equipment.record_types.ConnectionRecord`
        An Equipment Record or a Connection Record.
    """
    dialog = QtWidgets.QDialog()
    dialog.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
    dialog.setWindowTitle(record.__class__.__name__.replace('R', ' R'))

    widget = QtWidgets.QTextEdit()
    widget.setReadOnly(True)
    widget.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
    widget.setText(record.to_yaml())

    hbox = QtWidgets.QHBoxLayout()
    hbox.addWidget(widget)
    dialog.setLayout(hbox)

    size = widget.document().size()
    sb = widget.horizontalScrollBar().size().height()
    dialog.resize(int((size.width() + sb) * 1.1), int((size.height() + sb) * 1.1))  # add 10%
    dialog.exec_()


from .message_based import MessageBased
from .configuration_viewer import ConfigurationViewer

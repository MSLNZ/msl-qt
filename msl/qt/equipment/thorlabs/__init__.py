"""
Custom :class:`~QtWidgets.QWidget`'\s for equipment from Thorlabs.
"""
from PyQt5 import QtWidgets, QtCore


def show_hardware_info(connection):
    """Displays the hardware information about a Thorlabs
    :class:`~msl.equipment.resources.thorlabs.kinesis.motion_control.MotionControl` device
    in a :class:`QtWidgets.QDialog`

    Parameters
    ----------
    connection : :class:`~msl.equipment.resources.thorlabs.kinesis.motion_control.MotionControl`
        A Thorlabs Motion Control subclass.
    """
    info = connection.get_hardware_info()

    dialog = QtWidgets.QDialog()
    dialog.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
    dialog.setWindowTitle(connection.__class__.__name__)

    widget = QtWidgets.QTextEdit()
    widget.setReadOnly(True)
    widget.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)

    text = 'Serial Number: {}\n'.format(info.serialNumber)
    text += 'Model Number: {}\n'.format(info.modelNumber.decode('utf-8'))
    text += 'Type: {}\n'.format(info.type)
    text += 'Number of Channels: {}\n'.format(info.numChannels)
    text += 'Notes: {}\n'.format(info.notes.decode('utf-8'))
    text += 'Firmware Version: {}\n'.format(connection.to_version(info.firmwareVersion))
    text += 'Hardware Version: {}\n'.format(connection.to_version(info.hardwareVersion))
    text += 'Modification State: {}'.format(info.modificationState)
    widget.setText(text)

    hbox = QtWidgets.QHBoxLayout()
    hbox.addWidget(widget)
    dialog.setLayout(hbox)

    size = widget.document().size()
    pad = widget.horizontalScrollBar().size().height() * 1.1
    dialog.resize(int(size.width() + pad), int(size.height() + pad))
    dialog.exec_()


from .translation_stage import TranslationStage

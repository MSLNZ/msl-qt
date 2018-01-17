"""
Example showing the use of the :obj:`MessageBased <msl.qt.equipment.message_based.MessageBased>` widget.

The messages are sent to a *dummy* :class:`~msl.equipment.record_types.EquipmentRecord` in demo mode.
"""
from msl.equipment import EquipmentRecord, ConnectionRecord, Backend

from msl.qt import application
from msl.qt.equipment import MessageBased

record = EquipmentRecord(
    manufacturer='Manufacturer',
    model='Model#',
    serial='Serial#',
    connection=ConnectionRecord(
        backend=Backend.MSL,
        address='COM1'
    )
)


def show():
    app = application()
    mb = MessageBased(record.connect(True))
    mb.resize(1000, 600)
    mb.show()
    app.exec_()


if __name__ == '__main__':
    show()

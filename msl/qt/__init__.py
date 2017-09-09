"""
Custom `Qt <https://www.qt.io/>`_ components for the user interface.
"""
import sys
from collections import namedtuple

from PyQt5 import QtWidgets, QtCore

__author__ = 'Joseph Borbely'
__copyright__ = '\xa9 2017, ' + __author__
__version__ = '0.1.0'

version_info = namedtuple('version_info', 'major minor micro')(*map(int, __version__.split('.')[:3]))
""":obj:`~collections.namedtuple`: Contains the version information as a (major, minor, micro) tuple."""


def application(args=None):
    """Returns the :obj:`~QtWidgets.QApplication` instance (creating one if necessary).

    Parameters
    ----------
    args : :obj:`list` of :obj:`str`, optional
        A list of arguments to initialize the :obj:`~QtWidgets.QApplication`.
        If :obj:`None` then uses :obj:`sys.argv`.

    Returns
    -------
    :obj:`~QtWidgets.QApplication`
        The QApplication instance.
    """
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv if args is None else args)

        # use a default *MSL logo* as the app icon
        logo = 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAACXBIWXMAAAsTAAALEwEAmpwYAAAAGXRFWHR' \
               'Db21tZW50AENyZWF0ZWQgd2l0aCBHSU1QV4EOFwAAAx9JREFUWIXNlk9oXFUYxX/fnZmmmQ6aVt+rBCsEgo' \
               'UWLBNjRUg0sxA3ihsHEwKiGxcWQ1ZunYIrt0IpuunKRKYgal0I2j47qIsmThTqQvy3i2m0pqmkSX3vHhfJj' \
               'KWT1OmbNPSs3rvvnu+e+/19RkosjhZ7ZRwHCsHB+rhV8GnsuLQC4gw9gpcFo1wsW1o72bRExSacdOPawljx' \
               'ayCWceKB9+vTd1TAFngCwMGn7RJSC1jrvufX/NryoCnJWLWapLWTWkDfqWgV+D4tv4HUSbhd2O4cuCUWx4p' \
               'PeXgbyIRx/+NWrSZ3VMDv4wPPmudJpF/2T9dPSgQYR9fVLBp04IFL5cMFsl1DHnL7p749Y6CWTdLTwATGN8' \
               'BJWeue9I3IdR0Q+sjQx5TLm9oxEW88/rOVndQCHHEG2HU7HMlaPJ46BNe69/2UX1s+4rxl2+0DXbv9Z/F1N' \
               '4iXEUVJRwIKq1f2JaZJ71xBFUbbGUZ7T80tAbM3rnU0jAx7CVTuZBilFqDYBJvfWo3cMHVtvOe3stN2CObH' \
               'i4dMPGLSajjfc2ae5ZY94fy9OQBGIg8QPjw3QTQySRAI6p0JcJ4XgONgSwsHLj/I9VaqRdF62UUb7xU8RLf' \
               'MjU0FCGxhdGASU58T58Pp+ul2hd4utswBM/+iwesyK232PUeSAH8A1zhcbe2CbSJ1GQYffPcj0JuW30DTAw' \
               'ITpC6ntGh64NJY8SqwtIBeYWru8x0XAOwB9gi3+3848ku51DG/GW03ovBg/a0w7s+GcX/Q+8nsynYJuDkJP' \
               'W5jZsuEgSQPjZqubte5dw+aWb8wVvwNuOJgIpiqf7lTApohEDprxkqS+D936vC7As0QlIYefddgRXLvnfvq' \
               'wg+l4cFJPH1ynI9qM6dLwwPPIPecsKvBXytvXi4U9vpc8oaMfFSbeQ1QaeixEyCP2Yfnahe+KA0PPm9SCeP' \
               'ns7XZd0pDR49A8qrM3Eht5lgF/H9lKAuFC5KM1me5V48ZAVgBwJTNgwLD3/f3Q2sm57LA/SbCSuMiUggKpK' \
               'QbQN4KwgXy9AA4r13gAhPhxfL6T8y/FrQlyIjl7wYAAAAASUVORK5CYII='
        from msl.qt.io import get_icon
        app.setWindowIcon(get_icon(QtCore.QByteArray(logo.encode())))

    return app

from .logger import Logger
from .loop_until_abort import LoopUntilAbort
from .toggle_switch import ToggleSwitch
from .button import Button

"""
Custom `Qt <https://www.qt.io/>`_ components for the graphical user interface.
"""
import re
import sys
from collections import namedtuple

__author__ = 'Measurement Standards Laboratory of New Zealand'
__copyright__ = '\xa9 2017 - 2023, ' + __author__
__version__ = '0.1.0.dev0'

_v = re.search(r'(\d+)\.(\d+)\.(\d+)[.-]?(.*)', __version__).groups()

version_info = namedtuple('version_info', 'major minor micro releaselevel')(int(_v[0]), int(_v[1]), int(_v[2]), _v[3])
""":obj:`~collections.namedtuple`: Contains the version information as a (major, minor, micro, releaselevel) tuple."""


def application(*args):
    """Returns the :class:`QtWidgets.QApplication` instance (creating one if necessary).

    Parameters
    ----------
    args
        A list of arguments to initialize the application. If :data:`None` then
        uses :data:`sys.argv`.

    Returns
    -------
    :class:`QtWidgets.QApplication`
        The application instance.
    """
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(args if args else sys.argv)

        # use a default MSL logo as the app icon
        logo = b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAACXBIWXMAAAsTAAALEwEAmpwYAAAAGXRFWHR' \
               b'Db21tZW50AENyZWF0ZWQgd2l0aCBHSU1QV4EOFwAAAx9JREFUWIXNlk9oXFUYxX/fnZmmmQ6aVt+rBCsEgo' \
               b'UWLBNjRUg0sxA3ihsHEwKiGxcWQ1ZunYIrt0IpuunKRKYgal0I2j47qIsmThTqQvy3i2m0pqmkSX3vHhfJj' \
               b'KWT1OmbNPSs3rvvnu+e+/19RkosjhZ7ZRwHCsHB+rhV8GnsuLQC4gw9gpcFo1wsW1o72bRExSacdOPawljx' \
               b'ayCWceKB9+vTd1TAFngCwMGn7RJSC1jrvufX/NryoCnJWLWapLWTWkDfqWgV+D4tv4HUSbhd2O4cuCUWx4p' \
               b'PeXgbyIRx/+NWrSZ3VMDv4wPPmudJpF/2T9dPSgQYR9fVLBp04IFL5cMFsl1DHnL7p749Y6CWTdLTwATGN8' \
               b'BJWeue9I3IdR0Q+sjQx5TLm9oxEW88/rOVndQCHHEG2HU7HMlaPJ46BNe69/2UX1s+4rxl2+0DXbv9Z/F1N' \
               b'4iXEUVJRwIKq1f2JaZJ71xBFUbbGUZ7T80tAbM3rnU0jAx7CVTuZBilFqDYBJvfWo3cMHVtvOe3stN2CObH' \
               b'i4dMPGLSajjfc2ae5ZY94fy9OQBGIg8QPjw3QTQySRAI6p0JcJ4XgONgSwsHLj/I9VaqRdF62UUb7xU8RLf' \
               b'MjU0FCGxhdGASU58T58Pp+ul2hd4utswBM/+iwesyK232PUeSAH8A1zhcbe2CbSJ1GQYffPcj0JuW30DTAw' \
               b'ITpC6ntGh64NJY8SqwtIBeYWru8x0XAOwB9gi3+3848ku51DG/GW03ovBg/a0w7s+GcX/Q+8nsynYJuDkJP' \
               b'W5jZsuEgSQPjZqubte5dw+aWb8wVvwNuOJgIpiqf7lTApohEDprxkqS+D936vC7As0QlIYefddgRXLvnfvq' \
               b'wg+l4cFJPH1ynI9qM6dLwwPPIPecsKvBXytvXi4U9vpc8oaMfFSbeQ1QaeixEyCP2Yfnahe+KA0PPm9SCeP' \
               b'ns7XZd0pDR49A8qrM3Eht5lgF/H9lKAuFC5KM1me5V48ZAVgBwJTNgwLD3/f3Q2sm57LA/SbCSuMiUggKpK' \
               b'QbQN4KwgXy9AA4r13gAhPhxfL6T8y/FrQlyIjl7wYAAAAASUVORK5CYII='
        app.setWindowIcon(convert.to_qicon(QtCore.QByteArray(logo)))

    return app


from ._qt import *
from . import convert
from . import prompt
from . import utils
from .characters import *
from .exceptions import excepthook
from .loop_until_abort import LoopUntilAbort
from .sleep import Sleep
from .threading import Thread
from .threading import Worker
from .widgets import Button
from .widgets import CheckBox
from .widgets import ComboBox
from .widgets import DoubleSpinBox
from .widgets import LED
from .widgets import LineEdit
from .widgets import Logger
from .widgets import SpinBox
from .widgets import ToggleSwitch

# the following object is imported from _qt.py
binding = binding
""":obj:`~collections.namedtuple`: The Python binding for the Qt framework."""

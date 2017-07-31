"""
Custom `Qt <https://wiki.python.org/moin/PyQt>`_ components for the UI.
"""
import sys
from collections import namedtuple

from PyQt5 import QtWidgets, QtGui, QtCore

__author__ = 'Joseph Borbely'
__copyright__ = '\xa9 2017, ' + __author__
__version__ = '0.1.0'

version_info = namedtuple('version_info', 'major minor micro')(*map(int, __version__.split('.')[:3]))
""":obj:`~collections.namedtuple`: Contains the version information as a (major, minor, micro) tuple."""


def application(args=None, icon=None):
    """Returns the QApplication instance (creating one if necessary).

    Parameters
    ----------
    args : :obj:`list` of :obj:`str`
        A list of arguments to initialize the QApplication.
        If :obj:`None` then uses :obj:`sys.argv`.

    icon : :obj:`QIcon`
        The icon to use for the QApplication.
        If :obj:`None` then a default *MSL logo* is used as the icon.

    Returns
    -------
    :obj:`QtWidgets.QApplication`
        The QApplication instance.
    """
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv if args is None else args)
        if icon is None:
            base64 = QtCore.QByteArray.fromBase64(
                b'iVBORw0KGgoAAAANSUhEUgAAAEAAAABrCAYAAADHAoQrAAAACXBIWXMAAAsT'
                b'AAALEwEAmpwYAAACtklEQVR4nO2cMW6DMBSG/1Ts5AjdWbImUqTkGizNFXKC'
                b'khPkCunCNUoVKVlZ2DlCOEE7NEjEWC20ht/ovW/Dsng/v2zzMLYB4cwYQas4'
                b'SoyiU5gWJUEKAkZQAK/GdQagHF8G8MQI6hNqAFsAG/EGsAbBX6niaAFg3ii6'
                b'hWmRu47jrQEAjgA2jesMwNZ1EPFdQA1gC2CjBrAFsGG9BczR3PnrrSsUA8K0'
                b'yBhxbYjvAmoAWwAbNYAtgI0awBbARrwBPs8HOKOKo3ejaF9ProgwAI8TK0Bj'
                b'pkl8FxBvwKS7QBVHGxjNO0yLpM89Jm0Avh/e/M2W9LmB+C4g3gBKF/D293gV'
                b'RwCAMC2GjuvN7/GgfmipiB8D1ABbYRVHkNI1tAWwBbARb4A1ERo6DwjTYtT1'
                b'iT/FE98C1AC2ADasj6FPo2jL+mMsvgWoAbZCTYUFoQaMMPvjNQHwmPpWcTTG'
                b'lJg3tPIAjx7+DcBH47q01Mn+G4S1acqbRMhpJnhf439sloVp4XyJu0tcp8Jz'
                b'tH9Fe42+BtkC2KgBbAFsOg+CVRztADw3isowLU6O9YxOn7fAC9q7uE4OtVAQ'
                b'3wXUALYANqwtM5RvEBviW4AawBbARg1gC2CjBrAFsAkA6xzdoe+q66kivgWo'
                b'AWwBbNQAtgA2rr8GSwAHx/ccFKcG3Dc9JC7vOTTiu4AawBbARrwB9SBojtyZ'
                b'pW6XBQuKokyLGWDdyZn5dNzVkNSDoLmTE3CwAmsKiH8NqgFsAYqiKAqRGQCs'
                b'1suNUV5ezteyWbBaL1uHnV/O19yoMwewaJZdztfMDGqJl1/O19sf4j3jcele'
                b'73h1JmgeNnZAe26vy2HnC8u9bMthzDpbtDPPLvF2aGexveKJzwPUALYANvUY'
                b'YPat0lJ3D2NQstTJLfey0eVo7S7xTuj21erNUd7e8QXVKpuqaR3U/AAAAABJ'
                b'RU5ErkJggg=='
            )
            img = QtGui.QImage()
            img.loadFromData(base64, 'PNG')
            app.setWindowIcon(QtGui.QIcon(QtGui.QPixmap.fromImage(img)))
    return app

from .loop_until_abort import LoopUntilAbort

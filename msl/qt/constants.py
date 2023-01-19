"""
Constants used by the **MSL-Qt** package.
"""
import os

HOME_DIR = os.path.join(os.path.expanduser('~'), '.msl')
""":class:`str`: The default ``$HOME`` directory where all files used by the package are located."""

SI_PREFIX_MAP = {i: prefix for i, prefix in enumerate('qryzafpnum kMGTPEZYRQ', start=-10)}
""":class:`dict`: The SI prefixes used to form multiples of :math:`10^{3n}, n=` -10 .. 10"""

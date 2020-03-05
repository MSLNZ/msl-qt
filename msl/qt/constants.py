"""
Constants used by the **MSL-Qt** package.
"""
import os

HOME_DIR = os.path.join(os.path.expanduser('~'), '.msl')
""":class:`str`: The default ``$HOME`` directory where all files are to be located."""

SI_PREFIX_MAP = {i: prefix for i, prefix in enumerate('yzafpn\u00b5m kMGTPEZY', start=-8)}
""":class:`dict`: The SI prefixes used to form multiples of 10**(3*n), n=-8..8"""

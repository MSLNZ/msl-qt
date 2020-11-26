"""
Color schemes compatible with `Sublime Text`_.

.. _Sublime Text: https://www.sublimetext.com/
"""
import os
import plistlib

COLOR_SCHEME_MAP = dict()


def add_color_schemes(directory):
    """Recursively find all `Sublime Text`_ color schemes that are in a directory.

    Parameters
    ----------
    directory : :class:`str`
        The root directly to begin the search.
    """
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.tmTheme') or filename.endswith('.stTheme'):
                COLOR_SCHEME_MAP[filename[:-8]] = os.path.join(root, filename)


def load(scheme):
    """Load a color scheme.

    Parameters
    ----------
    scheme : :class:`str`
        The name of a color scheme.

    Returns
    -------
    class:`bytes`
        The contents of the color-scheme file.
    """
    with open(COLOR_SCHEME_MAP[scheme], mode='rb') as fp:
        return plistlib.load(fp, fmt=plistlib.FMT_XML)


add_color_schemes(os.path.dirname(__file__))

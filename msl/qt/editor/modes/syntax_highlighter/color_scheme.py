import os
import plistlib

from ...color_schemes import COLOR_SCHEME_MAP
from .... import (
    QtGui,
    Qt,
)


class ColorScheme(object):

    def __init__(self, name):
        """A color scheme to use for syntax highlighting.

        Parameters
        ----------
        name : :class:`str`
            Creates a color scheme for the specified style name.

        Raises
        ------
        ValueError
            If a color scheme with the name `name` does not exist.
        """
        self._name = name

        with open(COLOR_SCHEME_MAP[name], 'rb') as fp:
            data = plistlib.load(fp)

        self._styles = dict()
        self._styles['globals'] = dict()
        self._styles['scopes'] = dict()
        for dictionary in data['settings']:
            if len(dictionary) == 1:
                self._styles['globals'] = dictionary['settings']
            else:
                if ',' in dictionary['scope']:
                    for scope in dictionary['scope'].split(','):
                        self._styles['scopes'][scope.strip()] = dictionary['settings']
                elif ' ' in dictionary['scope']:
                    # TODO figure out a proper way to handle multiple matching conditions
                    # self._styles['scopes'][setting['scope'].replace(' ', '&')] = setting['settings']
                    pass
                else:
                    self._styles['scopes'][dictionary['scope']] = dictionary['settings']

        self._foreground = self._qcolor(self._global_setting('foreground', Qt.black))
        self._background = self._qcolor(self._global_setting('background', Qt.white))
        self._invisibles = self._qcolor(self._global_setting('invisibles', Qt.black))
        self._caret = self._qcolor(self._global_setting('caret', Qt.black))
        self._line_highlight = self._qcolor(self._global_setting('lineHighlight', Qt.lightGray))
        self._find_highlight = self._qcolor(self._global_setting('findHighlight', '#FFE792'))
        self._find_highlight_foreground = self._qcolor(self._global_setting('findHighlightForeground', Qt.black))
        self._gutter = self._qcolor(self._global_setting('gutter', Qt.black))
        self._gutter_foreground = self._qcolor(self._global_setting('gutterForeground', Qt.white))
        self._selection = self._qcolor(self._global_setting('selection', Qt.darkCyan))
        self._selection_border = self._qcolor(self._global_setting('selectionBorder', Qt.black))
        self._inactive_selection = self._qcolor(self._global_setting('inactiveSelection', Qt.black))
        self._brackets_foreground = self._qcolor(self._global_setting('bracketsForeground', Qt.black))
        self._brackets_background = self._qcolor(self._global_setting('bracketsBackground', '#2471A3'))
        self._brackets_options = self._global_setting('bracketsOptions', 'background')
        self._misspelling = self._qcolor(self._global_setting('misspelling', Qt.red))
        self._lint_error = self._qcolor(self._global_setting('lintError', Qt.red))
        self._lint_warning = self._qcolor(self._global_setting('lintWarning', Qt.darkGray))

    @property
    def foreground(self):
        """:class:`QtGui.QColor`: Default foreground color."""
        return self._foreground

    @property
    def background(self):
        """:class:`QtGui.QColor`: Default background color."""
        return self._background

    @property
    def invisibles(self):
        """:class:`QtGui.QColor`: The color to use for invisibles."""
        return self._invisibles

    @property
    def caret(self):
        """:class:`QtGui.QColor`: The color of the caret."""
        return self._caret

    @property
    def line_highlight(self):
        """:class:`QtGui.QColor`: The background color of the line the caret is in."""
        return self._line_highlight

    @property
    def find_highlight(self):
        """:class:`QtGui.QColor`: Background color of regions matching the current search."""
        return self._find_highlight

    @property
    def find_highlight_foreground(self):
        """:class:`QtGui.QColor`: Foreground color of regions matching the current search."""
        return self._find_highlight_foreground

    @property
    def gutter(self):
        """:class:`QtGui.QColor`: Background color of the gutter."""
        return self._gutter

    @property
    def gutter_foreground(self):
        """:class:`QtGui.QColor`: Foreground color of the gutter."""
        return self._gutter_foreground

    @property
    def selection(self):
        """:class:`QtGui.QColor`: Color of the selection regions."""
        return self._selection

    @property
    def selection_border(self):
        """:class:`QtGui.QColor`: Color of the selection regions' border."""
        return self._selection_border

    @property
    def inactive_selection(self):
        """:class:`QtGui.QColor`: Color of inactive selections (inactive view)."""
        return self._inactive_selection

    @property
    def brackets_foreground(self):
        """:class:`QtGui.QColor`: The foreground color to use for bracket matching."""
        return self._brackets_foreground

    @property
    def brackets_background(self):
        """:class:`QtGui.QColor`: The background color to use for bracket matching."""
        return self._brackets_background

    @property
    def brackets_options(self):
        """:class:`str`: How brackets are highlighted when the caret is next to one."""
        return self._brackets_options

    @property
    def misspelling(self):
        """:class:`QtGui.QColor`: The color to use for the squiggly underline drawn under misspelled words."""
        return self._misspelling

    @property
    def lint_error(self):
        """:class:`QtGui.QColor`: The color to use for the squiggly underline drawn
        under words that have lint errors."""
        return self._lint_error

    @property
    def lint_warning(self):
        """:class:`QtGui.QColor`: The color to use for the squiggly underline drawn
        under words that have lint warnings."""
        return self._lint_warning

    @property
    def name(self):
        """:class:`str`: The name of the color scheme."""
        return self._name

    def to_format(self, scopes):
        """Convert the scopes to a :class:`QtGui.QTextCharFormat`.

        Parameters
        ----------
        scopes : :class:`list` of :class:`str`
            A list of scopes.

        Returns
        -------
        :class:`QtGui.QTextCharFormat`
            The format to use for syntax highlighting.
        """
        style = self._get_style_from_scopes(scopes)
        fmt = QtGui.QTextCharFormat()
        if style:
            fmt.setForeground(self._qcolor(style.get('foreground', self._foreground)))
            fmt.setBackground(self._qcolor(style.get('background', self._background)))
            font_styles = style.get('fontStyle')
            if font_styles:
                for font_style in font_styles.split():
                    if font_style == 'bold':
                        fmt.setFontWeight(QtGui.QFont.Bold)
                    elif font_style == 'italic':
                        fmt.setFontItalic(True)
                    elif font_style == 'underline':
                        fmt.setUnderlineStyle(QtGui.QTextCharFormat.SingleUnderline)
        return fmt

    def _global_setting(self, name, default):
        return self._styles['globals'].get(name, default)

    def _qcolor(self, color):
        if isinstance(color, str) and len(color) == 4:
            color = '#' + color[1]*2 + color[2]*2 + color[3]*2
        return QtGui.QColor(color)

    def _get_style_from_scopes(self, scopes):
        # find the most-specific scope that has a style
        for scope in scopes[::-1]:
            while True:
                style = self._styles['scopes'].get(scope)
                if style:
                    return style
                scope, ext = os.path.splitext(scope)
                if not ext:
                    break
        return self._styles['scopes'].get('source')

from . import PYTHON_GRAMMAR_PATH
from ..base import BaseEditor
from ..modes import LineHighlighterMode
from ..modes import SyntaxHighlighterMode
from ..modes import AutoCompleteMode
from ..modes import LineLengthMode
from ..modes import SmartHomeMode
from ..modes import BracketMatcherMode
from ..panels import LineNumberPanel
from .code_completer import PythonCodeCompleterMode
from .indent_dedent import PythonIndentDedentMode
from .linter import PythonLinter
from .hyperlink import PythonHyperlinkMode


class PythonEditor(BaseEditor):

    def __init__(self, parent=None, font=None, cursor_width=2,
                 color_scheme_name=None, min_completer_length=2, indent=4, max_line_length=80):
        BaseEditor.__init__(self, parent=parent, font=font, cursor_width=cursor_width)

        if color_scheme_name is None:
            color_scheme_name = 'Chromodynamics'

        self.modes.add(PythonCodeCompleterMode(self, min_completer_length))
        self.modes.add(AutoCompleteMode(self, **{'"""': '"""', "'''": "'''"}))
        self.modes.add(LineLengthMode(self, max_line_length))
        self.modes.add(PythonIndentDedentMode(self, indent))
        self.modes.add(SmartHomeMode(self))
        self.modes.add(LineHighlighterMode(self))
        self.modes.add(BracketMatcherMode(self))  # must come after LineHighlighterMode (because of QTextEdit.ExtraSelection)
        self.modes.add(SyntaxHighlighterMode(self, PYTHON_GRAMMAR_PATH, color_scheme_name))
        self.modes.add(PythonLinter(self, max_line_length=max_line_length))  # must come after SyntaxHighlighterMode
        self.modes.add(PythonHyperlinkMode(self))

        self.panels.add(LineNumberPanel(self))

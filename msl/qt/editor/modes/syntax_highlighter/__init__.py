"""
Performs syntax highlighting for the :class:`BaseEditor`.

This package implements the code from https://github.com/atom/first-mate
to create tokens to use for syntax highlighting.

The code was written based from first-mate v7.1.0 (commit 4216f7d)
"""
import logging

from .grammar import Grammar
from .grammar_registry import GrammarRegistry
from .color_scheme import ColorScheme
from ...types import Mode
from ...profiler import Profile
from .... import (
    QtGui,
    Qt,
)

logger = logging.getLogger(__name__)

registry = GrammarRegistry()


class SyntaxHighlighterMode(Mode):

    def __init__(self, editor, grammar_url, color_scheme_name):
        """Performs syntax highlighting for the :class:`BaseEditor`.

        Parameters
        ----------
        editor : :class:`BaseEditor`
            The editor.
        grammar_url : :class:`str`
            The URL to a grammar file.
        color_scheme_name : :class:`str`
            The name of a Sublime Text color scheme.
        """
        super(SyntaxHighlighterMode, self).__init__(editor)

        self._grammar = registry.loadGrammarSync(grammar_url)
        self.editor.color_scheme = color_scheme_name
        self.update_color_scheme(self.editor.color_scheme)

    def add(self):
        self.editor.new_text_event.connect(self.retokenize)
        self.editor.key_release_event.connect(self._check_rehighlight)
        self.editor.new_color_scheme_event.connect(self.update_color_scheme)
        self.editor.paste_event.connect(self._paste_event)

    def remove(self):
        self.editor.new_text_event.disconnect(self.retokenize)
        self.editor.key_release_event.disconnect(self._check_rehighlight)
        self.editor.new_color_scheme_event.disconnect(self.update_color_scheme)
        self.editor.paste_event.disconnect(self._paste_event)

    @Profile()
    def update_color_scheme(self, scheme):
        s = 'QPlainTextEdit{color: %s; background-color: %s; selection-background-color: %s;}' % \
            (scheme.caret.name(), scheme.background.name(), scheme.selection.name())
        self.editor.setStyleSheet(s)

        block = self.editor.document().begin()
        if block.userData() is None:
            return  # no tokens exist

        cursor = self.editor.textCursor()
        while block.isValid():
            self._rehightlight_line(block, cursor, block.userData().tokens)
            block = block.next()

    @Profile()
    def retokenize(self):
        results = self._grammar.tokenizeLines(self.editor.text())
        block = self.editor.document().begin()
        if results:
            cursor = self.editor.textCursor()
            while block.isValid():
                try:
                    result = results[block.blockNumber()]
                except IndexError:
                    block.setUserData(TextBlockUserData(None))
                else:
                    self._rehightlight_line(block, cursor, result.tokens)
                    block.setUserData(TextBlockUserData(result))
                block = block.next()
        else:
            while block.isValid():
                block.setUserData(TextBlockUserData(None))
                block = block.next()

    @Profile()
    def rehighlight(self, event):
        cursor = self.editor.textCursor()
        block = cursor.block()
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            block = block.previous()

        while block.isValid():
            line = block.text()
            result = self._tokenize_line(line, block, cursor)
            unchanged = self._line_ending_scope_unchanged(line, result.tokens, block.userData())
            # since self._line_ending_scope_unchanged() only checks if the line
            # ends with the same scope there is a possibility that a scope changed
            # within the line, so we must update the userData
            block.setUserData(TextBlockUserData(result))
            if unchanged:
                break
            block = block.next()

    def _tokenize_line(self, line, block, cursor):
        rule_stack = None
        if block.blockNumber() > 0:
            rule_stack = block.previous().userData().rule_stack
        result = self._grammar.tokenizeLine(line, ruleStack=rule_stack)
        self._rehightlight_line(block, cursor, result.tokens)
        return result

    def _rehightlight_line(self, block, cursor, tokens):
        position = block.position()
        for token in tokens:
            length = len(token['value'])
            if length > 0:
                cursor.setPosition(position)
                cursor.setPosition(position + length, mode=cursor.KeepAnchor)
                cursor.setCharFormat(self.editor.color_scheme.to_format(token['scopes']))
                position += length

    def _line_ending_scope_unchanged(self, line, tokens, user_data):
        """
        Checks whether the last scope for this line has not changed.

        This makes the assumption that if the last scope remains unchanged that
        all the lines that follow do not need to be rehighlighted.
        """
        if not line.strip() or not user_data or not user_data.tokens:
            return False

        if len(tokens) != len(user_data.tokens):
            return False

        if tokens[-1]['scopes'][-1] != user_data.tokens[-1]['scopes'][-1]:
            return False

        return True

    def _check_rehighlight(self, event):
        if self.editor.is_code_completer_visible or self.editor.is_navigation(event):
            return

        key = event.key()
        if key == Qt.Key_Escape:
            return
        if key == Qt.Key_Insert:
            return
        if key == Qt.Key_Backtab:
            return
        if key == Qt.Key_Control:
            return
        if key == Qt.Key_Shift:
            return

        if self.editor.document().blockCount() == 1:
            # this can happen for CTRL+A then Delete
            self.retokenize()
        else:
            self.rehighlight(event)

    def _paste_event(self, text):
        n = len(text.splitlines())
        cursor = self.editor.textCursor()
        cursor.movePosition(cursor.PreviousBlock, cursor.MoveAnchor, n=n)
        block = cursor.block()
        for _ in range(n):
            # don't use "for line in text.splitlines()"
            # using block.text() guarantees to be the correct text for that block
            result = self._tokenize_line(block.text(), block, cursor)
            block.setUserData(TextBlockUserData(result))
            block = block.next()


class TextBlockUserData(QtGui.QTextBlockUserData):

    def __init__(self, result):
        super(TextBlockUserData, self).__init__()

        if result:
            self.tokens = result.tokens
            self.rule_stack = result.ruleStack
        else:
            self.tokens = []
            self.rule_stack = []

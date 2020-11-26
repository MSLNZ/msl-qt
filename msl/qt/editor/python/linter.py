"""
Performs linting using pycodestyle and pyflakes
"""
import os
from ast import PyCF_ONLY_AST
import logging

# import sys
# import subprocess
# from flake8.api import legacy as flake8

import tempfile
import pycodestyle
from pyflakes import checker, messages

from ..modes import LinterMode

logger = logging.getLogger(__name__)


class Report(pycodestyle.StandardReport):

    def get_file_results(self):
        return self._deferred_print


class Checker(pycodestyle.Checker):

    def __init__(self, *args, **kwargs):
        report = Report(kwargs.pop('options'))
        super(Checker, self).__init__(*args, report=report, **kwargs)


class PythonLinter(LinterMode):

    PYFLAKES_ERROR_MESSAGES = [
        messages.DoctestSyntaxError,
        messages.ReturnWithArgsInsideGenerator,
        messages.UndefinedExport,
        messages.UndefinedName,
        messages.UndefinedLocal
    ]

    def __init__(self, editor, max_line_length=80, pep8_ignore=None):
        """

        pep8_ignore ->  ['W291', 'W292', 'W293', 'W391']

        """
        LinterMode.__init__(self, editor)

        self.cursor = None
        self.doc = None

        pycodestyle.MAX_LINE_LENGTH = max_line_length

        if pep8_ignore is None:
            self._pep8_ignore_rules = []

        self._pep8style = pycodestyle.StyleGuide(
            parse_argv=False, config_file='', checker_class=Checker
        )

        self._filename_source = os.path.join(tempfile.gettempdir(), 'msl-flake8-source.py')
        # self._filename_report = os.path.join(tempfile.gettempdir(), 'msl-flake8-report.py')
        # with open(self._filename_report, 'w') as fp:
        #     fp.write('')
        #
        # self._flake8_style_guide = flake8.get_style_guide(
        #     ignore=self._pep8_ignore_rules,
        #     output_file=self._filename_report,
        # )

    # def _run_flake8(self, source_code):
    #      with open(self._filename_source, 'w') as fp:
    #          fp.write(source_code)
    #
    #      self._flake8_style_guide.check_files([self._filename_source])
    #
    #      with open(self._filename_report, 'r') as fp:
    #          report = fp.read()

    def lint(self, source_code):
        # this is not working like I want to to
        # do not want to save the source code to a file and then read the results from a file
        # self._run_flake8(source_code)

        self.cursor = self.editor.textCursor()
        self.doc = self.editor.document()
        self._run_pycodestyle(source_code)
        self._run_pyflakes(source_code)

    def _run_pycodestyle(self, source_code):
        try:
            results = self._pep8style.input_file(None, lines=source_code.splitlines(True))
        except Exception as e:
            logger.error(e)
        else:
            for line_number, column, code, msg, _ in results:
                if code in self._pep8_ignore_rules:
                    continue
                self._append('[PEP8] %s: %s' % (code, msg), line_number, column, code.startswith('E'))

    def _run_pyflakes(self, source_code):
        try:
            tree = compile(source_code.encode('utf-8'), self._filename_source, 'exec', PyCF_ONLY_AST)
        except SyntaxError as e:
            # See if the MagicPython syntax highlighter found this syntax error
            msg = '[SyntaxError] ' + e.args[0]
            block = self.doc.findBlockByNumber(e.lineno - 1)
            if block.userData():
                index = 0
                for token in block.userData().tokens:
                    index += len(token['value'])
                    if index >= e.offset:
                        for scope in token['scopes'][::-1]:
                            if scope.startswith('invalid.illegal'):
                                index -= len(token['value'])
                                self._append(msg, e.lineno, index, True)
                                return
            self._append(msg, e.lineno, e.offset, True)
        else:
            w = checker.Checker(tree, os.path.split(self._filename_source)[1])
            for message in w.messages:
                status = 'W' if message.__class__ not in self.PYFLAKES_ERROR_MESSAGES else 'E'
                msg = '[pyFlakes] %s: %s' % (status, str(message).split(':')[-1].strip())
                self._append(msg, message.lineno, message.col, status == 'E')

    def _append(self, message, line_number, column_number, is_error):
        block = self.doc.findBlockByNumber(line_number - 1)
        self.cursor.setPosition(block.position() + column_number, mode=self.cursor.MoveAnchor)
        if self.cursor.atBlockEnd():
            self.cursor.movePosition(self.cursor.Left, mode=self.cursor.KeepAnchor)
            if self.cursor.selectedText() == '\u2029':
                self.cursor.movePosition(self.cursor.Left, mode=self.cursor.KeepAnchor)
        else:
            self.cursor.movePosition(self.cursor.EndOfWord, mode=self.cursor.KeepAnchor)
            if not self.cursor.selectedText():
                self.cursor.movePosition(self.cursor.NextWord, mode=self.cursor.KeepAnchor)

        fmt = self.cursor.charFormat()
        fmt.setUnderlineStyle(fmt.WaveUnderline)
        fmt.setUnderlineColor(self.error_color if is_error else self.warning_color)
        self.cursor.setCharFormat(fmt)

        self._linter_info.append((
            self.cursor.selectionStart(),
            self.cursor.selectionEnd(),
            message,
        ))

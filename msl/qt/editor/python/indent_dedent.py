from ..modes import IndentDedentMode


class PythonIndentDedentMode(IndentDedentMode):

    def additional_newline_handler(self, cursor, left, right):
        indent = max(self._num_spaces, self.get_current_line_indentation())

        if left.rstrip().endswith(':'):
            text = '\u2029' + ' ' * indent + right.lstrip()
            cursor.insertText(text)
            cursor.movePosition(cursor.EndOfBlock, cursor.KeepAnchor)
            extra = len(cursor.selectedText()) - len(right.lstrip())
            cursor.removeSelectedText()
            cursor.movePosition(cursor.StartOfBlock, cursor.MoveAnchor)
            cursor.movePosition(cursor.Right, cursor.MoveAnchor, n=indent)
            self.indent_dedent_event.emit(1 + indent - extra)
            return True

        if '#' in left and right.strip():
            cursor.insertText('\u2029' + ' ' * indent + '# ')
            self.indent_dedent_event.emit(1 + indent + 2)
            return True

        return False

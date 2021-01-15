import jedi

from ... import (
    QtWidgets,
    QtGui,
)
from ..modes import HyperlinkMode


class PythonHyperlinkMode(HyperlinkMode):

    def __init__(self, editor):
        super(PythonHyperlinkMode, self).__init__(editor)

    def draw_hyperlink_from_scopes(self, scopes):
        for scope in scopes[::-1]:
            if scope.startswith('comment.typehint'):
                return True
            elif scope.startswith('string.quoted'):
                return False
            elif scope.startswith('string.regexp'):
                return False
            elif scope.startswith('comment.line'):
                return False
            elif scope.startswith('constant.numeric'):
                return False
        return True

    def hyperlink(self, cursor):
        script = self._get_script(cursor)
        assignments = script.goto_assignments(follow_imports=True)
        if assignments:
            a = assignments[0]  # TODO handle multiple assignments
            cursor = self.editor.textCursor()
            block = self.editor.document().findBlockByNumber(a.line - 1)
            position = block.position() + a.column
            if a.module_path is None:
                cursor.setPosition(position)
                self.editor.setTextCursor(cursor)
            else:
                self.hyperlink_external_event.emit(a.module_path, position)

    def popup(self, cursor):
        script = self._get_script(cursor)
        assignments = script.goto_assignments(follow_imports=False)
        if assignments:
            a = assignments[0]  # TODO handle multiple assignments
            if a.module_path:
                message = '{}\n\n{}'.format(a.module_path, a.docstring())
            else:
                message = a.docstring()
            if len(message) > 1024:
                message = message[:1024] + ' ... '  # TODO maybe we should create a QToolTip with a scrollbar
            QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), message)

    def _get_script(self, cursor):
        return jedi.Script(
            source=self.editor.text(),
            line=cursor.blockNumber() + 1,
            column=cursor.positionInBlock(),
            encoding='utf-8'
        )

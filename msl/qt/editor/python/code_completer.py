"""
Performs code completion for the :class:`PythonEditor`.
"""
import os
import logging

import jedi

from ..modes import CodeCompleterMode
from ... import (
    QtGui,
    Qt,
)

logger = logging.getLogger(__name__)


class PythonCodeCompleterMode(CodeCompleterMode):

    def __init__(self, editor, min_prefix_length=1):
        """Performs code completion for the :class:`PythonEditor`.

        Parameters
        ----------
        editor : :class:`PythonEditor`
            The editor.
        min_prefix_length : :class:`int`, optional
            The minimum length that the prefix must be before the completion
            popup is displayed. To disable the popup based on the length of
            the prefix specify a value < 1.
        """
        super(PythonCodeCompleterMode, self).__init__(editor, min_prefix_length=min_prefix_length)
        self.model.setColumnCount(2)

        root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'icons'))

        self._icon_map = {
            'builtins': QtGui.QIcon(os.path.join(root, 'B.png')),
            'class': QtGui.QIcon(os.path.join(root, 'C.png')),
            'function': QtGui.QIcon(os.path.join(root, 'F.png')),
            'imported': QtGui.QIcon(os.path.join(root, 'I.png')),
            'instance': QtGui.QIcon(os.path.join(root, 'Z.png')),
            'keyword': QtGui.QIcon(os.path.join(root, 'K.png')),
            'method': QtGui.QIcon(os.path.join(root, 'Z.png')),
            'module': QtGui.QIcon(os.path.join(root, 'M.png')),
            'parameter': QtGui.QIcon(os.path.join(root, 'P.png')),
            'variable': QtGui.QIcon(os.path.join(root, 'V.png')),
        }

        self._unknown_icon = QtGui.QIcon(os.path.join(root, 'Z.png'))

    def update_model(self, event):
        self.model.clear()

        # get the source code
        cursor = self.editor.textCursor()
        line, column = cursor.blockNumber()+1, cursor.positionInBlock()

        if self._is_trigger_key:
            source = self.editor.text()
        else:
            i = cursor.position()
            text = self.editor.text()
            source = text[:i] + event.text() + text[i:]
            column += 1

        script = jedi.Script(source=source, line=line, column=column)

        row = 0
        for completion in script.completions():
            try:
                icon = self._icon_map[completion.type]
            except KeyError:
                icon = self._unknown_icon

            item0 = QtGui.QStandardItem(icon, completion.name_with_symbols)
            item0.setTextAlignment(Qt.AlignLeft)
            self.model.setItem(row, 0, item0)

            item1 = QtGui.QStandardItem(completion.module_name)
            item1.setTextAlignment(Qt.AlignRight)
            self.model.setItem(row, 1, item1)

            row += 1

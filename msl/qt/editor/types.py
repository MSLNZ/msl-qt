import logging

from msl.qt import QtWidgets, QtCore

logger = logging.getLogger(__name__)


class EditorType(object):

    def __init__(self, editor):
        self._editor = editor
        logger.debug('initialized ' + str(self))

    def __repr__(self):
        return '<{} id={:#x} editor={}>'.format(self.name, id(self), self._editor)

    def __del__(self):
        logger.debug('deleted ' + str(self))

    @property
    def editor(self):
        """:class:`~editor.base.BaseEditor`: The code editor."""
        return self._editor

    @property
    def name(self):
        return self.__class__.__name__

    def add(self):
        """Add the mode to the :class:`~editor.base.BaseEditor`."""
        pass

    def remove(self):
        """Remove the mode from the :class:`~editor.base.BaseEditor`."""
        pass


class Mode(EditorType, QtCore.QObject):

    def __init__(self, editor):
        EditorType.__init__(self, editor)
        QtCore.QObject.__init__(self)  # allows a Mode to emit signals


class Panel(EditorType, QtWidgets.QWidget):

    def __init__(self, editor):
        EditorType.__init__(self, editor)
        QtWidgets.QWidget.__init__(self, parent=editor)
